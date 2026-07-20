# Helm Deployment

> **Status:** The chart is locally hardened and statically verified. v0.0.2 is
> superseded; no deployment is authorized until a successor has green remote
> CI/security evidence and an approved target overlay.

The chart renders eight application workloads, persistent audit/backup
storage, RBAC, Pod Security settings, NetworkPolicies, PDBs, ingress,
digest-pinned images, external-monitoring integration, and operational
verification CronJobs. It deliberately does not install a monitoring stack or
create production secret values.

## Production procedure

1. Copy `helm/values.prod.yaml` to an environment-controlled overlay. Replace
   the v0.0.2 baseline tag/digests, placeholder host/TLS/storage inputs, and
   selector labels with the approved successor and target values.
2. Provision `project-ai-api-secrets` through the approved secret manager with
   keys `PROJECT_AI_DATABASE_URL`, `PROJECT_AI_SETUP_SECRET`,
   `PROJECT_AI_MFA_KEY`, and `PROJECT_AI_EXECUTION_SECRET`. The production
   values set `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=true`, so the shared
   `PROJECT_AI_API_TOKEN` bootstrap file is intentionally not mounted. If a
   development overlay uses the shared fallback, add that key and set the
   enforcement flag to `false`. Helm mounts this Secret read-only; do not put
   values in Git or CLI flags.
3. Verify the exact render:

   ```powershell
   helm lint helm/project-ai -f <APPROVED_VALUES_FILE>
   helm template project-ai helm/project-ai `
     --namespace <NAMESPACE> `
     -f <APPROVED_VALUES_FILE> |
     uv run python tools/verify_helm_template.py `
       --expected-namespace <NAMESPACE> `
       --project-image-registry ghcr.io `
       --project-image-owner iamsothirsty `
       --require-project-image-digests
   ```

4. Capture current context, Helm history, PVCs, image IDs, and ingress. Run a
   server-side dry run and review the manifest delta with the implementer and
   rollback owner.
5. Deploy only inside the approved window:

   ```powershell
   helm upgrade --install project-ai helm/project-ai `
     --namespace <NAMESPACE> `
     --create-namespace `
     -f <APPROVED_VALUES_FILE> `
     --atomic --wait --timeout 10m --history-max 10
   ```

6. With the owner/MFA session, provision one scoped machine credential per
   approved program and place each raw token in that program's approved secret
   manager. Record only credential ids/scopes; never put raw tokens in Helm
   values or release metadata.

7. Verify Ready workloads, exact image IDs, `/health/live`, `/metrics`, public
   and protected routes, audit integrity, canonical replay, frozen history,
   persistence, dashboards, alerts, backup, and the approved observation
   period. Use `docs/operations/cab/ROLLBACK_RUNBOOK.md` for rollback.

The target cluster, namespace, DNS/TLS, secret manager, external monitoring
stack, paging routes, remote backup, owners, maintenance window, and
known-good rollback revision remain mandatory operator inputs.
