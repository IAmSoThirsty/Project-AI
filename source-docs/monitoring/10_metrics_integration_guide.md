# Metrics Integration Guide

**Component:** Application Integration  
**Type:** Developer Guide  
**Owner:** Security Agents Team  
**Status:** Production  
**Last Updated:** 2026-04-20

---

## Overview

This guide provides step-by-step instructions for integrating monitoring and metrics into Project-AI components. Learn how to instrument new features, add custom metrics, and ensure observability compliance.

---

## Quick Start

### Adding Metrics to a New Feature

**5-Step Integration Process:**

```python
# 1. Import collector
from app.monitoring.metrics_collector import collector

# 2. Define your feature
class NewFeature:
    def execute(self, data):
        # 3. Record start
        start_time = time.time()
        
        try:
            # 4. Execute logic
            result = self._process(data)
            
            # 5. Record success metrics
            duration = time.time() - start_time
            collector.record_feature_execution(
                feature_name="new_feature",
                status="success",
                duration_seconds=duration
            )
            
            return result
        
        except Exception as e:
            # 5. Record failure metrics
            duration = time.time() - start_time
            collector.record_feature_execution(
                feature_name="new_feature",
                status="error",
                duration_seconds=duration,
                error_type=type(e).__name__
            )
            
            raise
```

---

## Integration Patterns by Component Type

### 1. AI System Integration

**Example: AI Persona**

```python
# src/app/core/ai_systems.py
import logging
from app.monitoring.metrics_collector import collector

logger = logging.getLogger(__name__)

class AIPersona:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.mood = {"energy": 0.5, "enthusiasm": 0.5}
        self.traits = {}
        
        # Initialize metrics on startup
        logger.info("Initializing AI Persona")
        self._load_state()
        self._report_initial_metrics()
    
    def _report_initial_metrics(self):
        """Report initial state metrics."""
        collector.collect_persona_metrics({
            "mood": self.mood,
            "traits": self.traits,
            "interaction_counts": {}
        })
    
    def update_mood(self, mood_changes):
        """Update mood and record metrics."""
        logger.debug("Updating mood: %s", mood_changes)
        
        # Update state
        self.mood.update(mood_changes)
        self._save_state()
        
        # Record metrics
        collector.collect_persona_metrics({
            "mood": self.mood,
            "traits": self.traits
        })
        
        logger.info("Mood updated: energy=%.2f, enthusiasm=%.2f",
                   self.mood["energy"], self.mood["enthusiasm"])
    
    def handle_interaction(self, interaction_type):
        """Handle user interaction."""
        # Record interaction
        collector.update_persona_interaction(interaction_type)
        
        logger.info("Interaction recorded: %s", interaction_type)
```

**Metrics Exposed:**
- `project_ai_persona_mood_energy`
- `project_ai_persona_mood_enthusiasm`
- `project_ai_persona_interactions_total{interaction_type}`

---

### 2. Security System Integration

**Example: Four Laws Validation**

```python
# src/app/core/ai_systems.py
from app.monitoring.metrics_collector import collector

class FourLaws:
    @staticmethod
    def validate_action(action, context):
        """Validate action against Four Laws."""
        
        # Perform validation
        is_allowed, reason = FourLaws._evaluate(action, context)
        
        # Extract severity
        severity = context.get("severity", "medium")
        
        # Determine violated law
        law_violated = None
        if not is_allowed:
            # Extract law from reason (e.g., "First Law: ...")
            law_violated = reason.split(":")[0] if ":" in reason else "Unknown"
        
        # Record metrics
        collector.record_four_laws_validation(
            is_allowed=is_allowed,
            law_violated=law_violated,
            severity=severity
        )
        
        # Log result
        if not is_allowed:
            logger.warning("Four Laws denial: %s - %s", action, reason)
        else:
            logger.debug("Four Laws allowed: %s", action)
        
        return is_allowed, reason
```

**Metrics Exposed:**
- `project_ai_four_laws_validations_total{result="allowed|denied"}`
- `project_ai_four_laws_denials_total{law_violated, severity}`

---

### 3. Plugin System Integration

**Example: Plugin Execution**

