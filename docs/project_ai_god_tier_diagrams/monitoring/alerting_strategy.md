# Alerting Strategy

## Alerting Philosophy

Project-AI implements a multi-tier alerting strategy focused on **actionable alerts** that require human intervention. Our approach follows industry best practices:

1. **Alert on symptoms, not causes** - Alert when users are affected
2. **Reduce alert fatigue** - Aggregate similar alerts, use appropriate thresholds
3. **Context-rich notifications** - Include runbook links, graphs, recent changes
4. **Escalation paths** - Clear ownership and escalation procedures
5. **Alert lifecycle management** - Track, resolve, and learn from alerts

## Alert Severity Levels

### Critical (P1)
- **Response Time**: Immediate (< 5 minutes)
- **Escalation**: PagerDuty + Slack + Email
- **Examples**: Service down, data loss, security breach
- **On-Call**: Yes

### Warning (P2)
- **Response Time**: Within 1 hour
- **Escalation**: Slack + Email
- **Examples**: High latency, elevated error rates, resource pressure
- **On-Call**: No (business hours only)

### Info (P3)
- **Response Time**: Next business day
- **Escalation**: Email only
- **Examples**: Certificate expiring soon, configuration drift
- **On-Call**: No

## AlertManager Configuration

```yaml
# /etc/alertmanager/alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

# Templates for alert messages
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Alert routing tree
route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 4h
  
  routes:
    # Critical alerts route
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      group_wait: 10s
      group_interval: 5m
      repeat_interval: 1h
      continue: true
    
    # Critical alerts also go to Slack
    - match:
        severity: critical
      receiver: 'slack-critical'
      group_wait: 10s
      repeat_interval: 1h
      continue: false
    
    # Warning alerts route
    - match:
        severity: warning
      receiver: 'slack-warnings'
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
    
    # Info alerts route
    - match:
        severity: info
      receiver: 'email-info'
      group_wait: 5m
      group_interval: 10m
      repeat_interval: 24h
    
    # Security alerts (always critical)
    - match:
        component: security
      receiver: 'security-team'
      group_wait: 0s
      repeat_interval: 30m
    
    # Database alerts
    - match:
        component: database
      receiver: 'database-team'
      group_wait: 30s
      repeat_interval: 2h
    
    # Temporal workflow alerts
    - match:
        component: orchestration
      receiver: 'platform-team'
      group_wait: 1m
      repeat_interval: 4h

# Alert receivers/integrations
receivers:
  # Default receiver (catch-all)
  - name: 'default'
    slack_configs:
      - channel: '#alerts-general'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true
  
  # PagerDuty for critical alerts
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        severity: 'critical'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
        details:
          firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
          alertname: '{{ .GroupLabels.alertname }}'
          summary: '{{ .CommonAnnotations.summary }}'
          description: '{{ .CommonAnnotations.description }}'
          runbook_url: '{{ .CommonAnnotations.runbook_url }}'
        client: 'Project-AI Monitoring'
        client_url: 'https://grafana.project-ai.com'
  
  # Slack for critical alerts
  - name: 'slack-critical'
    slack_configs:
      - channel: '#alerts-critical'
        color: 'danger'
        title: '🚨 [CRITICAL] {{ .GroupLabels.alertname }}'
        title_link: '{{ .CommonAnnotations.runbook_url }}'
        text: |
          *Summary:* {{ .CommonAnnotations.summary }}
          *Description:* {{ .CommonAnnotations.description }}
          *Severity:* {{ .CommonLabels.severity }}
          *Component:* {{ .CommonLabels.component }}
          
          *Firing Alerts:* {{ .Alerts.Firing | len }}
          {{ range .Alerts }}
          • *Instance:* {{ .Labels.instance }}
            *Value:* {{ .Annotations.value }}
          {{ end }}
        send_resolved: true
        actions:
          - type: button
            text: 'View Runbook'
            url: '{{ .CommonAnnotations.runbook_url }}'
          - type: button
            text: 'View Dashboard'
            url: 'https://grafana.project-ai.com/d/{{ .CommonLabels.dashboard_uid }}'
          - type: button
            text: 'View Logs'
            url: 'https://grafana.project-ai.com/explore?left={{ .CommonLabels.instance }}'
  
  # Slack for warnings
  - name: 'slack-warnings'
    slack_configs:
      - channel: '#alerts-warnings'
        color: 'warning'
        title: '⚠️  [WARNING] {{ .GroupLabels.alertname }}'
        title_link: '{{ .CommonAnnotations.runbook_url }}'
        text: |
          *Summary:* {{ .CommonAnnotations.summary }}
          *Description:* {{ .CommonAnnotations.description }}
          
          {{ range .Alerts }}
          • {{ .Labels.instance }}: {{ .Annotations.value }}
          {{ end }}
        send_resolved: true
  
  # Email for info alerts
  - name: 'email-info'
    email_configs:
      - to: 'team@project-ai.com'
        from: 'alertmanager@project-ai.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alertmanager@project-ai.com'
        auth_password: 'YOUR_EMAIL_PASSWORD'
        headers:
          Subject: '[INFO] {{ .GroupLabels.alertname }}'
        html: |
          <h2>{{ .GroupLabels.alertname }}</h2>
          <p><strong>Summary:</strong> {{ .CommonAnnotations.summary }}</p>
          <p><strong>Description:</strong> {{ .CommonAnnotations.description }}</p>
          <p><strong>Component:</strong> {{ .CommonLabels.component }}</p>
          
          <h3>Firing Alerts ({{ .Alerts.Firing | len }})</h3>
          <ul>
          {{ range .Alerts }}
            <li>{{ .Labels.instance }}: {{ .Annotations.description }}</li>
          {{ end }}
          </ul>
          
          <p><a href="{{ .CommonAnnotations.runbook_url }}">View Runbook</a></p>
        send_resolved: true
  
  # Security team alerts
  - name: 'security-team'
    slack_configs:
      - channel: '#security-alerts'
        color: 'danger'
        title: '🔒 [SECURITY] {{ .GroupLabels.alertname }}'
        text: |
          *SECURITY ALERT*
          
          {{ .CommonAnnotations.summary }}
          {{ .CommonAnnotations.description }}
        send_resolved: true
    email_configs:
      - to: 'security@project-ai.com'
        from: 'alertmanager@project-ai.com'
        headers:
          Subject: '[SECURITY ALERT] {{ .GroupLabels.alertname }}'
        send_resolved: true
  
  # Database team alerts
  - name: 'database-team'
    slack_configs:
      - channel: '#db-alerts'
        title: '🗄️  [DATABASE] {{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
        send_resolved: true
  
  # Platform team alerts
  - name: 'platform-team'
    slack_configs:
      - channel: '#platform-alerts'
        title: '⚙️  [PLATFORM] {{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
        send_resolved: true

# Inhibition rules (suppress alerts when related alerts are firing)
inhibit_rules:
  # Inhibit warning/info alerts when critical alert for same service is firing
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'service', 'instance']
  
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'info'
    equal: ['alertname', 'service', 'instance']
  
  # Inhibit individual instance alerts when entire service is down
  - source_match:
      alertname: 'ServiceDown'
    target_match_re:
      alertname: '.*'
    equal: ['service']
  
  # Inhibit downstream errors when upstream service is down
  - source_match:
      alertname: 'DatabaseDown'
    target_match:
      component: 'application'
    equal: ['cluster']
```

