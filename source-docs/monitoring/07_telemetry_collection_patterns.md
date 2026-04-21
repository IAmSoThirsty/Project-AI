# Telemetry Collection Patterns

**Component:** Telemetry & Instrumentation  
**Type:** Engineering Guide  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This guide covers telemetry collection patterns, instrumentation techniques, sampling strategies, and data pipeline design for Project-AI observability. Learn how to instrument code for maximum visibility with minimal performance impact.

---

## Telemetry Architecture

### Collection Pipeline

```
┌───────────────────────────────────────────────────────┐
│                Application Code                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ AI Core  │  │ Security │  │ Plugins  │           │
│  │ Systems  │  │ Agents   │  │          │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │              │                  │
│       └─────────────┴──────────────┘                  │
│                     │                                  │
└─────────────────────┼────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  Metrics Collector Layer     │
        │  - Counter increments        │
        │  - Gauge updates             │
        │  - Histogram observations    │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  Prometheus Exporter         │
        │  - Registry management       │
        │  - HTTP scrape endpoint      │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  Prometheus Server           │
        │  - Time-series storage       │
        │  - Query engine (PromQL)     │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │  Visualization (Grafana)     │
        │  - Dashboards                │
        │  - Alerts                    │
        └──────────────────────────────┘
```

---

## Instrumentation Patterns

### 1. Counter Instrumentation

**Use Case:** Count discrete events (requests, errors, validations)

**Pattern:**
```python
from app.monitoring.metrics_collector import collector

class AIPersona:
    def handle_chat_message(self, message):
        # Increment counter
        collector.update_persona_interaction("chat")
        
        # Process message
        response = self._generate_response(message)
        
        return response
```

**Best Practices:**
- ✅ Increment counters **after** successful operation
- ✅ Use labels sparingly (low cardinality)
- ✅ Use descriptive label values
- ❌ Don't use user IDs, request IDs as labels (too many unique values)

**Example with Error Handling:**
```python
def execute_plugin(plugin_name, args):
    try:
        result = plugin.run(args)
        
        # Record success
        collector.record_plugin_execution(
            plugin_name=plugin_name,
            status="success"
        )
        
        return result
    
    except Exception as e:
        # Record failure with error type
        collector.record_plugin_execution(
            plugin_name=plugin_name,
            status="error",
            error_type=type(e).__name__
        )
        
        raise
```

---

### 2. Gauge Instrumentation

**Use Case:** Measure current state (active users, queue depth, resource usage)

**Pattern:**
```python
class MemorySystem:
    def update_knowledge_base(self, category, entries):
        self.knowledge[category] = entries
        
        # Update gauge
        collector.set_knowledge_entries(
            category=category,
            count=len(entries)
        )
```

**Periodic Gauges:**
```python
import threading
import time

def update_gauges_periodically(interval_seconds=15):
    """Background thread to update gauges."""
    
    while True:
        # Collect current state
        collector.collect_all_metrics()
        
        # Sleep until next update
        time.sleep(interval_seconds)

# Start background thread
gauge_thread = threading.Thread(
    target=update_gauges_periodically,
    daemon=True
)
gauge_thread.start()
```

---

### 3. Histogram Instrumentation

**Use Case:** Measure distribution of values (latency, duration, size)

**Pattern with Context Manager:**
```python
import time
from contextlib import contextmanager

@contextmanager
def timed_operation(operation_name):
    """Context manager for timing operations."""
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        
        # Record duration
        collector.record_operation_duration(
            operation=operation_name,
            duration_seconds=duration
        )

# Usage
with timed_operation("memory_query"):
    results = memory_system.search(query)
```

**Pattern with Decorator:**
```python
from functools import wraps

def measure_latency(operation_name):
    """Decorator to measure function latency."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record latency
                duration = time.time() - start_time
                collector.record_memory_query(
                    query_type=operation_name,
                    status="success",
                    duration_seconds=duration
                )
                
                return result
            
            except Exception as e:
                # Record error
                duration = time.time() - start_time
                collector.record_memory_query(
                    query_type=operation_name,
                    status="error",
                    duration_seconds=duration
                )
                
                raise
        
        return wrapper
    return decorator

# Usage
@measure_latency("search")
def search_knowledge(query):
    return memory_system.search(query)
```

---

### 4. Rate Calculation Pattern

**Use Case:** Measure events per time unit (requests/sec, errors/sec)

**Implementation:**
```python
# Counters automatically support rate calculation in Prometheus
# Just increment the counter; rate is calculated at query time

collector.update_persona_interaction("chat")
# PromQL: rate(project_ai_persona_interactions_total[5m])
```

---

## Sampling Strategies

### 1. Always Sample (Low Volume)

**Use Case:** Security events, Four Laws validations, critical operations

```python
# Always record Four Laws validations
def validate_action(action, context):
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    # ALWAYS record (no sampling)
    collector.record_four_laws_validation(
        is_allowed=is_allowed,
        law_violated=reason if not is_allowed else None
    )
    
    return is_allowed, reason
```

---

### 2. Head-Based Sampling (High Volume)

