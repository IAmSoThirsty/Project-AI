# Production Deployment Details — v0.0.3 Successor / v0.0.2 Digest Baseline

**Status:** v0.0.3 repository identity prepared; immutable image overlay and
real target details pending.

**Hostname boundary (2026-07-19):** No approved production hostname or DNS
record is present in the current repository or CAB records. The tracked
`project-ai.example.com` value is an explicit placeholder and must be replaced
by an owner-approved environment overlay before any production render or
deployment is authorized. Historical/example domains elsewhere in recovered
documentation are not approval evidence.

## Immutable release input

- Commit: `82aa1476657e16a1d38caccba38357c83380a3e3`
- Tag: `v0.0.2`
- Registry: `ghcr.io`
- Owner: `iamsothirsty`
- Chart: `helm/project-ai`
- Base values: `helm/values.prod.yaml`
- Rendered release name: proposed `project-ai`
- Rendered namespace: proposed `project-ai-prod`

The checked-in production values use owner `iamsothirsty`, tag `v0.0.2`, and
exact OCI index digests for all eight published v0.0.2 images. Those digests
are retained only as a verified baseline: they do not contain the remediation
working tree and must be replaced with successor digests before deployment.
The v0.0.3 publish workflow now creates and attaches an image-only values
overlay containing all eight resolved OCI index digests, then verifies the
merged render. The base v0.0.2 digests must never be used by changing only the
tag.

## Target record

| Field | Current value |
|---|---|
| Environment | TBD — operator decision required |
| Cloud/account/subscription | TBD |
| Cluster name | TBD |
| Kubernetes context | TBD |
| Region/zone | TBD |
| Namespace | TBD; proposed `project-ai-prod` |
| Production hostname/DNS record | TBD — owner/environment approval required |
| Helm release | TBD; proposed `project-ai` |
| Existing release/revision | TBD |
| Existing user traffic | TBD |
| Expected user impact | Unknown until existing target and routing are inspected |
| Maintenance window/timezone | TBD |
| Freeze/calendar status | TBD |

## Repository-defined workload shape

| Component | Replicas | CPU request/limit | Memory request/limit |
|---|---:|---:|---:|
| API | 2 | 200m / 1000m | 256Mi / 512Mi |
| Docs portal | 2 | 50m / 500m | 64Mi / 256Mi |
| Proof portal | 2 | 50m / 500m | 64Mi / 256Mi |
| Operator console | 2 | 100m / 500m | 128Mi / 256Mi |
| SWR | 1 | 100m / 500m | 128Mi / 256Mi |
| Atlas | 1 | 100m / 500m | 128Mi / 256Mi |
| Arbiter/RLP | 1 | 100m / 500m | 128Mi / 256Mi |
| Genesis | 1 | 50m / 500m | 32Mi / 128Mi |

Production values also enable persistence, RBAC, NetworkPolicy, PDBs,
monitoring, alerting, backup, three operational verification CronJobs, and
ingress. Local Helm verification rendered 47 manifests using the proposed
name/namespace and digest-pinned v0.0.2 baseline.

## Storage and data

- General persistence: enabled, `storageClass: standard`, 10Gi.
- Audit PVC: enabled, 5Gi at `/data`.
- Local backup schedule: `0 2 * * *`.
- Remote backup: disabled until a real rclone configuration Secret and
  destination are supplied.
- API human-state variables require a PostgreSQL database for multi-replica
  state. `secrets.api.databaseUrl` is blank in tracked values.
- Real storage class, retention, backup destination, restore test, RPO, and RTO
  are not recorded.

## Secrets and configuration

Production Helm references the existing Secret `project-ai-api-secrets`,
mounts it read-only, and supplies only `_FILE` paths to the API. Tracked values
intentionally contain no production secret values for:

- API token (development fallback only; production Helm does not mount it when
  durable credential enforcement is enabled);
- setup secret;
- MFA key;
- database URL;
- execution secret.

