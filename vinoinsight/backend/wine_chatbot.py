"""
VinoInsight AI - Wine Chatbot (Gemini-backed, with a broad offline fallback)
---------------------------------------------------------------------------
Purpose
    A GENERAL-PURPOSE wine information assistant for users who have little or
    no prior knowledge of wine. It is deliberately NOT restricted to the
    physicochemical inputs used by VinoInsight's prediction models: it answers
    across the whole wine domain — wine types, grape varieties, characteristics,
    taste and aroma, food pairing, serving, storage, regions, production,
    terminology, and comparisons between wines — in plain, beginner-friendly
    English.

Two answer paths
    1. LIVE AI (preferred). Google Gemini answers the question. This is what
       gives true open-domain coverage — any reasonable wine question works.
    2. OFFLINE FALLBACK. If no API key is configured, or the API call fails
       (no internet, rate limit, transient error), a scored keyword matcher
       answers from wine_knowledge.KNOWLEDGE_BASE. This covers ~90 common wine
       topics so the app still behaves sensibly during an offline demo.

    get_chat_response() returns (answer_text, used_ai) and the frontend shows
    an "AI-generated" badge only when used_ai is True, so the two paths are
    always distinguishable to the user.

Setup (one time, no credit card required)
    1. Create a free API key at https://aistudio.google.com/apikey
    2. In this `backend` folder create a file named exactly `.env` containing:
           GEMINI_API_KEY=your-key-here
    3. Run `python app.py` as normal — the key loads automatically each time.

    Run `python check_gemini.py` in this folder to verify the key works and to
    see exactly which model is being used.
"""

import os
import re

from dotenv import load_dotenv

from wine_knowledge import KNOWLEDGE_BASE, FALLBACK_DEFAULT, GREETING

load_dotenv()  # reads GEMINI_API_KEY from a local .env file if present

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Models are tried in order and the first one that answers successfully is
# cached for the rest of the process. Google retires and renames model IDs
# periodically, so a chain is far more robust than a single hardcoded name —
# a rename used to silently drop the bot into fallback mode for every question.
MODEL_CANDIDATES = [
    m.strip() for m in os.environ.get(
        "GEMINI_MODELS",
        "gemini-flash-latest,gemini-2.5-flash,gemini-2.0-flash,"
        "gemini-2.5-flash-lite,gemini-1.5-flash",
    ).split(",") if m.strip()
]

_client = None
_active_model = None      # remembered after the first successful call
_last_error = None        # surfaced by get_status() for debugging

if GEMINI_API_KEY:
    try:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:            # pragma: no cover - depends on environment
        _last_error = f"client init failed: {e}"
        print(f"[chatbot] Gemini client failed to initialise, using offline "
              f"knowledge base instead: {e}")
        _client = None
