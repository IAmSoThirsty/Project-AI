# Observability and Metrics - Cerberus Telemetry

## Overview

CerberusObservability provides comprehensive telemetry, SLO tracking, and incident forensics for the Cerberus Hydra Defense system. It tracks agent timelines, incident graphs, performance metrics, and generates Prometheus-compatible metrics.

**Location:** [[src/app/core/cerberus_observability.py]] (`src/app/core/cerberus_observability.py`) (437 lines)

**Core Philosophy:** Complete visibility into defense system behavior for forensics, optimization, and compliance.

---

## Architecture

### Data Structures

```python
@dataclass
class AgentTimeline:
    """Timeline of agent lifecycle events"""
    agent_id: str
    spawn_time: float
    tasks: list[dict[str, Any]]
    decisions: list[dict[str, Any]]
    termination_time: float | None
    termination_reason: str | None

@dataclass
class IncidentGraph:
    """Hydra graph for incident visualization"""
    incident_id: str
    start_time: float
    nodes: dict[str, dict]           # agent_id -> metadata
    edges: list[tuple[str, str, dict]]  # (from, to, metadata)
    resolution_time: float | None
    outcome: str | None

@dataclass
class SLOMetrics:
    """Service Level Objective metrics"""
    # Detection response
    detect_to_lockdown_times: deque[float]
    
    # False positives
    total_lockdowns: int
    false_positive_lockdowns: int
    
    # Resources
    max_concurrent_agents_samples: deque[int]
    resource_overhead_samples: deque[float]
    
    # Availability
    total_incidents: int
    contained_incidents: int
    failed_containments: int
```

---

## API Reference

### Initialization

```python
from app.core.cerberus_observability import CerberusObservability

obs = CerberusObservability(data_dir="data")

# Creates telemetry directory: data/cerberus/telemetry/
```

### Agent Timeline Tracking

```python
# Start tracking agent
obs.start_agent_timeline("agent-001")

# Add tasks to timeline
obs.add_agent_task("agent-001", {
    "type": "monitor",
    "section": "authentication",
    "rules": ["rate_limit", "credential_validation"]
})

# Add decisions
obs.add_agent_decision("agent-001", {
    "action": "lockdown",
    "confidence": 0.92,
    "reason": "repeated_authentication_failures"
})

# Record termination
obs.terminate_agent("agent-001", reason="incident_resolved")

# Get agent timeline report
report = obs.get_agent_timeline_report("agent-001")
print(f"""
Agent Timeline:
- Spawn time: {report['spawn_time']}
- Lifetime: {report['lifetime_seconds']:.2f}s
- Total tasks: {report['total_tasks']}
- Total decisions: {report['total_decisions']}
- Terminated: {report['terminated']}
- Reason: {report['termination_reason']}
- Recent tasks: {report['tasks'][-5:]}
- Recent decisions: {report['decisions'][-5:]}
""")
```

### Incident Graph Tracking

```python
# Start incident graph
obs.start_incident_graph("inc-001")

# Add agent nodes
obs.add_agent_to_incident("inc-001", "agent-001", {
    "language": "Python",
    "generation": 0,
    "locked_section": "authentication"
})

obs.add_agent_to_incident("inc-001", "agent-002", {
    "language": "Rust",
    "generation": 1,
    "locked_section": "api_endpoints",
    "parent": "agent-001"
})

# Add communication edges (information flow)
obs.add_agent_communication(
    incident_id="inc-001",
    from_agent="agent-001",
    to_agent="agent-002",
    metadata={
        "type": "spawn",
        "reason": "bypass_detected",
        "timestamp": time.time()
    }
)

# Resolve incident
obs.resolve_incident("inc-001", outcome="contained")

# Get incident graph report
report = obs.get_incident_graph_report("inc-001")
print(f"""
Incident Graph:
- Start time: {report['start_time']}
- Duration: {report['duration_seconds']:.2f}s
- Total agents: {report['total_agents']}
- Communications: {report['total_communications']}
- Outcome: {report['outcome']}
- Resolved: {report['resolved']}
""")

# Visualize graph structure
print("Nodes:", report['nodes'])
print("Edges:", report['edges'])
```

### SLO Metrics

```python
# Record detect-to-lockdown time
obs.slo_metrics.record_detect_to_lockdown(2.5)  # 2.5 seconds

# Record lockdown event
obs.slo_metrics.record_lockdown(is_false_positive=False)

# Record agent count
obs.slo_metrics.record_agent_count(15)

# Record resource overhead
obs.slo_metrics.record_resource_overhead(12.5)  # 12.5% CPU overhead

# Record incident outcome
obs.slo_metrics.record_incident_outcome(contained=True)

# Get SLO report
slo = obs.get_slo_report()
print(f"""
SLO Metrics:
- Median detect-to-lockdown: {slo['detect_to_lockdown']['median_seconds']:.2f}s
- P95 detect-to-lockdown: {slo['detect_to_lockdown']['p95_seconds']:.2f}s
- Total lockdowns: {slo['lockdowns']['total']}
- False positives: {slo['lockdowns']['false_positives']}
- False positive rate: {slo['lockdowns']['false_positive_rate']:.2%}
- Max concurrent agents: {slo['resources']['max_concurrent_agents']}
- Avg overhead: {slo['resources']['avg_overhead_percent']:.2f}%
- Containment rate: {slo['incidents']['containment_rate']:.2%}
""")
```

