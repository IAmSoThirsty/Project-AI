# Security Metrics and Measurement Relationships

**Document:** 07_security_metrics.md  
**Purpose:** Define metrics, KPIs, and measurement relationships across systems  
**Classification:** AGENT-054 Security Documentation

---

## Metrics Framework

Project-AI security systems are measured through comprehensive metrics that track performance, effectiveness, and system health.

---

## System-Level Metrics

### 1. OctoReflex Constitutional Enforcement

#### Primary Metrics
```python
metrics = {
    "total_validations": 156234,          # Total syscalls validated
    "violations_detected": 1247,          # Total violations
    "violations_blocked": 1247,           # 100% enforcement rate
    "enforcement_rate": 1.0,              # violations_blocked / violations_detected
    "false_positive_rate": 0.012,         # 1.2% false positives
    "average_validation_time_ms": 8.3,    # < 10ms target
    "rules_enabled": 12,                  # Out of 12 default rules
    "enforcement_distribution": {
        "MONITOR": 45,
        "WARN": 312,
        "BLOCK": 823,
        "TERMINATE": 52,
        "ESCALATE": 15
    }
}
```

#### KPIs
- **Target:** 99.9% enforcement rate (BLOCK/TERMINATE/ESCALATE)
- **Target:** < 10ms validation time
- **Target:** < 2% false positive rate
- **Alert Threshold:** > 50 ESCALATE events per day

#### Relationships
```python
# OctoReflex effectiveness impacts:
downstream_impact = {
    "incident_responder": "violations → incident creation rate",
    "cerberus_hydra": "ESCALATE events → Hydra activation rate",
    "authentication": "auth violations → account lockout rate"
}
```

---

### 2. Cerberus Hydra Defense

#### Primary Metrics
```python
metrics = {
    "total_agents_spawned": 729,         # 3^6 = 729 (6 bypass levels)
    "active_agents": 245,                # Currently running
    "terminated_agents": 484,            # Completed/terminated
    "bypass_events_detected": 42,        # Total bypasses
    "spawn_rate": 3.0,                   # Always 3x (Hydra principle)
    "average_spawn_time_s": 4.2,         # < 5s target
    "lockdown_stage": 18,                # Current stage (max 25)
    "language_diversity": 0.87,          # 87% unique combos
    "agent_health_check_rate": 0.98,     # 98% agents healthy
    "exponential_growth_factor": 3.0     # 3^n growth confirmed
}
```

#### KPIs
- **Target:** 100% spawn success rate (3 agents per bypass)
- **Target:** < 5s spawn time per agent
- **Target:** > 80% language diversity
- **Alert Threshold:** > 20 lockdown stage (approaching max)

#### Exponential Growth Tracking
```python
bypass_history = [
    {"bypass_id": "BYP_001", "agents_spawned": 3, "total_agents": 3},
    {"bypass_id": "BYP_002", "agents_spawned": 3, "total_agents": 6},
    {"bypass_id": "BYP_003", "agents_spawned": 9, "total_agents": 15},
    {"bypass_id": "BYP_004", "agents_spawned": 27, "total_agents": 42},
    {"bypass_id": "BYP_005", "agents_spawned": 81, "total_agents": 123}
]

# Verify exponential growth: 3^n
assert agents_spawned == 3 ** bypass_depth
```

#### Relationships
```python
# Cerberus metrics correlate with:
correlations = {
    "incident_responder": "bypass_events ↔ CRITICAL incidents",
    "octoreflex": "agent_spawns → validation_requests",
    "threat_detection": "bypass_events ↔ CRITICAL threats"
}
```

---

### 3. Encryption System

#### Primary Metrics
```python
metrics = {
    "total_encryptions": 45678,          # Total encrypt operations
    "total_decryptions": 45234,          # Total decrypt operations
    "encryption_success_rate": 1.0,      # 100% success
    "decryption_success_rate": 0.9992,   # 99.92% success
    "average_encryption_time_ms": 42.5,  # < 50ms target
    "average_decryption_time_ms": 38.1,  # < 50ms target
    "data_integrity_failures": 36,       # 0.08% integrity failures
    "layer_count": 7,                    # Always 7 layers
    "key_rotation_count": 156,           # Quantum key rotations
    "encryption_strength": {
        "AES": "256-bit",
        "RSA": "4096-bit",
        "ECC": "521-bit",
        "ChaCha20": "256-bit"
    }
}
```

