# Incident Response Playbook

## Purpose

Comprehensive incident response procedures for the Sovereign Governance Substrate platform, based on the Autonomous Incident Reflex System API. Includes detection, escalation, containment, and recovery procedures for various incident types.

## Incident Classification

### Severity Levels

| Severity | RTO | Impact | Examples | Escalation |
|----------|-----|--------|----------|------------|
| **P0 - Critical** | 15 min | Complete outage, data loss, security breach | Database down, all services unavailable, active attack | Immediate - Page on-call, notify leadership |
| **P1 - High** | 1 hour | Major functionality impaired, significant performance degradation | Primary service down, major bug affecting 50%+ users | Immediate - Page on-call engineer |
| **P2 - Medium** | 4 hours | Minor functionality impaired, some users affected | Single microservice down, degraded performance | Normal - Assign to on-call queue |
| **P3 - Low** | 1 day | Low impact, workaround available | Minor bugs, cosmetic issues | Normal - Schedule for next sprint |

### Incident Types

1. **Infrastructure Failure** - Server, network, or cloud provider issues
2. **Application Error** - Code bugs, crashes, exceptions
3. **Performance Degradation** - Slow response times, resource exhaustion
4. **Security Incident** - Unauthorized access, data breach, DDoS attack
5. **Data Integrity** - Data corruption, inconsistencies
6. **External Dependency** - Third-party API failures
7. **Configuration Error** - Misconfiguration causing issues

---

## Incident Detection

### Automated Detection

#### Health Check Failures

```bash

# Main application health check

curl -f http://localhost:8000/health || echo "ALERT: Main application unhealthy"

# All microservices health check

for port in {8011..8018}; do
  curl -sf http://localhost:$port/api/v1/health/liveness || \
    echo "ALERT: Service on port $port unhealthy"
done

# Kubernetes health check

kubectl get pods -n production | grep -v Running
```

#### Monitoring Alerts

- **Prometheus Alertmanager**: Monitor alert dashboard at http://localhost:9093
- **Grafana Alerts**: Check dashboard for triggered alerts
- **Log-based alerts**: Error rate threshold exceeded

#### Key Metrics to Monitor

```promql

# High error rate (>5% for 5 minutes)

rate(http_requests_failed_total[5m]) / rate(http_requests_total[5m]) > 0.05

# High latency (>1s p99 for 5 minutes)

histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1

# Pod crash loops

kube_pod_container_status_restarts_total > 5

# High CPU usage (>80% for 10 minutes)

container_cpu_usage_seconds_total > 0.8

# High memory usage (>90% for 5 minutes)

container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9

# Database connection pool exhaustion

db_pool_connections_active / db_pool_connections_max > 0.9
```

### Manual Detection

#### User Reports

- Support ticket system
- Email alerts
- Direct customer reports

#### Incident Reporting API

```bash

# Report incident via API

curl -X POST http://localhost:8012/api/v1/incidents \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "title": "High error rate on API endpoint",
    "description": "Users reporting 500 errors on /api/v1/policies",
    "severity": "high",
    "source": "manual_report",
    "affected_component": "api-gateway",
    "impact": {
      "user_count": 500,
      "services": ["mutation-firewall"]
    }
  }'
```

---

## Incident Response Process

### Step 1: Acknowledge (Within 5 minutes)

#### Acknowledge Incident

```bash

# Via Incident Reflex API

curl -X PATCH http://localhost:8012/api/v1/incidents/{incident_id} \
  -H "X-API-Key: ${API_KEY}" \
  -d '{"status": "investigating", "assigned_to": "oncall-engineer"}'

# Via Alertmanager

curl -X POST http://localhost:9093/api/v1/silences \
  -d '{
    "matchers": [{"name":"alertname","value":"HighErrorRate","isRegex":false}],
    "startsAt":"2026-04-09T10:00:00Z",
    "endsAt":"2026-04-09T12:00:00Z",
    "comment":"Investigating - acknowledged by oncall"
  }'
```

#### Notify Team

