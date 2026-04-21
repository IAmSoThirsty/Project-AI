# Grafana Dashboard Setup

**Component:** Visualization and Dashboards  
**Type:** Configuration Guide  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This guide covers the setup, configuration, and maintenance of Grafana dashboards for Project-AI monitoring. Grafana provides real-time visualization of Prometheus metrics with pre-built dashboards for AI systems, security posture, performance monitoring, and operational health.

---

## Installation

### Docker Compose (Recommended)

**File:** `monitoring/docker-compose.yml`

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: project-ai-prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
    ports:
      - "9090:9090"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: project-ai-grafana
    volumes:
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=http://localhost:3000
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

**Start Stack:**
```bash
cd monitoring
docker-compose up -d

# Verify services
docker-compose ps

# Access Grafana
open http://localhost:3000
# Default credentials: admin/admin
```

---

### Standalone Installation

```bash
# Install Grafana (Ubuntu/Debian)
sudo apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/oss/release/grafana_10.0.0_amd64.deb
sudo dpkg -i grafana_10.0.0_amd64.deb

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Install Grafana (macOS)
brew install grafana
brew services start grafana

# Install Grafana (Windows)
choco install grafana
```

---

## Datasource Configuration

### Prometheus Datasource

**File:** `monitoring/grafana/datasources/prometheus.yml`

```yaml
apiVersion: 1

datasources:
  - name: Project-AI Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      httpMethod: POST
      timeInterval: 15s
```

**Manual Configuration:**

1. Navigate to **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   - **Name:** Project-AI Prometheus
   - **URL:** `http://localhost:9090` (or `http://prometheus:9090` in Docker)
   - **Access:** Server (default)
5. Click **Save & Test**

---

## Dashboard Provisioning

### Dashboard Provider Configuration

**File:** `monitoring/grafana/dashboards/provider.yml`

```yaml
apiVersion: 1

providers:
  - name: 'Project-AI Dashboards'
    orgId: 1
    folder: 'Project-AI'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: true
```

### Dashboard Directory Structure

```
monitoring/grafana/dashboards/
├── provider.yml
├── ai_systems/
│   ├── ai_persona_dashboard.json
│   ├── memory_system_dashboard.json
│   └── learning_requests_dashboard.json
├── security/
│   ├── security_posture_dashboard.json
│   ├── four_laws_dashboard.json
│   └── cerberus_dashboard.json
└── performance/
    ├── api_performance_dashboard.json
    ├── plugin_metrics_dashboard.json
    └── system_health_dashboard.json
```

---

## Pre-Built Dashboards

### 1. AI System Health Dashboard

**File:** `ai_persona_dashboard.json`

**Panels:**
1. **Mood Metrics** (Gauge)
   - Energy, Enthusiasm, Contentment, Engagement
2. **Trait Values** (Bar Chart)
   - All 8 personality traits
3. **Interaction Rate** (Graph)
   - Interactions per minute by type
4. **Mood Trends** (Time Series)
   - 24-hour mood evolution

**Example Panel: Mood Energy Gauge**

```json
{
  "type": "gauge",
  "title": "Energy Level",
  "targets": [{
    "expr": "project_ai_persona_mood_energy",
    "legendFormat": "Energy"
  }],
  "options": {
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    },
    "showThresholdLabels": false,
    "showThresholdMarkers": true
  },
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "min": 0,
      "max": 1,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 0, "color": "red"},
          {"value": 0.3, "color": "yellow"},
          {"value": 0.7, "color": "green"}
        ]
      }
    }
  }
}
```

---

### 2. Security Posture Dashboard

**Panels:**
1. **Attack Success Rate** (Stat)
   - Current rate with threshold indicators
2. **Cerberus Blocks** (Graph)
   - Blocks per minute by attack type
3. **Threat Detection Scores** (Heatmap)
   - Threat levels by type
4. **Four Laws Denials** (Bar Chart)
   - Denials by law and severity
5. **Security Incidents Timeline** (Table)
   - Recent incidents with details

**Example Panel: Attack Success Rate**

```json
{
  "type": "stat",
  "title": "Attack Success Rate (24h)",
  "targets": [{
    "expr": "rate(project_ai_cerberus_blocks_total{attack_type=\"bypass\"}[24h]) / rate(project_ai_cerberus_blocks_total[24h])",
    "legendFormat": "Success Rate"
  }],
  "options": {
    "graphMode": "area",
    "colorMode": "background",
    "justifyMode": "center",
    "textMode": "value_and_name"
  },
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit",
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 0.05, "color": "yellow"},
          {"value": 0.1, "color": "red"}
        ]
      }
    }
  }
}
```