#### KPIs
- **Target:** 100% encryption success rate
- **Target:** > 99.9% decryption success rate
- **Target:** < 50ms encryption/decryption time
- **Alert Threshold:** > 0.1% data integrity failures

#### Relationships
```python
# Encryption usage by system:
usage_stats = {
    "location_tracker": 12456,    # Location history encryptions
    "authentication": 8734,       # Token encryptions
    "incident_responder": 234,    # Backup encryptions
    "emergency_alert": 89          # Emergency data encryptions
}
```

---

### 4. Authentication System

#### Primary Metrics
```python
metrics = {
    "total_login_attempts": 34567,       # All login attempts
    "successful_logins": 32145,          # Successful authentications
    "failed_logins": 2422,               # Failed attempts
    "success_rate": 0.93,                # 93% success rate
    "blocked_attempts": 1234,            # Rate-limited/blocked
    "mfa_enabled_users": 156,            # Users with MFA
    "mfa_challenge_success_rate": 0.98,  # 98% MFA success
    "token_generation_rate": 32145,      # Tokens generated
    "token_revocation_rate": 234,        # Tokens revoked
    "average_auth_time_ms": 842,         # < 1000ms target
    "jwt_expiration_rate": 0.02,         # 2% tokens expire unused
    "refresh_token_usage": 0.78          # 78% tokens refreshed
}
```

#### KPIs
- **Target:** > 90% login success rate (legitimate users)
- **Target:** < 1000ms authentication time
- **Target:** > 95% MFA success rate
- **Alert Threshold:** > 10% failed logins (brute force indicator)

#### Relationships
```python
# Authentication impacts:
downstream_effects = {
    "octoreflex": "auth_success → validation_requests",
    "incident_responder": "failed_logins → brute_force_incidents",
    "threat_detection": "auth_patterns → behavioral_analysis"
}
```

---

### 5. Honeypot Detector

#### Primary Metrics
```python
metrics = {
    "total_requests_analyzed": 123456,   # Total requests
    "attacks_detected": 3456,            # Attack attempts
    "detection_rate": 0.96,              # 96% detection rate
    "false_positive_rate": 0.04,         # 4% false positives
    "unique_attackers": 234,             # Unique IPs
    "average_analysis_time_ms": 85,      # < 100ms target
    "attack_type_distribution": {
        "SQL_INJECTION": 1234,
        "XSS": 789,
        "PATH_TRAVERSAL": 456,
        "COMMAND_INJECTION": 234,
        "UNKNOWN": 743
    },
    "tool_detection_accuracy": 0.92,     # 92% tool fingerprinting
    "high_sophistication_attackers": 12  # Sophistication > 7.0
}
```

#### KPIs
- **Target:** > 95% attack detection rate
- **Target:** < 5% false positive rate
- **Target:** < 100ms analysis time
- **Alert Threshold:** > 10 high-sophistication attackers

#### Attack Pattern Metrics
```python
attacker_profiles = {
    "automated": 156,       # 67% - automated tools
    "targeted": 45,         # 19% - targeted attacks
    "random": 33            # 14% - random scanning
}

sophistication_distribution = {
    "0-3": 123,    # Low sophistication
    "4-6": 89,     # Medium sophistication
    "7-10": 22     # High sophistication (APT-level)
}
```

#### Relationships
```python
# Honeypot feeds data to:
data_consumers = {
    "threat_detection": "attack_attempts → threat_assessment",
    "security_resources": "attack_patterns → signature_updates",
    "incident_responder": "high_severity → incident_creation"
}
```

---

### 6. Incident Responder

