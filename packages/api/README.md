# Project-AI API

Development FastAPI gateway for liveness, DOI registry, replay status, Atlas
status, Atlas Sludge narrative generation, Chimera audit evidence, verdict
relay, and canary relay surfaces.

Protected routes require both `PROJECT_AI_API_TOKEN` and
`PROJECT_AI_AUDIT_PATH`. Missing configuration fails closed with HTTP 503.
The gateway does not contain governance authority and does not execute actions.

Public routes:

- `GET /health/live`
- `GET /dois`
- `GET /replay/status`
- `GET /atlas/status`

Protected routes:

- `GET /audit`
- `POST /chimera/verdict`
- `POST /chimera/canary`
- `POST /atlas/sludge`

`/atlas/sludge` consumes a Reality Stack snapshot, returns an SS-only fictional
Sludge artifact, and records an `atlas.sludge_narrative` audit event. It does
not grant authority or actuate a decision.
