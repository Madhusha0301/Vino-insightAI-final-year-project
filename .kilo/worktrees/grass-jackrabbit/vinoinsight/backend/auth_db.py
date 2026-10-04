"""
VinoInsight AI - User Database & Auth (MongoDB)
------------------------------------------------------------------
Backed by MongoDB, as specified in the original project proposal
(Section 1.4 / 4.4 of the contextual report), rather than a local
file-based database.

Role-based access control:
  - roles: 'buyer', 'seller', 'admin'
  - sellers require admin approval before they can access seller features
    (status: 'pending' -> 'approved' / 'rejected')
  - buyers are auto-approved (no verification needed to browse/buy)

Auth is a simple bearer-token scheme (tokens kept in-memory) — adequate
for a final year project demo. A production system would use JWT with
expiry, refresh tokens, and HTTPS-only cookies.

Connection:
  Reads MONGO_URI from the environment (falls back to a local default).
  See README.md for local MongoDB and MongoDB Atlas (free cloud) setup.
"""

import os
import uuid
import hashlib
from datetime import datetime, timezone

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "vinoinsight")

_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
_db = _client[DB_NAME]
_users = _db["users"]

try:
    _users.create_index([("email", ASCENDING)], unique=True)
except Exception as e:
    print("=" * 70)
    print("COULD NOT CONNECT TO MONGODB.")
    print(f"Tried to connect to: {MONGO_URI}")
    print(f"Error: {e}")
    print()
    print("Fix options:")
    print("  1. Install MongoDB Community Server locally and make sure it's")
    print("     running (mongod), OR")
    print("  2. Use a free MongoDB Atlas cloud database and set MONGO_URI")
    print("     in your backend/.env file, e.g.:")
    print("     MONGO_URI=mongodb+srv://user:pass@cluster0.mongodb.net/")
    print("See README.md 'Database Setup (MongoDB)' section for full steps.")
    print("=" * 70)
    raise SystemExit(1)

# In-memory token store: token -> user_id (resets on server restart)
_TOKENS = {}


def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _public(doc):
    """Strip internal/sensitive fields before returning a user to the API layer."""
    if not doc:
        return None
    return {
        "id": doc["_id"],
        "name": doc["name"],
        "email": doc["email"],
        "role": doc["role"],
        "status": doc["status"],
        "company_name": doc.get("company_name"),
    }


def init_db():
    """Seed a default admin account if none exists yet."""
    if _users.find_one({"role": "admin"}) is None:
        salt = uuid.uuid4().hex
        _users.insert_one({
            "_id": str(uuid.uuid4()),
            "name": "System Admin",
            "email": "admin@vinoinsight.ai",
            "password_hash": _hash_password("Admin@123", salt),
            "salt": salt,
            "role": "admin",
            "status": "approved",
            "company_name": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        print("Seeded default admin account -> admin@vinoinsight.ai / Admin@123")


def create_user(name, email, password, role, company_name=None):
    if role not in ("buyer", "seller"):
        return None, "Invalid role."

    status = "approved" if role == "buyer" else "pending"
    salt = uuid.uuid4().hex
    user_id = str(uuid.uuid4())
    doc = {
        "_id": user_id,
        "name": name,
        "email": email,
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "role": role,
        "status": status,
        "company_name": company_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _users.insert_one(doc)
    except DuplicateKeyError:
        return None, "An account with this email already exists."

    return _public(doc), None


def authenticate(email, password):
    doc = _users.find_one({"email": email})
    if not doc:
        return None, "No account found with this email."
    if _hash_password(password, doc["salt"]) != doc["password_hash"]:
        return None, "Incorrect password."

    token = uuid.uuid4().hex
    _TOKENS[token] = doc["_id"]
    return {"token": token, "user": _public(doc)}, None


def get_user_by_token(token):
    user_id = _TOKENS.get(token)
    if not user_id:
        return None
    doc = _users.find_one({"_id": user_id})
    return _public(doc)


def list_pending_sellers():
    docs = _users.find({"role": "seller", "status": "pending"}).sort("created_at", -1)
    return [
        {
            "id": d["_id"], "name": d["name"], "email": d["email"],
            "company_name": d.get("company_name"), "created_at": d["created_at"],
        }
        for d in docs
    ]


def set_seller_status(user_id, status):
    if status not in ("approved", "rejected"):
        return False
    result = _users.update_one(
        {"_id": user_id, "role": "seller"},
        {"$set": {"status": status}},
    )
    return result.matched_count > 0


init_db()
