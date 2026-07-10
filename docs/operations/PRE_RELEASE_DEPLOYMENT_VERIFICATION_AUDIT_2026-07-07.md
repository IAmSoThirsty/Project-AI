# Project-AI Pre-Release Deployment Verification Audit

**Status:** formal production-gate audit complete
**Date:** 2026-07-07
**Workspace:** `T:\00-Active\Project-AI-Beginnings`
**Branch observed at audit start:** `chore/warning-cleanup-utc-artifacts`
**Target branch requested by user:** `main`
**Ship decision:** DO NOT DEPLOY to production
**Overall deployment confidence:** 62%

This audit verifies the current repository against production deployment
readiness requirements. It does not approve a deployment. Evidence below is
limited to files and commands inspected in this checkout during this session.

## 1. Executive Summary

The repository is locally buildable/testable enough for continued development
and pre-deployment rehearsal, but it is not production-ready.

The strongest verified surfaces are:

- Locked Python workspace and CI-shaped local verifier:
  `tools/verify_pre_deployment.py`.
- Compose development stack with seven hardened services in `compose.yaml`.
- Helm development chart in `helm/project-ai/`.
- GitHub Actions CI coverage for Python, Rust, Node, Android, desktop,
  Compose, Kubernetes render, and SBOM in `.github/workflows/ci.yaml`.
- Deployment/operator documentation in `docs/deployment/` and `docs/runbooks/`.

The production blockers are concrete:

- Production image registry, immutable image tags, and release automation are
  not defined.
- Kubernetes runtime secret injection is not wired into the chart; the token
  value defaults to an inline empty value in `helm/project-ai/values.yaml`.
- TLS, ingress, production persistence, backup/restore, monitoring/alerting,
  and tested real rollback are not implemented as production assets.
- Helm docs state the chart is a development baseline and not production
  hardened.
- No production deployment, release tag, GitHub Release, package publication,
  or image publication has been performed or verified.

## 2. Production Readiness Assessment

**Result:** NOT READY.

The repo contains a credible pre-deployment baseline, not a production release.
`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` explicitly lists the remaining
production gaps: image registry policy, runtime secrets through Kubernetes
Secret, TLS, ingress, persistence retention, monitoring, alerting, backup,
real rollback, production deployment, release tag, GitHub Release, package
publication, and image publication.

## 3. Deployment Readiness Assessment

**Compose:** PASS WITH WARNINGS.

Evidence:

- `compose.yaml` defines `api`, `docs-portal`, `proof-portal`, `swr`, `atlas`,
  `arbiter-rlp`, and `genesis`.
- `tools/verify_pre_deployment.py` verifies the exact service set,
  `read_only: true`, `cap_drop: [ALL]`, `no-new-privileges:true`, and
  healthchecks.

Warning:

- Compose is documented as a production-like single-host procedure, not a
  verified production environment. Real host hardening, TLS termination,
  backup, monitoring, and rollback are not proven.

**Kubernetes / Helm:** PARTIAL.

Evidence:

- `helm/project-ai/templates/` emits deployments and services.
- `templates/_helpers.tpl` includes `runAsNonRoot: true`,
  `readOnlyRootFilesystem: true`, dropped capabilities, no privilege
  escalation, and `seccompProfile: RuntimeDefault`.
- `.github/workflows/ci.yaml` renders the chart through
  `tools/verify_helm_template.py`.

Blocking gaps:

- `docs/deployment/HELM_DEPLOY.md` says the chart is a development baseline.
- No NetworkPolicy, Ingress/TLS, PersistentVolumeClaim, ServiceAccount/RBAC,
  or production secret wiring is implemented in the chart.