---

### 3. Four Laws Compliance Dashboard

**Panels:**
1. **Validation Results** (Pie Chart)
   - Allowed vs. Denied ratio
2. **Denials by Law** (Bar Chart)
   - Breakdown by First/Second/Third/Fourth Law
3. **Critical Violations** (Stat)
   - Count of critical denials (alert if > 0)
4. **Override Attempts** (Table)
   - User, timestamp, result
5. **Denial Trends** (Graph)
   - Denials per hour over 7 days

**Example Panel: Denials by Law**

```json
{
  "type": "barchart",
  "title": "Four Laws Denials by Law",
  "targets": [{
    "expr": "sum by (law_violated) (project_ai_four_laws_denials_total)",
    "legendFormat": "{{law_violated}} Law"
  }],
  "options": {
    "orientation": "horizontal",
    "showValue": "always",
    "groupWidth": 0.7,
    "barWidth": 0.8
  },
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"}
    }
  }
}
```

---

### 4. Memory System Performance Dashboard

**Panels:**
1. **Knowledge Base Size** (Graph)
   - Entries by category over time
2. **Query Latency** (Heatmap)
   - p50/p95/p99 by query type
3. **Query Rate** (Graph)
   - Queries per second
4. **Error Rate** (Stat)
   - Percentage with threshold
5. **Storage Usage** (Gauge)
   - Bytes with capacity indicator

**Example Panel: Query Latency Percentiles**

```json
{
  "type": "timeseries",
  "title": "Query Latency (p50/p95/p99)",
  "targets": [
    {
      "expr": "histogram_quantile(0.50, rate(project_ai_memory_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p50"
    },
    {
      "expr": "histogram_quantile(0.95, rate(project_ai_memory_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p95"
    },
    {
      "expr": "histogram_quantile(0.99, rate(project_ai_memory_query_duration_seconds_bucket[5m]))",
      "legendFormat": "p99"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "s",
      "custom": {
        "drawStyle": "line",
        "lineWidth": 2,
        "fillOpacity": 10
      }
    }
  }
}
```

---

### 5. API Performance Dashboard

**Panels:**
1. **Request Rate** (Graph)
   - Requests per second by endpoint
2. **Latency Distribution** (Heatmap)
   - p95 latency by endpoint
3. **Error Rate** (Stat)
   - 4xx and 5xx errors
4. **Active Users** (Gauge)
   - Current active user count
5. **Top Endpoints** (Table)
   - Request count, avg latency, error rate

**Example Panel: Request Rate**

```json
{
  "type": "timeseries",
  "title": "API Request Rate by Endpoint",
  "targets": [{
    "expr": "sum by (endpoint) (rate(project_ai_api_requests_total[5m]))",
    "legendFormat": "{{endpoint}}"
  }],
  "options": {
    "legend": {
      "displayMode": "list",
      "placement": "bottom"
    }
  },
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "custom": {
        "drawStyle": "line",
        "lineWidth": 1,
        "fillOpacity": 20,
        "stacking": {"mode": "normal"}
      }
    }
  }
}
```

---

### 6. Plugin Execution Dashboard

**Panels:**
1. **Loaded Plugins** (Stat)
   - Current count
2. **Execution Rate** (Graph)
   - Executions per minute by plugin
3. **Execution Duration** (Heatmap)
   - p95 duration by plugin
4. **Error Rate** (Bar Chart)
   - Errors by plugin
5. **Plugin Leaderboard** (Table)
   - Execution count, success rate, avg duration

---

## Dashboard Variables

### Template Variables

**Use Case:** Filter dashboards by user, plugin, endpoint, etc.

**Example: Plugin Name Variable**

1. Navigate to **Dashboard Settings** → **Variables**
2. Click **Add variable**
3. Configure:
   - **Name:** `plugin`
   - **Type:** Query
   - **Data source:** Project-AI Prometheus
   - **Query:** `label_values(project_ai_plugin_execution_total, plugin_name)`
   - **Multi-value:** Yes
   - **Include All option:** Yes

