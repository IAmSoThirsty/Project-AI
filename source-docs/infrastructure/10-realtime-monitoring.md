# Real-Time Monitoring System

**Module:** `src/app/core/realtime_monitoring.py`  
**Type:** Core Infrastructure  
**Dependencies:** threading, requests, collections  
**Related Modules:** telemetry.py, data_persistence.py

---

## Overview

The Real-Time Monitoring System provides streaming data architecture for the Global Scenario Engine with incremental updates, real-time alerts, webhook notifications, and dashboard metrics for production observability.

### Core Features

- **Incremental Updates**: Update specific countries/domains without full reload
- **Real-Time Alert System**: Threshold-based alerts with subscriber pattern
- **Webhook Notifications**: HTTP POST notifications to external systems
- **Monitoring Dashboard**: Real-time metrics and historical data
- **Background Monitoring**: Daemon threads for continuous surveillance

---

## Architecture

```
Real-Time Monitoring System
├── IncrementalUpdateManager (granular data updates)
├── RealTimeAlertSystem (threshold alerts + subscribers)
├── WebhookNotifier (HTTP POST to external systems)
└── MonitoringDashboard (metrics + history export)
```

---

## Core Classes

### IncrementalUpdateManager

```python
from app.core.realtime_monitoring import IncrementalUpdateManager
from app.core.simulation_contingency_root import GlobalScenarioEngine

# Initialize with scenario engine
engine = GlobalScenarioEngine()
update_manager = IncrementalUpdateManager(engine)

# Update specific country/domain/year (no full reload)
success = update_manager.update_country_data(
    country="USA",
    domain="economic",
    year=2026,
    value=0.75  # New risk score
)

if success:
    print("Country data updated successfully")

# Get update history (last 100 updates)
history = update_manager.get_update_history(limit=100)
for update in history:
    print(f"{update['timestamp']}: {update['country']}/{update['domain']} "
          f"changed from {update['old_value']} to {update['new_value']}")
```

**Update Log Structure:**
```python
{
    "timestamp": "2026-04-20T14:00:00+00:00",
    "country": "USA",
    "domain": "economic",
    "year": 2026,
    "old_value": 0.68,
    "new_value": 0.75
}
```

---

### RealTimeAlertSystem

```python
from app.core.realtime_monitoring import RealTimeAlertSystem

# Initialize with scenario engine
alert_system = RealTimeAlertSystem(
    engine=engine,
    alert_threshold=0.7  # Alert on scenarios with 70%+ likelihood
)

# Subscribe to alerts (callback function)
def handle_alert(alert):
    """Handle crisis alert."""
    print(f"🚨 ALERT: {alert.scenario.title}")
    print(f"   Risk Score: {alert.risk_score}")
    print(f"   Likelihood: {alert.scenario.likelihood:.1%}")
    print(f"   Year: {alert.scenario.year}")
    print(f"   Summary: {alert.explainability[:200]}...")
    
    # Send notifications (email, Slack, PagerDuty, etc.)
    send_email_notification(alert)
    send_slack_alert(alert)

alert_system.subscribe(handle_alert)

# Start continuous monitoring (background thread)
alert_system.start_monitoring(interval=3600)  # Check every hour

# Manually trigger alert check
alert_system.check_for_alerts()

# Stop monitoring
alert_system.stop_monitoring()

# Unsubscribe from alerts
alert_system.unsubscribe(handle_alert)
```

**Alert Flow:**
```
1. Background thread runs every N seconds
2. Re-runs scenario simulation
3. Generates alerts for scenarios above threshold
4. Emits alerts to all subscribers
5. Subscribers handle alerts (notifications, logging, etc.)
```

---

### WebhookNotifier

