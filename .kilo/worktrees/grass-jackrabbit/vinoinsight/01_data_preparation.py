"""
VinoInsight AI - Step 1: Data Preparation
-------------------------------------------
Loads the UCI Wine Quality dataset (red+white merged), cleans it,
and engineers derived labels for the outputs that have no direct
ground-truth in the raw data: price_range, aroma_profile, consumer_segment.

Why derived labels?
The contextual report proposes 5 outputs (quality score, quality range,
price range, aroma, consumer segment). Only "quality" exists as a real
label in the UCI dataset. Wine price/aroma/segment datasets that pair
with physicochemical values do not publicly exist together, so these
three outputs are generated using domain-informed rules (based on
enology literature cited in your report, e.g. Cortez et al. 2009,
Moreira et al. 2024). Document this clearly in your reflective report
as a stated methodological assumption / limitation.
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------
df = pd.read_csv("dataset1/wine_quality_merged.csv")
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
print(f"Loaded {len(df)} rows, {df.shape[1]} columns")
print(df.isnull().sum().sum(), "missing values found")

# ---------------------------------------------------------
# 2. Target 1: Quality Score (already real -> just use 'quality')
# ---------------------------------------------------------
df["quality_score"] = df["quality"]

# ---------------------------------------------------------
# 3. Target 2: Quality Range (bucket the real quality score)
# ---------------------------------------------------------
def quality_range(q):
    if q <= 4:
        return "Low"
    elif q <= 6:
        return "Medium"
    else:
        return "High"

df["quality_range"] = df["quality_score"].apply(quality_range)

# ---------------------------------------------------------
# 4. Target 3: Price Range (derived rule)
# Rationale: higher quality + higher alcohol + moderate-to-high sulphates
# typically correlate with higher-priced wines (supported by Moreira et al. 2024
# who found alcohol and rating as strong price predictors on Vivino data).
#
# FIX (project audit, cleanup task): the original thresholds (18/24/30) were
# picked without checking against this dataset's actual score distribution.
# The composite score's real range on this data is ~13.7 to ~29.75 (max
# possible is close to that too, given realistic alcohol/sulphates values),
# so a "< 30" ceiling for Premium meant the score could NEVER reach the
# Luxury threshold — 0 of 6,497 rows were ever labelled "Luxury (£40+)",
# and the trained classifier's label encoder only ever learned 3 classes
# (Budget, Standard, Premium), making "Luxury" a class the model could
# mathematically never predict. Thresholds below are re-calibrated against
# this dataset's actual score distribution (see cleanup_evidence.txt for the
# percentile analysis) so all four advertised price bands are genuinely
# reachable: ~13.7% Budget, ~59.6% Standard, ~22.5% Premium, ~4.2% Luxury.
# ---------------------------------------------------------
def price_range(row):
    score = (row["quality_score"] * 2) + (row["alcohol"] * 0.8) + (row["sulphates"] * 3)
    if score < 19:
        return "Budget (< £10)"
    elif score < 23:
        return "Standard (£10-£20)"
    elif score < 26:
        return "Premium (£20-£40)"
    else:
        return "Luxury (£40+)"

df["price_range"] = df.apply(price_range, axis=1)

# ---------------------------------------------------------
# 5. Target 4: Aroma Profile (derived rule)
# Rationale: residual sugar -> sweetness/fruitiness; volatile acidity -> sharp/vinegar notes;
# alcohol -> body/warmth; citric acid -> freshness. These mappings are simplified but
# grounded in general enology knowledge (see Molnar 2022 for feature-to-outcome reasoning).
# ---------------------------------------------------------
def aroma_profile(row):
    if row["residual_sugar"] > 6 and row["citric_acid"] > 0.3:
        return "Sweet & Fruity"
    elif row["volatile_acidity"] > 0.6:
        return "Sharp & Earthy"
    elif row["alcohol"] > 11.5:
        return "Full-Bodied & Warm"
    elif row["citric_acid"] > 0.4:
        return "Crisp & Fresh"
    else:
        return "Balanced & Floral"

df["aroma_profile"] = df.apply(aroma_profile, axis=1)

# ---------------------------------------------------------
# 6. Target 5: Consumer Segment (derived from quality + price combo)
#
# FIX (project audit, cleanup task): the original condition
#   `quality_range == "High" and "Premium" in price_range or "Luxury" in price_range`
# relies on Python's `and`/`or` precedence (and binds tighter than or), so it
# actually evaluated as:
#   (quality_range == "High" and "Premium" in price_range) or ("Luxury" in price_range)
# which meant ANY Luxury-priced wine was labelled "Connoisseurs" regardless
# of its quality_range — a Low-quality, Luxury-priced wine would have been
# (wrongly) called a Connoisseurs-segment wine. This never actually showed
# up in the trained model (0 rows were ever priced "Luxury" before the
# price_range fix above), but it was a latent bug that would have started
# mislabelling data the moment "Luxury" became reachable. Fixed by making
# the intended condition explicit with parentheses: High quality AND
# (Premium OR Luxury) price -> Connoisseurs.
# ---------------------------------------------------------
def consumer_segment(row):
    if row["quality_range"] == "High" and ("Premium" in row["price_range"] or "Luxury" in row["price_range"]):
        return "Connoisseurs"
    elif row["quality_range"] == "High":
        return "Wine Enthusiasts"
    elif row["price_range"] == "Budget (< £10)":
        return "Budget Buyers"
    else:
        return "Casual Drinkers"

df["consumer_segment"] = df.apply(consumer_segment, axis=1)

# ---------------------------------------------------------
# 7. Save cleaned + labeled dataset
# ---------------------------------------------------------
df.to_csv("vino_prepared.csv", index=False)

print("\n--- Label distributions (sanity check) ---")
for col in ["quality_range", "price_range", "aroma_profile", "consumer_segment"]:
    print(f"\n{col}:")
    print(df[col].value_counts())

print("\nSaved cleaned dataset -> vino_prepared.csv")
print(f"Final shape: {df.shape}")
