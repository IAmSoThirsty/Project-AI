# Incident Response Runbook

## Overview
This runbook provides step-by-step procedures for responding to incidents in the Sovereign Governance Substrate production environment.

## Severity Levels

### P0 (Critical)
- **Definition**: Complete service outage or critical security breach
- **Response Time**: Immediate (< 5 minutes)
- **Escalation**: Page on-call engineer + incident commander

### P1 (High)
- **Definition**: Partial service degradation affecting >50% of users
- **Response Time**: < 15 minutes
- **Escalation**: Notify on-call engineer

### P2 (Medium)
- **Definition**: Minor service degradation affecting <50% of users
- **Response Time**: < 1 hour
- **Escalation**: Create ticket for next business day

### P3 (Low)
- **Definition**: Non-critical issues, no user impact
- **Response Time**: < 4 hours
- **Escalation**: Regular ticket queue

## Incident Response Process

### 1. Detection and Triage (5 minutes)
```bash
# Check overall system health
kubectl get pods -n sovereign-governance
kubectl get pods -n temporal

# Check recent events
kubectl get events -n sovereign-governance --sort-by='.lastTimestamp' | tail -20

# Check application logs
kubectl logs -n sovereign-governance deployment/temporal-worker --tail=100

# Check metrics
curl http://prometheus:9090/api/v1/query?query=up

# Determine severity and page appropriate personnel
```

### 2. Initial Assessment (10 minutes)
```bash
# Identify affected components
kubectl get deployments -n sovereign-governance -o wide
kubectl get statefulsets -n temporal -o wide

# Check resource utilization
kubectl top pods -n sovereign-governance
kubectl top nodes

# Review monitoring dashboards
# - Grafana: http://grafana.example.com/d/sovereign-overview
# - Temporal UI: http://temporal-ui.example.com
```

### 3. Communication (Ongoing)
**Immediately:**
- Create incident channel: `#incident-YYYYMMDD-HHMMM`
- Post initial status update
- Set up incident bridge call (if P0/P1)

**Status Update Template:**
```
[INCIDENT] Sovereign Governance - <Brief Description>
Severity: P<X>
Started: <Timestamp>
Affected: <Components/Users>
Status: <Investigating|Identified|Fixing|Monitoring|Resolved>
ETA: <If known>
Incident Lead: @<name>
```

**Update Frequency:**
- P0: Every 15 minutes
- P1: Every 30 minutes
- P2: Every hour
- P3: At major milestones

### 4. Mitigation Strategies

#### High CPU Usage
```bash
# Identify resource hogs
kubectl top pods -n sovereign-governance --sort-by=cpu

# Scale up workers
kubectl scale deployment/temporal-worker --replicas=10 -n sovereign-governance

# Check for runaway workflows
temporal workflow list --namespace=default | grep RUNNING | wc -l

# Terminate problematic workflows (if identified)
temporal workflow terminate --workflow-id=<id> --reason="Resource cleanup"
```

#### High Memory Usage
```bash
# Check memory by pod
kubectl top pods -n sovereign-governance --sort-by=memory

# Look for memory leaks
kubectl logs -n sovereign-governance <pod-name> | grep -i "OutOfMemory\|OOM"

# Restart affected pods (rolling restart)
kubectl rollout restart deployment/temporal-worker -n sovereign-governance

# Increase memory limits if needed
kubectl set resources deployment/temporal-worker -n sovereign-governance \
  --limits=memory=4Gi --requests=memory=2Gi
```

#### Database Connection Issues
```bash
# Check database pod status
kubectl get pods -n temporal -l app=cassandra

# Verify database connectivity
kubectl exec -it -n temporal temporal-server-0 -- \
  cqlsh -e "DESCRIBE KEYSPACES;"

# Check connection pool metrics
kubectl logs -n sovereign-governance deployment/temporal-worker | \
  grep "connection pool"

# Scale down workers temporarily to reduce load
kubectl scale deployment/temporal-worker --replicas=2 -n sovereign-governance

# Verify database health
kubectl exec -it -n temporal cassandra-0 -- nodetool status
```

#### Workflow Execution Failures
```bash
# List failed workflows
temporal workflow list --query="ExecutionStatus='Failed'" | head -20

# Get workflow details
temporal workflow describe --workflow-id=<id>

# Check workflow history
temporal workflow show --workflow-id=<id>

# Retry failed workflows (batch)
for id in $(temporal workflow list --query="ExecutionStatus='Failed'" | awk '{print $1}'); do
  temporal workflow reset --workflow-id=$id --event-id=<last-good-event>
done

# Check activity failures
kubectl logs -n sovereign-governance deployment/temporal-worker | \
  grep "activity failed"
```

#### Network Connectivity Issues
```bash
# Test pod-to-pod connectivity
kubectl exec -it -n sovereign-governance <worker-pod> -- \
  curl -v http://temporal-frontend:7233

# Check network policies
kubectl get networkpolicies -n sovereign-governance

# Verify DNS resolution
kubectl exec -it -n sovereign-governance <worker-pod> -- \
  nslookup temporal-frontend.temporal.svc.cluster.local

# Check service endpoints
kubectl get endpoints -n temporal temporal-frontend
```

#### Pod Crash Loops
```bash
# Identify crashing pods
kubectl get pods -n sovereign-governance | grep CrashLoop

# Get pod logs (including previous)
kubectl logs -n sovereign-governance <pod-name> --previous

# Describe pod for events
kubectl describe pod -n sovereign-governance <pod-name>

# Check resource constraints
kubectl describe node <node-name> | grep -A 5 "Allocated resources"

# Rollback to previous version if needed
kubectl rollout undo deployment/temporal-worker -n sovereign-governance
```

