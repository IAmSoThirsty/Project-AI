# Security Metrics Deep Dive

**Component:** Security Monitoring & Analytics  
**Type:** Technical Deep Dive  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This document provides an in-depth analysis of security-specific metrics in Project-AI, covering attack detection, Four Laws enforcement, Cerberus gate monitoring, threat scoring, and security incident management. These metrics are critical for maintaining system security posture and detecting adversarial behavior.

---

## Security Metrics Architecture

### Three-Layer Security Monitoring

```
┌─────────────────────────────────────────────────┐
│         Layer 1: Attack Detection                │
│  - Cerberus gate blocks                          │
│  - Threat detection scores                       │
│  - Malware/phishing detections                   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│         Layer 2: AI Ethics Enforcement           │
│  - Four Laws validations                         │
│  - Command override attempts                     │
│  - Black Vault access attempts                   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│         Layer 3: Access Control                  │
│  - Authentication failures                       │
│  - Authorization denials                         │
│  - Unauthorized access attempts                  │
└─────────────────────────────────────────────────┘
```

---

## Attack Detection Metrics

### Attack Success Rate

**Metric:** `project_ai_cerberus_blocks_total` / Total Attack Attempts

**Purpose:** Measure effectiveness of security gates in preventing attacks

**Collection:**
```python
from app.monitoring.security_metrics import SecurityMetricsCollector

collector = SecurityMetricsCollector()

# Record attack result
collector.record_attack_result(
    persona="adversary_jailbreak",
    guardrail="cerberus_injection_gate",
    success=False,  # Attack blocked
    turns=3
)

# Calculate success rate
attack_stats = collector.get_attack_success_rate(hours=24)
# Returns: {"success_rate": 0.05, "total_attacks": 200, "successful_attacks": 10}
```

**Thresholds:**
- **Green:** <5% success rate
- **Yellow:** 5-10% success rate
- **Red:** >10% success rate (CRITICAL ALERT)

**Analysis Queries:**
```promql
# Overall attack success rate (24h)
sum(rate(project_ai_cerberus_blocks_total{attack_type="bypass"}[24h])) / 
sum(rate(project_ai_cerberus_blocks_total[24h]))

# Success rate by attack type
sum by (attack_type) (
  rate(project_ai_cerberus_blocks_total{attack_type!="bypass"}[1h])
) / 
sum(rate(project_ai_cerberus_blocks_total[1h]))

# Trend over 7 days
avg_over_time(
  sum(rate(project_ai_cerberus_blocks_total{attack_type="bypass"}[1h])) / 
  sum(rate(project_ai_cerberus_blocks_total[1h]))
[7d])
```

**Response Actions:**
```python
# If success rate > 10%
if attack_stats["success_rate"] > 0.1:
    # 1. Alert security team
    alert_manager.fire_alert("high_attack_success", metrics)
    
    # 2. Enable emergency lockdown
    security_system.enable_lockdown()
    
    # 3. Analyze recent bypasses
    recent_bypasses = collector.attack_results[-100:]
    successful = [a for a in recent_bypasses if a["success"]]
    
    # 4. Update Cerberus patterns
    for attack in successful:
        cerberus.learn_from_bypass(attack)
```

---

### Time to Detect (TTD)

**Metric:** Time from attack initiation to detection

**Purpose:** Measure security responsiveness

**Collection:**
```python
import time

attack_start = time.time()
# ... attack occurs ...
detection_time_ms = (time.time() - attack_start) * 1000

collector.record_detection_event(
    attack_type="prompt_injection",
    detected=True,
    detection_time_ms=detection_time_ms
)
```

**Calculation:**
```python
ttd_stats = collector.get_time_to_detect(hours=24)
# Returns: {"mean_ms": 150, "median_ms": 120, "p95_ms": 300}
```

**Thresholds:**
- **Target:** p95 < 500ms
- **Warning:** p95 > 1000ms
- **Critical:** p95 > 5000ms

**PromQL Queries:**
```promql
# p95 detection time
histogram_quantile(0.95, 
  rate(project_ai_detection_duration_seconds_bucket[5m])
)

# Detection rate (events per second)
rate(project_ai_detection_events_total[5m])
```