### Performance Samples

```python
# Record performance sample
obs.record_performance_sample({
    "concurrent_agents": 15,
    "resource_overhead_percent": 12.5,
    "cpu_percent": 45.2,
    "memory_mb": 1024,
    "spawn_rate": 3.5  # agents/second
})

# Samples auto-update SLO metrics
```

### Export Telemetry

```python
# Export incident graph and SLO metrics to JSON files
obs.export_telemetry(incident_id="inc-001")

# Creates files:
# - data/cerberus/telemetry/incident_inc-001_20240115_103045.json
# - data/cerberus/telemetry/slo_metrics_20240115_103045.json
```

### Generate Prometheus Metrics

```python
# Generate Prometheus-compatible metrics
metrics = obs.generate_prometheus_metrics()

print(metrics)
"""
Output:
cerberus_detect_to_lockdown_median_seconds 2.5
cerberus_detect_to_lockdown_p95_seconds 4.8
cerberus_lockdowns_total 42
cerberus_lockdowns_false_positive_total 3
cerberus_lockdowns_false_positive_rate 0.071
cerberus_max_concurrent_agents 25
cerberus_resource_overhead_percent 12.5
cerberus_incidents_total 15
cerberus_incidents_contained 14
cerberus_incidents_failed 1
cerberus_incidents_containment_rate 0.933
"""

# Expose metrics endpoint
@app.route('/metrics')
def metrics_endpoint():
    return obs.generate_prometheus_metrics(), 200, {'Content-Type': 'text/plain'}
```

---

## SLO Targets

### Detection and Response

**Target:** Median detect-to-lockdown < 3 seconds

```python
median = slo['detect_to_lockdown']['median_seconds']

if median < 3.0:
    print("✓ SLO met: Fast detection and response")
elif median < 5.0:
    print("⚠ SLO warning: Slower than target")
else:
    print("✗ SLO violated: Detection too slow")
```

### False Positives

**Target:** False positive rate < 5%

```python
fp_rate = slo['lockdowns']['false_positive_rate']

if fp_rate < 0.05:
    print("✓ SLO met: Low false positive rate")
elif fp_rate < 0.10:
    print("⚠ SLO warning: Elevated false positives")
else:
    print("✗ SLO violated: Too many false positives")
```

### Resource Efficiency

**Target:** Average overhead < 15%

```python
overhead = slo['resources']['avg_overhead_percent']

if overhead < 15.0:
    print("✓ SLO met: Efficient resource usage")
elif overhead < 25.0:
    print("⚠ SLO warning: Higher overhead")
else:
    print("✗ SLO violated: Excessive overhead")
```

### Containment Rate

**Target:** Containment rate > 95%

```python
containment = slo['incidents']['containment_rate']

if containment > 0.95:
    print("✓ SLO met: High containment success")
elif containment > 0.90:
    print("⚠ SLO warning: Some containment failures")
else:
    print("✗ SLO violated: Too many failures")
```

---

## Integration Patterns

### Cerberus Hydra Integration

```python
from app.core.cerberus_hydra import CerberusHydraDefense
from app.core.cerberus_observability import CerberusObservability

# Initialize with observability
hydra = CerberusHydraDefense(data_dir="data")
obs = CerberusObservability(data_dir="data")

# On agent spawn
agent_id = hydra._spawn_single_agent(generation=0)
obs.start_agent_timeline(agent_id)
obs.add_agent_to_incident(incident_id, agent_id, {
    "language": runtime.name,
    "generation": 0
})

# On agent decision
obs.add_agent_decision(agent_id, {
    "action": "lockdown",
    "confidence": 0.9
})

# On incident resolution
obs.resolve_incident(incident_id, outcome="contained")
```

### Prometheus Integration