```python
from app.core.realtime_monitoring import WebhookNotifier

# Initialize with webhook URLs
notifier = WebhookNotifier(webhook_urls=[
    "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
    "https://api.pagerduty.com/incidents",
    "https://custom-alerting-system.example.com/webhook"
])

# Add webhook dynamically
notifier.add_webhook("https://new-webhook.example.com/alerts")

# Remove webhook
notifier.remove_webhook("https://old-webhook.example.com/alerts")

# Subscribe to alert system
alert_system.subscribe(notifier.notify)

# Webhook payload structure
"""
POST /webhook
Content-Type: application/json

{
  "timestamp": "2026-04-20T14:30:00+00:00",
  "alert": {
    "alert_id": "alert_abc123",
    "risk_score": 0.85,
    "scenario_title": "Global Economic Collapse",
    "likelihood": 0.75,
    "severity": "critical",
    "year": 2027,
    "summary": "High probability of economic crisis..."
  }
}
"""

# Get notification history
history = notifier.notification_log
for entry in history:
    print(f"{entry['timestamp']}: {entry['url']} - {entry['status']}")
```

**Webhook Retry Logic:**
```python
# Automatic retry with exponential backoff (not implemented in base class)
# Recommended enhancement:
def notify_with_retry(alert, max_retries=3):
    for attempt in range(max_retries):
        try:
            notifier.notify(alert)
            break
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Webhook notification failed after {max_retries} attempts: {e}")
```

---

### MonitoringDashboard

```python
from app.core.realtime_monitoring import MonitoringDashboard

# Initialize with scenario engine
dashboard = MonitoringDashboard(engine)

# Get current metrics
metrics = dashboard.get_current_metrics()
print(f"Data Points: {metrics['data_points']}")
print(f"Countries: {metrics['countries']}")
print(f"Domains: {metrics['domains']}")
print(f"Scenarios: {metrics['scenarios']}")
print(f"Alerts: {metrics['alerts']}")
print(f"Top Risks: {metrics['top_risks']}")

"""
Example output:
{
  "timestamp": "2026-04-20T14:00:00+00:00",
  "data_points": 15000,
  "countries": 195,
  "domains": 8,
  "threshold_events": 42,
  "scenarios": 120,
  "alerts": 15,
  "top_risks": [
    {
      "title": "Global Economic Crisis",
      "likelihood": 0.85,
      "year": 2027,
      "severity": "critical"
    },
    ...
  ]
}
"""

# Get metrics history (last 60 minutes)
history = dashboard.get_metrics_history(minutes=60)
for metric in history:
    print(f"{metric['timestamp']}: {metric['scenarios']} scenarios, {metric['alerts']} alerts")

# Export dashboard state to file
dashboard.export_dashboard_state("dashboard_snapshot_2026-04-20.json")
```

**Dashboard Metrics:**
- `data_points`: Total historical data entries
- `countries`: Number of countries tracked
- `domains`: Risk domains (economic, political, environmental, etc.)
- `threshold_events`: Events exceeding thresholds
- `scenarios`: Generated scenarios
- `alerts`: Active alerts
- `top_risks`: Top 5 highest-likelihood scenarios

---

## Factory Function: setup_real_time_monitoring

```python
from app.core.realtime_monitoring import setup_real_time_monitoring

# One-line setup with all components
components = setup_real_time_monitoring(
    engine=engine,
    enable_alerts=True,
    enable_webhooks=True,
    webhook_urls=[
        "https://hooks.slack.com/services/...",
        "https://api.pagerduty.com/incidents"
    ],
    alert_threshold=0.7,
    monitor_interval=3600  # Check every hour
)

# Access components
update_manager = components["update_manager"]
alert_system = components["alert_system"]
webhook_notifier = components["webhook_notifier"]
dashboard = components["dashboard"]

# Components are automatically wired together
# alert_system → webhook_notifier (subscribed)
# Monitoring is automatically started
```

**Configuration Options:**
- `enable_alerts`: Enable real-time alert system
- `enable_webhooks`: Enable webhook notifications
- `webhook_urls`: List of webhook endpoints
- `alert_threshold`: Minimum likelihood for alerts (0.0-1.0)
- `monitor_interval`: Check interval in seconds

---

## Integration Examples

### With Telemetry System

