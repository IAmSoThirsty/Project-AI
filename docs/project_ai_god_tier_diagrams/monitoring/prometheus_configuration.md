# Prometheus Configuration

## Complete Configuration File

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'project-ai-production'
    region: 'us-east-1'
    environment: 'production'

# AlertManager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'alertmanager-1:9093'
            - 'alertmanager-2:9093'
      timeout: 10s
      api_version: v2

# Load rules from files
rule_files:
  - '/etc/prometheus/rules/recording_rules.yml'
  - '/etc/prometheus/rules/alerting_rules.yml'
  - '/etc/prometheus/rules/sla_rules.yml'

# Scrape configurations
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          instance: 'prometheus-1'
          service: 'prometheus'

  # Project-AI application metrics
  - job_name: 'project-ai-app'
    scrape_interval: 10s
    scrape_timeout: 5s
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'app-1:8000'
          - 'app-2:8000'
          - 'app-3:8000'
        labels:
          service: 'project-ai'
          component: 'application'
    relabel_configs:
      # Extract instance name from address
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+):.*'
        replacement: '$1'

  # Flask API servers
  - job_name: 'project-ai-api'
    scrape_interval: 10s
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'api-1:5000'
          - 'api-2:5000'
        labels:
          service: 'project-ai-api'
          component: 'backend'

  # PyQt6 desktop application (via local exporter)
  - job_name: 'project-ai-desktop'
    scrape_interval: 30s
    static_configs:
      - targets:
          - 'localhost:8001'
        labels:
          service: 'project-ai-desktop'
          component: 'gui'

  # Node exporter for system metrics
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node-exporter-1:9100'
          - 'node-exporter-2:9100'
          - 'node-exporter-3:9100'
        labels:
          service: 'node-exporter'
          component: 'infrastructure'

  # PostgreSQL exporter
  - job_name: 'postgresql'
    static_configs:
      - targets:
          - 'postgres-exporter:9187'
        labels:
          service: 'postgresql'
          component: 'database'

  # Redis exporter
  - job_name: 'redis'
    static_configs:
      - targets:
          - 'redis-exporter:9121'
        labels:
          service: 'redis'
          component: 'cache'

  # Temporal.io workflow engine
  - job_name: 'temporal'
    scrape_interval: 15s
    static_configs:
      - targets:
          - 'temporal-frontend:9090'
          - 'temporal-history:9090'
          - 'temporal-matching:9090'
          - 'temporal-worker:9090'
        labels:
          service: 'temporal'
          component: 'orchestration'

  # Kubernetes service discovery (if deployed on k8s)
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with prometheus.io/scrape annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      # Use custom scrape path if defined
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      # Use custom port if defined
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      # Add namespace label
      - source_labels: [__meta_kubernetes_namespace]
        target_label: kubernetes_namespace
      # Add pod name label
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: kubernetes_pod_name

  # File-based service discovery (for dynamic targets)
  - job_name: 'file-sd'
    file_sd_configs:
      - files:
          - '/etc/prometheus/targets/*.json'
        refresh_interval: 30s

# Remote write configuration (for long-term storage)
remote_write:
  - url: 'http://thanos-receive:19291/api/v1/receive'
    queue_config:
      capacity: 10000
      max_shards: 50
      max_samples_per_send: 1000
      batch_send_deadline: 5s
    write_relabel_configs:
      # Drop high-cardinality metrics
      - source_labels: [__name__]
        regex: 'go_.*|process_.*'
        action: drop

# Remote read configuration (for query federation)
remote_read:
  - url: 'http://thanos-query:10902/api/v1/query'
    read_recent: true
