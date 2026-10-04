"""
Tests for signup/login/me — the authentication endpoints.
"""


def test_signup_buyer_is_auto_approved(client):
    res = client.post("/api/signup", json={
        "name": "New Buyer", "email": "newbuyer@example.com", "password": "password123", "role": "buyer",
    })
    assert res.status_code == 201
    assert res.get_json()["user"]["status"] == "approved"


def test_signup_seller_is_pending(client):
    res = client.post("/api/signup", json={
        "name": "New Seller", "email": "newseller@example.com", "password": "password123",
        "role": "seller", "company_name": "Test Vineyard",
    })
    assert res.status_code == 201
    assert res.get_json()["user"]["status"] == "pending"


def test_signup_rejects_short_password(client):
    res = client.post("/api/signup", json={
        "name": "X", "email": "shortpw@example.com", "password": "abc", "role": "buyer",
    })
    assert res.status_code == 400


def test_signup_rejects_duplicate_email(client):
    payload = {"name": "X", "email": "dupe@example.com", "password": "password123", "role": "buyer"}
    first = client.post("/api/signup", json=payload)
    second = client.post("/api/signup", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


def test_login_wrong_password_returns_generic_error(client):
    client.post("/api/signup", json={"name": "X", "email": "wp@example.com", "password": "password123", "role": "buyer"})
    res = client.post("/api/login", json={"email": "wp@example.com", "password": "wrongpassword"})
    assert res.status_code == 401
    # Should not leak whether the email exists vs. the password being wrong differently
    assert "error" in res.get_json()


def test_me_requires_valid_token(client):
    res = client.get("/api/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_me_returns_user_for_valid_token(client, buyer_token):
    res = client.get("/api/me", headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 200
    assert res.get_json()["user"]["role"] == "buyer"
