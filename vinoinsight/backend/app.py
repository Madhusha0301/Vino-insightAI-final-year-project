"""
VinoInsight AI - Flask Backend API
------------------------------------------------------------------
Run with:  python app.py

Endpoints:
  GET  /api/health
  POST /api/predict                 - wine quality/price/aroma/segment prediction
                                       (auto-saved to history if caller is logged in)
  GET  /api/predictions              - logged-in user's saved prediction history
  GET  /api/predictions/stats        - aggregates for the Dashboard (real, not mock)
  GET  /api/predictions/trends       - the user's own predictions grouped by date
                                       (NOT year-based: the model has no year input,
                                       see predictions_db.py docstring)
  POST /api/signup             - create buyer/seller account
  POST /api/login              - authenticate, returns token
  GET  /api/me                 - get current user from token
  POST /api/chat                - wine chatbot (Gemini-backed, with fallback)
  GET  /api/admin/pending-sellers   - admin only
  POST /api/admin/approve/<id>      - admin only
  POST /api/admin/reject/<id>       - admin only
  GET  /api/shap/global             - global SHAP feature importance (all 5 outputs)
"""

from dotenv import load_dotenv
load_dotenv()  # load .env before importing modules that read env vars (Mongo URI, Gemini key)

from flask import Flask, request, jsonify
from flask_cors import CORS
import explain_recommend
from explain_recommend import predict_all, FEATURES
import auth_db
import predictions_db
from wine_chatbot import get_chat_response, get_status as get_chat_status

app = Flask(__name__)
CORS(app)


def _get_auth_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    return auth_db.get_user_by_token(token)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "VinoInsight AI backend is running"})


# ------------------------- PREDICTION -------------------------

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "No JSON body received"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        input_dict = {f: float(data[f]) for f in FEATURES}
        result = predict_all(input_dict)
        result["inputs"] = input_dict

        # Persist to MongoDB if the caller is a logged-in user (closes the
        # "Database Storage" gap identified in the project audit). Anonymous
        # calls (no/invalid token) still get a prediction back as before —
        # they just aren't saved to any history, since there's no user to
        # attach them to.
        user = _get_auth_user()
        wine_style = data.get("wine_style")  # optional label from the frontend
        saved = None
        if user:
            try:
                saved = predictions_db.save_prediction(user["id"], wine_style, result)
            except Exception as e:
                # Persistence failure should never break a working prediction —
                # degrade gracefully and surface it in the response instead of
                # crashing the whole request (mirrors the chatbot's fallback
                # philosophy rather than auth_db's hard-crash-on-connect design).
                print(f"Warning: failed to save prediction history: {e}")
        result["saved_to_history"] = saved is not None

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------- PREDICTION HISTORY -------------------------

@app.route("/api/predictions", methods=["GET"])
def get_predictions():
    user = _get_auth_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    limit = request.args.get("limit", default=100, type=int)
    return jsonify({"predictions": predictions_db.list_predictions_for_user(user["id"], limit=limit)})


@app.route("/api/predictions/stats", methods=["GET"])
def get_predictions_stats():
    user = _get_auth_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify(predictions_db.get_stats_for_user(user["id"]))


@app.route("/api/predictions/trends", methods=["GET"])
def get_predictions_trends():
    user = _get_auth_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"trends": predictions_db.get_trends_for_user(user["id"])})


# ------------------------- EXPLAINABILITY -------------------------

@app.route("/api/shap/global", methods=["GET"])
def get_global_shap_importance():
    """
    Global SHAP feature importance for all 5 outputs (project audit, Task 5
    - closes the "SHAP Global" half of the Contextual Report's "SHAP Global
    & Local" claim, which previously had no global explanation at all).
    Precomputed once at startup (see explain_recommend.py); this endpoint
    just returns the cached result, no per-request computation. Public
    (no auth required) since it describes the model in general, not any
    specific user's data.
    """
    return jsonify({"global_importance": explain_recommend.GLOBAL_SHAP_IMPORTANCE})


# ------------------------- AUTH -------------------------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role")
    company_name = (data.get("company_name") or "").strip() or None

    if not name or not email or not password or role not in ("buyer", "seller"):
        return jsonify({"error": "name, email, password, and role (buyer/seller) are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    user, err = auth_db.create_user(name, email, password, role, company_name)
    if err:
        return jsonify({"error": err}), 409

    return jsonify({
        "user": user,
        "message": (
            "Account created. Your seller account is pending admin verification "
            "before you can access seller features."
            if role == "seller" else
            "Account created successfully."
        ),
    }), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result, err = auth_db.authenticate(email, password)
    if err:
        return jsonify({"error": err}), 401

    return jsonify(result)


@app.route("/api/me", methods=["GET"])
def me():
    user = _get_auth_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"user": user})


# ------------------------- ADMIN -------------------------

def _require_admin():
    user = _get_auth_user()
    if not user or user["role"] != "admin":
        return None
    return user


@app.route("/api/admin/pending-sellers", methods=["GET"])
def pending_sellers():
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403
    return jsonify({"pending": auth_db.list_pending_sellers()})


@app.route("/api/admin/approve/<user_id>", methods=["POST"])
def approve_seller(user_id):
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403
    ok = auth_db.set_seller_status(user_id, "approved")
    return jsonify({"success": ok})


@app.route("/api/admin/reject/<user_id>", methods=["POST"])
def reject_seller(user_id):
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403
    ok = auth_db.set_seller_status(user_id, "rejected")
    return jsonify({"success": ok})


# ------------------------- CHATBOT -------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "message is required"}), 400

    answer, used_ai = get_chat_response(message, history)
    return jsonify({"answer": answer, "ai_powered": used_ai})


@app.route("/api/chat/status", methods=["GET"])
def chat_status():
    """Diagnostics for the chatbot.

    Added because the failure this endpoint exposes is otherwise invisible from
    the UI: with no GEMINI_API_KEY the bot silently degrades to the offline
    knowledge base and simply looks like a weak chatbot. Visit
    http://localhost:5000/api/chat/status to see whether the key was found,
    which Gemini model is live, and the last API error if any.
    """
    return jsonify(get_chat_status())


if __name__ == "__main__":
    # threaded=True (project audit, performance testing task): Flask's dev
    # server is single-threaded by default, so without this, concurrent
    # requests are guaranteed to queue and be served strictly one at a time.
    # test_performance.py measured 10 simultaneous users making 30 total
    # /api/predict calls: ~9.4s wall time with threaded=False, and it did
    # NOT meaningfully improve (~9.1s) after adding threaded=True on this
    # 2-core test machine — because /api/predict is CPU-bound (5 model
    # inferences + SHAP per call, and scikit-learn/XGBoost already use
    # n_jobs=-1 internally), not I/O-bound, so Python's GIL limits how much
    # true parallelism threading alone can add once all cores are already
    # saturated by model inference. threaded=True is kept anyway because it
    # is still strictly safer (no risk of one slow request blocking health
    # checks or other endpoints) and would matter more on a machine with
    # more CPU cores than this test environment's 2. State plainly in the
    # report: for meaningfully better concurrent throughput, the fix is a
    # production WSGI server (e.g. gunicorn with multiple workers) rather
    # than Flask's built-in dev server, threaded or not.
    app.run(debug=True, port=5000, threaded=True)
