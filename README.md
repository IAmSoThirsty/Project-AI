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

- Local successor version: `0.0.3` (committed on the working branch; not tagged,
  merged, or published as a production release).
- Active branch: `agent/production-readiness-2026-07-19`; immutable code candidate
  `6684828d` is the tested successor revision.
- Stage 18 local acceptance: accepted from a detached clean checkout.
- Published `v0.0.2` is superseded because its exact-commit CI failed and it
  does not contain the current hardening work.
- The local v0.0.3 candidate passes local remediation gates; replacement V3Q
  public-key enrollment and exact-manifest ratification are now verified. It
  still requires secure retirement of the old local private material, green
  remote release/security evidence, external proof custody, an approved
  ingress/backup overlay, target-cluster rehearsal, and CAB approval.

See `docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md`,
`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md`, and
`docs/operations/CONTINUITY_MAP.md` for the current evidence trail.

## Quick start

```powershell
# Install locked Python workspace dependencies.
uv sync --frozen --all-extras --all-packages

# Verify immutable provenance inputs.
uv run python tools/verify_frozen_history.py
uv run python tools/canonical_replay.py

# Verify pre-deployment evidence and operator docs.
uv run python tools/verify_pre_deployment.py

# List every current blocker in one diagnostic pass (still exits non-zero when blocked).
uv run python tools/verify_pre_deployment.py --report

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

## Operator documentation

These docs are the operator-facing references for working with the
deployed stack. Read them in this order on first contact:

1. **`docs/operator.md`** — prerequisites, install commands, all env vars,
   service endpoints, CLI install, K8s validation, frozen-history
   verification, CI command mapping.
2. **`docs/architecture.md`** — package dependency graph (downward-only),
   package/application overview, 9-service Compose stack, governance pipeline
   (kernel → governance → capability → execution), container hardening.
3. **`docs/security.md`** — fail-closed execution gate, capability token
   semantics, container security table, secret scanning, audit trail
   format.
4. **`docs/api/API_REFERENCE.md`** — every FastAPI route (8 routes) with
   auth model, request/response shape, curl examples, error responses.
5. **`docs/cli/CLI_REFERENCE.md`** — every `project-ai` subcommand with
   examples, env vars, exit codes.
6. **`docs/runbooks/INCIDENT_RESPONSE.md`** — 8 most-likely incidents
   (service unhealthy, audit chain break, token rejected, compose won't
   start, atlas replay fails, pytest regression, CI red on main) with
   diagnostics and recovery.
7. **`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md`** — the pre-deploy
   gate (the 4 canonical gates + the evidence they must produce).
8. **`docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md`** — start/verify/inspect/
   stop the 9-service Compose stack.
9. **`docs/provenance.md`** — frozen-history SHA-256 chain verification,
   paper corpus provenance, merge provenance.

## Repository layout

```text
apps/
  android/          - scoped read-only DOI/replay client
  desktop/          - PyQt6 development desktop client
  web/              - React portals and Chimera-protected web surfaces
docs/
  deployment/       - pre-deployment checklist and non-production gates
  internal/         - execution ledger, stage acceptance, session evidence
  operations/       - continuity map and handoff state
  reference/        - canonical papers, charter, manifest
  runbooks/         - local development stack operation guides
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

The local v0.0.3 successor passes the recorded local acceptance gates and is
pushed on the active branch. Immutable code-candidate CI and vulnerability
evidence are green, and the latest gate/documentation follow-up runs
`29717900198` and `29717900199` also passed. The tracked production host is
still a placeholder and remote backup is unconfigured. Open production work is
tracked in the continuity map and CAB records.

## License

MIT - see `LICENSE`.