```python
from app.core.realtime_monitoring import RealTimeAlertSystem
from app.core.telemetry import send_event

# Subscribe telemetry logger to alerts
def log_alert_to_telemetry(alert):
    send_event("crisis_alert_generated", {
        "alert_id": alert.alert_id,
        "risk_score": alert.risk_score,
        "scenario_title": alert.scenario.title,
        "likelihood": alert.scenario.likelihood,
        "severity": alert.scenario.severity.value,
        "year": alert.scenario.year
    })

alert_system.subscribe(log_alert_to_telemetry)
```

### With Email Notifications

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(alert):
    """Send email notification for crisis alert."""
    msg = MIMEText(f"""
Crisis Alert Generated

Alert ID: {alert.alert_id}
Risk Score: {alert.risk_score:.2f}
Scenario: {alert.scenario.title}
Likelihood: {alert.scenario.likelihood:.1%}
Severity: {alert.scenario.severity.value}
Year: {alert.scenario.year}

Summary:
{alert.explainability}
    """)
    
    msg["Subject"] = f"🚨 Crisis Alert: {alert.scenario.title}"
    msg["From"] = "alerts@project-ai.example"
    msg["To"] = "ops-team@company.com"
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("alerts@project-ai.example", "password")
        server.send_message(msg)

alert_system.subscribe(send_email_alert)
```

### With Slack Webhook

```python
import requests

def send_slack_alert(alert):
    """Send Slack notification via webhook."""
    webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
    
    # Determine color based on severity
    color_map = {
        "minor": "#36a64f",      # Green
        "moderate": "#ff9900",   # Orange
        "major": "#ff5500",      # Dark orange
        "critical": "#ff0000"    # Red
    }
    
    payload = {
        "attachments": [
            {
                "fallback": f"Crisis Alert: {alert.scenario.title}",
                "color": color_map.get(alert.scenario.severity.value, "#808080"),
                "title": f"🚨 Crisis Alert: {alert.scenario.title}",
                "fields": [
                    {
                        "title": "Risk Score",
                        "value": f"{alert.risk_score:.2f}",
                        "short": True
                    },
                    {
                        "title": "Likelihood",
                        "value": f"{alert.scenario.likelihood:.1%}",
                        "short": True
                    },
                    {
                        "title": "Severity",
                        "value": alert.scenario.severity.value.upper(),
                        "short": True
                    },
                    {
                        "title": "Year",
                        "value": str(alert.scenario.year),
                        "short": True
                    }
                ],
                "text": alert.explainability[:500],
                "footer": "Project-AI Global Scenario Engine",
                "ts": int(time.time())
            }
        ]
    }
    
    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()

alert_system.subscribe(send_slack_alert)
```

### With Grafana Dashboard

```python
import requests

def push_to_grafana(metrics):
    """Push metrics to Grafana via HTTP API."""
    grafana_url = "https://grafana.example.com/api/annotations"
    grafana_token = "Bearer your-grafana-api-token"
    
    annotations = [
        {
            "dashboardId": 1,
            "panelId": 2,
            "time": int(time.time() * 1000),  # Milliseconds
            "tags": ["monitoring", "scenarios"],
            "text": f"Scenarios: {metrics['scenarios']}, Alerts: {metrics['alerts']}"
        }
    ]
    
    headers = {"Authorization": grafana_token, "Content-Type": "application/json"}
    requests.post(grafana_url, json=annotations, headers=headers, timeout=10)

# Push metrics every 5 minutes
schedule.every(5).minutes.do(lambda: push_to_grafana(dashboard.get_current_metrics()))
```

---

## Performance Considerations

### Thread Safety

```python
# All managers use threading.Lock for thread safety
class IncrementalUpdateManager:
    def __init__(self, engine):
        self.engine = engine
        self.lock = threading.Lock()  # Protect shared state
    
    def update_country_data(self, country, domain, year, value):
        with self.lock:  # Atomic update
            # Modify engine state
            ...
```

### Memory Management

```python
# Update log uses deque with maxlen (automatic rotation)
from collections import deque