```python
# src/app/plugins/plugin_runner.py
import time
from app.monitoring.metrics_collector import collector

class PluginRunner:
    def execute_plugin(self, plugin_name, args):
        """Execute plugin with metrics."""
        start_time = time.time()
        
        try:
            # Load plugin
            plugin = self._load_plugin(plugin_name)
            
            # Execute
            result = plugin.run(args)
            
            # Record success
            duration = time.time() - start_time
            collector.record_plugin_execution(
                plugin_name=plugin_name,
                status="success",
                duration_seconds=duration
            )
            
            logger.info("Plugin %s executed successfully in %.3fs",
                       plugin_name, duration)
            
            return result
        
        except Exception as e:
            # Record failure
            duration = time.time() - start_time
            collector.record_plugin_execution(
                plugin_name=plugin_name,
                status="error",
                duration_seconds=duration,
                error_type=type(e).__name__
            )
            
            logger.error("Plugin %s failed: %s", plugin_name, e, exc_info=True)
            
            raise
    
    def load_plugins(self):
        """Load all plugins and update count."""
        plugins = self._discover_plugins()
        
        # Update gauge
        collector.set_plugin_count(len(plugins))
        
        logger.info("Loaded %d plugins", len(plugins))
        
        return plugins
```

**Metrics Exposed:**
- `project_ai_plugin_loaded_total` (Gauge)
- `project_ai_plugin_execution_total{plugin_name, status}`
- `project_ai_plugin_execution_duration_seconds{plugin_name}` (Histogram)

---

### 4. API Endpoint Integration

**Example: Flask API**

```python
# src/app/interfaces/web/app.py
import time
from flask import Flask, request, jsonify
from app.monitoring.metrics_collector import collector

app = Flask(__name__)

@app.before_request
def before_request():
    """Record request start time."""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Record request metrics."""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        
        collector.record_api_request(
            method=request.method,
            endpoint=request.path,
            status=response.status_code,
            duration_seconds=duration
        )
    
    return response

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with error handling."""
    try:
        data = request.get_json()
        message = data.get('message')
        
        # Process chat
        response = ai_engine.chat(message)
        
        return jsonify({"response": response})
    
    except Exception as e:
        logger.error("Chat API error: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500
```

**Metrics Exposed:**
- `project_ai_api_requests_total{method, endpoint, status}`
- `project_ai_api_request_duration_seconds{method, endpoint}` (Histogram)

---

### 5. Background Task Integration

**Example: Periodic Metrics Collection**

```python
# src/app/monitoring/background_collector.py
import threading
import time
from app.monitoring.metrics_collector import collector

class BackgroundCollector:
    def __init__(self, interval_seconds=15):
        self.interval = interval_seconds
        self.running = False
        self.thread = None
    
    def start(self):
        """Start background collection thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._collect_loop,
            daemon=True,
            name="BackgroundCollector"
        )
        self.thread.start()
        
        logger.info("Background metrics collection started (interval=%ds)",
                   self.interval)
    
    def stop(self):
        """Stop background collection."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Background metrics collection stopped")
    
    def _collect_loop(self):
        """Periodically collect metrics."""
        while self.running:
            try:
                # Collect all metrics from disk
                collector.collect_all_metrics()
                
                logger.debug("Collected metrics from disk")
            
            except Exception as e:
                logger.error("Error collecting metrics: %s", e)
            
            # Sleep until next collection
            time.sleep(self.interval)

# Global instance
background_collector = BackgroundCollector(interval_seconds=15)
```

**Usage in Application:**

```python
# src/app/main.py
from app.monitoring.background_collector import background_collector

def main():
    # Start background collection
    background_collector.start()
    
    # Start application
    app.run()
    
    # Cleanup on shutdown
    background_collector.stop()
```

---

## Adding Custom Metrics

### Step 1: Define Metric in Prometheus Exporter

```python
# src/app/monitoring/prometheus_exporter.py
from prometheus_client import Counter, Gauge, Histogram

class PrometheusMetrics:
    def __init__(self, registry=None):
        self.registry = registry or CollectorRegistry()
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        # ... existing metrics ...
        
        # Add your custom metric
        self.custom_feature_executions_total = Counter(
            'project_ai_custom_feature_executions_total',
            'Total custom feature executions',
            ['feature_name', 'status'],
            registry=self.registry
        )
        
        self.custom_feature_duration_seconds = Histogram(
            'project_ai_custom_feature_duration_seconds',
            'Custom feature execution duration',
            ['feature_name'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )
```

