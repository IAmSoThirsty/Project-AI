# Alert Rules Configuration

**Component:** Alert Management  
**Type:** Operational Configuration  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This document defines alerting rules, severity levels, notification channels, and incident response procedures for Project-AI monitoring infrastructure. Alert rules are implemented in `src/app/monitoring/alert_manager.py` using condition-based evaluation of Prometheus metrics.

---

## Alert Architecture

### Components

```
┌──────────────────────────────────────────────────┐
│           Alert Evaluation Flow                   │
├──────────────────────────────────────────────────┤
│                                                    │
│  1. Metrics Collection                            │
│     └─> SecurityMetricsCollector.get_all_metrics()│
│                                                    │
│  2. Rule Evaluation                               │
│     └─> AlertManager.evaluate_metrics(metrics)    │
│                                                    │
│  3. Condition Check                               │
│     └─> AlertRule.should_fire(metrics)            │
│                                                    │
│  4. Cooldown Verification                         │
│     └─> Check time since last_fired               │
│                                                    │
│  5. Notification Dispatch                         │
│     └─> Send to channels (PAGER, EMAIL, SLACK)    │
│                                                    │
│  6. Incident Creation (HIGH/CRITICAL only)        │
│     └─> Create incident, trigger workflow         │
│                                                    │
│  7. Persistence                                   │
│     └─> Save alert_history, incident_log          │
│                                                    │
└──────────────────────────────────────────────────┘
```

---

## Severity Levels

### Definitions

| Severity | Impact | Response Time | Notification | Examples |
|----------|--------|---------------|--------------|----------|
| **INFO** | Informational | None | LOG | Metrics collected, backup completed |
| **LOW** | Minor issue | 24 hours | EMAIL | Low patch acceptance, slow queries |
| **MEDIUM** | Significant issue | 2 hours | EMAIL, SLACK, TICKET | CI regression, high latency, pattern update failure |
| **HIGH** | Major issue | 30 minutes | EMAIL, SLACK, TICKET | Rising false positives, sustained high latency |
| **CRITICAL** | System compromised | Immediate | PAGER, EMAIL, SLACK, TICKET | Attack success, security breach, Four Laws bypass |

### Severity Escalation

```python
# Example: Low → Medium escalation
if low_severity_alert_count > 10 in last_hour:
    escalate_to_medium()

# Example: Medium → High escalation  
if medium_severity_alert_duration > 2_hours:
    escalate_to_high()
```

---

## Default Alert Rules

### Security Alerts

#### 1. High Attack Success Rate (CRITICAL)

**Rule Name:** `high_severity_attack_success`  
**Severity:** CRITICAL  
**Channels:** PAGER, SLACK, TICKET  
**Cooldown:** 30 minutes

**Condition:**
```python
lambda m: m.get("security", {})
    .get("attack_success_rate", {})
    .get("success_rate", 0) > 0.1
```

**PromQL Equivalent:**
```promql
rate(project_ai_cerberus_blocks_total{attack_type="bypass"}[1h]) 
  / rate(project_ai_cerberus_blocks_total[1h]) > 0.1
```

**Message:** `CRITICAL: Attack success rate {security[attack_success_rate][success_rate]:.1%} exceeds threshold`

**Response Actions:**
1. Page on-call engineer immediately
2. Review attack patterns in last hour
3. Check if new bypass technique detected
4. Consider enabling emergency lockdown
5. Analyze recent code/config changes

---

#### 2. Rising False Positive Rate (HIGH)

**Rule Name:** `rising_false_positive_rate`  
**Severity:** HIGH  
**Channels:** EMAIL, TICKET  
**Cooldown:** 120 minutes

**Condition:**
```python
lambda m: m.get("security", {})
    .get("false_positive_rate", {})
    .get("false_positive_rate", 0) > 0.2
```

**PromQL Equivalent:**
```promql
sum(project_ai_safety_detections{is_true_positive="false"}[1h]) 
  / sum(project_ai_safety_detections[1h]) > 0.2
```

**Message:** `HIGH: False positive rate {security[false_positive_rate][false_positive_rate]:.1%} exceeds threshold - safety review required`