self.update_log = deque(maxlen=1000)  # Keep last 1000 updates
self.alert_queue = deque(maxlen=100)  # Keep last 100 alerts
self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics snapshots
```

### Background Thread Optimization

```python
# Monitoring interval tuning
alert_system.start_monitoring(interval=3600)  # 1 hour (default)
alert_system.start_monitoring(interval=300)   # 5 minutes (aggressive)
alert_system.start_monitoring(interval=7200)  # 2 hours (conservative)

# Trade-offs:
# - Shorter interval: More responsive, higher CPU/network usage
# - Longer interval: Less responsive, lower resource usage
```

---

## Configuration

```python
# Environment variables
export MONITORING_ENABLED=true
export MONITORING_INTERVAL=3600        # Seconds between checks
export ALERT_THRESHOLD=0.7             # Minimum likelihood for alerts
export WEBHOOK_URLS="url1,url2,url3"  # Comma-separated webhook URLs

# Configuration file
{
  "monitoring": {
    "enabled": true,
    "interval": 3600,
    "alert_threshold": 0.7,
    "webhooks": [
      "https://hooks.slack.com/services/...",
      "https://api.pagerduty.com/incidents"
    ],
    "dashboard": {
      "export_interval": 300,
      "metrics_retention": 1000
    }
  }
}
```

---

## Testing

```python
import unittest
from unittest.mock import Mock
from app.core.realtime_monitoring import RealTimeAlertSystem

class TestRealTimeAlertSystem(unittest.TestCase):
    def setUp(self):
        self.engine = Mock()
        self.alert_system = RealTimeAlertSystem(self.engine, alert_threshold=0.7)
    
    def test_subscribe_unsubscribe(self):
        """Test subscriber management."""
        callback = Mock()
        
        self.alert_system.subscribe(callback)
        self.assertIn(callback, self.alert_system.subscribers)
        
        self.alert_system.unsubscribe(callback)
        self.assertNotIn(callback, self.alert_system.subscribers)
    
    def test_emit_alert(self):
        """Test alert emission to subscribers."""
        callback1 = Mock()
        callback2 = Mock()
        
        self.alert_system.subscribe(callback1)
        self.alert_system.subscribe(callback2)
        
        mock_alert = Mock()
        self.alert_system.emit_alert(mock_alert)
        
        callback1.assert_called_once_with(mock_alert)
        callback2.assert_called_once_with(mock_alert)
```

---

## Troubleshooting

### "Monitoring already started"
```python
# Stop before restarting
alert_system.stop_monitoring()
alert_system.start_monitoring(interval=1800)
```

### Webhook Notification Failures
```python
# Check webhook URL
print(notifier.webhook_urls)

# Check notification log for errors
for entry in notifier.notification_log:
    if entry["status"] == "failed":
        print(f"Failed webhook: {entry['url']}")
        print(f"Error: {entry['error']}")
```

### High CPU Usage
```python
# Increase monitoring interval
alert_system.stop_monitoring()
alert_system.start_monitoring(interval=7200)  # 2 hours

# Or disable monitoring
alert_system.stop_monitoring()
```

---

## Best Practices

1. **Use Appropriate Intervals**: Don't poll too frequently
2. **Implement Retry Logic**: Handle webhook failures gracefully
3. **Monitor Resource Usage**: Track CPU/memory in production
4. **Test Alert Handlers**: Ensure notifications work before deployment
5. **Export Dashboard State**: Periodic snapshots for post-mortem analysis
6. **Rate Limit Alerts**: Prevent alert fatigue with deduplication

---

## Future Enhancements

1. **Alert Deduplication**: Prevent duplicate alerts for same scenario
2. **Alert Escalation**: Automatic escalation for unacknowledged alerts
3. **Multi-Channel Notifications**: SMS, phone calls, push notifications
4. **Metric Aggregation**: Time-series database integration (Prometheus, InfluxDB)
5. **Anomaly Detection**: ML-based anomaly detection for unexpected patterns
6. **Alert Grouping**: Group related alerts to reduce noise

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
