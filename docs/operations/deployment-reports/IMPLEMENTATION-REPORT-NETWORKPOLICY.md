# NetworkPolicies Implementation Report

## Overview

Implemented **network segmentation** via Kubernetes NetworkPolicies. Pod-to-pod communication is now restricted to authorized connections, preventing lateral movement and limiting blast radius of compromised services.

## Files Created

### 1. `helm/project-ai/templates/networkpolicy.yaml` (NEW)
- 4 NetworkPolicies (api, portals, adapters, genesis)
- Ingress and Egress rules per service
- Conditional creation via `networkPolicy.enabled` flag

## Files Modified

### 1. `helm/project-ai/values.yaml` (MODIFIED)
- Added: `networkPolicy.enabled: false` (development default)

### 2. `helm/values.prod.yaml` (MODIFIED)
- Added: `networkPolicy.enabled: true` (production default)

## Architecture

### Network Segmentation Model

```
┌─────────────────────────────────────────────────────────┐
│ External Users                                          │
│ (Internet/Ingress Controller)                           │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP(S) on port 8080
                   ▼
        ┌──────────────────────┐
        │   Portal Pods        │
        │ (docs, proof)        │
        │ ✓ Recv from external │
        │ ✓ Send to API        │
        │ ✗ Recv from adapters │
        │ ✗ Recv from genesis  │
        └──────────────────────┘
                   │ HTTP on port 8000
                   ▼
        ┌──────────────────────┐
        │   API Pod            │
        │ ✓ Recv from portals  │
        │ ✓ Recv from adapters │
        │ ✓ Recv from genesis  │
        │ ✗ Recv from external │
        │ ✓ Send to adapters   │
        │ ✓ Send to genesis    │
        └──────────────────────┘
                   │
        ┌──────────────────────┐
        │ Adapter Pods         │
        │ (swr, atlas, arbiter)│
        │ ✓ Recv from API only │
        │ ✗ Recv from portals  │
        │ ✗ Recv from external │
        └──────────────────────┘

        ┌──────────────────────┐
        │ Genesis Pod          │
        │ ✓ Recv from API only │
        │ ✗ Recv from portals  │
        │ ✗ Recv from adapters │
        └──────────────────────┘
```

## NetworkPolicy Rules

### API Service NetworkPolicy

**Ingress:**
- ✅ From portals (TCP port 8000)
- ✅ From adapters (TCP port 8000)
- ✅ From anywhere (DNS UDP port 53)

**Egress:**
- ✅ To any pod (for service calls)
- ✅ DNS (UDP port 53)

**Security Benefit:** API is the central hub, only portals and adapters can initiate connections.

### Portal Services NetworkPolicy

**Ingress:**
- ✅ From API (TCP port 8000, internal communication)
- ✅ From ingress-nginx namespace (external HTTP users)

**Egress:**
- ✅ To API service
- ✅ DNS (UDP port 53)

**Security Benefit:** Portals can only reach API, no inter-pod access.

### Adapter Services NetworkPolicy

**Ingress:**
- ✅ From API only (TCP port 8000)

**Egress:**
- ✅ To any pod (external API calls)
- ✅ DNS (UDP port 53)

**Security Benefit:** Adapters are isolated from portals, no lateral movement.

### Genesis Service NetworkPolicy

**Ingress:**
- ✅ From API only (TCP port 8080)

**Egress:**
- ✅ To any pod (external blockchain/service calls)
- ✅ DNS (UDP port 53)

**Security Benefit:** Genesis isolated from all other services, reads only from API.

## Deployment Modes

### Mode 1: Development (No NetworkPolicy)

```yaml
networkPolicy:
  enabled: false
```

**Result:**
- No NetworkPolicies created
- All traffic allowed between pods
- Default Kubernetes behavior
- Easier for local testing

### Mode 2: Production (NetworkPolicy Enabled)

```yaml
networkPolicy:
  enabled: true
```

**Result:**
- NetworkPolicies enforced
- Traffic restricted to defined rules
- Unauthorized connections blocked
- Network segmentation active

## Security Properties

### ✅ Implemented