**Response Actions:**
1. Create Jira ticket for safety team review
2. Analyze recent detection pattern changes
3. Review Black Vault additions (may indicate overzealous blocking)
4. Consider rolling back recent safety guard updates
5. Schedule safety calibration meeting

---

#### 3. Four Laws Critical Violation (CRITICAL)

**Rule Name:** `four_laws_critical_violation`  
**Severity:** CRITICAL  
**Channels:** PAGER, EMAIL, SLACK, TICKET  
**Cooldown:** 15 minutes

**Condition:**
```python
lambda m: m.get("four_laws", {})
    .get("critical_denials", {})
    .get("count", 0) > 0
```

**PromQL Equivalent:**
```promql
increase(project_ai_four_laws_critical_denials_total[5m]) > 0
```

**Message:** `CRITICAL: Four Laws critical violation detected - {law_violated} law`

**Response Actions:**
1. Immediate page to on-call + security lead
2. Review denial context and reasoning
3. Verify no AI behavior anomalies
4. Check for command override attempts
5. Document incident in audit log
6. Consider temporary Four Laws hardening

---

### Reliability Alerts

#### 4. CI Red-Team Regression (MEDIUM)

**Rule Name:** `ci_redteam_regression`  
**Severity:** MEDIUM  
**Channels:** SLACK, TICKET  
**Cooldown:** 60 minutes

**Condition:**
```python
lambda m: m.get("reliability", {})
    .get("ci_failure_rate", {})
    .get("failure_rate", 0) > 0.3
```

**PromQL Equivalent:**
```promql
sum(project_ai_ci_runs{success="false"}[1h]) 
  / sum(project_ai_ci_runs[1h]) > 0.3
```

**Message:** `MEDIUM: CI failure rate {reliability[ci_failure_rate][failure_rate]:.1%} - block merges to main`

**Response Actions:**
1. Post alert to #ci-failures Slack channel
2. Create blocking Jira ticket
3. Freeze main branch merges until resolved
4. Identify failing test patterns
5. Assign to relevant agent team

---

#### 5. High Agent Latency (MEDIUM)

**Rule Name:** `high_agent_latency`  
**Severity:** MEDIUM  
**Channels:** SLACK, EMAIL  
**Cooldown:** 60 minutes

**Condition:**
```python
lambda m: (
    m.get("reliability", {})
    .get("long_context_latency", {})
    .get("p95_ms", 0) > 5000
    or m.get("reliability", {})
    .get("safety_guard_latency", {})
    .get("p95_ms", 0) > 500
)
```

**PromQL Equivalent:**
```promql
histogram_quantile(0.95, 
  rate(project_ai_memory_query_duration_seconds_bucket{query_type="long_context"}[5m])
) > 5
or
histogram_quantile(0.95,
  rate(project_ai_memory_query_duration_seconds_bucket{query_type="safety_guard"}[5m])
) > 0.5
```

**Message:** `MEDIUM: Agent latency exceeds threshold - performance investigation required`

**Response Actions:**
1. Check system resource utilization (CPU, memory, disk I/O)
2. Review recent code changes to agent execution paths
3. Analyze query patterns for inefficiencies
4. Consider enabling query caching
5. Scale up infrastructure if needed

---

### Quality Alerts

#### 6. Low Patch Acceptance Rate (LOW)

**Rule Name:** `low_patch_acceptance`  
**Severity:** LOW  
**Channels:** EMAIL  
**Cooldown:** 240 minutes (4 hours)

**Condition:**
```python
lambda m: m.get("quality", {})
    .get("patch_acceptance_rate", {})
    .get("acceptance_rate", 1.0) < 0.3
```

**PromQL Equivalent:**
```promql
sum(project_ai_patch_proposals{accepted="true"}[7d]) 
  / sum(project_ai_patch_proposals[7d]) < 0.3
```

**Message:** `LOW: Patch acceptance rate {quality[patch_acceptance_rate][acceptance_rate]:.1%} - review patch quality`

**Response Actions:**
1. Send weekly summary email to agent team leads
2. Review recent rejected patches for patterns
3. Analyze patch generation logic for quality issues
4. Consider adjusting patch proposal thresholds
5. Schedule patch quality retrospective