**Use Case:** Reduce storage for high-frequency events

```python
import random

SAMPLE_RATE = 0.1  # Sample 10% of events

def record_api_request(method, endpoint, status, duration):
    # Sample only 10% of requests
    if random.random() < SAMPLE_RATE:
        collector.record_api_request(
            method=method,
            endpoint=endpoint,
            status=status,
            duration_seconds=duration
        )
```

**Considerations:**
- Adjust sample rate based on volume
- Ensure representative sampling
- Document sample rate in metrics metadata

---

### 3. Tail-Based Sampling (Errors Only)

**Use Case:** Always sample errors, occasionally sample successes

```python
def record_operation(operation, status, duration):
    # Always record errors
    if status == "error":
        collector.record_operation(operation, status, duration)
    
    # Sample 1% of successes
    elif random.random() < 0.01:
        collector.record_operation(operation, status, duration)
```

---

### 4. Adaptive Sampling

**Use Case:** Dynamically adjust sampling based on load

```python
class AdaptiveSampler:
    def __init__(self, target_rate=100):
        self.target_rate = target_rate  # Events per second
        self.current_rate = 0
        self.sample_probability = 1.0
    
    def should_sample(self):
        """Adjust sampling to maintain target rate."""
        
        # If current rate exceeds target, reduce sampling
        if self.current_rate > self.target_rate:
            self.sample_probability = self.target_rate / self.current_rate
        else:
            self.sample_probability = 1.0
        
        return random.random() < self.sample_probability
    
    def record_event(self):
        self.current_rate += 1

# Usage
sampler = AdaptiveSampler(target_rate=100)

def record_chat_message(message):
    if sampler.should_sample():
        collector.update_persona_interaction("chat")
    
    sampler.record_event()
```

---

## Instrumentation Best Practices

### 1. Minimize Performance Impact

**✅ Good:**
```python
# Fast: No string formatting unless logged
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Complex state: %s", json.dumps(state, indent=2))

# Fast: Lazy evaluation
logger.debug("State: %s", lambda: expensive_computation())
```

**❌ Bad:**
```python
# Slow: Always formats string even if not logged
logger.debug(f"Complex state: {json.dumps(state, indent=2)}")

# Slow: Always computes even if not logged
logger.debug("Result: %s", expensive_computation())
```

---

### 2. Use Consistent Label Names

**✅ Good:**
```python
# Consistent naming across metrics
collector.record_plugin_execution(plugin_name="osint", status="success")
collector.record_memory_query(query_type="search", status="success")
```

**❌ Bad:**
```python
# Inconsistent: plugin_name vs plugin_id
collector.record_plugin_execution(plugin_name="osint", status="success")
collector.record_plugin_execution(plugin_id="osint", result="ok")
```

---

### 3. Aggregate Early

**✅ Good:**
```python
# Aggregate before storing
category_counts = {}
for entry in knowledge_base:
    category = entry["category"]
    category_counts[category] = category_counts.get(category, 0) + 1

for category, count in category_counts.items():
    collector.set_knowledge_entries(category=category, count=count)
```

**❌ Bad:**
```python
# Store individual entries (high cardinality)
for entry in knowledge_base:
    collector.set_knowledge_entry(
        entry_id=entry["id"],  # UNIQUE ID - BAD!
        category=entry["category"]
    )
```

---

### 4. Handle Errors Gracefully

**✅ Good:**
```python
def collect_metrics():
    try:
        # Collect metrics
        metrics = get_current_metrics()
        exporter.update(metrics)
    
    except Exception as e:
        # Log error but don't crash application
        logger.error("Failed to collect metrics: %s", e)
```

**❌ Bad:**
```python
def collect_metrics():
    # Crashes application if metrics collection fails
    metrics = get_current_metrics()
    exporter.update(metrics)
```

---

## Advanced Patterns

### 1. Multi-Dimensional Metrics

**Pattern:**
```python
# Track latency by both operation AND status
@measure_latency
def execute_operation(operation_type, data):
    try:
        result = perform_operation(data)
        
        # Record successful execution
        collector.record_operation_execution(
            operation=operation_type,
            status="success",
            result_size=len(result)
        )
        
        return result
    
    except Exception as e:
        # Record failed execution
        collector.record_operation_execution(
            operation=operation_type,
            status="error",
            error_type=type(e).__name__
        )
        
        raise
```

**Query:**
```promql
# Latency by operation and status
sum by (operation, status) (
  rate(operation_duration_seconds_sum[5m])
) / 
sum by (operation, status) (
  rate(operation_duration_seconds_count[5m])
)
```

---

### 2. Composite Metrics

**Pattern:**
```python
class CompositeMetric:
    """Combine multiple metrics into single view."""
    
    def get_system_health_score(self):
        """Calculate health score (0-100)."""
        
        # Weighted combination of metrics
        weights = {
            "attack_success_rate": -50,  # Negative impact
            "validation_success_rate": 30,
            "query_success_rate": 20
        }
        
        score = 100
        
        # Attack success (lower is better)
        attack_rate = collector.get_attack_success_rate()["success_rate"]
        score += weights["attack_success_rate"] * attack_rate
        
        # Validation success (higher is better)
        validation_rate = collector.get_validation_success_rate()
        score += weights["validation_success_rate"] * validation_rate
        
        # Query success (higher is better)
        query_rate = collector.get_query_success_rate()
        score += weights["query_success_rate"] * query_rate
        
        return max(0, min(100, score))
```