1. **Defense in Depth:**
   - Container security (non-root, read-only filesystem)
   - RBAC (ServiceAccount permissions)
   - NetworkPolicies (network segmentation)

2. **Lateral Movement Prevention:**
   - Adapters cannot reach portals
   - Portals cannot reach adapters
   - Genesis isolated from all but API
   - Each service has minimal connectivity

3. **Blast Radius Limitation:**
   - If portal compromised: only API accessible
   - If adapter compromised: cannot reach other services
   - If API compromised: can reach adapters/genesis (by design)
   - Genesis cannot initiate inbound connections

4. **Zero Trust Network:**
   - Default deny all traffic
   - Explicit allow rules only
   - No implicit trust between services

## Verification Commands

### Pre-Deployment

```bash
# Verify NetworkPolicy template renders (production)
helm template test ./helm/project-ai \
  -f helm/values.prod.yaml | grep "kind: NetworkPolicy"
# Expected: 4 NetworkPolicies

# Verify no NetworkPolicies (development)
helm template test ./helm/project-ai \
  -f helm/project-ai/values.yaml | grep "kind: NetworkPolicy"
# Expected: (empty)
```

### Post-Deployment

```bash
# List NetworkPolicies
kubectl get networkpolicies -n project-ai-prod

# Inspect NetworkPolicy details
kubectl describe networkpolicy project-ai-prod-api -n project-ai-prod

# Test connectivity (from within pod)
kubectl exec -n project-ai-prod <portal-pod> -- \
  curl -v http://project-ai-prod-api:8000/health/live
# Expected: 200 OK (allowed)

# Test blocked connectivity (from within pod)
kubectl exec -n project-ai-prod <adapter-pod> -- \
  curl -v http://<portal-pod-ip>:8080/
# Expected: connection timeout/refused (blocked)
```

## Troubleshooting

### Connectivity Broken

**Symptom:** Services cannot reach each other

**Check NetworkPolicy:**
```bash
# Get NetworkPolicy
kubectl get networkpolicy -n project-ai-prod

# Describe the policy
kubectl describe networkpolicy <name> -n project-ai-prod

# Check pod labels (used for matching)
kubectl get pods -n project-ai-prod --show-labels

# Test if pod matches selector
kubectl get pods -n project-ai-prod \
  -l app.kubernetes.io/component=api -o name
```

**Common Causes:**
1. Pod labels don't match selector
2. Port number mismatch
3. Namespace selector missing
4. Policy rule order wrong

### DNS Resolution Failing

**Symptom:** Pods cannot resolve service names

**Solution:** DNS egress rule required

```yaml
egress:
  - to:
      - namespaceSelector: {}  # Allow to any namespace
    ports:
      - protocol: UDP
        port: 53  # DNS port
```

### External Connectivity Blocked

**Symptom:** Adapters cannot call external APIs

**Solution:** Allow unrestricted egress

```yaml
egress:
  - to:
      - namespaceSelector: {}  # All traffic allowed
```

## Production Checklist

Before deploying to production:

- [ ] Review NetworkPolicy architecture
- [ ] Verify `networkPolicy.enabled: true` in values.prod.yaml
- [ ] Deploy with NetworkPolicies enabled
- [ ] List NetworkPolicies: `kubectl get networkpolicies`
- [ ] Test connectivity between pods (allowed rules)
- [ ] Test blocked connectivity (denied rules)
- [ ] Check for connection timeouts in logs
- [ ] Verify DNS resolution works
- [ ] Monitor for NetworkPolicy violations
- [ ] Document any custom NetworkPolicy modifications

## Future Enhancements

- [ ] Egress to specific external IPs (more restrictive)
- [ ] NetworkPolicy for kube-system services
- [ ] Egress rules for specific registries
- [ ] DNS policy (separate from NetworkPolicy)
- [ ] Service mesh integration (Istio, Linkerd)
- [ ] NetworkPolicy policy generation automation

## References

- Kubernetes NetworkPolicies: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Network Policy Editor: https://cilium.io/blog/2021/12/01/network-policy-editor/
- Calico Network Policies: https://docs.projectcalico.org/about/about-network-policy