## 4. Missing Implementations

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| Critical | Production image publication is not implemented. | `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md`; `.github/workflows/ci.yaml` has SBOM upload but no image publish/release job. | Production deploys need immutable image references and a repeatable promotion path. | Add signed image build/publish workflow, immutable tags, registry policy, and deployment docs tied to commit SHA. |
| Critical | Kubernetes secret injection is not production-wired. | `helm/project-ai/values.yaml` uses `api.env.PROJECT_AI_API_TOKEN: ""`; `templates/api.yaml` renders the token as a direct env value. | Empty inline defaults fail closed, but real deployments need secret references without committing token material. | Add `api.bearerTokenSecret` / `secretKeyRef` support and verifier coverage. |
| High | TLS and ingress are absent. | No ingress template under `helm/project-ai/templates/`; `HELM_DEPLOY.md` lists ingress + TLS as unchecked. | Public API and portals cannot be safely exposed without TLS boundary decisions. | Add optional Ingress with TLS secret reference, hostname values, and docs. |
| High | Production persistence and backup/restore are not implemented. | `templates/api.yaml` uses `emptyDir: {}` for `audit-data`; `PRE_DEPLOYMENT_CHECKLIST.md` lists retention, backup, and real rollback as remaining. | Audit continuity is a core governance requirement and cannot rely on ephemeral storage. | Add PVC support, retention policy, backup command, restore test, and rollback proof. |
| High | Monitoring/alerting is not implemented. | `PRE_DEPLOYMENT_CHECKLIST.md` lists monitoring and alerting as remaining; no dashboard/alert manifests found in Helm templates. | Operators cannot detect failure, saturation, or governance-denial anomalies in production. | Add metrics endpoint contract, scrape config, alert rules, and SLO dashboard docs. |
| Medium | Kustomize, Terraform, Ansible, Pulumi, systemd, Windows Services, canary, and blue/green deployment are not present. | No matching primary deployment assets inspected in repo root; deployment docs cover Compose and Helm only. | Not all requested deployment mechanisms exist. | Either implement intentionally or document them as out of scope for this release gate. |

## 5. Broken Implementations

No broken implementation was confirmed in the focused checks executed this
session. Current verified gates passed for the pre-deployment verifier and the
targeted regression set listed in section 18.

## 6. Configuration Problems

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| High | Helm values are development defaults. | `helm/project-ai/values.yaml` starts with "Development values - not for production use." | A production release cannot be driven by development image names and empty token defaults. | Add `values.production.yaml` with explicit registry, pull policy, secrets, persistence, ingress, and resource settings. |
| Medium | Generated Alien Invaders artifacts can reappear as untracked repo noise. | `engines/alien_invaders/artifacts/` regenerated after prior commit `76a86c84` removed it. | Dirty generated output hides real worktree state. | Ignore generated runtime artifacts and keep regression data under tracked test fixtures. |

## 7. CI/CD Problems

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| High | CI validates but does not release. | `.github/workflows/ci.yaml` has test/build/render/SBOM jobs, no release or deployment job. | Passing CI is not a deployable artifact pipeline. | Add release workflow gated by tags or manual approval. |
| Medium | GitHub remote default branch reports `master`, while current repo/user flow targets `main`. | `gh repo view --json defaultBranchRef` returned `master`; local `main` tracks `origin/main`. | Branch mismatch can route PRs/checks/release automation to the wrong base. | Align remote default branch with the intended trunk or document the deliberate split. |

## 8. Infrastructure Problems

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| High | No production Kubernetes network isolation. | `helm/project-ai/templates/` has deployments/services only; no NetworkPolicy. | Services remain broader than necessary inside a cluster. | Add least-privilege NetworkPolicies. |
| High | No production RBAC model for Kubernetes. | No ServiceAccount/Role/RoleBinding templates inspected. | Runtime identity and audit writer permissions are not constrained. | Add explicit ServiceAccounts and RBAC. |
| Medium | No PodDisruptionBudget. | No PDB template inspected; `HELM_DEPLOY.md` lists it as unchecked for genesis. | Rolling maintenance can drop singleton services unexpectedly. | Add PDBs where availability requires them. |

## 9. Security Findings

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| High | Runtime secrets are documented but not chart-wired. | `ENVIRONMENT_VARIABLES.md` requires secret manager/K8s Secret; chart renders inline env value. | Docs and implementation diverge at the production security boundary. | Implement secretKeyRef and update verifier/tests. |
| Medium | Image signing is not implemented. | No signing workflow or cosign policy found in inspected CI workflow. | Supply-chain provenance is incomplete for production. | Add image signing and verification policy. |
| Medium | DAST is not implemented. | CI has SAST-like lint/pre-commit and tests, but no running app dynamic scan job. | Runtime-exposed routes are not dynamically probed in CI. | Add bounded DAST against Compose preview or staging. |

## 10. Observability Findings

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| High | Metrics, tracing, dashboards, and alert rules are not production-wired. | `PRE_DEPLOYMENT_CHECKLIST.md` lists monitoring and alerting as remaining; no Helm observability manifests inspected. | Operators cannot prove runtime health beyond healthchecks. | Add metrics contract, dashboard, alert rules, and incident thresholds. |
| Medium | Healthchecks exist but do not replace observability. | Compose and Helm define health/readiness probes. | Liveness is necessary, not sufficient for production operations. | Keep probes and add metrics/tracing/log retention. |

## 11. Documentation Mismatches