---

#### 7. Pattern Update Regression (MEDIUM)

**Rule Name:** `pattern_regression`  
**Severity:** MEDIUM  
**Channels:** SLACK, TICKET  
**Cooldown:** 60 minutes

**Condition:**
```python
lambda m: m.get("quality", {})
    .get("regression_rate", {})
    .get("regression_rate", 0) > 0.1
```

**PromQL Equivalent:**
```promql
sum(project_ai_pattern_updates{caused_regression="true"}[7d]) 
  / sum(project_ai_pattern_updates[7d]) > 0.1
```

**Message:** `MEDIUM: Pattern update regression rate {quality[regression_rate][regression_rate]:.1%} - rollback required`

**Response Actions:**
1. Identify regressed pattern updates
2. Rollback to last known good pattern set
3. Re-run CI adversarial tests
4. Document regression in incident report
5. Review pattern update approval process

---

## Notification Channels

### PAGER (PagerDuty / Opsgenie)

**Severity:** CRITICAL only  
**Response Time:** Immediate (< 5 minutes)  
**On-Call Rotation:** 24/7 coverage

**Configuration:**
```python
from app.monitoring.alert_manager import AlertChannel

def send_pager_alert(alert):
    """Send alert to PagerDuty."""
    import requests
    
    payload = {
        "routing_key": os.getenv("PAGERDUTY_ROUTING_KEY"),
        "event_action": "trigger",
        "payload": {
            "summary": alert["message"],
            "severity": alert["severity"],
            "source": "project-ai-monitoring",
            "custom_details": alert["metrics_snapshot"]
        }
    }
    
    response = requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json=payload
    )
    response.raise_for_status()
```

---

### EMAIL

**Severity:** LOW, MEDIUM, HIGH, CRITICAL  
**Response Time:** Check within 1 hour (business hours)  
**Recipients:** Team distribution list

**Configuration:**
```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(alert):
    """Send alert via email."""
    
    msg = MIMEText(alert["message"])
    msg["Subject"] = f"[{alert['severity'].upper()}] Project-AI Alert"
    msg["From"] = "alerts@project-ai.example.com"
    msg["To"] = os.getenv("ALERT_EMAIL_RECIPIENTS")
    
    with smtplib.SMTP(os.getenv("SMTP_HOST"), 587) as server:
        server.starttls()
        server.login(
            os.getenv("SMTP_USERNAME"),
            os.getenv("SMTP_PASSWORD")
        )
        server.send_message(msg)
```

---

### SLACK

**Severity:** MEDIUM, HIGH, CRITICAL  
**Response Time:** Real-time monitoring (business hours)  
**Channel:** #project-ai-alerts

**Configuration:**
```python
import requests

def send_slack_alert(alert):
    """Send alert to Slack."""
    
    color_map = {
        "critical": "danger",
        "high": "warning",
        "medium": "warning",
        "low": "good"
    }
    
    payload = {
        "channel": "#project-ai-alerts",
        "username": "Project-AI Monitor",
        "icon_emoji": ":robot_face:",
        "attachments": [{
            "color": color_map.get(alert["severity"], "good"),
            "title": f"{alert['severity'].upper()}: {alert['rule_name']}",
            "text": alert["message"],
            "footer": f"Incident: {alert.get('incident_id', 'N/A')}",
            "ts": time.time()
        }]
    }
    
    response = requests.post(
        os.getenv("SLACK_WEBHOOK_URL"),
        json=payload
    )
    response.raise_for_status()
```

---

### TICKET (Jira / GitHub Issues)

**Severity:** MEDIUM, HIGH, CRITICAL  
**Response Time:** Triaged within 2 hours  
**Project:** PROJECT-AI

**Configuration:**
```python
from jira import JIRA

def create_ticket_alert(alert):
    """Create Jira ticket for alert."""
    
    jira = JIRA(
        server=os.getenv("JIRA_SERVER"),
        basic_auth=(
            os.getenv("JIRA_USERNAME"),
            os.getenv("JIRA_API_TOKEN")
        )
    )
    
    priority_map = {
        "critical": "Highest",
        "high": "High",
        "medium": "Medium",
        "low": "Low"
    }
    
    issue = jira.create_issue(
        project="PROJECTAI",
        summary=f"[{alert['severity'].upper()}] {alert['rule_name']}",
        description=alert["message"],
        issuetype={"name": "Bug"},
        priority={"name": priority_map[alert["severity"]]},
        labels=["monitoring", "alert", alert["severity"]]
    )
    
    return issue.key
```