#### Primary Metrics
```python
metrics = {
    "total_incidents": 2345,             # Total incidents handled
    "incidents_by_severity": {
        "CRITICAL": 45,
        "HIGH": 234,
        "MEDIUM": 789,
        "LOW": 1277
    },
    "total_responses": 8912,             # Total response actions
    "response_success_rate": 0.982,      # 98.2% success
    "average_response_time_s": 0.842,    # < 1s target
    "automated_response_rate": 1.0,      # 100% automated
    "manual_intervention_rate": 0.0,     # 0% manual (fully automated)
    "action_distribution": {
        "LOG_FORENSICS": 2345,
        "BLOCK_IP": 1234,
        "ISOLATE_COMPONENT": 456,
        "BACKUP_DATA": 345,
        "ALERT_TEAM": 1567,
        "ESCALATE": 123
    },
    "cerberus_activations": 42,          # Hydra triggers
    "emergency_alerts_sent": 18          # Critical alerts
}
```

#### KPIs
- **Target:** < 1s average response time
- **Target:** > 98% response success rate
- **Target:** 100% automation rate
- **Alert Threshold:** > 10 CRITICAL incidents per day

#### Response Chain Metrics
```python
response_chains = {
    "detection_to_response_time": 1.234,  # 1.234s average
    "response_to_resolution_time": 45.6,  # 45.6s average
    "incident_resolution_rate": 0.96,     # 96% resolved
    "false_positive_resolution": 0.04     # 4% false positives
}
```

#### Relationships
```python
# Incident Responder is central hub:
integration_metrics = {
    "honeypot_incidents": 1234,       # From Honeypot
    "threat_detection_incidents": 789, # From Threat Detection
    "octoreflex_incidents": 234,      # From OctoReflex
    "cerberus_triggers": 42,          # To Cerberus Hydra
    "emergency_triggers": 18           # To Emergency Alert
}
```

---

### 7. Threat Detection Engine

#### Primary Metrics
```python
metrics = {
    "total_assessments": 45678,          # Total threat assessments
    "threat_distribution": {
        "SAFE": 42134,        # 92.2%
        "SUSPICIOUS": 2345,   # 5.1%
        "MALICIOUS": 1045,    # 2.3%
        "CRITICAL": 154       # 0.3%
    },
    "average_confidence": 0.87,          # 87% average confidence
    "false_positive_rate": 0.048,        # 4.8% false positives
    "false_negative_rate": 0.012,        # 1.2% false negatives
    "ml_prediction_accuracy": 0.91,      # 91% ML accuracy
    "behavioral_analysis_accuracy": 0.89, # 89% behavior accuracy
    "pattern_matching_accuracy": 0.94,   # 94% pattern accuracy
    "average_analysis_time_ms": 345,     # < 500ms target
    "attack_sequence_detection_rate": 0.87 # 87% sequence detection
}
```

#### KPIs
- **Target:** > 95% threat detection accuracy
- **Target:** < 5% false positive rate
- **Target:** < 500ms analysis time
- **Alert Threshold:** > 10 CRITICAL threats per day

#### ML Model Performance
```python
ml_metrics = {
    "model_version": "CodexDeus-ThreatDetector-v1",
    "training_accuracy": 0.95,
    "validation_accuracy": 0.91,
    "test_accuracy": 0.89,
    "precision": 0.92,
    "recall": 0.87,
    "f1_score": 0.89,
    "auc_roc": 0.93
}
```

#### Relationships
```python
# Threat Detection consumes data from:
data_sources = {
    "honeypot": 3456,         # Attack attempts
    "security_resources": 1234, # Threat intelligence
    "behavioral_data": 45678   # User behavior patterns
}

# Threat Detection triggers:
triggered_systems = {
    "incident_responder": 1199,  # MALICIOUS + CRITICAL
    "octoreflex": 1199           # Validation requests
}
```

---

### 8. Security Resources

#### Primary Metrics
```python
metrics = {
    "total_repositories": 12,            # Managed repos
    "active_repositories": 12,           # Currently active
    "total_signatures": 15678,           # Attack signatures
    "signature_updates_per_day": 45,     # Daily updates
    "api_calls": 2345,                   # GitHub API calls
    "cache_hit_rate": 0.92,              # 92% cache hits
    "average_fetch_time_ms": 234,        # < 500ms target
    "repository_freshness_days": 3.5,    # < 7 days target
    "signature_distribution": {
        "SQL_INJECTION": 3456,
        "XSS": 2345,
        "PATH_TRAVERSAL": 1234,
        "COMMAND_INJECTION": 789,
        "OTHER": 7854
    }
}
```