| Severity | Finding | Evidence | Why it matters | Recommended fix |
|---|---|---|---|---|
| High | Production deploy docs describe procedures that are not fully backed by production assets. | `PRODUCTION_DEPLOY.md` gives production-like Compose steps; `PRE_DEPLOYMENT_CHECKLIST.md` still says production gaps remain. | Operators could confuse rehearsal instructions with release approval. | Keep the warning language and add explicit "rehearsal only" labeling where needed. |
| Medium | Helm install docs contain a likely secret name mismatch. | `HELM_DEPLOY.md` creates `project-ai-api-token` but sample install sets `api.bearerTokenSecret=project-ai-token`. | Copy/paste install can fail once secret wiring is implemented. | Correct the name when adding secretKeyRef support. |

## 12. Governance Verification

**Result:** PARTIAL.

Evidence:

- `packages/execution/src/execution/gate.py` and tests enforce non-ALLOW
  denial paths.
- `packages/capability/`, `packages/audit/`, `packages/canonical/`, and
  `packages/rlp/` provide code-backed governance primitives.
- `tools/canonical_replay.py` and `tools/verify_frozen_history.py` provide
  replay/frozen-history verification paths.

Limit:

- Production deployment authorization, immutable release provenance, and
  production runtime audit persistence are not fully implemented.

## 13. Deployment Risks

| Severity | Risk | Impact | Action |
|---|---|---|---|
| Critical | Deploying now would use development/default infrastructure assumptions. | False production confidence and weak operational recovery. | Do not deploy until production values, secrets, persistence, TLS, and monitoring are implemented and verified. |
| High | Empty or missing API token fails protected surfaces closed. | Protected API paths return 503; deployment smoke fails. | Keep fail-closed behavior; wire real secrets before release. |
| High | Ephemeral Kubernetes audit storage loses records on pod restart. | Governance audit continuity can be lost. | Add PVC and backup/restore validation. |

## 14. Required Actions Before Release

1. Align remote default branch policy with the intended `main` trunk or document
   why GitHub default remains `master`.
2. Add production image build/publish workflow with immutable tags and SBOM
   attachment.
3. Add image signing and verification.
4. Add Helm production values with registry, immutable tags, secret references,
   ingress/TLS, persistence, resource requests/limits, NetworkPolicies, RBAC,
   and PodDisruptionBudgets.
5. Add production secret injection through Kubernetes Secret references.
6. Add audit PVC, backup, restore, and rollback verification.
7. Add monitoring, metrics, dashboards, alert rules, and incident thresholds.
8. Add deployment smoke and rollback tests.
9. Rerun full CI on the exact release commit.
10. Only then create a release tag or production deployment approval.

## 15. Optional Improvements

- Add Kustomize overlays only if an operator actually needs them.
- Add Terraform/Pulumi/Ansible only after the target infrastructure is named.
- Add blue/green or canary rollout only after ingress, service routing, and
  health metrics are implemented.

## 16. Scorecard

| Category | Score |
|---|---|
| Implementation | PASS WITH WARNINGS |
| Verification | PASS WITH WARNINGS |
| Completeness | PARTIAL |
| Reliability | PARTIAL |
| Operational Readiness | PARTIAL |
| Deployment Readiness | PARTIAL |
| Security | PARTIAL |
| Maintainability | PASS WITH WARNINGS |
| Documentation | PASS WITH WARNINGS |
| Observability | FAIL |

## 17. Ship Decision

DO NOT DEPLOY to production.

The safe next state is: land the current branch and audit artifacts on `main`,
push them to GitHub, keep the production gate closed, and use the required
actions above as the next release-hardening backlog.

## 18. Verification Executed In This Session

```powershell
git rev-parse --show-toplevel
git branch --show-current
git status --short
git remote -v
gh --version
gh auth status
gh repo view --json nameWithOwner,defaultBranchRef,url
git fetch origin --prune
git log --oneline --decorate main..HEAD
git diff --stat main..HEAD
git diff --check
git check-ignore -v engines\alien_invaders\artifacts\raw_data.json
uv run python tools/verify_pre_deployment.py
uv run python -m pytest tools/tests/test_verify_pre_deployment.py packages/alien-invaders/tests/test_fixtures_regression.py packages/simulation-contract/tests/test_simulation_contract.py packages/canonical/tests/test_governed_action.py packages/identity/tests/test_identity_registry.py packages/thirstys-trading-hub/tests/test_core_integration.py packages/tarl/tests/test_tarl_os.py -q --tb=short
```

Executed results:

- `tools/verify_pre_deployment.py`: passed.
- Targeted regression set: `62 passed`.
- `git diff --check`: passed.
- Generated Alien Invaders artifacts are now ignored by `.gitignore`.

Not yet executed in this session:

- Full pytest suite.
- CI-shaped MyPy.
- Ruff check/format.
- Rust, Node, Android, Docker Compose runtime, and Helm runtime validation.
