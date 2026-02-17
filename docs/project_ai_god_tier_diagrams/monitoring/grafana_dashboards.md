# Grafana Dashboards

## Dashboard Architecture

Project-AI includes 12 production-ready Grafana dashboards providing comprehensive visualization of system metrics, application performance, and business intelligence.

## Dashboard Catalog

### 1. System Overview Dashboard

**ID**: `project-ai-overview` **Purpose**: High-level system health and performance **Refresh**: 10s **Time Range**: Last 6 hours

### 2. Application Performance Dashboard

**ID**: `project-ai-app-performance` **Purpose**: Request rates, latencies, error rates **Refresh**: 10s **Time Range**: Last 1 hour

### 3. AI Models Dashboard

**ID**: `project-ai-ai-models` **Purpose**: AI inference metrics, model performance **Refresh**: 30s **Time Range**: Last 6 hours

### 4. Infrastructure Dashboard

**ID**: `project-ai-infrastructure` **Purpose**: CPU, memory, disk, network metrics **Refresh**: 15s **Time Range**: Last 3 hours

### 5. Database Dashboard

**ID**: `project-ai-database` **Purpose**: PostgreSQL performance and health **Refresh**: 15s **Time Range**: Last 1 hour

### 6. Cache Dashboard

**ID**: `project-ai-cache` **Purpose**: Redis cache performance **Refresh**: 15s **Time Range**: Last 1 hour

### 7. Temporal Workflows Dashboard

**ID**: `project-ai-temporal` **Purpose**: Workflow orchestration metrics **Refresh**: 30s **Time Range**: Last 6 hours

### 8. User Activity Dashboard

**ID**: `project-ai-users` **Purpose**: User engagement and feature usage **Refresh**: 1m **Time Range**: Last 24 hours

### 9. Security Dashboard

**ID**: `project-ai-security` **Purpose**: Authentication, authorization, security events **Refresh**: 30s **Time Range**: Last 24 hours

### 10. SLA Dashboard

**ID**: `project-ai-sla` **Purpose**: SLA compliance and error budgets **Refresh**: 5m **Time Range**: Last 30 days

### 11. Business Metrics Dashboard

**ID**: `project-ai-business` **Purpose**: Feature usage, conversion metrics **Refresh**: 5m **Time Range**: Last 7 days

### 12. Alerts Dashboard

**ID**: `project-ai-alerts` **Purpose**: Active alerts and alert history **Refresh**: 30s **Time Range**: Last 24 hours

## Complete Dashboard JSON Examples

### System Overview Dashboard