---

### Time to Respond (TTR)

**Metric:** Time from detection to mitigation

**Purpose:** Measure incident response effectiveness

**Collection:**
```python
incident_id = "INC-20260420-001"
response_start = time.time()

# ... apply mitigation ...

response_time = time.time() - response_start

collector.record_response_event(
    incident_id=incident_id,
    response_time_seconds=response_time,
    mitigated=True
)
```

**Thresholds:**
- **Target:** p95 < 60s (1 minute)
- **Warning:** p95 > 300s (5 minutes)
- **Critical:** p95 > 1800s (30 minutes)

---

### False Positive Rate

**Metric:** Legitimate actions incorrectly flagged as threats

**Purpose:** Balance security vs. usability

**Collection:**
```python
# Safety guard detects potential threat
is_actual_threat = human_reviewer_confirms_threat()

collector.record_safety_detection(
    detection_type="harmful_content",
    is_true_positive=is_actual_threat,
    confidence=0.85
)
```

**Calculation:**
```python
fp_stats = collector.get_false_positive_rate(hours=24)
# Returns: {"false_positive_rate": 0.15, "total_detections": 100, "false_positives": 15}
```

**Thresholds:**
- **Green:** <10% false positive rate
- **Yellow:** 10-20% false positive rate
- **Red:** >20% false positive rate (HIGH ALERT)

**Tuning Strategies:**

1. **Adjust Confidence Thresholds:**
   ```python
   # Reduce false positives by increasing threshold
   if detection_confidence < 0.7:
       allow_action()  # Was 0.5, now 0.7
   ```

2. **Whitelist Common Patterns:**
   ```python
   SAFE_PATTERNS = [
       r"how to learn python",  # Educational queries
       r"summarize this document"  # Normal AI tasks
   ]
   ```

3. **Human-in-the-Loop Feedback:**
   ```python
   if user_reports_false_positive:
       # Add to exception list
       safety_guard.add_exception(content_hash)
       
       # Retrain classifier
       classifier.train_on_feedback(
           content=content,
           label="safe"
       )
   ```

---

## Four Laws Enforcement Metrics

### Validation Results

**Metrics:**
- `project_ai_four_laws_validations_total{result="allowed|denied"}`
- `project_ai_four_laws_denials_total{law_violated, severity}`

**Collection:**
```python
from app.core.ai_systems import FourLaws
from app.monitoring.metrics_collector import collector

# Validate action
is_allowed, reason = FourLaws.validate_action(
    action="delete system files",
    context={
        "is_user_order": True,
        "endangers_humanity": False,
        "severity": "high"
    }
)

# Record validation
law_violated = None if is_allowed else reason.split(":")[0]
collector.record_four_laws_validation(
    is_allowed=is_allowed,
    law_violated=law_violated,
    severity=context["severity"]
)
```

**Analysis:**

```promql
# Denial rate by law
sum by (law_violated) (
  rate(project_ai_four_laws_denials_total[1h])
)

# First Law violations (most critical)
project_ai_four_laws_denials_total{law_violated="First"}

# Denials by severity
sum by (severity) (project_ai_four_laws_denials_total)
```

**Interpretation:**

- **First Law Denials:** Human safety violations (CRITICAL)
- **Second Law Denials:** Disobedience to user orders
- **Third Law Denials:** Self-preservation conflicts
- **Fourth Law Denials:** Ethical principle violations

---

### Override Monitoring

**Metrics:**
- `project_ai_four_laws_overrides_total{result, user}`
- `project_ai_command_override_active` (boolean gauge)

**Purpose:** Audit privileged access and override abuse

**Collection:**
```python
# User attempts override
override_success = command_override_system.attempt_override(
    user="admin_user",
    password_hash=sha256_hash,
    command="bypass_safety_check"
)

collector.record_four_laws_override(
    success=override_success,
    user="admin_user"
)

if override_success:
    collector.set_command_override_active(True)
```

**Security Monitoring:**

```promql
# Failed override attempts (potential attack)
sum by (user) (
  rate(project_ai_four_laws_overrides_total{result="failed"}[5m])
)

# Alert if ANY override active
project_ai_command_override_active == 1

# Override duration
time() - (project_ai_command_override_active * time())
```

