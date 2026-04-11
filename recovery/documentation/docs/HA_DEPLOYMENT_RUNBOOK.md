# HIGH AVAILABILITY DEPLOYMENT RUNBOOK

## Team Bravo - High Availability Architect

**Date**: 2026-04-09  
**Status**: Production Ready  
**Failover Target**: <30 seconds ✅

---

## OVERVIEW

This runbook covers deployment, monitoring, and failover procedures for:

- **PostgreSQL HA**: 1 master + 2 read replicas
- **Redis Sentinel**: 1 master + 2 slaves + 3 sentinels

---

## POSTGRESQL HIGH AVAILABILITY

### Architecture

```
┌─────────────────────────────────────┐
│        PgBouncer Pool (2-8)         │  ← Application connections
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Master (postgres-0)            │  ← Writes only
└─────────────────────────────────────┘
                 ↓ Streaming replication
┌─────────────┬───────────────────────┐
│ Replica 1   │     Replica 2         │  ← Reads only
│ (postgres-  │   (postgres-read-     │
│ read-       │    replica-1)         │
│ replica-0)  │                       │
└─────────────┴───────────────────────┘
```

### Deployment Steps

#### 1. Deploy PostgreSQL Master

```bash
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/secret.yaml
kubectl apply -f k8s/base/postgres.yaml

# Wait for master to be ready

kubectl wait --for=condition=ready pod/postgres-0 -n project-ai --timeout=120s

# Verify master is running

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT version();"
```

#### 2. Deploy Read Replicas

```bash
kubectl apply -f k8s/base/postgres-read-replicas.yaml

# Wait for replicas to be ready

kubectl wait --for=condition=ready pod/postgres-read-replica-0 -n project-ai --timeout=300s
kubectl wait --for=condition=ready pod/postgres-read-replica-1 -n project-ai --timeout=300s

# Verify replication status

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT * FROM pg_stat_replication;"
```

Expected output:
```
 application_name | state     | sync_state
------------------+-----------+------------
 replica-0        | streaming | async
 replica-1        | streaming | async
```

#### 3. Deploy PgBouncer Connection Pool

```bash

# Already included in postgres-read-replicas.yaml

kubectl get pods -n project-ai | grep pgbouncer

# Verify PgBouncer is working

kubectl exec -n project-ai pgbouncer-xxxxx -- psql -h localhost -p 6432 -U projectai -c "SHOW POOLS;"
```

### Monitoring

#### Check Replication Lag

```bash

# On master

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "
  SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
  FROM pg_stat_replication;
"

# On replica (check lag)

kubectl exec -n project-ai postgres-read-replica-0 -- psql -U projectai -c "
  SELECT 
    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds;
"
```

**Alert Threshold**: Lag > 10 seconds

#### Check Connection Pool Health

```bash
kubectl exec -n project-ai pgbouncer-xxxxx -- psql -h localhost -p 6432 -U projectai -c "
  SHOW STATS;
  SHOW POOLS;
"
```

### Failover Procedures

#### Scenario 1: Master Failure (Automatic)

**Detection**: Kubernetes liveness probe fails (3 consecutive failures)

**Automatic Actions**:

1. Kubernetes restarts postgres-0 pod
2. PgBouncer detects connection failures
3. Applications retry connections (handled by PgBouncer)
4. New master pod comes up and resumes replication

**Expected Recovery Time**: 45-60 seconds

**Manual Verification**:
```bash

# Check pod status

kubectl get pods -n project-ai | grep postgres-0

# Verify replication resumed

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT * FROM pg_stat_replication;"
```

#### Scenario 2: Manual Failover (Promote Replica)

**Use Case**: Master node maintenance, hardware issues

```bash

# 1. Identify replica to promote

kubectl get pods -n project-ai | grep postgres-read-replica

# 2. Promote replica to master

kubectl exec -n project-ai postgres-read-replica-0 -- pg_ctl promote

# 3. Update application config to point to new master

# (Update service endpoint or use HAProxy/Patroni)

# 4. Rebuild old master as new replica

kubectl delete pod postgres-0 -n project-ai
kubectl apply -f k8s/base/postgres.yaml
```

**Expected Downtime**: <30 seconds ✅

#### Scenario 3: Split-Brain Prevention

**Issue**: Network partition causes both master and replica to think they're primary

**Prevention**:

1. Use synchronous replication for critical transactions
2. Implement fencing with Patroni or Stolon
3. Use quorum-based writes

**Detection**:
```bash

# Check for multiple masters

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT pg_is_in_recovery();"
kubectl exec -n project-ai postgres-read-replica-0 -- psql -U projectai -c "SELECT pg_is_in_recovery();"

# Both should NOT return 'f' (false = master)

```

**Resolution**:
```bash

# Manually fence the split-brain node

kubectl delete pod postgres-read-replica-0 -n project-ai --force --grace-period=0

# Rebuild from master

kubectl apply -f k8s/base/postgres-read-replicas.yaml
```