## Alert Message Templates

```go
// /etc/alertmanager/templates/custom.tmpl
{{ define "slack.project-ai.title" }}
[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .GroupLabels.alertname }}
{{ end }}

{{ define "slack.project-ai.text" }}
{{ range .Alerts }}
*Alert:* {{ .Labels.alertname }}
*Summary:* {{ .Annotations.summary }}
*Description:* {{ .Annotations.description }}
*Severity:* {{ .Labels.severity }}
*Instance:* {{ .Labels.instance }}
*Value:* {{ .Annotations.value }}
*Started:* {{ .StartsAt.Format "2006-01-02 15:04:05" }}
{{ if .EndsAt }}*Ended:* {{ .EndsAt.Format "2006-01-02 15:04:05" }}{{ end }}
{{ end }}
{{ end }}

{{ define "email.project-ai.subject" }}
[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }} ({{ .Alerts.Firing | len }} firing)
{{ end }}

{{ define "email.project-ai.html" }}
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .alert { margin: 20px 0; padding: 15px; border-left: 5px solid #dc3545; }
    .critical { border-left-color: #dc3545; background: #f8d7da; }
    .warning { border-left-color: #ffc107; background: #fff3cd; }
    .info { border-left-color: #17a2b8; background: #d1ecf1; }
    .resolved { border-left-color: #28a745; background: #d4edda; }
    h2 { margin-top: 0; }
    .labels { margin: 10px 0; }
    .label { display: inline-block; background: #6c757d; color: white; 
             padding: 2px 8px; margin: 2px; border-radius: 3px; font-size: 12px; }
  </style>
</head>
<body>
  <h1>Alert Notification: {{ .GroupLabels.alertname }}</h1>
  
  <p><strong>Status:</strong> {{ .Status | toUpper }}</p>
  <p><strong>Firing Alerts:</strong> {{ .Alerts.Firing | len }}</p>
  <p><strong>Resolved Alerts:</strong> {{ .Alerts.Resolved | len }}</p>
  
  {{ range .Alerts }}
  <div class="alert {{ .Labels.severity }}">
    <h2>{{ .Labels.alertname }}</h2>
    <p><strong>Summary:</strong> {{ .Annotations.summary }}</p>
    <p>{{ .Annotations.description }}</p>
    
    <div class="labels">
      {{ range .Labels.SortedPairs }}
      <span class="label">{{ .Name }}: {{ .Value }}</span>
      {{ end }}
    </div>
    
    <p><strong>Started:</strong> {{ .StartsAt.Format "2006-01-02 15:04:05 MST" }}</p>
    {{ if .EndsAt }}
    <p><strong>Ended:</strong> {{ .EndsAt.Format "2006-01-02 15:04:05 MST" }}</p>
    {{ end }}
    
    {{ if .Annotations.runbook_url }}
    <p><a href="{{ .Annotations.runbook_url }}">View Runbook</a></p>
    {{ end }}
  </div>
  {{ end }}
  
  <hr>
  <p><small>Generated by AlertManager at {{ .ExternalURL }}</small></p>
</body>
</html>
{{ end }}
```