```bash

# Post to incident channel (Slack/Teams)

# Include:

# - Incident ID

# - Severity

# - Initial assessment

# - Assigned responder

# Example Slack notification

curl -X POST ${SLACK_WEBHOOK_URL} \
  -d '{
    "text": "🚨 P1 Incident: High error rate on API gateway",
    "attachments": [{
      "color": "danger",
      "fields": [
        {"title":"Incident ID","value":"INC-20260409-001","short":true},
        {"title":"Severity","value":"P1 - High","short":true},
        {"title":"Assigned","value":"@oncall-engineer","short":true},
        {"title":"Link","value":"http://incident-dashboard/INC-20260409-001","short":true}
      ]
    }]
  }'
```

### Step 2: Assess Impact (Within 15 minutes)

#### Check Service Status

```bash

# Check all services

docker-compose ps
kubectl get pods -n ${NAMESPACE}

# Check metrics

curl http://localhost:9090/api/v1/query?query=up{job="project-ai"}

# Check error rates

curl http://localhost:9090/api/v1/query?query=rate(http_requests_failed_total[5m])
```

#### Identify Affected Components

```bash

# View incident details

curl http://localhost:8012/api/v1/incidents/{incident_id} \
  -H "X-API-Key: ${API_KEY}"

# Check logs for errors

docker-compose logs --tail=100 | grep ERROR
kubectl logs -l app=project-ai -n ${NAMESPACE} --tail=100 | grep ERROR

# Check recent deployments

kubectl rollout history deployment/project-ai-app -n ${NAMESPACE}
git log --oneline -10
```

#### Determine Blast Radius

```bash

# Count affected users (from logs)

docker-compose logs | grep "user_id" | cut -d'"' -f4 | sort -u | wc -l

# Check traffic patterns

curl "http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m])"

# Identify degraded services

for port in {8011..8018}; do
  response_time=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:$port/api/v1/health/liveness)
  echo "Port $port: ${response_time}s"
done
```

### Step 3: Contain (Within 30 minutes)

#### Immediate Containment Actions

**For Security Incidents:**
```bash

# Block suspicious IP addresses

# Update network policy

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-suspicious-ips
spec:
  podSelector:
    matchLabels:
      app: project-ai
  policyTypes:

  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 192.168.1.100/32  # Suspicious IP

EOF

# Rotate compromised credentials

./emergency-rotate-secrets.sh

# Enable additional logging

kubectl set env deployment/project-ai-app LOG_LEVEL=DEBUG -n ${NAMESPACE}
```

**For Performance Issues:**
```bash

# Scale up immediately

kubectl scale deployment/project-ai-app --replicas=10 -n ${NAMESPACE}

# Enable rate limiting

curl -X POST http://localhost:8011/api/v1/policies \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "name": "emergency_rate_limit",
    "type": "rate_limit",
    "config": {
      "requests_per_minute": 100,
      "burst": 50
    }
  }'
```

**For Service Failures:**
```bash

# Rollback to previous version

kubectl rollout undo deployment/project-ai-app -n ${NAMESPACE}

# Or use automated rollback

./rollback.sh production --force

# Disable failing feature

kubectl set env deployment/project-ai-app FEATURE_X_ENABLED=false -n ${NAMESPACE}
```

**For Database Issues:**
```bash

# Switch to read replica

kubectl patch service postgres -n ${NAMESPACE} -p '
spec:
  selector:
    app: postgres
    role: replica
'

# Scale up connection pool

kubectl set env deployment/project-ai-app DB_POOL_SIZE=50 -n ${NAMESPACE}

# Clear connection pool

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -c "from app.db import engine; engine.dispose()"
```

### Step 4: Investigate Root Cause (Ongoing)

#### Collect Evidence

**Logs:**
```bash

# Export all relevant logs

mkdir -p incident-logs/INC-$(date +%Y%m%d-%H%M%S)
cd incident-logs/INC-$(date +%Y%m%d-%H%M%S)

# Application logs

docker-compose logs --no-color > application.log
kubectl logs deployment/project-ai-app -n ${NAMESPACE} --all-containers=true > k8s-application.log

# Microservices logs

for service in mutation-firewall incident-reflex trust-graph data-vault; do
  docker-compose logs $service > ${service}.log
done

# System logs (if accessible)

journalctl -u docker.service --since "1 hour ago" > docker-daemon.log
kubectl get events -n ${NAMESPACE} > k8s-events.log
```

