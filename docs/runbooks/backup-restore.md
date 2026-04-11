# Backup and Restore Runbook

## Overview
Procedures for backing up and restoring the Sovereign Governance Substrate system, including databases, configurations, and workflow state.

## Backup Strategy

### Backup Components

1. **Temporal Database** (Cassandra/PostgreSQL)
   - Workflow execution history
   - Task queue state
   - Metadata and configuration

2. **Application Database**
   - Agent state
   - Governance data
   - User data

3. **Kubernetes Resources**
   - Deployments, Services, ConfigMaps
   - Secrets (encrypted)
   - Custom Resource Definitions

4. **Workflow Code**
   - Git repository (primary source)
   - Container images

5. **Configuration**
   - Environment variables
   - Feature flags
   - API keys (encrypted)

### Backup Schedule

| Component | Frequency | Retention | Type |
|-----------|-----------|-----------|------|
| Temporal DB | Hourly | 7 days | Incremental |
| Temporal DB | Daily | 30 days | Full |
| Temporal DB | Weekly | 1 year | Full |
| App DB | Hourly | 7 days | Incremental |
| App DB | Daily | 30 days | Full |
| K8s Resources | Daily | 30 days | Full |
| Secrets | Daily | 90 days | Encrypted |
| Volumes | Daily | 14 days | Snapshot |

## Cassandra Backup

### Automated Backup Script

```bash
#!/bin/bash
# cassandra-backup.sh

set -e

BACKUP_DIR="/backups/cassandra"
DATE=$(date +%Y%m%d_%H%M%S)
NAMESPACE="temporal"
POD_NAME="cassandra-0"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Create snapshot
echo "Creating Cassandra snapshot..."
kubectl exec -it -n $NAMESPACE $POD_NAME -- \
  nodetool snapshot -t backup_$DATE

# Copy snapshot data
echo "Copying snapshot data..."
for keyspace in temporal temporal_visibility; do
  kubectl exec -n $NAMESPACE $POD_NAME -- \
    tar czf /tmp/${keyspace}_${DATE}.tar.gz \
    /var/lib/cassandra/data/$keyspace/*/snapshots/backup_$DATE
  
  kubectl cp $NAMESPACE/$POD_NAME:/tmp/${keyspace}_${DATE}.tar.gz \
    $BACKUP_DIR/$DATE/${keyspace}_${DATE}.tar.gz
  
  kubectl exec -n $NAMESPACE $POD_NAME -- \
    rm /tmp/${keyspace}_${DATE}.tar.gz
done

# Clear snapshot
echo "Clearing snapshot..."
kubectl exec -it -n $NAMESPACE $POD_NAME -- \
  nodetool clearsnapshot -t backup_$DATE

# Upload to S3
echo "Uploading to S3..."
aws s3 sync $BACKUP_DIR/$DATE s3://sovereign-backups/cassandra/$DATE/

# Clean old backups
echo "Cleaning old backups..."
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} +

echo "Backup completed: $DATE"
```

### Schedule Backup (CronJob)

```yaml
# cassandra-backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cassandra-backup
  namespace: temporal
spec:
  schedule: "0 */4 * * *"  # Every 4 hours
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: backup-sa
          
          containers:
            - name: backup
              image: bitnami/cassandra:4.1
              
              env:
                - name: AWS_ACCESS_KEY_ID
                  valueFrom:
                    secretKeyRef:
                      name: aws-credentials
                      key: access-key-id
                - name: AWS_SECRET_ACCESS_KEY
                  valueFrom:
                    secretKeyRef:
                      name: aws-credentials
                      key: secret-access-key
              
              volumeMounts:
                - name: backup-script
                  mountPath: /scripts
                - name: backup-storage
                  mountPath: /backups
              
              command:
                - /bin/bash
                - /scripts/cassandra-backup.sh
          
          volumes:
            - name: backup-script
              configMap:
                name: backup-scripts
                defaultMode: 0755
            - name: backup-storage
              persistentVolumeClaim:
                claimName: backup-pvc
          
          restartPolicy: OnFailure
```

### Manual Backup

```bash
# Create immediate backup
kubectl exec -it -n temporal cassandra-0 -- nodetool snapshot -t manual_backup

# List snapshots
kubectl exec -it -n temporal cassandra-0 -- \
  nodetool listsnapshots

# Export snapshot
SNAPSHOT_NAME="manual_backup"
kubectl exec -n temporal cassandra-0 -- \
  tar czf /tmp/backup.tar.gz \
  /var/lib/cassandra/data/temporal/*/snapshots/$SNAPSHOT_NAME

kubectl cp temporal/cassandra-0:/tmp/backup.tar.gz ./backup.tar.gz

# Upload to backup location
aws s3 cp backup.tar.gz s3://sovereign-backups/cassandra/manual/
```