**Alert Rules:**

1. **Multiple Failed Overrides:** > 3 failures in 5 minutes → Block user
2. **Override Active Too Long:** > 1 hour → Send alert, require re-auth
3. **Unusual Override Time:** Outside business hours → Extra verification

---

## Cerberus Gate Monitoring

### Per-Gate Block Rates

**Metric:** `project_ai_cerberus_blocks_total{attack_type, gate}`

**Purpose:** Track effectiveness of each security gate

**Gate Types:**
- `injection_gate` - Prompt injection detection
- `jailbreak_gate` - Jailbreak attempt detection
- `bypass_gate` - Four Laws bypass detection
- `exfiltration_gate` - Data exfiltration prevention
- `malware_gate` - Malicious content detection

**Collection:**
```python
from app.monitoring.cerberus_dashboard import record_incident

def on_gate_block(gate_name, attack_type, source):
    record_incident({
        "gate": gate_name,
        "type": attack_type,
        "source": source,
        "severity": "high"
    })
```

**Analysis:**

```promql
# Blocks per gate
sum by (gate) (rate(project_ai_cerberus_blocks_total[1h]))

# Most attacked gate
topk(1, sum by (gate) (project_ai_cerberus_blocks_total))

# Gate effectiveness (blocks / attempts)
rate(project_ai_cerberus_blocks_total{attack_type!="bypass"}[1h]) / 
rate(project_ai_cerberus_blocks_total[1h])
```

**Gate Health Dashboard:**

| Gate | Blocks/Hour | Success Rate | Status |
|------|-------------|--------------|--------|
| injection_gate | 50 | 98% | ✅ Healthy |
| jailbreak_gate | 30 | 95% | ✅ Healthy |
| bypass_gate | 5 | 92% | ⚠️ Warning |
| exfiltration_gate | 10 | 99% | ✅ Healthy |

---

### Threat Detection Scores

**Metric:** `project_ai_threat_detection_score{threat_type}` (Gauge 0-1)

**Purpose:** Real-time threat level assessment

**Threat Types:**
- `malware` - Malicious file/URL detection
- `phishing` - Social engineering attempts
- `injection` - Code/prompt injection
- `exfiltration` - Data leak attempts
- `bypass` - Security bypass techniques

**Collection:**
```python
# ML-based threat scoring
threat_score = threat_detector.analyze(content)

collector.record_threat_score(
    threat_type="malware",
    score=threat_score  # 0.0 (safe) to 1.0 (malicious)
)
```

**Thresholds:**

```python
THREAT_LEVELS = {
    "safe": (0.0, 0.3),
    "suspicious": (0.3, 0.6),
    "likely_threat": (0.6, 0.8),
    "confirmed_threat": (0.8, 1.0)
}
```

**Alert Rules:**

```promql
# Any threat score > 0.8
max(project_ai_threat_detection_score) > 0.8

# Multiple concurrent high threats
count(project_ai_threat_detection_score > 0.6) > 3
```

---

## Access Control Metrics

### Authentication Failures

**Metric:** `project_ai_auth_failures_total{user, reason}`

**Failure Reasons:**
- `invalid_password` - Wrong password
- `account_locked` - Too many failures
- `expired` - Password expired
- `mfa_failed` - MFA challenge failed

**Collection:**
```python
from app.core.user_manager import UserManager

user_manager = UserManager()

# Authentication attempt
auth_success = user_manager.authenticate(username, password)

if not auth_success:
    collector.record_auth_failure(
        user=username,
        reason="invalid_password"
    )
```

**Account Lockout Logic:**

```python
# Lock account after 5 failed attempts
failed_attempts = collector.get_auth_failures(user=username, hours=1)
if failed_attempts >= 5:
    user_manager.lock_account(username, duration_minutes=30)
```

**Security Monitoring:**

```promql
# Brute force detection (high failure rate)
sum by (user) (
  rate(project_ai_auth_failures_total[5m])
) > 0.1  # More than 1 failure per 10 seconds

# Account lockout rate
rate(project_ai_auth_failures_total{reason="account_locked"}[1h])
```

---

