# Security Monitoring and Alerting

## Overview

SecurityMonitor provides AWS CloudWatch integration, SNS alerting, structured audit logging, and threat campaign signature tracking. It enables centralized security event logging with cloud-native monitoring and alerting capabilities.

**Location:** `src/app/security/monitoring.py` (431 lines)

**Core Philosophy:** Centralized logging, automated alerting, cloud-native monitoring.

---

## Architecture

### Data Structures

```python
@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_type: str              # e.g., 'authentication_failure'
    severity: str                # critical, high, medium, low
    source: str                  # Event source
    description: str             # Event description
    metadata: dict[str, Any]     # Additional context
    timestamp: float             # Unix timestamp
```

---

## API Reference

### Initialization

```python
from app.security.monitoring import SecurityMonitor

monitor = SecurityMonitor(
    region="us-east-1",                              # AWS region
    sns_topic_arn="arn:aws:sns:us-east-1:123456789:security-alerts",
    cloudwatch_namespace="ProjectAI/Security"        # Metrics namespace
)

# Without AWS credentials: Falls back to local logging only
monitor_local = SecurityMonitor()  # boto3 features disabled
```

### Log Security Event

```python
# Log event with auto-alerting
monitor.log_security_event(
    event_type="authentication_failure",
    severity="high",
    source="login_api",
    description="Multiple failed login attempts from suspicious IP",
    metadata={
        "ip_address": "192.168.1.100",
        "username": "admin",
        "attempts": 10,
        "time_window": "60s"
    }
)

# Auto-actions:
# 1. Log to standard Python logging
# 2. Send to CloudWatch Metrics (if configured)
# 3. Send SNS alert (if severity is high/critical)
```

**Severity Levels:**
- **critical:** Immediate action required (root access, data breach)
- **high:** Serious security issue (privilege escalation, bypass)
- **medium:** Potential security issue (unusual activity, policy violation)
- **low:** Informational (failed login, access denied)

### Threat Signatures

```python
# Add threat campaign signature
monitor.add_threat_signature(
    campaign_name="log4shell",
    indicators=[
        "${jndi:ldap://",
        "${jndi:rmi://",
        "${jndi:dns://",
        "jndi:ldap://"
    ]
)

monitor.add_threat_signature(
    campaign_name="wannacry",
    indicators=[
        "192.168.1.50",           # Known C2 server
        "malicious.example.com",
        "43f3e2c8d9a1b2e4"        # File hash
    ]
)

# Check data against signatures
data = "User-Agent: ${jndi:ldap://malicious.com/exploit}"
matches = monitor.check_threat_signatures(data)

if matches:
    print(f"Threat signatures matched: {matches}")
    monitor.log_security_event(
        event_type="threat_signature_detected",
        severity="critical",
        source="threat_intel",
        description=f"Known threat campaign detected: {', '.join(matches)}",
        metadata={"campaigns": matches, "data_sample": data[:100]}
    )
```

### Event Statistics

```python
# Get statistics for time window
stats = monitor.get_event_statistics(time_window=3600)  # Last hour

print(f"""
Event Statistics (Last Hour):
- Total events: {stats['total_events']}
- By severity:
  - Critical: {stats['by_severity'].get('critical', 0)}
  - High: {stats['by_severity'].get('high', 0)}
  - Medium: {stats['by_severity'].get('medium', 0)}
  - Low: {stats['by_severity'].get('low', 0)}
- By type:
  {stats['by_type']}
- By source:
  {stats['by_source']}
""")

# Get all-time statistics
all_stats = monitor.get_event_statistics()
```

### Anomaly Detection

```python
# Detect anomalous event patterns
anomalies = monitor.detect_anomalies(
    time_window=3600,  # Last hour
    threshold=10       # Events to trigger anomaly
)

for anomaly in anomalies:
    print(f"""
    Anomaly Detected:
    - Event type: {anomaly['event_type']}
    - Count: {anomaly['count']}
    - Time window: {anomaly['time_window']}s
    - Threshold: {anomaly['threshold']}
    """)
    
    # Log anomaly as high severity event
    monitor.log_security_event(
        event_type="anomaly_detected",
        severity="high",
        source="anomaly_detector",
        description=f"Unusual spike in {anomaly['event_type']} events",
        metadata=anomaly
    )
```

### Export Audit Log

```python
# Export to JSON
monitor.export_audit_log(
    output_path="data/audit_logs/security_20240115.json",
    format="json"
)

# Export to CSV
monitor.export_audit_log(
    output_path="data/audit_logs/security_20240115.csv",
    format="csv"
)
```

