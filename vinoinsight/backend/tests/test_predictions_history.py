"""
Tests for the new prediction-history endpoints (/api/predictions,
/api/predictions/stats, /api/predictions/trends) — the direct fix for
the "Database Storage" gap flagged in the project audit.
"""
from conftest import SAMPLE_WINE


def test_predictions_requires_auth(client):
    res = client.get("/api/predictions")
    assert res.status_code == 401


def test_predictions_stats_requires_auth(client):
    res = client.get("/api/predictions/stats")
    assert res.status_code == 401


def test_new_user_has_empty_history_and_zeroed_stats(client, buyer_token):
    hist = client.get("/api/predictions", headers={"Authorization": f"Bearer {buyer_token}"})
    assert hist.get_json()["predictions"] == []

    stats = client.get("/api/predictions/stats", headers={"Authorization": f"Bearer {buyer_token}"})
    body = stats.get_json()
    assert body["total_predictions"] == 0
    assert body["avg_quality_score"] is None


def test_stats_reflect_real_saved_predictions(client, buyer_token):
    headers = {"Authorization": f"Bearer {buyer_token}"}
    for _ in range(3):
        client.post("/api/predict", json=SAMPLE_WINE, headers=headers)

    stats = client.get("/api/predictions/stats", headers=headers).get_json()
    assert stats["total_predictions"] == 3
    assert stats["avg_quality_score"] is not None


def test_history_is_isolated_per_user(client):
    # Buyer A
    client.post("/api/signup", json={"name": "A", "email": "a@example.com", "password": "password123", "role": "buyer"})
    token_a = client.post("/api/login", json={"email": "a@example.com", "password": "password123"}).get_json()["token"]
    # Buyer B
    client.post("/api/signup", json={"name": "B", "email": "b@example.com", "password": "password123", "role": "buyer"})
    token_b = client.post("/api/login", json={"email": "b@example.com", "password": "password123"}).get_json()["token"]

    client.post("/api/predict", json=SAMPLE_WINE, headers={"Authorization": f"Bearer {token_a}"})

    hist_a = client.get("/api/predictions", headers={"Authorization": f"Bearer {token_a}"}).get_json()["predictions"]
    hist_b = client.get("/api/predictions", headers={"Authorization": f"Bearer {token_b}"}).get_json()["predictions"]
    assert len(hist_a) == 1
    assert len(hist_b) == 0, "Buyer B must not see Buyer A's predictions"


def test_trends_groups_by_date(client, buyer_token):
    headers = {"Authorization": f"Bearer {buyer_token}"}
    client.post("/api/predict", json=SAMPLE_WINE, headers=headers)
    res = client.get("/api/predictions/trends", headers=headers)
    assert res.status_code == 200
    trends = res.get_json()["trends"]
    assert len(trends) == 1
    assert trends[0]["samples"] == 1
    assert "avg_quality" in trends[0]
    assert "price_distribution" in trends[0]
