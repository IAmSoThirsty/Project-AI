# Formal Change Record — Project-AI v0.0.2 Remediation / Successor Release

**Change ID:** `PROJECT-AI-NEXT-PROD` (repository-local draft; replace with
the organization change-system identifier)
**Status:** Draft / local v0.0.3 successor prepared / immutable commit and
release evidence required
**Risk:** High until target, ownership, security evidence, rollback rehearsal,
and acceptance are complete

## Change objective

Produce and deploy Project-AI `v0.0.3` as the successor to `v0.0.2` from the remediated,
committed revision after remote CI/security gates pass. The successor must use
the existing `helm/project-ai` chart plus an approved production overlay that
pins all eight newly published image digests. v0.0.2 commit
`82aa1476657e16a1d38caccba38357c83380a3e3` is retained as historical release
evidence and is not the deployable candidate for this change.

## Scope

In scope:

- `project-ai-api:v0.0.3@sha256:<DIGEST>`
- `project-ai-docs-portal:v0.0.3@sha256:<DIGEST>`
- `project-ai-proof-portal:v0.0.3@sha256:<DIGEST>`
- `project-ai-operator-console:v0.0.3@sha256:<DIGEST>`
- `project-ai-swr:v0.0.3@sha256:<DIGEST>`
- `project-ai-atlas:v0.0.3@sha256:<DIGEST>`
- `project-ai-arbiter-rlp:v0.0.3@sha256:<DIGEST>`
- `project-ai-genesis:v0.0.3@sha256:<DIGEST>`
- Helm resources rendered by `helm/project-ai` with
  `helm/values.prod.yaml`
- `packages/thirstys-waterfall` provenance-preserving Project-AI rebuild and
  `packages/waterfall-adapter` governed integration boundary. The standalone
  product at `T:\\01-Projects\\Thirstys-waterfall` remains an independently
  usable release lane and is not replaced by this change.

Out of scope unless separately approved:

- merging dependency PRs #509 or #510;
- changing application behavior, governance policy, authorization semantics,
  or capability scope;
- publishing Python packages, Android artifacts, desktop installers, or the
  separate Triumvirate site;
- changing DNS, external identity providers, secret-manager policy, cluster
  infrastructure, or data-retention policy.
- changing or deploying the standalone Waterfall product independently of the
  Project-AI rebuild lane.

## Target and ownership

| Field | Required value |
|---|---|
| Environment | TBD — operator decision required |
| Kubernetes cluster/context | TBD — operator decision required |
| Namespace | TBD — proposed `project-ai-prod`; must be confirmed |
| Production hostname/DNS record | TBD — owner/environment approval required |
| Helm release name | Proposed `project-ai`; must be confirmed |
| Maintenance window | TBD — start/end/timezone required |
| Freeze/change-calendar check | TBD — evidence required |
| Change owner | TBD — named person required |
| Implementer | TBD — named person required |
| Approver/CAB authority | TBD — named person required |
| Rollback owner and backup | TBD — two named contacts required |
| Support/on-call owner | TBD — named person or rota required |

## Expected impact

- New or updated Kubernetes Deployments, Services, Secrets, PVCs, ingress,
  scheduled verification/backup resources, and monitoring resources.
- Public routes proposed by current values: `/`, `/docs`, `/proof`, and `/api`.
- Rolling pod replacement is expected. User impact cannot be declared until the
  existing target state and ingress behavior are inspected.
- Human-state repositories can initialize or migrate schemas at application
  startup. Helm rollback does not reverse data/schema changes.
- Audit and application data on PVCs persist across ordinary Helm rollback.

## Risk and controls