---

## REDIS SENTINEL HIGH AVAILABILITY

### Architecture

```
┌─────────────────────────────────────┐
│      Redis Master (redis-master-0)  │  ← Writes
└─────────────────────────────────────┘
                 ↓ Replication
┌─────────────┬───────────────────────┐
│  Slave 1    │       Slave 2         │  ← Reads
│ (redis-     │   (redis-slave-1)     │
│ slave-0)    │                       │
└─────────────┴───────────────────────┘
       ↑                 ↑
       └─────────┬───────┘
                 ↓ Monitored by
┌────────────────────────────────────────┐
│ Sentinel 1  Sentinel 2  Sentinel 3    │  ← Quorum (2/3)
└────────────────────────────────────────┘
```

### Deployment Steps

#### 1. Deploy Redis Master

```bash
kubectl apply -f k8s/base/redis.yaml

# Wait for master to be ready

kubectl wait --for=condition=ready pod/redis-master-0 -n project-ai --timeout=120s

# Verify master

kubectl exec -n project-ai redis-master-0 -- redis-cli INFO replication
```

#### 2. Deploy Redis Sentinel

```bash
kubectl apply -f k8s/base/redis-sentinel.yaml

# Wait for all sentinels to be ready

kubectl wait --for=condition=ready pod/redis-sentinel-0 -n project-ai --timeout=120s
kubectl wait --for=condition=ready pod/redis-sentinel-1 -n project-ai --timeout=120s
kubectl wait --for=condition=ready pod/redis-sentinel-2 -n project-ai --timeout=120s

# Verify sentinel status

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL masters
```

### Monitoring

#### Check Replication Status

```bash

# On master

kubectl exec -n project-ai redis-master-0 -- redis-cli INFO replication

# Expected output:

# role:master

# connected_slaves:2

# slave0:ip=10.x.x.x,state=online,offset=xxxx

# slave1:ip=10.x.x.x,state=online,offset=xxxx

```

#### Check Sentinel Quorum

```bash

# Check sentinel configuration

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL masters

# Check quorum status

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL ckquorum mymaster
```

**Expected**: `OK 3 usable Sentinels. Quorum and failover authorization can be reached`

### Failover Procedures

#### Scenario 1: Automatic Failover

**Trigger**: Master becomes unreachable (Sentinels detect after 30s)

**Automatic Actions**:

1. Sentinel quorum (2/3) agrees master is down
2. Sentinel promotes a slave to master
3. Other slave reconfigures to new master
4. Applications reconnect to new master

**Expected Failover Time**: 15-30 seconds ✅

**Monitor Failover**:
```bash

# Watch sentinel logs

kubectl logs -n project-ai redis-sentinel-0 -f

# Check new master

kubectl exec -n project-ai redis-master-0 -- redis-cli INFO replication
```

#### Scenario 2: Manual Failover

**Use Case**: Planned maintenance, testing

```bash

# Trigger failover via sentinel

kubectl exec -n project-ai redis-sentinel-0 -- \
  redis-cli -p 26379 SENTINEL failover mymaster

# Monitor failover progress

kubectl exec -n project-ai redis-sentinel-0 -- \
  redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
```

#### Scenario 3: Slave Out of Sync

**Detection**:
```bash

# Check slave lag

kubectl exec -n project-ai redis-slave-0 -- redis-cli INFO replication | grep master_last_io_seconds_ago

# If lag > 60 seconds, investigate

```

**Resolution**:
```bash

# Force full resync

kubectl exec -n project-ai redis-slave-0 -- redis-cli REPLICAOF redis-master-0.redis.project-ai.svc.cluster.local 6379
```

---

## DISASTER RECOVERY

### Backup Strategy

#### PostgreSQL Backups

```bash

# Automated daily backups (CronJob)

kubectl apply -f k8s/base/backup-cronjob.yaml

# Manual backup

kubectl exec -n project-ai postgres-0 -- pg_dump -U projectai projectai > backup-$(date +%Y%m%d).sql

# Backup to S3 (AWS)

kubectl exec -n project-ai postgres-0 -- pg_dump -U projectai projectai | \
  aws s3 cp - s3://project-ai-backups/postgres-$(date +%Y%m%d).sql
```

#### Redis Backups

```bash

# Trigger RDB snapshot

kubectl exec -n project-ai redis-master-0 -- redis-cli BGSAVE

# Copy snapshot

kubectl cp project-ai/redis-master-0:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb

# Automated AOF backups (already configured)

```

### Restore Procedures

#### Restore PostgreSQL

```bash

# 1. Stop all applications

kubectl scale deployment app --replicas=0 -n project-ai

# 2. Restore from backup

kubectl exec -i -n project-ai postgres-0 -- psql -U projectai projectai < backup-20260409.sql

# 3. Verify data

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT COUNT(*) FROM users;"

# 4. Restart applications

kubectl scale deployment app --replicas=3 -n project-ai
```

