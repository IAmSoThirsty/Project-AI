# Production Closure Plan — Owner-Controlled Execution of Remaining External Gates

> **Current scope (2026-07-26):** This is a future optional P2 hosted/Kubernetes
> closure plan. Project-AI v0.0.3 is separately released for the single-user P1
> Offline-First Local production profile. None of the P2 steps below are a
> prerequisite for installing or operating the P1 release.

- **Date:** 2026-07-24 UTC
- **Mode:** Approved owner-closure planning and evidence refresh. Repository implementation
  authority: suspended. Commit authority: not granted.
- **Candidate commit (Git HEAD at plan production):** `b022ed746d91161d53a736793b69e84ddeb365ea`
  on branch `agent/production-readiness-2026-07-19`.
- **Authority basis:** Operator authorization of 2026-07-24 granting only (a) read-only
  evidence-refresh commands, (b) creation of this document, (c) an append-only continuity
  entry, (d) the final Thirsty's Standard v3 §35 report.
- **Settled facts (not revisited here):** repository engineering complete; immutable legacy
  relay exception closed by disposition (`docs/operations/SECURITY_RELAY_LEGACY_EXCEPTION.md`);
  repository-local production gates exhausted; deployment and publication prohibited; no
  repository-local change can satisfy the remaining blockers.
- **Decision restated:** **NOT production-ready. Production deployment and publication remain
  prohibited.** This document authorizes nothing by itself; it sequences the owner and
  external work required to reach authorization.

Authoritative machine gate: `tools/verify_pre_deployment.py` (all three modes exit 1 as of
this document — see Evidence Appendix). The per-gate truth is the `required.*` boolean map in
`docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json` (`status: "missing"`, `review_only: true`,
9 of 14 required flags false) plus two machine-checkable production-values gates
(`production_ingress_host`, `production_remote_backup`).

---

## Phase 1 — Ordered owner execution checklist

Gates keep their original numbering (G1–G15); they are listed in dependency-driven execution
order. No step below may be performed by an agent without a new, explicit, per-action operator
authorization; several may only be performed by the owner personally.

### Step 1 — G1: Owner key rotation

- **Governing document:** `docs/operations/cab/V3Q_OWNER_KEY_ROTATION.md` (procedure §1–§8,
  "Required evidence"); verifier `tools/verify_pre_deployment.py::verify_owner_key_rotation_tool`;
  `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` (V3Q minimum acceptance gate).
- **Exact current blocker:** `owner_key_rotation_verified: false`;
  `owner_key_rotation_record: null`. Replacement key `owner-rotation-2026-07-19-01` is enrolled
  in `packages/thirstys-standard-v3q/trusted-keys.json` and exact-manifest ratification passed,
  but independent evidence of retirement/secure destruction of the compromised-treated
  `owner-primary` key (and affected local image layers) is not recorded. The off-repository
  relocation of `owner-private.json` (2026-07-20) is verified absent from the checkout but is
  not itself retirement evidence.
- **Required owner action:** Jeremy Karrick (or authorized custodian) completes retirement of
  the former owner key under the approved custody process and records independently verifiable
  evidence. Agents must not self-ratify.
- **Required credentials/environment:** Offline signing system holding the approved
  off-repository private key; custody policy identity; access to the secure storage location
  (`%USERPROFILE%\Documents\Project-AI-Secrets` or approved equivalent).
- **Exact procedure (from `V3Q_OWNER_KEY_ROTATION.md`):** if a further rotation is required,
  generate with `packages/thirstys-standard-v3q/tools/create_owner_key.py` (private material
  written only off-repository), then ratify and verify:

  ```powershell
  uv run python packages/thirstys-standard-v3q/tools/ratify_manifest.py `
    --manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.manifest.yaml `
    --owner-private-key <APPROVED-OFF-REPO-PATH> `
    --effective-date <YYYY-MM-DD> `
    --output-manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.ratified.manifest.yaml `
    --output-record packages/thirstys-standard-v3q/owner-ratification.json

  uv run python packages/thirstys-standard-v3q/tools/verify_ratification.py `
    --manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.ratified.manifest.yaml `
    --record packages/thirstys-standard-v3q/owner-ratification.json `
    --registry packages/thirstys-standard-v3q/trusted-keys.json
  ```

- **Evidence to capture:** new/current public key ID and reviewed registry diff; offline
  signing-system identity, custody policy, rotation timestamp; ratified manifest + owner
  record; `verify_ratification.py` output; required-mode positive and negative startup
  evidence; owner confirmation that the old key and affected image layers are retired; then a
  structured `owner_key_rotation_record` written into `REMOTE_SUCCESSOR_EVIDENCE.json` and the
  boolean flipped — by the owner or under explicit owner authorization only.
- **Expected success condition:** `verify_ratification.py` exits 0; blockers mode no longer
  lists `owner_key_rotation_verified`.
- **Rollback/failure handling:** If ratification fails, do not edit the evidence record; the
  gate stays fail-closed. A failed rotation leaves the prior enrolled key state intact.
- **Dependencies:** None (first gate; other owner gates reference its custody chain).
- **Classification:** Reversible in repository terms; **externally consequential**
  (cryptographic trust root). Not destructive to the repo; key destruction itself is
  intentionally irreversible and owner-only.

### Step 2 — G2: External proof custody

- **Governing document:** `tools/verify_pre_deployment.py::verify_v3q_authority_boundary`;
  CAB pack `docs/operations/cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md`
  ("Release-blocking conditions"); `V3Q_OWNER_KEY_ROTATION.md` §8.
- **Exact current blocker:** `external_proof_custody_verified: false`;
  `proof_custody_record: null`. The runtime authority boundary itself passes (no proof-minting
  in `integration.py`, no private key in `deployment.py` or Helm, ExecutionGate blocks
  `deny`/`require_approval`), but no independent witness/vault custody record exists for the
  release proofs. A prior working-tree `vault-audit/20260720-0345` reference is classified
  unverified and excluded.
- **Required owner action:** Demonstrate external proof issuance and custody (independent
  witness or vault) for required-mode execution and record it.
- **Required credentials/environment:** Access to the external vault/witness system; owner
  identity.
- **Procedure:** Owner-defined per custody policy; the repository does not (and must not)
  contain a tool that can self-issue this evidence. Result is a structured
  `proof_custody_record` string in `REMOTE_SUCCESSOR_EVIDENCE.json`.