## PagerDuty Integration

### Service Configuration

```python
# src/app/monitoring/pagerduty_integration.py
import requests
import json
from typing import Dict, Optional
from datetime import datetime

class PagerDutyIntegration:
    """Integration with PagerDuty for critical alerts"""
    
    def __init__(self, integration_key: str, api_token: str):
        self.integration_key = integration_key
        self.api_token = api_token
        self.events_url = "https://events.pagerduty.com/v2/enqueue"
        self.api_url = "https://api.pagerduty.com"
    
    def trigger_incident(
        self,
        summary: str,
        severity: str,
        source: str,
        component: str,
        custom_details: Dict = None
    ) -> Dict:
        """Trigger a PagerDuty incident"""
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "payload": {
                "summary": summary,
                "severity": severity,
                "source": source,
                "component": component,
                "timestamp": datetime.utcnow().isoformat(),
                "custom_details": custom_details or {}
            }
        }
        
        response = requests.post(
            self.events_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def resolve_incident(self, dedup_key: str) -> Dict:
        """Resolve a PagerDuty incident"""
        payload = {
            "routing_key": self.integration_key,
            "event_action": "resolve",
            "dedup_key": dedup_key
        }
        
        response = requests.post(
            self.events_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def acknowledge_incident(self, dedup_key: str) -> Dict:
        """Acknowledge a PagerDuty incident"""
        payload = {
            "routing_key": self.integration_key,
            "event_action": "acknowledge",
            "dedup_key": dedup_key
        }
        
        response = requests.post(
            self.events_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def get_on_call(self, escalation_policy_id: str) -> list:
        """Get current on-call users for an escalation policy"""
        headers = {
            "Authorization": f"Token token={self.api_token}",
            "Accept": "application/vnd.pagerduty+json;version=2"
        }
        
        response = requests.get(
            f"{self.api_url}/oncalls",
            params={"escalation_policy_ids[]": escalation_policy_id},
            headers=headers
        )
        response.raise_for_status()
        return response.json()["oncalls"]
    
    def create_incident_note(self, incident_id: str, note: str) -> Dict:
        """Add a note to an existing incident"""
        headers = {
            "Authorization": f"Token token={self.api_token}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json"
        }
        
        payload = {
            "note": {
                "content": note
            }
        }
        
        response = requests.post(
            f"{self.api_url}/incidents/{incident_id}/notes",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# Usage example
def handle_critical_alert():
    """Handle a critical alert by triggering PagerDuty incident"""
    pd = PagerDutyIntegration(
        integration_key=os.getenv("PAGERDUTY_INTEGRATION_KEY"),
        api_token=os.getenv("PAGERDUTY_API_TOKEN")
    )
    
    incident = pd.trigger_incident(
        summary="High error rate detected on production API",
        severity="critical",
        source="project-ai-api-prod-1",
        component="application",
        custom_details={
            "error_rate": "12.5%",
            "threshold": "5%",
            "affected_endpoints": ["/api/generate", "/api/chat"],
            "runbook_url": "https://docs.project-ai.com/runbooks/high-error-rate"
        }
    )
    
    return incident["dedup_key"]
```

