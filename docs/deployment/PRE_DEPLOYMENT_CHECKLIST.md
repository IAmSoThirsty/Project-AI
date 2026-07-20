# Pre-Deployment Checklist

**Status:** v0.0.3 successor identity prepared; replacement owner public key
enrolled and exact manifest ratification verified. The aggregate pre-deployment
gate still correctly fails on the retired local owner-private key, missing remote
successor evidence, placeholder production ingress, and unconfigured remote
backup. No production deployment is authorized.
**Evidence date:** 2026-07-20.

**Current CAB entry point:**
[`PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md`](../operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)

## Current local evidence

- Full pytest: 3406 passed, 5 PostgreSQL environment-gated skips, zero
  failures, XFAIL/XPASS results, or warnings.
- Batched branch coverage: 87.32%, threshold 80%.
- Canonical replay: 5/5; frozen history: 2264/2264.
- Rebuilt API image: live metrics, canonical replay, frozen-history verifier,
  and valid empty security-relay genesis proven inside the container.
- Compose: 9/9 healthy with read-only/cap-drop/no-new-privileges checks.
- Helm: lint passes; production render has 47 manifests and enforces namespace
  plus all eight image digests.
- Checkov 3.3.8: Kubernetes 1123/0/0, Dockerfile 248/0/0, GitHub Actions
  976/0/0.
- Workflow action pinning: all 103 remote action references in the successor
  checkout use full commit SHAs; local workflow verification passes.
- Dependency audits: Python OSV and Node moderate+ pass after upgrading locked
  setuptools 82.0.1 to 83.0.0.
- Rust dependency audit: `cargo audit` 0.22.2 reports no advisories for the
  current `Cargo.lock`; `cargo fmt`, Clippy, and workspace tests pass.
- Local CycloneDX SBOMs: Python workspace SBOM contains 155 components and Rust
  workspace SBOM contains 20 components; both validate as CycloneDX JSON.
- Web surfaces: ESLint, all portal tests (61 tests), and all four production
  builds pass locally.
- Android: `testDebugUnitTest assembleDebug` passes with the configured Android
  SDK; Gradle reports only the SDK XML-version compatibility warning.
- Desktop: offscreen source smoke and unsigned PyInstaller onedir build/smoke
  both pass under Python 3.12.10.
- Standalone Waterfall: production-candidate image has zero HIGH/CRITICAL
  Trivy findings and its temporary `/health` probe returned 200; the mutable
  prior `latest` image is not promotable. The standalone locked test replay is
  also green at `309 passed` with no warnings. The Project-AI copied-runtime
  replay passes `313` tests.
- ADR-002 machine credentials: owner/MFA issuance, scoped route enforcement,
  revocation, audit attribution, and SQLite-to-disposable-PostgreSQL migration
  are locally verified.
- Backup/restore: audit and SWR bundle round-trip passes locally; non-empty
  restore targets and unsafe archive paths fail closed.
- V3Q package suite: 46 tests pass, including 28 required-mode/
  integration/execution tests plus owner-key tool safety checks. This does not
  replace owner ratification of the exact production manifest.

## Mandatory candidate gates

```powershell
uv sync --frozen --all-extras --all-packages
uv run python tools/verify_pre_deployment.py
# Optional diagnostic pass: list every current blocker without fail-fast stop.
uv run python tools/verify_pre_deployment.py --report
uv run ruff check .
uv run ruff format --check .
uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src packages/sovereign-vault/src apps/desktop/src apps/services/src tools
uv run pytest -q
uv run python tools/run_ci_coverage.py --batches 8
uv run python tools/canonical_replay.py
uv run python tools/verify_frozen_history.py
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 240
python tools/verify_compose_health.py
helm lint helm/project-ai -f helm/values.prod.yaml
helm template project-ai helm/project-ai --namespace project-ai-prod -f helm/values.prod.yaml | uv run python tools/verify_helm_template.py --expected-namespace project-ai-prod --project-image-registry ghcr.io --project-image-owner iamsothirsty --require-project-image-digests
```

The exact successor commit must then pass remote CI, CodeQL, Checkov, Trivy
for all eight published images, Python/Node/Rust dependency scans, SBOM and
signature/attestation verification. The CAB pack additionally requires the
real target, owners, maintenance window, secret provenance, server-side dry
run, monitoring/page delivery, backup/restore, rollback rehearsal, and named
acceptance. Local gates alone are not production approval.

