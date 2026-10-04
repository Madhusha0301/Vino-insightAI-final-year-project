# VinoInsight AI — How to Run (Backend + Frontend)

## What's new in this update (v12): General-domain chatbot + pre-viva audit fixes

Two pieces of work: the chatbot was rebuilt to answer the whole wine domain,
and a full pre-submission audit found and fixed six further issues.

### Chatbot rebuilt as a general wine assistant

Previously the bot only reliably answered **chemistry** questions (acidity,
tannins, pH, sulphates) plus a few app-specific ones. The root cause was that
no `backend/.env` existed, so `GEMINI_API_KEY` was empty and Gemini was never
actually being called — *every* answer came from a hardcoded 14-topic keyword
list. Three secondary issues would have limited it even with a key: the system
prompt led with chemistry framing and told the model to "redirect" anything it
judged off-topic; a single hardcoded model ID meant any Google rename silently
killed the AI path; and the frontend sent its static greeting as `history[0]`,
so requests opened on a `model` turn.

| File | Change |
|---|---|
| `backend/wine_chatbot.py` | General-purpose system prompt, 5-model fallback chain, sanitised history, scored keyword matching, `get_status()` |
| `backend/wine_knowledge.py` | **New** — 112-topic offline wine knowledge base |
| `backend/check_gemini.py` | **New** — one-command connection diagnostic |
| `backend/app.py` | Added `GET /api/chat/status` |
| `backend/tests/test_chat.py` | Rewritten to pin down both answer paths deterministically |
| `src/components/ChatBot.jsx` | Broader greeting, clickable starter-prompt chips |

The offline matcher now scores matches instead of taking the first hit in list
order (which is why old answers felt arbitrary), and uses word-boundary
matching so short keywords can't false-positive — "ph" no longer fires inside
"phone", "port" no longer fires inside "important".

### Six issues found in the pre-viva audit and fixed

1. **A live API key was shipping inside the distributed zip.** `.gitignore`
   excluded `backend/.env`, but *gitignore does not apply to zip files*, so
   the real key travelled with every copy of the project. Added
   `backend/.env.example` (a safe, secret-free template documenting every
   setting), and a documented packaging command that excludes `.env` — see
   "Packaging the project for submission" below.