---

## AWS Integration

### CloudWatch Metrics

**Automatic metric publishing:**
```python
# Each logged event creates CloudWatch metric:
# - Metric name: SecurityEvent_{event_type}
# - Value: 1 (count)
# - Dimensions: Severity, Source
# - Namespace: ProjectAI/Security

# View in AWS Console: CloudWatch > Metrics > ProjectAI/Security
```

**Custom CloudWatch queries:**
```python
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

# Get authentication failure count
response = cloudwatch.get_metric_statistics(
    Namespace='ProjectAI/Security',
    MetricName='SecurityEvent_authentication_failure',
    Dimensions=[{'Name': 'Severity', 'Value': 'high'}],
    StartTime=datetime.now() - timedelta(hours=1),
    EndTime=datetime.now(),
    Period=300,  # 5 minutes
    Statistics=['Sum']
)

print(f"Auth failures (last hour): {sum(p['Sum'] for p in response['Datapoints'])}")
```

### SNS Alerts

**Alert message structure:**
```json
{
  "default": "Security Alert: authentication_failure",
  "email": "Security Alert\n==============\n\nType: authentication_failure\nSeverity: high\nSource: login_api\nTime: 2024-01-15 10:30:45\n\nDescription:\nMultiple failed login attempts\n\nMetadata:\n{\n  \"ip_address\": \"192.168.1.100\",\n  \"attempts\": 10\n}\n",
  "sms": "Security Alert (high): authentication_failure"
}
```

**SNS topic subscription:**
```bash
# Subscribe email to SNS topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789:security-alerts \
  --protocol email \
  --notification-endpoint security@example.com

# Subscribe SMS
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789:security-alerts \
  --protocol sms \
  --notification-endpoint +1234567890
```

---

## Integration Patterns

### Cerberus Hydra Integration

```python
from app.core.cerberus_hydra import CerberusHydraDefense
from app.security.monitoring import SecurityMonitor

hydra = CerberusHydraDefense(data_dir="data")
monitor = SecurityMonitor()

# Log bypass events
@hydra.on_bypass
def log_bypass(event):
    monitor.log_security_event(
        event_type="cerberus_bypass",
        severity="critical",
        source="cerberus_hydra",
        description=f"Security agent bypassed: {event['bypass_type']}",
        metadata={
            "agent_id": event['agent_id'],
            "bypass_type": event['bypass_type'],
            "risk_score": event['risk_score']
        }
    )

# Log agent spawns
@hydra.on_spawn
def log_spawn(agent_id, generation):
    monitor.log_security_event(
        event_type="cerberus_agent_spawned",
        severity="medium",
        source="cerberus_hydra",
        description=f"Defense agent spawned (generation {generation})",
        metadata={"agent_id": agent_id, "generation": generation}
    )
```

### Application Security Events

```python
# Authentication failures
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if not authenticate(username, password):
        monitor.log_security_event(
            event_type="authentication_failure",
            severity="medium",
            source="login_api",
            description=f"Failed login attempt for user {username}",
            metadata={
                "username": username,
                "ip_address": request.remote_addr,
                "user_agent": request.user_agent.string
            }
        )
        return jsonify({"error": "Invalid credentials"}), 401
    
    return jsonify({"token": generate_token(username)})

# Authorization failures
def check_admin_permission(user):
    if not user.is_admin:
        monitor.log_security_event(
            event_type="authorization_failure",
            severity="high",
            source="admin_panel",
            description=f"Unauthorized admin access attempt by {user.username}",
            metadata={"user_id": user.id, "username": user.username}
        )
        raise PermissionError("Admin access required")
```

### Structured Logging

```python
from app.security.monitoring import StructuredLogger

# Create structured logger
logger = StructuredLogger(log_path="data/audit_logs/security.log")

# Log with structured fields
logger.info("User login successful", 
    user_id=123,
    username="alice",
    ip_address="192.168.1.10"
)

logger.error("Database connection failed",
    error_code="DB_CONN_TIMEOUT",
    database="postgresql",
    retry_count=3
)

logger.critical("Security breach detected",
    breach_type="privilege_escalation",
    affected_users=["admin", "root"],
    containment_status="in_progress"
)

# Log file format (JSONL):
# {"timestamp": 1705315845.123, "level": "info", "message": "User login successful", "user_id": 123, ...}
```

---

## Threat Intelligence

