# SLOs, Error Budgets & Operational Maturity

**Version**: 1.0.0  
**Date**: 2026-02-12  
**Status**: Active

---

## XXV. OPERATIONAL MATURITY & SLOS

### 1. Service Level Objectives (SLOs)

#### Availability SLO

**Target**: 99.9% availability (monthly)

**Definition**:
```
Availability = (Total Time - Downtime) / Total Time × 100
```

**Measurement Window**: 30 days (rolling)

**Success Criteria**:
- API responds with non-5xx status code
- Response time < 30 seconds (timeout)
- Health checks pass

**Error Budget**:
- **Monthly downtime allowed**: 43.8 minutes
- **Daily downtime allowed**: 1.44 minutes
- **Hourly downtime allowed**: 0.06 minutes (3.6 seconds)

**Monitoring**:
```promql
# Availability percentage
(sum(rate(http_requests_total{status_code!~"5.."}[5m])) /
 sum(rate(http_requests_total[5m]))) * 100

# Error budget remaining
1 - ((sum(increase(http_requests_total{status_code=~"5.."}[30d])) /
      sum(increase(http_requests_total[30d]))) / 0.001)
```

**Current Status**: 99.95% (Jan 2026) ✅

---

#### Latency SLO

**Target**: 
- **p50**: < 200ms
- **p95**: < 500ms  
- **p99**: < 1000ms

**Definition**:
- p50: 50% of requests complete within target
- p95: 95% of requests complete within target
- p99: 99% of requests complete within target

**Measurement**:
- Measured at API gateway
- Includes network, processing, database time
- Excludes client-side rendering

**Error Budget**:
- **p95 violations**: < 5% of requests per day
- **p99 violations**: < 1% of requests per day

**Monitoring**:
```promql
# p50 latency
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# p99 latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# SLO compliance (p95)
(sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m])) /
 sum(rate(http_request_duration_seconds_count[5m]))) >= 0.95
```

**Current Status**: 
- p50: 150ms ✅
- p95: 450ms ✅
- p99: 800ms ✅

---

#### Error Rate SLO

**Target**: < 1% error rate (excluding 4xx client errors)

**Definition**:
```
Error Rate = (5xx Responses) / (Total Responses) × 100
```

**Excluded**: 
- 4xx errors (client mistakes)
- 401/403 (expected auth failures)
- 429 (rate limiting, expected behavior)

**Included**:
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

**Error Budget**:
- **Daily errors allowed**: 1% of total requests
- If 10,000 requests/day → 100 errors allowed

**Monitoring**:
```promql
# Error rate percentage
(sum(rate(http_requests_total{status_code=~"5.."}[5m])) /
 sum(rate(http_requests_total[5m]))) * 100

# Error budget remaining
1 - ((sum(increase(http_requests_total{status_code=~"5.."}[30d])) /
      sum(increase(http_requests_total[30d]))) / 0.01)
```

**Current Status**: 0.5% (Jan 2026) ✅

---

### 2. Error Budget Policy

#### What is an Error Budget?

**Error budget** = Amount of downtime/errors allowed while still meeting SLO

**Example**:
- 99.9% availability SLO = 0.1% downtime allowed
- 30 days = 43,200 minutes
- Error budget = 43.2 minutes of downtime per month

#### Error Budget States

##### State 1: Healthy (> 75% budget remaining) 🟢

**Allowed Actions**:
- ✅ Deploy new features
- ✅ Run experiments
- ✅ Aggressive optimization
- ✅ Chaos engineering tests
- ✅ Major refactors

**Release Cadence**: Weekly (Fridays)

**Risk Tolerance**: High

---

##### State 2: Warning (25-75% budget remaining) 🟡

**Allowed Actions**:
- ✅ Deploy bug fixes
- ✅ Deploy performance improvements
- ⚠️ New features (with extra caution)
- ⚠️ Small experiments only
- ❌ No major refactors

