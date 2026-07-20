# Rollback Runbook — Project-AI Successor to v0.0.2

**Status:** Procedure defined; target, owner, known-good revision, timing, and
rehearsal evidence pending.
**Primary strategy:** Helm revision rollback.
**Do not use:** `git checkout` + rebuild as the first production recovery path;
it is slower and does not restore the exact previously deployed image digests.

## Required before deployment

Record all values in the change record:

| Item | Required value |
|---|---|
| Cluster/context | TBD |
| Namespace | TBD |
| Helm release | Proposed `project-ai` |
| New revision | Assigned by Helm during deployment |
| Previous Helm revision | TBD from `helm history` |
| Previous image tag | TBD from actual pre-change deployment; `v0.0.1` is not certified known-good |
| Previous commit | TBD from actual pre-change deployment |
| Previous image digests | TBD — record from live workloads/registry |
| Backup identifier + restore proof | TBD |
| Rollback owner / backup | TBD / TBD |
| Rehearsed duration | TBD |

`v0.0.1` is merely the previous published release. It must not be called
known-good until its exact digests have been deployed and accepted in the target
environment or another revision is explicitly certified.

## Rollback triggers

Initiate rollback when any one of these occurs and cannot be corrected safely
inside five minutes without changing the approved scope:

- Helm `--atomic` fails or any required workload is not Ready by the 10-minute
  deployment timeout;
- API `/health/live` is non-200 for two consecutive checks one minute apart;
- protected routes accept missing/invalid credentials, or expected governance
  denial/fail-closed tests fail once;
- audit writes fail, chain verification fails, or persistence is not mounted as
  approved;
- 5xx responses exceed 5% for five minutes, p99 latency exceeds one second for
  five minutes, or an API pod is non-running for five minutes, after confirming
  the corresponding metrics are real;
- unplanned data mutation, secret exposure, privilege expansion, or ingress/TLS
  failure is observed;
- the change owner, rollback owner, or incident commander directs rollback.

## Procedure

1. Declare rollback in the incident/change channel and record the timestamp,
   trigger, current revision, and operator.

2. Preserve evidence without exposing secrets:

   ```powershell
   kubectl config current-context
   helm status project-ai -n <NAMESPACE>
   helm history project-ai -n <NAMESPACE>
   kubectl get pods,deployments,services,ingress,pvc -n <NAMESPACE> -o wide
   kubectl logs -n <NAMESPACE> -l app.kubernetes.io/instance=project-ai --tail=200
   ```

3. Confirm the target revision from the pre-change record. Do not guess from
   revision order during an incident.

4. Roll back:

   ```powershell
   helm rollback project-ai <PREVIOUS_REVISION> `
     --namespace <NAMESPACE> `
     --wait --timeout 10m --cleanup-on-fail
   ```

5. Verify the restored images and workload state:

   ```powershell
   helm status project-ai -n <NAMESPACE>
   kubectl rollout status deployment/project-ai-api -n <NAMESPACE> --timeout=5m
   kubectl get pods -n <NAMESPACE>
   kubectl get pods -n <NAMESPACE> `
     -o jsonpath="{range .items[*]}{.metadata.name}{' '}{range .status.containerStatuses[*]}{.imageID}{' '}{end}{'`n'}{end}"
   ```

6. Port-forward or use the approved internal probe path, then verify:

   ```powershell
   kubectl port-forward -n <NAMESPACE> svc/project-ai-api 8001:8000
   curl.exe --fail --silent --show-error http://127.0.0.1:8001/health/live
   curl.exe --fail --silent --show-error http://127.0.0.1:8001/metrics
   ```

7. Run release-independent governance and audit checks from the approved
   operator checkout:

   ```powershell
   uv run python tools/canonical_replay.py
   uv run python tools/verify_frozen_history.py
   ```

8. Confirm audit-chain continuity and application data readability. If schema or
   data created by the successor release is incompatible with the restored application, stop
   traffic and invoke the separately rehearsed data-restore procedure. Helm
   rollback alone does not reverse database or PVC state.

9. Observe for the approved rollback observation period (TBD; proposed minimum
   30 minutes), then record outcome and obtain incident/change-owner sign-off.

## Data and state impact

- Helm rollback restores Kubernetes manifests from an earlier Helm revision.
- PVC contents are retained and are not versioned by Helm.
- Account/workflow repositories perform schema checks or migrations during
  initialization. Backward compatibility with a prior image has not been
  proven against a production database.
- Audit state must remain append-only; never delete or truncate the audit PVC as
  part of rollback.
- The current backup CronJob has not been proven against a real remote target;
  a CAB-approved backup and restore rehearsal is mandatory.

## Rehearsal record

| Field | Value |
|---|---|
| Environment | Not run |
| From revision/tag | Not run |
| To revision/tag | Not run |
| Trigger exercised | Not run |
| Start/end/duration | Not run |
| Data validation | Not run |
| Audit continuity | Not run |
| Owner acceptance | Missing |
