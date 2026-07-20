# Release-Specific Evidence Bundle — v0.0.2

**Evidence cutoff:** 2026-07-19
**Candidate commit:** `82aa1476657e16a1d38caccba38357c83380a3e3`

## Successor update — 2026-07-20

The v0.0.2 material below is retained as historical evidence only. The
immutable v0.0.3 successor code candidate is
`6684828d23b08beaac77aee5efadc532bed23181`; successor CI run `29716300475`
and vulnerability scan `29716300404` both passed. This does not supply image
signatures, SBOM attestations, external proof custody, target approval, or
deployment/rollback evidence.

> **Supersession notice:** v0.0.2 is no longer a deployable candidate. The
> remediation working tree contains CI, runtime, monitoring, security, and
> dependency fixes that are not in this commit or its images. Local results
> below demonstrate the remediation path, not release evidence for v0.0.2. A
> successor bundle must be generated from a committed and remotely green
> revision.

## Release identity

| Evidence | Result |
|---|---|
| Local/remote main | `82aa1476657e16a1d38caccba38357c83380a3e3` |
| Annotated tag | `v0.0.2` resolves to the candidate commit |
| Tag signature | GitHub reports the annotated Git tag as unsigned |
| GitHub Release | Published 2026-07-19 08:16:56 UTC |
| Release URL | <https://github.com/IAmSoThirsty/Project-AI/releases/tag/v0.0.2> |
| Release metadata | `targetCommitish` displays `master`; the tag object itself resolves to the candidate commit |
| Release assets | No standalone assets attached to the GitHub Release |

The v0.0.2 release body lists seven images and omits operator-console. The
remediated publish workflow now verifies and documents all eight images, but
that workflow change has not run remotely yet.

## GitHub Actions evidence

| Workflow/run | Result | CAB interpretation |
|---|---|---|
| Publish `29679414341` | Passed | Eight image build/sign jobs, seven-image pull verification, SBOM/provenance configuration, and release notes succeeded |
| Publish `29679407181` | Passed | Duplicate exact-commit publish run also succeeded |
| Publish to Docker Hub `29679414310` | Passed | Secondary registry publish succeeded; not the Helm source in this change |
| Verify TAAR bundle `29679414313` | Passed | Clean-clone TAAR evidence verification succeeded |
| CI `29679407137` | **Failed** | Release cannot be described as CI-green |

Exact-commit CI failures:

- `Python (policy, type, test, replay)` was terminated with exit code `137` at
  54% of the coverage run. The log displayed failure markers before
  termination but did not reach a test summary, so the exact assertions are not
  available from that run.
- `Compose (build, health, security)` built/started far enough to invoke
  `tools/verify_compose_health.py`, then failed with
  `ModuleNotFoundError: No module named 'kernel'`.

## Remediation working-tree evidence

The worktree also contained the pre-existing untracked `compose.hub.yaml`; it
was not read, changed, staged, or used by these commands.

| Command | Result |
|---|---|
| `uv run python tools/verify_pre_deployment.py` | **Fail-closed:** all other checks pass, but the checkout contains `packages/thirstys-standard-v3q/owner-private.json`; owner-controlled rotation/retirement is required before this gate can pass |
| `uv run python tools/canonical_replay.py` | Passed: 5/5 invariants |
| `uv run python tools/verify_frozen_history.py` | Passed: 2264/2264 sections |
| Earlier remediation checkpoint (`uv run pytest -q`) | Passed: 3049 passed, 5 environment-gated skips, 1 documented xfail, 1 warning; retained as historical working-tree evidence |
| Current-tree full Python suite (`uv run pytest -q`) | Passed: 3410 passed, 5 PostgreSQL environment-gated skips, zero failures, XFAIL/XPASS results, or warnings; this is successor working-tree evidence, not v0.0.2 release evidence |
| `uv run python tools/run_ci_coverage.py --batches 8` | Passed: all 8 batches; combined branch coverage 87.32%, threshold 80% |
| `helm lint helm/project-ai` | Passed: 1 chart, 0 failures; icon recommendation only |
| Production-values Helm render + verifier | Passed: 47 manifests; namespace enforced and all eight v0.0.2 images digest pinned |
| Checkov 3.3.8 | Passed: Kubernetes 1123/0/0, Dockerfile 248/0/0, GitHub Actions 976/0/0 |
| Rebuilt API + Compose smoke | API image built; complete stack 9/9 healthy; runtime security settings verified |
| In-image governance checks | Canonical replay 5/5; frozen history 2264/2264; empty security relay valid at genesis |
| API Prometheus endpoint | Live `/metrics` exposes build info, bounded request counter, and latency histogram |
| Python dependency audit | OSV audit passed after upgrading locked `setuptools` 82.0.1 to 83.0.0 |
| Node dependency audit | `pnpm audit --audit-level=moderate` reported no known vulnerabilities |
| Web acceptance | ESLint passed; four portal suites passed (61 tests total); all four production builds passed | Working-tree evidence only; no immutable successor artifact |
| Android acceptance | `testDebugUnitTest assembleDebug` passed with the configured SDK | Working-tree evidence only; unsigned debug artifact and remote release evidence remain out of scope |
| Desktop acceptance | Offscreen source smoke and unsigned PyInstaller onedir build/smoke passed under Python 3.12.10 | Working-tree evidence only; signed installer/release artifact remains unverified |
| Standalone Waterfall full suite | `T:\\01-Projects\\Thirstys-waterfall`: `uv sync --frozen --extra test` followed by `uv run python -m pytest -q --no-cov` passed **309 tests** with no warnings | Correct repository-environment replay; standalone target/registry release evidence remains external |