```json
{
  "dashboard": {
    "id": null,
    "uid": "project-ai-overview",
    "title": "Project-AI System Overview",
    "tags": ["project-ai", "overview"],
    "timezone": "browser",
    "schemaVersion": 36,
    "version": 1,
    "refresh": "10s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
        "type": "stat",
        "title": "System Status",
        "targets": [
          {
            "expr": "up{job=~\"project-ai.*\"}",
            "refId": "A",
            "legendFormat": "{{instance}}"
          }
        ],
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          },
          "colorMode": "background",
          "graphMode": "none",
          "orientation": "auto",
          "textMode": "auto"
        },
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {"type": "value", "value": "0", "text": "DOWN", "color": "red"},
              {"type": "value", "value": "1", "text": "UP", "color": "green"}
            ],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 1, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
        "type": "stat",
        "title": "Request Rate",
        "targets": [
          {
            "expr": "sum(rate(project_ai_requests_total[5m]))",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          },
          "colorMode": "value",
          "graphMode": "area",
          "orientation": "auto",
          "textMode": "value_and_name"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "decimals": 2,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 100, "color": "yellow"},
                {"value": 500, "color": "red"}
              ]
            }
          }
        }
      },
      {
        "id": 3,
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
        "type": "stat",
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum(rate(project_ai_requests_total{status=~\"5..\"}[5m])) / sum(rate(project_ai_requests_total[5m])) * 100",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          },
          "colorMode": "value",
          "graphMode": "area",
          "orientation": "auto",
          "textMode": "value_and_name"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 2,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 1, "color": "yellow"},
                {"value": 5, "color": "red"}
              ]
            }
          }
        }
      },
      {
        "id": 4,
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
        "type": "stat",
        "title": "Active Users",
        "targets": [
          {
            "expr": "sum(project_ai_active_users)",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {
            "values": false,
            "calcs": ["lastNotNull"]
          },
          "colorMode": "value",
          "graphMode": "area",
          "orientation": "auto",
          "textMode": "value_and_name"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 1, "color": "yellow"},
                {"value": 10, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 5,
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
        "type": "graph",
        "title": "Request Rate by Endpoint",
        "targets": [
          {
            "expr": "sum(rate(project_ai_requests_total[5m])) by (endpoint)",
            "refId": "A",
            "legendFormat": "{{endpoint}}"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "reqps", "label": "Requests/sec", "show": true},
          {"format": "short", "show": false}
        ],
        "legend": {
          "show": true,
          "alignAsTable": true,
          "avg": true,
          "current": true,
          "max": true,
          "min": false,
          "rightSide": false,
          "total": false,
          "values": true
        },
        "lines": true,
        "fill": 1,
        "linewidth": 2,
        "points": false,
        "pointradius": 5,
        "bars": false,
        "stack": false,
        "percentage": false,
        "nullPointMode": "null"
      },
      {
        "id": 6,
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
        "type": "graph",
        "title": "Response Time Percentiles",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le))",
            "refId": "A",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le))",
            "refId": "B",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le))",
            "refId": "C",
            "legendFormat": "p99"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "s", "label": "Response Time", "show": true},
          {"format": "short", "show": false}
        ],
        "legend": {
          "show": true,
          "alignAsTable": true,
          "avg": true,
          "current": true,
          "max": true,
          "min": false,
          "rightSide": false,
          "total": false,
          "values": true
        },
        "lines": true,
        "fill": 1,
        "linewidth": 2,
        "points": false,
        "bars": false,
        "stack": false
      },
      {
        "id": 7,
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
        "type": "graph",
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "refId": "A",
            "legendFormat": "{{instance}}"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "percent", "label": "CPU %", "show": true, "min": 0, "max": 100},
          {"format": "short", "show": false}
        ],
        "legend": {"show": true, "values": true, "current": true},
        "lines": true,
        "fill": 1,
        "linewidth": 2
      },
      {
        "id": 8,
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
        "type": "graph",
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "refId": "A",
            "legendFormat": "{{instance}}"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "percent", "label": "Memory %", "show": true, "min": 0, "max": 100},
          {"format": "short", "show": false}
        ],
        "legend": {"show": true, "values": true, "current": true},
        "lines": true,
        "fill": 1,
        "linewidth": 2
      }
    ]
  }
}
```

### AI Models Dashboard