### Unauthorized Access Attempts

**Metric:** `project_ai_unauthorized_access_total{resource, source_ip}`

**Collection:**
```python
# Access control check
if not user_has_permission(user, resource):
    collector.record_unauthorized_access(
        resource=resource,
        source_ip=request.remote_addr
    )
    return 403  # Forbidden
```

**Analysis:**

```promql
# Most targeted resources
topk(5, sum by (resource) (project_ai_unauthorized_access_total))

# Suspicious IPs (multiple resources)
count by (source_ip) (project_ai_unauthorized_access_total) > 10
```

---

## Black Vault Security

### Access Attempt Monitoring

**Metric:** `project_ai_black_vault_access_attempts_total{user, content_hash}`

**Purpose:** Detect attempts to access forbidden content

**Collection:**
```python
from app.core.ai_systems import LearningRequestManager

manager = LearningRequestManager()

# Check if content in Black Vault
content_hash = hashlib.sha256(content.encode()).hexdigest()

if content_hash in manager.black_vault:
    collector.record_black_vault_access(
        user=current_user,
        content_hash=content_hash
    )
    
    # Log security incident
    logger.critical(
        "Black Vault access attempted by %s: %s",
        current_user, content_hash
    )
    
    return "Content denied"
```

**Alert Rules:**

```promql
# Any Black Vault access attempt
increase(project_ai_black_vault_access_attempts_total[5m]) > 0

# Repeated attempts by same user
sum by (user) (project_ai_black_vault_access_attempts_total) > 3
```

---

## Emergency Protocol Activation

### Emergency Metrics

**Metric:** `project_ai_emergency_activations_total{protocol_type}`

**Protocol Types:**
- `deadman_switch` - Failsafe activation
- `lockdown` - Emergency security lockdown
- `self_destruct` - Data wipe protocol
- `safe_mode` - Restricted operation mode

**Collection:**
```python
# Emergency activation
def activate_emergency_protocol(protocol_type, reason):
    logger.critical(
        "Emergency protocol activated: %s - Reason: %s",
        protocol_type, reason
    )
    
    collector.record_emergency_activation(protocol_type=protocol_type)
    
    # Execute protocol
    if protocol_type == "lockdown":
        security_system.enable_lockdown()
    elif protocol_type == "deadman_switch":
        deadman_switch.trigger()
```

**Alert Rules:**

```promql
# ANY emergency activation
increase(project_ai_emergency_activations_total[5m]) > 0
```

---

## Security Incident Workflow

### Incident Lifecycle

```
Detection → Classification → Response → Mitigation → Resolution
    ↓            ↓              ↓           ↓           ↓
 Metrics    Severity      Notification  Remediation  Post-Mortem
```

### Incident Tracking

```python
from app.monitoring.alert_manager import alert_manager

# Security incident detected
incident_id = alert_manager.create_incident(
    severity="high",
    event_type="four_laws_bypass",
    description="Attempted bypass of First Law via prompt injection",
    metrics_snapshot=current_metrics
)

# Record actions taken
alert_manager.add_incident_action(
    incident_id=incident_id,
    action="Enabled emergency lockdown",
    timestamp=datetime.now()
)

# Resolve incident
alert_manager.resolve_incident(
    incident_id=incident_id,
    resolution_notes="Vulnerability patched, pattern updated"
)
```

---

## Security Dashboards

### Real-Time Security Posture

**Grafana Dashboard Panels:**

1. **Threat Level Indicator** (Gauge)
   - Aggregate threat score across all types
   - Color-coded: Green/Yellow/Red

2. **Attack Timeline** (Graph)
   - Attack attempts over time
   - Stacked by attack type

3. **Four Laws Compliance** (Stat)
   - Validation success rate
   - Critical denials count

4. **Gate Status** (Table)
   - Per-gate block rates
   - Effectiveness percentage

5. **Access Anomalies** (Heatmap)
   - Auth failures by user
   - Unauthorized access by resource

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
- [Alert Rules Configuration](04_alert_rules_configuration.md)
- [Observability Best Practices](08_observability_best_practices.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-security
- **On-Call:** PagerDuty rotation
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/monitoring/security_metrics.py`
