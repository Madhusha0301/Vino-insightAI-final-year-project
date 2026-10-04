"""
VinoInsight AI - Step 5: 5-Fold Cross-Validation
------------------------------------------------------------------
A single train/test split can be misleading (lucky/unlucky split).
This script runs 5-fold cross-validation for all 5 models and reports
mean +/- std, which is what examiners expect in a Testing/Evaluation
chapter (matches your report Section 4.6: "five-fold cross-validation").

--------------------------------------------------------------------
CHANGES (project audit, Tasks 3 & 4):
--------------------------------------------------------------------
1. Class-imbalance handling is now included INSIDE the cross-validation
   pipeline, matching the evidence-based, per-target strategy settled on
   in 06_retrain_with_type.py (see that file's docstring for the full
   before/after numbers that justified each choice):
     - quality_range    -> class_weight="balanced"
     - price_range      -> SMOTE (via imblearn's Pipeline, which re-fits
       SMOTE separately on each fold's training portion only, so no
       synthetic points derived from a fold's held-out data ever leak
       into that fold's training)
     - consumer_segment -> class_weight="balanced" (SMOTE measured WORSE
       than the majority-class baseline for this target — see below)
     - aroma_profile    -> untouched (comparatively balanced already;
       label is rule-derived/circular, see project audit Section 9)
2. A DummyClassifier(strategy="most_frequent") baseline is now reported
   alongside every classifier — "always guess the majority class" is
   the correct academic baseline to compare against, and was previously
   missing (a "missing baselines" gap flagged in the project audit).
   The gap between the dummy baseline and the real model is the actual,
   honest measure of what the model has learned.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

df = pd.read_csv("vino_prepared.csv")
df["is_red"] = (df["type"] == "red").astype(int) if "type" in df.columns else 0
FEATURES = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide",
    "density", "ph", "sulphates", "alcohol", "is_red"
]
X = df[FEATURES]

print("===== 5-FOLD CROSS-VALIDATION RESULTS =====\n")

# 1. Quality Score (regression) -> R2
kf = KFold(n_splits=5, shuffle=True, random_state=42)
reg = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)
scores = cross_val_score(reg, X, df["quality_score"], cv=kf, scoring="r2")
print(f"Quality Score (R2):        {scores.mean():.3f} ± {scores.std():.3f}   folds={np.round(scores,3)}")


def cv_classifier(target_col, model_type="rf", imbalance_strategy="none"):
    """imbalance_strategy: "none" | "smote" | "class_weight" — see module docstring."""
    y = df[target_col]
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    class_weight = "balanced" if imbalance_strategy == "class_weight" else None
    if model_type == "rf":
        base_model = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1, class_weight=class_weight)
    else:
        base_model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                                    eval_metric="mlogloss", random_state=42)

    # --- Majority-class baseline (Task 4: previously missing) ---
    dummy = DummyClassifier(strategy="most_frequent")
    dummy_scores = cross_val_score(dummy, X, y_enc, cv=skf, scoring="accuracy")
    print(f"{target_col + ' (majority-class baseline)':40s} {dummy_scores.mean():.3f} ± {dummy_scores.std():.3f}")

    if imbalance_strategy == "smote":
        pipeline = ImbPipeline([("smote", SMOTE(random_state=42)), ("model", base_model)])
        scores = cross_val_score(pipeline, X, y_enc, cv=skf, scoring="accuracy")
    else:
        scores = cross_val_score(base_model, X, y_enc, cv=skf, scoring="accuracy")
    label = f"{target_col} ({model_type}, {imbalance_strategy})"
    print(f"{label:40s} {scores.mean():.3f} ± {scores.std():.3f}   folds={np.round(scores,3)}")
    lift = scores.mean() - dummy_scores.mean()
    print(f"{'  -> lift over majority-class baseline':40s} {'+' if lift >= 0 else ''}{lift:.3f}\n")


cv_classifier("quality_range", "rf", imbalance_strategy="class_weight")
cv_classifier("price_range", "xgb", imbalance_strategy="smote")
cv_classifier("aroma_profile", "xgb", imbalance_strategy="none")  # comparatively balanced; circular label (see audit Section 9)
cv_classifier("consumer_segment", "rf", imbalance_strategy="class_weight")  # SMOTE measured worse than baseline here

print("\nInterpretation for your report:")
print("- Low std (e.g. < 0.03) across folds = model is stable, not overfitting to one split.")
print("- The 'lift over majority-class baseline' row is the honest measure of what each")
print("  model has actually learned, beyond what a trivial always-guess-the-common-class")
print("  rule would already get for free on this imbalanced data.")
print("- Compare these SMOTE-enabled numbers to a plain (non-SMOTE) run to discuss the")
print("  accuracy/minority-recall trade-off explicitly (see smote_before_after evidence).")