## PostgreSQL Backup (Alternative)

### Automated Backup

```bash
#!/bin/bash
# postgres-backup.sh

set -e

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
NAMESPACE="temporal"
POD_NAME="postgres-0"
DATABASE="temporal"

mkdir -p $BACKUP_DIR

# Full backup
kubectl exec -n $NAMESPACE $POD_NAME -- \
  pg_dump -U temporal -Fc $DATABASE > $BACKUP_DIR/temporal_${DATE}.dump

# Compress
gzip $BACKUP_DIR/temporal_${DATE}.dump

# Upload to S3
aws s3 cp $BACKUP_DIR/temporal_${DATE}.dump.gz \
  s3://sovereign-backups/postgres/$DATE/

# WAL archiving for point-in-time recovery
kubectl exec -n $NAMESPACE $POD_NAME -- \
  pg_basebackup -U temporal -D /backups/base -Ft -z -P

echo "PostgreSQL backup completed: $DATE"
```

## Kubernetes Resources Backup

### Using Velero

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.5.0 \
  --bucket sovereign-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --secret-file ./credentials-velero

# Create backup schedule
velero schedule create sovereign-daily \
  --schedule="@daily" \
  --include-namespaces sovereign-governance,temporal \
  --ttl 720h  # 30 days

# Create immediate backup
velero backup create sovereign-backup-$(date +%Y%m%d) \
  --include-namespaces sovereign-governance,temporal \
  --wait

# List backups
velero backup get

# Describe backup
velero backup describe sovereign-backup-20260411
```

### Manual K8s Resource Export

```bash
# Export all resources
kubectl get all --all-namespaces -o yaml > k8s-all-resources.yaml

# Export specific namespace
kubectl get all -n sovereign-governance -o yaml > sovereign-governance.yaml

# Export ConfigMaps
kubectl get configmap -n sovereign-governance -o yaml > configmaps.yaml

# Export Secrets (encrypted)
kubectl get secrets -n sovereign-governance -o yaml | \
  openssl enc -aes-256-cbc -salt -out secrets.yaml.enc

# Export PVCs
kubectl get pvc -n sovereign-governance -o yaml > pvcs.yaml

# Export CRDs
kubectl get crd -o yaml > crds.yaml
```

## Volume Snapshots

### Create Volume Snapshot

```yaml
# volume-snapshot.yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: cassandra-snapshot-20260411
  namespace: temporal
spec:
  volumeSnapshotClassName: csi-aws-vsc
  source:
    persistentVolumeClaimName: data-cassandra-0
```

```bash
# Create snapshot
kubectl apply -f volume-snapshot.yaml

# Verify snapshot
kubectl get volumesnapshot -n temporal

# Describe snapshot
kubectl describe volumesnapshot cassandra-snapshot-20260411 -n temporal
```

### Automated Snapshot Schedule

```yaml
# snapshot-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: volume-snapshot
  namespace: temporal
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: snapshot-sa
          
          containers:
            - name: snapshot
              image: bitnami/kubectl:latest
              
              command:
                - /bin/bash
                - -c
                - |
                  DATE=$(date +%Y%m%d)
                  for pvc in $(kubectl get pvc -n temporal -o name); do
                    cat <<EOF | kubectl apply -f -
                  apiVersion: snapshot.storage.k8s.io/v1
                  kind: VolumeSnapshot
                  metadata:
                    name: $(basename $pvc)-snapshot-$DATE
                    namespace: temporal
                  spec:
                    volumeSnapshotClassName: csi-aws-vsc
                    source:
                      persistentVolumeClaimName: $(basename $pvc)
                  EOF
                  done
          
          restartPolicy: OnFailure
```

## Restore Procedures

### Restore Cassandra from Backup

```bash
#!/bin/bash
# cassandra-restore.sh

set -e

BACKUP_DATE=$1  # e.g., 20260411_120000
NAMESPACE="temporal"
POD_NAME="cassandra-0"

if [ -z "$BACKUP_DATE" ]; then
  echo "Usage: $0 BACKUP_DATE"
  exit 1
fi

echo "Restoring Cassandra from backup: $BACKUP_DATE"

# Download backup from S3
mkdir -p /tmp/restore
aws s3 sync s3://sovereign-backups/cassandra/$BACKUP_DATE/ /tmp/restore/

# Stop Cassandra
kubectl exec -n $NAMESPACE $POD_NAME -- nodetool drain
kubectl scale statefulset cassandra --replicas=0 -n $NAMESPACE

# Wait for pod to terminate
kubectl wait --for=delete pod/$POD_NAME -n $NAMESPACE --timeout=300s

