# Development Stack Runbook

**Status:** active development runbook.
**Date:** 2026-06-29
**Scope:** local pre-deployment validation only.

This runbook describes how to start, verify, inspect, and stop the current
development stack. It is not a production deployment procedure.

## Prerequisites

- Python `3.12.10`
- `uv`
- Docker with Compose v2
- Node.js `22` and `pnpm 10.30.0`
- Rust stable toolchain for local Rust validation
- Helm for chart rendering checks

## Configuration

Use `.env.example` as the non-secret configuration reference.

Protected API routes require:

- `PROJECT_AI_API_TOKEN`
- `PROJECT_AI_AUDIT_PATH`

The Compose stack provides `PROJECT_AI_AUDIT_PATH=/data/chimera-audit.jsonl`.
Set `PROJECT_AI_API_TOKEN` in the shell before starting Compose if protected
routes must be exercised.

## Start

```powershell
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 240
```

## Verify

```powershell
python tools/verify_compose_health.py
```

Expected result:

```text
compose runtime: 9/9 healthy and security settings verified
```

Public probes:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/live
Invoke-RestMethod http://127.0.0.1:4173/healthz
Invoke-RestMethod http://127.0.0.1:4174/healthz
Invoke-RestMethod http://127.0.0.1:4175/healthz
```

Protected audit probe:

```powershell
$headers = @{ Authorization = "Bearer $env:PROJECT_AI_API_TOKEN" }
Invoke-RestMethod http://127.0.0.1:8000/audit -Headers $headers
```

If token or audit path configuration is missing, protected routes must fail
closed with HTTP `503`. If the token is wrong, protected routes must return
HTTP `401`.

## Inspect

```powershell
docker compose ps
docker compose logs --no-color api
docker compose logs --no-color docs-portal
docker compose logs --no-color proof-portal
docker compose logs --no-color genesis
```

## Stop

```powershell
docker compose down
```

## Kubernetes Render Rehearsal

```powershell
helm lint helm/project-ai
helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py
```

This verifies offline manifest shape only. It does not apply resources to a
cluster.

## Expected Development Boundaries

- API, service adapters, portals, and Genesis expose development liveness only.
- Applications do not embed governance authority.
- `arbiter` and `rlp` remain experimental operator-side packages.
- The Atlas replay and Sludge routes are subordinate evidence surfaces, not
  authority grants.
- Compose and Helm values are development defaults.

## Escalation

If a health or security verification fails:

1. Capture the exact failing command and output.
2. Run `docker compose ps`.
3. Inspect the failed service logs.
4. Stop the stack with `docker compose down`.
5. Fix the failing source, Dockerfile, Compose config, or Helm values.
6. Re-run the full pre-deployment gate in
   `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md`.
