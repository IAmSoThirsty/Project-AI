# Project-AI

> **Constitutional AGI ecosystem.** Built by Jeremy Karrick.
> Canonical reference: `docs/reference/AGI_Charter_for_Project-AI_v2_3.pdf`

## What this is

Project-AI v0.0.3 is a released single-user, offline-first Windows product with
runtime authority checks, provenance records, replay verification, local
application surfaces, encrypted backup/restore, and a no-pull offline installer.

## Use it locally - the product deployment

Project-AI's primary product profile is **offline-first local operation**. Kubernetes,
cloud publication, hosted ingress, and SaaS integrations are optional additions; they are
not required to run the product.

For a prepared offline bundle, extract it and run `Install Project-AI Offline.cmd`.
In this source checkout, run `Start Project-AI.cmd`, then open:

`http://127.0.0.1:4175`

See [`OWNER_QUICKSTART.md`](OWNER_QUICKSTART.md) for owner start, status, stop, backup,
restore, recovery, and offline installation instructions. The authoritative profile
definition is
[`docs/deployment/DEPLOYMENT_MODEL.md`](docs/deployment/DEPLOYMENT_MODEL.md).

The development baseline keeps the AI-side runtime behind explicit governance
and authority gates. Operator-side experimental packages (`arbiter` and `rlp`)
cannot grant themselves authority; applications consume API surfaces and do not
embed governance authority.

## Current status

- Released version: `v0.0.3`.
- Production profile: `P1 Offline-First Local`, for one Windows user.
- Distribution:
  `project-ai-p1-v0.0.3-windows-amd64.zip` plus `.sha256`, `.sig`, and `.pub`
  sidecars on the GitHub Release.
- Startup: extract the ZIP and run `Install Project-AI Offline.cmd`.
- P2 Kubernetes, hosted ingress, registry images, cloud services, and
  organizational CAB controls are future optional deployment work. P1 does not
  authorize or imply P2.

See [`docs/deployment/OFFLINE_FIRST_READINESS.md`](docs/deployment/OFFLINE_FIRST_READINESS.md)
and [`docs/operations/CONTINUITY_MAP.md`](docs/operations/CONTINUITY_MAP.md) for
the exact release acceptance and evidence trail.

## Verify the downloaded release

```powershell
pwsh -File .\scripts\owner\Test-OfflineRelease.ps1 `
  -ArchivePath .\project-ai-p1-v0.0.3-windows-amd64.zip
```

The validator checks the SHA-256 sidecar, SSH Ed25519 detached signature,
release public key, internal file manifest, image inventory, `LICENSE`,
`NOTICE`, and `RELEASE.json`. The release signing-key fingerprint is
`SHA256:rKRWH+iipbORKpYSUuK3zU2w8e9vcLr/2RbI/QUToE8`.

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
7. **`docs/deployment/OFFLINE_FIRST_READINESS.md`** — the released P1
   production acceptance and exact-artifact evidence.
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

The v0.0.3 P1 release is built from one clean release revision and distributed
as an integrity-addressed, detached-signature-verified offline ZIP. Its
acceptance covers install, first account setup, governed Atlas/SWR operation,
restart/repeat, encrypted backup, restore, and explicit removal on the supported
Windows/Docker Desktop platform. Hosted P2 infrastructure remains
unprovisioned and outside this release.

## License

MIT - see `LICENSE`. Distribution notices are in `NOTICE` and
`THIRD_PARTY_NOTICES.md`.
