# Quick Deploy: PersistentVolumes

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Development (No Persistence - uses emptyDir)

```bash
helm install project-ai ./helm/project-ai \
  -f helm/project-ai/values.yaml
```

Data is lost when pod restarts. Use for testing only.

---

## Production (Persistent Storage)

### Step 1: Check Available Storage Classes

```bash
kubectl get storageclasses
```

**Expected Output (varies by cluster):**
- AWS: `gp2`, `gp3`, `io1`, `sc1`, `st1`
- Azure: `default`, `managed-premium`, `managed-csi`, `premium-retain`
- GCP: `standard`, `premium-rwo`, `balanced-rwo`
- On-prem: `local-storage`, `nfs-client`, `fast`, `slow`

### Step 2: Determine Storage Size

**Audit Data Growth:**
- Baseline: 1 GB
- Add 1 GB per 100,000 API calls
- Or monitor: `df -h /data` in dev environment

**Recommendation:**
```yaml
persistence:
  size: 10Gi        # 10 GB for ~1M API calls/month
  audit:
    size: 5Gi       # Backup staging area
```

### Step 3: Deploy

```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set persistence.storageClass="gp3"  # Use your storage class
  -n project-ai-prod \
  --create-namespace
```

Or with custom size:

```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set persistence.storageClass="gp3" \
  --set persistence.size="20Gi" \
  -n project-ai-prod \
  --create-namespace
```

### Step 4: Verify

```bash
# Check PVC created and bound
kubectl get pvc -n project-ai-prod

# Check API pod has volume mounted
kubectl exec -n project-ai-prod $(kubectl get pods -n project-ai-prod -l app.kubernetes.io/component=api -o jsonpath='{.items[0].metadata.name}') -- df -h /data

# Verify audit data directory exists
kubectl exec -n project-ai-prod <pod-name> -- ls -la /data/
```

---

## Monitoring

### Check Disk Usage

```bash
# Inside pod
kubectl exec -n project-ai-prod <pod-name> -- df -h /data

# PVC status
kubectl get pvc -n project-ai-prod -o wide
```

### Alert if > 80% Full

Set up monitoring alert:
```bash
# If using Prometheus, define rule that alerts when PVC > 80% used
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.80
```

---

## Resize Volume

```bash
# Check if storage class allows expansion
kubectl get storageclass <storage-class> -o yaml | grep allowVolumeExpansion

# Expand PVC
kubectl patch pvc project-ai-audit-data-pvc -n project-ai-prod \
  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# Or via Helm
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set persistence.size="20Gi" \
  -n project-ai-prod
```

---

## Troubleshoot

### PVC Stuck in Pending

```bash
# Check storage class exists
kubectl get storageclasses | grep <your-storage-class>

# Check PVC events
kubectl describe pvc project-ai-audit-data-pvc -n project-ai-prod

# Wait for provisioning
kubectl wait --for=condition=Bound pvc/project-ai-audit-data-pvc -n project-ai-prod --timeout=300s
```

### Pod Stuck in ContainerCreating

```bash
# Check pod events
kubectl describe pod <pod-name> -n project-ai-prod

# Check PVC bound status
kubectl get pvc -n project-ai-prod

# Check volume attachment at node
kubectl describe node <node-name>
```

### Disk Full

```bash
# Scale down pod
kubectl scale deployment project-ai-api --replicas=0 -n project-ai-prod

# Expand PVC
kubectl patch pvc project-ai-audit-data-pvc -n project-ai-prod \
  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# Scale pod back up
kubectl scale deployment project-ai-api --replicas=2 -n project-ai-prod
```

---

## Delete & Retain Data

```bash
# Delete deployment (PVC persists)
helm uninstall project-ai -n project-ai-prod

# List orphaned PVCs
kubectl get pvc -n project-ai-prod

# Manually keep PVC
kubectl patch pvc project-ai-audit-data-pvc -n project-ai-prod \
  -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'

# Or delete when ready
kubectl delete pvc project-ai-audit-data-pvc -n project-ai-prod
```