- **Evidence to capture:** vault/witness identity, custody reference, timestamps, reviewer.
- **Expected success condition:** blockers mode no longer lists
  `external_proof_custody_verified`.
- **Rollback/failure handling:** No record → gate stays fail-closed. Nothing to roll back.
- **Dependencies:** G1 (custody chain of the rotated key).
- **Classification:** Non-destructive; externally consequential (trust/custody claim).

### Step 3 — G15: Artifact signing and certificate provisioning

- **Governing document:** `docs/deployment/WINDOWS_INSTALLER.md` ("Signing");
  `tools/sign_windows_artifact.ps1`; `docs/operations/PRODUCTION_READINESS_STATUS.md`
  (unsigned-build rows).
- **Exact current blocker:** No code-signing certificate is configured anywhere.
  `sign_windows_artifact.ps1` reads `CODESIGN_CERT_PATH` / `CODESIGN_CERT_PASSWORD`; both
  unset, so every signing call is an honest no-op ("unsigned: no signing certificate
  configured"). Desktop/API onedir executables, both MSIs, and the Burn bundle are unsigned;
  SmartScreen will flag them. (Container-image signing is separate and already
  `image_signatures_verified: true` via cosign v3.1.2 — but bound to branch provenance; see G3.)
- **Required owner action:** Procure a code-signing certificate (EV or standard, owner
  decision); provision it to the build host.
- **Required credentials/environment:** Certificate file + password (or HSM/token), Windows
  build host with WiX v7 and signtool.
- **Exact procedure:**

  ```powershell
  $env:CODESIGN_CERT_PATH = '<path-to-cert>'
  $env:CODESIGN_CERT_PASSWORD = '<password>'
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build_windows_installer.ps1 -OutputRoot build\acceptance\windows-installer
  ```

  The build script signs both onedir executables before MSI packaging, both MSIs, and the
  Burn bootstrapper.
- **Evidence to capture:** signtool output (non-no-op), `Get-AuthenticodeSignature` results on
  all five artifacts, SHA-256 of each signed artifact.
- **Expected success condition:** All artifacts report a valid Authenticode signature.
- **Rollback/failure handling:** A failed signing run leaves prior unsigned artifacts in
  `build/`; rebuild is repeatable. Never store certificate material in the repository.
- **Dependencies:** None strictly, but must precede the final elevated smoke (G11) so the
  smoke exercises the shipping (signed) artifact.
- **Classification:** Non-destructive; reversible (rebuildable); externally consequential once
  signed artifacts are distributed (they are not to be distributed under current prohibition).

### Step 4 — G8: Target approval

- **Governing document:** CAB pack "Release-blocking conditions";
  `docs/operations/cab/PRODUCTION_DEPLOYMENT_DETAILS.md`;
  `docs/operations/cab/ROLLBACK_RUNBOOK.md` ("Required before deployment" — all rows TBD).
- **Exact current blocker:** `target_environment_approved: false`;
  `target_environment_record: null`. No approved production cluster, context, namespace, Helm
  release, maintenance window, implementer, rollback owner, approver, support owner, paging
  route, secret manager, or acceptance authority is recorded.
- **Required owner action:** Owner/CAB names and approves all twelve items and records them.
- **Required credentials/environment:** None technical; organizational decision authority.
- **Procedure:** Complete the TBD table in `ROLLBACK_RUNBOOK.md` and
  `PRODUCTION_DEPLOYMENT_DETAILS.md`; write the structured `target_environment_record`.
- **Evidence to capture:** the completed named-role record; approver identity; date.
- **Expected success condition:** blockers mode no longer lists `target_environment_approved`.
- **Rollback/failure handling:** Nothing to roll back; absence keeps everything downstream
  blocked.
- **Dependencies:** None, but it is the precondition for G5/G6/G7/G9/G10 (their evidence must
  be produced "in the approved target").
- **Classification:** Non-destructive; reversible (approval can be withdrawn); externally
  consequential (authorizes infrastructure work).

### Step 5 — G3 + G4 (joint): Release provenance and SBOM attestations (single re-publish)

- **Governing document:** `docs/operations/cab/EXTERNAL_AUDITOR_EVIDENCE_2026-07-20.md`;
  `tools/verify_pre_deployment.py::verify_publish_workflow` / `verify_supply_chain_policy`;
  `.github/workflows/publish.yaml`; `tools/sign_and_attest_image.sh`;
  `tools/verify_supply_chain.py` + `tools/supply_chain_policy.json`.
- **Exact current blocker:**
  - `release_provenance_verified: false` — all eight candidate digests were signed from the
    unmerged branch `agent/production-readiness-2026-07-19` via `workflow_dispatch`. Live
    confirmation this session: strict cosign verification fails with SAN
    `https://github.com/IAmSoThirsty/Project-AI/.github/workflows/publish.yaml@refs/heads/agent/production-readiness-2026-07-19`,
    which does not match the approved regexp
    `^https://github[.]com/IAmSoThirsty/Project-AI/[.]github/workflows/publish[.]yaml@refs/(tags/v[^/]+|heads/main)$`.
  - `sbom_attestations_verified: false` — SPDX and SLSA attestations are confirmed absent 0/8
    (`sbom_attestations: []` in this session's registry-layer run). The corrected
    `publish.yaml` (cosign attest via `sign_and_attest_image.sh`) has never executed;
    attestations are build-time and cannot be applied retroactively.
- **Required owner/external action:** Owner merges the successor to `main` (or creates a
  `refs/tags/v*` tag) and re-runs the corrected publish workflow so all eight images
  (`api`, `docs-portal`, `proof-portal`, `operator-console`, `swr`, `atlas`, `arbiter-rlp`,
  `genesis`) are rebuilt, signed, and attested under release provenance. This is an external
  publication event — **prohibited without explicit owner authorization.**
- **Required credentials/environment:** GitHub push/merge/tag rights on
  `IAmSoThirsty/Project-AI`; GitHub Actions OIDC (ambient in workflow); ghcr.io publish rights.
- **Exact verification commands (after re-publish, digests updated in evidence record):**

  ```powershell
  uv run python tools/verify_supply_chain.py --layer registry --json
  uv run python tools/verify_supply_chain.py --layer cosign --require-attestations
  ```

  Both must pass **without** `--allow-branch-provenance`.
- **Evidence to capture:** new 8/8 digests; 8/8 `signature_verifications` and 8/8
  `sbom_attestations` records (spdxjson + slsaprovenance, cosign ≥ 3) in
  `REMOTE_SUCCESSOR_EVIDENCE.json`; CI run URL; certificate SAN matching the approved regexp.
- **Expected success condition:** strict cosign layer exit 0 with attestations required;
  blockers mode drops both flags.
- **Rollback/failure handling:** A failed publish run leaves prior images untouched (new
  digests only on success); never delete published digests (append-only registry posture).
  If verification fails, the evidence record must not be updated.
- **Dependencies:** G1/G2 (owner authority chain), G8 recommended first (CAB sequencing);
  supersedes the current candidate digests — every downstream gate must then reference the new
  immutable digests.
- **Classification:** **Externally consequential (publication)**; not destructive; not
  reversible in the "unpublish" sense. Explicitly prohibited without owner authorization.

### Step 6 — G5 + G10 (joint): Production overlay completion and placeholder ingress replacement

- **Governing document:** `helm/values.prod.yaml`;
  `tools/verify_pre_deployment.py::verify_production_values` (rejects `*.example.com` in
  ingress and TLS hosts) and `verify_v3q_authority_boundary` production assertions
  (`v3q.required: true`, `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=true`);
  `docs/operations/cab/PRODUCTION_DEPLOYMENT_DETAILS.md`; `docs/deployment/HELM_DEPLOY.md`.
- **Exact current blocker:** `production_overlay_verified: false`;
  `production_overlay_record: null`; machine gate `production_ingress_host` fails —
  `helm/values.prod.yaml` still carries placeholder host `project-ai.example.com` in ingress
  and TLS. (This session's structural render check passed 47 manifests digest-pinned; the
  placeholder rejection is enforced by `verify_production_values`, which failed as required.)
- **Required owner action:** Platform owner supplies the approved production namespace,
  real ingress host(s), TLS configuration, and secret source; edits `helm/values.prod.yaml`
  accordingly (owner-authorized change; currently prohibited to agents).
- **Required credentials/environment:** Approved DNS name(s) and TLS issuer for the target
  (G8); helm CLI.
- **Exact verification command:**

  ```powershell
  helm template project-ai helm/project-ai --namespace project-ai-prod -f helm/values.prod.yaml | uv run python tools/verify_helm_template.py --expected-namespace project-ai-prod --project-image-registry ghcr.io --project-image-owner iamsothirsty --require-project-image-digests
  uv run python tools/verify_pre_deployment.py --report
  ```

- **Evidence to capture:** overlay diff review; render output; `production_overlay_record`
  string; passing `production Helm values` gate in report mode.
- **Expected success condition:** `verify_production_values` passes (no placeholder hosts);
  `production_overlay_verified` flips with a structured record.
- **Rollback/failure handling:** Overlay edits are plain-file reversible via Git; keep the
  placeholder until a real host is approved (fail-closed by design).
- **Dependencies:** G8 (approved target/hostname). If digests change under G3/G4, the overlay
  must pin the new digests.
- **Classification:** Repository file change (reversible) + externally consequential naming
  (public DNS/TLS identity). Not destructive.

### Step 7 — G6: Remote backup configuration and restore proof

- **Governing document:** `tools/verify_pre_deployment.py::verify_production_backup`;
  `helm/values.prod.yaml` (`backup.remote`); `helm/project-ai/templates/backup.yaml`;
  `tools/backup_audit_data.sh` / `tools/restore_audit_data.sh`;
  `docs/operations/cab/ROLLBACK_RUNBOOK.md` ("Data and state impact").
- **Exact current blocker:** `remote_backup_verified: false`; machine gate
  `production_remote_backup` fails — `backup.remote.enabled: false` with empty `destination`
  and `secretName`. The backup CronJob has never been proven against a real remote target; a
  CAB-approved backup **and restore rehearsal** is mandatory.
- **Required owner/external action:** Configure a real remote backup destination + secret in
  the approved target; run a backup; prove a restore.
- **Required credentials/environment:** Approved cluster (G8); remote storage endpoint and
  credentials in the target's secret manager.
- **Procedure:** Set `backup.remote.enabled: true`, `destination`, `secretName` in
  `helm/values.prod.yaml` (owner-authorized change); deploy/exercise the CronJob in the
  approved target; execute `restore_audit_data.sh` restore rehearsal; record results.
- **Evidence to capture:** backup artifact listing at the remote destination; restore
  rehearsal log with timestamps; `remote_backup_record` string.
- **Expected success condition:** `verify_production_backup` passes; blockers mode drops both
  backup entries.
- **Rollback/failure handling:** Restore rehearsal must target rehearsal data, never live
  volumes; failed rehearsal keeps the gate closed.
- **Dependencies:** G8 (target + secret manager); G5 (overlay carries the config).
- **Classification:** External infrastructure mutation — **prohibited to agents**; rehearsal
  is potentially destructive if mis-targeted (must be isolated); externally consequential.

### Step 8 — G7: Monitoring CRD deployment and paging verification

- **Governing document:** `docs/operations/cab/MONITORING_ALERTING_PLAN.md`; Helm templates
  `monitoring.yaml`, `servicemonitor.yaml`, `prometheusrule.yaml` and verification CronJobs;
  CAB pack release-blocking conditions.
- **Exact current blocker:** `monitoring_crds_verified: false`; `monitoring_crds_record: null`.
  Prometheus Operator CRDs are not installed in any approved target and no alert/page delivery
  has been proven. There is intentionally no local script that can attest this.
- **Required external action:** Install Prometheus Operator CRDs in the approved cluster;
  deploy the chart's monitors/rules; fire a test alert; prove delivery through the approved
  paging route.
- **Required credentials/environment:** Cluster admin on the approved target; paging provider
  access (route named in G8's record).
- **Procedure:** Per `MONITORING_ALERTING_PLAN.md`; capture `kubectl get crd`, ServiceMonitor/
  PrometheusRule admission, alertmanager test-fire, and the received page.
- **Evidence to capture:** CRD listing, rendered monitors admitted, alert delivery proof
  (page receipt with timestamp); `monitoring_crds_record` string.
- **Expected success condition:** blockers mode drops `monitoring_crds_verified`.
- **Rollback/failure handling:** CRD installation is cluster-scoped — removal affects other
  tenants; treat as forward-only infrastructure change under the target owner's control.
- **Dependencies:** G8 (approved target); G5 (overlay enables monitoring).
- **Classification:** External infrastructure mutation — **prohibited to agents**; reversible
  with care; externally consequential.

### Step 9 — G9: Rollback rehearsal

- **Governing document:** `docs/operations/cab/ROLLBACK_RUNBOOK.md` (§4 procedure,
  "Rehearsal record" table — currently all "Not run"/"Missing").
- **Exact current blocker:** `rollback_rehearsal_verified: false`;
  `rollback_rehearsal_record: null`. No rehearsal executed; `v0.0.1` is explicitly NOT
  certified known-good.
- **Required external action:** Rollback owner (named in G8) rehearses a Helm revision
  rollback in the approved target and records the full table.
- **Required credentials/environment:** Approved cluster + Helm release (G8); a known-good
  prior revision to roll back to.
- **Exact procedure (runbook §4):**

  ```powershell
  helm rollback project-ai <PREVIOUS_REVISION> `
    --namespace <NAMESPACE> `
    --wait --timeout 10m --cleanup-on-fail
  ```

  plus evidence preservation (`helm status`/`history`, `kubectl get pods,deployments,...`),
  verification (`kubectl rollout status`, `/health/live`, `/metrics`), and release-independent
  checks `uv run python tools/canonical_replay.py` and
  `uv run python tools/verify_frozen_history.py`.
- **Evidence to capture:** completed rehearsal record (environment, from/to revision, trigger,
  duration, data validation, audit continuity, owner acceptance).
- **Expected success condition:** blockers mode drops `rollback_rehearsal_verified`.
- **Rollback/failure handling:** Helm rollback does not reverse DB/PVC state — the rehearsal
  must validate data-state handling per G6's restore proof; a failed rehearsal is itself
  recorded evidence and keeps the gate closed.
- **Dependencies:** G8 (target/owners), G6 (backup/restore), G5 (deployed overlay).
- **Classification:** External infrastructure mutation in a rehearsal context —
  **prohibited to agents**; potentially service-affecting; externally consequential.

### Step 10 — G12: Legacy-state repository restoration or authorized relocation record

- **Governing document:** `tools/verify_legacy_state.py` + `tools/legacy_source_guard.py`
  (`DEFAULT_LEGACY_ROOT = T:\00-Active\Project-AI-main`, override env
  `PROJECT_AI_LEGACY_REPO`); `docs/internal/LEGACY_SOURCE_STATE.json`; AGENTS.md §2.1.
- **Exact current blocker:** Re-confirmed this session at 18:44:14 UTC: verifier exits 1
  because `git -C T:\00-Active\Project-AI-main rev-parse HEAD` exits 128 — the read-only
  legacy repository is absent from this host (directory listing of `T:\00-Active` contains no
  `Project-AI-main`).
- **Required owner action:** Workspace owner either (a) restores the legacy repository
  byte-identical at `T:\00-Active\Project-AI-main` (HEAD must match
  `docs/internal/LEGACY_SOURCE_STATE.json`), or (b) records an authorized relocation
  (new path + `PROJECT_AI_LEGACY_REPO` setting + continuity entry), or (c) records an
  authorized permanent-disposition decision. Relocation/restoration is
  **prohibited to agents** under current authority.
- **Required credentials/environment:** Access to the legacy repository copy/backup.
- **Exact verification command:** `uv run python tools/verify_legacy_state.py`
  (with `PROJECT_AI_LEGACY_REPO` set if relocated).
- **Evidence to capture:** verifier exit 0 output (snapshot match, frozen-history containment,
  2264 sections, SHA-256 match, unchanged-during-verification), or the signed relocation/
  disposition record.
- **Expected success condition:** exit 0, or an owner-recorded disposition that amends the
  acceptance-gate expectations.
- **Rollback/failure handling:** The legacy tree is READ-ONLY — restoration must never write
  into it; a hash mismatch after restoration is a stop-and-report event.
- **Dependencies:** None; blocks G13 (acceptance gate includes the legacy-state step).
- **Classification:** Blocked by missing legacy workspace; restoration is non-destructive;
  disposition decision is owner-only.

### Step 11 — G11: Elevated Windows installer install/smoke/uninstall run

- **Governing document:** `docs/deployment/WINDOWS_INSTALLER.md`;
  `tools/build_windows_installer.ps1`; `tools/smoke_windows_installer.ps1`;
  `docs/operations/PRODUCTION_READINESS_STATUS.md` (exit-124 row).
- **Exact current blocker:** Build succeeded (two MSIs + Burn bundle; current bundle SHA-256
  `0DF24708B3CBA40C663112E2382059730B87CFB0499788F0231ECA2EC73FE4A8`). Smoke exited 124 after
  1200 s because Burn launches an elevated engine and the agent session is unelevated
  (`IsInRole(Administrator)` false) — elevation cannot be approved non-interactively. Not
  retried (would reproduce).
- **Required owner action:** Run the smoke once from an **elevated interactive** PowerShell on
  a Windows host (ideally after G15 signing, so the signed bundle is what is smoked).
- **Required credentials/environment:** Local Administrator; WiX-built bundle present.
- **Exact procedure:**

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\smoke_windows_installer.ps1 -BundleExe .\build\acceptance\windows-installer\installer\Project-AI-Desktop-Setup.exe
  ```

- **Evidence to capture:** exit 0 with all script assertions (install, both exes present, ARP
  registry entry, app launch + bundled API server spawn/terminate, silent uninstall, install
  root and ARP removal, audit evidence retained at
  `%LOCALAPPDATA%\Project-AI-Desktop\data\chimera-audit.jsonl`); install/uninstall logs.
- **Expected success condition:** exit 0; status row promoted from exit 124.
- **Rollback/failure handling:** The script uninstalls on its own path; on failure, run
  `Project-AI-Desktop-Setup.exe /quiet /uninstall /log uninstall.log` manually and verify ARP
  cleanup before retrying.
- **Dependencies:** G15 recommended first (smoke the signed artifact).
- **Classification:** Requires elevated interactive execution — **prohibited in this
  session**; mutating on the test host (installs/uninstalls); reversible; not externally
  consequential.

### Step 12 — G13: Clean-checkout whole-gate run

- **Governing document:** `tools/acceptance_gate.ps1` (clean-checkout assertions bracket the
  full step list); `docs/operations/PRODUCTION_READINESS_STATUS.md` ("Acceptance steps not
  promoted").
- **Exact current blocker:** The whole-gate run has never executed end-to-end because its
  clean-baseline and final-clean-checkout assertions conflict with the intentionally preserved
  dirty workspace (346 dirty/untracked entries at this session's snapshot, including `.vs/`,
  `data/`, `output/`, `plans/`, `500`, and the zero-byte `{'chunk_id` awaiting operator
  review). Individual steps were exercised and recorded as the sanctioned alternative.
- **Required owner action:** Owner decides the disposition of the dirty workspace (commit,
  archive, or discard — discard is destructive and owner-only), or provides a separate clean
  authorized checkout of the candidate commit; then runs the whole gate there.
- **Required credentials/environment:** Full local toolchain (uv/Python 3.12.10, Docker,
  helm, WiX, Android SDK, Rust, pnpm), elevation for the installer step, and the legacy repo
  (G12) for the legacy-state step.
- **Exact procedure:**

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\acceptance_gate.ps1
  ```

- **Evidence to capture:** whole-gate exit 0 log with per-step results; the clean
  `git status --porcelain --untracked-files=all` baseline and final assertions.
- **Expected success condition:** exit 0 in a clean checkout of the candidate commit.
- **Rollback/failure handling:** The gate is fail-fast; any generated/untracked write fails
  the final assertion — investigate before rerunning. Never run it over the preserved dirty
  workspace (it would fail immediately and any cleanup would be destructive).
- **Dependencies:** G12 (legacy-state step), G11 (elevation for installer step), workspace
  disposition decision.
- **Classification:** Requires explicit owner approval (workspace disposition) + elevated
  execution; mutating (builds, containers, MSI install); reversible.

### Step 13 — G14: Fresh Compose rebuild and startup

- **Governing document:** `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` ("Mandatory candidate
  gates"); `tools/verify_compose_health.py`.
- **Exact current blocker:** Health has only been verified against the pre-existing running
  stack (re-confirmed this session: 9/9 healthy, readonly/cap_drop=ALL/no-new-privileges
  verified — see Evidence Appendix). A fresh `up -d --build --wait` was deliberately not run
  over the live persistent volumes; rebuilding the live stack is **prohibited without owner
  authorization** (infrastructure mutation over live state).
- **Required owner action:** Authorize and run a fresh build/start in a context that does not
  clobber live volumes (fresh volumes or after G6 backup proof), then re-verify health.
- **Required credentials/environment:** Docker Desktop/daemon on the host.
- **Exact procedure:**

  ```powershell
  docker compose config --quiet
  docker compose up -d --build --wait --wait-timeout 240
  uv run python tools/verify_compose_health.py
  ```

- **Evidence to capture:** build log; `compose runtime: 9/9 healthy and security settings
  verified` from the fresh stack; image digests used.
- **Expected success condition:** verifier exit 0 from a freshly built stack.
- **Rollback/failure handling:** `docker compose down` (without `-v` — never remove volumes
  autonomously); restore from G6 backups if state is affected.
- **Dependencies:** Owner authorization; ideally after G6 (backups proven) and in the G13
  clean-checkout context.
- **Classification:** Infrastructure mutation on the host — **prohibited in this session**;
  mostly reversible; volume-destructive only if misused.

### Step 14 — Evidence-record closure (owner)

- **Governing document:** `tools/verify_pre_deployment.py::verify_remote_successor_evidence`;
  `docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json`.
- **Action:** Only after G1–G9 evidence physically exists on the same immutable successor:
  owner (or explicitly authorized agent) writes the structured records, sets every `required.*`
  flag true, sets `review_only: false`, `status: "verified"`. Setting `status: "verified"`
  before the evidence exists is prohibited and would be a falsified record.
- **Verification:** all three `verify_pre_deployment.py` modes exit 0.
- **Classification:** Owner-only record of externally produced facts.

### Step 15 — Final verification sequence and CAB authorization

Run the Phase 4 sequence (below). Deployment authorization is granted by the CAB on the
successor CAB review pack once every condition is evidenced on the same immutable candidate;
the owner (Jeremy Karrick) holds the owner-controlled prerequisites. Until then the recorded
decision remains **DEPLOYMENT NOT AUTHORIZED**.

---

## Phase 2 — Classification: executable now vs. owner handoff

| Gate | Classification | Executable this session? |
|------|----------------|--------------------------|
| G1 Owner key rotation | Requires owner credentials + explicit owner approval | No — prohibited (key rotation) |
| G2 External proof custody | Requires owner credentials + external witness/vault | No |
| G3 Release provenance | Requires external publication (merge/tag + re-publish) | No — prohibited (publication/push) |
| G4 SBOM attestations | Requires external publication (same re-publish) | No — prohibited |
| G5 Production overlay | Requires external infrastructure + owner approval | No — file edit prohibited (`helm/values.prod.yaml`) |
| G6 Remote backup | Requires external infrastructure + credentials | No — prohibited (backup configuration) |
| G7 Monitoring CRDs | Requires external infrastructure | No — prohibited (monitoring deployment) |
| G8 Target approval | Requires explicit owner/CAB approval | No — organizational decision |
| G9 Rollback rehearsal | Requires external infrastructure | No — prohibited (infrastructure mutation) |
| G10 Placeholder ingress | Requires owner-approved host (folds into G5) | No — file edit prohibited |
| G11 Elevated installer run | Requires elevated interactive execution | No — session unelevated, non-interactive |
| G12 Legacy-state restoration | Blocked by missing legacy workspace; owner decision | No — prohibited (legacy relocation) |
| G13 Clean-checkout whole gate | Requires explicit owner approval (workspace disposition) + elevation | No |
| G14 Fresh Compose rebuild | Requires explicit owner approval (live-state mutation) | No — prohibited (rebuild live stack) |
| G15 Signing/certificate | Requires owner-provided credentials (certificate) | No — prohibited (signing) |

**Executed this session (authorized, read-only evidence refresh only):** pre-deployment
verifier (3 modes), legacy-state verifier, supply-chain registry layer + strict cosign layer,
compose health against the existing stack, production Helm render check, evidence-file
hashing, Git snapshots. **Zero gates were closed, modified, reinterpreted, or simulated.**
Results in the Evidence Appendix.

---

## Phase 3 — Owner handoff packets

One packet per non-executable gate (G3+G4 and G5+G10 merged where a single action closes
both). "Consequence if skipped" is uniform in one respect: `verify_pre_deployment.py` remains
exit 1 and deployment stays prohibited; per-packet consequences add specifics.

### Packet 1 — Retire the former owner key with verifiable custody evidence (G1)

- **Why not completable now:** Owner-only cryptographic authority; agents must not
  self-ratify; key rotation explicitly prohibited under current authorization.
- **Prerequisites:** Offline signing system; approved custody policy; off-repository key
  storage.
- **Operator steps:** Follow `docs/operations/cab/V3Q_OWNER_KEY_ROTATION.md` §1–§8: confirm
  retirement/destruction of `owner-primary` material and affected local image layers; if
  rotating again, generate off-repo, enroll, ratify, verify; assemble the custody evidence
  set; write `owner_key_rotation_record` and flip the flag in
  `docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json`.
- **Verification command:** `uv run python packages/thirstys-standard-v3q/tools/verify_ratification.py --manifest packages/thirstys-standard-v3q/thirstys-standard-v3q.ratified.manifest.yaml --record packages/thirstys-standard-v3q/owner-ratification.json --registry packages/thirstys-standard-v3q/trusted-keys.json` then `uv run python tools/verify_pre_deployment.py --blockers`.
- **Expected pass evidence:** ratification verify exit 0; blockers list no longer contains
  `owner_key_rotation_verified`.
- **Update afterward:** `REMOTE_SUCCESSOR_EVIDENCE.json`, continuity map entry.
- **Consequence if skipped:** Trust root remains compromised-treated; every downstream release
  claim is unratifiable.

### Packet 2 — Record external proof custody (G2)

- **Why not completable now:** Requires an independent external witness/vault; no repository
  tool can (or should) self-issue it.
- **Prerequisites:** Packet 1; vault/witness system access.
- **Operator steps:** Issue/deposit the release proofs with the external custodian; obtain the
  custody reference; write `proof_custody_record`.
- **Verification command:** `uv run python tools/verify_pre_deployment.py --blockers`.
- **Expected pass evidence:** `external_proof_custody_verified` absent from blockers.
- **Update afterward:** `REMOTE_SUCCESSOR_EVIDENCE.json`, continuity map.
- **Consequence if skipped:** Runtime required-mode execution has no independently custodied
  proof source; authority boundary claim is incomplete.

### Packet 3 — Re-publish the eight images under release provenance with attestations (G3+G4)

- **Why not completable now:** Publication, push, and release creation are prohibited;
  requires GitHub merge/tag rights and a workflow run.
- **Prerequisites:** Packets 1–2; owner decision to merge `agent/production-readiness-2026-07-19`
  to `main` or cut `v*` tag; CAB sequencing.
- **Operator steps:** Merge/tag; run the corrected `.github/workflows/publish.yaml` from the
  approved ref; collect the eight new digests; update `REMOTE_SUCCESSOR_EVIDENCE.json`
  digests + signature + attestation records.
- **Verification command:** `uv run python tools/verify_supply_chain.py --layer cosign --require-attestations` (no `--allow-branch-provenance`), then `uv run python tools/verify_supply_chain.py --layer registry --json`.
- **Expected pass evidence:** exit 0 both layers; SAN matches
  `...publish.yaml@refs/(tags/v*|heads/main)`; 8/8 spdxjson + slsaprovenance attestations.
- **Update afterward:** `REMOTE_SUCCESSOR_EVIDENCE.json` (`release_provenance_verified`,
  `sbom_attestations_verified`, digests), CAB pack, continuity map.
- **Consequence if skipped:** Candidate images remain branch-provenance with zero attestations
  — permanently unacceptable for release (attestations cannot be added retroactively).

### Packet 4 — Approve and record the production target (G8)

- **Why not completable now:** Organizational approval; no infrastructure exists to point at.
- **Prerequisites:** None technical.
- **Operator steps:** Name and approve cluster, context, namespace, Helm release, maintenance
  window, implementer, rollback owner, approver, support owner, paging route, secret manager,
  acceptance authority; complete the TBD tables in `ROLLBACK_RUNBOOK.md` and
  `PRODUCTION_DEPLOYMENT_DETAILS.md`; write `target_environment_record`.
- **Verification command:** `uv run python tools/verify_pre_deployment.py --blockers`.
- **Expected pass evidence:** `target_environment_approved` absent from blockers.
- **Update afterward:** CAB docs above; `REMOTE_SUCCESSOR_EVIDENCE.json`; continuity map.
- **Consequence if skipped:** G5/G6/G7/G9/G10 have no approved place to be evidenced; nothing
  downstream can proceed.

### Packet 5 — Complete the production overlay with a real ingress host (G5+G10)

- **Why not completable now:** `helm/values.prod.yaml` is on the prohibited-modification list;
  a real host requires the approved target.
- **Prerequisites:** Packet 4 (host/namespace/TLS decisions); new digests from Packet 3 if
  re-published.
- **Operator steps:** Replace placeholder ingress + TLS hosts with approved names; set secret
  source; keep `v3q.required: true` and `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=true`; review
  diff; write `production_overlay_record`.
- **Verification command:** the helm render pipe to `tools/verify_helm_template.py`
  (Phase 1 Step 6), then `uv run python tools/verify_pre_deployment.py --report`.
- **Expected pass evidence:** `production Helm values` gate PASS; `production_ingress_host`
  blocker gone.
- **Update afterward:** `helm/values.prod.yaml`, `REMOTE_SUCCESSOR_EVIDENCE.json`,
  continuity map.
- **Consequence if skipped:** Machine gate fails forever on the placeholder; overlay
  unverifiable.

### Packet 6 — Configure remote backup and prove a restore (G6)

- **Why not completable now:** Backup configuration is prohibited; requires target
  infrastructure + secrets.
- **Prerequisites:** Packets 4–5.
- **Operator steps:** Provision remote destination + secret; enable `backup.remote` in the
  overlay; run the CronJob; perform a restore rehearsal onto rehearsal state; write
  `remote_backup_record`.
- **Verification command:** `uv run python tools/verify_pre_deployment.py --report` (production
  backup gate) plus rehearsal log review.
- **Expected pass evidence:** `production backup` gate PASS; restore log with matching hashes.
- **Update afterward:** overlay, `REMOTE_SUCCESSOR_EVIDENCE.json`, continuity map.
- **Consequence if skipped:** No proven data recovery path; rollback rehearsal (Packet 8)
  cannot honestly pass; data-loss exposure in production.

### Packet 7 — Install monitoring CRDs and prove paging (G7)

- **Why not completable now:** Monitoring deployment prohibited; needs cluster admin on an
  approved target.
- **Prerequisites:** Packets 4–5.
- **Operator steps:** Install Prometheus Operator CRDs; deploy chart monitors/rules; fire test
  alert; capture page receipt; write `monitoring_crds_record`.
- **Verification command:** `kubectl get crd | findstr monitoring.coreos.com` in the target;
  `uv run python tools/verify_pre_deployment.py --blockers`.
- **Expected pass evidence:** CRDs present; page received via approved route; blocker gone.
- **Update afterward:** `REMOTE_SUCCESSOR_EVIDENCE.json`, `MONITORING_ALERTING_PLAN.md`
  evidence section, continuity map.
- **Consequence if skipped:** Production would run blind — no alerting, no paging; CAB
  condition unmet.

### Packet 8 — Rehearse a production rollback (G9)

- **Why not completable now:** Infrastructure mutation prohibited; no target exists.
- **Prerequisites:** Packets 4–7.
- **Operator steps:** `ROLLBACK_RUNBOOK.md` §4 in the approved target; complete the rehearsal
  record table; obtain rollback-owner acceptance; write `rollback_rehearsal_record`.
- **Verification command:** `uv run python tools/verify_pre_deployment.py --blockers` plus
  runbook table review.
- **Expected pass evidence:** rehearsal table complete; blocker gone.
- **Update afterward:** `ROLLBACK_RUNBOOK.md`, `REMOTE_SUCCESSOR_EVIDENCE.json`, continuity map.
- **Consequence if skipped:** No proven recovery from a bad deploy; CAB condition unmet.

### Packet 9 — Provision code-signing and rebuild signed installers (G15)

- **Why not completable now:** Signing prohibited; no certificate exists on the host.
- **Prerequisites:** Certificate procurement (owner purchase/issuance decision).
- **Operator steps:** Set `CODESIGN_CERT_PATH`/`CODESIGN_CERT_PASSWORD`; rerun
  `tools/build_windows_installer.ps1`; verify Authenticode on all five artifacts; record
  hashes.
- **Verification command:** `Get-AuthenticodeSignature <artifact> | Format-List Status,SignerCertificate`.
- **Expected pass evidence:** `Status: Valid` on both onedir exes, both MSIs, bundle.
- **Update afterward:** `PRODUCTION_READINESS_STATUS.md` signing rows, continuity map.
- **Consequence if skipped:** SmartScreen-flagged unsigned binaries; distribution unacceptable.

### Packet 10 — Run the elevated installer smoke (G11)

- **Why not completable now:** Session is unelevated and non-interactive; Burn's elevation
  prompt cannot be approved.
- **Prerequisites:** Packet 9 (smoke the signed bundle) — or run against the current unsigned
  bundle (SHA-256 `0DF24708...E4A8`) purely to clear the functional gate.
- **Operator steps:** Elevated interactive PowerShell →
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\smoke_windows_installer.ps1 -BundleExe .\build\acceptance\windows-installer\installer\Project-AI-Desktop-Setup.exe`.
- **Verification command:** the smoke itself; `$LASTEXITCODE` must be 0.
- **Expected pass evidence:** exit 0, all assertions, install/uninstall logs.
- **Update afterward:** `PRODUCTION_READINESS_STATUS.md` (exit-124 row promoted), continuity map.
- **Consequence if skipped:** Installer end-to-end behavior unverified; desktop distribution
  gate open.

### Packet 11 — Restore or disposition the legacy repository (G12)

- **Why not completable now:** The legacy repository is physically absent from this host;
  relocation/restoration is owner-controlled and prohibited to agents.
- **Prerequisites:** Owner's backup/copy of `Project-AI-main`.
- **Operator steps:** Restore at `T:\00-Active\Project-AI-main` (read-only posture), or set
  `PROJECT_AI_LEGACY_REPO` to the authorized new location and record the relocation, or record
  a permanent disposition.
- **Verification command:** `uv run python tools/verify_legacy_state.py`.
- **Expected pass evidence:** exit 0 (snapshot match, frozen-history containment 2264
  sections, SHA-256 match, unchanged during verification).
- **Update afterward:** continuity map; `PRODUCTION_READINESS_STATUS.md` legacy row; relocation
  record if applicable.
- **Consequence if skipped:** Legacy provenance unverifiable on this host; acceptance gate
  (Packet 12) cannot pass its legacy step.

### Packet 12 — Whole-gate run in a clean checkout (G13)

- **Why not completable now:** Requires owner disposition of the preserved dirty workspace
  (346 entries) or a separate clean checkout; includes elevated and legacy-dependent steps.
- **Prerequisites:** Packets 10–11; workspace disposition decision (note the unreviewed
  zero-byte `{'chunk_id` file and untracked `500`, `.vs/`, `data/`, `output/`, `plans/`).
- **Operator steps:** In a clean checkout of the candidate commit:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\acceptance_gate.ps1`.
- **Verification command:** the gate itself; exit 0 end-to-end.
- **Expected pass evidence:** all steps PASS including clean-baseline and final-clean-checkout
  assertions.
- **Update afterward:** `PRODUCTION_READINESS_STATUS.md` completion-pass table, continuity map.
- **Consequence if skipped:** The individually-recorded steps remain the only evidence; the
  composed clean-tree guarantee is unproven.

### Packet 13 — Fresh Compose rebuild and health verification (G14)

- **Why not completable now:** Rebuilding over the live stack/volumes is prohibited without
  owner authorization.
- **Prerequisites:** Owner authorization; ideally Packet 6 (backups proven) and Packet 12
  context.
- **Operator steps:** `docker compose config --quiet` →
  `docker compose up -d --build --wait --wait-timeout 240` →
  `uv run python tools/verify_compose_health.py`.
- **Verification command:** the health verifier; expect
  `compose runtime: 9/9 healthy and security settings verified`.
- **Expected pass evidence:** exit 0 from a freshly built stack.
- **Update afterward:** `PRODUCTION_READINESS_STATUS.md` compose row, continuity map.
- **Consequence if skipped:** Only the long-running stack is evidenced; cold-build/startup
  path unproven.

---

## Phase 4 — Final verification sequence (run only after all owner/external actions)

Order matters; every step must exit 0 with current evidence, on the same immutable candidate:

1. Elevated installer smoke: `tools\smoke_windows_installer.ps1` → exit 0.
2. Legacy-state verifier: `uv run python tools/verify_legacy_state.py` → exit 0 (or recorded
   disposition).
3. Clean-checkout whole gate: `tools\acceptance_gate.ps1` → exit 0.
4. Fresh Compose rebuild + `uv run python tools/verify_compose_health.py` → 9/9 healthy.
5. Signed artifacts + attestations:
   `uv run python tools/verify_supply_chain.py --layer registry --json` and
   `uv run python tools/verify_supply_chain.py --layer cosign --require-attestations`
   (strict, no branch-provenance) → exit 0; `Get-AuthenticodeSignature` valid on installer
   artifacts.
6. Backup and monitoring evidence: restore-rehearsal log + page receipt current and reviewed.
7. All three pre-deployment modes:
   `uv run python tools/verify_pre_deployment.py`, `--report`, `--blockers` → all exit 0.
8. Complete production-readiness verification: report mode shows 23/23 PASS (report mode is
   the complete verifier; there is no separate overall script).
9. Blockers mode confirms **zero** mandatory blockers.
10. Deployment authorization: `REMOTE_SUCCESSOR_EVIDENCE.json` `status: "verified"`,
    `review_only: false`, all 14 `required.*` true, and the CAB decision in the successor CAB
    review pack updated from **DEPLOYMENT NOT AUTHORIZED** by the named acceptance authority.

Only when all ten hold may the final report state "Production-ready and authorized for
deployment." Anything less must state the first true condition of: Owner actions incomplete /
External infrastructure incomplete / Production verification incomplete.

**Current verdict: Owner actions incomplete.** (External infrastructure is also incomplete;
see blockers.) Production deployment and publication remain prohibited.

---

## Evidence Appendix — Read-only evidence refresh, 2026-07-24 UTC (this session)

Pre-execution snapshot 18:43:38 UTC: HEAD `b022ed746d91161d53a736793b69e84ddeb365ea`, branch
`agent/production-readiness-2026-07-19`, 346 dirty/untracked entries
(`git status --porcelain --untracked-files=all`).

| # | Command | Start (UTC) | Exit | Result |
|---|---------|-------------|------|--------|
| 1 | `uv run python tools/verify_pre_deployment.py` | 18:43:51 | 1 | Fail-closed: remote successor evidence not verified; 9 unresolved fields (owner_key_rotation, external_proof_custody, release_provenance, sbom_attestations, production_overlay, remote_backup, monitoring_crds, target_environment, rollback_rehearsal) |
| 2 | `... --report` | 18:44:01 | 1 | 22 PASS; 3 FAIL: remote successor evidence, production Helm values (placeholder host), production backup (remote disabled) |
| 3 | `... --blockers` | 18:44:05 | 1 | 11 mandatory blockers across owner / external-supply-chain / production; "deployment not authorized" |
| 4 | `uv run python tools/verify_legacy_state.py` | 18:44:14 | 1 | `git -C T:\00-Active\Project-AI-main rev-parse HEAD` exit 128 — legacy repository absent from host |
| 5 | `uv run python tools/verify_supply_chain.py --layer registry --json` | 18:44:33 | 0 | Signature storage layout verified 8/8 (sigstore bundle v0.3, subject-digest bound, no legacy `.sig` tags); `sbom_attestations: []` (absent 0/8); `signature_verifications: []` (registry layer performs no cert check — the JSON field `meets_approved_release_identity: true` reflects only the strict policy mode of the invocation, `not allow_branch_provenance` at `tools/verify_supply_chain.py:473`, not a verified certificate claim) |
| 6 | `uv run python tools/verify_supply_chain.py --layer cosign` (strict) | 18:45:42 | 1 | FAIL as expected: SAN `...publish.yaml@refs/heads/agent/production-readiness-2026-07-19` does not match approved release-identity regexp — live confirmation of the G3 blocker |
| 7 | `uv run python tools/verify_compose_health.py` (existing stack, no rebuild) | 18:46:21 | 0 | 9/9 services healthy; readonly=True, cap_drop=['ALL'], no-new-privileges on all; liveness endpoints live; API version 0.0.3 |
| 8 | `helm template ... -f helm/values.prod.yaml \| verify_helm_template.py --require-project-image-digests` | 18:46:32 | 0 | Structural render pass, 47 manifests, digest-pinned. Placeholder-host rejection is enforced by `verify_production_values` (row 2), which failed as required — consistent, no defect |

SHA-256 evidence-file pins (18:46:46 UTC):

| File | SHA-256 |
|------|---------|
| `docs/operations/cab/REMOTE_SUCCESSOR_EVIDENCE.json` | `DC0D40772B79FCE4F57FEF5B19A043F0D989EFF8A1948C0963106D13124BB89E` |
| `helm/values.prod.yaml` | `A9FEC5BACE7C48A5A3179973F7D58E5F8627D0BBED34C32F7923132E06A6BA30` |
| `packages/thirstys-standard-v3q/trusted-keys.json` | `CE7ADA21212B4E8E97BACE4F8CBF78641C87F61F696FFF8349AB5A4C402C0921` |
| `docs/operations/SECURITY_RELAY_LEGACY_EXCEPTION.md` | `8614A4B6C9E3F8B4DAC6978CF5C00288568EECA83229B2701C8358B2DBAAC7B6` |
| `build/acceptance/windows-installer/installer/Project-AI-Desktop-Setup.exe` | `0DF24708B3CBA40C663112E2382059730B87CFB0499788F0231ECA2EC73FE4A8` |

**Newly verified repository defects found: none.** Every failure observed matches a known,
recorded, externally controlled blocker. The one investigated anomaly
(`meets_approved_release_identity: true` in registry-layer JSON) resolved to a mode-descriptor
field, not a defect; the strict cosign layer independently confirmed the real identity state.

No gate state, evidence record, readiness flag, verifier, credential, infrastructure,
published artifact, Git history, or deployment state was modified by this session. Changes
were limited to this document and one append-only continuity-map entry.