```

## Recording Rules

```yaml
# /etc/prometheus/rules/recording_rules.yml
groups:
  # Application-level recording rules
  - name: project_ai_application
    interval: 1m
    rules:
      # Request rate (requests per second)
      - record: project_ai:requests:rate5m
        expr: |
          sum(rate(project_ai_requests_total[5m])) by (method, endpoint, status)
      
      # Error rate percentage
      - record: project_ai:requests:error_rate5m
        expr: |
          sum(rate(project_ai_requests_total{status=~"5.."}[5m])) by (service)
          /
          sum(rate(project_ai_requests_total[5m])) by (service)
          * 100
      
      # Request duration percentiles
      - record: project_ai:request_duration:p50
        expr: |
          histogram_quantile(0.50, sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le, endpoint))
      
      - record: project_ai:request_duration:p95
        expr: |
          histogram_quantile(0.95, sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le, endpoint))
      
      - record: project_ai:request_duration:p99
        expr: |
          histogram_quantile(0.99, sum(rate(project_ai_request_duration_seconds_bucket[5m])) by (le, endpoint))
      
      # Active users gauge
      - record: project_ai:users:active
        expr: |
          sum(project_ai_active_users) by (instance)

  # AI model performance
  - name: project_ai_ai_models
    interval: 1m
    rules:
      # Model inference duration
      - record: project_ai:ai_inference:duration:p95
        expr: |
          histogram_quantile(0.95, sum(rate(project_ai_ai_inference_duration_seconds_bucket[5m])) by (le, model))
      
      # Model success rate
      - record: project_ai:ai_inference:success_rate5m
        expr: |
          sum(rate(project_ai_ai_inference_total{status="success"}[5m])) by (model)
          /
          sum(rate(project_ai_ai_inference_total[5m])) by (model)
          * 100
      
      # Image generation rate
      - record: project_ai:image_generation:rate5m
        expr: |
          sum(rate(project_ai_image_generation_total[5m])) by (backend, style)
      
      # Chat message rate
      - record: project_ai:chat:message_rate5m
        expr: |
          sum(rate(project_ai_chat_messages_total[5m])) by (persona)

  # System resource usage
  - name: project_ai_resources
    interval: 1m
    rules:
      # CPU usage percentage
      - record: project_ai:cpu:usage_percent
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
      
      # Memory usage percentage
      - record: project_ai:memory:usage_percent
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
      
      # Disk usage percentage
      - record: project_ai:disk:usage_percent
        expr: |
          (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
      
      # Network throughput (bytes per second)
      - record: project_ai:network:receive_bytes_per_second
        expr: |
          rate(node_network_receive_bytes_total[5m])
      
      - record: project_ai:network:transmit_bytes_per_second
        expr: |
          rate(node_network_transmit_bytes_total[5m])

  # Database performance
  - name: project_ai_database
    interval: 1m
    rules:
      # Database connection pool usage
      - record: project_ai:db:connections:usage_percent
        expr: |
          (pg_stat_database_numbackends / pg_settings_max_connections) * 100
      
      # Query duration
      - record: project_ai:db:query_duration:p95
        expr: |
          histogram_quantile(0.95, sum(rate(pg_stat_statements_total_time_bucket[5m])) by (le, datname))
      
      # Transaction rate
      - record: project_ai:db:transactions:rate5m
        expr: |
          rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])

  # Cache performance
  - name: project_ai_cache
    interval: 1m
    rules:
      # Cache hit rate
      - record: project_ai:cache:hit_rate5m
        expr: |
          sum(rate(redis_keyspace_hits_total[5m]))
          /
          (sum(rate(redis_keyspace_hits_total[5m])) + sum(rate(redis_keyspace_misses_total[5m])))
          * 100
      
      # Cache memory usage
      - record: project_ai:cache:memory:usage_bytes
        expr: |
          redis_memory_used_bytes
      
      # Cache eviction rate
      - record: project_ai:cache:evictions:rate5m
        expr: |
          rate(redis_evicted_keys_total[5m])

  # Temporal workflow engine
  - name: project_ai_temporal
    interval: 1m
    rules:
      # Workflow execution rate
      - record: project_ai:temporal:workflow_executions:rate5m
        expr: |
          sum(rate(temporal_workflow_execution_count[5m])) by (workflow_type)
      
      # Workflow success rate
      - record: project_ai:temporal:workflow_success_rate5m
        expr: |
          sum(rate(temporal_workflow_execution_count{status="completed"}[5m])) by (workflow_type)
          /
          sum(rate(temporal_workflow_execution_count[5m])) by (workflow_type)
          * 100
      
      # Task queue lag
      - record: project_ai:temporal:task_queue_lag
        expr: |
          temporal_task_queue_depth - temporal_task_queue_processed_rate

  # Hourly aggregations (for long-term trends)
  - name: project_ai_hourly
    interval: 1h
    rules:
      # Hourly request count
      - record: project_ai:requests:count:1h
        expr: |
          sum(increase(project_ai_requests_total[1h])) by (service, status)
      
      # Hourly active users
      - record: project_ai:users:active:1h
        expr: |
          avg_over_time(project_ai:users:active[1h])
      
      # Hourly error count
      - record: project_ai:errors:count:1h
        expr: |
          sum(increase(project_ai_requests_total{status=~"5.."}[1h])) by (service)

  # Daily aggregations (for reporting)
  - name: project_ai_daily
    interval: 1d
    rules:
      # Daily request count
      - record: project_ai:requests:count:1d
        expr: |
          sum(increase(project_ai_requests_total[1d])) by (service)
      
      # Daily unique users
      - record: project_ai:users:unique:1d
        expr: |
          max_over_time(project_ai:users:active[1d])
      
      # Daily uptime percentage
      - record: project_ai:uptime:percent:1d
        expr: |
          (1 - (sum(increase(up{job="project-ai-app"}[1d]) == 0) / count(up{job="project-ai-app"}))) * 100
