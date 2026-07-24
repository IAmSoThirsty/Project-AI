# Production Readiness Status

**Assessment date:** 2026-07-24 UTC
**Mode:** Bounded repository production-readiness pass
**Branch:** `agent/production-readiness-2026-07-19`
**Workspace:** `T:\00-Active\Project-AI-Beginnings`

## Decision

**Not production-ready. Deployment and publication are not authorized by this assessment.**

The locally executable quality gates listed below were run independently. Several pass,
but the fail-closed pre-deployment verifier exits 1, all three available security-relay
audit artifacts fail direct verification (dispositioned 2026-07-24 as an owner-approved
immutable legacy exception; they remain chain-invalid — see
`docs/operations/SECURITY_RELAY_LEGACY_EXCEPTION.md`), installer install/smoke/uninstall
did not complete, and owner-, external-, and target-controlled evidence remains unresolved.
No failed, skipped, unavailable, or historical result is promoted to a pass.

## Local gate evidence

| Gate | Exact command / scope | Exit | Disposition and environmental reason |
|---|---|---:|---|
| Ruff lint | `uv run ruff check .` | 0 | PASS; zero findings |
| Ruff format | `uv run ruff format --check .` | 0 | PASS; 636 files already formatted |
| CI-scope MyPy | `uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src packages/sovereign-vault/src apps/desktop/src apps/services/src tools` | 0 | PASS; 180 source files |
| Focused repository-intelligence/service tests | `uv run pytest packages/knowledge/tests/test_repository.py apps/services/tests/test_services.py -q` | 0 | PASS; 12 passed after index rebuild |
| Knowledge/service suites | `uv run pytest packages/knowledge/tests apps/services/tests -q` | 0 | PASS; 53 passed |
| Full Python suite | `uv run pytest -q` | 0 | PASS; 3518 passed; 5 PostgreSQL tests skipped because `PROJECT_AI_TEST_DATABASE_URL` was not set |
| Tool verifier tests | `uv run pytest tools/tests -q` | 0 | PASS; 118 passed in the recorded full-tool run |
| Canonical replay | `uv run python tools/canonical_replay.py` | 0 | PASS; 5/5 invariants |
| Frozen history | `uv run python tools/verify_frozen_history.py docs/internal/frozen-history/PROJECT-AI_FROZEN_HISTORY.md` | 0 | PASS; 2264/2264 sections |
| Security verifier tests | `uv run pytest tools/tests/test_verify_security_relay.py tools/tests/test_verify_supply_chain.py -q` | 0 | PASS; 23 passed |
| Rust formatting | `cargo fmt --all -- --check` | 0 | PASS |
| Rust tests and clippy | `cargo test --workspace --locked && cargo clippy --workspace --all-targets --locked -- -D warnings` | 0 | PASS; 3 tests, clippy clean |
| Web lint | `pnpm web:lint` | 0 | PASS |
| Web tests and builds | `pnpm web:test && pnpm web:build` | 0 | PASS; operator-console/docs-portal/proof-portal/triumvirate tests and builds completed |
| Android acceptance | `set "ANDROID_HOME=C:\Users\Quencher\AppData\Local\Android\Sdk" && set "ANDROID_SDK_ROOT=C:\Users\Quencher\AppData\Local\Android\Sdk" && cd apps/android && gradlew.bat --no-daemon lintDebug lintRelease testDebugUnitTest assembleDebug assembleRelease` | 0 | PASS; SDK path explicitly configured for this host; Gradle reported BUILD SUCCESSFUL |
| Desktop source smoke | `set "QT_QPA_PLATFORM=offscreen" && set "PROJECT_AI_DESKTOP_SMOKE=1" && uv run --package project-ai-desktop python -m project_ai_desktop` | 0 | PASS; headless source smoke exited normally; Qt font warnings did not cause failure |
| Desktop packaged smoke | `set "QT_QPA_PLATFORM=offscreen" && set "PROJECT_AI_DESKTOP_SMOKE=1" && build\acceptance\desktop\dist\Project-AI-Desktop\Project-AI-Desktop.exe` | 0 | PASS; unsigned packaged executable exited normally; Qt font warnings did not cause failure |
| Unsigned Windows installer build | `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build_windows_installer.ps1 -OutputRoot build\acceptance\windows-installer` | 0 | PASS for build only; desktop/API onedir bundles, two MSIs, and Burn bundle were produced. Signing was intentionally a no-op because no certificate was configured. |
| Windows installer install/smoke/uninstall | `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\smoke_windows_installer.ps1 -BundleExe .\build\acceptance\windows-installer\installer\Project-AI-Desktop-Setup.exe` | 124 | FAIL/INCOMPLETE; timed out after 1200 seconds while Burn launched its elevated engine during silent install. No completion, install assertions, application launch, or uninstall assertions were verified. Not promoted to pass. |
| Compose syntax | `docker compose config --quiet` | 0 | PASS; syntax/config validation only |
| Helm validation | `helm lint helm/project-ai -f helm/values.prod.yaml && helm template project-ai helm/project-ai --namespace project-ai-prod -f helm/values.prod.yaml \| uv run python tools/verify_helm_template.py --expected-namespace project-ai-prod --project-image-registry ghcr.io --project-image-owner iamsothirsty --require-project-image-digests` | 0 | PASS; lint and 47-manifest offline verification |
| Repository index | `uv run python -m knowledge.repository_cli build --root . --output data\repository-intelligence`; then `... status ...` | 0 | PASS only after final documentation rebuild; live status must be reread below |
| Diff integrity | `git diff --check` | 0 | PASS; existing CRLF normalization warnings only |