The local full suite does not replace the failed remote CI run; both facts must
remain visible.

## Supply-chain and security evidence

| Control | Evidence | Status |
|---|---|---|
| Container signatures | Publish workflow uses keyless cosign for each build output | Workflow passed; independent v0.0.2 verification returned `no signatures found`; successor evidence required |
| Cosign verification attempt | Containerized cosign 2.2.4 queried the published v0.0.2 API digest with the documented GitHub OIDC identity; registry returned `no signatures found` | **Blocker:** successor must be rebuilt/published and independently verified |
| Image pull/manifest | v0.0.2 publish omitted operator-console verification; remediation verifies all eight | Remediation unrun remotely; successor evidence required |
| SBOM/provenance | Buildx `sbom: true`, `provenance: mode=max`; publish SBOM note passed | Attestations claimed by build workflow; no standalone release assets and no independent attestation verification attached |
| Python dependency audit | Pinned pip-audit 2.10.1 / OSV | Remediated lock passes; v0.0.2 lock contained vulnerable setuptools 82.0.1 |
| Python dependency licenses | Explicit allow-list plus installed-artifact verification for cel-python 0.4.0's missing metadata field | Local v0.0.3 gate passes; remote successor run required |
| Trivy image scan | Remediation scans all eight images on release publication | Exact-candidate remote successor result is missing; the historical GHCR pull attempt stalled, while the separate local containerized scan is recorded below |
| Local Trivy scan | Containerized Trivy 0.63.0 scanned all eight locally available v0.0.2 GHCR image digests with `HIGH,CRITICAL --ignore-unfixed`; all returned zero findings | Remote successor scan and attached immutable artifact remain required |
| Python/Rust/Node vulnerability scans | Remediation runs on push/PR and schedule | Python OSV, Rust `cargo audit` 0.22.2, and Node moderate+ audits pass locally; raw outputs are under `build/acceptance/security/`; no remote successor run |
| Local CycloneDX SBOMs | Pinned Python generator and `cargo-cyclonedx` 0.5.9 produced validated JSON (155 Python / 20 Rust components) at `build/acceptance/sbom/project-ai-python.cdx.json` and `build/acceptance/sbom/project-ai-rust.cdx.json` | Working-tree evidence only; no immutable successor artifacts or remote attestations attached |
| Weekly CycloneDX SBOM | `.github/workflows/sbom-weekly.yaml` exists on `main` | No v0.0.2-specific artifact attached |
| CodeQL | Pinned CodeQL v4 workflow covers Python and JavaScript/TypeScript | Added locally; no remote successor run |
| Checkov | Pinned Checkov 3.3.8 scans rendered production Kubernetes, Dockerfiles, and workflows | Local scans pass with zero skips/failures; no remote successor run |
| Git tag signature | Annotated tag object | Unsigned; distinct from container cosign signatures |
| Production secrets | Production values contain blank/example inputs | Unique production secret provenance not verified |
| V3Q signing material | Root `.dockerignore` excludes the ignored owner-key file; rebuilt images report it absent; replacement public key `owner-rotation-2026-07-19-01` is enrolled; production loads public verification keys only | **Blocker:** securely retire the old local `owner-primary` material and prove external proof issuance/custody before use |
| V3Q ratification | `owner-ratification.json` binds and verifies the exact ratified artifact; `verify_ratification.py` passes | **Pass for exact artifact;** production host integration and external proof custody remain open |
| V3Q package tests | Passed: 46 tests, including 28 deployment/integration/execution tests and owner-key tool safety checks covering missing registry/configuration, ratification verification, and `require_approval` denial | Retired local key removal, production integration, and external proof custody remain open |