## V3Q minimum acceptance gate

Production Helm sets `THIRSTYS_V3Q_REQUIRED=true` and loads only public
verification keys from the packaged or explicitly configured
`THIRSTYS_V3Q_REGISTRY`. Missing or malformed verification configuration aborts
application startup. The online runtime cannot mint its own authority or approval;
missing external proofs deny execution. Development remains dormant by default.

Do not deploy until all of the following are true:

- the retired local `owner-primary` private file and affected local layers are
  securely retired under the owner's approved process;
- the replacement private key remains only in the approved offline signing system
  and the replacement public key is committed in `trusted-keys.json`;
- Jeremy / Thirsty's exact-manifest ratification remains independently verifiable
  through `owner-ratification.json` and `verify_ratification.py`;
- a production-equivalent startup test proves required-mode activation and a
  negative test proves invalid configuration and missing proofs fail closed;
- a consequential action without an external approval proof is proven not to execute.

The source manifest remains `draft_unratified`; the signed
`thirstys-standard-v3q.ratified.manifest.yaml` is the current ratified artifact.
V3Q production minimum acceptance is still not satisfied until the retired local
material and external deployment controls are resolved.

Owner-controlled `owner-primary` key material is retired from the trusted
registry but still present as an ignored local file; secure destruction remains
an owner-controlled pre-deployment step.

Current draft-manifest review snapshot: `3ea08a2cf1244c4c0b4a9045aef4b5e5ac59ed9e82d7e03aa315d0d56fdcf09c`.
This hash is a review aid, not an owner ratification or release hash.

`docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json` is the machine-readable
successor evidence record. Its current `status` is `missing`; it must not be
changed to `verified` until the immutable remote and target-environment
evidence listed in that record exists. The record separately tracks owner-key
rotation, exact-manifest ratification, external proof custody, production
overlay, remote backup, monitoring CRDs, and Dependabot disposition; each must
be evidenced rather than inferred from local tests. Its
`candidate_manifest_sha256` is checked against the candidate manifest in the
checkout before any external evidence can be accepted.

<!-- Retired 2026-06-29 checkpoint retained as historical evidence only.

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
- GitHub Actions CI for immutable successor `6684828d`:
  CI run `29716300475` and vulnerability scan `29716300404` passed; image
  signatures, attestations, and target deployment evidence remain pending.
- Historical GitHub Actions CI:
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
| `PROJECT_AI_API_TOKEN` | API, CLI, Compose, Helm | Development/bootstrap fallback; production machine routes use durable per-program credentials. Keep blank in examples. |
| `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED` | API, Compose, Helm | Set `true` in production after scoped credentials are provisioned; rejects shared-token machine writes. |
| `PROJECT_AI_AUDIT_PATH` | API, Compose, Helm | Required with token for protected audit surfaces. Compose and Helm set it to `/data/chimera-audit.jsonl`. |
| `PROJECT_AI_DOI_REGISTRY` | API, Compose, Helm | Points to `docs/reference/DOI_REGISTRY.md` inside the API container. |
| `PROJECT_AI_API_URL` | CLI | Defaults to `http://127.0.0.1:8000`; documented in `.env.example`. |
| `PROJECT_AI_SERVICE` | service adapters | Must be one of `swr`, `atlas`, or `arbiter-rlp`. |
| `PROJECT_AI_DESKTOP_SMOKE` | desktop app | `1` enables offscreen smoke mode. |
| `QT_QPA_PLATFORM` | desktop tests/smoke | Use `offscreen` for CI and headless validation. |
| `VITE_API_BASE_URL` | web portals | Optional override; defaults to `/api`. |
| `PROJECT_AI_WATERFALL_ENABLED` | API | Leave `false` until the target has approved Waterfall configuration, V3Q rotation, and execution evidence. |
| `PROJECT_AI_WATERFALL_CONFIG` | API | Optional server-side Waterfall JSON configuration; never browser-supplied. |

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
- Candidate `6684828d` has green successor CI and vulnerability evidence, but
  image signatures, SBOM attestations, and target-environment proof are still
  absent.
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
- Target TLS/ingress ownership, persistence retention, monitoring/page delivery,
  remote backup/restore, and real Helm rollback evidence remain unverified.
- No production deployment has been performed.
- No release tag, GitHub Release, package publication, or image publication has
  been created.
-->