```json
{
  "dashboard": {
    "id": null,
    "uid": "project-ai-ai-models",
    "title": "Project-AI AI Models",
    "tags": ["project-ai", "ai", "models"],
    "timezone": "browser",
    "schemaVersion": 36,
    "version": 1,
    "refresh": "30s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "type": "graph",
        "title": "AI Inference Duration by Model",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(project_ai_ai_inference_duration_seconds_bucket[5m])) by (le, model))",
            "refId": "A",
            "legendFormat": "{{model}} (p95)"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "s", "label": "Duration", "show": true},
          {"format": "short", "show": false}
        ],
        "legend": {"show": true, "values": true, "current": true, "max": true},
        "lines": true,
        "fill": 1,
        "linewidth": 2,
        "alert": {
          "name": "Slow AI Inference",
          "conditions": [
            {
              "evaluator": {"params": [30], "type": "gt"},
              "operator": {"type": "and"},
              "query": {"params": ["A", "5m", "now"]},
              "reducer": {"params": [], "type": "avg"},
              "type": "query"
            }
          ],
          "executionErrorState": "alerting",
          "for": "10m",
          "frequency": "1m",
          "handler": 1,
          "message": "AI inference taking longer than 30s",
          "name": "Slow AI Inference",
          "noDataState": "no_data",
          "notifications": []
        }
      },
      {
        "id": 2,
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "type": "graph",
        "title": "AI Inference Rate by Model",
        "targets": [
          {
            "expr": "sum(rate(project_ai_ai_inference_total[5m])) by (model)",
            "refId": "A",
            "legendFormat": "{{model}}"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "reqps", "label": "Inferences/sec", "show": true},
          {"format": "short", "show": false}
        ],
        "legend": {"show": true, "values": true, "current": true},
        "lines": true,
        "fill": 1,
        "linewidth": 2,
        "stack": true
      },
      {
        "id": 3,
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
        "type": "graph",
        "title": "Image Generation Rate by Backend",
        "targets": [
          {
            "expr": "sum(rate(project_ai_image_generation_total[5m])) by (backend, style)",
            "refId": "A",
            "legendFormat": "{{backend}} - {{style}}"
          }
        ],
        "xaxis": {"mode": "time", "show": true},
        "yaxes": [
          {"format": "reqps", "label": "Generations/sec", "show": true},
          {"format": "short", "show": false}
        ],
        "legend": {"show": true, "values": true, "current": true},
        "lines": true,
        "fill": 1,
        "linewidth": 2
      },
      {
        "id": 4,
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
        "type": "piechart",
        "title": "AI Model Usage Distribution",
        "targets": [
          {
            "expr": "sum(increase(project_ai_ai_inference_total[1h])) by (model)",
            "refId": "A",
            "legendFormat": "{{model}}"
          }
        ],
        "options": {
          "legend": {
            "displayMode": "table",
            "placement": "right",
            "values": ["value", "percent"]
          },
          "pieType": "pie",
          "tooltip": {"mode": "single"}
        }
      },
      {
        "id": 5,
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 16},
        "type": "stat",
        "title": "OpenAI API Success Rate",
        "targets": [
          {
            "expr": "sum(rate(project_ai_ai_inference_total{backend=\"openai\", status=\"success\"}[5m])) / sum(rate(project_ai_ai_inference_total{backend=\"openai\"}[5m])) * 100",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {"values": false, "calcs": ["lastNotNull"]},
          "colorMode": "value",
          "graphMode": "area"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 2,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 95, "color": "yellow"},
                {"value": 99, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 6,
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 16},
        "type": "stat",
        "title": "HuggingFace API Success Rate",
        "targets": [
          {
            "expr": "sum(rate(project_ai_ai_inference_total{backend=\"huggingface\", status=\"success\"}[5m])) / sum(rate(project_ai_ai_inference_total{backend=\"huggingface\"}[5m])) * 100",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {"values": false, "calcs": ["lastNotNull"]},
          "colorMode": "value",
          "graphMode": "area"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "decimals": 2,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 95, "color": "yellow"},
                {"value": 99, "color": "green"}
              ]
            }
          }
        }
      },
      {
        "id": 7,
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 16},
        "type": "stat",
        "title": "Total AI Inferences (24h)",
        "targets": [
          {
            "expr": "sum(increase(project_ai_ai_inference_total[24h]))",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {"values": false, "calcs": ["lastNotNull"]},
          "colorMode": "value",
          "graphMode": "none"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0
          }
        }
      },
      {
        "id": 8,
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 16},
        "type": "stat",
        "title": "Total Images Generated (24h)",
        "targets": [
          {
            "expr": "sum(increase(project_ai_image_generation_total[24h]))",
            "refId": "A"
          }
        ],
        "options": {
          "reduceOptions": {"values": false, "calcs": ["lastNotNull"]},
          "colorMode": "value",
          "graphMode": "none"
        },
        "fieldConfig": {
          "defaults": {
            "unit": "short",
            "decimals": 0
          }
        }
      }
    ]
  }
}
```

## Dashboard Provisioning

### Provisioning Configuration

```yaml

# /etc/grafana/provisioning/dashboards/project-ai.yaml

apiVersion: 1

providers:

  - name: 'Project-AI Dashboards'

    orgId: 1
    folder: 'Project-AI'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards/project-ai
      foldersFromFilesStructure: true
```

### Data Source Provisioning

```yaml

# /etc/grafana/provisioning/datasources/prometheus.yaml

apiVersion: 1

datasources:

  - name: Prometheus

    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: 15s
      queryTimeout: 60s
      httpMethod: POST
    version: 1

  - name: Loki

    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    editable: false
    jsonData:
      maxLines: 1000
      derivedFields:

        - datasourceUid: Prometheus

          matcherRegex: "traceID=(\\w+)"
          name: TraceID
          url: "$${__value.raw}"
    version: 1
```

## Panel Templates

### Stat Panel Template

