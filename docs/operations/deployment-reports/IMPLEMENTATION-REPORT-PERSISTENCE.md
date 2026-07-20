# PersistentVolumes Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Implemented **production-grade persistent storage** for Project-AI. The API service now uses Kubernetes PersistentVolumeClaims (PVCs) to durably store audit data across pod restarts and cluster maintenance events.

## Files Created

### 1. `helm/project-ai/templates/persistence.yaml` (NEW)
- **Purpose:** Kubernetes PersistentVolumeClaim resource definitions
- **Content:**
  - Primary PVC for audit data (`audit-data-pvc`): main storage for chimera-audit.jsonl
  - Secondary PVC for backups (`backup-pvc`): for future backup/restore operations
  - Conditional creation based on `persistence.enabled` flag
  - Labeled for component tracking and RBAC

## Files Modified

### 1. `helm/project-ai/templates/api.yaml` (MODIFIED)
- **Changed:** Volume configuration from `emptyDir` to conditional PVC or emptyDir
- **Before:** Always uses `emptyDir {}` (ephemeral, data lost on pod restart)
- **After:** Uses PVC when `persistence.enabled=true`, emptyDir otherwise
- **Benefit:** Production uses persistent storage; development uses ephemeral

### 2. `helm/project-ai/values.yaml` (MODIFIED)
- **Added:** `persistence` section (development defaults)
- `persistence.enabled: false` (development uses emptyDir)
- `persistence.storageClass: "standard"`
- `persistence.size: 1Gi`
- `persistence.audit.enabled: false`
- `persistence.audit.size: 1Gi`

### 3. `helm/values.prod.yaml` (ALREADY PRESENT)
- Verified: `persistence.enabled: true` (production uses PVC)
- Storage size: 10Gi for audit data, 5Gi for backups

## Architecture

### Storage Layers

```
┌─────────────────────────────────────────────────────────┐
│ Pod (API Service)                                        │
├─────────────────────────────────────────────────────────┤
│ volumeMount: /data                                       │
│   ↓                                                       │
│   Application writes to /data/chimera-audit.jsonl        │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│ PersistentVolumeClaim (audit-data-pvc)                   │
├──────────────────────────────────────────────────────────┤
│ • accessMode: ReadWriteOnce (single pod, single node)    │
│ • storageClass: user-configurable                        │
│ • size: 10Gi (production)                                │
│ • resource type: PVC                                     │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│ PersistentVolume (dynamically provisioned)               │
├──────────────────────────────────────────────────────────┤
│ • provisioner: StorageClass provisioner                  │
│ • backend: EBS, Azure Disk, NFS, local storage, etc.     │
│ • reclaim policy: Delete (data removed with PVC)         │
└──────────────────────────────────────────────────────────┘
```

### Volume Lifecycle

```
1. Helm Install:
   persistence.yaml creates PVC → Kubernetes provisioner creates PV

2. Pod Scheduling:
   Deployment uses PVC name in volumeMount
   Kubelet attaches PV to node where pod runs

3. Container Runtime:
   Volume mounted at /data inside container
   Application writes audit data

4. Pod Restart/Reschedule:
   PVC persists (data retained)
   Pod can reschedule to same or different node (if RWX)
   ReadWriteOnce: same node, data retained

5. Helm Upgrade:
   PVC persists across upgrades
   Deployment continues using same PVC
   Data preserved

6. Helm Uninstall:
   Reclaim policy: Delete → PVC deleted → PV deleted
   Data is destroyed (by design, unless backed up)
```

## Configuration

### Storage Classes

**Common Options:**

```yaml
# AWS EBS (gp3)
storageClass: gp3

# Azure Disk
storageClass: managed-premium

# Google Cloud Persistent Disk
storageClass: pd-standard or pd-ssd

# Local provisioner (for on-prem)
storageClass: local-storage

# NFS
storageClass: nfs-client

# Generic "standard" (varies by cluster)
storageClass: standard
```

**Example Cluster Detection:**

```bash
# List available storage classes
kubectl get storageclasses

# Use default
kubectl get storageclasses -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'
```

### Size Recommendations

| Component | Purpose | Min Size | Prod Size | Justification |
|-----------|---------|----------|-----------|---------------|
| audit-data | Audit logs (chimera-audit.jsonl) | 1Gi | 10Gi | ~100MB/month of audit data |
| backup | Backup staging area | 1Gi | 5Gi | Temporary storage during backup ops |

**Formula for Audit Size:**
- Baseline: 1Gi (for ~10M audit events)
- Growth rate: ~100-500MB per month (depends on API usage)
- Recommendation: Size = baseline + (6 months growth) to avoid full disk
- For production: Monitor growth rate, scale accordingly

## Access Modes

### ReadWriteOnce (RWO) - Current Implementation

```yaml
accessModes:
  - ReadWriteOnce
```

**Characteristics:**
- Single pod can mount
- Single node only
- Highest performance for most storage backends
- Simpler provisioning

**Suitable for:**
- Single-replica services
- Services with pod affinity (prefer same node)