## Slack Integration

```python
# src/app/monitoring/slack_integration.py
import requests
from typing import Dict, List

class SlackIntegration:
    """Integration with Slack for alert notifications"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_alert(
        self,
        title: str,
        text: str,
        severity: str,
        fields: List[Dict] = None,
        actions: List[Dict] = None
    ):
        """Send an alert message to Slack"""
        color_map = {
            "critical": "danger",
            "warning": "warning",
            "info": "good"
        }
        
        attachment = {
            "title": title,
            "text": text,
            "color": color_map.get(severity, "#808080"),
            "fields": fields or [],
            "actions": actions or [],
            "footer": "Project-AI Monitoring",
            "footer_icon": "https://project-ai.com/favicon.ico",
            "ts": int(time.time())
        }
        
        payload = {
            "attachments": [attachment]
        }
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    
    def send_resolved_alert(self, title: str, duration: str):
        """Send a resolved alert notification"""
        self.send_alert(
            title=f"✅ RESOLVED: {title}",
            text=f"Alert has been resolved. Duration: {duration}",
            severity="info"
        )

# Usage example
slack = SlackIntegration(os.getenv("SLACK_WEBHOOK_URL"))

slack.send_alert(
    title="🚨 High Error Rate",
    text="Error rate has exceeded 5% threshold",
    severity="critical",
    fields=[
        {"title": "Service", "value": "project-ai-api", "short": True},
        {"title": "Error Rate", "value": "12.5%", "short": True},
        {"title": "Instance", "value": "prod-api-1", "short": True},
        {"title": "Threshold", "value": "5%", "short": True}
    ],
    actions=[
        {
            "type": "button",
            "text": "View Dashboard",
            "url": "https://grafana.project-ai.com/d/overview"
        },
        {
            "type": "button",
            "text": "View Runbook",
            "url": "https://docs.project-ai.com/runbooks/high-error-rate"
        }
    ]
)
```

## Alert Escalation Policy

### Escalation Hierarchy

```yaml
escalation_policies:
  # P1 - Critical
  critical:
    level_1:
      delay: 0m
      notify:
        - pagerduty
        - slack_critical
        - on_call_primary
    
    level_2:
      delay: 5m
      notify:
        - on_call_secondary
        - team_lead
    
    level_3:
      delay: 15m
      notify:
        - engineering_manager
        - cto
  
  # P2 - Warning
  warning:
    level_1:
      delay: 0m
      notify:
        - slack_warnings
    
    level_2:
      delay: 1h
      notify:
        - team_email
  
  # P3 - Info
  info:
    level_1:
      delay: 0m
      notify:
        - email_info
```

### On-Call Schedule

