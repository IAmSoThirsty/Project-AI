# Service Level Objectives (SLO) Definitions

**Sovereign Governance Substrate - Production SLOs**

**Version**: 1.0  
**Last Updated**: 2026-03-03  
**Owner**: Platform Engineering Team  
**Review Cycle**: Quarterly

---

## Table of Contents

1. [Overview](#overview)
2. [SLI Definitions](#sli-definitions)
3. [SLO Targets](#slo-targets)
4. [Error Budgets](#error-budgets)
5. [Alerting Thresholds](#alerting-thresholds)
6. [Measurement Methods](#measurement-methods)
7. [Compliance Tracking](#compliance-tracking)

---

## Overview

### What are SLOs?

**Service Level Objectives (SLOs)** are target values or ranges for service levels measured by Service Level Indicators (SLIs). They define the expected reliability, performance, and quality of the Sovereign Governance Substrate.

### SLO Hierarchy

```
SLA (Service Level Agreement) - Customer commitment (99.5%)
    └── SLO (Service Level Objective) - Internal target (99.9%)
            └── SLI (Service Level Indicator) - Actual measurement (99.95%)
```

### Principles

1. **User-Centric**: SLOs reflect user-experienced reliability
2. **Measurable**: All SLOs are objectively measurable via metrics
3. **Achievable**: Targets are realistic given current infrastructure
4. **Error Budget**: Allows for controlled failure and innovation
5. **Business-Aligned**: SLOs support business objectives

---

## SLI Definitions

### 1. API Availability SLI

**Definition**: Percentage of successful API requests

**Measurement**:
```prometheus

# Good events (non-5xx responses)

sum(rate(project_ai_api_requests_total{status!~"5.."}[30d]))

# Total events

sum(rate(project_ai_api_requests_total[30d]))

# Availability %

(good_events / total_events) * 100
```

**Rationale**: 5xx errors indicate server failures that impact users

**Exclusions**:

- 4xx errors (client errors, not service failures)
- Health check endpoints
- Synthetic monitoring requests

---

### 2. API Latency SLI

**Definition**: 95th percentile request latency

**Measurement**:
```prometheus
histogram_quantile(0.95, 
  sum(rate(project_ai_api_request_duration_seconds_bucket[5m])) by (le)
)
```

**Rationale**: p95 ensures good experience for vast majority of users

**Exclusions**:

- Batch/background job endpoints
- Admin/debugging endpoints
- Requests with explicit timeout parameters

---

### 3. Error Rate SLI

**Definition**: Percentage of requests resulting in errors

**Measurement**:
```prometheus

# Error rate

sum(rate(project_ai_api_errors_total[5m])) / 
sum(rate(project_ai_api_requests_total[5m])) * 100
```

**Rationale**: Low error rates ensure system stability

**Categories**:

- Application errors (4xx, 5xx)
- Timeout errors
- Validation errors
- Dependency failures

---

### 4. Security Incident Rate SLI

**Definition**: Critical security incidents per day

**Measurement**:
```prometheus

# Daily critical incidents

sum(increase(project_ai_security_incidents_total{severity="critical"}[1d]))
```

**Rationale**: Security is paramount; zero critical incidents expected

**Severity Levels**:

- **Critical**: Immediate threat, active exploit
- **High**: Significant vulnerability, potential threat
- **Medium**: Minor vulnerability, mitigated
- **Low**: Informational, no immediate risk

---

### 5. Four Laws Availability SLI

**Definition**: Four Laws validation system uptime

**Measurement**:
```prometheus

# Four Laws system availability

sum(rate(project_ai_four_laws_validations_total[30d])) > 0
```

**Rationale**: Ethics system must always be functional

**Validation**:

- Validation requests processed
- No system crashes/timeouts
- Results returned within SLA

---

### 6. Data Integrity SLI

**Definition**: Audit log integrity verification success rate

**Measurement**:
```prometheus

# Audit integrity checks passed

sum(rate(project_ai_audit_integrity_checks_passed[1d])) /
sum(rate(project_ai_audit_integrity_checks_total[1d])) * 100
```

**Rationale**: Data integrity is critical for governance

**Checks**:

- Cryptographic hash validation
- Log sequence verification
- Timestamp consistency
- No tampering detected

---

## SLO Targets

### Tier 1: Critical Services (99.9% - "Three Nines")

**Services**: Main API, Four Laws, Security Systems

| Service | SLI | Target | Time Window |
|---------|-----|--------|-------------|
| **Main API** | Availability | ≥ 99.9% | 30 days |
| **Main API** | Latency (p95) | ≤ 200ms | 5 minutes |
| **Main API** | Error Rate | ≤ 0.1% | 5 minutes |
| **Four Laws** | Availability | ≥ 99.9% | 30 days |
| **Four Laws** | Latency (p95) | ≤ 100ms | 5 minutes |
| **Security** | Critical Incidents | 0 per day | 24 hours |
| **Audit Logs** | Data Integrity | 100% | 24 hours |

**Downtime Budget**: 43.2 minutes per month

**Rationale**: These services are mission-critical; minimal downtime acceptable

---

### Tier 2: High Priority Services (99.5% - "Two and a Half Nines")

**Services**: Memory System, Plugin Manager, Cerberus

| Service | SLI | Target | Time Window |
|---------|-----|--------|-------------|
| **Memory System** | Availability | ≥ 99.5% | 30 days |
| **Memory System** | Query Latency (p95) | ≤ 500ms | 5 minutes |
| **Plugin System** | Execution Success Rate | ≥ 99% | 5 minutes |
| **Cerberus** | Availability | ≥ 99.5% | 30 days |
| **Cerberus** | Block Latency (p95) | ≤ 50ms | 5 minutes |

**Downtime Budget**: 3.6 hours per month

**Rationale**: Important services with degraded experience acceptable for short periods

---

### Tier 3: Standard Services (99% - "Two Nines")

**Services**: Dashboards, Reporting, Background Jobs

| Service | SLI | Target | Time Window |
|---------|-----|--------|-------------|
| **Grafana** | Availability | ≥ 99% | 30 days |
| **Reporting** | Job Success Rate | ≥ 95% | 24 hours |
| **Background Jobs** | Completion Rate | ≥ 98% | 24 hours |

**Downtime Budget**: 7.2 hours per month

**Rationale**: Non-critical services; scheduled maintenance allowed

---

### Tier 4: Microservices (99.5%)

**Services**: All 8 emergent microservices

| Microservice | SLI | Target | Time Window |
|--------------|-----|--------|-------------|
| **Mutation Firewall** | Availability | ≥ 99.5% | 30 days |
| **Incident Reflex** | Response Time (p95) | ≤ 1s | 5 minutes |
| **Trust Graph** | Query Latency (p95) | ≤ 300ms | 5 minutes |
| **Data Vault** | Availability | ≥ 99.9% | 30 days |
| **Negotiation Agent** | Success Rate | ≥ 95% | 24 hours |
| **Compliance Engine** | Validation Rate | 100% | 24 hours |
| **Verifiable Reality** | Proof Generation Time | ≤ 5s | 5 minutes |
| **I Believe In You** | Availability | ≥ 99% | 30 days |

---

## Error Budgets

### Error Budget Concept

An **error budget** is the maximum amount of unreliability allowed within an SLO target.

**Formula**: `Error Budget = 100% - SLO Target`

**Example**:

- SLO: 99.9% availability
- Error Budget: 0.1% (43.2 min/month)

### Error Budget Policy

**When Error Budget > 50%**: ✅ GREEN

- Continue feature development
- Normal release velocity
- Innovation encouraged

**When Error Budget 20-50%**: ⚠️ YELLOW

- Slow feature releases
- Focus on reliability improvements
- Increase testing coverage
- Review recent changes

**When Error Budget < 20%**: 🔴 RED

- FREEZE non-critical features
- All hands on reliability
- Root cause analysis required
- Postmortem for all incidents

**When Error Budget Exhausted**: 🚨 CRITICAL

- COMPLETE feature freeze
- Emergency response team activated
- Executive escalation
- Customer communication required

### Error Budget Calculation

**30-Day Availability Budget**:
```
Total minutes in 30 days: 43,200
SLO: 99.9%
Error budget: 0.1% = 43.2 minutes

Remaining budget = 43.2 - (actual_downtime_minutes)
Budget % remaining = (remaining / 43.2) * 100
```

**Prometheus Query**:
```prometheus

# Error budget remaining (%)

(1 - (
  sum(rate(project_ai_api_requests_total{status=~"5.."}[30d])) /
  sum(rate(project_ai_api_requests_total[30d]))
)) / 0.001 * 100
```

### Burn Rate Alerts

**Fast Burn** (exhausted in 3 days):
```prometheus

# Burning at >10x rate

(1 - (
  sum(rate(project_ai_api_requests_total{status!~"5.."}[1h])) /
  sum(rate(project_ai_api_requests_total[1h]))
)) > 0.01
```
**Action**: Page on-call immediately

**Slow Burn** (exhausted in 15 days):
```prometheus

# Burning at >2x rate

(1 - (
  sum(rate(project_ai_api_requests_total{status!~"5.."}[6h])) /
  sum(rate(project_ai_api_requests_total[6h]))
)) > 0.002
```
**Action**: Alert engineering team, schedule review

---

## Alerting Thresholds

### Multi-Window, Multi-Burn-Rate Alerts

**Critical (Page Immediately)**:

- 2% budget consumed in 1 hour **AND** 5% in 6 hours
- Projected exhaustion in < 3 days

**High (Alert Engineering)**:

- 1% budget consumed in 1 hour **AND** 5% in 6 hours
- Projected exhaustion in < 7 days

**Warning (Ticket)**:

- 0.5% budget consumed in 1 hour **AND** 2.5% in 6 hours
- Projected exhaustion in < 15 days

### Example Alert Rules

```yaml

- alert: SLOBudgetBurnRateCritical
  expr: |
    (
      (1 - sum(rate(project_ai_api_requests_total{status!~"5.."}[1h])) / sum(rate(project_ai_api_requests_total[1h]))) > 0.0002
    and
      (1 - sum(rate(project_ai_api_requests_total{status!~"5.."}[6h])) / sum(rate(project_ai_api_requests_total[6h]))) > 0.0005
    )
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "SLO error budget burning critically fast"
    description: "At current rate, error budget will be exhausted in < 3 days"

```

---

## Measurement Methods

### Data Collection

**Prometheus Scraping**:

- Scrape interval: 15 seconds
- Retention: 15 days (local), 1 year (remote)
- High availability: 2 Prometheus replicas

**Recording Rules**:
```yaml
groups:

  - name: slo_rules
    interval: 30s
    rules:
      - record: api:availability:30d
        expr: |
          sum(rate(project_ai_api_requests_total{status!~"5.."}[30d])) /
          sum(rate(project_ai_api_requests_total[30d])) * 100

      - record: api:latency:p95
        expr: |
          histogram_quantile(0.95, 
            sum(rate(project_ai_api_request_duration_seconds_bucket[5m])) by (le)
          )

      - record: api:error_rate:5m
        expr: |
          sum(rate(project_ai_api_errors_total[5m])) / 
          sum(rate(project_ai_api_requests_total[5m])) * 100

```

### Grafana SLO Dashboard

**Panels**:

1. Current SLO compliance (gauge)
2. Error budget remaining (%)
3. Error budget burn rate
4. SLO history (30 days)
5. Incident timeline
6. Top error contributors

### Reporting

**Daily**:

- SLO compliance snapshot
- Error budget status
- New incidents

**Weekly**:

- SLO trend analysis
- Error budget consumption rate
- Reliability improvements

**Monthly**:

- Full SLO report
- Postmortems summary
- Compliance attestation
- Quarterly SLO review planning

---

## Compliance Tracking

### Verification Methods

1. **Automated Monitoring**: Prometheus + Grafana dashboards
2. **Manual Audits**: Weekly SLO review meetings
3. **Incident Reports**: RCA for every SLO violation
4. **Customer Surveys**: User-reported issues correlation

### SLO Review Process

**Weekly** (Engineering Team):

- Review current SLO status
- Analyze error budget consumption
- Identify reliability risks
- Plan mitigations

**Monthly** (Leadership):

- SLO compliance report
- Error budget policy enforcement
- Resource allocation decisions
- SLO target adjustments (if needed)

**Quarterly** (Executive):

- SLO effectiveness review
- Business impact analysis
- SLA vs SLO gap analysis
- Investment in reliability

### Consequences of SLO Violations

**Single Violation**:

- Incident postmortem required
- Action items tracked
- Follow-up in next review

**Repeated Violations (3+ per quarter)**:

- Executive escalation
- Reliability task force formed
- Feature freeze until resolved
- Customer communication plan

**Chronic Violations**:

- SLO target re-evaluation
- Architecture review
- Resource reallocation
- Potential SLA breach communication

---

## SLO Adjustment Process

### When to Adjust SLOs

**Tighten (Increase Target)**:

- Consistently exceeding current SLO (>99.95% for 99.9% target)
- Customer expectations increased
- Competitive pressure
- Business criticality increased

**Relax (Decrease Target)**:

- Chronically missing SLO despite best efforts
- Architecture limitations
- Cost-benefit analysis favors relaxation
- Feature velocity severely impacted

### Adjustment Procedure

1. **Data Analysis**: 3+ months of historical data
2. **Stakeholder Input**: Engineering, Product, Customer Success
3. **Business Case**: Cost/benefit analysis
4. **Approval**: VP Engineering + Product
5. **Communication**: Internal and external (if SLA-impacting)
6. **Implementation**: Update configs, alerts, dashboards
7. **Monitoring**: Ensure new target is realistic

### Change Log

| Date | SLO | Old Target | New Target | Reason | Approved By |
|------|-----|------------|------------|--------|-------------|
| 2026-03-03 | API Availability | N/A | 99.9% | Initial definition | Platform Eng |

---

## Appendix

### Useful Prometheus Queries

**Current API Availability**:
```prometheus
sum(rate(project_ai_api_requests_total{status!~"5.."}[5m])) /
sum(rate(project_ai_api_requests_total[5m])) * 100
```

**30-Day Availability**:
```prometheus
sum(increase(project_ai_api_requests_total{status!~"5.."}[30d])) /
sum(increase(project_ai_api_requests_total[30d])) * 100
```

**Error Budget Remaining (minutes)**:
```prometheus
43.2 - (
  (1 - (
    sum(increase(project_ai_api_requests_total{status!~"5.."}[30d])) /
    sum(increase(project_ai_api_requests_total[30d]))
  )) * 43200
)
```

**Time to Budget Exhaustion (days)**:
```prometheus
(error_budget_remaining_pct / 100) * 30 / 
(
  (1 - (
    sum(rate(project_ai_api_requests_total{status!~"5.."}[6h])) /
    sum(rate(project_ai_api_requests_total[6h]))
  )) / 0.001
)
```

### Reference Links

- [Google SRE Book - Implementing SLOs](https://sre.google/sre-book/service-level-objectives/)
- [SLO Workshop](https://github.com/google/sre-school)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

**Document Owner**: Platform Engineering  
**Reviewers**: SRE Team, Product Management  
**Next Review**: 2026-06-03  
**Version**: 1.0