Per-program machine credential tokens are created through the owner/MFA API and
must be stored in each approved program's secret manager. They are not Helm
Secret keys and are never recorded in this document.

Before deployment, record the approved secret manager and synchronization
method. Do not place secret values in this document, Helm CLI flags, Git, CI
logs, or the CAB ticket. Verify only secret name, required keys, rotation date,
and access policy.

| Secret/config source | Required record |
|---|---|
| Secret manager | TBD |
| Kubernetes Secret owner/controller | TBD |
| Secret name/key mapping | TBD |
| Machine credential inventory (ids/scopes only) and client secret references | TBD |
| Rotation/expiry | TBD |
| Database endpoint and TLS policy | TBD |
| Image pull policy/credentials | TBD |
| V3Q replacement key ID/rotation date | `owner-rotation-2026-07-19-01` / `2026-07-19` |
| V3Q owner ratification record | `packages/thirstys-standard-v3q/owner-ratification.json`; independently verified |

## Local Kubernetes rehearsal evidence

The current Docker context is `desktop-linux`, but the Docker Desktop Linux
engine is not running, so a new server-side dry run cannot be performed now. A
prior local `docker-desktop` attempt with `helm/values.prod.yaml` correctly
stopped because that cluster lacked the Prometheus Operator CRDs required by
the production `ServiceMonitor` and `PrometheusRule` resources. The same render
passes when monitoring and alerting are explicitly disabled. This is useful
chart/API evidence, but it is not evidence for the eventual production
cluster; the target must provide the monitoring CRDs and external routing,
secret, and alerting configuration before rehearsal.

Production sets `THIRSTYS_V3Q_REQUIRED=true`. The API loads public verification
keys only; an optional `THIRSTYS_V3Q_REGISTRY` path may override the packaged
registry. The online runtime does not receive owner private authority and cannot
manufacture authority or approval proofs. The pre-remediation local
`owner-primary` private key entered a local Docker image because the
package directory was copied without a matching root `.dockerignore` rule.
That build path is now excluded and regression-checked. A replacement key is
now enrolled for ratification, but the affected local private file still must be
securely retired before any production use. See `V3Q_OWNER_KEY_ROTATION.md`.

The production image pull policy is `Always`. All successor application images
must also be pinned by digest; a tag alone is not an approved input.

## Network, ingress, CORS, and TLS

- Ingress is enabled with class `nginx`.
- Tracked host `project-ai.example.com` and TLS secret `project-ai-tls` are
  placeholders and must be replaced by an approved environment overlay.
- Proposed routes are `/` (operator console), `/docs`, `/proof`, and `/api`.
- The production session cookie secure flag is `true`.
- Certificate issuer is configured as `letsencrypt-prod`; cluster availability,
  DNS, certificate issuance, TLS policy, WAF/rate limiting, and external access
  restrictions are not verified.
- CORS behavior is application-defined; approved production origins and a live
  cross-origin test are not recorded.

## Required preflight evidence

- [ ] Context, namespace, existing Helm history, current images, PVCs, and
      ingress captured.
- [ ] Environment overlay reviewed with no placeholder host/secret/storage
      inputs.
- [ ] Server-side dry run and manifest diff reviewed by implementer and rollback
      owner.
- [ ] Required CRDs/operators confirmed: Prometheus Operator resources are used
      when monitoring/alerting are enabled.
- [ ] Successor image digests pinned and signature/attestations verified for
      all eight images; do not reuse the v0.0.2 baseline digests.
- [ ] PostgreSQL connectivity, schema compatibility, backup, and restore proven.
- [ ] DNS, TLS certificate, ingress controller, NetworkPolicy, and external
      connectivity tested.
- [ ] Capacity/quota accommodates requested replicas and resources.
- [ ] Blast radius, user impact, maintenance window, and freeze status approved.
- [ ] V3Q owner key rotated offline, public registry updated, exact manifest
      ratified by Jeremy / Thirsty, and external authority/approval denial paths proven.
