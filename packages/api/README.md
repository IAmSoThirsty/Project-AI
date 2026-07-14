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

## Run standalone (no Docker)

`server.py` is a frozen-friendly entrypoint (installed as the
`project-ai-api-server` console script, `optional-dependencies.build` extra)
that binds its own listening socket and drives `uvicorn.Server` directly,
rather than shelling out to the `uvicorn` CLI (whose dynamic
`"project_ai_api.app:app"` module-string import does not resolve reliably
once frozen by PyInstaller):

```bash
uv run --package project-ai-api project-ai-api-server --host 127.0.0.1 --port 0 --port-file /tmp/api.port
```

`--port 0` lets the OS assign a free port; the resolved port is written to
`--port-file` immediately after bind and before serving starts, so a caller
that wants to talk to this process can wait on that file instead of
pre-guessing a port (there is no window in which some other process could
race for the same port, since the only process that ever binds it is the one
that reports it). `/health/live` is intentionally unauthenticated so a
caller can health-check before it has (or needs) a bearer token. This is what
`apps/desktop`'s `api_supervisor.py` uses to launch a bundled instance of
this service; see
[`docs/deployment/WINDOWS_INSTALLER.md`](../../docs/deployment/WINDOWS_INSTALLER.md).
