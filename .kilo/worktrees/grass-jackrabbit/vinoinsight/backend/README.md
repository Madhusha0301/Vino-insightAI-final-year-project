# VinoInsight AI — Backend

This is the Flask backend for VinoInsight AI. It serves the prediction API
and talks to MongoDB and the trained models in `models/`.

**For setup instructions, architecture, model performance, testing, and
known limitations, see the project root README:** [`../README.md`](../README.md)

That file is the single source of truth for this project and is kept up to
date as the system changes. This file used to duplicate that information
and had drifted out of date in ways that actively contradicted the current
system — for example it claimed "login is a mock (any email+password
works)" and "predictions aren't persisted to a database yet," both of
which have since been implemented for real (real MongoDB auth, real
per-user prediction history). That kind of stale, conflicting
documentation was flagged in the project audit as a cleanup item. Keeping
one maintained copy instead of three prevents it from happening again.

Quick reference for this folder specifically:

```bash
pip install -r requirements.txt
python app.py           # starts the API at http://127.0.0.1:5000

# Running the automated test suite (42 tests, no real MongoDB required):
pip install -r requirements-dev.txt
pytest tests/ -v
```

See the root README for MongoDB setup, the Gemini API key (optional, for
the AI chatbot), and full endpoint documentation.


## Wine chatbot

The chatbot is a **general-purpose wine information assistant** for users with
little or no wine knowledge. It answers across the whole wine domain — wine
types, grape varieties, characteristics, taste and aroma, food pairing,
serving, storage, regions, production, terminology, and comparisons — not just
the physicochemical inputs used by the prediction models.

**Files**

| File | Role |
|---|---|
| `wine_chatbot.py` | Gemini call, system prompt, fallback routing |
| `wine_knowledge.py` | 112-topic offline wine knowledge base |
| `check_gemini.py` | Connection diagnostic — run this first when answers look limited |

**Two answer paths**

1. **Live AI (preferred).** Google Gemini answers the question. This is what
   provides true open-domain coverage.
2. **Offline knowledge base.** Used automatically when no API key is set, or
   the API call fails (no internet, rate limit, transient error). Covers 112
   common wine topics via a scored keyword matcher.

`/api/chat` returns `ai_powered: true` only for path 1, and the UI shows an
"AI-generated" badge accordingly, so the two are always distinguishable.

**Enabling live AI**

Create `backend/.env` containing a single line:

```
GEMINI_API_KEY=your-key-here
```

Get a free key (no credit card) at <https://aistudio.google.com/apikey>.
`.env` is gitignored — never commit an API key. Note that .gitignore does
NOT apply to zip files: when packaging for submission you must exclude
`.env` explicitly (see the root README). `.env.example` is the safe,
secret-free template to share instead.

**Troubleshooting: "the chatbot only answers a few questions"**

That symptom means it is running on the offline knowledge base rather than
Gemini. Diagnose it in one step:

```bash
python check_gemini.py
```

Or check the live status endpoint while the server is running:

```
GET http://localhost:5000/api/chat/status
```

`mode` tells you which path is active — `offline-knowledge-base`,
`gemini-configured` (key present but no successful call yet, so live AI is
UNVERIFIED), or `gemini-active` (a real call has genuinely succeeded) — and
`last_error` explains why Gemini was not used.
