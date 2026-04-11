# OctoReflex Telemetry Deployment Guide

## 📋 Prerequisites

- Python 3.8+
- Prometheus server
- Grafana instance
- (Optional) eBPF capabilities for kernel event monitoring

## 🚀 Quick Start Deployment

### 1. Install Dependencies

```bash
pip install prometheus-client opentelemetry-api
```

### 2. Start Telemetry System

```python
from octoreflex.internal.telemetry.bridge import get_telemetry_bridge

# Initialize telemetry
bridge = get_telemetry_bridge()

# Telemetry is now active and collecting metrics
```

### 3. Expose Metrics Endpoint

```python
from flask import Flask, Response
from octoreflex.internal.telemetry.bridge import get_telemetry_bridge

app = Flask(__name__)
bridge = get_telemetry_bridge()

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        bridge.export_metrics(),
        mimetype='text/plain'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
```

### 4. Configure Prometheus

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'octoreflex'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
```

Start Prometheus:
```bash
prometheus --config.file=prometheus.yml
```

### 5. Import Grafana Dashboards

1. Open Grafana (default: http://localhost:3000)
2. Go to **Dashboards** → **Import**
3. Upload `octoreflex/dashboards/octoreflex-main.json`
4. Upload `octoreflex/dashboards/octoreflex-performance.json`
5. Configure Prometheus data source

### 6. Configure Alerting (Optional)

Copy alerting rules to Prometheus:

```bash
cp octoreflex/dashboards/prometheus-alerts.yml /etc/prometheus/alerts/
```

Update `prometheus.yml`:

```yaml
rule_files:
  - "/etc/prometheus/alerts/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
```

## 🔧 Production Configuration

### Environment Variables

```bash
# Logging
export OCTOREFLEX_LOG_LEVEL=INFO
export OCTOREFLEX_LOG_FORMAT=json

# Metrics
export OCTOREFLEX_METRICS_PORT=9090
export OCTOREFLEX_METRICS_PATH=/metrics
export OCTOREFLEX_METRICS_ENABLED=true

# Tracing
export OCTOREFLEX_TRACE_ENABLED=true
export OCTOREFLEX_TRACE_SAMPLE_RATE=1.0
export OCTOREFLEX_TRACE_EXPORTER=jaeger

# Events
export OCTOREFLEX_EBPF_ENABLED=true
export OCTOREFLEX_EVENT_BUFFER_SIZE=65536
```

### Docker Deployment

Create `Dockerfile.telemetry`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy telemetry code
COPY octoreflex/internal/telemetry /app/octoreflex/internal/telemetry

# Expose metrics port
EXPOSE 9090

# Start metrics server
CMD ["python", "-m", "octoreflex.internal.telemetry.server"]
```

### Docker Compose

Create `docker-compose.telemetry.yml`:

```yaml
version: '3.8'

services:
  octoreflex:
    build:
      context: .
      dockerfile: Dockerfile.telemetry
    ports:
      - "9090:9090"
    environment:
      - OCTOREFLEX_LOG_LEVEL=INFO
      - OCTOREFLEX_METRICS_ENABLED=true
    volumes:
      - ./config:/app/config
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./octoreflex/dashboards/prometheus-alerts.yml:/etc/prometheus/alerts/alerts.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./octoreflex/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  grafana-data:
```

Start stack:
```bash
docker-compose -f docker-compose.telemetry.yml up -d
```

## 🎯 Kubernetes Deployment

### ConfigMap for Prometheus

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: octoreflex-prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 5s
    scrape_configs:
      - job_name: 'octoreflex'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: octoreflex
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: octoreflex
spec:
  replicas: 3
  selector:
    matchLabels:
      app: octoreflex
  template:
    metadata:
      labels:
        app: octoreflex
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: octoreflex
        image: octoreflex:latest
        ports:
        - containerPort: 9090
          name: metrics
        env:
        - name: OCTOREFLEX_METRICS_ENABLED
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: octoreflex-metrics
spec:
  selector:
    app: octoreflex
  ports:
  - port: 9090
    targetPort: 9090
    name: metrics
```

## 📊 Monitoring Setup

### Key Metrics to Monitor

1. **Threat Score** - `octoreflex_threat_score_current`
   - Alert: > 90 for 1 minute

2. **Containment Latency** - `octoreflex_containment_latency_seconds`
   - Alert: p95 > 1s for 5 minutes

3. **False Positive Rate** - Calculated from counters
   - Alert: > 10% for 10 minutes

4. **Event Processing** - `octoreflex_events_per_second`
   - Alert: Dropped to 0 for 5 minutes

### Health Checks

```python
from octoreflex.internal.telemetry.bridge import get_telemetry_bridge

def health_check():
    """Check telemetry system health"""
    bridge = get_telemetry_bridge()
    stats = bridge.get_stats()
    
    # Check event stream
    if stats['event_stream']['events_dropped'] > 1000:
        return False, "Too many events dropped"
    
    # Check buffer utilization
    buffer_pct = (stats['event_stream']['buffer_used'] / 
                  stats['event_stream']['buffer_size']) * 100
    if buffer_pct > 90:
        return False, f"Buffer {buffer_pct}% full"
    
    return True, "Healthy"
```

## 🔍 Troubleshooting

### Metrics Not Appearing

1. Check metrics endpoint: `curl http://localhost:9090/metrics`
2. Verify Prometheus scrape config
3. Check logs for errors

### High Memory Usage

1. Reduce event buffer size: `OCTOREFLEX_EVENT_BUFFER_SIZE=32768`
2. Decrease metric retention in Prometheus
3. Use recording rules for aggregation

### eBPF Events Missing

1. Check capabilities: `capsh --print`
2. Grant CAP_BPF: `setcap cap_bpf+ep /path/to/python`
3. Fallback to userspace monitoring

### Performance Issues

1. Run benchmarks: `python -m octoreflex.internal.telemetry.benchmark`
2. Check for lock contention
3. Reduce scrape frequency
4. Use sampling for traces

## 📈 Performance Tuning

### Buffer Sizing

```python
# For high-throughput systems
event_stream = eBPFEventStream(buffer_size=131072)  # 128K events

# For low-latency systems
event_stream = eBPFEventStream(buffer_size=16384)   # 16K events
```

### Metric Cardinality

```python
# Good: Low cardinality
prometheus.counter_inc("requests_total", labels={"status": "200"})

# Bad: High cardinality (avoid user IDs in labels)
# prometheus.counter_inc("requests_total", labels={"user_id": "12345"})
```

### Trace Sampling

```python
# Sample 10% of traces in production
tracer = OctoTracer()
if random.random() < 0.1:
    with tracer.span("operation"):
        # traced
        pass
```

## 🎓 Best Practices

1. **Always use correlation IDs** for request tracking
2. **Monitor latency percentiles** (p95, p99), not averages
3. **Set up alerting** before deployment
4. **Test under load** with realistic traffic
5. **Document custom metrics** in team wiki
6. **Regular review** of dashboards and alerts
7. **Clean up unused metrics** to reduce cardinality

## 📚 Resources

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [eBPF Tutorial](https://ebpf.io/what-is-ebpf/)
- [Grafana Dashboard Design](https://grafana.com/docs/grafana/latest/dashboards/)

## 🆘 Support

For issues or questions:
1. Check the README.md
2. Run diagnostics: `python -m octoreflex.internal.telemetry.diagnostics`
3. Review logs with correlation IDs
4. Open an issue with full context
