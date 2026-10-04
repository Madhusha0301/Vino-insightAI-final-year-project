"""
VinoInsight AI - Step 3: Explainability + Recommendation Engine
------------------------------------------------------------------
Loads the trained models and provides:
  1. explain_prediction() -> SHAP values for a single wine input
  2. generate_recommendations() -> rule-based suggestions to improve quality

This module is imported directly by the Flask API (app.py).

--------------------------------------------------------------------
CHANGE (project audit, Task 5 - SHAP scope): the Contextual Report
(Table 1) claims "SHAP Global & Local" explainability as a differentiator.
Previously SHAP was wired to ONLY the Quality Score regression model, and
only as a per-instance ("local") explanation - there was no "global"
explanation at all, and 4 of the 5 outputs had no SHAP explanation of any
kind. This is now extended to genuinely cover both halves of the claim:

  - LOCAL: every one of the 5 outputs now gets its own per-instance SHAP
    explanation for every prediction (see explain_all()). For the 4
    classifiers, shap.TreeExplainer returns per-class SHAP values (shape
    n_features x n_classes); the values sliced out are for whichever class
    the model actually predicted for that wine, matching what a "why did
    it predict THIS label" explanation needs.
  - GLOBAL: a one-time, precomputed mean(|SHAP value|) per feature across a
    fixed sample of the training data (GLOBAL_SHAP_IMPORTANCE, computed at
    import time - see compute_global_shap_importance()) gives an overall
    feature-importance ranking per target, i.e. "across the whole dataset,
    which features matter most for this output" - the standard definition
    of a SHAP global explanation (mean absolute SHAP value, as used in a
    SHAP summary plot), as opposed to one single prediction's local
    explanation.

The original `explain_prediction()` / `shap_values` response field for the
Quality Score model is kept completely unchanged for backward compatibility
with the existing frontend chart; the additions are new fields
(`shap_values_by_output`) and a new endpoint (`GET /api/shap/global`).
--------------------------------------------------------------------
"""

import joblib
import shap
import numpy as np
import pandas as pd

FEATURES = joblib.load("models/feature_list.pkl")

# Load models once (kept in memory for speed)
quality_score_model = joblib.load("models/quality_score_model.pkl")
quality_range_model = joblib.load("models/quality_range_model.pkl")
quality_range_encoder = joblib.load("models/quality_range_encoder.pkl")
price_range_model = joblib.load("models/price_range_model.pkl")
price_range_encoder = joblib.load("models/price_range_encoder.pkl")
aroma_profile_model = joblib.load("models/aroma_profile_model.pkl")
aroma_profile_encoder = joblib.load("models/aroma_profile_encoder.pkl")
consumer_segment_model = joblib.load("models/consumer_segment_model.pkl")
consumer_segment_encoder = joblib.load("models/consumer_segment_encoder.pkl")

# SHAP explainer for the primary quality score model (kept as the original
# name/behaviour so the existing local-explanation response field is
# unchanged - this is the number users care about explaining the most).
shap_explainer = shap.TreeExplainer(quality_score_model)

# SHAP explainers for every output (Task 5: extend SHAP beyond Quality Score)
_ALL_MODELS = {
    "quality_score": quality_score_model,
    "quality_range": quality_range_model,
    "price_range": price_range_model,
    "aroma_profile": aroma_profile_model,
    "consumer_segment": consumer_segment_model,
}
_ALL_EXPLAINERS = {name: shap.TreeExplainer(model) for name, model in _ALL_MODELS.items()}