# Clear existing data
kubectl exec -n $NAMESPACE $POD_NAME -- \
  rm -rf /var/lib/cassandra/data/temporal/*

# Copy backup data to pod
for keyspace_backup in /tmp/restore/*.tar.gz; do
  kubectl cp $keyspace_backup $NAMESPACE/$POD_NAME:/tmp/
  
  kubectl exec -n $NAMESPACE $POD_NAME -- \
    tar xzf /tmp/$(basename $keyspace_backup) -C /var/lib/cassandra/data/
done

# Start Cassandra
kubectl scale statefulset cassandra --replicas=1 -n $NAMESPACE

# Wait for Cassandra to be ready
kubectl wait --for=condition=ready pod/$POD_NAME -n $NAMESPACE --timeout=600s

# Verify restore
kubectl exec -it -n $NAMESPACE $POD_NAME -- \
  cqlsh -e "DESCRIBE KEYSPACES;"

echo "Restore completed"
```

### Restore PostgreSQL from Backup

```bash
#!/bin/bash
# postgres-restore.sh

set -e

BACKUP_FILE=$1
NAMESPACE="temporal"
POD_NAME="postgres-0"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 BACKUP_FILE"
  exit 1
fi

echo "Restoring PostgreSQL from: $BACKUP_FILE"

# Download backup
aws s3 cp s3://sovereign-backups/postgres/$BACKUP_FILE ./

# Drop and recreate database
kubectl exec -it -n $NAMESPACE $POD_NAME -- \
  psql -U postgres -c "DROP DATABASE IF EXISTS temporal;"

kubectl exec -it -n $NAMESPACE $POD_NAME -- \
  psql -U postgres -c "CREATE DATABASE temporal;"

# Restore
gunzip -c $BACKUP_FILE | \
  kubectl exec -i -n $NAMESPACE $POD_NAME -- \
  pg_restore -U temporal -d temporal

# Verify
kubectl exec -it -n $NAMESPACE $POD_NAME -- \
  psql -U temporal -d temporal -c "\dt"

echo "PostgreSQL restore completed"
```

### Restore Using Velero

```bash
# List available backups
velero backup get

# Restore entire backup
velero restore create --from-backup sovereign-backup-20260411

# Restore specific namespace
velero restore create restore-sovereign \
  --from-backup sovereign-backup-20260411 \
  --include-namespaces sovereign-governance

# Restore with label selector
velero restore create restore-workers \
  --from-backup sovereign-backup-20260411 \
  --selector app=temporal-worker

# Monitor restore
velero restore describe restore-sovereign

# Get restore logs
velero restore logs restore-sovereign
```

### Restore from Volume Snapshot

```yaml
# restore-from-snapshot.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cassandra-restored
  namespace: temporal
spec:
  storageClassName: gp3
  dataSource:
    name: cassandra-snapshot-20260411
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

```bash
# Create PVC from snapshot
kubectl apply -f restore-from-snapshot.yaml

# Update StatefulSet to use restored PVC
kubectl edit statefulset cassandra -n temporal
# Change volumeClaimTemplates to reference cassandra-restored

# Restart StatefulSet
kubectl rollout restart statefulset cassandra -n temporal
```

## Point-in-Time Recovery (PITR)

### PostgreSQL PITR

```bash
# Configure continuous archiving (WAL)
kubectl exec -it -n temporal postgres-0 -- \
  psql -U postgres -c "ALTER SYSTEM SET archive_mode = 'on';"

kubectl exec -it -n temporal postgres-0 -- \
  psql -U postgres -c "ALTER SYSTEM SET archive_command = 'aws s3 cp %p s3://sovereign-backups/postgres/wal/%f';"

# Restart PostgreSQL
kubectl rollout restart statefulset postgres -n temporal

# Restore to specific point in time
RESTORE_TIME="2026-04-11 14:30:00"

# Download base backup and WAL files
aws s3 sync s3://sovereign-backups/postgres/base/ /tmp/base/
aws s3 sync s3://sovereign-backups/postgres/wal/ /tmp/wal/

# Create recovery configuration
cat > /tmp/recovery.conf <<EOF
restore_command = 'cp /tmp/wal/%f %p'
recovery_target_time = '$RESTORE_TIME'
recovery_target_action = 'promote'
EOF

# Copy to PostgreSQL pod and restore
kubectl cp /tmp/recovery.conf temporal/postgres-0:/var/lib/postgresql/data/
kubectl exec -n temporal postgres-0 -- pg_ctl -D /var/lib/postgresql/data restart
```

## Disaster Recovery Scenarios

### Scenario 1: Complete Cluster Loss

```bash
# 1. Provision new cluster
eksctl create cluster -f cluster-config.yaml

# 2. Install core components
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 3. Install Velero
velero install --provider aws --bucket sovereign-backups

# 4. Restore from latest backup
LATEST_BACKUP=$(velero backup get --output json | jq -r '.items[0].metadata.name')
velero restore create disaster-recovery --from-backup $LATEST_BACKUP

# 5. Monitor restore
velero restore describe disaster-recovery

# 6. Verify services
kubectl get pods -A
kubectl get svc -A

# 7. Restore databases separately if needed
./cassandra-restore.sh <backup_date>

# 8. Verify data integrity
kubectl exec -it -n temporal cassandra-0 -- nodetool status
kubectl logs -n sovereign-governance deployment/temporal-worker
```

### Scenario 2: Database Corruption

```bash
# 1. Identify corruption
kubectl exec -it -n temporal cassandra-0 -- nodetool status
kubectl exec -it -n temporal cassandra-0 -- nodetool verify temporal

# 2. Stop writes
kubectl scale deployment temporal-worker --replicas=0 -n sovereign-governance

# 3. Find last good backup
aws s3 ls s3://sovereign-backups/cassandra/ | sort -r

# 4. Restore from backup
./cassandra-restore.sh <last_good_backup>

# 5. Verify integrity
kubectl exec -it -n temporal cassandra-0 -- nodetool verify temporal

# 6. Resume operations
kubectl scale deployment temporal-worker --replicas=5 -n sovereign-governance
```

### Scenario 3: Accidental Data Deletion

```bash
# For Temporal workflows - restore specific keyspace
BACKUP_DATE="20260411_120000"

# 1. Restore to temporary keyspace
kubectl exec -it -n temporal cassandra-0 -- \
  cqlsh -e "CREATE KEYSPACE temporal_restore WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};"

# 2. Restore data
./cassandra-restore.sh $BACKUP_DATE temporal_restore

# 3. Copy specific data back
kubectl exec -it -n temporal cassandra-0 -- \
  cqlsh -e "COPY temporal.workflows FROM temporal_restore.workflows;"

# 4. Verify and clean up
kubectl exec -it -n temporal cassandra-0 -- \
  cqlsh -e "DROP KEYSPACE temporal_restore;"
```

## Backup Verification

### Automated Backup Testing

```bash
#!/bin/bash
# test-backup.sh

set -e

BACKUP_DATE=$1

echo "Testing backup: $BACKUP_DATE"

# 1. Create test namespace
kubectl create namespace backup-test

# 2. Restore backup to test namespace
velero restore create test-restore-$BACKUP_DATE \
  --from-backup sovereign-backup-$BACKUP_DATE \
  --namespace-mappings sovereign-governance:backup-test

# 3. Wait for restore
velero restore wait test-restore-$BACKUP_DATE

# 4. Verify pods are running
kubectl get pods -n backup-test

# 5. Run smoke tests
kubectl apply -f test/smoke-test.yaml -n backup-test
kubectl wait --for=condition=complete job/smoke-test -n backup-test --timeout=300s

# 6. Clean up
kubectl delete namespace backup-test
velero restore delete test-restore-$BACKUP_DATE --confirm

echo "Backup test passed: $BACKUP_DATE"
```

## Monitoring and Alerts

### Backup Monitoring

```yaml
# backup-monitoring-alert.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backup-alerts
  namespace: monitoring
data:
  backup-alerts.yml: |
    groups:
      - name: backup_alerts
        rules:
          - alert: BackupFailed
            expr: kube_job_status_failed{job_name=~".*backup.*"} > 0
            for: 5m
            labels:
              severity: critical
            annotations:
              summary: "Backup job failed"
              description: "Backup job {{ $labels.job_name }} has failed"
          
          - alert: BackupTooOld
            expr: time() - velero_backup_last_successful_timestamp > 86400
            for: 1h
            labels:
              severity: warning
            annotations:
              summary: "Backup is too old"
              description: "Last successful backup was more than 24 hours ago"
```

## Best Practices

### Backup
✅ **Test restores regularly**: Monthly restore drills
✅ **Encrypt backups**: Use encryption at rest
✅ **Multiple backup locations**: Cross-region replication
✅ **Automate backups**: CronJobs for consistency
✅ **Monitor backup jobs**: Alert on failures
✅ **Document procedures**: Keep runbooks updated

### Restore
✅ **Verify data integrity**: After every restore
✅ **Test in non-prod first**: Before production restore
✅ **Have rollback plan**: In case restore fails
✅ **Communicate**: Notify stakeholders
✅ **Document incidents**: Post-mortem for major restores

## Revision History

- 2026-04-11: Initial version
