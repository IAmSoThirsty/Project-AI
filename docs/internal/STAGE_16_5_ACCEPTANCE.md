# Stage 16.5 Kubernetes Acceptance

**Status:** accepted

## Deliverable

`helm/project-ai/` — Helm chart for the seven-service development stack.
Client-side manifest validation passes without a running cluster.

## Chart Structure

```
helm/project-ai/
  Chart.yaml          — chart metadata (name, version, appVersion)
  values.yaml         — per-service image, port, and resource defaults
  templates/
    _helpers.tpl      — shared labels, security contexts, tmp volume helpers
    api.yaml          — API gateway Deployment + Service
    portals.yaml      — docs-portal and proof-portal Deployments + Services
    adapters.yaml     — swr, atlas, arbiter-rlp Deployments + Services
    genesis.yaml      — genesis emitter Deployment + Service
```

## Security Properties (all containers)

- `readOnlyRootFilesystem: true`
- `allowPrivilegeEscalation: false`
- `capabilities.drop: [ALL]`
- `runAsNonRoot: true`
- `seccompProfile.type: RuntimeDefault`
- `/tmp` mounted as `emptyDir` (sizeLimit: 64Mi) — only writable surface

## Evidence

### Helm lint

```
$ helm lint helm/project-ai
==> Linting helm/project-ai
[INFO] Chart.yaml: icon is recommended
1 chart(s) linted, 0 chart(s) failed
```

INFO-level advisory (no icon) — not a failure; icon is optional for development charts.

### Client-side manifest validation

```
$ helm template project-ai-dev helm/project-ai | kubectl apply --dry-run=client -f -
service/project-ai-dev-swr created (dry run)
service/project-ai-dev-atlas created (dry run)
service/project-ai-dev-arbiter-rlp created (dry run)
service/project-ai-dev-api created (dry run)
service/project-ai-dev-genesis created (dry run)
service/project-ai-dev-docs-portal created (dry run)
service/project-ai-dev-proof-portal created (dry run)
deployment.apps/project-ai-dev-swr created (dry run)
deployment.apps/project-ai-dev-atlas created (dry run)
deployment.apps/project-ai-dev-arbiter-rlp created (dry run)
deployment.apps/project-ai-dev-api created (dry run)
deployment.apps/project-ai-dev-genesis created (dry run)
deployment.apps/project-ai-dev-docs-portal created (dry run)
deployment.apps/project-ai-dev-proof-portal created (dry run)
```

14 resources validated (7 Deployments + 7 Services). No server required.