### Acceptance steps not promoted

The full `tools/acceptance_gate.ps1` was not run as a whole because its clean-checkout
assertions conflict with the intentionally preserved dirty workspace and its final step
would assert no generated/untracked writes. On 2026-07-24 the completion pass exercised
its steps individually and recorded each result in the table below (the sanctioned
alternative per the handoff report). Still **NOT RUN/UNAVAILABLE**, not passed: clean
baseline/final clean checkout assertions (require a clean checkout), a fresh compose
build/start (health was verified against the pre-existing running stack), the installer
install/smoke/uninstall (unelevated session), and any external or target deployment
checks. The legacy-state snapshot was run and **FAILED** because the read-only legacy
repository `T:\00-Active\Project-AI-main` is absent from this host.

### Completion-pass local gate evidence (2026-07-24, second pass)

| Gate | Exact command / scope | Exit | Disposition and environmental reason |
|---|---|---:|---|
| Frozen locked install | `uv sync --frozen --all-extras --all-packages` | 0 | PASS; 156 packages checked |
| Exact runtime | scratch script asserting `sys.version_info[:3] == (3, 12, 10)` | 0 | PASS; 3.12.10 |
| Venv trampolines | `uv run python tools/verify_venv_trampolines.py` | 0 | PASS; all launchers healthy |
| Legacy-state snapshot | `uv run python tools/verify_legacy_state.py` | 1 | FAIL/UNAVAILABLE; `git -C T:\00-Active\Project-AI-main rev-parse HEAD` exits 128 because the read-only legacy repository is absent from this host. Owner must restore it; not promoted. |
| Pre-commit (all hooks) | `$env:SKIP='no-commit-to-branch,gitleaks'; uv run pre-commit run --all-files` | 0 | PASS after the mypy-hook fix below; before/after `git status --porcelain` comparison proved no hook modified any file |
| Gitleaks hook | `uv run pre-commit run gitleaks --all-files` | 0 | PASS; no hardcoded secrets detected |
| Arbiter baseline | `uv run python -m pytest packages/arbiter/tests/test_arbiter_gov.py -q` | 0 | PASS; 12 passed |
| 312-case asymmetric security | `uv run python -m pytest "packages/governance/tests/test_asymmetric_security.py::test_all_published_attack_vectors_are_blocked" -q` | 0 | PASS; 312 passed |
| CycloneDX SBOM | `uvx --from cyclonedx-bom==7.3.0 cyclonedx-py environment <venv-python> --pyproject pyproject.toml --output-reproducible --validate ...` plus scratch validation script | 0 | PASS; CycloneDX 1.6, 155 components, non-empty, reproducible |
| PostgreSQL integration | `uv run python -m pytest packages/accounts/tests/test_postgres_integration.py packages/api/tests/test_api_postgres_integration.py -q` with `PROJECT_AI_TEST_DATABASE_URL` pointing at a disposable local `postgres:16-alpine` container | 0 | PASS; 5 passed in 17.15s; container created for the run and removed afterward |
| Compose config + health | `docker compose config --quiet` then `uv run python tools/verify_compose_health.py` | 0 | PASS; 9/9 services healthy, `readonly`/`cap_drop=ALL`/`no-new-privileges` verified, liveness endpoints live. Verified against the pre-existing running stack (up 2 days, persistent volumes); a fresh `up -d --build --wait` was intentionally not run over live state. |
| Coverage-gated full suite | `uv run python -m pytest -q --cov=... --cov-branch --cov-fail-under=80` (acceptance-gate scope) | 1 | Coverage gate REACHED: 88.02% >= 80%. 3517 passed, 5 skipped (PostgreSQL; passed separately above), 1 failed: `test_real_repository_index_returns_distinct_grounded_searches`, caused by documentation edits made during the 8-minute run staling the live index (same known signature as the 2026-07-24 pre-rebuild failure in the continuity map). Root cause confirmed: after index rebuild the focused suite passed 12/12. Exit 1 is recorded honestly; the coverage percentage and pass counts stand. |
| Focused rerun after rebuild | `uv run python -m pytest packages/knowledge/tests/test_repository.py apps/services/tests/test_services.py -q` | 0 | PASS; 12 passed, including the previously failed real-index test |
| Pre-deployment (report/normal/blockers) | `uv run python tools/verify_pre_deployment.py` in all three modes | 1 | FAIL-CLOSED (expected, unchanged): 11 mandatory blockers across `owner`, `external-supply-chain`, and `production` categories. No local action can truthfully satisfy them. |