2. **Unknown URLs rendered a completely blank page.** The router had no
   catch-all route. Because the real pages are nested under `/dashboard/*`,
   the very natural guess `/predict` matched nothing and React Router rendered
   *nothing at all* — no message, no navigation, no way back. Added
   `src/pages/NotFound.jsx` and wildcard routes at both levels. It also
   detects this specific case and offers the correct link ("that page lives
   inside your dashboard") rather than a bare 404.
3. **The offline chatbot couldn't explain the project's own core concepts.**
   An independent 66-question probe answered only 55. The misses included
   **"What is SHAP?"** — the central explainability idea of the whole project
   — plus "How does the prediction work?" and "What are chlorides?"
   (chlorides being one of the model's own eleven inputs). Exactly the
   questions likely to be asked in a demo, and exactly when the live AI might
   be down. Added a "how the system works" section covering SHAP, the model
   architecture, real accuracy figures, and the missing inputs, plus regions
   and everyday topics. The same probe now answers 66/66, verified by content
   rather than by "something matched".
4. **`/api/chat/status` reported a working Gemini when it wasn't.** It said
   `mode: "gemini"` whenever the client object had been constructed — but
   constructing it makes no network call, so an invalid, revoked, or
   firewalled key still reported "gemini" while every answer silently came
   from the offline base. It now reports three distinct states:
   `offline-knowledge-base`, `gemini-configured` (key present but
   **unverified**), and `gemini-active` (a real call has actually succeeded),
   plus a `gemini_verified` boolean and a plain-English `note`.
5. **Weak web-font fallbacks.** `index.css` pulls Playfair Display and DM Sans
   from Google Fonts — the app's only remaining runtime network dependency.
   It degrades rather than breaks, but the fallback was a bare `sans-serif`.
   Both stacks are now explicit system stacks, so an offline demo still looks
   close to the intended design.
6. **Stale documentation.** This README (the declared single source of truth)
   still claimed a "14 topic" fallback and "25 tests", and its remaining-steps
   list still said to get a Gemini key. All corrected.

**Test suite: 42 passing** (up from 39), including three new tests that pin
down the status-endpoint states above. Verified to pass in all three
environment states: with a real key, with an invalid key, and with no `.env`
at all — the last being how a marker will run it.

> **Still outstanding — you must do this yourself.** The live Gemini path has
> never been verified end to end, because every automated environment used to
> build this project blocks `generativelanguage.googleapis.com` at the network
> layer. Run `python check_gemini.py` in `backend/` on your own machine before
> the viva.

## What's new in v11: 2 more small bugs found while building the User Manual

Found while capturing the screenshots for `VinoInsight_User_Manual.docx` —
another example of manual walkthrough testing catching things automated
tests don't:

- **PDF export dropped the "³" unit character.** `pdfReport.js` labelled
  units like "g/dm³", but jsPDF's standard font doesn't render that glyph,
  so every exported lab report silently showed "g/dm )" instead. The
  on-screen Results page was unaffected (browsers render it fine) — only
  the PDF export was broken, and only visible by actually opening an
  exported PDF rather than looking at the page that triggers it. Fixed by
  switching the PDF's unit labels to plain ASCII ("g/dm3").
- **Chatbot's static greeting always claimed "AI-generated."** The
  hardcoded welcome message shown before any question is asked had
  `ai: true` unconditionally, so the "AI-generated" badge appeared on it
  even with no Gemini API key configured (pure rule-based fallback mode).
  Real replies were unaffected — they already correctly used the backend's
  `ai_powered` flag (verified by `test_chat.py`). Fixed by setting the
  greeting's flag to `false`, since it isn't a model response at all.

## What's new in v10: Cleanup — dependencies, READMEs, hardcoded URLs

Closes the remaining "Should-complete" cleanup items from the project audit:

- **Removed the unused `html2canvas` dependency** from `vinoinsight/package.json`.
  It was listed as a dependency but never actually imported anywhere —
  `pdfReport.js` explicitly does its own drawing calls instead (see the
  comment at the top of that file) rather than a page-screenshot approach,
  so the dependency was dead weight.
- **Reconciled 3 conflicting READMEs into 1 source of truth.** This root
  README, `vinoinsight/README.md`, and `backend/README.md` had drifted out
  of sync — the frontend and backend READMEs still described login as a
  frontend-only mock and predictions as not persisted to a database, both
  long since implemented for real. Both sub-folder READMEs now point back
  to this file instead of duplicating (and re-drifting from) it.
- **Checked for hardcoded backend URLs**: confirmed there are none to fix.
  Every frontend file that calls the API imports the single `API_BASE`
  constant from `AuthContext.jsx` rather than hardcoding the URL itself
  (verified across `Predict.jsx`, `Compare.jsx`, `History.jsx`,
  `Dashboard.jsx`, `Trends.jsx`) — `Compare.jsx`'s two number inputs also
  use `step="any"` rather than a fixed step, so they were never at risk of
  the Density validation bug fixed in v9.

## What's new in v9: SHAP extended to all 5 outputs + 2 real bugs fixed via screenshot testing

Closes the remaining "SHAP Global & Local" gap (Task 5) and two bugs found
while producing screenshots for the User Manual/Reflective Report — proof
that this kind of manual walkthrough testing catches real issues automated
tests don't.

**SHAP extended to all 5 outputs, plus a genuine global explanation.**
Previously SHAP only explained the Quality Score model, and only as a
single-prediction ("local") explanation — there was no "global" explanation
of any kind, despite the Contextual Report claiming "SHAP Global & Local."
`backend/explain_recommend.py` now provides:
- **Local**: every prediction's response includes `shap_values_by_output`,
  a per-instance SHAP explanation for all 5 outputs (not just Quality
  Score). For the 4 classifiers, the explanation is for whichever class the
  model actually predicted for that wine.
- **Global**: a new `GET /api/shap/global` endpoint returns mean(|SHAP|)
  feature importance per output, computed once at startup from a fixed
  sample of the training data — the standard definition of a SHAP global
  explanation. Interestingly, this independently confirms the Aroma
  Profile circularity finding already disclosed in
  `Disclosure_Paragraphs_Task5_Task6.md`: its global importance gives
  *zero* weight to fixed_acidity, pH, and sulphates and all its weight to
  exactly the 4 features (alcohol, citric_acid, residual_sugar, volatile_
  acidity) its label is rule-derived from.
- The Results page now has a tab selector above the SHAP chart so a user
  can view the explanation for any of the 5 outputs, not just Quality
  Score (`Results.jsx`).

**Bug fix — Predict form couldn't actually be submitted with its own preset
values.** The Density field's native HTML5 `step` was `0.001`, but every
one of the 5 Wine Style presets (and the backend's own test fixture) uses a
4-decimal density like `0.9978`. The browser's built-in constraint
validation silently blocked the submit button and showed a "please enter a
valid value" tooltip — meaning the Predict form could never be submitted
with any of its own default presets loaded, only if a user happened to
manually retype Density to 3 decimals. Found via headless-browser
screenshot testing, fixed by tightening `step` to `0.0001`
(`Predict.jsx`).

**Bug fix — a blocked external resource crashed the entire page, not just
the 3D bottle.** `WineBottle3D.jsx` used `<Environment preset="city">`
from `@react-three/drei`, which fetches an HDR image from an external CDN
at runtime — quietly contradicting this same file's own documented design
goal ("No external photo/model files are used"). When that fetch is
blocked (a restricted network, corporate proxy, or offline demo), the
WebGL context crashes and — because there was no error boundary anywhere
in the render tree — it took down the *entire page* to a blank black
screen, not just the bottle component. Found via headless-browser
screenshot testing in this project's own build/test environment. Fixed by
removing the external HDR dependency entirely (replaced with a couple of
local point lights for a similar highlight, zero network dependency) and
adding a React error boundary around the 3D component as defense-in-depth,
so any future 3D rendering failure degrades to a small inline message
instead of blanking the page.

See `screenshots/` for full-app walkthrough screenshots (landing, signup,
buyer dashboard, Predict, Results with the new SHAP selector, History,
Trends, Compare, seller pending state, admin seller verification) captured
after these fixes, confirming the whole flow works end-to-end.

## What's new in v8: Fixed an unreachable "Luxury" price band

Closes a cleanup item from the project audit. `01_data_preparation.py`'s
`price_range()` function used thresholds (18/24/30) that were never checked
against this dataset's actual score distribution — the composite score's
real max on this data is ~29.75, so the "Luxury (£40+)" band (score ≥ 30)
was **mathematically unreachable**: 0 of 6,497 rows were ever labelled
Luxury, and the trained classifier's label encoder only ever learned 3 of
the 4 advertised price bands. A related latent bug in `consumer_segment()`
— `quality_range == "High" and "Premium" in price_range or "Luxury" in
price_range`, which due to Python's operator precedence ignored quality
entirely whenever price was Luxury — was masked by the same issue (it never
fired, since no row was ever priced Luxury) but would have started
mislabelling data the moment Luxury became reachable.

Both are fixed: price thresholds recalibrated against this dataset's actual
score distribution (13.7–29.75) so all four bands are genuinely reachable
(~13.7% Budget, ~59.6% Standard, ~22.5% Premium, ~4.2% Luxury), and the
consumer-segment condition now has explicit parentheses matching the
intended logic. Models were retrained on the corrected labels and verified
live: a high-alcohol/high-sulphates test wine now correctly predicts
`"price_range": "Luxury (£40+)"` through the running API, which was
impossible before this fix. See `cleanup_evidence.txt` for the before/after
label-distribution numbers.

## What's new in v7: Evidence-Based Class-Imbalance Handling + Baselines

Closes the "SMOTE" gap flagged in the project audit (Contextual Report Table 1
claims SMOTE as a differentiator; the code previously did not implement any
imbalance handling at all). Rather than bolting SMOTE onto every classifier
just to match the claim, both SMOTE and `class_weight="balanced"` were
actually tried and measured against a **majority-class baseline**
(`DummyClassifier(strategy="most_frequent")`) for every imbalanced target.
The technique used per target was chosen on that evidence, not by default:

| Target | Strategy used | Why |
|---|---|---|
| `quality_range` | `class_weight="balanced"` | Beat plain accuracy slightly (0.836 vs 0.832) **and** raised "Low" quality recall 2.0% → 16.3% |
| `price_range` | SMOTE | XGBoost has no simple `class_weight` option; SMOTE gave a genuine +6.7pt lift over baseline in 5-fold CV |
| `consumer_segment` | `class_weight="balanced"`, **not** SMOTE | SMOTE actually scored *below* the majority baseline here (0.729 vs 0.776 in CV) — a red flag caught by testing, not assumed away |
| `aroma_profile` | untouched | Classes are comparatively balanced already; label is rule-derived/circular (see limitations below), so "balancing" it wouldn't make the metric more meaningful |

Final 5-fold CV results (after the v8 price-band label fix below, which also
rebalanced these targets), all four classifiers showing a positive lift over
the majority-class baseline — the price_range and consumer_segment lifts are
now larger than in the original run, because the label fix reduced how
skewed those targets were toward one dominant class, making the trivial
"always guess majority" baseline weaker and the model's real lift more
visible:

| Target | Majority baseline | Model (CV accuracy) | Lift |
|---|---|---|---|
| quality_range | 0.766 | 0.823 (rf, class_weight) | +0.057 |
| price_range | 0.596 | 0.813 (xgb, smote) | +0.216 |
| consumer_segment | 0.667 | 0.784 (rf, class_weight) | +0.117 |
| aroma_profile | 0.452 | 0.999 (xgb, none)* | +0.547 |

\*See "Important Limitations" below — this one's near-perfect score is a
methodology artifact (circular label), not evidence the model generalises.

Full per-fold numbers, classification reports, and confusion matrices are in
`cross_validation_evidence.txt` and `final_training_evidence.txt`.

**Reproducing this (re-running the training scripts):** `05_cross_validation.py`
and `06_retrain_with_type.py` live in the repo root but (matching the existing
convention of `01_data_preparation.py` / `02_train_model.py`) read
`vino_prepared.csv` and write `models/...` as paths relative to the current
working directory, not the script location. To regenerate the live backend's
models, run them **with `backend/` as the working directory** and a copy of
`vino_prepared.csv` inside `backend/`:
```bash
cp vino_prepared.csv backend/vino_prepared.csv   # one-time, if not already there
cd backend
python3 ../06_retrain_with_type.py   # retrains and overwrites backend/models/*.pkl
python3 ../05_cross_validation.py    # 5-fold CV report only, does not write models
```

## What's new in v6: Real Prediction History + Automated Tests

Closes the "Database Storage" gap identified in the project audit: previously
no prediction was ever saved anywhere, and History/Dashboard/Trends all showed
hardcoded sample data. Now:

- Every prediction made by a **logged-in** user is saved to a new `predictions`
  MongoDB collection (`backend/predictions_db.py`). Anonymous predictions still
  work exactly as before, they just aren't saved (there's no user to attach
  them to).
- **History** shows your real saved predictions, not fabricated sample rows.
- **Dashboard** stat cards and "Recent Predictions" are computed from your
  real data (`GET /api/predictions/stats`, `GET /api/predictions`).
- **Trends** now charts your own prediction history over time (grouped by the
  date each prediction was made), instead of fabricated wine-vintage years —
  the model has no year/vintage input, so a literal year-based trend was never
  something it could honestly support. This substitution is documented in
  `predictions_db.py`'s module docstring and in the project audit.
- A new automated backend test suite (`backend/tests/`, run with `pytest`)
  covers `/api/predict`, `/api/predictions*`, `/api/signup`, `/api/login`,
  `/api/admin/*`, and `/api/chat` — 25 tests at the time of v6, since grown to
  **42** (see v12), run against an in-memory `mongomock` database so no real
  MongoDB server is required just to run the tests. See "Running the tests"
  below.
- Two real bugs were found and fixed while writing these tests: the chatbot's
  offline keyword fallback didn't match simple plurals (e.g. "tannins" didn't
  match the "tannin" keyword), and `/api/predict` returned a raw, unhelpful
  415 error instead of the intended friendly 400 message when called without
  a JSON body.

### Running the tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

## What's new in v5: Real Auth, Roles, Admin Verification, AI Chatbot

### 1. Buyer / Seller / Admin roles with real backend auth (MongoDB)
Previously login was a frontend-only mock. It's now backed by a real
**MongoDB** database (`backend/auth_db.py`), consistent with the database
choice stated in the original project proposal:
- Sign up as **Buyer** (instant access) or **Seller/Producer** (requires
  admin approval before seller features unlock).
- A default **Admin** account is seeded automatically the first time you
  run the backend: `admin@vinoinsight.ai` / `Admin@123`
- Admin logs in and goes to **Seller Verification** in the sidebar to
  approve or reject pending seller sign-ups.
- Until approved, a seller sees a "pending verification" banner on their
  dashboard, and seller-specific insights (Consumer Segment, Quality
  Improvement Recommendations) are visually locked on the Results page.
- The Dashboard's quick actions differ by role: Buyers see Compare Wines
  and food-pairing-oriented actions; Sellers see quality-improvement and
  price-positioning-oriented actions.

**Note on security scope:** tokens are a simple in-memory bearer scheme
(reset when the backend restarts) — adequate for a university FYP demo.
State in your report that a production system would use JWT with expiry,
HTTPS, and hashed-token storage.

#### Database Setup (MongoDB) — required, one-time

You need a MongoDB database for signup/login/admin approval to work.
Pick **one** of these two options:

**Option A — MongoDB Atlas (free cloud database, no local install, recommended)**
1. Go to https://www.mongodb.com/cloud/atlas/register and create a free account.
2. Create a free "M0" cluster (takes a couple of minutes to provision).
3. Under Database Access, create a database user with a username/password.
4. Under Network Access, add `0.0.0.0/0` (allow access from anywhere) for
   a student demo.
5. Click "Connect" -> "Drivers" and copy the connection string, which
   looks like:
   `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/`
6. Add it to your `backend/.env` file (same file used for the Gemini key):
   ```
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
   ```

**Option B — Local MongoDB Community Server**
1. Download and install from https://www.mongodb.com/try/download/community
2. Start the MongoDB service (on Windows this usually runs automatically
   as a service after install; you can also run `mongod` manually).
3. No `.env` entry needed — the app defaults to `mongodb://localhost:27017`.

If MongoDB isn't reachable, `python app.py` will fail immediately with a
clear message explaining what to fix, rather than a confusing error later.

### 2. Real AI-powered chatbot (Google Gemini, free tier)
The chatbot now calls a real generative AI model instead of only
keyword-matching, so it can answer *any* wine-related question, not just
a fixed list of topics.

**To enable it (free, no credit card required) — ONE-TIME setup:**
1. Go to https://aistudio.google.com/apikey and create a free API key.
2. In the `backend` folder, create a new file named exactly `.env`
   (in Notepad: File -> Save As -> filename `.env` -> "Save as type" ->
   "All Files", so it doesn't become `.env.txt`).
3. Put this single line inside it (replace with your real key):
   ```
   GEMINI_API_KEY=your-key-here
   ```
4. Save the file. Run `python app.py` as normal — from now on the key
   loads automatically **every time**, no terminal commands needed, even
   after closing and reopening the terminal.

**If you don't set a key**, the chatbot automatically falls back to an
offline knowledge base — the app still works, just with less open-ended
coverage. The chat UI shows an "AI-generated" tag under answers that came
from Gemini, so you can visually demonstrate the difference in your viva.

> **Superseded by v12.** The fallback described here was a 14-topic
> keyword FAQ when this section was written; it is now a 112-topic scored
> knowledge base (`backend/wine_knowledge.py`). See the v12 section at the
> top of this file for the current design.

### 3. Everything from previous updates is still included
- Landing page (white theme, Vivino-style layout, real photography)
- Realistic 3D wine bottle (LatheGeometry + glass material + canvas label)
- Wine Style selector on Predict (Still Red/White, Rosé, Sparkling, Dessert)
- `is_red` is now a genuine trained model feature (not just UI)
- Compare Wines page, PDF lab-report export, food pairing suggestions
- Dark/Light mode toggle in the dashboard top bar

## How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Runs at http://127.0.0.1:5000. Test: `curl http://127.0.0.1:5000/api/health`

On first run it connects to MongoDB (see "Database Setup" above) and seeds the admin account.

### Frontend
```bash
cd vinoinsight
npm install
npm start
```
Opens at http://localhost:3000

## Demo Walkthrough (recommended order for your viva)

1. Visit `/` — Landing page.
2. Click **Get Started** → Sign Up as a **Seller** (e.g. "Ravi Wines").
3. Try to log in — you'll see the pending-verification banner.
4. Open a second browser tab, log in as Admin
   (`admin@vinoinsight.ai` / `Admin@123`) → go to **Seller Verification**
   → Approve the seller.
5. Back in the seller tab, log out and log back in — full seller
   dashboard access unlocked.
6. Sign up a second account as **Buyer** — instant access, no approval
   needed. Show the different quick actions on their dashboard.
7. Run a **Predict** with different Wine Style presets.
8. Show the **3D bottle** (drag to rotate) and **Export Report (PDF)** on
   Results.
9. Use **Compare** to compare two wines.
10. Open the chatbot, ask a wine question, point out the "AI-generated"
    tag (if Gemini key configured).
11. Toggle **light/dark mode** in the top bar.

## Model Performance (with wine-type feature + evidence-based class-imbalance handling)

| Output | Model | Metric (held-out test split) |
|---|---|---|
| Quality Score | Random Forest Regressor | R²=0.488, MAE=0.452 |
| Quality Range | Random Forest Classifier (class_weight=balanced) | 83.6% accuracy, F1=0.829 |
| Price Range | XGBoost Classifier (SMOTE) | 81.7% accuracy, F1=0.817 (all 4 bands incl. Luxury reachable — see v8) |
| Aroma Profile | XGBoost Classifier | 100% accuracy* |
| Consumer Segment | Random Forest Classifier (class_weight=balanced) | 80.2% accuracy, F1=0.803 |

See the "v7" section above for the 5-fold cross-validation numbers (more
reliable than a single split) and majority-class baseline comparison.

*Aroma profile hit 100% because its label was rule-derived from the same
input features (see `01_data_preparation.py`). State this transparently
in your evaluation chapter.

## Important Limitations To State In Your Report

1. `price_range`, `aroma_profile`, and `consumer_segment` labels are
   rule-derived, not independently verified ground truth. The Aroma Profile
   case is a stronger form of this issue (its label is derived from the same
   features fed back into the model as inputs, so its ~100% accuracy is a
   circular-evaluation artifact, not evidence of real predictive power) —
   see `Disclosure_Paragraphs_Task5_Task6.md` for the full, report-ready
   explanation.
2. The model's only genuinely labelled training data is Vinho Verde-style
   red/white wine chemistry. Rosé/Sparkling/Dessert presets are realistic
   starting values, not independently validated for those styles.
3. Auth uses simple in-memory bearer tokens, not production-grade JWT/
   session security — acceptable for an academic prototype, flagged here
   as a known limitation and future-work item.
4. The chatbot's "AI-generated" answers depend on a Gemini API key being
   configured; without one, it runs in a smaller rule-based fallback mode.
5. The Proposal/Contextual Report describe the stack as including Node.js
   and the Kaggle Wine Reviews dataset. In the delivered system, Node.js is
   only the build-tool runtime for the React frontend (no separate Node.js
   backend was built — everything server-side is Flask), and only the UCI
   Wine Quality dataset was used for training (Kaggle Wine Reviews has no
   row-level key to join it to UCI, so combining them was not feasible
   without fabricating a mapping). See
   `Disclosure_Paragraphs_Task5_Task6.md` for the full, report-ready
   explanation of both.

## Remaining steps to reach full completion

The system itself is complete. What is left is verification that can only be
done outside the development sandbox, plus the write-up.

1. **Verify Gemini on your own machine** — run `python check_gemini.py` in
   `backend/` on the network you will demo from. This is the one thing that
   has never been confirmed end to end: every automated environment used to
   build this project blocks `generativelanguage.googleapis.com`, so the live
   AI path is tested only against a stubbed client. If it fails at the viva
   the chatbot silently drops to the offline knowledge base — still usable,
   but not the feature you want to be demonstrating.
   `GET /api/chat/status` reports `gemini-active` once a live call has
   genuinely succeeded (see v12).
2. **Screenshots** — 15 captured screenshots are already in `screenshots/`
   and embedded in the Reflective Report and User Manual. Recapture only if
   you change the UI.
3. Write up the Testing/Evaluation chapter using the accuracy numbers
   above plus the cross-validation script (`05_cross_validation.py`) and the
   Test Cases Report.
4. Optional: deploy backend (Render/Railway) + frontend (Vercel/Netlify)
   for a live demo link.

## Packaging the project for submission

**Never zip this folder without excluding `backend/.env`** — it holds a real
API key, and `.gitignore` does not apply to zip files. Use:

```bash
zip -r VinoInsight_Submission.zip vinoinsight \
  -x "*/node_modules/*" -x "*/__pycache__/*" -x "*/.pytest_cache/*" \
  -x "*/build/*" -x "*/.env"
```

`backend/.env.example` is safe to ship and documents every setting the
backend reads.

### Package version notes
- `@react-three/fiber@8.15.19` / `@react-three/drei@9.99.0` are pinned
  for React 18 compatibility.
- Backend uses `google-genai` (the current, non-deprecated Google SDK) —
  don't install the old `google-generativeai` package instead.
