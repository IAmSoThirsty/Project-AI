# 07: Health Checks and Monitoring Hooks

**Document**: Health Check Systems and Monitoring Integration  
**System**: Docker HEALTHCHECK, Kubernetes Probes, Prometheus, Alerting  
**Related Systems**: Docker, Kubernetes, Rollback Procedures

---


## Navigation

**Location**: `relationships\deployment\07_health_monitoring_hooks.md`

**Parent**: [[relationships\deployment\README.md]]


## Health Check Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              HEALTH CHECK & MONITORING SYSTEM                 │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Application Level                                            │
│  ┌────────────────────────────────────────────┐              │
│  │  /health Endpoint                          │              │
│  │  • Database connectivity                   │              │
│  │  • External API status                     │              │
│  │  • Cache availability (Redis)              │              │
│  │  • Disk space check                        │              │
│  └──────────────┬─────────────────────────────┘              │
│                 │                                             │
│                 ↓                                             │
│  ┌────────────────────────────────────────────┐              │
│  │  Docker HEALTHCHECK                        │              │
│  │  • Interval: 30s                           │              │
│  │  • Timeout: 10s                            │              │
│  │  • Retries: 3                              │              │
│  │  • Start Period: 5s                        │              │
│  └──────────────┬─────────────────────────────┘              │
│                 │                                             │
│                 ↓                                             │
│  ┌────────────────────────────────────────────┐              │
│  │  Kubernetes Probes                         │              │
│  │  ┌──────────────────────────────┐          │              │
│  │  │  Liveness Probe              │          │              │
│  │  │  • Checks: Container alive   │          │              │
│  │  │  • Action: Restart if fail   │          │              │
│  │  └──────────────────────────────┘          │              │
│  │  ┌──────────────────────────────┐          │              │
│  │  │  Readiness Probe             │          │              │
│  │  │  • Checks: Ready for traffic │          │              │
│  │  │  • Action: Remove from LB    │          │              │
│  │  └──────────────────────────────┘          │              │
│  │  ┌──────────────────────────────┐          │              │
│  │  │  Startup Probe               │          │              │
│  │  │  • Checks: Initial startup   │          │              │
│  │  │  • Action: Wait before other │          │              │
│  │  └──────────────────────────────┘          │              │
│  └──────────────┬─────────────────────────────┘              │
│                 │                                             │
│                 ↓                                             │
│  ┌────────────────────────────────────────────┐              │
│  │  Prometheus Metrics                        │              │
│  │  • /metrics endpoint                       │              │
│  │  • Custom business metrics                 │              │
│  │  • Resource metrics (CPU, memory)          │              │
│  └──────────────┬─────────────────────────────┘              │
│                 │                                             │
│                 ↓                                             │
│  ┌────────────────────────────────────────────┐              │
│  │  Grafana Dashboards                        │              │
│  │  • Real-time health visualization          │              │
│  │  • Historical trend analysis               │              │
│  └──────────────┬─────────────────────────────┘              │
│                 │                                             │
│                 ↓                                             │
│  ┌────────────────────────────────────────────┐              │
│  │  AlertManager                              │              │
│  │  • Alert on health failures                │              │
│  │  • Route to PagerDuty/Slack                │              │
│  └────────────────────────────────────────────┘              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Health Check Levels

### Level 1: Basic Health (Shallow)
```python
# src/app/main.py or web/backend/app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    """Basic health check - returns 200 if app is running."""
    return jsonify({"status": "healthy"}), 200
```

### Level 2: Deep Health (Component Check)
```python
# scripts/healthcheck.py
import requests
import sys

def check_api_health():
    """Check if API is healthy."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"API Online - {data.get('status', 'unknown')}"
        return False, f"API returned {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "API not reachable"
    except Exception as e:
        return False, f"API error: {str(e)}"

def check_database():
    """Check database connectivity."""
    try:
        # PostgreSQL connection test
        import psycopg2
        conn = psycopg2.connect("dbname=projectai user=postgres")
        conn.close()
        return True, "Database connected"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def check_redis():
    """Check Redis cache availability."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        return True, "Redis available"
    except Exception as e:
        return False, f"Redis error: {str(e)}"

def main():
    checks = [
        ("API Health", check_api_health),
        ("Database", check_database),
        ("Redis Cache", check_redis),
    ]
    
    results = []
    for name, check_func in checks:
        success, message = check_func()
        print(f"{'✅' if success else '❌'} {name}: {message}")
        results.append(success)
    
    if all(results):
        print("All systems operational!")
        return 0
    else:
        print("Some systems are not operational")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Docker Health Check

### Dockerfile HEALTHCHECK
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Application setup...
COPY src/ /app/src/
COPY scripts/healthcheck.py /app/healthcheck.py

# Health check configuration
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=5s \
            --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# Default command
CMD ["python", "-m", "app.main"]
```