else:
    _last_error = "no GEMINI_API_KEY found (checked environment and backend/.env)"
    print("[chatbot] No GEMINI_API_KEY set — running on the offline wine "
          "knowledge base. General wine questions will be limited until a key "
          "is added to backend/.env")


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
# This is the single most important setting for open-domain behaviour. The
# previous version led with app-specific chemistry framing and told the model
# to "redirect" anything it judged off-topic, which made it hedge or deflect on
# ordinary beginner questions ("what is Merlot?", "what should I drink with
# fish?"). It now leads with the general-assistant role, states explicitly that
# no wine question is out of scope, and confines the redirect instruction to
# genuinely unrelated subjects.
SYSTEM_PROMPT = """You are the VinoInsight wine assistant.

YOUR ROLE
You are a friendly, general-purpose wine expert helping people who may know
absolutely nothing about wine. Assume the user is a complete beginner unless
they show otherwise.

SCOPE — answer ANY wine-related question
Treat the entire world of wine as in scope, including but not limited to:
- Types and styles of wine (red, white, rosé, sparkling, dessert, fortified,
  orange, natural/organic, non-alcoholic)
- Grape varieties and what each one tastes like
- Wine characteristics: body, tannin, acidity, sweetness, finish, balance, oak
- Taste, aroma, flavour descriptions and how to taste wine
- Food and wine pairing, including everyday and regional dishes
- Serving: temperature, glassware, decanting, opening, pouring
- Storage, shelf life, how long an opened bottle lasts, ageing, wine faults
- Wine regions and countries, appellations, Old World vs New World
- How wine is made: harvesting, fermentation, oak, blending, bubbles
- Wine terminology, label reading, and what confusing words mean
- Comparisons and differences between wines, grapes, or regions
- Practical questions: choosing a bottle, price vs quality, how much to buy,
  calories, wine and health (with sensible caution), etiquette
- Wine chemistry, when asked
- How the VinoInsight app itself works

Never tell the user a wine question is outside your scope, and never restrict
yourself to chemistry or to the app's own features. If a question is vague,
answer the most likely interpretation rather than asking for clarification.

HOW TO ANSWER
- Plain, everyday English. Explain any wine jargon the moment you use it.
- 2-5 sentences for most questions. Be quick and useful, not exhaustive.
- Be concrete: name actual grapes, wines, temperatures, or dishes rather than
  speaking in generalities.
- Use a short bullet list only when genuinely listing several items.
- Warm and encouraging in tone — never snobbish, and never make the user feel
  they should already know something.
- If something is genuinely a matter of taste or debated, say so briefly.
- For health questions, give the mainstream view and suggest a doctor for
  personal advice. If a user seems to be drinking harmfully, be kind and
  factual rather than preachy.

ABOUT THIS APP (only when relevant)
VinoInsight predicts a wine's quality score, quality range, price range, aroma
profile, and consumer segment from physicochemical inputs such as acidity, pH,
alcohol, residual sugar, and sulphates. It also has a Compare Wines page and a
quality-improvement recommendations feature.

OFF-TOPIC
Only if a question has nothing to do with wine, drinks, or this app at all
(for example coding help or sport), give a one-line friendly redirect back to
wine."""


# ---------------------------------------------------------------------------
# Offline fallback matching
# ---------------------------------------------------------------------------
def _keyword_hit(keyword, lower_text):
    """Whole-word match, tolerating common English word endings.

    Word boundaries stop short keywords false-positiving inside longer words
    ("ph" must not match "phone", "port" must not match "important"). The
    optional suffix group lets one keyword cover its everyday inflections, so
    "tannin" matches "tannins" and "decant" matches "decanting" — the latter
    was a real miss before this was added.
    """
    return re.search(r'\b' + re.escape(keyword) + r'(s|es|ing|ed)?\b',
                     lower_text) is not None


def _score_entry(keywords, lower_text):
    """Score how well an entry matches the question.

    Two signals combine:
      * phrase specificity - a multi-word keyword such as "food pairing"
        outranks a bare "food", so "what food goes with steak" lands on the
        steak entry rather than the generic pairing entry;
      * breadth of match - scores are summed, so an entry hit by several of
        its keywords beats one hit by a single keyword. That is what routes
        "what temperature should I serve white wine at" to the serving
        temperature entry (matches both "serve" and "temperature") instead of
        the general "white wine" entry.

    Before this scoring existed the first matching entry in list order simply
    won, which is why the old bot's answers felt arbitrary.
    """
    total = 0
    for k in keywords:
        if _keyword_hit(k, lower_text):
            total += len(k.split()) * 100 + len(k)
    return total


def _fallback_answer(message):
    lower = (message or "").lower()

    # Bare "hi"/"hey" as a complete message only, so it can never shadow a
    # longer, more specific question that happens to contain those letters.
    if re.fullmatch(r'\s*(hi|hey|yo|hii)[\s!.?]*', lower):
        return GREETING

    best_answer, best_score = None, 0
    for keywords, answer in KNOWLEDGE_BASE:
        score = _score_entry(keywords, lower)
        if score > best_score:
            best_answer, best_score = answer, score

    return best_answer if best_answer else FALLBACK_DEFAULT


