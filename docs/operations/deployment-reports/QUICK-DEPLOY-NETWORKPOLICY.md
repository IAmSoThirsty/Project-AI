# Quick Deploy: NetworkPolicies

## Development (No NetworkPolicy)

```bash
helm install project-ai ./helm/project-ai \
  -f helm/project-ai/values.yaml
```

All pod-to-pod traffic allowed.

---

## Production (NetworkPolicy Enabled)

```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  -n project-ai-prod \
  --create-namespace
```

NetworkPolicies restrict traffic between pods.

---

## Verify NetworkPolicies

```bash
# List NetworkPolicies
kubectl get networkpolicies -n project-ai-prod

# Check specific policy
kubectl describe networkpolicy project-ai-prod-api -n project-ai-prod

# Test connectivity (allowed)
kubectl exec -n project-ai-prod <portal-pod> -- \
  curl http://project-ai-prod-api:8000/health/live

# Test blocked connectivity
kubectl exec -n project-ai-prod <adapter-pod> -- \
  curl http://<portal-ip>:8080/
```

---

## Network Flow

```
Allowed:
  External → Portal (ingress)
  Portal → API (service call)
  Adapter → API (service call)
  API → Any (outbound)
  Genesis reads from API

Blocked:
  Adapter → Portal
  Portal → Adapter
  External → API (direct)
  External → Adapter
  Portal → Genesis
```

---

## Troubleshoot

```bash
# No connectivity?
kubectl describe networkpolicy <name> -n project-ai-prod
kubectl get pods -n project-ai-prod --show-labels

# DNS broken?
kubectl exec <pod> -n project-ai-prod -- nslookup kubernetes.default
```

---

## Disable NetworkPolicy (Not Recommended)

```bash
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set networkPolicy.enabled=false \
  -n project-ai-prod
```
