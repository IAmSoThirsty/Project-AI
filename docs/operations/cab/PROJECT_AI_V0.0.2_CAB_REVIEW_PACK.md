# Project-AI v0.0.2 CAB Review Pack

**Prepared:** 2026-07-19
**Repository:** `IAmSoThirsty/Project-AI`
**Release:** `v0.0.2`
**Release commit:** `82aa1476657e16a1d38caccba38357c83380a3e3`
**Current decision:** **v0.0.2 SUPERSEDED — DEPLOYMENT NOT AUTHORIZED**

This pack converts the provisional CAB review into repository-backed change
records and runbooks. It is a review artifact, not approval to deploy.

## Decision summary

The release and all eight container build jobs were published successfully,
but the exact release CI failed. The remediation working tree now fixes the
known coverage/Compose failures, adds real metrics and operational verifiers,
hardens the Helm chart and workflows, and upgrades the vulnerable locked
`setuptools` version. Those changes are not in v0.0.2. An immutable v0.0.3
candidate must be built from a committed, green revision; v0.0.2 must not be
deployed as a substitute. CAB approval remains blocked because:

1. the exact v0.0.2 GitHub CI run is red and the remediation is not committed,
   pushed, released, or remotely verified;
2. no target cluster/context, approved namespace, maintenance window, named
   implementer, rollback owner, approver, support owner, or paging route is
   recorded;
3. local Compose health and metrics pass, but no live-cluster dry run,
   deployment smoke, alert-delivery test, rollback rehearsal, or acceptance
   sign-off exists;
4. local Checkov, dependency audits, and containerized Trivy scans pass on the
   remediated tree, but no successful successor CodeQL, cosign/attestation,
   Rust audit, or remote CI evidence exists; the published v0.0.2 API digest
   returned `no signatures found`;
5. Alertmanager routing, dashboard import/query proof, and paging ownership
   remain target-environment responsibilities;
6. remote backup is not configured and no restore rehearsal exists;
7. `v0.0.1` is the previous published tag, but it has not been certified as a
   known-good production revision.
8. the earlier local API image contained the ignored V3Q owner private-key
   file; the image and online-authority paths are repaired, but the old key
   must be rotated offline, external proof issuance must be evidenced, and the
   exact V3Q manifest remains unratified.
9. ADR-002 per-program machine credentials are now implemented and locally
   tested, but production still needs live PostgreSQL migration evidence,
   per-program secret provisioning, and owner acceptance of the credential
   inventory and rotation process.

## CAB records

| Record | Purpose | Status |
|---|---|---|
| [Formal change record](FORMAL_CHANGE_RECORD.md) | Objective, scope, impact, ownership, sequencing, decision | Partial — operator fields pending |
| [Rollback runbook](ROLLBACK_RUNBOOK.md) | Trigger, exact Helm recovery path, data impact, validation | Procedure defined; rehearsal and owner pending |
| [Release evidence bundle](RELEASE_EVIDENCE_BUNDLE.md) | Release-specific CI, local gates, supply-chain and security evidence | Partial — exact-commit CI/security evidence incomplete |
| [Production deployment details](PRODUCTION_DEPLOYMENT_DETAILS.md) | Target, values, secrets, ingress, resources, blast radius | Partial — repository defaults documented; real target pending |
| [Monitoring and alerting plan](MONITORING_ALERTING_PLAN.md) | Signals, thresholds, routing, observation and exit criteria | Partial — plan defined; runtime/routing proof pending |
| [Dependency disposition](DEPENDENCY_DISPOSITION.md) | Treatment of open Dependabot PRs | Proposed disposition; owner acceptance pending |
| [Communications and support plan](COMMUNICATIONS_SUPPORT_PLAN.md) | Stakeholder notices, escalation, status cadence | Drafted; names and channels pending |
| [Tracking issue draft](TRACKING_ISSUE_DRAFT.md) | One executable closeout checklist | Ready to copy; no external issue created |
| [V3Q owner-key rotation](V3Q_OWNER_KEY_ROTATION.md) | Containment, owner rotation, ratification, and evidence gate | Build path fixed; rotation and ratification pending |
| [Waterfall rebuild provenance](../INTEGRATION_VERIFICATION_CERBERUS_WATERFALL.md) | Standalone product continuity, copied rebuild, governed adapter boundary, replay evidence | Local replay green; live route/target evidence pending |

## Evidence status