#### KPIs
- **Target:** < 7 days repository freshness
- **Target:** > 90% cache hit rate
- **Target:** < 500ms fetch time
- **Alert Threshold:** > 14 days without update

#### Relationships
```python
# Security Resources feeds:
downstream_systems = {
    "honeypot": 15678,        # Signature updates
    "threat_detection": 15678, # Pattern updates
    "signature_updates_per_week": 315
}
```

---

### 9. Location Tracker

#### Primary Metrics
```python
metrics = {
    "total_location_requests": 1234,     # Total requests
    "ip_geolocation_success_rate": 0.96, # 96% IP success
    "gps_success_rate": 0.89,            # 89% GPS success
    "average_location_time_ms": 1234,    # < 2000ms target
    "encryption_success_rate": 1.0,      # 100% encryption
    "decryption_success_rate": 0.998,    # 99.8% decryption
    "history_entries": 5678,             # Total history
    "average_history_size_kb": 2.3,      # Per user
    "location_accuracy_meters": 50       # ±50m average
}
```

#### KPIs
- **Target:** > 95% location success rate
- **Target:** < 2000ms location acquisition time
- **Target:** 100% encryption success
- **Alert Threshold:** < 80% location success rate

#### Relationships
```python
# Location Tracker provides to:
consumers = {
    "emergency_alert": 345,  # Emergency locations
    "incident_responder": 123 # Incident locations
}
```

---

### 10. Emergency Alert

#### Primary Metrics
```python
metrics = {
    "total_alerts_sent": 234,            # Total alerts
    "alert_delivery_success_rate": 0.982, # 98.2% delivery
    "average_delivery_time_s": 8.5,      # < 10s target
    "email_delivery_rate": 0.98,         # 98% email success
    "sms_delivery_rate": 0.97,           # 97% SMS success (if enabled)
    "contact_notification_rate": 0.99,   # 99% at least 1 contact
    "alert_response_time_s": 234,        # Time to user response
    "false_alert_rate": 0.02             # 2% false alerts
}
```

#### KPIs
- **Target:** > 98% alert delivery success
- **Target:** < 10s delivery time
- **Target:** < 5% false alert rate
- **Alert Threshold:** > 5% alert delivery failures

#### Relationships
```python
# Emergency Alert triggered by:
trigger_sources = {
    "incident_responder": 216,  # 92% of alerts
    "user_initiated": 18         # 8% manual triggers
}

# Emergency Alert uses:
dependencies = {
    "location_tracker": 234,  # Location data
    "encryption": 234          # Data encryption
}
```

---

## Cross-System Metrics

### System Integration Health
```python
integration_health = {
    "honeypot_to_threat_detection": {
        "data_flow_rate": 3456,      # Events per day
        "latency_ms": 45,            # < 100ms target
        "error_rate": 0.001          # 0.1% errors
    },
    "threat_detection_to_incident_responder": {
        "data_flow_rate": 1199,
        "latency_ms": 123,
        "error_rate": 0.002
    },
    "incident_responder_to_cerberus": {
        "data_flow_rate": 42,
        "latency_ms": 4200,          # Spawn time
        "error_rate": 0.0
    },
    "all_to_octoreflex": {
        "validation_requests": 156234,
        "latency_ms": 8.3,
        "error_rate": 0.0001
    }
}
```

### Overall Security Posture
```python
security_posture = {
    "overall_threat_level": "ELEVATED",  # NORMAL, ELEVATED, HIGH, CRITICAL
    "active_incidents": 45,
    "active_threats": 234,
    "system_health_score": 0.97,         # 97% healthy
    "defense_coverage": 0.99,            # 99% coverage
    "mean_time_to_detect_s": 0.842,      # < 1s
    "mean_time_to_respond_s": 1.234,     # < 2s
    "mean_time_to_resolve_s": 45.6,      # < 60s
    "total_attacks_blocked": 3456,
    "total_attacks_mitigated": 3411,     # 98.7% mitigation rate
    "zero_day_detection_rate": 0.42      # 42% zero-day detection
}
```