---

### 3. Contextual Telemetry

**Pattern with Request Context:**
```python
from contextvars import ContextVar

request_context = ContextVar("request_context", default={})

class ContextualCollector:
    """Add request context to all metrics."""
    
    def record_event(self, event_type):
        # Get current request context
        context = request_context.get()
        
        # Record with context
        collector.record_event(
            event_type=event_type,
            user=context.get("user", "unknown"),
            session=context.get("session", "unknown")
        )

# Usage in request handler
def handle_request(request):
    request_context.set({
        "user": request.user,
        "session": request.session_id
    })
    
    # All metrics in this request include context
    collector.record_event("request_received")
```

---

## Data Retention & Downsampling

### Prometheus Retention Policy

**Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

storage:
  tsdb:
    retention.time: 15d  # Keep data for 15 days
    retention.size: 10GB  # Or until 10GB storage used
```

### Recording Rules (Downsampling)

**Purpose:** Pre-compute expensive queries for long-term storage

**Configuration:**
```yaml
# prometheus_rules.yml
groups:
  - name: aggregation_rules
    interval: 1m
    rules:
      # Record 5-minute average latency
      - record: project_ai:api_latency_5m
        expr: |
          histogram_quantile(0.95,
            rate(project_ai_api_request_duration_seconds_bucket[5m])
          )
      
      # Record hourly attack success rate
      - record: project_ai:attack_success_rate_1h
        expr: |
          sum(rate(project_ai_cerberus_blocks_total{attack_type="bypass"}[1h])) /
          sum(rate(project_ai_cerberus_blocks_total[1h]))
```

---

## Testing Instrumentation

### Unit Tests

```python
import pytest
from app.monitoring.metrics_collector import MetricsCollector

@pytest.fixture
def collector(tmp_path):
    return MetricsCollector(data_dir=str(tmp_path))

def test_counter_increment(collector):
    """Test counter increments correctly."""
    
    # Record event
    collector.update_persona_interaction("chat")
    collector.update_persona_interaction("chat")
    
    # Verify counter
    assert collector.get_interaction_count("chat") == 2

def test_gauge_update(collector):
    """Test gauge updates correctly."""
    
    # Update gauge
    collector.set_plugin_count(5)
    
    # Verify value
    assert collector.get_plugin_count() == 5

def test_histogram_observation(collector):
    """Test histogram records values."""
    
    # Record latencies
    for latency in [0.1, 0.2, 0.3, 0.5, 1.0]:
        collector.record_memory_query(
            query_type="search",
            status="success",
            duration_seconds=latency
        )
    
    # Verify percentiles
    stats = collector.get_latency_stats("search")
    assert stats["p50_ms"] == 300  # Median = 0.3s
```

### Integration Tests

```python
def test_end_to_end_metrics():
    """Test metrics flow from instrumentation to Prometheus."""
    
    # 1. Start metrics server
    from app.monitoring.metrics_server import MetricsServer
    server = MetricsServer(port=8001)
    server.start()
    
    # 2. Generate events
    for _ in range(10):
        collector.update_persona_interaction("chat")
    
    # 3. Scrape metrics
    import requests
    response = requests.get("http://localhost:8001/metrics")
    
    # 4. Verify metrics
    assert "project_ai_persona_interactions_total" in response.text
    assert 'interaction_type="chat"' in response.text
    
    # 5. Cleanup
    server.stop()
```

---

## Performance Considerations

### Metric Cardinality

**Problem:** Too many unique label combinations → High memory usage

**Bad Example:**
```python
# DON'T: User ID has millions of unique values
collector.record_api_request(
    user_id="user_12345",  # BAD: High cardinality
    endpoint="/api/chat"
)
```

**Good Example:**
```python
# DO: Use categories instead
collector.record_api_request(
    user_type="premium",  # GOOD: Low cardinality (free, premium, enterprise)
    endpoint="/api/chat"
)
```

**Cardinality Limits:**
- **Ideal:** <100 unique label combinations per metric
- **Warning:** 100-1000 combinations
- **Critical:** >1000 combinations (review needed)

---

### Collection Overhead

**Benchmark:**
```python
import time

def benchmark_collection():
    iterations = 10000
    
    # Baseline
    start = time.time()
    for _ in range(iterations):
        pass
    baseline = time.time() - start
    
    # With metrics
    start = time.time()
    for _ in range(iterations):
        collector.update_persona_interaction("chat")
    with_metrics = time.time() - start
    
    overhead = (with_metrics - baseline) / iterations * 1000
    print(f"Overhead per call: {overhead:.3f}ms")

# Expected: <0.1ms per call
```

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
- [Observability Best Practices](08_observability_best_practices.md)
- [Metrics Integration Guide](10_metrics_integration_guide.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/monitoring/`