| Risk | Severity | Control | Current status |
|---|---:|---|---|
| v0.0.2 CI is red; successor is unreleased | Blocker | New immutable candidate with green CI/security workflows | Open |
| Wrong cluster/namespace | High | Record context; two-person preflight; server dry run | Open |
| Invalid/placeholder secrets | High | Approved secret manager; secret metadata check; no values on CLI | Open |
| Unverified schema/data effect | High | Backup, restore proof, migration inspection, rollback rehearsal | Open |
| Monitoring route not proven | High | Repository metrics/rules are locally verified; prove receiver route and test page | Open |
| Machine credential migration/provisioning incomplete | High | Run schema version 5 migration, create scoped per-program credentials through owner/MFA API, store raw tokens only in approved secret manager, and test revocation | Open |
| Rollback target not known-good | Blocker | Certify deployed revision and rehearse rollback | Open |
| Supply-chain evidence incomplete | High | Candidate `eaed9905` has verified eight-image cosign and SPDX/SLSA registry evidence; attach remaining vulnerability artifacts and target proof | Open |
| Open dependency updates | Medium | Use disposition record; audit locked v0.0.2 dependencies | Open |
| Ingress/TLS target is placeholder | Blocker | Replace `project-ai.example.com`; prove certificate and routes | Open |

## Implementation plan

Commands below are a runbook template. Replace bracketed values only after CAB
records them; do not paste secrets into command history.

1. Record the immutable inputs:

   ```powershell
   git rev-parse HEAD
   git describe --tags --exact-match HEAD
   kubectl config current-context
   kubectl get namespace <NAMESPACE>
   helm history project-ai -n <NAMESPACE>
   ```

2. Verify release and security evidence per
   `RELEASE_EVIDENCE_BUNDLE.md`. Stop on any red/missing mandatory gate.

3. Back up human state and audit state; prove the backup is readable and record
   its immutable identifier. Stop if backup or restore validation fails.

4. Prepare secrets through the approved secret manager. Inspect only secret
   names and key presence, never values.

5. With the owner/MFA session, create one scoped machine credential for each
   approved program, place each raw token directly into the approved secret
   manager, and record only credential ids, scopes, and secret references in
   the change record. Enable `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=true`
   only after the credentials are verified against the target.

6. Validate the exact render:

   ```powershell
   helm lint helm/project-ai
   helm template project-ai helm/project-ai `
     --namespace <NAMESPACE> `
     -f <APPROVED_VALUES_FILE> |
     uv run python tools/verify_helm_template.py `
       --expected-namespace <NAMESPACE> `
       --project-image-registry ghcr.io `
       --project-image-owner iamsothirsty `
       --require-project-image-digests

   helm upgrade --install project-ai helm/project-ai `
     --namespace <NAMESPACE> `
     --create-namespace `
     -f <APPROVED_VALUES_FILE> `
     --dry-run=server --debug
   ```

7. Review the manifest delta and pause for implementer + rollback-owner
   concurrence.

8. Deploy only inside the approved window:

   ```powershell
   helm upgrade --install project-ai helm/project-ai `
     --namespace <NAMESPACE> `
     --create-namespace `
     -f <APPROVED_VALUES_FILE> `
     --atomic --wait --timeout 10m --history-max 10
   ```

9. Run the validation and observation checklist. Roll back immediately when a
   trigger in `ROLLBACK_RUNBOOK.md` is met.

10. Record actual Helm revision, image digests, timestamps, observations,
   acceptance, and communications in this change record and the continuity map.

## Acceptance criteria

- Exact image digests and signatures match the approved evidence bundle.
- All workloads become Ready without crash loops or unauthorized privilege.
- `/health/live` returns 200 and reports the approved successor version.
- `/metrics` is successfully scraped and required alert expressions return
  valid series.
- Public routes and protected routes behave as documented; unauthorized access
  remains denied.
- Each approved machine program authenticates with its own scoped credential;
  the shared token is rejected when production enforcement is enabled, and a
  revocation smoke test confirms the credential cannot be reused.
- Canonical/governance denial, audit-chain, persistence, and core user-flow
  smoke checks pass.
- Alert test reaches the named receiver.
- No rollback trigger fires during the approved observation period.
- Named business/technical acceptance is recorded.

## Decision/sign-off

| Role | Name | Decision | Timestamp |
|---|---|---|---|
| Change owner | TBD | Pending | TBD |
| Implementer | TBD | Pending | TBD |
| Rollback owner | TBD | Pending | TBD |
| Support owner | TBD | Pending | TBD |
| Acceptance authority | TBD | Pending | TBD |
| CAB authority | TBD | More information required | 2026-07-19 |