Pre-commit mypy-hook fix recorded: the committed state of
`tools/tests/test_verify_supply_chain.py:36` carried `# type: ignore[untyped-decorator]`,
which the repo-venv mypy (pytest typed) rejects as an unused ignore, while the hook's
isolated environment (no pytest, `--ignore-missing-imports`) required it — no single
state of the comment satisfied both checkers. The smallest supported correction was
adding `pytest>=8.3.0` to the mypy hook's `additional_dependencies` in
`.pre-commit-config.yaml` (the list's established purpose), making the decorator typed
in both contexts; the working tree keeps the ignore-free file and both checkers pass.

## Security-relay artifact dispositions

The authoritative implementation is `packages/security/src/security/bridge.py`.
`AppendOnlyAuditRelay.verify()` requires each JSONL record to contain `event`,
`previous_hash`, and `timestamp`, and requires `hash` to equal the SHA-256 digest of
the canonical JSON body without `hash`; the first `previous_hash` must be the genesis
value of 64 zeroes. `tools/verify_security_relay.py` directly invokes that verifier.

| Artifact | Observed schema/producer | Direct command result | Governed disposition |
|---|---|---|---|
| `.project-ai/automation/audit/2026-07-11.audit.jsonl` | Legacy fields `agent_id, classification, event_type, hash, message, run_id, status, task_id, timestamp`; no `previous_hash`; producers: automation monitor agents (`heartbeat-reader`, `runaway-reader`, `lock-reader`, `phantom-reader`, …) | `uv run python tools/verify_security_relay.py .project-ai/automation/audit/2026-07-11.audit.jsonl` -> exit 1, `security relay chain invalid (1 events)` | INVALID legacy artifact; DISPOSITIONED 2026-07-24 by owner-approved immutable legacy exception (`SECURITY_RELAY_LEGACY_EXCEPTION.md`, SHA-256 pinned). Remains chain-invalid by design; not evidence of a valid chain. Not edited. |
| `.project-ai/automation/audit/2026-07-12.audit.jsonl` | Same legacy schema; same producer family; includes admission-denied events | `uv run python tools/verify_security_relay.py .project-ai/automation/audit/2026-07-12.audit.jsonl` -> exit 1, `security relay chain invalid (1 events)` | INVALID legacy artifact; DISPOSITIONED 2026-07-24 by owner-approved immutable legacy exception (`SECURITY_RELAY_LEGACY_EXCEPTION.md`, SHA-256 pinned). Remains chain-invalid by design; not evidence of a valid chain. Not edited. |
| `docs/internal/verification/taar-e2e-2026-07-10/audit/2026-07-10.audit.jsonl` | Same legacy schema; producers: TAAR E2E reader/writer agents (`git-status-reader`, `governance-reader`, `*-report-writer`, …) | `uv run python tools/verify_security_relay.py docs/internal/verification/taar-e2e-2026-07-10/audit/2026-07-10.audit.jsonl` -> exit 1, `security relay chain invalid (1 events)` | INVALID legacy artifact; DISPOSITIONED 2026-07-24 by owner-approved immutable legacy exception (`SECURITY_RELAY_LEGACY_EXCEPTION.md`, SHA-256 pinned; bytes independently sealed in the TAAR bundle). Remains chain-invalid by design; not evidence of a valid chain. Not edited. |

These artifacts were not rewritten, rehashed, deleted, or relabeled. Passing relay
unit tests validate current code behavior only and do not override direct artifact
failures. The exception record `docs/operations/SECURITY_RELAY_LEGACY_EXCEPTION.md`
pins each artifact's raw-byte SHA-256 so any future modification is detectable; an
unexpected verifier exit 0 on these artifacts is itself a tamper alarm.

## Fail-closed pre-deployment result

Both required modes were run:

- `uv run python tools/verify_pre_deployment.py --report` -> **exit 1**; report mode
  recorded 20 of 23 check groups passing, with fail-closed results for remote successor
  evidence, placeholder ingress host, and disabled backup. (The success target is
  23/23; see `PRODUCTION_CLOSURE_PLAN.md` step 8.)
- `uv run python tools/verify_pre_deployment.py` -> **exit 1**; normal mode failed
  closed on these unresolved prerequisites:
  `owner_key_rotation_verified`, `external_proof_custody_verified`,
  `release_provenance_verified`, `sbom_attestations_verified`,
  `production_overlay_verified`, `remote_backup_verified`,
  `monitoring_crds_verified`, `target_environment_approved`, and
  `rollback_rehearsal_verified`.

No local action was taken against owner key rotation, proof custody, release approval,
production authorization/secrets, external attestations, remote backup, monitoring
infrastructure, deployment approval, target approval, or rollback authorization.

## Evidence reconciliation and repository intelligence

`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` and
`docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md` remain fail-closed
and continue to record that deployment is not authorized until the unchecked external
and target conditions are evidenced on one immutable successor. Historical CAB,
verification-bundle, and `data/repository-intelligence/final-verification.log` content
was not rewritten. The historical log is not current evidence; it records an older
snapshot and is retained as historical provenance.

After all current documentation changes, rebuild the index and record the live result
in the final handoff. A fingerprint is intentionally not embedded in this report
because this report is indexed content and editing it changes the fingerprint.

## Remaining owners and required evidence

1. **Automation/TAAR audit owners: DISPOSITIONED.** Jeremy Karrick (sole repository
   owner) approved the immutable legacy exception on 2026-07-24; the verifier boundary
   and pinned SHA-256 hashes are recorded in
   `docs/operations/SECURITY_RELAY_LEGACY_EXCEPTION.md`. No regeneration path remains
   open; the artifacts stay chain-invalid by design.
2. **Security/release owner:** complete owner-key rotation, external proof custody,
   release provenance, and SPDX/SLSA attestations for the same immutable candidate.
3. **Platform/infrastructure owner:** provide production overlay, remote backup/restore,
   monitoring CRDs and alert delivery, target environment approval, and deployment
   evidence in the approved environment.
4. **Deployment/rollback owner and approver:** perform and independently attest the
   authorized deployment, smoke, rollback rehearsal, and rollback authorization.
5. **Workspace owner:** decide retention/versioning for generated `.vs/`, `data/`,
   `output/`, `plans/`, and suspicious untracked entries `{'chunk_id` and `500`.

## Mandatory final status

**Mode:** Bounded repository production-readiness pass, extended by the 2026-07-24 completion pass.
**Created:** `docs/operations/PRODUCTION_READINESS_STATUS.md` and the handoff report.
**Modified:** Readiness and continuity documentation; `.pre-commit-config.yaml` (pytest added to the mypy hook's typed dependencies); prior unrelated dirty work preserved.
**Deleted:** None (the disposable PostgreSQL test container was created and removed by the completion pass; it is infrastructure, not evidence).
**Verified:** Both local gate tables above with their exact dispositions; relay exception frozen state (hash pins + expected exit 1); coverage 88.02% >= 80%; PostgreSQL integration 5/5; compose health 9/9; pre-commit and gitleaks green; SBOM validated; all three pre-deployment modes; repository index after final rebuild; final integrity checks.
**Failed/incomplete:** Three direct relay artifacts (expected; dispositioned by owner-approved immutable legacy exception); fail-closed pre-deployment (expected; externally controlled); installer install/smoke/uninstall (unelevated session); legacy-state snapshot (legacy repository absent from host).
**Not verified/unavailable:** Owner/external/target gates, clean-checkout whole-gate assertions, fresh compose build/start over the live stack, and artifact signing (no certificate).
**Risks:** Chain-invalid legacy audit artifacts (dispositioned, hash-pinned), unresolved release/target prerequisites, unsigned local artifacts, installer smoke gap, absent legacy source repository, dirty workspace, and suspicious untracked entries.
**Continuity map:** `docs/operations/CONTINUITY_MAP.md`; current dated entry appended without rewriting history.
**Remaining:** External evidence custody, approved target execution, installer smoke in an elevated interactive context, legacy repository restoration, workspace retention decisions, and final authorization. Relay-artifact owner disposition is complete (2026-07-24 exception); the stale `final-verification.log` is formally superseded (see `REPOSITORY_INTELLIGENCE.md`).
**Safe to continue:** Local non-deployment work only; **production deployment/publication is not authorized**.
**Stop reason:** The fail-closed gate and its owner/external/production-controlled prerequisites, the unelevated-session installer gap, and the absent legacy repository prevent a truthful production-ready claim; no further repository-local action can change that.
