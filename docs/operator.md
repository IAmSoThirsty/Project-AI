# Operator Guide

Development baseline for Project-AI. Not production-ready.

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12.10 | All Python packages |
| uv | ≥ 0.11 | Python dependency management |
| Rust / cargo | stable (≥ 1.85) | genesis-emitter |
| Node.js | 22 LTS | Web portal build |
| pnpm | 10.30.0 | Node package management |
| Docker + Compose | ≥ 27 / v2 | Container stack |
| Helm | ≥ 4 | Kubernetes manifests (optional) |

> **Note on Rust toolchain:** `rust-toolchain.toml` pins `stable-x86_64-pc-windows-gnu`
> for Windows development. On Linux (including Docker and CI), set
> `RUSTUP_TOOLCHAIN=stable` before running `cargo` commands.

## Python workspace

```bash
# Install all packages in editable mode
uv sync

# Run the full test suite
uv run pytest -q

# Lint + format check
uv run ruff check .
uv run ruff format --check .

# Type check
uv run mypy --ignore-missing-imports packages/*/src apps/desktop/src apps/services/src
```

## Rust (genesis-emitter)

```bash
# Build
cargo build --locked --release -p project-ai-genesis-emitter

# Test
cargo test --locked

# Emit a genesis record (reads JSON from stdin)
echo '{"content":"test","authority":"operator"}' | cargo run --release -- [previous-hash]

# Health check (stdout only)
./target/release/project-ai-genesis-emitter health

# HTTP server
./target/release/project-ai-genesis-emitter serve 127.0.0.1:8080
```

## Web portals

```bash
# Install Node dependencies
pnpm install --frozen-lockfile

# Lint (ESLint, zero warnings)
pnpm web:lint

# Test (Vitest)
pnpm web:test

# Build all four web applications
pnpm web:build
```

## Development container stack

```bash
# Build every Project-AI service image and resolve the PostgreSQL image
docker compose build

# Start all nine services and wait for health
docker compose up -d --wait --wait-timeout 240

# Verify health and container hardening
python tools/verify_compose_health.py

# Stop
docker compose down
```

### Service endpoints (from host)

| Service | URL | Notes |
|---|---|---|
| API gateway | http://127.0.0.1:8000/health/live | JSON health response |
| Operator console | http://127.0.0.1:4175/healthz | React SPA |
| Docs portal | http://127.0.0.1:4173/healthz | React SPA |
| Proof portal | http://127.0.0.1:4174/healthz | React SPA |
| PostgreSQL | internal (port 5432) | Shared human state; no host binding |
| SWR adapter | internal (port 8000) | No host binding |
| Atlas adapter | internal (port 8000) | No host binding |
| Arbiter/RLP adapter | internal (port 8000) | No host binding |
| Genesis emitter | internal (port 8080) | No host binding |

Internal adapters respond at `/health/live` and `/service/info`.

## Operator CLI

```bash
# Install CLI
uv run pip install -e packages/cli

# Available commands (require running API)
uv run project-ai --help
```

## Kubernetes (development, no cluster required)

```bash
# Validate manifests offline against repository invariants
helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py

# Lint chart
helm lint helm/project-ai
```

## Verify frozen history chain

```bash
python tools/verify_frozen_history.py
# Expected: 2,264/2,264 chain links verified
```

## CI

GitHub Actions workflow at `.github/workflows/ci.yaml` covers Python, Rust,
Node/web, Compose, Android, Kubernetes, SBOM, desktop packaging, and the Windows
installer. Run the applicable equivalents locally before pushing; only the
exact pushed commit's remote results are immutable CI evidence.

## See also

- **`docs/architecture.md`** — package dep graph, every package's role, governance model, container stack
- **`docs/security.md`** — fail-closed execution gate, capability tokens, container hardening, secret scanning
- **`docs/provenance.md`** — frozen-history SHA-256 chain, paper corpus, merge provenance
- **`docs/api/API_REFERENCE.md`** — every FastAPI route with auth, body, response, curl examples
- **`docs/cli/CLI_REFERENCE.md`** — every `project-ai` subcommand with examples
- **`docs/runbooks/INCIDENT_RESPONSE.md`** — 8 most-likely incidents with diagnostics
- **`docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md`** — start/verify/inspect/stop the Compose stack
- **`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md`** — the pre-deploy gate
- **`docs/deployment/PRODUCTION_DEPLOY.md`** — end-to-end deploy procedure
- **`docs/deployment/HELM_DEPLOY.md`** — Kubernetes install via the helm chart
- **`docs/deployment/ENVIRONMENT_VARIABLES.md`** — every env var with type/default/required-flag
- **`docs/operations/PERFORMANCE_SLOS.md`** — performance and SLO targets
- **`docs/operations/CONTINUITY_MAP.md`** — current-state handoff map
