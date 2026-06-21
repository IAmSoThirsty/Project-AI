# Project-AI API

Development FastAPI gateway for liveness, DOI registry, replay status, Chimera
audit evidence, verdict relay, and canary relay surfaces.

Protected routes require both `PROJECT_AI_API_TOKEN` and
`PROJECT_AI_AUDIT_PATH`. Missing configuration fails closed with HTTP 503.
The gateway does not contain governance authority and does not execute actions.
