# Pod Disruption Budgets Implementation Report

## Overview

Implemented **availability guarantees** via Kubernetes PodDisruptionBudgets (PDBs). Services can tolerate controlled disruptions during cluster maintenance while maintaining service availability.

## Files Created

### 1. `helm/project-ai/templates/poddisruptionbudget.yaml` (NEW)
- 4 PodDisruptionBudgets (api, portals, adapters, genesis)
- minAvailable policies for multi-replica services
- maxUnavailable policies for single-replica services
- Conditional creation via `podDisruptionBudgets.enabled` flag

## Files Modified

### 1. `helm/project-ai/values.yaml` (MODIFIED)
- Added: `podDisruptionBudgets.enabled: false` (dev default)

### 2. `helm/values.prod.yaml` (VERIFIED)
- Already contains pdb config per service

## Architecture

### PDB Strategy

```
Service         Replicas  Policy              Tolerance
─────────────────────────────────────────────────────────
API             2         minAvailable: 1     Allow 1 disruption
Portals         2         minAvailable: 1     Allow 1 disruption
Adapters        1         maxUnavailable: 0   No disruptions
Genesis         1         maxUnavailable: 0   No disruptions
─────────────────────────────────────────────────────────
```

### Availability Guarantees

| Service | Replicas | minAvailable | Guarantee |
|---------|----------|--------------|-----------|
| API | 2 | 1 | At least 1 always running |
| Portals | 2 | 1 | At least 1 always running |
| Adapters | 1 | N/A | Single replica, no tolerance |
| Genesis | 1 | N/A | Single replica, no tolerance |

## PDB Policies Explained

### minAvailable: 1 (API, Portals)

```yaml
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: project-ai-api
```

**Meaning:** At least 1 pod must remain available at all times

**Behavior:**
- 2 replicas deployed
- During disruption: evicts 1 pod only, keeps 1 running
- If 1 pod down naturally: won't evict the other
- Kubernetes respects this guarantee

**Use Case:** Critical services that need continuous availability

### maxUnavailable: 0 (Adapters, Genesis)

```yaml
spec:
  maxUnavailable: 0
  selector:
    matchLabels:
      app: project-ai-adapters
```

**Meaning:** No pods can be evicted (0 unavailable allowed)

**Behavior:**
- Single replica deployed
- During disruption: pods NOT evicted by Kubernetes
- Only manual deletion/drain can move pod
- Protects against cascading failures

**Use Case:** Single-replica services that need protection

## Disruption Scenarios

### Scenario 1: Node Drain (Planned)

```bash
# Admin drains node for maintenance
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# Kubernetes checks PDBs before evicting
# API pod: evicted (1 remains on other node)
# Portal pod: evicted (1 remains on other node)
# Adapter pod: NOT evicted (violates PDB)
# Genesis pod: NOT evicted (violates PDB)

# If adapter/genesis must move:
# kubectl drain --disable-eviction  (force eviction, ignore PDB)
```

### Scenario 2: Node Failure (Unplanned)

```
Node fails → kubelet stops reporting → pod marked NotReady
PDB doesn't prevent automatic rescheduling

API: 1 pod on failed node → 1 pod on other node → service continues
Adapters: 1 pod on failed node → pod rescheduled → brief outage
```

### Scenario 3: Cluster Autoscaling

```bash
# Cluster scales down (removes nodes)
# Kubernetes respects PDBs during scale-down

API: 1 evicted, 1 remains
Portals: 1 evicted, 1 remains
Adapters: 0 evicted (PDB protects)
Genesis: 0 evicted (PDB protects)
```

## Configuration

### Production Best Practices

```yaml
# Critical services (multi-replica)
api:
  replicas: 2
  pdb:
    minAvailable: 1  # Allow 1 disruption

# Non-critical services (single-replica)
adapters:
  replicas: 1
  pdb:
    # Use maxUnavailable: 0 to prevent eviction
    # OR omit PDB entirely
```

### High Availability (Future)

```yaml
# To scale to 3 replicas for HA
api:
  replicas: 3
  pdb:
    minAvailable: 2  # Allow 1 disruption out of 3
```

## Verification Commands

### Pre-Deployment

```bash
# Verify PDB template renders (production)
helm template test ./helm/project-ai \
  -f helm/values.prod.yaml | grep "kind: PodDisruptionBudget"
# Expected: 4 PDBs

# Verify no PDBs (development)
helm template test ./helm/project-ai \
  -f helm/project-ai/values.yaml | grep "kind: PodDisruptionBudget"
# Expected: (empty)
```

### Post-Deployment

```bash
# List PDBs
kubectl get poddisruptionbudgets -n project-ai-prod

# Check PDB details
kubectl describe pdb project-ai-prod-api -n project-ai-prod

# Check disruptions allowed
kubectl get pdb -n project-ai-prod -o wide

# Simulate drain (dry-run)
kubectl drain node-x --dry-run=client --ignore-daemonsets
```

### Testing Eviction

```bash
# Check if pod can be evicted (respects PDB)
kubectl evict pod <pod-name> -n project-ai-prod --dry-run=client

# Force eviction (ignore PDB - DANGEROUS)
kubectl evict pod <pod-name> -n project-ai-prod --force
```

## Limitations

### Single-Replica Services

Adapters and Genesis are single-replica, cannot provide high availability via PDB alone.

**Options:**
1. Scale to 2+ replicas + minAvailable PDB
2. Use maxUnavailable: 0 to prevent disruptions
3. Accept brief outages during maintenance

### Voluntary vs Involuntary Disruptions

**PDB Protects From (Voluntary):**
- `kubectl drain` (node maintenance)
- Cluster autoscaling
- Manual pod eviction

**PDB Does NOT Protect From (Involuntary):**
- Node failure (pod rescheduled but may have downtime)
- Out of memory killer
- Pod crashes
- Networking issues

## Production Checklist

- [ ] Review PDB strategy for each service
- [ ] Verify `podDisruptionBudgets.enabled: true` in values
- [ ] Deploy with PDBs enabled
- [ ] List PDBs: `kubectl get pdb -n <namespace>`
- [ ] Test drain: `kubectl drain --dry-run=client`
- [ ] Document maintenance procedures
- [ ] Plan node maintenance windows
- [ ] Train team on PDB constraints

## Future Enhancements

- [ ] Scale adapters/genesis to 2+ replicas for HA
- [ ] Custom PDB policies per environment
- [ ] Monitoring for PDB violations
- [ ] Automation for safe drains

## References

- Kubernetes PDBs: https://kubernetes.io/docs/tasks/run-application/configure-pdb/
- Pod Disruption Budgets API: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.28/#poddisruptionbudget-v1-policy
