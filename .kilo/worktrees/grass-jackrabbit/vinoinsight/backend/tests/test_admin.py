"""
Tests for the admin seller-verification workflow.
"""


def _signup_pending_seller(client, email="pendingseller@example.com"):
    client.post("/api/signup", json={
        "name": "Pending Seller", "email": email, "password": "password123",
        "role": "seller", "company_name": "Vineyard Co",
    })


def test_pending_sellers_requires_admin(client, buyer_token):
    res = client.get("/api/admin/pending-sellers", headers={"Authorization": f"Bearer {buyer_token}"})
    assert res.status_code == 403


def test_admin_sees_pending_seller(client, admin_token):
    _signup_pending_seller(client)
    res = client.get("/api/admin/pending-sellers", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    pending = res.get_json()["pending"]
    assert any(p["email"] == "pendingseller@example.com" for p in pending)


def test_admin_can_approve_seller(client, admin_token):
    _signup_pending_seller(client, "approveme@example.com")
    pending = client.get("/api/admin/pending-sellers", headers={"Authorization": f"Bearer {admin_token}"}).get_json()["pending"]
    seller_id = next(p["id"] for p in pending if p["email"] == "approveme@example.com")

    res = client.post(f"/api/admin/approve/{seller_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert res.get_json()["success"] is True

    login = client.post("/api/login", json={"email": "approveme@example.com", "password": "password123"})
    assert login.get_json()["user"]["status"] == "approved"


def test_admin_can_reject_seller(client, admin_token):
    _signup_pending_seller(client, "rejectme@example.com")
    pending = client.get("/api/admin/pending-sellers", headers={"Authorization": f"Bearer {admin_token}"}).get_json()["pending"]
    seller_id = next(p["id"] for p in pending if p["email"] == "rejectme@example.com")

    res = client.post(f"/api/admin/reject/{seller_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

    login = client.post("/api/login", json={"email": "rejectme@example.com", "password": "password123"})
    assert login.get_json()["user"]["status"] == "rejected"