**Limitations:**
- If pod restarts on different node, volume unmounts/remounts (brief unavailability)
- Cannot share between pods (sequential read-only possible via separate PVCs)

### ReadWriteMany (RWX) - For Future Multi-Replica

If moving to multi-replica audit service:

```yaml
accessModes:
  - ReadWriteMany  # Requires NFS, GlusterFS, or managed file service
```

**Cost:** More expensive, more complex provisioning

**Current Status:** Not implemented (audit service is single-instance)

## Deployment Scenarios

### Scenario 1: Development (No Persistence)

**Configuration:**
```yaml
persistence:
  enabled: false
```

**Result:**
- Uses `emptyDir: {}`
- Data lost on pod restart
- No cloud storage costs
- Suitable for testing

**Deploy:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/project-ai/values.yaml
```

### Scenario 2: Production (Persistent Storage)

**Configuration:**
```yaml
persistence:
  enabled: true
  storageClass: "gp3"  # AWS
  size: 10Gi
```

**Result:**
- Uses PVC with dynamic provisioning
- Data persisted across pod restarts
- Survives node failures (data retained)
- Monthly storage costs ($0.10-1.00/GB/month depending on provider)

**Deploy:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set persistence.storageClass="gp3"
```

### Scenario 3: Production with Pre-Created PV

**For environments without dynamic provisioning or specific PV requirements:**

```bash
# Step 1: Manually create PV (cluster admin)
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: audit-data-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:  # or nfs, cinder, etc.
    path: /mnt/data
    type: DirectoryOrCreate
EOF

# Step 2: Create storage class that uses this PV
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-audit-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
EOF

# Step 3: Deploy with this storage class
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set persistence.storageClass="local-audit-storage"
```

## Security Considerations

### 1. Storage Access Control

**Current Implementation:**
- Pod runs as UID 10001 (non-root)
- Volume mounted at /data
- Read-write permissions required

**Recommendation:**
- Define RBAC policies for PVC access
- Only API deployment can read/write audit data
- Restrict kubectl access to PVCs

```yaml
# Example RBAC Rule
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: audit-reader
rules:
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    resourceNames: ["project-ai-audit-data-pvc"]
    verbs: ["get", "list", "watch"]
```

### 2. Data at Rest Encryption

**Kubernetes Level:**
```bash
# Enable encryption for etcd (PVC metadata)
# Requires: kube-apiserver --encryption-provider-config=/etc/kubernetes/pki/encryption.yaml
```

**Storage Backend Level:**
```bash
# AWS EBS: Use encrypted volumes
kubectl create storageclass encrypted-gp3 \
  --provisioner ebs.csi.aws.com \
  --parameters iops=3000,throughput=125,type=gp3,encrypted=true

# Azure Disk: Enable encryption by default (automatic)
# GCP: Use Google-managed or customer-managed encryption keys
```

### 3. Data at Rest Backup

**Current Status:** ❌ Not yet implemented
- PVC data is live data only
- No automatic backups
- Planned for Production Blocker #15 (Backup)

**Interim Mitigation:**
- Manual kubectl cp for snapshots
- Document retention policy (how long to keep audit data)

### 4. Reclaim Policy

**Current Implementation:**
```yaml
persistentVolumeReclaimPolicy: Delete  # Default from StorageClass
```

**Implications:**
- When PVC deleted (helm uninstall), PV is deleted
- **Data is permanently removed** (no recovery)

**Safer Alternative:**
```yaml
# Modify StorageClass to use Retain
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: safe-audit-storage
provisioner: ebs.csi.aws.com
reclaimPolicy: Retain  # PV remains after PVC deleted
```

## Monitoring & Alerts

### Volume Usage

**Monitor disk space:**
```bash
# Pod disk usage
kubectl exec -n project-ai-prod <pod-name> -- df -h /data

# PVC status
kubectl get pvc -n project-ai-prod
kubectl describe pvc project-ai-audit-data-pvc -n project-ai-prod
```

**Prometheus Rule (example):**
```yaml
- alert: PersistentVolumeAboutToFull
  expr: |
    kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.80
  for: 5m
  annotations:
    summary: "PVC {{ $labels.persistentvolumeclaim }} is {{ $value | humanizePercentage }} full"
```

### Disk Events

```bash
# Watch for provisioning errors
kubectl get events -n project-ai-prod --field-selector type=Warning

# Watch for attachment failures
kubectl describe pvc project-ai-audit-data-pvc -n project-ai-prod | grep -i event
```

## Resizing Volumes

### Expand PVC (if storage class allows)

```bash
# Check if storage class allows expansion
kubectl get storageclass gp3 -o yaml | grep allowVolumeExpansion

# Expand PVC
kubectl patch pvc project-ai-audit-data-pvc \
  -n project-ai-prod \
  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# Verify expansion
kubectl get pvc project-ai-audit-data-pvc -n project-ai-prod

# Monitor pod (file system expansion happens automatically)
kubectl exec -n project-ai-prod <pod-name> -- df -h /data
```

### Helm-Based Resize

```bash
# Update values.prod.yaml or via CLI
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set persistence.size="20Gi"

# PVC is updated (if storage class supports expansion)
```

## Troubleshooting