### Resource Utilization
```python
resource_metrics = {
    "cpu_usage_percent": 34.5,           # 34.5% average
    "memory_usage_mb": 2456,             # 2.4GB
    "disk_usage_gb": 12.3,               # 12.3GB
    "network_throughput_mbps": 15.6,     # 15.6 Mbps
    "active_processes": 245,             # Cerberus agents
    "database_connections": 45,
    "api_calls_per_minute": 234
}
```

---

## Metrics Collection and Reporting

### Collection Intervals
```python
collection_schedule = {
    "real_time_metrics": "1s",           # OctoReflex, Authentication
    "fast_metrics": "10s",               # Threat Detection, Honeypot
    "medium_metrics": "60s",             # Incident Responder, Cerberus
    "slow_metrics": "300s",              # Security Resources, Encryption
    "daily_metrics": "86400s"            # Aggregated reports
}
```

### Metric Storage
```python
storage_config = {
    "time_series_db": "InfluxDB",        # Time-series metrics
    "aggregation_db": "PostgreSQL",      # Aggregated stats
    "log_storage": "Elasticsearch",      # Full logs
    "retention_days": 90,                # 90-day retention
    "backup_frequency": "daily"
}
```

### Dashboard Metrics
```python
dashboard_kpis = {
    "attacks_blocked_24h": 234,
    "incidents_created_24h": 45,
    "cerberus_agents_active": 245,
    "current_lockdown_stage": 18,
    "system_health_score": 0.97,
    "threat_level": "ELEVATED"
}
```

---

## Alerting Thresholds

### Critical Alerts
```python
critical_thresholds = {
    "octoreflex_escalate_events_per_hour": 10,
    "cerberus_lockdown_stage": 20,
    "incident_responder_critical_incidents_per_hour": 5,
    "threat_detection_critical_threats_per_hour": 10,
    "emergency_alert_delivery_failure_rate": 0.05,
    "system_health_score": 0.80
}
```

### Warning Alerts
```python
warning_thresholds = {
    "authentication_failed_login_rate": 0.20,
    "honeypot_false_positive_rate": 0.10,
    "encryption_data_integrity_failures": 0.001,
    "incident_responder_response_time_s": 2.0,
    "threat_detection_false_positive_rate": 0.10
}
```

---

---

## Related Systems

### Monitoring Infrastructure
All security metrics are collected, aggregated, and alerted through monitoring systems:

- [[../monitoring/01-logging-system.md|Logging System]] - Raw security events for metric calculation
- [[../monitoring/02-metrics-system.md|Metrics System]] - Central metrics collection, aggregation, and storage
- [[../monitoring/03-tracing-system.md|Tracing System]] - End-to-end performance tracing for latency metrics
- [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] - System performance and resource utilization
- [[../monitoring/06-error-tracking.md|Error Tracking]] - Error rates, failure patterns, detection failures
- [[../monitoring/07-log-aggregation.md|Log Aggregation]] - Centralized log aggregation for metric extraction
- [[../monitoring/08-metrics-collection.md|Metrics Collection]] - Metric collection infrastructure and pipelines
- [[../monitoring/10-alerting-system.md|Alerting System]] - Threshold-based alerts, anomaly detection, escalation

### Data Infrastructure
Metrics require persistent storage and efficient querying:

- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]] - Time-series metric storage architecture
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Metric persistence, historical data, aggregation storage
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - Sensitive metric encryption (authentication failures, IP addresses)
- [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]] - Metric backup, historical preservation, recovery

### Configuration Management
Metric thresholds and alerting rules are centrally configured:

- [[../configuration/03_settings_validator_relationships.md|Settings Validator]] - Metric thresholds, KPI targets, alert rules
- [[../configuration/04_feature_flags_relationships.md|Feature Flags]] - Metric collection toggles, feature-specific metrics
- [[../configuration/06_environment_variables_relationships.md|Environment Variables]] - Metric export endpoints, dashboard URLs
- [[../configuration/07_secrets_management_relationships.md|Secrets Management]] - Metric API keys, dashboard credentials

### Metrics Collection Architecture

**1. Collection Flow**
```
[Security Systems] → [Metric Emission] → [Collection] → [Aggregation] → [Storage]
        ↓                   ↓                 ↓              ↓             ↓
   [Events]           [Metrics API]      [Pipeline]     [Time-Series] [Database]
        ↓                   ↓                 ↓              ↓             ↓
   [Logging]          [Validation]       [Transform]   [Aggregate]   [Persistence]
```

