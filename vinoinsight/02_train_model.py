"""
VinoInsight AI - Step 2: Model Training
------------------------------------------
Trains models for all 5 outputs using the prepared dataset.
- quality_score      -> Regression (Random Forest Regressor)
- quality_range      -> Classification (Random Forest Classifier)
- price_range        -> Classification (XGBoost Classifier)
- aroma_profile       -> Classification (XGBoost Classifier)
- consumer_segment   -> Classification (Random Forest Classifier)

Saves trained models + label encoders to /models for later use in the Flask API.
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    r2_score, mean_absolute_error,
    accuracy_score, f1_score, classification_report
)
from xgboost import XGBClassifier

os.makedirs("models", exist_ok=True)

# ---------------------------------------------------------
# 1. Load prepared data
# ---------------------------------------------------------
df = pd.read_csv("vino_prepared.csv")

FEATURES = [
    "fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar",
    "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide",
    "density", "ph", "sulphates", "alcohol"
]
X = df[FEATURES]

results_summary = {}

# ---------------------------------------------------------
# 2. Quality Score -> Regression
# ---------------------------------------------------------
y = df["quality_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

reg = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42, n_jobs=-1)
reg.fit(X_train, y_train)
pred = reg.predict(X_test)
r2 = r2_score(y_test, pred)
mae = mean_absolute_error(y_test, pred)
results_summary["quality_score (regression)"] = f"R2={r2:.3f}, MAE={mae:.3f}"
joblib.dump(reg, "models/quality_score_model.pkl")

# ---------------------------------------------------------
# Helper for classification targets
# ---------------------------------------------------------
def train_classifier(target_col, model_type="rf"):
    y = df[target_col]
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    if model_type == "rf":
        model = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)
    else:
        model = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.1,
            eval_metric="mlogloss", random_state=42
        )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred, average="weighted")
    results_summary[f"{target_col} ({model_type})"] = f"Accuracy={acc:.3f}, F1={f1:.3f}"

    joblib.dump(model, f"models/{target_col}_model.pkl")
    joblib.dump(le, f"models/{target_col}_encoder.pkl")
    return model, le

# ---------------------------------------------------------
# 3. Quality Range -> Random Forest Classifier
# ---------------------------------------------------------
train_classifier("quality_range", model_type="rf")

# ---------------------------------------------------------
# 4. Price Range -> XGBoost Classifier
# ---------------------------------------------------------
train_classifier("price_range", model_type="xgb")

# ---------------------------------------------------------
# 5. Aroma Profile -> XGBoost Classifier
# ---------------------------------------------------------
train_classifier("aroma_profile", model_type="xgb")

# ---------------------------------------------------------
# 6. Consumer Segment -> Random Forest Classifier
# ---------------------------------------------------------
train_classifier("consumer_segment", model_type="rf")

# ---------------------------------------------------------
# Save feature list for API use
# ---------------------------------------------------------
joblib.dump(FEATURES, "models/feature_list.pkl")

print("\n===== MODEL PERFORMANCE SUMMARY =====")
for k, v in results_summary.items():
    print(f"{k:35s} -> {v}")

print("\nAll models saved in /models folder.")
