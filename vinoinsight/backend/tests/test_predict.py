"""
Tests for POST /api/predict — the core prediction endpoint.
Covers: happy path, validation (missing fields), and that a logged-in
user's predictions are actually saved to history (closing the gap
identified in the project audit — this used to not be tested at all
because it didn't exist).
"""
from conftest import SAMPLE_WINE


def test_predict_happy_path_returns_all_five_outputs(client):
    res = client.post("/api/predict", json=SAMPLE_WINE)
    assert res.status_code == 200
    body = res.get_json()
    for key in ["quality_score", "quality_range", "price_range", "aroma_profile", "consumer_segment"]:
        assert key in body, f"missing {key} in prediction response"
    assert "shap_values" in body
    assert "recommendations" in body and isinstance(body["recommendations"], list)


def test_predict_missing_fields_returns_400(client):
    incomplete = {k: v for k, v in SAMPLE_WINE.items() if k != "alcohol"}
    res = client.post("/api/predict", json=incomplete)
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_predict_no_json_body_returns_400(client):
    res = client.post("/api/predict")
    assert res.status_code == 400


def test_predict_anonymous_is_not_saved_to_history(client):
    res = client.post("/api/predict", json=SAMPLE_WINE)
    body = res.get_json()
    assert body["saved_to_history"] is False


def test_predict_logged_in_user_is_saved_to_history(client, buyer_token):
    res = client.post(
        "/api/predict",
        json={**SAMPLE_WINE, "wine_style": "Still Red"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res.status_code == 200
    assert res.get_json()["saved_to_history"] is True

    hist = client.get("/api/predictions", headers={"Authorization": f"Bearer {buyer_token}"})
    assert hist.status_code == 200
    predictions = hist.get_json()["predictions"]
    assert len(predictions) == 1
    assert predictions[0]["wine_style"] == "Still Red"
    assert predictions[0]["quality_score"] == res.get_json()["quality_score"]
