# Deployment Playbook

**Sovereign Governance Substrate - Operational Procedures**

**Version:** 1.0  
**Last Updated:** 2026-04-09  
**Classification:** Operational Runbook

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Production Deployment](#2-production-deployment)
3. [Rollback Procedures](#3-rollback-procedures)
4. [Health Check Validation](#4-health-check-validation)
5. [Troubleshooting](#5-troubleshooting)
6. [Emergency Procedures](#6-emergency-procedures)
7. [Monitoring & Alerts](#7-monitoring--alerts)
8. [Database Operations](#8-database-operations)
9. [Configuration Management](#9-configuration-management)
10. [Post-Deployment Tasks](#10-post-deployment-tasks)

---

## 1. Prerequisites

### 1.1 Required Tools

Install the following tools before deployment:

```bash

# Kubernetes CLI

kubectl version --client

# Kustomize

kustomize version

# Docker

docker --version

# Helm (optional)

helm version

# Python 3.11+

python --version

# Git

git --version
```

### 1.2 Access Requirements

- **Kubernetes Cluster Access**: kubeconfig configured
- **Docker Registry Access**: Credentials for image push/pull
- **Database Access**: Connection string and credentials
- **Monitoring Access**: Prometheus, Grafana credentials
- **VPN/Network Access**: If required for cluster access

### 1.3 Pre-Deployment Checklist

```bash

# Run pre-deployment validation

python pre_deploy_check.py --environment production

# Verify cluster connectivity

kubectl cluster-info
kubectl get nodes

# Check namespace exists

kubectl get namespace project-ai-production || kubectl create namespace project-ai-production

# Verify secrets are configured

kubectl get secrets -n project-ai-production

# Check resource quotas

kubectl describe resourcequota -n project-ai-production
```

**Checklist:**

- [ ] All required tools installed
- [ ] Cluster access verified
- [ ] Namespace created
- [ ] Secrets configured
- [ ] Resource quotas sufficient
- [ ] Database accessible
- [ ] Monitoring stack operational
- [ ] Backup taken
- [ ] Change ticket approved
- [ ] Rollback plan prepared

---

## 2. Production Deployment

### 2.1 Standard Deployment (Rolling Update)

**Use Case:** Standard production updates with minimal risk

```bash

# Step 1: Run pre-deployment validation

python pre_deploy_check.py --environment production --comprehensive

# Step 2: Build and push Docker image

export IMAGE_TAG="v$(date +%Y%m%d-%H%M%S)"
docker build -t ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG} .
docker tag ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG} ghcr.io/iamsothirsty/project-ai:latest
docker push ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG}
docker push ghcr.io/iamsothirsty/project-ai:latest

# Step 3: Execute deployment

./deploy.sh production rolling ${IMAGE_TAG}

# Step 4: Monitor deployment

kubectl rollout status deployment/project-ai-app -n project-ai-production

# Step 5: Verify health

./deploy.sh production verify
```

**Expected Duration:** 5-10 minutes  
**Risk Level:** Low  
**Downtime:** Zero

### 2.2 Blue-Green Deployment

**Use Case:** Critical updates requiring instant rollback capability

```bash

# Step 1: Validate environment

python pre_deploy_check.py --environment production

# Step 2: Build image (same as above)

export IMAGE_TAG="v$(date +%Y%m%d-%H%M%S)"
docker build -t ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG} .
docker push ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG}

# Step 3: Execute blue-green deployment

cd k8s
./blue-green-deploy.sh project-ai-production ${IMAGE_TAG} blue-green

# The script will:

# - Deploy new version (green)

# - Wait for readiness

# - Run smoke tests

# - Prompt for traffic switch

# - Switch traffic

# - Verify serving

# - Optionally cleanup old version

# Step 4: Monitor metrics

# Watch Grafana dashboard for anomalies

# Check error rates, latency, throughput

```

**Expected Duration:** 10-15 minutes  
**Risk Level:** Very Low  
**Downtime:** Zero  
**Instant Rollback:** Available

### 2.3 Canary Deployment

**Use Case:** High-risk updates, gradual traffic shift

```bash

# Step 1: Deploy canary

cd k8s
./blue-green-deploy.sh project-ai-production ${IMAGE_TAG} canary

# The script will:

# - Deploy new version

# - Shift 10% traffic → wait 60s

# - Shift 50% traffic → wait 60s

# - Shift 100% traffic

# - Monitor metrics at each stage

# Step 2: Monitor during canary

# Watch error rates in Grafana

# If anomalies detected, rollback immediately

```

**Expected Duration:** 15-20 minutes  
**Risk Level:** Very Low  
**Downtime:** Zero  
**Progressive Validation:** Yes

### 2.4 Deployment Script Usage

```bash

# Standard deployment

./deploy.sh <environment> <strategy> [options]

# Examples:

./deploy.sh production rolling v1.2.3
./deploy.sh staging bluegreen
./deploy.sh production canary --traffic-split=20,50,100

# Options:

--dry-run              # Preview changes without applying
--skip-tests           # Skip smoke tests (not recommended)
--skip-migrations      # Skip database migrations
--no-cleanup           # Keep old deployment for manual cleanup
--timeout=600          # Deployment timeout in seconds
```

---

## 3. Rollback Procedures

### 3.1 Automatic Rollback Triggers

**The deployment automatically rolls back if:**

- Health checks fail after deployment
- Smoke tests fail
- Error rate exceeds threshold (5% increase)
- Startup timeout exceeded (5 minutes)

### 3.2 Manual Rollback

**Immediate Rollback (< 2 minutes):**

```bash

# Execute rollback script

./rollback.sh production

# The script will:

# 1. Identify previous stable version

# 2. Revert Kubernetes deployment

# 3. Rollback database migrations (if needed)

# 4. Restore configuration

# 5. Verify health

# 6. Update deployment status

# Verify rollback success

kubectl get deployment project-ai-app -n project-ai-production
kubectl get pods -n project-ai-production
```

**Blue-Green Instant Rollback:**

```bash

# If blue-green deployment was used and old version kept

kubectl patch service project-ai -n project-ai-production \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify traffic switched

curl https://api.example.com/health/live
```

**Kubernetes Native Rollback:**

```bash

# Rollback to previous revision

kubectl rollout undo deployment/project-ai-app -n project-ai-production

# Rollback to specific revision

kubectl rollout history deployment/project-ai-app -n project-ai-production
kubectl rollout undo deployment/project-ai-app -n project-ai-production --to-revision=3

# Monitor rollback

kubectl rollout status deployment/project-ai-app -n project-ai-production
```

### 3.3 Database Rollback

**If database migrations were applied:**

```bash

# Option 1: Automated rollback (via script)

./rollback.sh production --include-database

# Option 2: Manual Alembic rollback

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic downgrade -1

# Option 3: Restore from backup

./restore_database.sh production <backup-timestamp>
```

### 3.4 Rollback Verification

**Post-Rollback Checks:**

```bash

# 1. Verify pods running

kubectl get pods -n project-ai-production

# 2. Check health endpoints

curl https://api.example.com/health/live
curl https://api.example.com/health/ready

# 3. Check error logs

kubectl logs -n project-ai-production -l app.kubernetes.io/name=project-ai --tail=100

# 4. Verify metrics

# Check Grafana dashboard for:

# - Error rate normalized

# - Latency within SLA

# - Traffic serving normally

# 5. Run smoke tests

./deploy.sh production test
```

---

## 4. Health Check Validation

### 4.1 Health Endpoint Testing

```bash

# Get service endpoint

export API_ENDPOINT=$(kubectl get ingress -n project-ai-production \
  -o jsonpath='{.items[0].spec.rules[0].host}')

# Test liveness

curl -f https://${API_ENDPOINT}/health/live || echo "LIVENESS FAILED"

# Test readiness

curl -f https://${API_ENDPOINT}/health/ready || echo "READINESS FAILED"

# Test deep health

curl -s https://${API_ENDPOINT}/health | jq .

# Expected deep health response:

{
  "status": "healthy",
  "timestamp": "2026-04-09T12:00:00Z",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "temporal": "healthy",
    "filesystem": "healthy"
  },
  "metrics": {
    "uptime_seconds": 3600,
    "memory_usage_mb": 512,
    "cpu_usage_percent": 25
  }
}
```

### 4.2 Kubernetes Health Validation

```bash

# Check pod health

kubectl get pods -n project-ai-production -o wide

# Describe pod for detailed status

kubectl describe pod <pod-name> -n project-ai-production

# Check probe failures

kubectl get events -n project-ai-production --sort-by='.lastTimestamp' | grep -i "unhealthy\|failed"

# Monitor probe status in real-time

kubectl get pods -n project-ai-production -w
```

### 4.3 Dependency Health Checks

```bash

# Database connectivity

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -c "from sqlalchemy import create_engine; import os; \
  engine = create_engine(os.environ['DATABASE_URL']); \
  conn = engine.connect(); print('DB OK'); conn.close()"

# Redis connectivity

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -c "import redis; import os; \
  r = redis.Redis.from_url(os.environ['REDIS_URL']); \
  r.ping(); print('Redis OK')"

# Temporal connectivity

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -c "import os; print(f'Temporal: {os.environ[\"TEMPORAL_HOST\"]}')"
```

---

## 5. Troubleshooting

### 5.1 Deployment Failures

**Issue: Pods not starting**

```bash

# Check pod status

kubectl get pods -n project-ai-production

# Describe pod for events

kubectl describe pod <pod-name> -n project-ai-production

# Common causes:

# - Image pull errors: Check image tag and registry credentials

# - Resource limits: Check if node has sufficient resources

# - Init container failure: Check database connectivity

# - Config/Secret missing: Verify ConfigMap and Secrets exist

# Check init container logs

kubectl logs <pod-name> -n project-ai-production -c wait-for-db
kubectl logs <pod-name> -n project-ai-production -c db-migrations

# Check main container logs

kubectl logs <pod-name> -n project-ai-production -c project-ai
```

**Issue: Image pull errors**

```bash

# Check ImagePullSecrets

kubectl get secrets -n project-ai-production | grep docker

# Verify image exists in registry

docker pull ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG}

# Update image pull secret if needed

kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  --namespace=project-ai-production
```

**Issue: Database migration failures**

```bash

# Check migration logs

kubectl logs <pod-name> -n project-ai-production -c db-migrations

# Manually run migration (debugging)

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic upgrade head

# Check database connectivity

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  nc -zv postgres.project-ai-production.svc.cluster.local 5432
```

### 5.2 Performance Issues

**Issue: High latency**

```bash

# Check resource utilization

kubectl top pods -n project-ai-production
kubectl top nodes

# Check HPA status

kubectl get hpa -n project-ai-production
kubectl describe hpa project-ai-hpa -n project-ai-production

# Check for CPU/Memory throttling

kubectl describe pod <pod-name> -n project-ai-production | grep -A 5 "Limits"

# Scale manually if needed

kubectl scale deployment project-ai-app -n project-ai-production --replicas=5
```

**Issue: High error rate**

```bash

# Check application logs

kubectl logs -n project-ai-production -l app.kubernetes.io/name=project-ai \
  --tail=1000 | grep -i error

# Check metrics

curl -s https://${API_ENDPOINT}/metrics | grep error

# Check Prometheus

# Query: rate(http_requests_total{job="project-ai",status=~"5.."}[5m])

```

### 5.3 Network Issues

**Issue: Service unreachable**

```bash

# Check service

kubectl get svc -n project-ai-production
kubectl describe svc project-ai -n project-ai-production

# Check endpoints

kubectl get endpoints -n project-ai-production

# Check ingress

kubectl get ingress -n project-ai-production
kubectl describe ingress project-ai-ingress -n project-ai-production

# Test internal connectivity

kubectl run -it --rm debug --image=alpine --restart=Never -n project-ai-production -- sh

# Inside pod:

# apk add curl

# curl http://project-ai.project-ai-production.svc.cluster.local/health/live

```

**Issue: Network policy blocking**

```bash

# Check network policies

kubectl get networkpolicy -n project-ai-production
kubectl describe networkpolicy -n project-ai-production

# Temporarily disable for debugging (NOT PRODUCTION)

# kubectl delete networkpolicy <policy-name> -n project-ai-production

```

---

## 6. Emergency Procedures

### 6.1 Production Down (P0 Incident)

**Immediate Actions (< 5 minutes):**

1. **Alert Team**
   ```bash
   # Notify on-call team via PagerDuty/Slack
   # Escalate to team lead immediately
   ```

2. **Assess Situation**
   ```bash
   # Check pod status
   kubectl get pods -n project-ai-production
   
   # Check recent deployments

   kubectl rollout history deployment/project-ai-app -n project-ai-production
   
   # Check logs

   kubectl logs -n project-ai-production -l app.kubernetes.io/name=project-ai --tail=100
   ```

3. **Immediate Rollback** (if deployment-related)
   ```bash
   ./rollback.sh production
   # OR
   kubectl rollout undo deployment/project-ai-app -n project-ai-production
   ```

4. **Scale Up** (if capacity-related)
   ```bash
   kubectl scale deployment project-ai-app -n project-ai-production --replicas=10
   ```

5. **Verify Recovery**
   ```bash
   curl https://${API_ENDPOINT}/health/live
   ```

### 6.2 Database Issues

**Database Unavailable:**

```bash

# Check database pod/service

kubectl get pods -n project-ai-production | grep postgres
kubectl get svc -n project-ai-production | grep postgres

# Test connectivity

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  nc -zv postgres.project-ai-production.svc.cluster.local 5432

# Check database logs

kubectl logs -n project-ai-production postgres-0 --tail=100

# Restart database (last resort)

kubectl delete pod postgres-0 -n project-ai-production
```

**Database Corruption:**

```bash

# Immediate: Restore from backup

./restore_database.sh production latest

# Post-restore: Verify integrity

kubectl exec -it postgres-0 -n project-ai-production -- \
  psql -U postgres -d project_ai -c "SELECT COUNT(*) FROM users;"
```

### 6.3 Security Incident

**Suspected Breach:**

1. **Isolate**
   ```bash
   # Block external traffic
   kubectl scale deployment project-ai-app -n project-ai-production --replicas=0
   # OR apply restrictive network policy
   ```

2. **Preserve Evidence**
   ```bash
   # Collect logs
   kubectl logs -n project-ai-production --all-containers=true > incident-logs.txt
   
   # Snapshot pods

   kubectl get pods -n project-ai-production -o yaml > incident-pods.yaml
   ```

3. **Investigate**
   ```bash
   # Check audit logs
   kubectl logs -n kube-system kube-apiserver-* | grep project-ai-production
   
   # Check for unauthorized changes

   kubectl get events -n project-ai-production --sort-by='.lastTimestamp'
   ```

4. **Notify Security Team**
   - Escalate immediately
   - Do NOT destroy evidence

---

## 7. Monitoring & Alerts

### 7.1 Prometheus Queries

**Key Metrics to Monitor:**

```promql

# Request rate

rate(http_requests_total{namespace="project-ai-production"}[5m])

# Error rate

rate(http_requests_total{namespace="project-ai-production",status=~"5.."}[5m])

# Latency (95th percentile)

histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Pod restarts

rate(kube_pod_container_status_restarts_total{namespace="project-ai-production"}[15m]) > 0

# Memory usage

container_memory_usage_bytes{namespace="project-ai-production"} / container_spec_memory_limit_bytes{namespace="project-ai-production"} > 0.8

# CPU usage

rate(container_cpu_usage_seconds_total{namespace="project-ai-production"}[5m]) / container_spec_cpu_quota{namespace="project-ai-production"} > 0.8
```

### 7.2 Grafana Dashboards

**Pre-configured Dashboards:**

- **Application Overview**: Request rate, error rate, latency
- **Resource Utilization**: CPU, memory, disk, network
- **Deployment Status**: Replica count, availability, rollouts
- **Database Metrics**: Connections, query performance, replication lag
- **Custom Metrics**: AGI continuity scores, business metrics

**Access:**
```
URL: https://grafana.example.com
Username: admin
Dashboard: "Project-AI Production"
```

### 7.3 Alert Rules

**Critical Alerts (P0):**

- Application down (all pods unavailable)
- Database unreachable
- Error rate > 10%
- Latency P95 > 5s

**High-Priority Alerts (P1):**

- Pod restarts > 5/hour
- Memory usage > 90%
- CPU usage > 90%
- Disk usage > 85%
- Error rate > 5%

**Medium-Priority Alerts (P2):**

- HPA maxed out
- Certificate expiring (< 7 days)
- Backup failures

---

## 8. Database Operations

### 8.1 Backup Procedures

**Automated Backups:**
```bash

# Backups run daily via CronJob

kubectl get cronjob -n project-ai-production

# Manual backup

kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%Y%m%d-%H%M%S) \
  -n project-ai-production

# Verify backup

kubectl logs job/manual-backup-<timestamp> -n project-ai-production
```

**Backup to S3:**
```bash

# Using pg_dump

kubectl exec -it postgres-0 -n project-ai-production -- \
  pg_dump -U postgres -d project_ai | \
  aws s3 cp - s3://backups/project-ai/db-$(date +%Y%m%d-%H%M%S).sql
```

### 8.2 Restore Procedures

**Restore from Backup:**
```bash

# List available backups

aws s3 ls s3://backups/project-ai/ | grep db-

# Download backup

aws s3 cp s3://backups/project-ai/db-20260409-120000.sql ./restore.sql

# Restore (WARNING: This will overwrite existing data)

kubectl exec -i postgres-0 -n project-ai-production -- \
  psql -U postgres -d project_ai < ./restore.sql

# Verify restore

kubectl exec -it postgres-0 -n project-ai-production -- \
  psql -U postgres -d project_ai -c "SELECT NOW();"
```

### 8.3 Migration Management

**Apply Migrations:**
```bash

# Migrations run automatically in init container

# Manual migration:

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic upgrade head

# Check current version

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic current

# Migration history

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic history
```

**Rollback Migration:**
```bash

# Rollback one version

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic downgrade -1

# Rollback to specific version

kubectl exec -it deployment/project-ai-app -n project-ai-production -- \
  python -m alembic downgrade <revision>
```

---

## 9. Configuration Management

### 9.1 ConfigMap Updates

**Update ConfigMap:**
```bash

# Edit ConfigMap

kubectl edit configmap project-ai-config -n project-ai-production

# OR update from file

kubectl create configmap project-ai-config \
  --from-file=config/ \
  --dry-run=client -o yaml | \
  kubectl apply -f - -n project-ai-production

# Restart pods to pick up changes

kubectl rollout restart deployment/project-ai-app -n project-ai-production
```

### 9.2 Secret Updates

**Update Secrets:**
```bash

# Update secret

kubectl create secret generic project-ai-secrets \
  --from-literal=database-password='[REDACTED]' \
  --dry-run=client -o yaml | \
  kubectl apply -f - -n project-ai-production

# Restart pods

kubectl rollout restart deployment/project-ai-app -n project-ai-production
```

**Secret Rotation:**
```bash

# Rotate database password

# 1. Update database password in database

# 2. Update secret

# 3. Restart pods (rolling restart ensures zero downtime)

```

---

## 10. Post-Deployment Tasks

### 10.1 Validation

**30-Minute Post-Deployment:**
```bash

# Check error rates

# Expected: < 1% errors

# Check latency

# Expected: P95 < 500ms

# Check resource utilization

kubectl top pods -n project-ai-production

# Expected: Memory < 70%, CPU < 60%

# Check logs for anomalies

kubectl logs -n project-ai-production -l app.kubernetes.io/name=project-ai \
  --since=30m | grep -i error | wc -l

# Expected: < 10 errors

```

### 10.2 Documentation

**Update Documentation:**

- [ ] Update CHANGELOG.md with deployment notes
- [ ] Document any issues encountered
- [ ] Update runbook with lessons learned
- [ ] Close change ticket with outcome

**Deployment Record:**
```yaml
Deployment Date: 2026-04-09
Deployment Time: 12:00 UTC
Version Deployed: v1.2.3
Deployment Strategy: Blue-Green
Deployed By: operator@example.com
Change Ticket: CHG-12345
Rollback Plan: Available (previous version: v1.2.2)
Issues: None
Outcome: Success
```

### 10.3 Cleanup

**Remove Old Resources:**
```bash

# Clean up old ReplicaSets

kubectl delete replicaset -n project-ai-production \
  $(kubectl get rs -n project-ai-production -o jsonpath='{.items[?(@.spec.replicas==0)].metadata.name}')

# Clean up completed jobs

kubectl delete job -n project-ai-production --field-selector status.successful=1

# Clean up old deployments (blue-green)

# Only after verifying new version is stable (24+ hours)

kubectl delete deployment project-ai-blue -n project-ai-production
```

---

## Appendix A: Quick Reference

### Common Commands

```bash

# Get pod status

kubectl get pods -n project-ai-production

# Get deployment status

kubectl get deployment -n project-ai-production

# View logs

kubectl logs -n project-ai-production -l app.kubernetes.io/name=project-ai --tail=100

# Check health

curl https://api.example.com/health/live

# Rollback

./rollback.sh production

# Scale

kubectl scale deployment project-ai-app -n project-ai-production --replicas=5

# Restart

kubectl rollout restart deployment/project-ai-app -n project-ai-production
```

### Emergency Contacts

- **On-Call Engineer**: Pager: +1-XXX-XXX-XXXX
- **Team Lead**: Slack: @team-lead
- **Engineering Manager**: Email: manager@example.com
- **CTO**: Phone: +1-XXX-XXX-XXXX

### Support Resources

- **Runbooks**: https://wiki.example.com/runbooks
- **Monitoring**: https://grafana.example.com
- **Logs**: https://logs.example.com
- **Chat**: #project-ai-ops (Slack)

---

**End of Deployment Playbook**

**Version:** 1.0  
**Last Updated:** 2026-04-09  
**Maintained By:** DevOps Team  
**Review Schedule:** Monthly
