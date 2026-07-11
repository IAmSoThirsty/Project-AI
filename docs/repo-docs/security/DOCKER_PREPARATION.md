# Docker Preparation Checklist

**Created:** 2026-05-18
**Status:** Pre-build — local testing only

## Architecture

| Surface | Dockerfile | Entrypoint | Port | Image Tag |
|---------|-----------|------------|------|-----------|
| Canonical API | `api/Dockerfile` | `uvicorn api.main:app` | 8001 | `projectai/api:1.0.0` |
| Monolith (legacy) | `Dockerfile` (root) | `uvicorn api.main:app` | 8001 | `projectai/monolith:omega` |

Both Dockerfiles use multi-stage builds, Python 3.11-slim base, non-root user (`appuser`, UID 10001), and healthcheck on `/health/live`.

## Safe Local Build Command

```bash
# This is safe to run — builds locally only, no push
docker compose build api
```

Verify after build:

```bash
docker compose up api -d
curl http://localhost:8001/health/live   # expect {"status": "alive"}
curl http://localhost:8001/health/ready   # expect {"status": "ready", ...}
curl http://localhost:8001/metrics        # expect Prometheus text
docker compose down
```

## DO NOT RUN (Until Freeze Lifted)

```bash
# ⛔ DO NOT RUN — Docker Build Cloud
docker buildx build --builder cloud-iamsothirsty-project-ai ...

# ⛔ DO NOT RUN — Registry push
docker push projectai/api:1.0.0
```

See `DEPLOYMENT_FREEZE.md` for lift conditions.

## Required CI Branch Checks (Before Any Push)

All of the following must pass on `master`:

| Check | Job / Workflow | Critical? |
|-------|---------------|----------|
| CodeQL | `codex-deus-ultimate.yml` | YES |
| Bandit | `codex-deus-ultimate.yml` | YES |
| Secret scanning | `codex-deus-ultimate.yml` | YES |
| Dependency security audit | `codex-deus-ultimate.yml` | YES |
| Ruff lint | `codex-deus-ultimate.yml` | YES |
| MyPy type check | `codex-deus-ultimate.yml` | YES |
| Coverage gate | `codex-deus-ultimate.yml` | YES |
| Python tests | `codex-deus-ultimate.yml` | YES |
| Integration tests | `codex-deus-ultimate.yml` | YES |
| Web lint / type-check / tests | `codex-deus-ultimate.yml` | YES |
| Governance regression tests | `test_governance_pipeline_regressions.py` | YES |
| Unschematized-action rejection | `test_governance_pipeline_regressions.py` | YES |

## Docker Compose Services

| Service | Build Context | Profile | Notes |
|---------|--------------|---------|-------|
| `api` | `api/` | default | Canonical runtime |
| `monolith` | `.` (root) | default | Legacy — uses same FastAPI entrypoint |
| `cerberus` | `../Cerberus-main` | default | External repo — requires adjacent clone |
| `web-backend` | override only | `dev-adapter` | Flask adapter, dev only |