### Step 2: Add Collection Method

```python
# src/app/monitoring/metrics_collector.py
class MetricsCollector:
    def record_custom_feature(self, feature_name, status, duration_seconds=None):
        """Record custom feature execution."""
        metrics.custom_feature_executions_total.labels(
            feature_name=feature_name,
            status=status
        ).inc()
        
        if duration_seconds is not None:
            metrics.custom_feature_duration_seconds.labels(
                feature_name=feature_name
            ).observe(duration_seconds)
```

### Step 3: Instrument Code

```python
# src/app/features/custom_feature.py
from app.monitoring.metrics_collector import collector

def execute_custom_feature(data):
    start_time = time.time()
    
    try:
        result = process_data(data)
        
        duration = time.time() - start_time
        collector.record_custom_feature(
            feature_name="data_processor",
            status="success",
            duration_seconds=duration
        )
        
        return result
    
    except Exception as e:
        duration = time.time() - start_time
        collector.record_custom_feature(
            feature_name="data_processor",
            status="error",
            duration_seconds=duration
        )
        
        raise
```

### Step 4: Test Metrics

```python
# tests/monitoring/test_custom_metrics.py
import pytest
from app.monitoring.metrics_collector import MetricsCollector

@pytest.fixture
def collector(tmp_path):
    return MetricsCollector(data_dir=str(tmp_path))

def test_custom_feature_metrics(collector):
    """Test custom feature metrics."""
    
    # Record execution
    collector.record_custom_feature(
        feature_name="test_feature",
        status="success",
        duration_seconds=0.5
    )
    
    # Verify counter incremented
    from app.monitoring.prometheus_exporter import metrics
    counter_value = metrics.custom_feature_executions_total.labels(
        feature_name="test_feature",
        status="success"
    )._value._value
    
    assert counter_value == 1
```

---

## Integration Checklist

### Before Integrating Metrics

- [ ] **Identify what to measure**
  - Success/failure counts
  - Execution duration
  - Error types
  - Resource usage

- [ ] **Choose metric types**
  - Counter for events
  - Gauge for current state
  - Histogram for distributions

- [ ] **Define label strategy**
  - Keep cardinality low (<1000 combinations)
  - Use meaningful label names
  - Avoid dynamic values (user IDs, request IDs)

- [ ] **Plan for testing**
  - Unit tests for metric collection
  - Integration tests for end-to-end flow

### During Integration

- [ ] **Add metrics to exporter**
  - Define metric in `prometheus_exporter.py`
  - Add collection method in `metrics_collector.py`

- [ ] **Instrument code**
  - Import collector
  - Record metrics at key points
  - Handle errors gracefully

- [ ] **Add logging**
  - Log INFO for normal operations
  - Log WARNING for recoverable errors
  - Log ERROR for failures
  - Include context (correlation IDs, user info)

- [ ] **Write tests**
  - Test metric increments/updates
  - Test error handling
  - Test metric persistence

### After Integration

- [ ] **Verify metrics exposed**
  ```bash
  curl http://localhost:8000/metrics | grep custom_feature
  ```

- [ ] **Create dashboard panel**
  - Add to relevant Grafana dashboard
  - Include queries, thresholds, units

- [ ] **Configure alerts (if needed)**
  - Define alert rules
  - Set thresholds based on SLOs
  - Test alert firing

