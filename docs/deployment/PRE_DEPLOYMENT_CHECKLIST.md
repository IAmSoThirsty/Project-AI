# Pre-Deployment Checklist

**Status:** pre-deployment output, not a deployment approval.
**Date:** 2026-06-29
**Scope:** current development checkpoint on `main`.
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md`.

This checklist records what must be true before any future deployment, release,
tag, publication, or production-readiness claim. It does not create a version
tag, GitHub Release, package publication, image publication, or deployment.

## Current Evidence

- Local Python tests: `1467 passed`.
- CI-shaped MyPy: clean on `95 source files`.
- Ruff check: passed.
- Ruff format check: `189 files already formatted`.
- Branch coverage gate: `88.47%`, threshold `80%`.
- Canonical replay: `5/5 invariants passed`.
- Frozen history: `2264 sections verified`.
- GitHub Actions CI:
  - Implementation run `28362042896` passed at commit `176990f08b6c403befccee43b350d6874e733507`.
  - Latest docs/evidence run `28362260186` passed at commit `22ad10aa49f24e5045ffd4493a6e92f9cb615b7a`.
- Pre-deployment verifier: `tools/verify_pre_deployment.py` passed locally.
- Compose runtime: `7/7 healthy and security settings verified` locally after
  starting Docker Desktop.
- Android debug test/build: `BUILD SUCCESSFUL` locally with
  `ANDROID_HOME=C:\Users\Quencher\AppData\Local\Android\Sdk`.

## Required Pre-Deployment Gates

Run these from the repository root:

```powershell
uv sync --frozen --all-extras --all-packages
uv run python tools/verify_pre_deployment.py
uv run ruff check .
uv run ruff format --check .
uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
uv run python -m pytest -q --tb=short
uv run python tools/canonical_replay.py
uv run python tools/verify_frozen_history.py
```

Run these when the required external runtimes are available:

```powershell
pnpm install --frozen-lockfile
pnpm web:lint
pnpm web:test
pnpm web:build
cargo fmt --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 240
python tools/verify_compose_health.py
docker compose down
helm lint helm/project-ai
helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py
```

## Environment Contract

Documented runtime variables:

| Variable | Surface | Requirement |
|---|---|---|
| `PROJECT_AI_API_TOKEN` | API, CLI, Compose, Helm | Required for protected API routes and protected CLI commands. Keep blank in examples. |
| `PROJECT_AI_AUDIT_PATH` | API, Compose, Helm | Required with token for protected audit surfaces. Compose and Helm set it to `/data/chimera-audit.jsonl`. |
| `PROJECT_AI_DOI_REGISTRY` | API, Compose, Helm | Points to `docs/reference/DOI_REGISTRY.md` inside the API container. |
| `PROJECT_AI_API_URL` | CLI | Defaults to `http://127.0.0.1:8000`; documented in `.env.example`. |
| `PROJECT_AI_SERVICE` | service adapters | Must be one of `swr`, `atlas`, or `arbiter-rlp`. |
| `PROJECT_AI_DESKTOP_SMOKE` | desktop app | `1` enables offscreen smoke mode. |
| `QT_QPA_PLATFORM` | desktop tests/smoke | Use `offscreen` for CI and headless validation. |
| `VITE_API_BASE_URL` | web portals | Optional override; defaults to `/api`. |

## Runtime Surfaces

Compose development services:

- `api` -> `http://127.0.0.1:8000/health/live`
- `docs-portal` -> `http://127.0.0.1:4173/healthz`
- `proof-portal` -> `http://127.0.0.1:4174/healthz`
- `swr` -> internal `/health/live`
- `atlas` -> internal `/health/live`
- `arbiter-rlp` -> internal `/health/live`
- `genesis` -> `genesis-emitter health`

Kubernetes development chart:

- Chart path: `helm/project-ai`
- Offline render check: `helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py`
- Values file: `helm/project-ai/values.yaml`
- Current chart values are development defaults, not production values.

## Fail-Closed Conditions

Do not deploy if any of these are true:

- `tools/verify_pre_deployment.py` fails.
- Local tests, lint, type checking, canonical replay, or frozen-history
  verification fail.
- GitHub Actions CI is not green for the exact commit intended for deployment.
- `PROJECT_AI_API_TOKEN` is committed with a real value in tracked files.
- Protected API routes do not fail closed when token or audit path is missing.
- Compose health/security verification fails.
- Helm rendering verification fails.
- The continuity map is stale or does not list the current changed files,
  commands, verification results, risks, and remaining work.

## Rollback Preparation

No production deployment exists at this checkpoint. For a future development
deployment rehearsal, rollback is limited to stopping local runtime surfaces:

```powershell
docker compose down
```

For a future Kubernetes rehearsal, rollback must target the named release used
for that rehearsal:

```powershell
helm uninstall project-ai-dev
```

Do not treat either command as production rollback until a real deployment
environment, release name, namespace, image registry, and persistence model are
explicitly defined and tested.

## Remaining Before Production

- Production image names and registry policy are not defined.
- Runtime secrets are not wired through a Kubernetes Secret.
- TLS, ingress, persistence retention, monitoring, alerting, backup, and real
  rollback are not implemented.
- No production deployment has been performed.
- No release tag, GitHub Release, package publication, or image publication has
  been created.
