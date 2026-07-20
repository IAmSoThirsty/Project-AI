# Restore Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Documented **disaster recovery procedures** for restoring Project-AI from backups. Point-in-time recovery to previous data states.

## Restore Procedure

### Step 1: Identify Backup

```bash
# List available backups
aws s3 ls s3://bucket/backups/

# Select backup: audit-20240101-020000.tar.gz
BACKUP="audit-20240101-020000.tar.gz"
```

### Step 2: Create Restore Pod

```bash
# Create temporary pod with backup PVC mounted
kubectl run restore-pod \
  --image=busybox \
  --volumes='[{"name":"backup","persistentVolumeClaim":{"claimName":"project-ai-backup-pvc"}}]' \
  --volumeMounts='[{"name":"backup","mountPath":"/backup"}]' \
  -it \
  -n project-ai-prod \
  -- /bin/sh
```

### Step 3: Download Backup

```bash
# Inside pod:
cd /backup
aws s3 cp s3://bucket/backups/$BACKUP .
tar tzf $BACKUP | head -10  # Verify contents
```

### Step 4: Scale Down API

```bash
# Stop API pods to prevent conflicts
kubectl scale deployment project-ai-api --replicas=0 -n project-ai-prod
kubectl wait --for=condition=Unavailable pod -l app.kubernetes.io/component=api -n project-ai-prod --timeout=60s
```

### Step 5: Extract Backup to Audit PVC

```bash
# Create temporary pod with both PVCs
kubectl run restore-extract \
  --image=busybox \
  --volumes='[{"name":"backup","persistentVolumeClaim":{"claimName":"project-ai-backup-pvc"}},{"name":"audit","persistentVolumeClaim":{"claimName":"project-ai-audit-data-pvc"}}]' \
  --volumeMounts='[{"name":"backup","mountPath":"/backup"},{"name":"audit","mountPath":"/audit"}]' \
  -n project-ai-prod \
  -- tar xzf /backup/$BACKUP -C /audit
```

### Step 6: Scale Up API

```bash
# Restart API pods with restored data
kubectl scale deployment project-ai-api --replicas=2 -n project-ai-prod
kubectl rollout status deployment/project-ai-api -n project-ai-prod
```

### Step 7: Verify Restore

```bash
# Check audit data restored
kubectl exec -n project-ai-prod <api-pod> -- ls -la /data/

# Check data integrity
kubectl exec -n project-ai-prod <api-pod> -- wc -l /data/chimera-audit.jsonl
```

## Cleanup

```bash
# Delete temporary pods
kubectl delete pod restore-pod restore-extract -n project-ai-prod

# Delete extracted backup from backup PVC
kubectl exec -n project-ai-prod <cleanup-pod> -- rm /backup/$BACKUP
```

## Recovery Time Objectives (RTO)

| Scenario | RTO | RPO |
|----------|-----|-----|
| Single pod failure | 30s | 0 (stateless) |
| PVC corruption | 15m | 24h (daily backup) |
| Cluster failure | 1h | 24h (daily backup) |
| Data loss | 15m + restore | 24h |

## Automated Restore (Future)

```bash
# Script for automated restore
./restore.sh s3://bucket/backups/audit-20240101-020000.tar.gz project-ai-prod
```

## References

- Kubernetes Persistence: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- PVC Recovery: https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/

## Runbook

- Document restore procedure in runbook
- Test restore monthly
- Train team on restore procedures
- Set recovery time targets (RTO/RPO)