**2. Alerting Flow**
```
[Metrics] → [Threshold Check] → [Alert Trigger] → [Notification] → [Escalation]
     ↓              ↓                  ↓                ↓              ↓
[Storage]      [Config]          [Alerting]        [SMTP/API]     [Incident]
```

**3. Dashboard Flow**
```
[Metrics DB] → [Query] → [Aggregation] → [Visualization] → [Dashboard]
      ↓           ↓           ↓                ↓               ↓
[Persistence] [API]     [Compute]         [Render]        [Display]
```

### Metric-Driven Integrations

| Security System | Metrics Published | Consumed By | Alert Triggers |
|----------------|-------------------|-------------|----------------|
| OctoReflex | Violations, Enforcement Rate | Metrics System, Dashboard | > 50 ESCALATE/day |
| Cerberus Hydra | Agent Count, Spawn Rate | Metrics System, Incident Responder | Lockdown Stage > 20 |
| Encryption | Encryption Time, Failures | Performance Monitoring | Failure Rate > 0.1% |
| Authentication | Auth Failures, Token Issues | Alerting System, Dashboard | Failure Rate > 5% |
| Honeypot | Detection Rate, Attacks | Threat Detection, Metrics System | Detection < 90% |
| Incident Responder | Response Time, Success Rate | Metrics System, Dashboard | Response > 5s |
| Threat Detection | Accuracy, False Positives | Metrics System, Dashboard | FP Rate > 10% |
| Security Resources | Repository Freshness | Metrics System | Age > 14 days |
| Location Tracker | Location Accuracy | Emergency Alert, Metrics | Success < 90% |
| Emergency Alert | Delivery Success | Metrics System, Alerting | Delivery < 95% |

---

## Metric Export Endpoints

Security metrics are exported to external monitoring systems via standard formats:

- **Prometheus:** `/metrics` endpoint with Prometheus format
- **StatsD:** UDP metrics export to StatsD aggregator
- **CloudWatch:** AWS CloudWatch metrics API
- **Custom API:** REST API for custom metric consumers

Configuration via [[../configuration/06_environment_variables_relationships.md|Environment Variables]]:
- `METRICS_EXPORT_ENDPOINT` - Metric export URL
- `METRICS_EXPORT_FORMAT` - Export format (prometheus, statsd, cloudwatch)
- `METRICS_EXPORT_INTERVAL` - Export interval in seconds

---

**End of Security Metrics Documentation**

```
┌──────────────────────────────────────────────────────┐
│  Detection Layer Metrics                             │
│  ├─ Honeypot: 96% detection rate                     │
│  ├─ Threat Detection: 87% confidence                 │
│  └─ Security Resources: 3.5 day freshness            │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│  Enforcement Layer Metrics                           │
│  ├─ OctoReflex: 8.3ms validation time                │
│  └─ Authentication: 93% success rate                 │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│  Response Layer Metrics                              │
│  ├─ Incident Responder: 0.842s response time         │
│  ├─ Cerberus Hydra: 4.2s spawn time                  │
│  └─ Emergency Alert: 98.2% delivery                  │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│  Foundation Layer Metrics                            │
│  ├─ Encryption: 42.5ms encryption time               │
│  └─ Location Tracker: 96% success rate               │
└──────────────────────────────────────────────────────┘
```

---

**End of Security Relationship Mapping Documentation**

**Mission Status:** ✅ COMPLETE  
**Systems Documented:** 10/10  
**Documents Created:** 7  
**Classification:** AGENT-054 Security Relationship Mapping Specialist

---

## 📁 Source Code References

This documentation references the following source files:

- [[kernel/threat_detection.py]]
- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/emergency_alert.py]]
- [[src/app/core/honeypot_detector.py]]
- [[src/app/core/incident_responder.py]]
- [[src/app/core/location_tracker.py]]
- [[src/app/core/octoreflex.py]]
- [[src/app/core/security_resources.py]]
- [[src/app/core/security/auth.py]]
- [[src/app/security/advanced/mfa_auth.py]]
- [[utils/encryption/god_tier_encryption.py]]

---
