# Prometheus Integration Guide for Project-AI

## Overview

This document describes the Prometheus monitoring integration for Project-AI, providing comprehensive observability for AI systems, security events, and application performance.

## Table of Contents

1. [Architecture](#architecture)
1. [Quick Start](#quick-start)
1. [Metrics Categories](#metrics-categories)
1. [Configuration](#configuration)
1. [Grafana Dashboards](#grafana-dashboards)
1. [Alerting](#alerting)
1. [Integration with Existing Systems](#integration-with-existing-systems)
1. [Troubleshooting](#troubleshooting)
1. [Advanced Usage](#advanced-usage)

---

## Architecture

The Prometheus integration consists of:

- **Prometheus**: Time-series database scraping metrics from Project-AI
- **AlertManager**: Routes and manages alerts based on defined rules
- **Grafana**: Visualization dashboards for metrics
- **Metrics Exporter**: Python module exposing Project-AI metrics
- **Metrics Collector**: Integration layer connecting AI systems to Prometheus

```
┌─────────────────┐
│   Project-AI    │
│  (Main App)     │
│                 │
│  ┌───────────┐  │
│  │ AI Systems│  │──┐
│  │ Security  │  │  │ Metrics
│  │ Plugins   │  │  │ Collection
│  └───────────┘  │  │
└─────────────────┘  │
                     ▼
           ┌────────────────┐
           │ Metrics Server │ HTTP :8000-8003
           │  (Exporter)    │
           └────────────────┘
                     │
                     ▼ Scrape (every 15s)
              ┌────────────┐
              │ Prometheus │ :9090
              └────────────┘
                │         │
      ┌─────────┘         └─────────┐
      ▼                             ▼
┌──────────────┐           ┌──────────────┐
│ AlertManager │ :9093     │   Grafana    │ :3000
│  (Alerts)    │           │ (Dashboards) │
└──────────────┘           └──────────────┘
```

---

## Quick Start

### Using Docker Compose (Recommended)

1. **Start the full stack:**

```bash
docker-compose up -d
```

This starts:

- Project-AI application with metrics server (port 8000)
- Prometheus (port 9090)
- AlertManager (port 9093)
- Grafana (port 3000)
- Node Exporter (port 9100) - optional system metrics

1. **Access the services:**

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Metrics**: http://localhost:8000/metrics

1. **View pre-configured dashboards:**

Navigate to Grafana → Dashboards → Project-AI folder

### Standalone Metrics Server

To run metrics server without Docker:

```bash
# Install dependencies
pip install prometheus-client

# Start metrics server
python -m src.app.monitoring.metrics_server
```

Server will be available at http://localhost:8000/metrics

---

## Metrics Categories

### 1. AI Persona Metrics

Track AI personality, mood, and interaction patterns:

```promql
# Current mood levels
project_ai_persona_mood_energy
project_ai_persona_mood_enthusiasm
project_ai_persona_mood_contentment
project_ai_persona_mood_engagement

# Personality traits
project_ai_persona_trait_value{trait="curiosity"}
project_ai_persona_trait_value{trait="empathy"}

# Interaction counts
rate(project_ai_persona_interactions_total[5m])
```

**Use Cases:**

- Monitor AI responsiveness and engagement
- Detect unusual personality shifts
- Track user satisfaction through mood indicators

### 2. Four Laws Validation Metrics

Ethical decision-making and policy enforcement:

```promql
# Validation results
rate(project_ai_four_laws_validations_total{result="allowed"}[5m])
rate(project_ai_four_laws_validations_total{result="denied"}[5m])

# Denials by law and severity
project_ai_four_laws_denials_total{law_violated="first_law",severity="critical"}

# Override attempts
project_ai_four_laws_overrides_total{result="success"}
```

**Use Cases:**

- Audit ethical compliance
- Detect policy violation attempts
- Monitor override usage patterns

### 3. Memory System Metrics

Knowledge base health and query performance:

```promql
# Knowledge base size
project_ai_memory_knowledge_entries{category="technical"}

# Query performance
histogram_quantile(0.95, rate(project_ai_memory_query_duration_seconds_bucket[5m]))

# Error rates
rate(project_ai_memory_query_errors_total[5m])

# Storage size
project_ai_memory_storage_bytes
```

**Use Cases:**

- Capacity planning for knowledge base
- Performance optimization
- Error detection and debugging

### 4. Learning Request Metrics

Human-in-the-loop learning and Black Vault monitoring:

```promql
# Request status breakdown
project_ai_learning_requests_total{status="approved"}
project_ai_learning_requests_total{status="denied"}

# Pending queue size
project_ai_learning_pending_requests

# Black Vault additions
rate(project_ai_learning_black_vault_additions_total[15m])
```

**Use Cases:**

- Monitor learning request backlog
- Detect suspicious learning patterns
- Track Black Vault growth

### 5. Security & Cerberus Metrics

Threat detection and defensive system monitoring:

```promql
# Security incidents
rate(project_ai_security_incidents_total{severity="critical"}[5m])

# Cerberus blocks
project_ai_cerberus_blocks_total{attack_type="injection"}

# Threat scores
project_ai_threat_detection_score{threat_type="prompt_injection"}

# Authentication failures
rate(project_ai_auth_failures_total[5m])
```

**Use Cases:**

- Real-time security monitoring
- Attack pattern detection
- Incident response automation

### 6. Plugin System Metrics

Plugin health and execution tracking:

```promql
# Loaded plugins
project_ai_plugin_loaded_total

# Execution success rate
rate(project_ai_plugin_execution_total{status="success"}[5m]) /
rate(project_ai_plugin_execution_total[5m])

# Execution duration
histogram_quantile(0.95, rate(project_ai_plugin_execution_duration_seconds_bucket[5m]))

# Load failures
project_ai_plugin_load_failures_total
```

**Use Cases:**

- Plugin performance optimization
- Failure detection and recovery
- Capacity planning

### 7. System Performance Metrics

Application and API performance:

```promql
# API latency
histogram_quantile(0.99, rate(project_ai_api_request_duration_seconds_bucket[5m]))

# Request rate
rate(project_ai_api_requests_total[5m])

# Active users
project_ai_active_users

# Application uptime
project_ai_app_uptime_seconds
```

---

## Configuration

### Prometheus Configuration

Located at `config/prometheus/prometheus.yml`:

- **Scrape Interval**: 15 seconds (adjustable)
- **Retention**: 15 days (configurable in docker-compose.yml)
- **Remote Write**: Commented out, configure for Thanos/Mimir integration

**Scrape Targets:**

```yaml
scrape_configs:
  - job_name: 'project-ai-app'
    static_configs:
      - targets: ['project-ai:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'project-ai-security'
    static_configs:
      - targets: ['project-ai:8002']
    metrics_path: '/security-metrics'
    scrape_interval: 15s
```

### AlertManager Configuration

Located at `config/alertmanager/alertmanager.yml`:

**Configure email alerts** by setting environment variables:

```bash
# .env file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

ALERT_EMAIL_DEFAULT=admin@project-ai.local
ALERT_EMAIL_CRITICAL=oncall@project-ai.local
ALERT_EMAIL_SECURITY=security@project-ai.local
```

**Alert Routing:**

- **Critical alerts**: Immediate notification (no grouping delay)
- **Four Laws violations**: 5-minute grouping, sent to ethics team
- **Security incidents**: 5-minute grouping, sent to security team
- **AI system health**: 10-minute grouping, 4-hour repeat interval

### Environment Variables

Add to `.env` file:

```bash
# Enable metrics collection
ENABLE_METRICS=true
METRICS_PORT=8000

# Grafana credentials
GRAFANA_USER=admin
GRAFANA_PASSWORD=change_me_in_production

# Alert email configuration (see AlertManager section)
```

---

## Grafana Dashboards

### Pre-configured Dashboards

Located in `config/grafana/dashboards/`:

1. **AI System Health** (`ai_system_health.json`)
   - AI Persona mood gauges
   - Four Laws validation rates
   - Memory system metrics
   - Security incident tracking
   - Plugin execution rates
   - API performance

### Accessing Dashboards

1. Navigate to http://localhost:3000
1. Login (default: admin/admin)
1. Go to Dashboards → Browse → Project-AI folder
1. Select "AI System Health"

### Creating Custom Dashboards

1. In Grafana, click "+" → Dashboard
1. Add Panel
1. Select Prometheus datasource
1. Enter PromQL query (see Metrics Categories section)
1. Configure visualization
1. Save dashboard

**Example PromQL queries for custom panels:**

```promql
# Average AI mood over 1 hour
avg_over_time(project_ai_persona_mood_contentment[1h])

# Four Laws denial rate by severity
sum(rate(project_ai_four_laws_denials_total[5m])) by (severity)

# Top 5 most active plugins
topk(5, rate(project_ai_plugin_execution_total[5m]))
```

---

## Alerting

### Alert Rules

Located in `config/prometheus/alerts/`:

#### AI System Alerts (`ai_system_alerts.yml`)

- **HighFourLawsDenialRate**: Triggers when denial rate > 0.5/sec for 5 minutes
- **PersonaMoodDegraded**: Triggers when mood < 0.3 for 10 minutes
- **MemorySystemOverloaded**: Triggers when entries > 10,000
- **BlackVaultAdditionsSpike**: Triggers on increased Black Vault activity

#### Security Alerts (`security_alerts.yml`)

- **CriticalSecurityIncident**: Immediate alert on critical events
- **CerberusDefenseActivation**: Alert when Cerberus blocks > 10 actions
- **AuthenticationFailureSpike**: Alert on potential brute force attacks
- **BlackVaultAccessAttempt**: Alert on unauthorized vault access

### Alert Workflow

1. **Detection**: Prometheus evaluates rules every 30 seconds
1. **Firing**: Alert fires after "for" duration (e.g., 5 minutes)
1. **Routing**: AlertManager routes based on labels (severity, component)
1. **Notification**: Email sent to configured recipients
1. **Resolution**: Alert resolves when condition clears

### Testing Alerts

```bash
# Manually trigger test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "Test alert from Project-AI"
    }
  }]'
```

### Silencing Alerts

During maintenance:

1. Navigate to http://localhost:9093
1. Click "Silences" → "New Silence"
1. Add matchers (e.g., `alertname="MemorySystemOverloaded"`)
1. Set duration and comment
1. Create silence

---

## Integration with Existing Systems

### Adding Metrics to AI Systems

The metrics collector provides easy integration hooks:

```python
from app.monitoring.metrics_collector import collector

# In your AI Persona code
def update_mood(self, new_mood):
    self.mood = new_mood
    # Collect metrics
    collector.collect_persona_metrics(self.get_state())

# In Four Laws validation
def validate_action(self, action, context):
    is_allowed, reason = self._check_rules(action, context)
    # Record validation
    collector.record_four_laws_validation(
        is_allowed=is_allowed,
        law_violated=reason if not is_allowed else None,
        severity="critical" if context.get("endangers_humanity") else "medium"
    )
    return is_allowed, reason
```

### Periodic Metrics Collection

The collector automatically scrapes from disk every scrape interval (15s):

```python
from app.monitoring.metrics_collector import collector

# Manually trigger collection
collector.collect_all_metrics()
```

### Custom Metrics

Add custom metrics to `prometheus_exporter.py`:

```python
# In PrometheusMetrics.__init__()
self.custom_metric = Counter(
    'project_ai_custom_metric_total',
    'Description of custom metric',
    ['label1', 'label2'],
    registry=self.registry
)

# Usage
from app.monitoring.prometheus_exporter import metrics
metrics.custom_metric.labels(label1='value1', label2='value2').inc()
```

---

## Troubleshooting

### Metrics Not Appearing

1. **Check metrics server is running:**

   ```bash
   curl http://localhost:8000/health
   ```

1. **Verify Prometheus is scraping:**
   - Navigate to http://localhost:9090/targets
   - Check if `project-ai-app` target is UP
   - If DOWN, check container networking

1. **Check logs:**

   ```bash
   docker logs project-ai-dev
   docker logs project-ai-prometheus
   ```

### Alerts Not Firing

1. **Verify alert rules loaded:**
   - Navigate to http://localhost:9090/alerts
   - Check if rules are present

1. **Check AlertManager:**
   - Navigate to http://localhost:9093
   - Verify configuration and status

1. **Test email configuration:**

   ```bash
   docker exec project-ai-alertmanager \
     amtool config routes test --config.file=/etc/alertmanager/alertmanager.yml
   ```

### Dashboard Not Showing Data

1. **Verify datasource connection:**
   - Grafana → Configuration → Data Sources
   - Test connection to Prometheus

1. **Check time range:**
   - Ensure dashboard time range covers when app was running
   - Try "Last 5 minutes" to see recent data

1. **Verify metrics exist:**
   - In Prometheus (http://localhost:9090)
   - Run query: `project_ai_persona_mood_energy`

### High Memory Usage

If Prometheus memory usage is high:

1. **Reduce retention time:**

   ```yaml
   # docker-compose.yml
   command:
     - '--storage.tsdb.retention.time=7d'  # Reduce from 15d
   ```

1. **Reduce scrape frequency:**

   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 30s  # Increase from 15s
   ```

---

## Advanced Usage

### Federated Setup (Multiple Project-AI Instances)

For multi-instance deployment:

1. **Enable remote write in Prometheus:**

```yaml
# prometheus.yml
remote_write:
  - url: "http://thanos-receiver:19291/api/v1/receive"
    queue_config:
      capacity: 10000
      max_shards: 50
```

1. **Deploy Thanos or Mimir:**

```bash
# Example Thanos sidecar
docker run -d \
  --name thanos-sidecar \
  --network project-ai-network \
  -v ./prometheus-data:/prometheus \
  quay.io/thanos/thanos:latest \
  sidecar \
  --tsdb.path=/prometheus \
  --prometheus.url=http://prometheus:9090
```

### Service Discovery

For dynamic scraping of multiple instances:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'project-ai-dynamic'
    file_sd_configs:
      - files:
        - '/etc/prometheus/targets/*.json'
        refresh_interval: 30s
```

Create target files:

```json
[
  {
    "targets": ["instance1:8000", "instance2:8000"],
    "labels": {
      "env": "production",
      "datacenter": "us-east"
    }
  }
]
```

### Long-term Storage with Mimir

```yaml
# prometheus.yml
remote_write:
  - url: "http://mimir:9009/api/v1/push"
    headers:
      X-Scope-OrgID: project-ai
    queue_config:
      capacity: 10000
      max_samples_per_send: 5000
      batch_send_deadline: 5s
```

### Recording Rules for Performance

Create pre-computed aggregations:

```yaml
# prometheus.yml - add to rule_files
- 'recording_rules.yml'
```

```yaml
# recording_rules.yml
groups:
  - name: project_ai_aggregations
    interval: 30s
    rules:
      - record: project_ai:persona_mood_avg
        expr: avg(project_ai_persona_mood_energy)
      
      - record: project_ai:api_request_rate_5m
        expr: rate(project_ai_api_requests_total[5m])
```

### Prometheus Client Integration (Python)

For custom application integration:

```python
from prometheus_client import start_http_server, Summary
import time

# Create metric
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function
@REQUEST_TIME.time()
def process_request(t):
    time.sleep(t)

# Start server
if __name__ == '__main__':
    start_http_server(8000)
    while True:
        process_request(random.random())
```

---

## Best Practices

1. **Use Labels Wisely**: Don't create high-cardinality labels (e.g., user IDs)
1. **Set Appropriate Scrape Intervals**: Balance between freshness and overhead
1. **Configure Retention**: Match retention to storage and query needs
1. **Use Recording Rules**: Pre-compute expensive queries
1. **Monitor Prometheus Itself**: Watch prometheus_tsdb_* metrics
1. **Test Alerts**: Regularly test alert delivery and response procedures
1. **Dashboard Organization**: Group related panels, use consistent naming
1. **Document Custom Metrics**: Add descriptions and usage examples

---

## Security Considerations

1. **Network Isolation**: Keep Prometheus/Grafana on internal network
1. **Authentication**: Enable Grafana authentication in production
1. **Encryption**: Use TLS for AlertManager email and webhooks
1. **Access Control**: Restrict who can silence alerts or modify configs
1. **Sensitive Data**: Avoid exposing PII in metric labels
1. **API Keys**: Store credentials in secrets, not config files

---

## Support and Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Project-AI Issues**: https://github.com/IAmSoThirsty/Project-AI/issues

---

## Appendix: Complete Metric List

See `src/app/monitoring/prometheus_exporter.py` for the complete, up-to-date metric definitions.

**Metric Naming Convention:**

- Prefix: `project_ai_`
- Component: `persona_`, `four_laws_`, `memory_`, etc.
- Type suffix: `_total` (counter), `_seconds` (histogram), no suffix (gauge)

---

*Last Updated: 2026-01-07*
*Version: 1.0*
