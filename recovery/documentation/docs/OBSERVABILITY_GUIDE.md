# Observability Guide

**Sovereign Governance Substrate - Best Practices & Patterns**

**Version**: 1.0  
**Date**: 2026-03-03  
**Audience**: Developers, SREs, Operations  
**Status**: Active

---

## Table of Contents

1. [Introduction](#introduction)
2. [The Three Pillars of Observability](#the-three-pillars-of-observability)
3. [Metrics Best Practices](#metrics-best-practices)
4. [Logging Best Practices](#logging-best-practices)
5. [Distributed Tracing](#distributed-tracing)
6. [Instrumentation Patterns](#instrumentation-patterns)
7. [Dashboard Design](#dashboard-design)
8. [Alerting Philosophy](#alerting-philosophy)
9. [Incident Response](#incident-response)
10. [Cost Optimization](#cost-optimization)
11. [Troubleshooting Playbooks](#troubleshooting-playbooks)

---

## Introduction

### What is Observability?

**Observability** is the ability to understand the internal state of a system by examining its outputs. In software systems, this means:

- **Understanding** what your system is doing
- **Debugging** when things go wrong
- **Optimizing** performance and costs
- **Predicting** future behavior

### Observability vs Monitoring

| Monitoring | Observability |
|------------|---------------|
| "Is it working?" | "Why is it not working?" |
| Known unknowns | Unknown unknowns |
| Predefined dashboards | Ad-hoc exploration |
| Alert on symptoms | Investigate root causes |

### Why Observability Matters

1. **Faster MTTR** (Mean Time To Recovery)
2. **Proactive problem detection**
3. **Better user experience**
4. **Informed architectural decisions**
5. **Cost optimization**
6. **Compliance and audit trails**

---

## The Three Pillars of Observability

### 1. Metrics (What is happening?)

**Characteristics**:

- Numerical measurements over time
- Cheap to collect and store
- Aggregatable and queryable
- Foundation for alerting

**Use Cases**:

- Resource utilization (CPU, memory)
- Application performance (latency, throughput)
- Business KPIs (requests/sec, error rates)
- SLO/SLA tracking

**Tools**: Prometheus, Grafana

---

### 2. Logs (What happened?)

**Characteristics**:

- Timestamped event records
- Rich contextual information
- Expensive to store at scale
- Great for debugging

**Use Cases**:

- Error investigation
- Audit trails
- Security forensics
- User behavior analysis

**Tools**: Loki, ELK Stack, Splunk

---

### 3. Traces (How did it happen?)

**Characteristics**:

- Request flow across services
- End-to-end visibility
- Expensive to collect
- Critical for microservices

**Use Cases**:

- Distributed system debugging
- Performance bottleneck identification
- Service dependency mapping
- Latency attribution

**Tools**: Jaeger, Tempo, OpenTelemetry

---

### The Golden Signals

**For every service, monitor**:

1. **Latency** - How long do requests take?
2. **Traffic** - How much demand is there?
3. **Errors** - What is failing?
4. **Saturation** - How full is the service?

---

## Metrics Best Practices

### Naming Conventions

**Format**: `<namespace>_<subsystem>_<metric_name>_<unit>`

**Examples**:
```
project_ai_api_requests_total          # Counter
project_ai_api_request_duration_seconds # Histogram
project_ai_memory_usage_bytes          # Gauge
```

**Rules**:

- Use snake_case
- Include units (seconds, bytes, ratio)
- Be descriptive but concise
- Namespace by application

---

### Metric Types

#### 1. Counter (Monotonically Increasing)

**Use For**: Events that only increase

- Total requests
- Total errors
- Items processed

**Example**:
```python
from prometheus_client import Counter

api_requests = Counter(
    'project_ai_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_requests.labels(method='GET', endpoint='/users', status='200').inc()
```

**Prometheus Query**:
```prometheus
rate(project_ai_api_requests_total[5m])  # Requests per second
increase(project_ai_api_requests_total[1h])  # Total in last hour
```

---

#### 2. Gauge (Can Go Up or Down)

**Use For**: Current state measurements

- Memory usage
- Active connections
- Queue length
- Temperature

**Example**:
```python
from prometheus_client import Gauge

active_connections = Gauge(
    'project_ai_active_connections',
    'Number of active database connections',
    ['database']
)

active_connections.labels(database='postgres').set(42)
```

**Prometheus Query**:
```prometheus
project_ai_active_connections{database="postgres"}  # Current value
avg_over_time(project_ai_active_connections[1h])   # Average over time
```

---

#### 3. Histogram (Distribution of Values)

**Use For**: Latencies, sizes, durations

- Request duration
- Response size
- Query time

**Example**:
```python
from prometheus_client import Histogram

request_duration = Histogram(
    'project_ai_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

with request_duration.labels(method='GET', endpoint='/users').time():

    # Process request

    pass
```

**Prometheus Query**:
```prometheus

# 95th percentile

histogram_quantile(0.95, 
  rate(project_ai_api_request_duration_seconds_bucket[5m])
)

# Average

rate(project_ai_api_request_duration_seconds_sum[5m]) / 
rate(project_ai_api_request_duration_seconds_count[5m])
```

---

#### 4. Summary (Pre-calculated Quantiles)

**Use For**: Client-side quantiles

- Similar to Histogram but calculated client-side
- Less flexible, cheaper on server

**Example**:
```python
from prometheus_client import Summary

latency = Summary(
    'project_ai_processing_latency_seconds',
    'Processing latency',
    ['operation']
)

with latency.labels(operation='inference').time():

    # AI processing

    pass
```

---

### Label Best Practices

**DO**:

- ✅ Use labels for dimensions you'll query on
- ✅ Keep cardinality low (<100 values per label)
- ✅ Use consistent label names across metrics
- ✅ Include labels like `component`, `service`, `environment`

**DON'T**:

- ❌ Use user IDs, timestamps, or unbounded values as labels
- ❌ Have labels with >1000 unique values
- ❌ Use labels for data that should be in metric name
- ❌ Mix units in same metric (seconds vs milliseconds)

**Example**:
```python

# ✅ GOOD

api_requests.labels(method='POST', endpoint='/users', status='201')

# ❌ BAD (user_id is unbounded)

api_requests.labels(user_id='12345', endpoint='/users')

# ❌ BAD (timestamp shouldn't be a label)

api_requests.labels(timestamp='2026-03-03T14:30:00Z')
```

---

### Cardinality Management

**Problem**: High cardinality = memory explosion

**Example**:
```
10 methods × 100 endpoints × 10 status codes = 10,000 time series
Add user_id with 1M users = 10 BILLION time series ❌
```

**Solutions**:

1. **Aggregate** high-cardinality labels
2. **Drop** unnecessary labels
3. **Relabel** to reduce cardinality
4. **Use logs** for high-cardinality data

**Prometheus Relabeling**:
```yaml
relabel_configs:

  # Drop metrics with certain labels

  - source_labels: [__name__]
    regex: 'expensive_metric.*'
    action: drop

  # Aggregate status codes (200-299 → 2xx)

  - source_labels: [status]
    regex: '2..'
    replacement: '2xx'
    target_label: status

```

---

## Logging Best Practices

### Structured Logging

**Traditional (Unstructured)**:
```
2026-03-03 14:30:00 ERROR Failed to process user 12345 request
```

**Structured (JSON)**:
```json
{
  "timestamp": "2026-03-03T14:30:00Z",
  "level": "ERROR",
  "message": "Failed to process request",
  "user_id": 12345,
  "request_id": "abc123",
  "endpoint": "/users",
  "error": "Database connection timeout",
  "duration_ms": 5000
}
```

**Benefits**:

- ✅ Machine-parsable
- ✅ Searchable by field
- ✅ Consistent structure
- ✅ Easier correlation

---

### Logging Levels

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Detailed diagnostic info | Function entry/exit, variable values |
| **INFO** | General informational | Request received, job completed |
| **WARNING** | Potential issues | Deprecated API used, high latency |
| **ERROR** | Errors that don't stop execution | Failed to send email, retry attempted |
| **CRITICAL** | Errors that stop execution | Database unreachable, service crash |

**Guidelines**:

- Production: INFO and above
- Development: DEBUG and above
- Never log in hot paths (tight loops)

---

### What to Log

**DO Log**:

- ✅ Request/response (excluding PII)
- ✅ State changes
- ✅ Errors and exceptions
- ✅ Security events
- ✅ Performance issues
- ✅ Business events

**DON'T Log**:

- ❌ Passwords, tokens, secrets
- ❌ Credit card numbers, SSNs
- ❌ Excessive debug in production
- ❌ Personal identifiable information (PII)

---

### Log Correlation

**Use Correlation IDs** to track requests across services:

```python
import logging
import uuid

# Generate correlation ID

correlation_id = str(uuid.uuid4())

# Log with correlation ID

logger.info("Processing request", extra={
    "correlation_id": correlation_id,
    "user_id": 12345,
    "endpoint": "/users"
})

# Pass to downstream services

headers = {"X-Correlation-ID": correlation_id}
requests.post(url, headers=headers)
```

**Benefits**:

- Trace single request across multiple services
- Correlate logs, metrics, and traces
- Easier debugging

---

### Log Retention

| Environment | Retention | Reason |
|-------------|-----------|--------|
| Production | 30-90 days | Debugging, compliance |
| Staging | 7-14 days | Testing, cost savings |
| Development | 1-3 days | Minimal retention |

**Compliance Considerations**:

- GDPR: Right to deletion
- SOC 2: Audit trail requirements
- PCI DSS: 1 year minimum for payment logs

---

## Distributed Tracing

### OpenTelemetry Instrumentation

**Install SDK**:
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger
```

**Initialize Tracer**:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracer

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

**Instrument Code**:
```python
@tracer.start_as_current_span("process_user_request")
def process_user_request(user_id):

    # Span automatically created

    span = trace.get_current_span()
    span.set_attribute("user_id", user_id)
    
    # Child span

    with tracer.start_as_current_span("fetch_user_data"):
        user = fetch_from_database(user_id)
    
    with tracer.start_as_current_span("validate_user"):
        validate(user)
    
    return user
```

---

### Trace Context Propagation

**HTTP Headers** (W3C Trace Context):
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: vendor1=value1,vendor2=value2
```

**FastAPI Middleware**:
```python
from fastapi import Request
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.middleware("http")
async def trace_middleware(request: Request, call_next):

    # Extract trace context from headers

    # Automatically handled by OpenTelemetry

    response = await call_next(request)
    return response
```

---

### Sampling Strategies

**1. Always On** (100% sampling):

- Development/debugging
- Low traffic services

**2. Probability-Based** (sample 1-10%):

- Production high-traffic services
- Cost-effective

**3. Tail-Based** (sample errors/slow requests):

- Keep all errors
- Keep requests > p95 latency
- Best of both worlds

**Configuration**:
```python
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

# Sample 10% of traces

sampler = ParentBasedTraceIdRatio(0.1)
```

---

## Instrumentation Patterns

### Instrumenting FastAPI

```python
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

app = FastAPI()

# Metrics

REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

### Instrumenting Database Queries

```python
from prometheus_client import Histogram

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table']
)

def query_with_metrics(operation, table, query_func):
    with DB_QUERY_DURATION.labels(operation=operation, table=table).time():
        return query_func()

# Usage

users = query_with_metrics('SELECT', 'users', lambda: session.query(User).all())
```

---

### Instrumenting Background Jobs

```python
from prometheus_client import Counter, Gauge

JOBS_TOTAL = Counter('background_jobs_total', 'Total jobs', ['job_type', 'status'])
JOBS_ACTIVE = Gauge('background_jobs_active', 'Active jobs', ['job_type'])

def run_background_job(job_type, job_func):
    JOBS_ACTIVE.labels(job_type=job_type).inc()
    
    try:
        result = job_func()
        JOBS_TOTAL.labels(job_type=job_type, status='success').inc()
        return result
    except Exception as e:
        JOBS_TOTAL.labels(job_type=job_type, status='failure').inc()
        raise
    finally:
        JOBS_ACTIVE.labels(job_type=job_type).dec()
```

---

## Dashboard Design

### Dashboard Hierarchy

**1. Overview Dashboard** (Executive View):

- System health at a glance
- Key SLO metrics
- Active alerts
- Business KPIs

**2. Service Dashboard** (Ops View):

- Per-service health
- Resource utilization
- Error rates
- Dependency status

**3. Detail Dashboard** (Engineering View):

- Detailed metrics
- Performance profiling
- Error analysis
- Debug information

---

### Dashboard Best Practices

**DO**:

- ✅ Start with the most important metrics (top-left)
- ✅ Use color coding (green=good, yellow=warning, red=critical)
- ✅ Include time range selector
- ✅ Add dashboard links for drill-down
- ✅ Document what each panel shows
- ✅ Keep it simple (max 12 panels per dashboard)

**DON'T**:

- ❌ Overcrowd with too many metrics
- ❌ Use default Grafana panel titles
- ❌ Forget to set appropriate thresholds
- ❌ Mix unrelated metrics in one panel

---

### Panel Selection Guide

| Data Type | Recommended Panel |
|-----------|-------------------|
| Single value | Stat, Gauge |
| Time series | Graph (timeseries) |
| Distribution | Heatmap |
| Multiple values | Table |
| Comparison | Bar chart |
| Status | Stat with thresholds |

---

## Alerting Philosophy

### Alert Fatigue Prevention

**Problem**: Too many alerts → Ignored alerts → Missed incidents

**Solution**: Alert on **symptoms**, not **causes**

**Example**:
```
❌ BAD: Alert on "High CPU usage"
✅ GOOD: Alert on "API latency > SLO" (CPU is a cause, latency is the symptom)
```

---

### Alert Actionability

**Every alert must**:

1. Be **actionable** (someone can fix it)
2. Require **human intervention**
3. Be about **user-impacting** problems
4. Include **context** in the description

**Alert Template**:
```yaml

- alert: APILatencyHigh
  expr: api:latency:p95 > 0.5
  for: 5m
  labels:
    severity: warning
    component: api
  annotations:
    summary: "API latency above SLO"
    description: "{{ $labels.endpoint }} p95 latency is {{ $value }}s (SLO: 200ms)"
    runbook: "https://wiki.company.com/runbooks/api-latency"

```

---

### Alert Severities

| Severity | Response Time | Example |
|----------|---------------|---------|
| **Critical** | Immediate (page on-call) | Service down, data loss |
| **High** | 30 minutes | Performance degradation |
| **Warning** | 4 hours | Resource exhaustion approaching |
| **Info** | Next business day | State changes, deployments |

---

## Incident Response

### On-Call Runbook Template

```markdown

# Runbook: High API Latency

## Symptoms

- API p95 latency > 500ms
- User complaints about slow response

## Impact

- Degraded user experience
- Potential SLO violation

## Triage Steps

1. Check Grafana: API Performance Dashboard
2. Identify slow endpoints
3. Check database query performance
4. Review recent deployments

## Resolution Steps

### Option 1: Database Issue

- Check slow query log
- Identify missing indexes
- Kill long-running queries if safe

### Option 2: High Traffic

- Scale up API servers
- Enable rate limiting
- Cache frequently accessed data

### Option 3: External Dependency

- Check third-party API status
- Enable circuit breakers
- Fail fast on timeouts

## Escalation

- If unresolved in 30 minutes, escalate to engineering lead
- If SLO breach imminent, page CTO

## Post-Incident

- File incident report
- Schedule postmortem
- Update runbook with learnings

```

---

## Cost Optimization

### Metrics Cost Optimization

**1. Reduce Cardinality**:
```prometheus

# Before: 1M time series

api_requests{user_id="12345", endpoint="/users"}

# After: 1K time series

api_requests{endpoint="/users"}
```
**Savings**: 99.9% reduction in storage

**2. Increase Scrape Interval**:
```yaml

# Before: 15s interval

scrape_interval: 15s

# After: 60s for non-critical metrics

scrape_interval: 60s
```
**Savings**: 75% reduction in data points

**3. Use Recording Rules**:
```yaml

# Pre-compute expensive queries

- record: api:error_rate:5m
  expr: rate(api_errors_total[5m]) / rate(api_requests_total[5m])

```
**Savings**: Faster queries, less CPU usage

**4. Retention Policies**:
```yaml

# Prometheus config

storage:
  tsdb:
    retention.time: 15d  # Keep only 15 days
```

---

### Log Cost Optimization

**1. Log Sampling**:
```python

# Log 10% of successful requests

if response.status_code == 200 and random.random() < 0.1:
    logger.info("Request successful")

# Always log errors

if response.status_code >= 400:
    logger.error("Request failed")
```

**2. Dynamic Log Levels**:
```python

# Increase log level in production

if os.getenv('ENVIRONMENT') == 'production':
    logging.setLevel(logging.INFO)
else:
    logging.setLevel(logging.DEBUG)
```

**3. Log Aggregation**:

- Use structured logs for easy querying
- Aggregate similar log lines
- Drop unnecessary fields

---

## Troubleshooting Playbooks

### Problem: High API Latency

**Symptoms**:

- Dashboard shows p95 latency > 500ms
- User complaints

**Investigation**:

1. Check API Performance Dashboard
2. Identify slow endpoints:
   ```prometheus
   topk(10, api:latency:p95)
   ```
3. Check database query performance:
   ```prometheus
   pg_stat_database_blks_read
   ```
4. Review recent changes (git log, deployment history)

**Resolution**:

- Add database indexes
- Optimize slow queries
- Scale API servers
- Enable caching

---

### Problem: Memory Leak

**Symptoms**:

- Memory usage continuously increasing
- OOM killer triggered

**Investigation**:

1. Check memory dashboard
2. Identify process with leak:
   ```prometheus
   container_memory_usage_bytes
   ```
3. Profile application (Python memory_profiler, Go pprof)
4. Review code for common patterns:
   - Unbounded caches
   - Circular references
   - Event listener leaks

**Resolution**:

- Fix leak in code
- Restart service (temporary)
- Add memory limits to prevent system-wide impact

---

### Problem: Disk Space Full

**Symptoms**:

- Disk usage > 90%
- Write failures

**Investigation**:

1. Check disk usage:
   ```bash
   df -h
   du -sh /* | sort -h
   ```
2. Find large files:
   ```bash
   find / -type f -size +1G
   ```
3. Check log rotation

**Resolution**:

- Delete old logs
- Compress infrequently accessed data
- Extend disk volume
- Set up log rotation

---

## Conclusion

Observability is not a destination but a **continuous practice**. 

**Key Takeaways**:

1. ✅ Instrument early and often
2. ✅ Start with the Golden Signals
3. ✅ Keep dashboards simple and actionable
4. ✅ Alert on symptoms, not causes
5. ✅ Use structured logging
6. ✅ Correlate logs, metrics, and traces
7. ✅ Optimize costs continuously
8. ✅ Document runbooks

**Next Steps**:

- Review your current instrumentation
- Identify gaps in observability
- Implement missing metrics/logs/traces
- Create/update dashboards
- Test incident response

---

**Questions?** Contact: Platform Engineering Team  
**Contributing**: Submit PRs to improve this guide  
**Feedback**: observability@company.com

**Version**: 1.0  
**Last Updated**: 2026-03-03