**Release Cadence**: Bi-weekly (Fridays)

**Risk Tolerance**: Medium

**Required**:
- Additional staging testing
- Gradual rollout (canary)
- Extra monitoring during deploy

---

##### State 3: Critical (< 25% budget remaining) 🔴

**Allowed Actions**:
- ✅ Critical bug fixes only
- ✅ Security patches
- ❌ NO new features
- ❌ NO experiments
- ❌ NO refactors

**Release Cadence**: Emergency only

**Risk Tolerance**: Minimal

**Required**:
- Incident review
- Root cause analysis
- Remediation plan
- Freeze new features until budget recovers

---

##### State 4: Exhausted (0% budget remaining) ⛔

**Consequence**: **FEATURE FREEZE** 🧊

**Allowed Actions**:
- ✅ Critical security patches ONLY
- ❌ NO new features
- ❌ NO refactors
- ❌ NO experiments

**Duration**: Until next measurement window (monthly reset)

**Required Actions**:
1. **Incident Postmortem** - Within 48 hours
2. **Root Cause Analysis** - 5 Whys
3. **Remediation Plan** - Documented action items
4. **Prevention Measures** - Updated monitoring, testing, processes
5. **Executive Review** - Engineering leadership approval to resume

**Communication**:
- Engineering team notified
- Feature roadmap adjusted
- Stakeholders informed

---

### 3. Error Budget Tracking

#### Daily Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ Error Budget Status - 2026-02-12                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Availability SLO (99.9%)                                │
│ ████████████████████████████████░░░░░░░  85% remaining  │
│ Budget used: 6.5 minutes / 43.8 minutes                 │
│                                                         │
│ Latency SLO (p95 < 500ms)                               │
│ ██████████████████████████████████████  95% remaining   │
│ Violations: 0.5% / 5% allowed                           │
│                                                         │
│ Error Rate SLO (< 1%)                                   │
│ ██████████████████████████████████░░░░  90% remaining   │
│ Errors: 0.1% / 1% allowed                               │
│                                                         │
│ Overall Status: 🟢 HEALTHY - Weekly releases allowed    │
└─────────────────────────────────────────────────────────┘
```

#### Prometheus Queries

```promql
# Availability error budget remaining (%)
(1 - (
  sum(increase(http_requests_total{status_code=~"5.."}[30d])) /
  sum(increase(http_requests_total[30d]))
) / 0.001) * 100

# Latency error budget remaining (%)
(1 - (
  sum(rate(http_request_duration_seconds_bucket{le!="0.5"}[30d])) /
  sum(rate(http_request_duration_seconds_count[30d]))
) / 0.05) * 100

# Error rate budget remaining (%)
(1 - (
  sum(increase(http_requests_total{status_code=~"5.."}[30d])) /
  sum(increase(http_requests_total[30d]))
) / 0.01) * 100
```

#### Alerts

```yaml
# Alert when error budget < 25%
- alert: ErrorBudgetCritical
  expr: error_budget_remaining_percent < 25
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Error budget critical ({{ $value }}% remaining)"
    description: "Feature freeze imminent. Immediate investigation required."

# Alert when error budget < 50%
- alert: ErrorBudgetWarning
  expr: error_budget_remaining_percent < 50
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "Error budget warning ({{ $value }}% remaining)"
    description: "Reduce release cadence and increase caution."

# Alert when error budget exhausted
- alert: ErrorBudgetExhausted
  expr: error_budget_remaining_percent <= 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Error budget EXHAUSTED - FEATURE FREEZE"
    description: "Feature freeze in effect. Security patches only."