**Usage in Query:**
```promql
rate(project_ai_plugin_execution_total{plugin_name=~"$plugin"}[5m])
```

**Example: Time Range Variable**

```json
{
  "name": "range",
  "type": "interval",
  "auto": true,
  "auto_count": 30,
  "auto_min": "10s",
  "options": [
    {"text": "1m", "value": "1m"},
    {"text": "5m", "value": "5m"},
    {"text": "15m", "value": "15m"},
    {"text": "1h", "value": "1h"}
  ]
}
```

---

## Alert Configuration in Grafana

### Alert Rule Example

**Panel:** Four Laws Critical Violations

1. Click panel → **Edit**
2. Navigate to **Alert** tab
3. Configure:
   - **Name:** Four Laws Critical Violation
   - **Evaluate every:** 1m
   - **For:** 2m
   - **Conditions:**
     ```
     WHEN last() OF query(A, 5m, now) IS ABOVE 0
     ```
   - **No Data:** Set state to NoData
   - **Error:** Set state to Error

4. **Notifications:**
   - Add notification channel
   - Message: "Critical Four Laws violation detected"

### Notification Channels

**Slack:**
```json
{
  "type": "slack",
  "settings": {
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "username": "Grafana",
    "icon_emoji": ":chart_with_upwards_trend:",
    "channel": "#project-ai-alerts"
  }
}
```

**Email:**
```json
{
  "type": "email",
  "settings": {
    "addresses": "alerts@project-ai.example.com",
    "singleEmail": true
  }
}
```

---

## Best Practices

### Dashboard Design

1. **Use Meaningful Titles:** Describe what the panel shows
2. **Add Descriptions:** Help text for complex panels
3. **Set Appropriate Units:** Percentages, bytes, seconds
4. **Use Color Thresholds:** Green/yellow/red for quick assessment
5. **Organize Logically:** Group related panels, use rows
6. **Leverage Variables:** Make dashboards reusable
7. **Test on Different Screen Sizes:** Ensure mobile compatibility

### Query Optimization

1. **Use Recording Rules:** Pre-compute expensive queries
2. **Limit Time Range:** Don't query years of data
3. **Use Rate for Counters:** `rate(metric[5m])` not `metric`
4. **Aggregate Early:** `sum by (label)` before histogram_quantile
5. **Avoid Regex:** Use exact label matches when possible

### Maintenance

1. **Regular Reviews:** Quarterly dashboard audits
2. **Remove Unused Dashboards:** Keep catalog clean
3. **Update Thresholds:** Adjust based on SLO changes
4. **Document Changes:** Version control dashboard JSON
5. **Test Alert Rules:** Verify notifications work

---

## Exporting and Importing Dashboards

### Export Dashboard

```bash
# Via UI
Dashboard → Share → Export → Save to file

# Via API
curl -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  http://localhost:3000/api/dashboards/uid/ai-persona \
  > ai_persona_dashboard.json
```

### Import Dashboard

```bash
# Via UI
Create → Import → Upload JSON file

# Via API
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  -d @ai_persona_dashboard.json \
  http://localhost:3000/api/dashboards/db
```

---

## Troubleshooting

### Dashboard Not Loading

**Symptom:** Dashboard shows "No data" or blank panels

**Solutions:**
1. Verify Prometheus datasource is configured
2. Check query syntax in panel editor
3. Verify metrics exist: `curl http://localhost:9090/api/v1/query?query=project_ai_persona_mood_energy`
4. Check time range (not too far in past)
5. Review Grafana logs: `docker logs project-ai-grafana`

### Slow Dashboard

**Symptom:** Dashboard takes >30s to load

**Solutions:**
1. Reduce time range
2. Use dashboard variables to filter data
3. Optimize queries (avoid regex, use recording rules)
4. Increase Grafana cache timeout
5. Consider splitting into multiple dashboards

### Alert Not Firing

**Symptom:** Alert configured but no notifications

**Solutions:**
1. Check alert rule conditions
2. Verify notification channel is configured
3. Test notification channel manually
4. Check alert state history in panel
5. Review Grafana alerting logs

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
- [Alert Rules Configuration](04_alert_rules_configuration.md)
- [Monitoring Operations Runbook](09_monitoring_operations_runbook.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **Grafana URL:** http://localhost:3000
- **Documentation:** `source-docs/monitoring/`
- **Dashboards:** `monitoring/grafana/dashboards/`
