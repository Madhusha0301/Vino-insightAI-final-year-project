# VinoInsight AI — Frontend

This is the React frontend for VinoInsight AI. It talks to the Flask
backend in `../backend`.

**For setup instructions, architecture, model performance, testing, and
known limitations, see the project root README:** [`../README.md`](../README.md)

That file is the single source of truth for this project and is kept up to
date as the system changes. This file used to duplicate that information
(routes, setup steps, a sample API response) but had drifted out of date —
for example it still described login as a frontend-only mock and listed
routes that no longer match `App.jsx` — which is exactly the kind of
conflicting-documentation problem flagged in the project audit (cleanup
task). Keeping one maintained copy instead of three prevents that from
happening again.

Quick reference for this folder specifically:

```bash
npm install
npm start        # dev server at http://localhost:3000
npm run build    # production build
```

The backend must be running first (`cd ../backend && python app.py`) for
API calls to succeed — see the root README for full backend setup,
including MongoDB configuration.