### Pre-Built Threat Signatures

```python
# Common attack patterns
THREAT_SIGNATURES = {
    "sql_injection": [
        "' OR '1'='1",
        "'; DROP TABLE",
        "UNION SELECT",
        "' OR 1=1--"
    ],
    "xss": [
        "<script>alert(",
        "javascript:",
        "onerror=",
        "<img src=x onerror="
    ],
    "path_traversal": [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "%2e%2e%2f",
        "....//....//....//etc/passwd"
    ],
    "log4shell": [
        "${jndi:ldap://",
        "${jndi:rmi://",
        "${jndi:dns://",
        "${lower:jndi:"
    ],
    "command_injection": [
        "; cat /etc/passwd",
        "| whoami",
        "`id`",
        "$(curl malicious.com)"
    ]
}

# Load all signatures
for campaign, indicators in THREAT_SIGNATURES.items():
    monitor.add_threat_signature(campaign, indicators)
```

### External Threat Feeds

```python
import requests

# Load threat intelligence from external feed
def load_threat_feed(feed_url):
    response = requests.get(feed_url)
    threat_data = response.json()
    
    for threat in threat_data['threats']:
        monitor.add_threat_signature(
            campaign_name=threat['name'],
            indicators=threat['indicators']
        )
    
    print(f"Loaded {len(threat_data['threats'])} threat signatures")

# Example feed
load_threat_feed("https://threat-intel.example.com/feeds/latest.json")
```

---

## Performance Considerations

### Memory Usage

- **Event Log:** ~1 KB per event
- **Threat Signatures:** ~100 KB (depends on indicator count)
- **In-Memory Events:** Unbounded (export periodically to disk)

### Optimization

```python
# Limit in-memory event log size
MAX_EVENTS = 10000

def log_event_with_rotation(monitor, event_type, severity, source, description, metadata):
    monitor.log_security_event(event_type, severity, source, description, metadata)
    
    # Rotate if too many events
    if len(monitor.event_log) > MAX_EVENTS:
        # Export to disk
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        monitor.export_audit_log(
            f"data/audit_logs/security_{timestamp}.json",
            format="json"
        )
        
        # Keep only recent events
        monitor.event_log = monitor.event_log[-5000:]
```

### AWS Cost Optimization

```python
# Reduce CloudWatch/SNS usage in non-production
import os

environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    monitor = SecurityMonitor(
        region="us-east-1",
        sns_topic_arn="arn:aws:sns:...",
        cloudwatch_namespace="ProjectAI/Security"
    )
else:
    # Local logging only (no AWS costs)
    monitor = SecurityMonitor()
```

---

## Monitoring Dashboard

### Grafana Dashboard Setup

```yaml
# grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-dashboard
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Security Events",
        "panels": [
          {
            "title": "Critical Events (Last Hour)",
            "targets": [{
              "expr": "sum(cloudwatch_projectai_security_securityevent{severity='critical'})"
            }]
          },
          {
            "title": "Authentication Failures",
            "targets": [{
              "expr": "rate(cloudwatch_projectai_security_securityevent_authentication_failure[5m])"
            }]
          },
          {
            "title": "Top Event Sources",
            "targets": [{
              "expr": "topk(10, sum by (source) (cloudwatch_projectai_security_securityevent))"
            }]
          }
        ]
      }
    }
```

---

## Best Practices

1. **Structured Logging:** Use StructuredLogger for all security events
2. **Severity Classification:** Correctly classify event severity (don't overuse critical)
3. **Metadata Richness:** Include IP, user, action in metadata for forensics
4. **Regular Export:** Export audit logs daily to prevent memory growth
5. **Threat Signatures:** Update threat signatures weekly from threat feeds
6. **Alert Fatigue:** Set appropriate SNS alert thresholds to avoid noise
7. **Cost Monitoring:** Monitor CloudWatch/SNS usage in production

---


---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/security/auth.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]

---
## Related Documentation

- [01-cerberus-hydra-defense.md](01-cerberus-hydra-defense.md) - Logs bypass/spawn events
- [04-observability-metrics.md](04-observability-metrics.md) - Prometheus metrics
- [06-agent-security.md](06-agent-security.md) - Agent-level security events

---

## See Also

- [AWS CloudWatch Integration Guide](../../docs/AWS_CLOUDWATCH.md)
- [Threat Intelligence Feeds](../../docs/THREAT_INTEL.md)
- [Security Event Taxonomy](../../docs/SECURITY_EVENTS.md)