## Runtime acceptance evidence

| Check | Status |
|---|---|
| Target cluster/namespace dry run | Local `docker-desktop` server-side dry run attempted; production values are blocked because the cluster lacks Prometheus Operator `PrometheusRule`/`ServiceMonitor` CRDs. The same server-side render passes with monitoring/alerting disabled; this is not production-target evidence |
| Production machine-auth Helm mode | Passed locally: production render sets durable credential enforcement and omits `PROJECT_AI_API_TOKEN_FILE`; 47-manifest verifier passes |
| v0.0.2 pods Ready in a cluster | Not run |
| Local rebuilt `/health/live` | Passed; reports successor version 0.0.3 with complete Compose stack 9/9 healthy |
| Local rebuilt `/metrics` scrape | Passed; required HTTP/build series present |
| Protected-route denial/allow smoke | Passed locally: 50 focused account/API tests cover missing/invalid/shared-token denial, scoped credential allow, wrong-scope denial, and revocation; target-environment proof not run |
| Local audit-chain genesis/replay | Passed; live-cluster continuity not run |
| Alert delivery | Not run |
| Rollback rehearsal | Not run |
| Local backup/restore rehearsal | Passed: `backup_audit_data.sh` round-tripped audit and SWR bundle files through `restore_audit_data.sh`; non-empty restore targets were rejected. Production PVC/remote restore remains unrun |
| Named acceptance sign-off | Missing |
| V3Q required-mode startup | Helm render sets required mode and mounted key path; target startup not run |
| Waterfall standalone/rebuild replay | Passed: standalone repair gate `35/35`; standalone full suite `309 passed` with no warnings using the locked test extra; Project-AI copied replay `313 passed`; copied source/tests/examples direct Ruff check passes; typed adapter/transport checks green |
| Waterfall-integrated API image | Passed: rebuilt `project-ai-api:waterfall-route-local` (`sha256:9f6f2125531a8fdad6293e81698ba7e1683dbb3588f6819e18acf4124d11e4bc`); image imports `project_ai_waterfall` and `waterfall_adapter`, exposes the Waterfall OpenAPI route, and excludes the owner-private path |
| Standalone Waterfall web candidate | Rebuilt `thirstys-waterfall:production-candidate`; zero HIGH/CRITICAL Trivy findings and temporary `/health` probe returned 200; prior `latest` image had eight HIGH findings and is not promotable | Local candidate only; standalone registry publication, signature, and independent CI evidence remain required |
| Waterfall authenticated API surface | Passed locally: status and operation routes require machine auth; operation requires V3Q-wired adapter/audit and records evidence hashes; OpenAPI baseline regenerated |
| ADR-002 machine credentials | Passed locally: schema version 5 (SQLite/PostgreSQL), owner/MFA-protected one-time token issuance, scope enforcement, revocation, machine-write attribution, and SQLite→PostgreSQL migration against disposable PostgreSQL 16; focused account/API and 5 integration tests passed | Production-target migration/rollback and credential provisioning remain open |
| Waterfall image secret containment | Passed: local image reports the V3Q owner-private path absent; host checkout still contains owner-controlled material and fails the fail-closed pre-deployment gate |

## Commands to complete the security bundle

Run from an approved, authenticated operator environment and attach raw outputs
to the external change record. Pin by digest, not only by tag.

```powershell
cosign verify `
  --certificate-identity-regexp '^https://github.com/IAmSoThirsty/Project-AI/.github/workflows/publish.yaml@.*$' `
  --certificate-oidc-issuer https://token.actions.githubusercontent.com `
  ghcr.io/iamsothirsty/project-ai-<IMAGE>@<DIGEST>

cosign verify-attestation `
  --certificate-identity-regexp '^https://github.com/IAmSoThirsty/Project-AI/.github/workflows/publish.yaml@.*$' `
  --certificate-oidc-issuer https://token.actions.githubusercontent.com `
  ghcr.io/iamsothirsty/project-ai-<IMAGE>@<DIGEST>
```

Repeat for all eight images, then attach green CodeQL, Checkov, Trivy, Python,
Rust, and Node dependency-scan evidence tied to the candidate digest/commit.