```python
# src/app/monitoring/oncall_schedule.py
from datetime import datetime, timedelta
from typing import List, Optional

class OnCallSchedule:
    """Manage on-call rotation schedule"""
    
    def __init__(self):
        self.schedule = {
            "week_1": {"primary": "engineer_a", "secondary": "engineer_b"},
            "week_2": {"primary": "engineer_b", "secondary": "engineer_c"},
            "week_3": {"primary": "engineer_c", "secondary": "engineer_d"},
            "week_4": {"primary": "engineer_d", "secondary": "engineer_a"}
        }
        self.contacts = {
            "engineer_a": {
                "name": "Alice Smith",
                "phone": "+1-555-0101",
                "email": "alice@project-ai.com",
                "pagerduty_id": "PXXXXXX"
            },
            "engineer_b": {
                "name": "Bob Johnson",
                "phone": "+1-555-0102",
                "email": "bob@project-ai.com",
                "pagerduty_id": "PXXXXXX"
            }
            # ... more engineers
        }
    
    def get_current_on_call(self) -> Dict:
        """Get current on-call engineer"""
        week_number = datetime.now().isocalendar()[1] % 4
        week_key = f"week_{week_number + 1}"
        
        on_call = self.schedule[week_key]
        return {
            "primary": self.contacts[on_call["primary"]],
            "secondary": self.contacts[on_call["secondary"]]
        }
    
    def notify_on_call(self, alert: Dict, level: str = "primary"):
        """Notify the on-call engineer"""
        on_call = self.get_current_on_call()
        engineer = on_call[level]
        
        # Trigger PagerDuty page
        pd = PagerDutyIntegration(
            integration_key=os.getenv("PAGERDUTY_INTEGRATION_KEY"),
            api_token=os.getenv("PAGERDUTY_API_TOKEN")
        )
        
        pd.trigger_incident(
            summary=alert["summary"],
            severity=alert["severity"],
            source=alert["source"],
            component=alert["component"],
            custom_details={
                "on_call_engineer": engineer["name"],
                **alert.get("details", {})
            }
        )
```

## Runbook Links

### Runbook Structure

```markdown
# Runbook: High Error Rate

## Severity: Critical

## Overview
This alert fires when the error rate exceeds 5% for more than 5 minutes.

## Impact
- Users are experiencing errors
- Service degradation
- Potential data loss

## Diagnosis
1. Check Grafana dashboard: https://grafana.project-ai.com/d/overview
2. Review recent deployments: `kubectl rollout history deployment/project-ai-api`
3. Check application logs: `kubectl logs -l app=project-ai-api --tail=100`
4. Check database health: `psql -c "SELECT * FROM pg_stat_activity"`

## Resolution Steps
1. If recent deployment, consider rollback: `kubectl rollout undo deployment/project-ai-api`
2. Scale up pods if CPU/memory constrained: `kubectl scale deployment/project-ai-api --replicas=5`
3. Check external dependencies (OpenAI, HuggingFace)
4. Review database connection pool

## Verification
- Error rate returns to < 1%
- Response times return to normal (p95 < 1s)
- No user reports of issues

## Post-Incident
- Create incident report
- Update runbook if needed
- Schedule post-mortem meeting
```

## Alert Testing

```bash
# Test AlertManager configuration
amtool check-config /etc/alertmanager/alertmanager.yml

# Send test alert
amtool alert add test_alert \
  alertname=TestAlert \
  severity=warning \
  instance=test-instance \
  summary="This is a test alert"

# Verify alert routing
amtool config routes --config.file=/etc/alertmanager/alertmanager.yml

# Test silence creation
amtool silence add \
  alertname=TestAlert \
  --duration=1h \
  --comment="Testing silence functionality"
```

## Metrics and SLIs

```python
# Track alert metrics
ALERTS_FIRED = Counter(
    'alertmanager_alerts_fired_total',
    'Total number of alerts fired',
    ['alertname', 'severity']
)

ALERT_RESOLUTION_TIME = Histogram(
    'alertmanager_alert_resolution_seconds',
    'Time to resolve alerts',
    ['alertname', 'severity'],
    buckets=[60, 300, 900, 1800, 3600, 7200, 14400]
)

ALERT_ACKNOWLEDGMENT_TIME = Histogram(
    'alertmanager_alert_acknowledgment_seconds',
    'Time to acknowledge alerts',
    ['alertname', 'severity'],
    buckets=[60, 180, 300, 600, 1800]
)
```

## Alert Fatigue Prevention

### Alert Review Process
- Weekly review of all alerts
- Identify noisy alerts and adjust thresholds
- Consolidate related alerts
- Remove alerts that don't require action

### Alert Quality Metrics
- **Alert precision**: % of alerts that require action
- **Mean time to acknowledge**: Average time to acknowledge alerts
- **Mean time to resolve**: Average time to resolve alerts
- **False positive rate**: % of alerts that were false positives