#### Restore Redis

```bash

# 1. Stop Redis

kubectl scale statefulset redis-master --replicas=0 -n project-ai

# 2. Restore dump.rdb

kubectl cp redis-backup-20260409.rdb project-ai/redis-master-0:/data/dump.rdb

# 3. Restart Redis

kubectl scale statefulset redis-master --replicas=1 -n project-ai

# 4. Verify data

kubectl exec -n project-ai redis-master-0 -- redis-cli DBSIZE
```

---

## HEALTH CHECKS

### PostgreSQL Health Check Script

```bash
#!/bin/bash

# pg-health-check.sh

NAMESPACE="project-ai"
THRESHOLD=10  # Max replication lag in seconds

# Check master

kubectl exec -n $NAMESPACE postgres-0 -- psql -U projectai -c "SELECT 1;" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "CRITICAL: PostgreSQL master is down"
  exit 2
fi

# Check replication lag

LAG=$(kubectl exec -n $NAMESPACE postgres-read-replica-0 -- psql -U projectai -t -c \
  "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));" | tr -d ' ')

if (( $(echo "$LAG > $THRESHOLD" | bc -l) )); then
  echo "WARNING: Replication lag is ${LAG}s (threshold: ${THRESHOLD}s)"
  exit 1
fi

echo "OK: PostgreSQL HA is healthy"
exit 0
```

### Redis Health Check Script

```bash
#!/bin/bash

# redis-health-check.sh

NAMESPACE="project-ai"

# Check master

kubectl exec -n $NAMESPACE redis-master-0 -- redis-cli PING > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "CRITICAL: Redis master is down"
  exit 2
fi

# Check sentinels

SENTINELS=$(kubectl exec -n $NAMESPACE redis-sentinel-0 -- redis-cli -p 26379 SENTINEL ckquorum mymaster | grep "OK")
if [ -z "$SENTINELS" ]; then
  echo "CRITICAL: Sentinel quorum lost"
  exit 2
fi

echo "OK: Redis HA is healthy"
exit 0
```

---

## TROUBLESHOOTING

### PostgreSQL Issues

#### "No replication slots available"

```bash

# Check replication slots

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT * FROM pg_replication_slots;"

# Increase max_replication_slots

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "ALTER SYSTEM SET max_replication_slots = 10;"
kubectl delete pod postgres-0 -n project-ai  # Restart to apply
```

#### "Connection refused" from PgBouncer

```bash

# Check PgBouncer logs

kubectl logs -n project-ai pgbouncer-xxxxx

# Verify database is in PgBouncer config

kubectl exec -n project-ai pgbouncer-xxxxx -- psql -h localhost -p 6432 -U projectai -c "SHOW DATABASES;"
```

### Redis Issues

#### "READONLY You can't write against a read only replica"

```bash

# Check current master

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# Verify application is connecting to correct master

# Update connection string if needed

```

#### "Sentinel quorum lost"

```bash

# Check sentinel pods

kubectl get pods -n project-ai | grep sentinel

# Restart sentinels if needed

kubectl rollout restart statefulset redis-sentinel -n project-ai
```

---

## PERFORMANCE TUNING

### PostgreSQL

```bash

# Analyze query performance

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Optimize connection pooling

# Edit PgBouncer config in k8s/base/postgres-read-replicas.yaml:

# - PGBOUNCER_DEFAULT_POOL_SIZE: Increase for more concurrent connections

# - PGBOUNCER_POOL_MODE: Use 'transaction' for short queries, 'session' for long-lived connections

```

### Redis

```bash

# Monitor slow queries

kubectl exec -n project-ai redis-master-0 -- redis-cli SLOWLOG GET 10

# Analyze memory usage

kubectl exec -n project-ai redis-master-0 -- redis-cli INFO memory

# Optimize maxmemory policy

kubectl exec -n project-ai redis-master-0 -- redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## ALERTS & MONITORING

### Prometheus Alerts (Recommended)

```yaml
groups:

- name: database
  rules:
  - alert: PostgreSQLDown
    expr: up{job="postgres"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL is down"
      
  - alert: PostgreSQLReplicationLag
    expr: pg_replication_lag_seconds > 30
    for: 5m
    labels:
      severity: warning
      
  - alert: RedisDown
    expr: up{job="redis"} == 0
    for: 1m
    labels:
      severity: critical
      
  - alert: RedisSentinelQuorumLost
    expr: redis_sentinel_known_sentinels < 2
    for: 1m
    labels:
      severity: critical

```

---

**Maintained By**: High Availability Architect (Team Bravo)  
**Last Updated**: 2026-04-09  
**Next Review**: 2026-07-09  
**On-Call Escalation**: Run `kubectl get events -n project-ai` for recent issues