```

---

### 4. Capacity Planning

#### Current Capacity (Feb 2026)

**Infrastructure**:
- **Kubernetes Cluster**: 5 nodes (n1-standard-4)
- **Application Pods**: 3-10 (HPA configured)
- **Database**: PostgreSQL (db-n1-standard-2, 50GB)
- **Cache**: Redis (memory-1-standard-2, 5GB)

**Traffic**:
- **Average RPS**: 10 requests/second
- **Peak RPS**: 50 requests/second
- **Daily Requests**: ~860,000
- **Monthly Requests**: ~26 million

**Resources**:
- **CPU Usage**: 30% average, 60% peak
- **Memory Usage**: 40% average, 70% peak
- **Database Size**: 15GB (30% of capacity)
- **Cache Hit Rate**: 85%

---

#### Growth Projections

##### Q1 2026 (Current)
- **Users**: 1,000 active
- **RPS**: 10 average, 50 peak
- **Infrastructure**: Current (adequate)

##### Q2 2026 (3 months)
- **Users**: 2,500 active (2.5x growth)
- **RPS**: 25 average, 125 peak (2.5x)
- **Infrastructure Needs**:
  - Scale pods: 5-15 (increase HPA max)
  - Database: Upgrade to 100GB
  - Cache: Upgrade to 10GB

##### Q3 2026 (6 months)
- **Users**: 5,000 active (5x growth)
- **RPS**: 50 average, 250 peak (5x)
- **Infrastructure Needs**:
  - Scale cluster: 10 nodes
  - Scale pods: 10-20
  - Database: Upgrade to 200GB, read replicas
  - Cache: Upgrade to 20GB, Redis cluster

##### Q4 2026 (12 months)
- **Users**: 10,000 active (10x growth)
- **RPS**: 100 average, 500 peak (10x)
- **Infrastructure Needs**:
  - Scale cluster: 20 nodes
  - Scale pods: 20-40
  - Database: 500GB, multi-region
  - Cache: Redis cluster, 50GB
  - CDN: CloudFlare for static assets

---

#### Capacity Alerts

```yaml
# Alert when CPU usage sustained > 70%
- alert: HighCPUUsage
  expr: avg(rate(container_cpu_usage_seconds_total[5m])) > 0.7
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "High CPU usage ({{ $value }})"
    description: "Consider scaling up pods or nodes."