### PVC Stuck in Pending

**Symptoms:**
```
kubectl get pvc
NAME                        STATUS    VOLUME   CAPACITY   ACCESS MODES
project-ai-audit-data-pvc   Pending
```

**Causes:**
1. Storage class doesn't exist
2. No nodes with correct zone/node label
3. Provisioner is down
4. Insufficient cluster resources

**Solution:**
```bash
# Check storage class
kubectl get storageclasses

# Check PVC events
kubectl describe pvc project-ai-audit-data-pvc -n project-ai-prod

# If provisioner is slow, wait:
kubectl wait --for=condition=Bound pvc/project-ai-audit-data-pvc -n project-ai-prod --timeout=300s

# If still pending, debug provisioner
kubectl logs -n kube-system deployment/ebs-csi-controller
```

### Pod Stuck in ContainerCreating

**Symptoms:**
```
kubectl get pods
NAME                          READY   STATUS              RESTARTS
project-ai-api-xyz            0/1     ContainerCreating   0
```

**Cause:** Usually volume attachment failure

**Debug:**
```bash
# Check pod events
kubectl describe pod project-ai-api-xyz -n project-ai-prod

# Check PVC status
kubectl get pvc -n project-ai-prod

# Check node events (if volume attachment fails at node level)
kubectl describe node <node-name>
```

### Pod Marked as Failed Due to Disk Full

**Symptoms:**
- Pod crashes with exit code 137 or I/O errors
- `df -h` shows 100% disk usage

**Solution:**
```bash
# Step 1: Scale down pod to free space
kubectl scale deployment project-ai-api --replicas=0 -n project-ai-prod

# Step 2: Expand PVC (if storage class allows)
kubectl patch pvc project-ai-audit-data-pvc \
  -n project-ai-prod \
  -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# Step 3: Clear old audit logs (if safe)
kubectl run -it cleanup-pod \
  --image=busybox \
  --volumes='[{"name":"audit","persistentVolumeClaim":{"claimName":"project-ai-audit-data-pvc"}}]' \
  --volumeMounts='[{"name":"audit","mountPath":"/data"}]' \
  -n project-ai-prod \
  -- rm -f /data/chimera-audit.old.jsonl

# Step 4: Scale pod back up
kubectl scale deployment project-ai-api --replicas=2 -n project-ai-prod
```

## Validation Commands

### Pre-Deployment

```bash
# Check persistence template renders correctly
helm template test ./helm/project-ai \
  -f helm/values.prod.yaml | grep -A 10 "kind: PersistentVolumeClaim"

# Verify API deployment uses PVC
helm template test ./helm/project-ai \
  -f helm/values.prod.yaml | grep -A 3 "persistentVolumeClaim"
```

### Post-Deployment

```bash
# Verify PVC created
kubectl get pvc -n project-ai-prod

# Verify PV provisioned
kubectl get pv | grep audit-data

# Verify pod volume mounted
kubectl get pods -n project-ai-prod -l app.kubernetes.io/component=api \
  -o jsonpath='{.items[0].spec.volumes[*].name}'

# Verify volume is accessible in pod
kubectl exec -n project-ai-prod <pod-name> -- df -h /data

# Verify data persists across pod restart
kubectl exec -n project-ai-prod <pod-name> -- touch /data/test-file
kubectl delete pod <pod-name> -n project-ai-prod
# Wait for new pod to start
kubectl exec -n project-ai-prod <pod-name> -- ls /data/test-file  # Should exist
```

## Production Checklist

Before deploying to production:

- [ ] Choose storage class appropriate for your cluster (EBS, Azure Disk, NFS, etc.)
- [ ] Verify storage class exists: `kubectl get storageclasses`
- [ ] Determine audit data growth rate (monitor for 2-4 weeks)
- [ ] Size PVC appropriately (baseline + 6 months growth)
- [ ] Test volume expansion capability
- [ ] Configure audit data retention policy
- [ ] Set up monitoring alerts for disk usage > 80%
- [ ] Plan backup strategy (implemented in Task 15)
- [ ] Test disaster recovery (delete PVC, verify system behavior)
- [ ] Document per-environment storage configurations
- [ ] Train team on PVC operations (expand, troubleshoot)
- [ ] Set reclaim policy to "Retain" if data protection needed

## Future Enhancements

- [ ] Multi-replica with ReadWriteMany (shared storage for audit service scale-out)
- [ ] Automated backup snapshots (AWS EBS snapshots, GCP snapshots)
- [ ] Volume encryption keys (customer-managed KMS)
- [ ] Cross-zone redundancy (multi-AZ snapshots)
- [ ] Audit data archival (S3, GCS, Azure Blob)
- [ ] Volume performance monitoring dashboard

## References

- Kubernetes PersistentVolumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- Storage Classes: https://kubernetes.io/docs/concepts/storage/storage-classes/
- AWS EBS CSI Driver: https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html
- Azure Disk CSI Driver: https://github.com/kubernetes-sigs/azuredisk-csi-driver
- GCP Persistent Disks: https://cloud.google.com/kubernetes-engine/docs/concepts/persistentvolumes
