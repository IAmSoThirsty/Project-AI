# Project-AI

> **Constitutional AGI ecosystem.** Built by Jeremy Karrick.
> Canonical reference: `docs/reference/AGI_Charter_for_Project-AI_v2_3.pdf`

## What this is

Project-AI is a governed AI systems rebuild with runtime authority checks,
provenance records, replay verification, application surfaces, and deployment
manifests under active development.

The development baseline keeps the AI-side runtime behind explicit governance
and authority gates. Operator-side experimental packages (`arbiter` and `rlp`)
cannot grant themselves authority; applications consume API surfaces and do not
embed governance authority.

## Current status

- Development version: `0.0.0.dev0`.
- Active branch: `main`.
- Stage 18 local acceptance: accepted from a detached clean checkout.
- Development checkpoint: `main` is pushed and GitHub Actions CI passed on
  commit `25c3237b` in run `28308833729`.
- No version tag, GitHub Release, package publication, image publication,
  deployment, or production-readiness claim is part of this checkpoint.

See `docs/internal/REBUILD_EXECUTION_PLAN.md`,
`docs/internal/STAGE_18_ACCEPTANCE.md`, and
`docs/operations/CONTINUITY_MAP.md` for the current evidence trail.

## Quick start

```powershell
# Install locked Python workspace dependencies.
uv sync --frozen --all-extras --all-packages

# Verify immutable provenance inputs.
uv run python tools/verify_frozen_history.py
uv run python tools/canonical_replay.py

# Run the core Python validation used by the local checkpoint.
uv run pytest
uv run ruff check .
uv run ruff format --check .

# Validate the web workspace.
pnpm install --frozen-lockfile
pnpm web:lint
pnpm web:test
pnpm web:build

# Validate Helm rendering offline.
helm lint helm/project-ai
helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py
```

## Repository layout

```text
apps/
  android/          - scoped read-only DOI/replay client
  desktop/          - PyQt6 development desktop client
  web/              - React portals and Chimera-protected web surfaces
docs/
  internal/         - execution ledger, stage acceptance, session evidence
  operations/       - continuity map and handoff state
  reference/        - canonical papers, charter, manifest
helm/
  project-ai/       - Kubernetes chart for the development stack
packages/
  api/              - FastAPI application and routes
  arbiter/          - experimental operator-side ledger/gates/dual-sig
  atlas/            - subordinate audit and discovery support
  capability/       - scoped capability token logic
  cli/              - operator command surface
  companion/        - governed companion state restoration
  execution/        - governed actuation boundary
  governance/       - verdict and policy engine
  kernel/           - core runtime primitives
  rlp/              - experimental operator-side policy package
  security/         - shared security utilities
  swr/              - scenario/world/replay support
tools/
  acceptance_gate.* - local acceptance gates
  canonical_replay.py
  verify_frozen_history.py
  verify_helm_template.py
```

## Build status

Local acceptance and remote development CI are green for the current checkpoint,
but this repository remains a development baseline. Open post-acceptance work is
tracked in the continuity map and stage/session ledgers.

## License

MIT - see `LICENSE`.
