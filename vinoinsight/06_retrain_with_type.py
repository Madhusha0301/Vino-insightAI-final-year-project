"""
VinoInsight AI - Step 6: Retrain With Wine Type Feature + Class-Imbalance Handling
------------------------------------------------------------------
Adds 'type' (red/white, one-hot encoded) as a genuine model feature.
This is a real accuracy improvement AND makes the "Wine Style" selector
on the frontend meaningful (not just cosmetic) for the two styles that
actually exist as labelled data (red, white).

For styles with no labelled chemistry data (Rosé, Sparkling, Dessert,
Fortified) the frontend applies transparent presentation-layer
adjustments only (see WINE_STYLES presets in Predict.jsx) — this script
does NOT fabricate training data for those styles, since doing so would
not be honest, defensible research practice for the report.

--------------------------------------------------------------------
CHANGE (project audit, Task 3): class-imbalance handling, evidence-based
--------------------------------------------------------------------
The Contextual Report (Table 1, Research Gap) claims SMOTE as a
differentiator. Earlier versions of this script did not implement any
imbalance handling at all — an undisclosed gap between documentation
and code.

Rather than bolting on SMOTE everywhere just to match the claim, both
SMOTE and class_weight="balanced" were actually tried and measured
against a majority-class baseline for every imbalanced target (see
smote_before_after_evidence.txt and cross_validation_evidence.txt).
The result differs by target, and the technique actually used per
target was chosen on that evidence:

  - quality_range  -> class_weight="balanced". Beat plain accuracy
    slightly (0.836 vs 0.832 on the held-out split) AND raised "Low"
    quality recall from 2.0% to 16.3%. Strictly better on both axes.
  - price_range    -> SMOTE. XGBoost has no built-in class_weight
    option as simple as RandomForest's; SMOTE gave a genuine positive
    lift over the majority baseline (+6.7pts in 5-fold CV) with a
    reasonable, disclosed accuracy trade-off, and raised "Budget"
    recall from 20.0% to 31.4%.
  - consumer_segment -> class_weight="balanced", NOT SMOTE. This is
    the one target where SMOTE actually measured WORSE than simply
    always guessing the majority class (0.729 vs 0.776 baseline in
    5-fold CV) — a red flag that would not survive scrutiny.
    class_weight="balanced" instead scored above baseline (0.827)
    while still raising "Budget Buyers" recall from ~0% to 20%.
  - aroma_profile  -> left untouched. Its classes are comparatively
    balanced already (least-common ~8.5%) and its label is rule-derived
    from the same features it's predicted from (see project audit,
    Section 9) — "fixing" the balance of an already-circular label
    would not make the metric more meaningful, just differently
    misleading.

This is a stronger, more defensible Methodology section than "we used
SMOTE because we said we would": it shows the choice was evidence-based
per target rather than applied uniformly on faith.
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    r2_score, mean_absolute_error, accuracy_score, f1_score,
    classification_report, confusion_matrix,
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

os.makedirs("models", exist_ok=True)

df = pd.read_csv("vino_prepared.csv")
df["is_red"] = (df["type"] == "red").astype(int)

FEATURES = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide",
    "density", "ph", "sulphates", "alcohol", "is_red"
]
X = df[FEATURES]

results_summary = {}

# Quality Score -> Regression (imbalance handling does not apply to regression)
y = df["quality_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
reg = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)
reg.fit(X_train, y_train)
pred = reg.predict(X_test)
results_summary["quality_score (regression)"] = f"R2={r2_score(y_test, pred):.3f}, MAE={mean_absolute_error(y_test, pred):.3f}"
joblib.dump(reg, "models/quality_score_model.pkl")


def train_classifier(target_col, model_type="rf", imbalance_strategy="none"):
    """
    imbalance_strategy: "none" | "smote" | "class_weight"
    See module docstring for which strategy was chosen for each target
    and why, based on measured evidence rather than assumption.
    """
    y = df[target_col]
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    X_fit, y_fit = X_train, y_train
    if imbalance_strategy == "smote":
        smote = SMOTE(random_state=42)
        X_fit, y_fit = smote.fit_resample(X_train, y_train)

    class_weight = "balanced" if imbalance_strategy == "class_weight" else None
    if model_type == "rf":
        model = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1, class_weight=class_weight)
    else:
        model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                               eval_metric="mlogloss", random_state=42)
    model.fit(X_fit, y_fit)
    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred, average="weighted")
    results_summary[f"{target_col} ({model_type}, {imbalance_strategy})"] = f"Accuracy={acc:.3f}, F1(weighted)={f1:.3f}"

    print(f"\n----- {target_col} [{imbalance_strategy}] : classification report on the REAL test split -----")
    print(classification_report(y_test, pred, target_names=[str(c) for c in le.classes_], zero_division=0))
    print(f"Confusion matrix (rows=actual, cols=predicted), classes={list(le.classes_)}:")
    print(confusion_matrix(y_test, pred))

    joblib.dump(model, f"models/{target_col}_model.pkl")
    joblib.dump(le, f"models/{target_col}_encoder.pkl")
    return model, le


train_classifier("quality_range", "rf", imbalance_strategy="class_weight")
train_classifier("price_range", "xgb", imbalance_strategy="smote")
train_classifier("consumer_segment", "rf", imbalance_strategy="class_weight")
train_classifier("aroma_profile", "xgb", imbalance_strategy="none")

joblib.dump(FEATURES, "models/feature_list.pkl")

print("\n===== MODEL PERFORMANCE (with wine-type feature + evidence-based imbalance handling) =====")
for k, v in results_summary.items():
    print(f"{k:45s} -> {v}")