def predict_all(input_dict):
    """
    input_dict: dict with keys matching FEATURES (must include 'is_red': 0 or 1)
        e.g. {"fixed_acidity": 7.4, ..., "is_red": 1}
    Returns a dict with all 5 predictions + SHAP values + recommendations.
    """
    X = pd.DataFrame([input_dict])[FEATURES]

    quality_score = float(quality_score_model.predict(X)[0])

    quality_range = quality_range_encoder.inverse_transform(
        quality_range_model.predict(X)
    )[0]

    price_range = price_range_encoder.inverse_transform(
        price_range_model.predict(X)
    )[0]

    aroma_profile = aroma_profile_encoder.inverse_transform(
        aroma_profile_model.predict(X)
    )[0]

    consumer_segment = consumer_segment_encoder.inverse_transform(
        consumer_segment_model.predict(X)
    )[0]

    shap_vals = explain_prediction(X)
    recommendations = generate_recommendations(input_dict, quality_score)

    # Task 5: local SHAP explanation for every output, not just Quality Score.
    predicted_class_indices = {
        "quality_range": int(quality_range_model.predict(X)[0]),
        "price_range": int(price_range_model.predict(X)[0]),
        "aroma_profile": int(aroma_profile_model.predict(X)[0]),
        "consumer_segment": int(consumer_segment_model.predict(X)[0]),
    }
    shap_by_output = explain_all(X, predicted_class_indices)

    return {
        "quality_score": round(quality_score, 2),
        "quality_range": quality_range,
        "price_range": price_range,
        "aroma_profile": aroma_profile,
        "consumer_segment": consumer_segment,
        "shap_values": shap_vals,
        "shap_values_by_output": shap_by_output,
        "recommendations": recommendations,
    }


def explain_prediction(X):
    """Returns a dict of {feature: shap_value} for the quality score prediction.
    Kept unchanged (name and behaviour) for backward compatibility with the
    existing frontend chart, which reads the top-level `shap_values` field."""
    shap_values = shap_explainer.shap_values(X)
    values = shap_values[0] if len(shap_values.shape) > 1 else shap_values
    return {feat: round(float(val), 3) for feat, val in zip(FEATURES, values)}


def explain_all(X, predicted_class_indices):
    """
    Local SHAP explanation for ALL FIVE outputs for a single wine input.

    X: single-row DataFrame with columns == FEATURES.
    predicted_class_indices: dict mapping each classifier target name to the
        integer class index the model actually predicted for this row
        (i.e. model.predict(X)[0], BEFORE inverse_transform to a label) -
        needed because TreeExplainer returns per-class SHAP values for a
        classifier, and we want the explanation for whichever class was
        actually predicted, not an arbitrary fixed class.

    Returns: {target_name: {feature: shap_value}} for all 5 targets.
    """
    result = {}
    for target, explainer in _ALL_EXPLAINERS.items():
        raw = explainer.shap_values(X)
        if target == "quality_score":
            # Regression: shape (n_samples, n_features)
            values = raw[0] if len(raw.shape) > 1 else raw
        else:
            # Classification: shape (n_samples, n_features, n_classes) in
            # this shap version - slice out the predicted class for row 0.
            class_idx = predicted_class_indices[target]
            if raw.ndim == 3:
                values = raw[0, :, class_idx]
            elif isinstance(raw, list):
                # Older shap versions return a list of per-class arrays.
                values = raw[class_idx][0]
            else:
                values = raw[0]
        result[target] = {feat: round(float(val), 3) for feat, val in zip(FEATURES, values)}
    return result