# Alert when memory usage > 80%
- alert: HighMemoryUsage
  expr: avg(container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.8
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High memory usage ({{ $value }})"
    description: "Memory leak or need to scale."

# Alert when DB size > 80% capacity
- alert: DatabaseNearCapacity
  expr: pg_database_size_bytes / pg_tablespace_size_bytes > 0.8
  for: 1h
  labels:
    severity: critical
  annotations:
    summary: "Database near capacity ({{ $value }}%)"
    description: "Upgrade database or archive old data."
```

---

### 5. Cost Guardrails

#### Monthly Budget: $2,000

**Breakdown**:
- **Kubernetes**: $800 (5 nodes × $160/node)
- **Database**: $600 (PostgreSQL + backups)
- **Cache**: $200 (Redis)
- **Monitoring**: $150 (Prometheus, Grafana)
- **External APIs**: $200 (OpenAI, Hugging Face)
- **Misc**: $50 (DNS, CDN, etc.)

**Total**: $2,000/month

#### Cost Alerts

```yaml
# Alert when monthly spend > $1,800 (90% of budget)
- alert: BudgetNearLimit
  expr: monthly_cloud_spend_dollars > 1800
  labels:
    severity: warning
  annotations:
    summary: "Cloud spend near budget limit (${{ $value }})"
    description: "Review resource usage and optimize."

# Alert when daily spend > $100 (projected $3,000/month)
- alert: DailySpendHigh
  expr: daily_cloud_spend_dollars > 100
  labels:
    severity: critical
  annotations:
    summary: "Daily spend high (${{ $value }})"
    description: "Investigate unexpected resource usage."
```

#### Cost Optimization

**Quick Wins**:
1. **Right-size pods** - Reduce resource requests if usage < 50%
2. **Spot instances** - Use for non-critical workloads (30-80% discount)
3. **Reserved instances** - Commit to 1-year for stable workloads (up to 40% discount)
4. **Data lifecycle** - Archive old data to cold storage (90% cheaper)
5. **Cache aggressively** - Reduce database queries and external API calls

**Monitoring**:
- Weekly cost review
- Tag all resources (project, environment, owner)
- FinOps dashboard in Grafana

---

### 6. Game Days & Chaos Engineering

#### Purpose
- Validate incident response procedures
- Test failure scenarios in production
- Build team confidence
- Improve MTTR (Mean Time To Recovery)

#### Schedule
- **Frequency**: Quarterly (Jan, Apr, Jul, Oct)
- **Duration**: 2-4 hours
- **Participants**: Engineering team, on-call, SRE

#### Chaos Scenarios

##### Scenario 1: Database Failover
**Objective**: Validate database failover and application recovery

**Steps**:
1. Announce game day (no surprise)
2. Trigger database pod kill
3. Observe application behavior
4. Measure recovery time
5. Review logs and metrics
6. Document learnings

**Success Criteria**:
- Application recovers within 2 minutes
- No data loss
- Circuit breaker opens correctly
- Alerts triggered
- No manual intervention needed

---

##### Scenario 2: Network Partition
**Objective**: Test behavior during network split

**Steps**:
1. Inject network latency (iptables delay)
2. Observe timeout handling
3. Verify circuit breaker behavior
4. Check user experience
5. Restore network
6. Review metrics

**Success Criteria**:
- Requests timeout gracefully (no hangs)
- Circuit breaker opens after 5 failures
- Error messages clear to users
- System recovers automatically

---

##### Scenario 3: Resource Exhaustion
**Objective**: Test autoscaling and rate limiting

**Steps**:
1. Generate traffic spike (10x normal)
2. Observe HPA scaling
3. Verify rate limiting kicks in
4. Check memory/CPU limits
5. Measure user impact
6. Review scaling metrics

**Success Criteria**:
- HPA scales from 3 to 10 pods within 5 minutes
- Rate limiting protects system
- No pod crashes (OOMKilled)
- p99 latency < 2x normal
- Recovery within 10 minutes after traffic normalizes

---

##### Scenario 4: Chaos Mesh Pod Deletion
**Objective**: Test pod failure and self-healing

**Steps**:
1. Use Chaos Mesh to randomly kill pods
2. Verify Kubernetes recreates pods
3. Check service continuity
4. Review liveness/readiness probes
5. Measure downtime per pod failure

**Success Criteria**:
- Pods recreate within 30 seconds
- No user-facing downtime (load balancer routes around)
- Health checks prevent routing to unhealthy pods
- Zero failed requests during pod restart

---

#### Game Day Checklist

**Before**:
- [ ] Schedule game day (1 week notice)
- [ ] Notify team and stakeholders
- [ ] Prepare runbook for scenarios
- [ ] Set up monitoring dashboards
- [ ] Create incident channel (#game-day-2026-02-12)
- [ ] Brief participants on objectives

**During**:
- [ ] Assign roles (incident commander, observers, scripters)
- [ ] Execute scenarios one at a time
- [ ] Document observations in real-time
- [ ] Capture metrics and screenshots
- [ ] Note any surprises or issues

**After**:
- [ ] Debrief within 24 hours
- [ ] Document learnings
- [ ] Create action items (Jira tickets)
- [ ] Update runbooks
- [ ] Share report with team
- [ ] Schedule follow-up for action items

---

## Related Documentation

- [DEPLOYABLE_SYSTEM_STANDARD.md](DEPLOYABLE_SYSTEM_STANDARD.md) - Full standard
- [FAILURE_MODELS_OPERATIONS.md](FAILURE_MODELS_OPERATIONS.md) - Failure handling
- [TRUST_BOUNDARIES.md](TRUST_BOUNDARIES.md) - Trust analysis

---

**Last Updated**: 2026-02-12  
**Next Review**: 2026-05-12 (Quarterly)