| Evidence | Current result |
|---|---|
| Git tag resolution | `v0.0.2` resolves to `82aa1476657e16a1d38caccba38357c83380a3e3` |
| GitHub Release | Published 2026-07-19 at 08:16:56 UTC |
| Container publish | Passed; Publish run `29679414341` |
| Exact-commit CI | **Failed**; run `29679407137` |
| Initial local Python baseline | Passed: `3020 passed, 5 skipped, 1 xfailed` |
| Governance replay | Passed: `5/5` invariants |
| Frozen history | Passed: `2264/2264` sections |
| Earlier remediated local Python checkpoint | Passed: `3049 passed, 5 skipped, 1 xfailed`; historical working-tree evidence, not v0.0.2 release evidence |
| Current successor working-tree Python suite | Passed: `3406 passed, 5 skipped`, with zero failures, XFAIL/XPASS results, or warnings; not immutable successor evidence |
| Batched branch coverage | Passed: `87.32%` combined, threshold `80%` |
| Governance/frozen history | Passed: `5/5` and `2264/2264`, including inside rebuilt API image |
| Helm production render | Passed: `47` manifests, exact namespace and eight digest-pinned v0.0.2 images; v0.0.2 remains superseded |
| Checkov | Passed locally: Kubernetes `1123/0/0`, Dockerfile `248/0/0`, GitHub Actions `976/0/0` |
| Python/Node dependency audit | Remediated tree passed; `setuptools` upgraded `82.0.1` to `83.0.0`; Node reported no findings at moderate+ |
| Local Trivy image scan | Containerized Trivy 0.63.0 scanned all eight locally available v0.0.2 GHCR images; zero HIGH/CRITICAL findings with unfixed findings ignored | Successor remote scan artifact remains required |
| Cosign verification attempt | Containerized cosign 2.2.4 queried the published v0.0.2 API digest and returned `no signatures found` | Successor signature and attestation verification required |
| Local runtime/health/metrics | Passed: rebuilt v0.0.3 application stack `9/9` healthy; `/metrics`, empty relay, replay, and frozen history verified |
| Waterfall standalone/rebuild replay | Passed: standalone repair gate `35/35`; standalone full suite `309 passed` with no warnings using the locked test extra; Project-AI copied replay `313 passed`; typed adapter/transport checks green |
| Waterfall-integrated API image | Passed: rebuilt `project-ai-api:waterfall-route-local` (`sha256:9f6f2125531a8fdad6293e81698ba7e1683dbb3588f6819e18acf4124d11e4bc`); imports both Waterfall integration packages, exposes the OpenAPI route, and has the owner-private path absent |
| Waterfall authenticated API surface | Passed locally: status/operation routes are machine-authenticated, V3Q-gated, audit-backed, and represented in the OpenAPI baseline |
| ADR-002 machine credentials | Passed locally: owner/MFA-protected one-time issuance, scope enforcement, revocation, audit attribution, schema version 5, and SQLite→PostgreSQL migration against disposable PostgreSQL 16; focused and integration tests passed | Production-target migration and secret evidence pending |
| Protected-route credential smoke | Passed locally: shared-token machine-write denial, scoped allow, wrong-scope denial, and revocation covered by focused tests | Target credentials and target-cluster proof pending |
| Live cluster/deployment rehearsal | Local `docker-desktop` server-side dry run is blocked by missing Prometheus Operator `PrometheusRule`/`ServiceMonitor` CRDs under production values; monitoring-disabled dry run passes. No production target deployment was attempted |
| Production machine-auth Helm mode | Passed locally: production render omits the shared API token file when durable credential enforcement is enabled; 47-manifest verifier passes |
| V3Q required-mode local tests | Passed: 28 deployment/integration/execution tests cover invalid configuration, ratification verification, and `require_approval` fail-closed behavior | Owner-signed production manifest and external proof custody pending |
| Rollback rehearsal | Not run: no approved target or known-good deployed revision |
| Local backup/restore rehearsal | Passed: backup/restore scripts round-tripped audit and SWR bundle files and rejected a non-empty restore target; production PVC/remote proof pending |
| Acceptance sign-off | Missing |

## Required approval conditions

- [ ] Commit the remediation, choose the next release version, and produce a
      new candidate only after its remote CI and security workflows are green.
- [ ] Attach current CodeQL, Checkov, Trivy, SBOM-attestation verification,
      cosign verification, and language dependency-audit outputs.
- [ ] Complete every `TBD — operator decision required` field in the change,
      deployment, monitoring, rollback, and support records.
- [ ] Prove the target context and namespace with a server-side Kubernetes dry
      run and a Helm diff or equivalent reviewed manifest delta.
- [ ] Confirm production secrets come from the approved secret manager and are
      not supplied through tracked values or command history.
- [ ] Provision one scoped machine credential per approved program through the
      owner/MFA administration surface; record only ids/scopes and secret-manager
      references, never raw tokens.
- [ ] Run the account schema migration against the approved PostgreSQL target and
      attach the migration/rollback evidence.
- [ ] Execute release-specific health, metrics, core-flow, governance denial,
      audit-chain, and alert-delivery checks in a non-production rehearsal.
- [ ] Execute and time a rollback rehearsal using a certified known-good
      revision; record data/state effects.
- [ ] Record CAB decision, change authority, implementation owner, rollback
      owner, support owner, maintenance window, and acceptance sign-off.

## CAB decision record

| Field | Value |
|---|---|
| Decision requested | Review after approval conditions are complete |
| Current disposition | More information required |
| Deployment authorized | No |
| Decision authority | TBD — explicit name/sign-off required |
| Decision date | TBD |
| Conditions/exceptions accepted | None recorded |