# ---------------------------------------------------------------------------
# History handling
# ---------------------------------------------------------------------------
def _build_contents(message, history):
    """Convert the frontend's message list into Gemini `contents`.

    Defensive on three counts:
      * entries missing "role"/"text" are skipped instead of raising KeyError,
      * leading assistant turns are dropped — the frontend sends its hardcoded
        opening greeting as history[0], and a conversation that opens on a
        model turn is not a valid multi-turn request,
      * only the last few turns are kept, to stay fast and cheap.
    """
    contents = []
    for h in (history or [])[-8:]:
        if not isinstance(h, dict):
            continue
        text = (h.get("text") or "").strip()
        if not text:
            continue
        role = "user" if h.get("role") == "user" else "model"
        if not contents and role == "model":
            continue  # skip the static opening greeting / any leading bot turn
        contents.append({"role": role, "parts": [{"text": text}]})

    contents.append({"role": "user", "parts": [{"text": message}]})
    return contents


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def get_chat_response(message, history=None):
    """
    message: the user's latest message (string)
    history: optional list of {"role": "user"|"model", "text": "..."} for context
    Returns: (answer_text, used_ai: bool)
    """
    global _active_model, _last_error

    message = (message or "").strip()
    if not message:
        return GREETING, False

    if not _client:
        return _fallback_answer(message), False

    contents = _build_contents(message, history)

    base_config = {
        "system_instruction": SYSTEM_PROMPT,
        "max_output_tokens": 800,   # raised: 500 could truncate a full answer
        "temperature": 0.7,         # a little warmth without drifting off-facts
    }

    # Try the model that already worked first, then the rest of the chain.
    ordered = ([_active_model] if _active_model else []) + \
              [m for m in MODEL_CANDIDATES if m != _active_model]

    errors = []
    for model_name in ordered:
        # thinking_config is only accepted by the 2.5-generation models; sending
        # it to an older one is rejected, so try with it and retry without.
        for config in ({**base_config, "thinking_config": {"thinking_budget": 0}},
                       base_config):
            try:
                response = _client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                text = (getattr(response, "text", "") or "").strip()
                if text:
                    _active_model = model_name
                    _last_error = None
                    return text, True
                errors.append(f"{model_name}: empty response")
                break  # empty (e.g. safety-blocked) — no point retrying config
            except Exception as e:
                errors.append(f"{model_name}: {e}")
                continue

    _last_error = " | ".join(errors[-3:])
    print(f"[chatbot] All Gemini attempts failed, using offline knowledge "
          f"base. Last errors: {_last_error}")
    return _fallback_answer(message), False


def get_status():
    """Diagnostics for the /api/chat/status endpoint and check_gemini.py.

    `mode` deliberately distinguishes THREE states, not two. An earlier version
    reported "gemini" whenever the client object had merely been constructed,
    which was misleading in the exact situation the endpoint exists to
    diagnose: with a key that is invalid, revoked, or blocked by a firewall,
    `genai.Client(...)` still succeeds (it makes no network call), so the
    status said "gemini" while every single answer was actually coming from the
    offline knowledge base.

    Constructing the client proves nothing. Only a completed generate_content
    call does, and that is what `_active_model` records — so:

      offline-knowledge-base  no key, or the client could not be created
      gemini-configured       key present, but no successful call yet, so it
                              is UNVERIFIED — it may still fall back
      gemini-active           a real call has succeeded this process
    """
    if not _client:
        mode = "offline-knowledge-base"
    elif _active_model:
        mode = "gemini-active"
    else:
        mode = "gemini-configured"

    return {
        "api_key_configured": bool(GEMINI_API_KEY),
        "client_ready": _client is not None,
        # True only once a live call has actually returned an answer.
        "gemini_verified": _active_model is not None,
        "active_model": _active_model,
        "candidate_models": MODEL_CANDIDATES,
        "offline_topics": len(KNOWLEDGE_BASE),
        "last_error": _last_error,
        "mode": mode,
        "note": {
            "offline-knowledge-base":
                "No Gemini key/client — every answer comes from the offline "
                "knowledge base. Set GEMINI_API_KEY in backend/.env to enable "
                "live AI.",
            "gemini-configured":
                "A key is configured but no Gemini call has succeeded yet, so "
                "live AI is UNVERIFIED. Ask the chatbot a question, then check "
                "this endpoint again, or run: python check_gemini.py",
            "gemini-active":
                "Verified — a live Gemini call has succeeded in this process.",
        }[mode],
    }