### Health Check Status Flow
```
Container Starts
    ↓ waits
Start Period: 5s (allows initialization)
    ↓ then every 30s
Execute: python healthcheck.py
    ├─→ Exit 0 (healthy)
    │   ↓ status
    │   Container: healthy
    │   ↓ action
    │   None (continue)
    │
    └─→ Exit 1 (unhealthy)
        ↓ retry (max 3 times)
        Still failing?
        ↓ status
        Container: unhealthy
        ↓ triggers
        Restart Policy (if configured)
            restart: unless-stopped
            ↓ action
            Container Restart
```

## Kubernetes Probes

### Liveness Probe
```yaml
# Deployment manifest
spec:
  containers:
  - name: backend
    image: projectai/backend:latest
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 30
      timeoutSeconds: 5
      successThreshold: 1
      failureThreshold: 3
```

### Readiness Probe
```yaml
spec:
  containers:
  - name: backend
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
```

### Startup Probe (for slow-starting apps)
```yaml
spec:
  containers:
  - name: backend
    startupProbe:
      httpGet:
        path: /health/startup
        port: 8000
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 30  # 30 * 5s = 150s max startup time
```

### Probe Decision Flow
```
Pod Created
    ↓ starts container
Container Running
    ↓ waits
initialDelaySeconds: 10s
    ↓ executes
Startup Probe (if defined)
    ├─→ Pass
    │   ↓ enables
    │   Liveness & Readiness Probes
    │
    └─→ Fail (after 30 attempts)
        ↓ action
        Restart Container

Liveness Probe (every 30s)
    ├─→ Pass
    │   ↓ status
    │   Container: Running
    │
    └─→ Fail (3 consecutive)
        ↓ action
        Restart Container
        ↓ increments
        Restart Count
        ↓ backoff
        CrashLoopBackOff (if frequent)

Readiness Probe (every 10s)
    ├─→ Pass
    │   ↓ status
    │   Pod: Ready
    │   ↓ action
    │   Add to Service Endpoints
    │   ↓ receives
    │   Traffic
    │
    └─→ Fail (3 consecutive)
        ↓ status
        Pod: Not Ready
        ↓ action
        Remove from Service Endpoints
        ↓ no traffic
        But Container Keeps Running
```

## E2E Health Check Orchestration

### Health Checker Class
```python
# e2e/orchestration/health_checks.py
class HealthChecker:
    def check_service_health(
        self,
        service: ServiceConfig,
        timeout: float = 5.0,
    ) -> tuple[bool, str]:
        """Check health of a single service."""
        if not service.enabled:
            return True, "Service is disabled"
        
        try:
            response = requests.get(service.health_url, timeout=timeout)
            if response.status_code == 200:
                return True, "Service is healthy"
            else:
                return False, f"Health check failed with status {response.status_code}"
        except requests.RequestException as e:
            return False, f"Health check failed: {e}"
    
    def wait_for_all_services_healthy(
        self,
        timeout: float = 120.0,
        check_interval: float = 1.0,
    ) -> bool:
        """Wait for all enabled services to become healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            results = self.check_all_services_health()
            all_healthy = all(is_healthy for is_healthy, _ in results.values())
            
            if all_healthy:
                return True
            
            time.sleep(check_interval)
        
        return False
```

## Prometheus Metrics

### Metrics Export
```python
# src/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# Export endpoint
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
```

### Prometheus Scrape Config
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'project-ai'
    static_configs:
      - targets: ['project-ai:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
```

## Grafana Dashboards

### Dashboard JSON Structure
```json
{
  "dashboard": {
    "title": "Project-AI Health Dashboard",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Request Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "active_users"
          }
        ]
      }
    ]
  }
}
```

## AlertManager Configuration

### Alert Rules
```yaml
# alert-rules.yml
groups:
  - name: project-ai-alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} per second"
      
      - alert: ServiceDown
        expr: up{job="project-ai"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Project-AI service has been down for more than 1 minute"
      
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{container="backend"} / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"
```

### AlertManager Routing
```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@projectai.com'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<pagerduty_key>'
  
  - name: 'slack'
    slack_configs:
      - api_url: '<slack_webhook>'
        channel: '#alerts'
```

## Related Systems

- `02_docker_relationships.md` - Docker HEALTHCHECK
- `03_kubernetes_orchestration.md` - K8s probes
- `08_rollback_procedures.md` - Health-triggered rollback

---

**Status**: ✅ Complete  
**Coverage**: Health checks, monitoring hooks, Prometheus, Grafana, alerting