```json
{
  "type": "stat",
  "title": "Panel Title",
  "targets": [{"expr": "metric_query", "refId": "A"}],
  "options": {
    "reduceOptions": {"values": false, "calcs": ["lastNotNull"]},
    "colorMode": "value",
    "graphMode": "area",
    "orientation": "auto",
    "textMode": "value_and_name"
  },
  "fieldConfig": {
    "defaults": {
      "unit": "short",
      "decimals": 2,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 80, "color": "yellow"},
          {"value": 90, "color": "red"}
        ]
      }
    }
  }
}
```

### Graph Panel Template

```json
{
  "type": "graph",
  "title": "Time Series Graph",
  "targets": [
    {"expr": "metric_query", "refId": "A", "legendFormat": "{{label}}"}
  ],
  "xaxis": {"mode": "time", "show": true},
  "yaxes": [
    {"format": "short", "label": "Y-Axis Label", "show": true},
    {"format": "short", "show": false}
  ],
  "legend": {
    "show": true,
    "alignAsTable": true,
    "avg": true,
    "current": true,
    "max": true,
    "min": false,
    "rightSide": false,
    "total": false,
    "values": true
  },
  "lines": true,
  "fill": 1,
  "linewidth": 2,
  "points": false,
  "bars": false,
  "stack": false,
  "percentage": false,
  "nullPointMode": "null"
}
```

### Heatmap Panel Template

```json
{
  "type": "heatmap",
  "title": "Request Duration Heatmap",
  "targets": [
    {
      "expr": "sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le)",
      "refId": "A",
      "format": "heatmap",
      "legendFormat": "{{le}}"
    }
  ],
  "dataFormat": "tsbuckets",
  "heatmap": {},
  "highlightCards": true,
  "cardColor": "#b4ff00",
  "color": {
    "mode": "spectrum",
    "cardColor": "#b4ff00",
    "colorScale": "sqrt",
    "exponent": 0.5,
    "colorScheme": "interpolateOranges"
  },
  "legend": {"show": true},
  "yAxis": {
    "format": "s",
    "decimals": 2,
    "logBase": 1,
    "show": true
  },
  "xAxis": {
    "show": true,
    "mode": "time"
  }
}
```

## Variables and Templating

```json
{
  "templating": {
    "list": [
      {
        "name": "instance",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(up{job=\"project-ai-app\"}, instance)",
        "refresh": 1,
        "multi": true,
        "includeAll": true,
        "allValue": ".*"
      },
      {
        "name": "endpoint",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(project_ai_requests_total, endpoint)",
        "refresh": 1,
        "multi": true,
        "includeAll": true
      },
      {
        "name": "time_range",
        "type": "interval",
        "options": [
          {"text": "1m", "value": "1m"},
          {"text": "5m", "value": "5m"},
          {"text": "15m", "value": "15m"},
          {"text": "1h", "value": "1h"}
        ],
        "current": {"text": "5m", "value": "5m"}
      }
    ]
  }
}
```

## Alert Configuration in Panels

```json
{
  "alert": {
    "name": "High Response Time",
    "conditions": [
      {
        "evaluator": {"params": [5.0], "type": "gt"},
        "operator": {"type": "and"},
        "query": {"params": ["A", "5m", "now"]},
        "reducer": {"params": [], "type": "avg"},
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "for": "10m",
    "frequency": "1m",
    "handler": 1,
    "message": "Response time has exceeded 5 seconds for the past 10 minutes",
    "name": "High Response Time Alert",
    "noDataState": "no_data",
    "notifications": [
      {"uid": "slack-notifications"},
      {"uid": "email-critical"}
    ]
  }
}
```

## Python Dashboard Generation