**Metrics:**
```bash

# Export metrics snapshot

curl -G http://localhost:9090/api/v1/query_range \
  --data-urlencode 'query=rate(http_requests_total[5m])' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)" \
  --data-urlencode "end=$(date +%s)" \
  --data-urlencode 'step=60' > metrics-snapshot.json

# Export Grafana dashboard

curl http://admin:admin@localhost:3000/api/dashboards/uid/main-dashboard > dashboard-snapshot.json
```

**Configuration:**
```bash

# Export current configuration

kubectl get deployment/project-ai-app -n ${NAMESPACE} -o yaml > deployment-config.yaml
kubectl get configmap -n ${NAMESPACE} -o yaml > configmaps.yaml
docker-compose config > docker-compose-config.yaml
```

#### Analyze Logs

```bash

# Find errors around incident time

cat application.log | grep -A 10 -B 10 "2026-04-09 10:30"

# Count error types

cat application.log | grep ERROR | cut -d: -f2 | sort | uniq -c | sort -rn

# Find slow queries

cat application.log | grep "duration" | awk '{if ($NF > 1000) print}'

# Trace specific request

REQUEST_ID="abc-123-def"
cat application.log | grep "$REQUEST_ID"
```

#### Analyze Metrics

```bash

# Check metric spike correlation

curl "http://localhost:9090/api/v1/query?query=increase(http_requests_failed_total[5m])&time=2026-04-09T10:30:00Z"

# Compare to baseline

curl "http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m])" | jq .
```

### Step 5: Resolve (Within RTO)

#### Apply Fix

**For Code Issues:**
```bash

# Deploy hotfix

git checkout -b hotfix/incident-response

# Make fix...

git commit -m "fix: resolve incident INC-20260409-001"
git push

# Deploy

./k8s/deploy.sh production deploy

# Verify fix

curl http://localhost:8000/health
```

**For Configuration Issues:**
```bash

# Update configuration

kubectl edit configmap project-ai-config -n ${NAMESPACE}

# Restart services

kubectl rollout restart deployment/project-ai-app -n ${NAMESPACE}

# Verify

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}
```

**For Infrastructure Issues:**
```bash

# Provision additional resources

kubectl patch deployment project-ai-app -n ${NAMESPACE} --patch '
spec:
  template:
    spec:
      containers:

      - name: project-ai
        resources:
          requests:
            cpu: "2000m"
            memory: "4Gi"
          limits:
            cpu: "4000m"
            memory: "8Gi"

'

# Verify

kubectl top pod -n ${NAMESPACE}
```

#### Verify Resolution

```bash

# Check health

./verify_runtime_setup.py

# Run smoke tests

./k8s/deploy.sh production test

# Monitor for 15 minutes

watch -n 30 'curl -s http://localhost:8000/health'

# Check error rate returned to normal

curl "http://localhost:9090/api/v1/query?query=rate(http_requests_failed_total[5m])"
```

### Step 6: Communicate (Throughout)

#### Status Updates

**Initial Notification (Within 5 minutes):**
```
🚨 INCIDENT DETECTED
Incident ID: INC-20260409-001
Severity: P1 - High
Status: Investigating
Impact: API errors affecting ~500 users
Assigned: @oncall-engineer
Next Update: 10:30 UTC
```

**Progress Updates (Every 15-30 minutes):**
```
📊 INCIDENT UPDATE
Incident ID: INC-20260409-001
Time: 10:30 UTC
Status: Containment in progress
Actions Taken:

- Rolled back deployment to v1.9.0
- Scaled up to 10 replicas
- Identified root cause: database connection pool exhaustion

Next Steps:

- Apply database configuration fix
- Monitor for 15 minutes

Next Update: 11:00 UTC
```

**Resolution Notification:**
```
✅ INCIDENT RESOLVED
Incident ID: INC-20260409-001
Duration: 45 minutes (10:15-11:00 UTC)
Root Cause: Database connection pool exhausted due to configuration error
Resolution: Increased pool size and applied connection timeout
Impact: ~500 users experienced intermittent 500 errors
Post-Mortem: Scheduled for 2026-04-10 10:00 UTC
```