```

## Alerting Rules

```yaml
# /etc/prometheus/rules/alerting_rules.yml
groups:
  # Critical alerts (require immediate attention)
  - name: project_ai_critical
    interval: 1m
    rules:
      # Service down
      - alert: ServiceDown
        expr: up{job=~"project-ai.*"} == 0
        for: 2m
        labels:
          severity: critical
          component: infrastructure
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for more than 2 minutes."
          runbook_url: "https://docs.project-ai.com/runbooks/service-down"
      
      # High error rate
      - alert: HighErrorRate
        expr: project_ai:requests:error_rate5m > 5
        for: 5m
        labels:
          severity: critical
          component: application
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for service {{ $labels.service }}"
          runbook_url: "https://docs.project-ai.com/runbooks/high-error-rate"
      
      # Database connection pool exhausted
      - alert: DatabaseConnectionPoolExhausted
        expr: project_ai:db:connections:usage_percent > 90
        for: 2m
        labels:
          severity: critical
          component: database
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool is at {{ $value | humanizePercentage }} capacity"
          runbook_url: "https://docs.project-ai.com/runbooks/db-connections"
      
      # Disk space critical
      - alert: DiskSpaceCritical
        expr: project_ai:disk:usage_percent > 90
        for: 5m
        labels:
          severity: critical
          component: infrastructure
        annotations:
          summary: "Disk space critical on {{ $labels.instance }}"
          description: "Disk usage is {{ $value | humanizePercentage }}"
          runbook_url: "https://docs.project-ai.com/runbooks/disk-space"
      
      # Memory pressure
      - alert: HighMemoryUsage
        expr: project_ai:memory:usage_percent > 90
        for: 5m
        labels:
          severity: critical
          component: infrastructure
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value | humanizePercentage }}"
          runbook_url: "https://docs.project-ai.com/runbooks/memory-pressure"

  # Warning alerts
  - name: project_ai_warnings
    interval: 1m
    rules:
      # High response time
      - alert: HighResponseTime
        expr: project_ai:request_duration:p95 > 5
        for: 10m
        labels:
          severity: warning
          component: application
        annotations:
          summary: "High response time on {{ $labels.endpoint }}"
          description: "P95 response time is {{ $value }}s"
          runbook_url: "https://docs.project-ai.com/runbooks/high-latency"
      
      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: project_ai:cache:hit_rate5m < 80
        for: 15m
        labels:
          severity: warning
          component: cache
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"
          runbook_url: "https://docs.project-ai.com/runbooks/cache-performance"
      
      # High CPU usage
      - alert: HighCPUUsage
        expr: project_ai:cpu:usage_percent > 80
        for: 15m
        labels:
          severity: warning
          component: infrastructure
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanizePercentage }}"
          runbook_url: "https://docs.project-ai.com/runbooks/cpu-usage"
      
      # Temporal workflow failures
      - alert: HighWorkflowFailureRate
        expr: project_ai:temporal:workflow_success_rate5m < 95
        for: 10m
        labels:
          severity: warning
          component: orchestration
        annotations:
          summary: "High workflow failure rate"
          description: "Workflow {{ $labels.workflow_type }} success rate is {{ $value | humanizePercentage }}"
          runbook_url: "https://docs.project-ai.com/runbooks/workflow-failures"
      
      # AI model inference slow
      - alert: SlowAIInference
        expr: project_ai:ai_inference:duration:p95 > 30
        for: 10m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "Slow AI inference for {{ $labels.model }}"
          description: "P95 inference time is {{ $value }}s"
          runbook_url: "https://docs.project-ai.com/runbooks/slow-inference"

  # Informational alerts
  - name: project_ai_info
    interval: 5m
    rules:
      # Certificate expiry
      - alert: CertificateExpiringSoon
        expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 30
        for: 1h
        labels:
          severity: info
          component: security
        annotations:
          summary: "TLS certificate expiring soon"
          description: "Certificate for {{ $labels.instance }} expires in {{ $value }} days"
          runbook_url: "https://docs.project-ai.com/runbooks/cert-renewal"
      
      # Version mismatch
      - alert: VersionMismatch
        expr: count(count by (version) (project_ai_version_info)) > 1
        for: 30m
        labels:
          severity: info
          component: deployment
        annotations:
          summary: "Multiple application versions detected"
          description: "{{ $value }} different versions are running"
          runbook_url: "https://docs.project-ai.com/runbooks/version-mismatch"