- [ ] **Update documentation**
  - Add to [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
  - Document in feature README
  - Update runbooks if needed

---

## Advanced Integration Patterns

### Pattern 1: Decorator-Based Instrumentation

```python
from functools import wraps
import time

def monitored_operation(operation_name):
    """Decorator to automatically instrument functions."""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                collector.record_operation(
                    operation=operation_name,
                    status="success",
                    duration_seconds=duration
                )
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                collector.record_operation(
                    operation=operation_name,
                    status="error",
                    duration_seconds=duration,
                    error_type=type(e).__name__
                )
                
                raise
        
        return wrapper
    return decorator

# Usage
@monitored_operation("memory_query")
def search_memory(query):
    return memory_system.search(query)
```

---

### Pattern 2: Context Manager for Timing

```python
from contextlib import contextmanager

@contextmanager
def timed_block(operation_name):
    """Context manager for timing code blocks."""
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        collector.record_operation_duration(
            operation=operation_name,
            duration_seconds=duration
        )

# Usage
with timed_block("database_migration"):
    migrate_database()
```

---

### Pattern 3: Batch Metric Collection

```python
class BatchCollector:
    """Collect metrics in batches for efficiency."""
    
    def __init__(self, flush_interval=10):
        self.buffer = []
        self.flush_interval = flush_interval
        self.last_flush = time.time()
    
    def record(self, metric_type, **kwargs):
        """Add metric to buffer."""
        self.buffer.append({
            "type": metric_type,
            "timestamp": time.time(),
            **kwargs
        })
        
        # Flush if interval exceeded
        if time.time() - self.last_flush > self.flush_interval:
            self.flush()
    
    def flush(self):
        """Flush buffered metrics."""
        for metric in self.buffer:
            if metric["type"] == "counter":
                collector.increment_counter(metric["name"], metric["value"])
            elif metric["type"] == "gauge":
                collector.set_gauge(metric["name"], metric["value"])
        
        self.buffer.clear()
        self.last_flush = time.time()

# Usage
batch_collector = BatchCollector(flush_interval=10)

for item in large_dataset:
    batch_collector.record("counter", name="items_processed", value=1)

batch_collector.flush()
```

---

## Common Integration Issues

### Issue 1: Circular Import

**Problem:**
```python
# app/core/ai_systems.py imports metrics_collector
# metrics_collector.py imports ai_systems (circular!)
```

**Solution:**
```python
# Use late import
def get_metrics():
    from app.monitoring.metrics_collector import collector
    return collector

# Or: Import at function level
def update_mood(self):
    from app.monitoring.metrics_collector import collector
    collector.collect_persona_metrics(self.state)
```

---

### Issue 2: Metrics Not Persisting

**Problem:** Metrics reset on application restart

**Solution:** Use periodic collection to sync with disk state
```python
# Periodically collect metrics from persistent storage
collector.collect_all_metrics()
```

---

### Issue 3: High Performance Overhead

**Problem:** Metrics collection slows down application

**Solution 1: Sample high-frequency events**
```python
import random

if random.random() < 0.1:  # Sample 10%
    collector.record_event()
```

**Solution 2: Use async collection**
```python
import asyncio

async def record_metric_async(metric_name, value):
    await asyncio.sleep(0)  # Yield control
    collector.record(metric_name, value)
```

---

## Testing Integration

### Unit Test Example

```python
# tests/monitoring/test_integration.py
import pytest
from app.monitoring.metrics_collector import MetricsCollector
from app.monitoring.prometheus_exporter import PrometheusMetrics

@pytest.fixture
def collector(tmp_path):
    return MetricsCollector(data_dir=str(tmp_path))

@pytest.fixture
def metrics():
    return PrometheusMetrics()

def test_feature_metrics_integration(collector, metrics):
    """Test full metrics integration."""
    
    # Execute feature
    from app.features.custom_feature import execute_custom_feature
    result = execute_custom_feature({"data": "test"})
    
    # Verify metrics recorded
    assert result is not None
    
    # Check counter incremented
    counter = metrics.custom_feature_executions_total.labels(
        feature_name="data_processor",
        status="success"
    )
    assert counter._value._value == 1
    
    # Check histogram recorded
    histogram = metrics.custom_feature_duration_seconds.labels(
        feature_name="data_processor"
    )
    assert histogram._count._value == 1
```

---

## Related Documentation

- [Monitoring Architecture Overview](01_monitoring_architecture_overview.md)
- [Prometheus Metrics Catalog](03_prometheus_metrics_catalog.md)
- [Telemetry Collection Patterns](07_telemetry_collection_patterns.md)
- [Observability Best Practices](08_observability_best_practices.md)

---

## Contact & Support

- **Team:** Security Agents Team
- **Slack:** #project-ai-monitoring
- **Code Reviews:** Request review from @monitoring-team
- **Documentation:** `source-docs/monitoring/`
- **Code:** `src/app/monitoring/`

---

**Last Updated:** 2026-04-20  
**Maintainer:** Security Agents Team  
**Version:** 1.0