---

## Escalation Procedures

### Escalation Criteria

**Escalate to Senior Engineer:**

- Incident duration > 30 minutes
- Multiple failed resolution attempts
- Uncertainty about correct action
- Potential for major data loss

**Escalate to Engineering Manager:**

- Incident duration > 1 hour
- Severity P0-P1 impacting critical functionality
- Need for coordination across multiple teams
- Requires architectural decisions

**Escalate to CTO/Leadership:**

- Incident duration > 2 hours
- Security breach or data loss
- Significant financial impact
- Public relations concern
- Requires executive decision

### Escalation Contacts

```bash

# Example: escalation.txt

# On-call Engineer: +1-555-0100

# Senior Engineer: +1-555-0101  

# Engineering Manager: +1-555-0102

# CTO: +1-555-0103

# 

# Escalation sequence:

# 1. Primary on-call

# 2. Secondary on-call (if no response in 10 min)

# 3. Engineering Manager (if P0/P1 > 30 min)

# 4. CTO (if P0 > 1 hour or security breach)

```

---

## Recovery Playbooks

### Playbook: Complete Service Outage

**Symptoms:**

- All health checks failing
- No response from any service
- 100% error rate

**Response:**
```bash

# 1. Check infrastructure

docker ps -a  # Are containers running?
kubectl get nodes  # Are nodes healthy?

# 2. Check recent changes

git log --oneline -10
kubectl rollout history deployment/project-ai-app -n ${NAMESPACE}

# 3. Rollback

./rollback.sh production --force

# 4. If rollback fails, restart from scratch

docker-compose down
docker-compose up -d

# Or K8s:

kubectl delete pod --all -n ${NAMESPACE}
```

### Playbook: Database Failure

**Symptoms:**

- Database connection errors
- Timeout errors
- Data inconsistency

**Response:**
```bash

# 1. Check database status

kubectl get pods -n ${NAMESPACE} -l app=postgres
docker-compose ps temporal-postgresql

# 2. Check database logs

kubectl logs -l app=postgres -n ${NAMESPACE}
docker-compose logs temporal-postgresql

# 3. Attempt reconnection

kubectl rollout restart deployment/project-ai-app -n ${NAMESPACE}

# 4. Switch to read replica (if available)

kubectl patch service postgres -n ${NAMESPACE} -p '
spec:
  selector:
    role: replica
'

# 5. Restore from backup (if necessary)

# See: P0_RUNBOOKS/postgresql-wal-backup-setup.md

```

### Playbook: Security Breach

**Symptoms:**

- Unauthorized access detected
- Suspicious API activity
- Alert from security scanning

**Response:**
```bash

# 1. IMMEDIATE: Isolate affected systems

kubectl scale deployment/project-ai-app --replicas=0 -n ${NAMESPACE}

# 2. Rotate ALL credentials

./emergency-rotate-secrets.sh

# 3. Enable comprehensive logging

kubectl set env deployment/project-ai-app LOG_LEVEL=DEBUG -n ${NAMESPACE}

# 4. Block suspicious IPs

# Update firewall/network policies

# 5. Collect forensic evidence

kubectl logs --all-containers=true -n ${NAMESPACE} > forensic-logs.txt
kubectl get events -n ${NAMESPACE} > forensic-events.txt

# 6. Notify security team

# Send alert to security@company.com

# 7. After containment, restore from clean backup

```

### Playbook: High Memory/CPU Usage

**Symptoms:**

- OOMKilled pods
- Slow response times
- High resource metrics

**Response:**
```bash

# 1. Identify resource hog

kubectl top pod -n ${NAMESPACE} --sort-by=memory
kubectl top pod -n ${NAMESPACE} --sort-by=cpu

# 2. Check for memory leaks

kubectl logs <pod> -n ${NAMESPACE} | grep "OutOfMemory"

# 3. Scale up resources

kubectl patch deployment project-ai-app -n ${NAMESPACE} --patch '
spec:
  template:
    spec:
      containers:

      - name: project-ai
        resources:
          limits:
            memory: "8Gi"
            cpu: "4000m"

'

# 4. Scale out (more replicas)

kubectl scale deployment/project-ai-app --replicas=10 -n ${NAMESPACE}

# 5. Restart to clear memory

kubectl rollout restart deployment/project-ai-app -n ${NAMESPACE}
```