```

## SLA Rules

```yaml
# /etc/prometheus/rules/sla_rules.yml
groups:
  - name: project_ai_sla
    interval: 5m
    rules:
      # Availability SLA (99.9% uptime)
      - record: project_ai:sla:availability:30d
        expr: |
          (
            sum(up{job="project-ai-app"} == 1)
            /
            count(up{job="project-ai-app"})
          ) * 100
      
      # Performance SLA (95% requests < 1s)
      - record: project_ai:sla:performance:30d
        expr: |
          (
            sum(rate(project_ai_request_duration_seconds_bucket{le="1.0"}[30d]))
            /
            sum(rate(project_ai_request_duration_seconds_count[30d]))
          ) * 100
      
      # Error budget (0.1% error rate allowed)
      - record: project_ai:sla:error_budget:30d
        expr: |
          (
            0.001 - project_ai:requests:error_rate5m / 100
          ) * 100
      
      # SLA violations
      - alert: SLAViolation
        expr: project_ai:sla:availability:30d < 99.9
        for: 5m
        labels:
          severity: critical
          component: sla
        annotations:
          summary: "SLA availability violation"
          description: "Availability is {{ $value | humanizePercentage }}, below 99.9% target"
          runbook_url: "https://docs.project-ai.com/runbooks/sla-violation"
```

## Integration with Application

```python
# src/app/monitoring/prometheus_exporter.py
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from flask import Response
import time
import functools

# Metric definitions
REQUEST_COUNT = Counter(
    'project_ai_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'project_ai_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

ACTIVE_USERS = Gauge(
    'project_ai_active_users',
    'Number of active users',
    ['instance']
)

AI_INFERENCE_DURATION = Histogram(
    'project_ai_ai_inference_duration_seconds',
    'AI model inference duration',
    ['model', 'backend'],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

AI_INFERENCE_COUNT = Counter(
    'project_ai_ai_inference_total',
    'Total AI inference count',
    ['model', 'backend', 'status']
)

IMAGE_GENERATION_COUNT = Counter(
    'project_ai_image_generation_total',
    'Total image generation count',
    ['backend', 'style', 'status']
)

CHAT_MESSAGES = Counter(
    'project_ai_chat_messages_total',
    'Total chat messages',
    ['persona', 'direction']
)

VERSION_INFO = Info(
    'project_ai_version',
    'Application version information'
)

# Initialize version info
VERSION_INFO.info({
    'version': '1.0.0',
    'python_version': '3.11',
    'build_date': '2024-02-08'
})

def track_request_metrics(f):
    """Decorator to track request metrics"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        method = request.method
        endpoint = request.endpoint or 'unknown'
        
        start_time = time.time()
        try:
            response = f(*args, **kwargs)
            status = response.status_code if hasattr(response, 'status_code') else 200
            return response
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    return wrapper

def track_ai_inference(model, backend):
    """Decorator to track AI inference metrics"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            try:
                result = f(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                AI_INFERENCE_DURATION.labels(model=model, backend=backend).observe(duration)
                AI_INFERENCE_COUNT.labels(model=model, backend=backend, status=status).inc()
        return wrapper
    return decorator

# Metrics endpoint
def metrics_endpoint():
    """Flask endpoint for Prometheus metrics"""
    return Response(generate_latest(), mimetype='text/plain')
```

## Testing Configuration

```bash
# Validate Prometheus configuration
promtool check config /etc/prometheus/prometheus.yml

# Check recording rules
promtool check rules /etc/prometheus/rules/recording_rules.yml

# Check alerting rules
promtool check rules /etc/prometheus/rules/alerting_rules.yml

# Test alert evaluation
promtool test rules /etc/prometheus/rules/test_rules.yml

# Query Prometheus API
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="project-ai-app"}'

# Reload configuration (without restart)
curl -X POST http://localhost:9090/-/reload
```

## Performance Tuning

```yaml
# High-performance configuration
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s

# Storage optimization
storage:
  tsdb:
    path: /prometheus
    retention.time: 15d
    retention.size: 50GB
    wal-compression: true
    
# Query performance
query:
  max_concurrency: 20
  timeout: 2m
  lookback_delta: 5m
  max_samples: 50000000
```