```python
from prometheus_client import CollectorRegistry, Gauge, generate_latest

registry = CollectorRegistry()

# Define gauges
detect_to_lockdown = Gauge(
    'cerberus_detect_to_lockdown_median_seconds',
    'Median time from detection to lockdown',
    registry=registry
)

lockdown_false_positive_rate = Gauge(
    'cerberus_lockdown_false_positive_rate',
    'False positive lockdown rate',
    registry=registry
)

# Update metrics periodically
def update_prometheus_metrics():
    slo = obs.get_slo_report()
    
    detect_to_lockdown.set(slo['detect_to_lockdown']['median_seconds'])
    lockdown_false_positive_rate.set(slo['lockdowns']['false_positive_rate'])

# Expose metrics
@app.route('/metrics')
def prometheus_metrics():
    update_prometheus_metrics()
    return generate_latest(registry)
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Cerberus Hydra Observability",
    "panels": [
      {
        "title": "Detect-to-Lockdown Time",
        "targets": [{
          "expr": "cerberus_detect_to_lockdown_median_seconds"
        }],
        "thresholds": [3.0, 5.0]
      },
      {
        "title": "False Positive Rate",
        "targets": [{
          "expr": "cerberus_lockdown_false_positive_rate"
        }],
        "thresholds": [0.05, 0.10]
      },
      {
        "title": "Concurrent Agents",
        "targets": [{
          "expr": "cerberus_max_concurrent_agents"
        }]
      },
      {
        "title": "Containment Rate",
        "targets": [{
          "expr": "cerberus_incidents_containment_rate"
        }],
        "thresholds": [0.90, 0.95]
      }
    ]
  }
}
```

---

## Incident Forensics

### Reconstruct Attack Timeline

```python
# Get incident graph
report = obs.get_incident_graph_report(incident_id)

# Analyze attack flow
print(f"Incident Duration: {report['duration_seconds']:.2f}s")
print(f"Agents Spawned: {report['total_agents']}")

# Trace agent spawn cascade
for edge in report['edges']:
    from_agent = edge['from']
    to_agent = edge['to']
    metadata = edge['metadata']
    
    if metadata['type'] == 'spawn':
        print(f"  {from_agent} spawned {to_agent}")
        print(f"    Reason: {metadata['reason']}")

# Identify breach patterns
breach_agents = [
    node_id for node_id, data in report['nodes'].items()
    if data.get('locked_section') == 'authentication'
]
print(f"Authentication agents: {len(breach_agents)}")
```

### Root Cause Analysis

```python
# Find initial breach agent (generation 0)
initial_agents = [
    (agent_id, data) for agent_id, data in report['nodes'].items()
    if data.get('generation') == 0
]

print(f"Initial breach agents: {len(initial_agents)}")

# Analyze spawn cascade depth
max_generation = max(
    data.get('generation', 0) 
    for data in report['nodes'].values()
)
print(f"Max spawn depth: {max_generation}")

# Count agents per generation
from collections import Counter
generation_counts = Counter(
    data.get('generation', 0)
    for data in report['nodes'].values()
)
print(f"Agents by generation: {dict(generation_counts)}")
```

---

## Performance Considerations

### Memory Usage

- **Agent Timelines:** ~5 KB per agent
- **Incident Graphs:** ~10 KB per incident (depends on agent count)
- **SLO Metrics:** ~50 KB (rolling windows of 1000 samples)
- **Performance Samples:** ~1 MB (deque of 10,000 samples)

### Optimization

```python
# Limit timeline history
obs.agent_timelines[agent_id].tasks = obs.agent_timelines[agent_id].tasks[-100:]
obs.agent_timelines[agent_id].decisions = obs.agent_timelines[agent_id].decisions[-100:]

# Export and clear old incidents
for incident_id in list(obs.incident_graphs.keys())[:-50]:
    obs.export_telemetry(incident_id)
    del obs.incident_graphs[incident_id]

# Persist to disk periodically
import schedule

schedule.every(5).minutes.do(lambda: obs.export_telemetry())
```

---

## Best Practices

1. **Start Timelines Early:** Call `start_agent_timeline()` immediately after agent spawn
2. **Resolve Incidents:** Always call `resolve_incident()` with outcome
3. **Export Regularly:** Export telemetry every 5-10 minutes to prevent memory growth
4. **Monitor SLOs:** Set up alerts for SLO violations
5. **Analyze Failures:** Review failed containments for system improvements
6. **Graph Visualization:** Use incident graphs for post-mortem analysis
7. **Prometheus Integration:** Expose metrics for real-time monitoring

---


---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/cerberus_observability.py]]
- [[src/app/core/security/auth.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]

---
## Related Documentation

- [01-cerberus-hydra-defense.md](01-cerberus-hydra-defense.md) - Uses observability for tracking
- [02-lockdown-controller.md](02-lockdown-controller.md) - Lockdown events tracked
- [05-security-monitoring.md](05-security-monitoring.md) - CloudWatch integration

---

## See Also

- [Prometheus Metrics Guide](../../docs/PROMETHEUS_METRICS.md)
- [Grafana Dashboard Setup](../../docs/GRAFANA_DASHBOARDS.md)
- [SLO Targets and Monitoring](../../docs/SLO_MONITORING.md)