### Playbook: External Dependency Failure

**Symptoms:**

- Timeout errors from external APIs
- Third-party service unavailable
- Failed API calls

**Response:**
```bash

# 1. Verify external service status

curl https://status.openai.com
curl https://api.openai.com/v1/models

# 2. Enable fallback mode (if available)

kubectl set env deployment/project-ai-app FALLBACK_MODE=true -n ${NAMESPACE}

# 3. Use cached responses

kubectl set env deployment/project-ai-app USE_CACHE=true -n ${NAMESPACE}

# 4. Implement circuit breaker

# Already implemented in code, verify it's working

# 5. Notify users of degraded functionality

# Post status update

# 6. Monitor for service restoration

watch -n 60 'curl -s https://api.openai.com/v1/models'
```

---

## Post-Incident Activities

### Incident Report Template

```markdown

# Incident Report: [Title]

## Summary

- **Incident ID**: INC-20260409-001
- **Severity**: P1 - High
- **Start Time**: 2026-04-09 10:15 UTC
- **End Time**: 2026-04-09 11:00 UTC
- **Duration**: 45 minutes
- **Detected By**: Automated monitoring
- **Responders**: @engineer1, @engineer2

## Impact

- **Users Affected**: ~500 users
- **Services Affected**: Main API, Mutation Firewall
- **Revenue Impact**: Estimated $1,000 in lost transactions
- **Data Loss**: None

## Timeline

- **10:15 UTC**: Alert triggered for high error rate
- **10:17 UTC**: Incident acknowledged by on-call engineer
- **10:20 UTC**: Root cause identified (database connection pool exhaustion)
- **10:25 UTC**: Rollback to previous version initiated
- **10:30 UTC**: Configuration fix applied
- **10:35 UTC**: Services returning to normal
- **10:45 UTC**: Monitoring period begins
- **11:00 UTC**: Incident resolved and declared stable

## Root Cause

Database connection pool was exhausted due to:

1. Recent deployment increased worker count from 4 to 8
2. Connection pool size remained at 20 (should be ≥ workers * 3)
3. Long-running queries held connections open
4. No connections available for new requests = 500 errors

## Resolution

1. Rolled back to previous deployment
2. Increased DB_POOL_SIZE from 20 to 50
3. Added connection timeout configuration
4. Re-deployed with fix

## Prevention

- [ ] Add validation: DB_POOL_SIZE ≥ WORKERS * 3
- [ ] Add monitoring alert: connection pool usage > 80%
- [ ] Document pool sizing in deployment guide
- [ ] Add pre-deployment checklist
- [ ] Load test with increased worker count

## Action Items

- [ ] @engineer1: Implement pool size validation (Due: 2026-04-12)
- [ ] @engineer2: Add monitoring alert (Due: 2026-04-10)
- [ ] @sre: Update deployment guide (Due: 2026-04-11)
- [ ] @manager: Schedule post-mortem meeting (2026-04-10 10:00 UTC)

## Lessons Learned

### What Went Well

- Quick detection via monitoring
- Rollback executed smoothly
- Clear communication throughout

### What Went Wrong

- Configuration not validated before deployment
- No load testing with new worker count
- Connection pool monitoring alert missing

### What We Learned

- Always load test configuration changes
- Database connection pooling requires careful tuning
- Pre-deployment checklists prevent configuration errors

```

### Post-Mortem Meeting

**Agenda:**

1. Review timeline (10 minutes)
2. Discuss root cause (15 minutes)
3. Review prevention measures (15 minutes)
4. Assign action items (10 minutes)
5. Lessons learned (10 minutes)

**Attendees:**

- Incident responders
- Service owners
- Engineering manager
- SRE team

---

**Last Updated**: 2026-04-09  
**Maintained By**: SRE Team  
**Review Frequency**: After each P0/P1 incident