---

### LOG

**Severity:** All levels  
**Response Time:** N/A (passive logging)  
**Destination:** `data/logs/audit.log`

**Configuration:**
```python
def log_alert(alert):
    """Log alert to application logs."""
    logger = logging.getLogger("audit")
    logger.warning(
        "ALERT | severity=%s | rule=%s | message=%s",
        alert["severity"],
        alert["rule_name"],
        alert["message"]
    )
```

---

## Cooldown Management

### Purpose

Prevent **alert fatigue** by rate-limiting identical alerts within a time window.

### Implementation

```python
class AlertRule:
    def __init__(self, name, severity, channels, condition, 
                 message_template, cooldown_minutes=60):
        self.cooldown_minutes = cooldown_minutes
        self.last_fired = None
    
    def should_fire(self, metrics):
        # Check cooldown period
        if self.last_fired:
            minutes_since_last = (datetime.now() - self.last_fired).total_seconds() / 60
            if minutes_since_last < self.cooldown_minutes:
                return False  # Still in cooldown
        
        # Evaluate condition
        return self.condition(metrics)
```

### Cooldown Periods by Severity

| Severity | Default Cooldown | Rationale |
|----------|------------------|-----------|
| CRITICAL | 15-30 minutes | Urgent, but avoid paging storm |
| HIGH | 60-120 minutes | Allow time for investigation |
| MEDIUM | 60 minutes | Balance signal vs. noise |
| LOW | 240 minutes | Informational, not actionable |

### Override Cooldown

```python
# Force alert to fire regardless of cooldown
alert_manager.rules[0].last_fired = None
```

---

## Incident Management

### Incident Creation

**Trigger:** HIGH or CRITICAL alerts

**Incident Structure:**
```json
{
  "incident_id": "INC-20260420153045",
  "rule_name": "high_severity_attack_success",
  "severity": "critical",
  "status": "open",
  "created_at": "2026-04-20T15:30:45Z",
  "alert": {...},
  "metrics": {...},
  "actions_taken": [],
  "resolved_at": null
}
```

### Incident Workflow

```
┌──────────────┐
│ Alert Fires  │
└──────┬───────┘
       │
       ├─> Severity == HIGH/CRITICAL?
       │   ├─> Yes: Create Incident
       │   │   └─> incident_id = "INC-<timestamp>"
       │   │
       │   └─> No: Log alert only
       │
       ├─> Send Notifications
       │   └─> Channels per severity
       │
       ├─> Trigger Automated Response
       │   ├─> Rollback (pattern regression)
       │   ├─> Scale up (high latency)
       │   └─> Lockdown (security breach)
       │
       └─> Log to Incident Management System
```

### Incident Resolution

```python
from app.monitoring.alert_manager import alert_manager

# Resolve incident
alert_manager.resolve_incident(
    incident_id="INC-20260420153045",
    resolution_notes="False positive due to load test. Adjusted thresholds."
)
```

---

## Custom Alert Rules

### Adding New Rules

```python
from app.monitoring.alert_manager import AlertManager, AlertRule, AlertSeverity, AlertChannel

# Initialize alert manager
alert_manager = AlertManager()

# Define custom rule
custom_rule = AlertRule(
    name="memory_storage_critical",
    severity=AlertSeverity.CRITICAL,
    channels=[AlertChannel.PAGER, AlertChannel.SLACK],
    condition=lambda m: m.get("memory", {}).get("storage_bytes", 0) > 1e9,  # 1 GB
    message_template="CRITICAL: Memory storage {memory[storage_bytes]} bytes exceeds 1 GB",
    cooldown_minutes=30
)

# Add rule
alert_manager.rules.append(custom_rule)
```

### Testing Rules

