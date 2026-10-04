"""
Shared pytest fixtures for the VinoInsight AI backend test suite.

IMPORTANT: this patches pymongo.MongoClient -> mongomock.MongoClient
BEFORE app.py (and the auth_db / predictions_db modules it imports) are
ever imported, so the whole app runs against an in-memory fake Mongo
instead of requiring a real MongoDB server to run the test suite.

This does NOT change production behaviour at all — app.py, auth_db.py,
and predictions_db.py are completely unmodified; they still call the
real pymongo.MongoClient when actually deployed. Only the test process's
import of `pymongo` is patched, and only for the duration of running
pytest.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymongo
import mongomock

# Patch BEFORE any of our modules import `from pymongo import MongoClient`
pymongo.MongoClient = mongomock.MongoClient

# Use a fixed, isolated test database name so a real local MongoDB (if one
# happens to be running) is never touched, even if this patch were ever
# bypassed.
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB_NAME", "vinoinsight_test")

import app as flask_app_module  # noqa: E402  (import after the monkeypatch, deliberately)
import auth_db  # noqa: E402
import predictions_db  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_db():
    """
    Resets the in-memory mongomock store before every test. Without this,
    the module-level cached collections in auth_db.py / predictions_db.py
    (cached once and reused for speed in production) leak data across
    tests in the same pytest session — e.g. two tests both using a
    "buyer_token" fixture would otherwise silently share the same
    underlying user record and prediction history.
    """
    auth_db._users.delete_many({})
    try:
        predictions_db._get_collection().delete_many({})
    except Exception:
        pass
    auth_db.init_db()  # reseed the default admin account each test
    yield


@pytest.fixture()
def client():
    flask_app_module.app.config["TESTING"] = True
    with flask_app_module.app.test_client() as c:
        yield c


@pytest.fixture()
def admin_token(client):
    """Logs in as the seeded default admin account and returns a bearer token."""
    res = client.post("/api/login", json={"email": "admin@vinoinsight.ai", "password": "Admin@123"})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["token"]


@pytest.fixture()
def buyer_token(client):
    """Creates and logs in a fresh buyer account (auto-approved), returns a bearer token."""
    email = "test_buyer@example.com"
    client.post("/api/signup", json={
        "name": "Test Buyer", "email": email, "password": "password123", "role": "buyer",
    })
    res = client.post("/api/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["token"]


SAMPLE_WINE = {
    "fixed_acidity": 7.4, "volatile_acidity": 0.70, "citric_acid": 0.0,
    "residual_sugar": 1.9, "chlorides": 0.076, "free_sulfur_dioxide": 11.0,
    "total_sulfur_dioxide": 34.0, "density": 0.9978, "ph": 3.51,
    "sulphates": 0.56, "alcohol": 9.4, "is_red": 1,
}