### 5. Escalation Paths

#### Level 1: On-Call Engineer
- Initial response
- Basic troubleshooting
- Immediate mitigation

**When to escalate:**
- Unable to identify root cause in 30 minutes
- Issue is beyond expertise
- Multiple components affected

#### Level 2: Senior Engineer / Team Lead
- Complex troubleshooting
- Architectural decisions
- Coordination with other teams

**When to escalate:**
- P0 incidents
- Data integrity concerns
- Security incidents
- Multi-team coordination needed

#### Level 3: Engineering Manager / Incident Commander
- Major incidents
- Business continuity decisions
- External communication

**When to escalate:**
- Extended outage (>2 hours)
- Data loss or corruption
- Security breach
- Executive notification required

### 6. Recovery Verification

```bash
# Verify all pods are healthy
kubectl get pods -n sovereign-governance -o wide
kubectl get pods -n temporal -o wide

# Check application health endpoints
curl http://temporal-frontend:7233/health
curl http://sovereign-api:8080/health

# Run smoke tests
kubectl apply -f test/smoke-test-job.yaml
kubectl wait --for=condition=complete job/smoke-test --timeout=5m
kubectl logs job/smoke-test

# Verify workflow execution
temporal workflow start \
  --workflow-type=HealthCheckWorkflow \
  --task-queue=test-queue \
  --workflow-id=health-check-$(date +%s)

# Monitor metrics for 30 minutes
# - Error rate should be < 0.1%
# - Latency P95 should be < 2s
# - No alerts firing
```

### 7. Post-Incident Activities

#### Immediate (< 2 hours after resolution)
```
1. Update incident channel with final status
2. Schedule post-mortem meeting (within 48 hours)
3. Create post-mortem document template
4. Gather relevant logs and metrics
```

#### Short-term (< 24 hours)
```
1. Document timeline of events
2. Identify contributing factors
3. Create action items with owners
4. Communicate lessons learned to team
```

#### Long-term (< 1 week)
```
1. Conduct blameless post-mortem
2. Update runbooks with lessons learned
3. Implement preventive measures
4. Update monitoring and alerting
5. Share post-mortem with broader team
```

## Common Incident Scenarios

### Scenario 1: Complete Service Outage

**Symptoms:**
- All workflow executions failing
- API returning 503 errors
- No pods in Running state

**Response:**
```bash
# 1. Check cluster health
kubectl cluster-info
kubectl get nodes

# 2. Check control plane
kubectl get pods -n kube-system

# 3. Check application namespace
kubectl get all -n sovereign-governance

# 4. Likely causes:
# - Cluster resource exhaustion
# - Network failure
# - Database unavailable
# - Configuration error

# 5. Quick recovery options:
# Option A: Rollback recent deployment
kubectl rollout undo deployment/temporal-worker -n sovereign-governance

# Option B: Scale to zero and back (force restart)
kubectl scale deployment/temporal-worker --replicas=0 -n sovereign-governance
sleep 30
kubectl scale deployment/temporal-worker --replicas=5 -n sovereign-governance

# Option C: Delete and recreate (last resort)
kubectl delete deployment/temporal-worker -n sovereign-governance
kubectl apply -f k8s/base/temporal-worker-deployment.yaml
```

### Scenario 2: Degraded Performance

**Symptoms:**
- Increased latency (P95 > 5s)
- Timeouts
- Slow workflow execution

**Response:**
```bash
# 1. Identify bottleneck
kubectl top pods -n sovereign-governance
kubectl top nodes

# 2. Check for resource contention
kubectl describe node <node-name> | grep -i pressure

# 3. Check database performance
kubectl exec -it -n temporal cassandra-0 -- nodetool tablestats

# 4. Scale horizontally
kubectl scale deployment/temporal-worker --replicas=10 -n sovereign-governance

# 5. Enable autoscaling if not already
kubectl autoscale deployment/temporal-worker \
  --min=5 --max=20 --cpu-percent=70 -n sovereign-governance
```

### Scenario 3: Data Inconsistency

**Symptoms:**
- Workflow state doesn't match expected
- Missing or duplicate events
- Replay issues

**Response:**
```bash
# 1. STOP - Do not delete data
# 2. Isolate affected workflows
temporal workflow list --query="<filter>"

# 3. Export workflow history
temporal workflow show --workflow-id=<id> > workflow-history.json

# 4. Contact data recovery team
# 5. Consider point-in-time recovery if recent

# For Cassandra:
nodetool snapshot temporal

# 6. Document exact symptoms and timeline
```

## Contacts

- **On-Call Engineer**: Check PagerDuty
- **Incident Commander**: Check on-call rotation
- **Engineering Manager**: manager@example.com
- **Database Team**: dba@example.com
- **Security Team**: security@example.com
- **Platform Team**: platform@example.com

## Tools and Resources

- **Monitoring**: https://grafana.example.com
- **Logs**: https://kibana.example.com
- **Temporal UI**: https://temporal-ui.example.com
- **PagerDuty**: https://example.pagerduty.com
- **Incident Channel**: #incidents
- **Runbooks**: https://wiki.example.com/runbooks
- **Post-Mortems**: https://wiki.example.com/post-mortems

## Revision History

- 2026-04-11: Initial version
- Update this runbook after each major incident with lessons learned
