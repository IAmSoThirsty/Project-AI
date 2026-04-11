# Database Failover Runbook

**Team Charlie - SRE Documentation Lead**



## Overview

This runbook covers PostgreSQL primary database failover procedures for the Sovereign Governance Substrate.



## Prerequisites

- Access to Kubernetes cluster
- PostgreSQL admin credentials
- Monitoring dashboards accessible



## Architecture

```
┌─────────────┐
│  Primary DB │ (Write + Read)
│  postgres-0 │
└──────┬──────┘
       │ Streaming Replication
       ▼
┌─────────────┐
│ Standby DB  │ (Read-only)
│ postgres-1  │
└─────────────┘
```



## Failure Detection



### Automated Alerts

- **Alert**: `PostgreSQLDown`
- **Threshold**: Primary unreachable for >30 seconds
- **PagerDuty**: Auto-escalates to on-call DBA



### Manual Detection

```bash

# Check pod status

kubectl get pods -l app=postgresql -n default



# Test primary connectivity

kubectl exec -n default postgresql-0 -- pg_isready



# Check replication status

kubectl exec -n default postgresql-0 -- \
  psql -U sovereign -c "SELECT * FROM pg_stat_replication;"
```



## Failover Procedure



### Step 1: Confirm Primary Failure (1 minute)

```bash

# Verify primary is truly down (not just network blip)

for i in {1..5}; do
  kubectl exec -n default postgresql-0 -- pg_isready
  sleep 2
done



# Check pod logs

kubectl logs -n default postgresql-0 --tail=50



# Verify standby is healthy

kubectl exec -n default postgresql-1 -- pg_isready
```



### Step 2: Promote Standby to Primary (2 minutes)

```bash

# Promote standby

kubectl exec -n default postgresql-1 -- \
  su - postgres -c "pg_ctl promote -D /var/lib/postgresql/data"



# Verify promotion

kubectl exec -n default postgresql-1 -- \
  psql -U sovereign -c "SELECT pg_is_in_recovery();"


# Should return: f (false = not in recovery = primary)



# Update service to point to new primary

kubectl patch service postgresql -n default -p \
  '{"spec":{"selector":{"statefulset.kubernetes.io/pod-name":"postgresql-1"}}}'
```



### Step 3: Verify Applications Reconnect (2 minutes)

```bash

# Check application logs for reconnection

kubectl logs -n default -l app=sovereign-vault --tail=100 | grep -i "database\|connection"



# Run health checks

for svc in firewall vault trust-graph compliance incident-reflex; do
  kubectl exec -n default deploy/$svc -- \
    curl -f http://localhost:8000/api/v1/health/readiness
done
```



### Step 4: Rebuild Failed Primary as New Standby (10 minutes)

```bash

# Delete failed primary pod

kubectl delete pod postgresql-0 -n default



# Wait for pod recreation

kubectl wait --for=condition=Ready pod/postgresql-0 -n default --timeout=300s



# Configure as standby (basebackup from new primary)

kubectl exec -n default postgresql-0 -- \
  su - postgres -c "pg_basebackup -h postgresql-1 -D /var/lib/postgresql/data -U replication -Fp -Xs -P -R"



# Restart as standby

kubectl delete pod postgresql-0 -n default
kubectl wait --for=condition=Ready pod/postgresql-0 -n default --timeout=180s



# Verify replication

kubectl exec -n default postgresql-1 -- \
  psql -U sovereign -c "SELECT * FROM pg_stat_replication;"
```



### Step 5: Post-Failover Validation (5 minutes)

```bash

# Test write operations

kubectl exec -n default postgresql-1 -- \
  psql -U sovereign -d sovereign_db -c \
  "CREATE TABLE failover_test (id SERIAL, ts TIMESTAMP DEFAULT NOW());"

kubectl exec -n default postgresql-1 -- \
  psql -U sovereign -d sovereign_db -c \
  "INSERT INTO failover_test DEFAULT VALUES;"



# Verify replication to standby

sleep 5
kubectl exec -n default postgresql-0 -- \
  psql -U sovereign -d sovereign_db -c \
  "SELECT * FROM failover_test;"



# Clean up test table

kubectl exec -n default postgresql-1 -- \
  psql -U sovereign -d sovereign_db -c \
  "DROP TABLE failover_test;"



# Run E2E smoke tests

pytest tests/e2e/test_smoke.py -v
```



## Rollback Procedure

If failover causes issues:
```bash

# Demote current primary back to standby

kubectl exec -n default postgresql-1 -- \
  su - postgres -c "pg_ctl stop -D /var/lib/postgresql/data -m fast"



# Promote original primary

kubectl exec -n default postgresql-0 -- \
  su - postgres -c "pg_ctl promote -D /var/lib/postgresql/data"



# Revert service

kubectl patch service postgresql -n default -p \
  '{"spec":{"selector":{"statefulset.kubernetes.io/pod-name":"postgresql-0"}}}'
```



## Communication Template

```
📊 Database Failover in Progress

Time: [HH:MM UTC]
Status: [In Progress / Complete]
Impact: [Brief user-facing impact]

Actions taken:

- [timestamp] Primary failure detected
- [timestamp] Standby promoted to primary
- [timestamp] Applications reconnected
- [timestamp] Validation complete

Next steps:

- [Action item 1]
- [Action item 2]

ETA for full recovery: [X minutes]
```



## Common Issues



### Issue: Standby promotion fails

```bash

# Check replication lag

kubectl exec -n default postgresql-0 -- \
  psql -U sovereign -c "SELECT pg_last_wal_receive_lsn() - pg_last_wal_replay_lsn() AS lag;"



# If lag is high, wait for catch-up before promoting

```



### Issue: Split-brain (both think they're primary)

```bash

# DANGER: This is serious. Fence old primary immediately.

kubectl scale statefulset postgresql --replicas=0 -n default


# Then scale back up and rebuild from scratch

```



## Performance Impact

- **Failover Time**: ~3-5 minutes
- **Data Loss**: 0 (synchronous replication)
- **Downtime**: ~30 seconds (application reconnect time)



## Monitoring Queries

```sql
-- Check replication lag
SELECT
  client_addr,
  state,
  pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS sending_lag,
  pg_wal_lsn_diff(pg_current_wal_lsn(), write_lsn) AS write_lag,
  pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag
FROM pg_stat_replication;

-- Check database size
SELECT
  pg_database.datname,
  pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database;
```



## Related Runbooks

- [Incident Response Playbook](../playbooks/INCIDENT_RESPONSE.md)
- [Disaster Recovery](./disaster-recovery-runbook.md)
- [Backup & Restore](./backup-restore-runbook.md)

---
**Last Updated**: 2025-01-15  
**Owner**: Team Charlie - SRE  
**Review Cycle**: Quarterly
