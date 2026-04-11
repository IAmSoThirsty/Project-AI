# OctoReflex Telemetry - Quick Reference

## 🚀 Import & Initialize

```python
from octoreflex.internal.telemetry import (
    PrometheusExporter,
    OctoTracer,
    eBPFEventStream,
    get_logger,
    trace_operation,
)

# Or use the bridge for everything
from octoreflex.internal.telemetry.bridge import get_telemetry_bridge
bridge = get_telemetry_bridge()
```

## 📊 Metrics (Prometheus)

```python
# Get exporter
from octoreflex.internal.telemetry.prometheus import get_exporter
prom = get_exporter()

# Record threat score
prom.octo.record_threat_score(85.0)

# Record state transition
prom.octo.record_state_transition("monitoring", "containment")

# Record containment latency
prom.octo.record_containment(0.0023)  # 2.3ms

# Record detection
prom.octo.record_true_positive()
prom.octo.record_false_positive()

# Record event processed
prom.octo.record_event_processed()

# Record processing latency
prom.octo.record_processing_latency(0.00015)  # 150μs

# Export metrics
text = prom.export_text()
```

## 🔍 Tracing (OpenTelemetry)

```python
from octoreflex.internal.telemetry.tracing import get_tracer, trace_operation

tracer = get_tracer()

# Context manager
with tracer.span("operation_name"):
    # Do work
    pass

# Decorator
@trace_operation("my_function")
def my_function():
    pass

# Manual
span = tracer.start_span("manual_op")
span.set_attribute("key", "value")
span.add_event("checkpoint")
tracer.end_span(span)

# Export
traces = tracer.export_jaeger()
```

## 📡 Events (eBPF)

```python
from octoreflex.internal.telemetry.events import get_event_stream, EventType

stream = get_event_stream()

# Subscribe to events
def handle_syscall(event):
    print(f"Syscall: {event.syscall_name}")

stream.subscribe(EventType.SYSCALL, handle_syscall)

# Start processing
stream.start()

# Get stats
stats = stream.get_stats()

# Stop
stream.stop()
```

## 📝 Logging (Structured)

```python
from octoreflex.internal.telemetry import get_logger, CorrelationContext

logger = get_logger(__name__)

# With correlation ID
with CorrelationContext() as corr_id:
    logger.info("Processing request", request_id=123, user="alice")
    # Output: {"timestamp": 1234567890, "correlation_id": "...", ...}

# Simple logging
logger.info("Event processed", count=42)
logger.warning("High threat", score=95.0)
logger.error("Failed to contain", reason="timeout")
```

## 🌉 Bridge (All-in-one)

```python
from octoreflex.internal.telemetry.bridge import get_telemetry_bridge

bridge = get_telemetry_bridge()

# Process with telemetry
bridge.process_reflex({
    "threat_score": 85.0,
    "from_state": "monitoring",
    "to_state": "containment"
})

# Record containment
bridge.record_containment(0.0015)

# Record detection
bridge.record_detection(is_true_positive=True)

# Export all metrics
metrics = bridge.export_metrics()

# Get stats
stats = bridge.get_stats()
```

## 📈 Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `octoreflex_threat_score_current` | Gauge | Current threat level (0-100) |
| `octoreflex_state_transitions_total` | Counter | State changes by from/to |
| `octoreflex_containment_latency_seconds` | Histogram | Containment response time |
| `octoreflex_false_positives_total` | Counter | False positive count |
| `octoreflex_true_positives_total` | Counter | True positive count |
| `octoreflex_events_processed_total` | Counter | Total events processed |
| `octoreflex_processing_latency_seconds` | Histogram | Processing time |

## 🎯 Common Patterns

### Full Request Instrumentation

```python
from octoreflex.internal.telemetry import (
    get_tracer,
    get_logger,
    CorrelationContext,
)
from octoreflex.internal.telemetry.prometheus import get_exporter

tracer = get_tracer()
logger = get_logger(__name__)
prom = get_exporter()

def process_event(event):
    with CorrelationContext() as corr_id:
        with tracer.span("process_event"):
            logger.info("Processing event", event_id=event.id)
            
            # Process...
            
            prom.octo.record_event_processed()
            logger.info("Event complete")
```

### Error Handling with Telemetry

```python
with tracer.span("risky_operation") as span:
    try:
        # Do work
        result = dangerous_operation()
        span.set_attribute("result", result)
        prom.octo.record_true_positive()
    except Exception as e:
        span.set_attribute("error", str(e))
        logger.error("Operation failed", error=str(e))
        prom.octo.record_false_positive()
        raise
```

## 🔧 Configuration

```bash
# Environment variables
export OCTOREFLEX_LOG_LEVEL=INFO
export OCTOREFLEX_METRICS_PORT=9090
export OCTOREFLEX_TRACE_ENABLED=true
export OCTOREFLEX_EBPF_ENABLED=true
export OCTOREFLEX_EVENT_BUFFER_SIZE=65536
```

## 📊 Dashboards

Import to Grafana:
- `octoreflex/dashboards/octoreflex-main.json` - Main monitoring
- `octoreflex/dashboards/octoreflex-performance.json` - Performance analysis

## 🚨 Alerts

Load into Prometheus:
```yaml
# prometheus.yml
rule_files:
  - "octoreflex/dashboards/prometheus-alerts.yml"
```

## 🧪 Testing

```bash
# Run tests
python -m pytest octoreflex/internal/telemetry/test_telemetry.py

# Run benchmarks
python octoreflex/internal/telemetry/benchmark.py

# Run example
python octoreflex/internal/telemetry/example.py
```

## 📚 Documentation

- Full API: `octoreflex/internal/telemetry/README.md`
- Deployment: `octoreflex/internal/telemetry/DEPLOYMENT.md`
- Summary: `octoreflex/internal/telemetry/IMPLEMENTATION_SUMMARY.md`

## ⚡ Performance Tips

1. **Use gauges for current state** (threat score)
2. **Use counters for totals** (events processed)
3. **Use histograms for latencies** (response time)
4. **Keep label cardinality low** (avoid user IDs)
5. **Sample traces in production** (10% is good)
6. **Set correlation IDs early** (at request boundary)
7. **Monitor buffer utilization** (prevent drops)

## 🆘 Troubleshooting

```python
# Check health
bridge = get_telemetry_bridge()
stats = bridge.get_stats()
print(f"Events dropped: {stats['event_stream']['events_dropped']}")
print(f"Buffer used: {stats['event_stream']['buffer_used']}")

# Debug metrics
print(prom.export_text())

# Debug traces
print(tracer.export_jaeger())
```

---

**Quick Links**:
- Metrics endpoint: `http://localhost:9090/metrics`
- Prometheus: `http://localhost:9091`
- Grafana: `http://localhost:3000`
