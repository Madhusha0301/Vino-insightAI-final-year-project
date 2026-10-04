"""
Tests for the /api/chat wine chatbot endpoint.

The chatbot has two answer paths — live Gemini, and an offline knowledge base
used whenever the API is unreachable — so these tests pin down BOTH
deterministically rather than depending on whether a GEMINI_API_KEY happens to
be present on the machine running pytest.

The `offline` fixture below forces the offline path by clearing the module's
Gemini client. That matters: before it existed, adding a real key to
backend/.env made the "ai_powered is False" assertions fail, because the tests
had silently been relying on the developer machine having no key configured.
"""

import pytest

import wine_chatbot
from wine_knowledge import KNOWLEDGE_BASE


@pytest.fixture()
def offline(monkeypatch):
    """Force the offline knowledge-base path regardless of local .env state."""
    monkeypatch.setattr(wine_chatbot, "_client", None)
    yield


@pytest.fixture()
def fake_ai(monkeypatch):
    """Force the live-AI path with a stubbed client, so no real API call is made."""
    class _FakeModels:
        def generate_content(self, model, contents, config):
            return type("R", (), {"text": "A stubbed Gemini answer about wine."})()

    monkeypatch.setattr(wine_chatbot, "_client", type("C", (), {"models": _FakeModels()})())
    monkeypatch.setattr(wine_chatbot, "_active_model", None)
    yield


# ---------------------------------------------------------------------------
# Endpoint contract
# ---------------------------------------------------------------------------
def test_chat_requires_message(client):
    res = client.post("/api/chat", json={})
    assert res.status_code == 400


def test_chat_returns_answer_and_ai_flag(client):
    res = client.post("/api/chat", json={"message": "What are tannins?"})
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body["answer"], str) and body["answer"]
    assert isinstance(body["ai_powered"], bool)


def test_chat_status_endpoint_reports_mode(client):
    res = client.get("/api/chat/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["mode"] in (
        "gemini-active", "gemini-configured", "offline-knowledge-base")
    assert body["offline_topics"] == len(KNOWLEDGE_BASE)
    assert body["note"]


def test_status_offline_when_no_client(client, offline):
    body = client.get("/api/chat/status").get_json()
    assert body["mode"] == "offline-knowledge-base"
    assert body["gemini_verified"] is False


def test_status_configured_but_unverified_before_any_call(client, fake_ai):
    """A constructed client is NOT proof Gemini works — it makes no network
    call. Reporting plain "gemini" here used to hide a broken key completely."""
    body = client.get("/api/chat/status").get_json()
    assert body["mode"] == "gemini-configured"
    assert body["gemini_verified"] is False
    assert "UNVERIFIED" in body["note"]


def test_status_becomes_active_after_a_successful_call(client, fake_ai):
    assert client.post("/api/chat", json={"message": "hi"}).status_code == 200
    body = client.get("/api/chat/status").get_json()
    assert body["mode"] == "gemini-active"
    assert body["gemini_verified"] is True


# ---------------------------------------------------------------------------
# Offline knowledge-base path
# ---------------------------------------------------------------------------
def test_offline_answers_a_known_chemistry_topic(client, offline):
    res = client.post("/api/chat", json={"message": "What are tannins?"})
    body = res.get_json()
    assert body["ai_powered"] is False
    assert "tannin" in body["answer"].lower()


@pytest.mark.parametrize("question,expected", [
    ("What is Merlot?", "merlot"),
    ("What wine goes with steak?", "cabernet"),
    ("How long does an opened bottle last?", "days"),
    ("What temperature should I serve white wine at?", "°c"),
    ("What is the difference between Champagne and Prosecco?", "prosecco"),
    ("How is wine made?", "ferment"),
    ("What does terroir mean?", "terroir"),
    ("What wine should a beginner start with?", "pinot"),
])
def test_offline_covers_general_wine_domain(client, offline, question, expected):
    """The regression this whole change was about: general (non-chemistry)
    wine questions must get a real answer, not the generic catch-all."""
    res = client.post("/api/chat", json={"message": question})
    body = res.get_json()
    answer = body["answer"].lower()
    assert body["ai_powered"] is False
    assert "i don't have a stored answer" not in answer, f"no KB match for: {question}"
    assert expected in answer


def test_offline_default_for_unknown_topic(client, offline):
    res = client.post("/api/chat", json={"message": "asdkjaskdjaskjd nonsense"})
    body = res.get_json()
    assert res.status_code == 200
    assert body["ai_powered"] is False
    assert body["answer"]


def test_short_keywords_do_not_false_positive(offline):
    """Word-boundary matching: 'ph' must not fire inside 'phone'."""
    answer, _ = wine_chatbot.get_chat_response("where is my phone")
    assert "acidic" not in answer.lower()


# ---------------------------------------------------------------------------
# Live-AI path (stubbed)
# ---------------------------------------------------------------------------
def test_ai_path_sets_ai_powered_true(client, fake_ai):
    res = client.post("/api/chat", json={"message": "Tell me about Pinot Noir"})
    body = res.get_json()
    assert body["ai_powered"] is True
    assert body["answer"] == "A stubbed Gemini answer about wine."


def test_history_drops_leading_bot_greeting():
    """A conversation sent to Gemini must not open on a model turn — the
    frontend always sends its static greeting as history[0]."""
    contents = wine_chatbot._build_contents(
        "and what about Merlot?",
        [{"role": "bot", "text": "Hi! I'm the VinoInsight wine assistant."},
         {"role": "user", "text": "Tell me about Pinot Noir"},
         {"role": "model", "text": "Pinot Noir is a light-bodied red..."}],
    )
    assert contents[0]["role"] == "user"
    assert contents[-1]["parts"][0]["text"] == "and what about Merlot?"


def test_history_tolerates_malformed_entries():
    contents = wine_chatbot._build_contents(
        "hello",
        [{"role": "user"}, None, {"text": ""}, "not a dict"],
    )
    assert len(contents) == 1
