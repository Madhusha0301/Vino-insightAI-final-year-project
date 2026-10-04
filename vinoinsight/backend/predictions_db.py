"""
VinoInsight AI - Prediction History & Analytics (MongoDB)
------------------------------------------------------------------
Added to close a gap identified in the FYP Readiness/Completion audit:
the Contextual Report's "Database Storage" feature (Table 2) promised
that predictions, SHAP data, and recommendations would be persisted to
MongoDB. Previously nothing was ever saved — History, the Dashboard's
"Recent Predictions", and Trends all rendered hardcoded sample arrays.

This module follows the same connection/pattern as auth_db.py.

Design decision (documented, not hidden): the trained model has no
year/vintage input at all (the UCI dataset has no year column), so a
literal "year-based trend analysis" as worded in the Contextual Report
is not something the model can honestly support. Instead, trends are
computed over the user's own prediction *history* (grouped by the date
each prediction was made), which is the trend data that genuinely
exists. This substitution is called out explicitly in the project audit
document (Section 5) and should be described the same way in the Thesis.

Also note: price_range is a categorical output (e.g. "Standard
(£10-£20)"), not a numeric value, so there is no honest way to compute
a numeric "average price" trend line the way the old mock data faked.
Trends therefore reports a price *distribution* per day instead of a
fabricated average price number.
"""

import os
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone

from pymongo import MongoClient, DESCENDING

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "vinoinsight")


def _get_collection():
    """
    Lazily resolves the `predictions` collection using the SAME MongoClient
    connection auth_db.py already established. Kept lazy (not connected at
    import time) so that predictions_db can also be imported/tested with a
    mongomock client without requiring a real MongoDB server, and so that
    app.py's prediction endpoint does not hard-fail if only the auth layer
    can reach MongoDB.
    """
    global _client, _collection
    if _collection is not None:
        return _collection
    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    _collection = _client[DB_NAME]["predictions"]
    _collection.create_index([("user_id", 1), ("created_at", DESCENDING)])
    return _collection


_client = None
_collection = None


def set_collection(collection):
    """Test hook: inject a mongomock (or any pymongo-compatible) collection directly."""
    global _collection
    _collection = collection


def _public(doc):
    if not doc:
        return None
    return {
        "id": doc["_id"],
        "created_at": doc["created_at"],
        "wine_style": doc.get("wine_style"),
        "inputs": doc.get("inputs"),
        "quality_score": doc.get("quality_score"),
        "quality_range": doc.get("quality_range"),
        "price_range": doc.get("price_range"),
        "aroma_profile": doc.get("aroma_profile"),
        "consumer_segment": doc.get("consumer_segment"),
        "shap_values": doc.get("shap_values"),
        "recommendations": doc.get("recommendations"),
    }


def save_prediction(user_id, wine_style, result):
    """
    Persists one prediction result for a logged-in user.
    `result` is the dict returned by explain_recommend.predict_all()
    (already includes inputs, the 5 outputs, shap_values, recommendations).
    Returns the public representation of the saved record, or None if
    user_id is falsy (anonymous/unauthenticated predictions are not saved
    — there is no user to attach history to).
    """
    if not user_id:
        return None
    doc = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "wine_style": wine_style,
        "inputs": result.get("inputs"),
        "quality_score": result.get("quality_score"),
        "quality_range": result.get("quality_range"),
        "price_range": result.get("price_range"),
        "aroma_profile": result.get("aroma_profile"),
        "consumer_segment": result.get("consumer_segment"),
        "shap_values": result.get("shap_values"),
        "recommendations": result.get("recommendations"),
    }
    _get_collection().insert_one(doc)
    return _public(doc)


def list_predictions_for_user(user_id, limit=100):
    if not user_id:
        return []
    cursor = _get_collection().find({"user_id": user_id}).sort("created_at", DESCENDING).limit(limit)
    return [_public(d) for d in cursor]


def get_stats_for_user(user_id):
    """Aggregates for the Dashboard's stat cards — all computed from real saved records."""
    docs = list_predictions_for_user(user_id, limit=10000)
    total = len(docs)
    if total == 0:
        return {
            "total_predictions": 0,
            "avg_quality_score": None,
            "distinct_price_ranges": 0,
            "distinct_consumer_segments": 0,
        }
    avg_quality = sum(d["quality_score"] for d in docs if d.get("quality_score") is not None) / total
    return {
        "total_predictions": total,
        "avg_quality_score": round(avg_quality, 2),
        "distinct_price_ranges": len({d["price_range"] for d in docs if d.get("price_range")}),
        "distinct_consumer_segments": len({d["consumer_segment"] for d in docs if d.get("consumer_segment")}),
    }


def get_trends_for_user(user_id):
    """
    Groups the user's own prediction history by calendar date.
    Honest substitute for "year-based" trends, since the model has no
    year input — see module docstring.
    """
    docs = list_predictions_for_user(user_id, limit=10000)
    by_day = defaultdict(list)
    for d in docs:
        day = d["created_at"][:10]  # YYYY-MM-DD
        by_day[day].append(d)

    trend = []
    for day in sorted(by_day.keys()):
        rows = by_day[day]
        qualities = [r["quality_score"] for r in rows if r.get("quality_score") is not None]
        alcohols = [r["inputs"]["alcohol"] for r in rows if r.get("inputs") and "alcohol" in r["inputs"]]
        price_dist = dict(Counter(r["price_range"] for r in rows if r.get("price_range")))
        trend.append({
            "date": day,
            "samples": len(rows),
            "avg_quality": round(sum(qualities) / len(qualities), 2) if qualities else None,
            "avg_alcohol": round(sum(alcohols) / len(alcohols), 2) if alcohols else None,
            "price_distribution": price_dist,
        })
    return trend
