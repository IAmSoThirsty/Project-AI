# Helm Deployment

> **Scope:** deploying the Project-AI development stack to a Kubernetes
> cluster via the `helm/project-ai` chart. For single-host Compose, see
> `PRODUCTION_DEPLOY.md`.

**The chart is currently a development baseline.** It renders manifests
client-side for validation (per `docs/operator.md`) but is not
production-hardened. Before using it in a real cluster, audit:

- [ ] Resource requests + limits per container
- [ ] NetworkPolicies (the chart does not currently emit them)
- [ ] PodSecurityStandards (the chart uses `runAsNonRoot: true` but does
      not pin a `seccompProfile`)
- [ ] ServiceAccount + RBAC for the audit writer
- [ ] PersistentVolume for the audit log
- [ ] Ingress + TLS for the public API
- [ ] PodDisruptionBudget for the genesis emitter

This document covers the basic install + verify; the security hardening
is the operator's responsibility.

---

## 0. Pre-flight

```bash
# Tools required
helm version          # >= 4
kubectl version       # matches the target cluster

# Repo is on the expected commit
cd T:/00-Active/Project-AI-Beginnings
git status --short
git rev-parse HEAD
```

---

## 1. Render the chart (client-side validation)

```bash
helm lint helm/project-ai
helm template project-ai-dev helm/project-ai \
    --set api.bearerTokenSecret=project-ai-api-token \
    > /tmp/rendered.yaml

# Validate via the project's verifier
cat /tmp/rendered.yaml | uv run python tools/verify_helm_template.py
```

If `verify_helm_template.py` fails, the chart is not in a valid state
for this commit. Fix the chart before proceeding.

---

## 2. Create the namespace + secrets

```bash
# Namespace
kubectl create namespace project-ai-dev

# API bearer token (64-char hex)
kubectl -n project-ai-dev create secret generic project-ai-api-token \
    --from-literal=token=$(openssl rand -hex 32)
```

---

## 3. Install the chart

```bash
helm install project-ai-dev helm/project-ai \
    --namespace project-ai-dev \
    --set api.bearerTokenSecret=project-ai-token \
    --set audit.persistence.size=10Gi
```

(Adjust the values to match the chart's `values.yaml` schema. The
chart is currently a single-file template; the `values.yaml` may
be minimal.)

---

## 4. Verify the install

```bash
# Pods are running
kubectl -n project-ai-dev get pods
# Expected: 7 pods, all Running, all Ready

# Services are exposed
kubectl -n project-ai-dev get svc
# Expected: 1 LoadBalancer/ClusterIP for api; internal ClusterIPs for the rest

# Liveness
kubectl -n project-ai-dev port-forward svc/api 8000:8000 &
curl -sS http://127.0.0.1:8000/health/live
# Expected: {"status":"live","version":"0.0.0.dev0"}

# Audit relay (read with the bearer token)
export $(kubectl -n project-ai-dev get secret project-ai-api-token \
    -o jsonpath='{.data.token}' | base64 -d | xargs)
curl -sS -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     "http://127.0.0.1:8000/audit?limit=5" | python -m json.tool
```

---

## 5. Smoke test from inside the cluster

```bash
# Run a sample verdict relay from a debug pod
kubectl -n project-ai-dev run curl-debug --rm -it --image=curlimages/curl -- sh

# Inside the pod
curl -sS http://api.project-ai-dev.svc.cluster.local:8000/health/live
curl -sS -X POST \
     -H "Authorization: Bearer $(cat /etc/secret/token)" \
     -H "Content-Type: application/json" \
     -d '{"action_id":"k8s-smoke-001","verdict":"ALLOW","source":"k8s-smoke"}' \
     http://api.project-ai-dev.svc.cluster.local:8000/chimera/verdict
```

---

## 6. Uninstall

```bash
helm uninstall project-ai-dev --namespace project-ai-dev
kubectl delete namespace project-ai-dev
```

The audit log persists only if the chart created a PersistentVolume;
check the chart's persistence configuration before uninstalling.

---

## 7. Source of truth

- `helm/project-ai/` — the chart source
- `tools/verify_helm_template.py` — client-side render validator
- `docs/deployment/PRODUCTION_DEPLOY.md` — the Compose-based
  alternative
- `docs/architecture.md` §"Container Stack" — the 7-service map