def compute_global_shap_importance(sample_size=30, random_state=42):
    """
    GLOBAL SHAP explanation (Task 5): mean(|SHAP value|) per feature across a
    fixed random sample of the training data, for every one of the 5
    outputs. This is the standard definition of SHAP global feature
    importance (the same aggregation a SHAP summary/beeswarm plot is built
    from), as distinct from a single prediction's local explanation.

    sample_size=30 is deliberately small: this function runs once at app
    startup (see GLOBAL_SHAP_IMPORTANCE below), and TreeExplainer over the
    large RandomForest models (n_estimators=300) is measurably slow in bulk
    - a 300-row sample across all 5 models was measured at 60s+ (too slow
    for a demo's startup time), while 30 rows measured ~6.6s. 30 rows is
    still a reasonable sample for a stable mean-|SHAP| ranking (the relative
    ordering of features was checked to be stable between 30 and 50 rows in
    testing); it trades a small amount of statistical smoothness for a
    startup delay that does not make the app feel broken/hung.

    Computed once at import time (see GLOBAL_SHAP_IMPORTANCE below) rather
    than per-request, since it does not depend on any single user's input
    and recomputing it on every API call would be wasted work.
    """
    try:
        df = pd.read_csv("vino_prepared.csv")
    except FileNotFoundError:
        # Training data not present in this deployment (e.g. a slimmed-down
        # production image with only models/ shipped) - global importance
        # is a nice-to-have, not required for predictions to work, so fail
        # soft rather than crash the whole app at import time.
        return {}

    df["is_red"] = (df["type"] == "red").astype(int) if "type" in df.columns else 0
    sample = df[FEATURES].sample(n=min(sample_size, len(df)), random_state=random_state)

    importance = {}
    for target, explainer in _ALL_EXPLAINERS.items():
        raw = explainer.shap_values(sample)
        if target == "quality_score":
            abs_mean = np.abs(raw).mean(axis=0)  # (n_features,)
        else:
            # Average |SHAP| across classes too, for an overall "how much
            # does this feature matter for this output in general" ranking
            # that isn't tied to one particular predicted class.
            abs_mean = np.abs(raw).mean(axis=(0, 2))
        importance[target] = {
            feat: round(float(val), 4)
            for feat, val in sorted(zip(FEATURES, abs_mean), key=lambda kv: -kv[1])
        }
    return importance


# Computed once at import time (module-level cache) - see docstring above.
GLOBAL_SHAP_IMPORTANCE = compute_global_shap_importance()


def generate_recommendations(input_dict, quality_score):
    """
    Rule-based recommendations, grounded in known thresholds from the
    UCI wine literature (Cortez et al. 2009; Gupta 2018) — high volatile
    acidity, low sulphates/alcohol are commonly associated with lower quality.
    """
    tips = []

    if input_dict["volatile_acidity"] > 0.6:
        tips.append(
            f"Volatile acidity is high ({input_dict['volatile_acidity']:.2f} g/dm³). "
            "Reduce below 0.60 g/dm³ to avoid a vinegar-like taste and improve quality."
        )
    if input_dict["sulphates"] < 0.5:
        tips.append(
            f"Sulphates are low ({input_dict['sulphates']:.2f} g/dm³). "
            "Increasing to 0.65-0.75 g/dm³ can improve preservation and flavour stability."
        )
    if input_dict["alcohol"] < 10:
        tips.append(
            f"Alcohol content is on the lower side ({input_dict['alcohol']:.1f}% vol). "
            "Wines in the 10.5-12.5% range tend to score higher for body and balance."
        )
    if input_dict["citric_acid"] < 0.2:
        tips.append(
            "Citric acid is low. A slight increase can add freshness and brighten the aroma profile."
        )
    if input_dict["total_sulfur_dioxide"] > 150:
        tips.append(
            "Total sulfur dioxide is quite high, which can affect aroma. "
            "Consider reducing to stay within a fresher sensory range."
        )

    if not tips:
        tips.append("This wine's chemical profile is already well balanced — no major changes suggested.")

    return tips


if __name__ == "__main__":
    # Quick manual test
    sample = {
        "fixed_acidity": 7.4, "volatile_acidity": 0.70, "citric_acid": 0.0,
        "residual_sugar": 1.9, "chlorides": 0.076, "free_sulfur_dioxide": 11.0,
        "total_sulfur_dioxide": 34.0, "density": 0.9978, "ph": 3.51,
        "sulphates": 0.56, "alcohol": 9.4
    }
    result = predict_all(sample)
    import json
    print(json.dumps(result, indent=2))