```python
# Mock metrics
mock_metrics = {
    "memory": {"storage_bytes": 1.5e9},
    "security": {"attack_success_rate": {"success_rate": 0.05}}
}

# Evaluate rules
alert_manager.evaluate_metrics(mock_metrics)

# Check alert history
print(alert_manager.alert_history[-1])
```

---

## Alert Tuning

### Reducing False Positives

1. **Increase Thresholds:** If alert fires too often with no issues
   ```python
   # Before: Alert at 10% attack success
   condition=lambda m: m.get("security", {}).get("attack_success_rate", 0) > 0.1
   
   # After: Alert at 15% attack success
   condition=lambda m: m.get("security", {}).get("attack_success_rate", 0) > 0.15
   ```

2. **Extend Cooldown:** Reduce notification frequency
   ```python
   cooldown_minutes=120  # 2 hours instead of 1 hour
   ```

3. **Add Composite Conditions:** Multiple criteria must be met
   ```python
   condition=lambda m: (
       m.get("security", {}).get("attack_success_rate", 0) > 0.1
       and m.get("security", {}).get("total_attacks", 0) > 100
   )
   ```

### Reducing False Negatives

1. **Lower Thresholds:** Catch issues earlier
   ```python
   # More sensitive to latency spikes
   condition=lambda m: m.get("reliability", {}).get("p95_ms", 0) > 3000  # Was 5000
   ```

2. **Shorter Evaluation Windows:** React faster
   ```promql
   # Evaluate over 5m instead of 1h
   rate(metric[5m]) > threshold
   ```

3. **Add Early Warning Alerts:** LOW severity for trends
   ```python
   AlertRule(
       name="memory_storage_warning",
       severity=AlertSeverity.LOW,
       condition=lambda m: m.get("memory", {}).get("storage_bytes", 0) > 0.5e9,  # 500 MB
       message_template="WARNING: Memory storage approaching limit"
   )
   ```

---

## Operational Procedures

### Daily Alert Review

```bash
# Summary of last 24h
curl http://localhost:8000/api/alerts/summary?hours=24

# Open incidents
curl http://localhost:8000/api/incidents?status=open
```

### Weekly Alert Report

```python
from app.monitoring.alert_manager import alert_manager

summary = alert_manager.get_alert_summary(hours=168)  # 7 days

print(f"Total Alerts: {summary['total_alerts']}")
print(f"By Severity: {summary['by_severity']}")
print(f"Open Incidents: {summary['open_incidents']}")
```

### On-Call Playbook

**When Paged:**

1. **Acknowledge Alert** (< 5 minutes)
   - Check PagerDuty incident
   - Note severity and rule name

2. **Assess Impact** (< 10 minutes)
   - Check metrics dashboard
   - Review recent changes (code, config)
   - Determine scope (users affected, systems down)

3. **Mitigate** (< 30 minutes)
   - Apply immediate fix (rollback, scale up, disable feature)
   - Document actions in incident log

4. **Communicate** (< 60 minutes)
   - Update Slack #incidents channel
   - Notify stakeholders if customer-impacting

5. **Root Cause Analysis** (< 24 hours)
   - Investigate underlying cause
   - Create Jira ticket for permanent fix
   - Document in runbook

6. **Resolve Incident** (when stable)
   - Mark incident as resolved
   - Add resolution notes
   - Schedule post-mortem if critical

---

## Testing

### Unit Tests

```bash
pytest tests/monitoring/test_alert_manager.py -v
```

### Integration Tests

```python
# Simulate high attack success rate
from app.monitoring.security_metrics import SecurityMetricsCollector

collector = SecurityMetricsCollector()
for _ in range(100):
    collector.record_attack_result("adversary", "guardrail_1", success=True, turns=3)

# Evaluate alerts
metrics = collector.get_all_metrics()
alert_manager.evaluate_metrics(metrics)

# Verify alert fired
assert len(alert_manager.alert_history) > 0
assert alert_manager.alert_history[-1]["severity"] == "critical"
```

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
- [Security Metrics Deep Dive](06_security_metrics_deep_dive.md)
- [Monitoring Operations Runbook](09_monitoring_operations_runbook.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **On-Call:** PagerDuty rotation
- **Slack:** #project-ai-alerts
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/monitoring/alert_manager.py`
