# Scaling Playbook

## Operational Guide for Horizontal and Vertical Scaling

**Version:** 1.0  
**Last Updated:** 2026-03-03  
**Owner:** Platform Team

---

## Table of Contents

1. [Daily Operations](#1-daily-operations)
2. [Scaling Procedures](#2-scaling-procedures)
3. [Troubleshooting](#3-troubleshooting)
4. [Emergency Procedures](#4-emergency-procedures)
5. [Monitoring Checklists](#5-monitoring-checklists)

---

## 1. Daily Operations

### 1.1 Morning Health Check

**Every morning, verify:**

```bash

# Check HPA status

kubectl get hpa -n project-ai

# Expected output: All HPAs with TARGETS showing current/target

# Example: 45%/70% means healthy, 85%/70% means scaling up

# Check pod health

kubectl get pods -n project-ai

# Expected: All pods Running or Completed

# Check resource usage

kubectl top nodes
kubectl top pods -n project-ai --sort-by=cpu
kubectl top pods -n project-ai --sort-by=memory

# Check for pending pods (indicates resource constraints)

kubectl get pods -n project-ai --field-selector=status.phase=Pending

# Review recent HPA events

kubectl get events -n project-ai --sort-by='.lastTimestamp' | grep HorizontalPodAutoscaler
```

### 1.2 Resource Quota Check

```bash

# Check quota usage

kubectl describe resourcequota -n project-ai
kubectl describe resourcequota -n project-ai-staging
kubectl describe resourcequota -n project-ai-dev

# Alert if usage > 80% of quota

```

### 1.3 Database Health

```bash

# Check PostgreSQL replication lag

kubectl exec -n project-ai postgres-0 -- psql -U projectai -c "SELECT * FROM pg_stat_replication;"

# Check Redis Sentinel status

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL masters

# Check PgBouncer connections

kubectl exec -n project-ai pgbouncer-0 -- psql -h localhost -p 6432 -U pgbouncer pgbouncer -c "SHOW POOLS;"
```

---

## 2. Scaling Procedures

### 2.1 Manual Scale-Up (Emergency)

**When to use:** Immediate traffic spike, HPA not scaling fast enough

```bash

# Scale specific deployment

kubectl scale deployment <deployment-name> --replicas=<count> -n project-ai

# Examples:

kubectl scale deployment project-ai-app --replicas=10 -n project-ai
kubectl scale deployment mutation-firewall --replicas=15 -n project-ai
kubectl scale deployment temporal-worker --replicas=20 -n project-ai

# Verify scaling

kubectl get deployment <deployment-name> -n project-ai -w
```

**Rollback:**
```bash

# Let HPA manage again (it will scale down based on policy)

# Or manually scale back:

kubectl scale deployment <deployment-name> --replicas=<original-count> -n project-ai
```

### 2.2 Manual Scale-Down (Cost Optimization)

**When to use:** Off-peak hours, maintenance windows

```bash

# Temporary scale down (HPA will override if load increases)

kubectl scale deployment <deployment-name> --replicas=<count> -n project-ai

# For longer maintenance, disable HPA:

kubectl patch hpa <hpa-name> -n project-ai -p '{"spec":{"minReplicas":1}}'

# After maintenance, restore:

kubectl patch hpa <hpa-name> -n project-ai -p '{"spec":{"minReplicas":3}}'
```

### 2.3 Adjust HPA Thresholds

**When to use:** Metrics show HPA is too aggressive or too slow

```bash

# Edit HPA interactively

kubectl edit hpa <hpa-name> -n project-ai

# Or apply updated HPA file

kubectl apply -f k8s/base/hpa.yaml
kubectl apply -f k8s/emergent-services/hpa-microservices.yaml
```

**Common Adjustments:**

```yaml

# Make scaling more aggressive (faster response)

spec:
  metrics:

  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 60  # Lower threshold = earlier scaling

# Make scaling less aggressive (cost optimization)

spec:
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60  # Wait longer before scaling up
```

### 2.4 Add Database Read Replicas

**When to use:** Read queries causing primary database load

```bash

# Scale read replica StatefulSet

kubectl scale statefulset postgres-read-replica --replicas=4 -n project-ai

# Verify replication status

kubectl exec -n project-ai postgres-0 -- \
  psql -U projectai -c "SELECT * FROM pg_stat_replication;"

# Update application to use read replicas

# Point read-only queries to: postgres-read-replica.project-ai.svc.cluster.local

```

### 2.5 Scale Redis Slaves

**When to use:** Cache read load is high

```bash

# Scale Redis slaves

kubectl scale statefulset redis-slave --replicas=4 -n project-ai

# Verify replication

kubectl exec -n project-ai redis-master-0 -- redis-cli INFO replication

# Applications automatically use redis-read service for read operations

```

### 2.6 Node Pool Scaling

**When to use:** Cluster autoscaler not responding fast enough

**GKE:**
```bash

# Scale node pool manually

gcloud container clusters resize <cluster-name> \
  --node-pool <pool-name> \
  --num-nodes <count> \
  --region <region>

# Example:

gcloud container clusters resize sovereign-cluster \
  --node-pool general-pool \
  --num-nodes 10 \
  --region us-central1
```

**AWS EKS:**
```bash

# Update Auto Scaling Group

aws autoscaling set-desired-capacity \
  --auto-scaling-group-name <asg-name> \
  --desired-capacity <count>
```

**Azure AKS:**
```bash

# Scale node pool

az aks nodepool scale \
  --cluster-name <cluster-name> \
  --name <nodepool-name> \
  --resource-group <rg-name> \
  --node-count <count>
```

---

## 3. Troubleshooting

### 3.1 HPA Not Scaling

**Symptoms:** High CPU/memory but HPA not adding pods

**Diagnosis:**
```bash

# Check HPA status

kubectl describe hpa <hpa-name> -n project-ai

# Look for errors in conditions or events

# Common issues:

# - "unable to get metrics" - metrics-server not running

# - "FailedGetResourceMetric" - resource requests not defined

# - "ScalingLimited" - hit maxReplicas limit

```

**Solutions:**

1. **Metrics-server not responding:**

```bash
kubectl get pods -n kube-system | grep metrics-server

# If not running, reinstall:

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

2. **Missing resource requests:**

```bash

# Resource requests must be defined for HPA to work

kubectl get deployment <name> -n project-ai -o yaml | grep -A 5 resources

# If empty, update deployment with resource requests

```

3. **Hit maxReplicas:**

```bash

# Increase maxReplicas

kubectl patch hpa <hpa-name> -n project-ai -p '{"spec":{"maxReplicas":20}}'
```

### 3.2 Pods Stuck in Pending

**Symptoms:** New pods created but never start

**Diagnosis:**
```bash

# Check pod status

kubectl describe pod <pod-name> -n project-ai

# Look for events:

# - "Insufficient cpu" - need more nodes

# - "Insufficient memory" - need more nodes

# - "FailedScheduling" - taints/tolerations mismatch

# - "PersistentVolumeClaim not found" - storage issue

```

**Solutions:**

1. **Resource constraints:**

```bash

# Check cluster capacity

kubectl describe nodes | grep -A 5 "Allocated resources"

# Trigger cluster autoscaler or add nodes manually

# See section 2.6

```

2. **Node selector/affinity issues:**

```bash

# Check if pods require specific node labels

kubectl get pod <pod-name> -n project-ai -o yaml | grep -A 10 nodeSelector

# Add label to nodes or remove constraint

```

3. **PVC issues:**

```bash

# Check PVC status

kubectl get pvc -n project-ai

# If Pending, check StorageClass

kubectl get storageclass
```

### 3.3 Database Replication Lag

**Symptoms:** Read replicas behind primary

**Diagnosis:**
```bash

# Check replication lag

kubectl exec -n project-ai postgres-0 -- \
  psql -U projectai -c "SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;"

# Check replica logs

kubectl logs -n project-ai postgres-read-replica-0
```

**Solutions:**

1. **Network issues:**

```bash

# Test connectivity

kubectl exec -n project-ai postgres-read-replica-0 -- nc -zv postgres.project-ai.svc.cluster.local 5432
```

2. **Replica overwhelmed:**

```bash

# Scale up replica resources

kubectl edit statefulset postgres-read-replica -n project-ai

# Increase CPU/memory limits

```

3. **WAL shipping issues:**

```bash

# Check primary WAL status

kubectl exec -n project-ai postgres-0 -- \
  psql -U projectai -c "SELECT * FROM pg_stat_archiver;"
```

### 3.4 Redis Failover Issues

**Symptoms:** Redis master unavailable but no failover

**Diagnosis:**
```bash

# Check Sentinel status

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL masters

# Check quorum

kubectl exec -n project-ai redis-sentinel-0 -- redis-cli -p 26379 SENTINEL ckquorum mymaster

# Check Sentinel logs

kubectl logs -n project-ai redis-sentinel-0
```

**Solutions:**

1. **Quorum not reached:**

```bash

# Ensure at least 2 of 3 sentinels are running

kubectl get pods -n project-ai -l app.kubernetes.io/component=sentinel

# If < 2, investigate pod issues

```

2. **Manual failover:**

```bash

# Force failover to specific slave

kubectl exec -n project-ai redis-sentinel-0 -- \
  redis-cli -p 26379 SENTINEL failover mymaster
```

### 3.5 Cluster Autoscaler Not Scaling

**Symptoms:** Pending pods but no new nodes

**Diagnosis:**
```bash

# Check cluster autoscaler logs

kubectl logs -f deployment/cluster-autoscaler -n kube-system

# Look for:

# - "scale up not possible" - hit max nodes or quota

# - "failed to increase node group" - cloud provider issue

# - "unschedulable pods" - confirms autoscaler sees demand

```

**Solutions:**

1. **Hit node pool limits:**

```bash

# Check cloud provider console for node pool max size

# Increase if needed through cloud provider UI or CLI

```

2. **Quota limits:**

```bash

# Check cloud provider quotas

# Request increase if needed

```

3. **Autoscaler misconfigured:**

```bash

# Verify autoscaler has correct permissions

kubectl describe deployment cluster-autoscaler -n kube-system
```

---

## 4. Emergency Procedures

### 4.1 Traffic Spike (Immediate Action Required)

**Scenario:** Unexpected 10x traffic increase

**Immediate Actions (< 5 minutes):**

```bash

# 1. Scale critical services immediately

kubectl scale deployment project-ai-app --replicas=10 -n project-ai
kubectl scale deployment mutation-firewall --replicas=15 -n project-ai
kubectl scale deployment temporal-worker --replicas=20 -n project-ai

# 2. Scale PgBouncer for database connections

kubectl scale deployment pgbouncer --replicas=6 -n project-ai

# 3. Monitor scaling

watch kubectl get pods -n project-ai

# 4. Add nodes if cluster at capacity (GKE example)

gcloud container clusters resize sovereign-cluster \
  --node-pool general-pool \
  --num-nodes 15 \
  --region us-central1 \
  --async
```

**Follow-up (5-15 minutes):**

```bash

# 5. Check application health

kubectl get pods -n project-ai | grep -v Running

# 6. Monitor resource usage

kubectl top pods -n project-ai
kubectl top nodes

# 7. Check error rates in Grafana/Prometheus

# Alert if error rate > 1%

```

**Recovery (15-60 minutes):**

```bash

# 8. Let HPA take over once stable

# HPA will automatically scale down when load decreases

# 9. Review logs for root cause

kubectl logs -n project-ai deployment/project-ai-app --tail=1000

# 10. Document incident

# Add to incident log with timeline, actions, impact

```

### 4.2 Database Failure

**Scenario:** Primary PostgreSQL database unavailable

**Immediate Actions:**

```bash

# 1. Check database status

kubectl get pods -n project-ai -l app.kubernetes.io/name=postgres

# 2. If pod crashed, check logs

kubectl logs -n project-ai postgres-0 --previous

# 3. Promote read replica to primary (manual process)

# WARNING: This is destructive - only if primary unrecoverable

# First, scale down applications to prevent writes

kubectl scale deployment project-ai-app --replicas=0 -n project-ai

# Promote replica (execute in replica pod)

kubectl exec -n project-ai postgres-read-replica-0 -- \
  pg_ctl promote -D /var/lib/postgresql/data/pgdata

# Update application config to point to new primary

# Update DNS or service endpoint

# 4. Restore application traffic

kubectl scale deployment project-ai-app --replicas=3 -n project-ai
```

### 4.3 Redis Failure

**Scenario:** Redis master down

**Immediate Actions:**

```bash

# 1. Check Redis status

kubectl get pods -n project-ai -l app.kubernetes.io/name=redis

# 2. Sentinel should auto-failover

# Verify new master

kubectl exec -n project-ai redis-sentinel-0 -- \
  redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

# 3. If failover didn't happen, manual failover

kubectl exec -n project-ai redis-sentinel-0 -- \
  redis-cli -p 26379 SENTINEL failover mymaster

# 4. Verify application can connect

kubectl exec -n project-ai project-ai-app-0 -- \
  redis-cli -h redis-master.project-ai.svc.cluster.local ping
```

### 4.4 Out of Cluster Resources

**Scenario:** All pods pending, no nodes available

**Immediate Actions:**

```bash

# 1. Add nodes immediately (bypass autoscaler)

# GKE:

gcloud container clusters resize sovereign-cluster \
  --node-pool general-pool \
  --num-nodes 20 \
  --region us-central1

# AWS:

aws autoscaling set-desired-capacity \
  --auto-scaling-group-name <asg> \
  --desired-capacity 20

# 2. Monitor node creation

kubectl get nodes -w

# 3. Once nodes ready, pods should schedule

kubectl get pods -n project-ai

# 4. Investigate why autoscaler didn't scale

kubectl logs deployment/cluster-autoscaler -n kube-system --tail=200
```

---

## 5. Monitoring Checklists

### 5.1 Daily Checklist

- [ ] All HPAs showing healthy targets (< 85% of threshold)
- [ ] No pods in Pending or CrashLoopBackOff state
- [ ] Resource quota usage < 80%
- [ ] Database replication lag < 5 seconds
- [ ] Redis Sentinel showing 3 sentinels
- [ ] Cluster autoscaler logs show no errors
- [ ] No nodes in NotReady state

### 5.2 Weekly Checklist

- [ ] Review VPA recommendations and apply if beneficial
- [ ] Review HPA scaling events for patterns
- [ ] Check for resource over/under-provisioning
- [ ] Review cluster autoscaler scale events
- [ ] Verify backup and disaster recovery procedures
- [ ] Run load test to validate auto-scaling
- [ ] Review and update resource quotas if needed

### 5.3 Monthly Checklist

- [ ] Analyze cost trends and optimize
- [ ] Review and update HPA thresholds based on data
- [ ] Update resource requests/limits based on VPA
- [ ] Review node pool configurations
- [ ] Audit and clean up unused PVCs
- [ ] Update scaling documentation
- [ ] Conduct chaos engineering test
- [ ] Review and update runbooks

---

## 6. Contacts and Escalation

### 6.1 On-Call Rotation

- **Primary:** Platform Engineering Team
- **Secondary:** SRE Team
- **Escalation:** VP Engineering

### 6.2 Escalation Criteria

**Escalate immediately if:**

- Error rate > 5% for > 5 minutes
- Database down for > 2 minutes
- Critical service unavailable for > 2 minutes
- Security breach detected
- Data loss detected

**Escalate within 1 hour if:**

- Degraded performance for > 30 minutes
- Scaling issues causing user impact
- Resource quota exhausted
- Multiple failed deployments

---

## Appendix: Quick Reference Commands

```bash

# Scale deployment

kubectl scale deployment <name> --replicas=<count> -n project-ai

# Check HPA

kubectl get hpa -n project-ai
kubectl describe hpa <name> -n project-ai

# Check resource usage

kubectl top nodes
kubectl top pods -n project-ai

# Check pod status

kubectl get pods -n project-ai
kubectl describe pod <name> -n project-ai

# Check logs

kubectl logs -n project-ai <pod-name>
kubectl logs -n project-ai <pod-name> --previous

# Execute command in pod

kubectl exec -n project-ai <pod-name> -- <command>

# Port forward for debugging

kubectl port-forward -n project-ai <pod-name> 8080:8080

# Check events

kubectl get events -n project-ai --sort-by='.lastTimestamp'

# Check node resources

kubectl describe node <node-name>
```

---

**Playbook Version:** 1.0  
**Last Updated:** 2026-03-03  
**Next Review:** 2026-04-03