```python

# src/app/monitoring/grafana_dashboard_generator.py

import json
from typing import Dict, List, Any

class GrafanaDashboardGenerator:
    """Generate Grafana dashboards programmatically"""

    def __init__(self):
        self.dashboard = {
            "dashboard": {
                "id": None,
                "uid": None,
                "title": "",
                "tags": [],
                "timezone": "browser",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "10s",
                "time": {"from": "now-6h", "to": "now"},
                "panels": []
            }
        }

    def create_dashboard(self, uid: str, title: str, tags: List[str]) -> 'GrafanaDashboardGenerator':
        """Initialize dashboard metadata"""
        self.dashboard["dashboard"]["uid"] = uid
        self.dashboard["dashboard"]["title"] = title
        self.dashboard["dashboard"]["tags"] = tags
        return self

    def add_stat_panel(
        self,
        panel_id: int,
        title: str,
        query: str,
        unit: str = "short",
        x: int = 0,
        y: int = 0,
        w: int = 6,
        h: int = 4,
        thresholds: List[Dict] = None
    ) -> 'GrafanaDashboardGenerator':
        """Add a stat panel to the dashboard"""
        if thresholds is None:
            thresholds = [
                {"value": 0, "color": "green"},
                {"value": 80, "color": "yellow"},
                {"value": 90, "color": "red"}
            ]

        panel = {
            "id": panel_id,
            "gridPos": {"h": h, "w": w, "x": x, "y": y},
            "type": "stat",
            "title": title,
            "targets": [{"expr": query, "refId": "A"}],
            "options": {
                "reduceOptions": {"values": False, "calcs": ["lastNotNull"]},
                "colorMode": "value",
                "graphMode": "area"
            },
            "fieldConfig": {
                "defaults": {
                    "unit": unit,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": thresholds
                    }
                }
            }
        }
        self.dashboard["dashboard"]["panels"].append(panel)
        return self

    def add_graph_panel(
        self,
        panel_id: int,
        title: str,
        queries: List[Dict[str, str]],
        unit: str = "short",
        x: int = 0,
        y: int = 0,
        w: int = 12,
        h: int = 8,
        stack: bool = False
    ) -> 'GrafanaDashboardGenerator':
        """Add a graph panel to the dashboard"""
        targets = [
            {"expr": q["expr"], "refId": chr(65 + i), "legendFormat": q.get("legend", "")}
            for i, q in enumerate(queries)
        ]

        panel = {
            "id": panel_id,
            "gridPos": {"h": h, "w": w, "x": x, "y": y},
            "type": "graph",
            "title": title,
            "targets": targets,
            "xaxis": {"mode": "time", "show": True},
            "yaxes": [
                {"format": unit, "show": True},
                {"format": "short", "show": False}
            ],
            "legend": {"show": True, "values": True, "current": True},
            "lines": True,
            "fill": 1,
            "linewidth": 2,
            "stack": stack
        }
        self.dashboard["dashboard"]["panels"].append(panel)
        return self

    def export_json(self, filename: str):
        """Export dashboard to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.dashboard, f, indent=2)

    def to_json(self) -> str:
        """Return dashboard as JSON string"""
        return json.dumps(self.dashboard, indent=2)

# Usage example

def generate_overview_dashboard():
    """Generate the system overview dashboard"""
    generator = GrafanaDashboardGenerator()

    dashboard = (
        generator
        .create_dashboard("project-ai-overview", "Project-AI System Overview", ["project-ai", "overview"])
        .add_stat_panel(
            panel_id=1,
            title="System Status",
            query='up{job=~"project-ai.*"}',
            unit="short",
            x=0, y=0, w=6, h=4,
            thresholds=[
                {"value": 0, "color": "red"},
                {"value": 1, "color": "green"}
            ]
        )
        .add_stat_panel(
            panel_id=2,
            title="Request Rate",
            query="sum(rate(project_ai_requests_total[5m]))",
            unit="reqps",
            x=6, y=0, w=6, h=4
        )
        .add_graph_panel(
            panel_id=3,
            title="Request Rate by Endpoint",
            queries=[
                {
                    "expr": "sum(rate(project_ai_requests_total[5m])) by (endpoint)",
                    "legend": "{{endpoint}}"
                }
            ],
            unit="reqps",
            x=0, y=4, w=12, h=8
        )
    )

    dashboard.export_json("/etc/grafana/dashboards/project-ai/overview.json")
    return dashboard.to_json()

if __name__ == "__main__":
    generate_overview_dashboard()
```

## Dashboard Performance Optimization

### Query Optimization

```json
{
  "targets": [
    {
      "expr": "rate(metric[5m])",
      "interval": "30s",
      "intervalFactor": 2,
      "step": 60
    }
  ]
}
```

### Caching Configuration

```ini

# /etc/grafana/grafana.ini

[caching]
enabled = true
ttl = 60

[dataproxy]
timeout = 30
keep_alive_seconds = 30
```

## Troubleshooting

```bash

# Test dashboard JSON syntax

jq . < dashboard.json

# Validate datasource connectivity

curl http://grafana:3000/api/datasources/proxy/1/api/v1/query?query=up

# Check dashboard provisioning

ls -la /etc/grafana/provisioning/dashboards/
cat /var/log/grafana/grafana.log | grep provisioning
```
