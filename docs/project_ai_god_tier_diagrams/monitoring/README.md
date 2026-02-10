# Project-AI Monitoring Stack

## Overview

Project-AI implements a production-grade observability stack using Prometheus, Grafana, and AlertManager. This comprehensive monitoring solution provides real-time insights into system health, performance metrics, and operational intelligence.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Application │─────▶│  Prometheus  │─────▶│  Grafana  │ │
│  │   Metrics    │      │   (TSDB)     │      │ (Dashboards)│
│  └──────────────┘      └──────┬───────┘      └───────────┘ │
│                               │                              │
│                               ▼                              │
│                        ┌──────────────┐                      │
│                        │ AlertManager │                      │
│                        │  (Alerting)  │                      │
│                        └──────┬───────┘                      │
│                               │                              │
│              ┌────────────────┼────────────────┐            │
│              ▼                ▼                ▼            │
│         ┌────────┐      ┌────────┐      ┌─────────┐        │
│         │ Email  │      │ Slack  │      │PagerDuty│        │
│         └────────┘      └────────┘      └─────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Prometheus
- **Role**: Time-series database and metrics collection
- **Port**: 9090
- **Scrape Interval**: 15s (configurable)
- **Retention**: 15 days (configurable)
- **Storage**: Local disk with optional remote write to Thanos/Cortex

### Grafana
- **Role**: Visualization and dashboarding
- **Port**: 3001
- **Data Sources**: Prometheus, Loki
- **Authentication**: Admin password, OAuth2 (optional)
- **Dashboards**: 12 pre-configured dashboards

### AlertManager
- **Role**: Alert routing and deduplication
- **Port**: 9093
- **Grouping Window**: 5m
- **Repeat Interval**: 4h
- **Receivers**: Email, Slack, PagerDuty, Webhook

## Metrics Categories

### Application Metrics
- Request rates and latencies
- Error rates and types
- AI model inference times
- Memory usage and GC statistics

### System Metrics
- CPU usage (user, system, idle)
- Memory usage (RSS, heap, swap)
- Disk I/O and space
- Network throughput

### Business Metrics
- Active users and sessions
- Feature usage (image generation, chat, learning paths)
- Persona interactions
- Command override attempts

### Performance Metrics
- API response times (p50, p95, p99)
- Database query latencies
- Cache hit/miss rates
- Plugin execution times

## Key Features

### Service Discovery
- **Static Targets**: Manual configuration for known services
- **Dynamic Discovery**: Kubernetes service discovery
- **File-Based**: JSON/YAML file_sd for container environments

### Recording Rules
- Pre-aggregated metrics for dashboard performance
- 5m, 1h, and 1d aggregation windows
- Resource usage trending
- SLA calculations

### Alerting Rules
- Multi-level severity (critical, warning, info)
- Intelligent alert grouping
- Rate-limiting and deduplication
- Context-rich alert descriptions

### Data Retention
- **Raw Metrics**: 15 days (high resolution)
- **5m Aggregates**: 60 days
- **1h Aggregates**: 1 year
- **Daily Aggregates**: 3 years

## Performance Specifications

### Prometheus
- **Ingestion Rate**: Up to 100k samples/sec
- **Query Latency**: p95 < 100ms for simple queries
- **Storage**: ~1-2 bytes per sample (compressed)
- **Memory**: 2-4GB for typical workload

### Grafana
- **Dashboard Load**: < 2s for typical dashboard
- **Concurrent Users**: Up to 100 (with caching)
- **Query Performance**: Depends on Prometheus backend
- **Refresh Rate**: 10s default, configurable per panel

### AlertManager
- **Alert Processing**: < 100ms per alert
- **Throughput**: Up to 10k alerts/min
- **Grouping Latency**: < 5s
- **Notification Latency**: < 30s (email), < 5s (webhook)

## Security

### Authentication
```python
# Prometheus basic auth
auth_config:
  username: admin
  password_hash: $2y$10$... # bcrypt hash
```

### TLS Configuration
```yaml
tls_config:
  cert_file: /etc/prometheus/certs/prometheus.crt
  key_file: /etc/prometheus/certs/prometheus.key
  ca_file: /etc/prometheus/certs/ca.crt
```

### Network Security
- Firewall rules limiting access to monitoring ports
- VPC isolation for monitoring infrastructure
- mTLS between Prometheus and exporters
- API authentication via bearer tokens

## High Availability

### Prometheus HA
```yaml
# Two Prometheus instances scraping identical targets
# Load balancer distributes query traffic
# AlertManager handles deduplication

prometheus_instance_1:
  external_labels:
    replica: 1
    
prometheus_instance_2:
  external_labels:
    replica: 2
```

### Grafana HA
- Multi-instance deployment behind load balancer
- Shared MySQL/PostgreSQL database
- Session affinity via sticky cookies
- Automated failover in < 10s

### AlertManager Clustering
```yaml
# AlertManager cluster configuration
cluster:
  listen_address: 0.0.0.0:9094
  peers:
    - alertmanager-1:9094
    - alertmanager-2:9094
    - alertmanager-3:9094
```

## Integration Points

### Application Integration
```python
from prometheus_client import Counter, Histogram, Gauge, Info

# Metrics registration
request_counter = Counter(
    'project_ai_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'project_ai_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

active_users = Gauge(
    'project_ai_active_users',
    'Number of active users'
)
```

### Export Endpoints
```python
# Flask integration
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Metrics available at /metrics
# Custom metrics via decorators
@app.route('/api/generate')
@metrics.histogram('generate_duration', 'Image generation duration')
def generate_image():
    # ... implementation
    pass
```

## Monitoring Deployment

### Docker Compose
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.45.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      
  grafana:
    image: grafana/grafana:10.0.0
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
      
  alertmanager:
    image: prom/alertmanager:v0.26.0
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"

volumes:
  prometheus_data:
  grafana_data:
```

### Kubernetes Deployment
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus
  namespace: monitoring
spec:
  serviceName: prometheus
  replicas: 2
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
  volumeClaimTemplates:
  - metadata:
      name: storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

## Troubleshooting

### Common Issues

**Prometheus not scraping targets**
```bash
# Check target status
curl http://localhost:9090/api/v1/targets

# Verify network connectivity
telnet <target_host> <target_port>

# Check Prometheus logs
docker logs prometheus
```

**High memory usage**
```bash
# Check cardinality
curl http://localhost:9090/api/v1/status/tsdb

# Reduce retention
--storage.tsdb.retention.time=7d

# Increase memory limit in docker-compose.yml
mem_limit: 4g
```

**Missing metrics**
```python
# Verify metric registration
from prometheus_client import REGISTRY
print(list(REGISTRY._collector_to_names.keys()))

# Check metric export endpoint
curl http://localhost:8000/metrics
```

## Related Documentation

- [Prometheus Configuration](./prometheus_configuration.md) - Complete scrape configs and rules
- [Grafana Dashboards](./grafana_dashboards.md) - Dashboard JSON and panel configs
- [Alerting Strategy](./alerting_strategy.md) - Alert definitions and escalation
- [Metrics Catalog](./metrics_catalog.md) - Complete metrics reference

## External Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
