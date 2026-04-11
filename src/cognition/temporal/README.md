# Chronos - Temporal Weight Engine

**Chronos** is one of "The Fates" - temporal agents responsible for tracking causality and maintaining temporal consistency across the Sovereign Governance Substrate.

Named after the Greek personification of time, Chronos provides a robust foundation for understanding causal relationships, detecting temporal anomalies, and assigning importance weights to events based on their temporal impact.

## Overview

Chronos implements a sophisticated temporal tracking system using:

- **Vector Clocks**: Track logical time across distributed agents
- **Causality Graphs**: Model "happens-before" relationships between events
- **Temporal Consistency**: Verify that time-based invariants hold (no effect before cause)
- **Weight Assignment**: Compute importance based on causal impact
- **Drift Detection**: Identify clock synchronization issues
- **Anomaly Detection**: Find unusual temporal patterns

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       Chronos                            │
│                Temporal Weight Engine                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Vector Clock │  │   Causality  │  │  Temporal    │ │
│  │ Management   │  │    Graph     │  │  Weights     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Consistency  │  │    Drift     │  │   Anomaly    │ │
│  │ Verification │  │  Detection   │  │  Detection   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Audit Ledger   │
                   └─────────────────┘
```

## Components

### 1. Vector Clock (`vector_clock.py`)

Implements Lamport's vector clocks for tracking causality in distributed systems.

**Key Operations:**
- `tick()`: Increment local logical time
- `merge(other)`: Merge another vector clock (on message receive)
- `happens_before(other)`: Check if this event causally precedes another
- `concurrent_with(other)`: Check if events are concurrent (no causal relationship)

**Example:**
```python
from src.cognition.temporal import VectorClock

# Agent 1 performs local event
vc1 = VectorClock("agent1")
vc1.tick()  # [agent1: 1]

# Agent 2 performs local event
vc2 = VectorClock("agent2")
vc2.tick()  # [agent2: 1]

# Agent 1 receives message from Agent 2
vc1.merge(vc2)  # [agent1: 2, agent2: 1]

# Check relationships
print(vc1.happens_before(vc2))  # False
print(vc1.concurrent_with(vc2))  # False (vc1 is now after)
```

### 2. Causality Graph (`causality_graph.py`)

A directed acyclic graph (DAG) representing "happens-before" relationships.

**Features:**
- Add events with causal dependencies
- Prevent cycles (maintains DAG property)
- Retrieve causal chains
- Find concurrent events
- Verify temporal consistency
- Topological sorting

**Example:**
```python
from src.cognition.temporal import CausalityGraph, VectorClock

graph = CausalityGraph()
vc = VectorClock("agent1")

# Add events
graph.add_event("e1", {"type": "start"}, vc.copy())
vc.tick()
graph.add_event("e2", {"type": "process"}, vc.copy(), causes=["e1"])
vc.tick()
graph.add_event("e3", {"type": "end"}, vc.copy(), causes=["e2"])

# Get causal chain
chain = graph.get_causal_chain("e3")
print(chain)  # ['e1', 'e2', 'e3']

# Verify consistency
is_consistent, violations = graph.verify_consistency()
print(f"Consistent: {is_consistent}")
```

### 3. Chronos Engine (`chronos.py`)

Main temporal tracking engine that coordinates all components.

**Capabilities:**
- Record events from multiple agents
- Automatically manage vector clocks
- Build and maintain causality graph
- Compute temporal weights
- Detect clock drift
- Find temporal anomalies
- Export/import state
- Integrate with audit logging

**Example:**
```python
from src.cognition.temporal import Chronos

# Initialize Chronos
chronos = Chronos("chronos-main")

# Record events
e1 = chronos.record_event(
    event_id="e1",
    event_type="data_ingestion",
    agent_id="worker1",
    data={"source": "sensor_a"}
)

e2 = chronos.record_event(
    event_id="e2",
    event_type="data_processing",
    agent_id="worker2",
    causes=["e1"],  # Causally depends on e1
    data={"algorithm": "filter"}
)

# Get statistics
stats = chronos.get_statistics()
print(f"Total events: {stats['total_events']}")
print(f"Active agents: {stats['active_agents']}")

# Verify consistency
is_consistent, violations = chronos.verify_consistency()
if not is_consistent:
    print("Violations:", violations)

# Detect anomalies
anomalies = chronos.detect_anomalies()
for anomaly in anomalies:
    print(f"Anomaly: {anomaly['type']} - {anomaly}")
```

## Temporal Weights

Chronos assigns weights to events based on their causal impact:

**Weight Factors:**
1. **Descendants**: Number of events that causally depend on this event (future impact)
2. **Depth**: Position in the causal chain (historical context)
3. **Branching**: Number of immediate descendants (direct impact)
4. **Event Type**: Critical events (security, failures) get higher weights

**Weight Formula:**
```
weight = 1.0 
       + (descendant_count × 0.1)
       + (ancestor_count × 0.05)
       + (immediate_descendants × 0.2)
       + type_weight
```

Weights are capped at 10.0 and indicate relative importance for:
- Audit prioritization
- Impact analysis
- Root cause analysis
- Event retention policies

## Consistency Verification

Chronos performs multi-level consistency checks:

### 1. Graph Structure
- Ensures DAG property (no cycles)
- Validates edge relationships

### 2. Vector Clock Consistency
- Verifies that causal edges align with vector clock ordering
- Detects violations where cause doesn't happen before effect

### 3. Wall-Clock Consistency
- Checks that physical timestamps don't contradict causality
- Allows 1-second tolerance for clock drift

**Example Violation:**
```
Event e1 (timestamp: 10:00:05) -> Event e2 (timestamp: 10:00:03)
Violation: Effect occurred 2 seconds before cause
```

## Drift Detection

Monitors time differences between causally related events:

**Configuration:**
- Default threshold: 5.0 seconds
- Customizable per instance

**Detection:**
```python
chronos = Chronos("test", drift_threshold_seconds=2.0)

# Record events with time gap
e1 = chronos.record_event("e1", "start", "agent1")
time.sleep(3)  # Simulate delay
e2 = chronos.record_event("e2", "continue", "agent1", causes=["e1"])

# Check violations
print(chronos.drift_violations)
# [{'event_id': 'e2', 'cause_id': 'e1', 'time_diff_seconds': 3.1, ...}]
```

## Anomaly Detection

Identifies unusual temporal patterns:

### 1. High Temporal Weight
Events with weight > 2× mean weight

### 2. Clock Drift
Events with time gaps exceeding threshold

### 3. Large Time Gaps
Causally related events separated by > 1 hour

**Example:**
```python
anomalies = chronos.detect_anomalies()

for anomaly in anomalies:
    if anomaly['type'] == 'high_temporal_weight':
        print(f"Critical event: {anomaly['event_id']} (weight: {anomaly['weight']})")
    elif anomaly['type'] == 'clock_drift':
        print(f"Drift detected: {anomaly['time_diff_seconds']}s")
    elif anomaly['type'] == 'large_time_gap':
        print(f"Time gap: {anomaly['gap_seconds']}s")
```

## Integration with Audit Ledger

Chronos automatically logs events to the audit system:

**Audit Entry Format:**
```yaml
---
timestamp: '2024-01-15T10:30:45.123456+00:00'
event_type: temporal_event
actor: 'chronos:chronos-main'
description: 'Temporal event: data_processing'
data:
  event_id: 'e2'
  event_type: 'data_processing'
  agent_id: 'worker2'
  temporal_weight: 1.45
  vector_clock: 'VectorClock(worker2, [worker1:1, worker2:2])'
  causes: ['e1']
metadata:
  chronos_instance: 'chronos-main'
previous_hash: 'abc123...'
hash: 'def456...'
```

**Disable Audit:**
```python
chronos = Chronos("test", enable_audit=False)
```

## State Persistence

Chronos can save and restore complete state:

**Save State:**
```python
from pathlib import Path

chronos = Chronos(
    "chronos-main",
    state_file=Path("./data/chronos_state.json")
)

# Record events...
chronos.record_event("e1", "start", "agent1")

# Save to file
chronos.save_state()
```

**Load State:**
```python
# State is automatically loaded if file exists
chronos = Chronos(
    "chronos-main",
    state_file=Path("./data/chronos_state.json")
)

print(f"Loaded {chronos.event_count} events")
```

**State Contents:**
- Instance ID
- Causality graph (nodes, edges, vector clocks, timestamps)
- Agent vector clocks
- All events
- Temporal weights
- Drift violations
- Consistency violations

## The Fates: Integration with Atropos and Clotho

Chronos is one of three "Fates" agents:

- **Clotho**: Event creation and initialization patterns
- **Chronos**: Temporal tracking and causality (this module)
- **Atropos**: Event lifecycle and termination patterns

Together they provide complete temporal governance:

```python
# Clotho: Event creation
event_id = clotho.create_event(event_type="process_start")

# Chronos: Track causality
chronos.record_event(
    event_id=event_id,
    event_type="process_start",
    agent_id="worker1"
)

# Atropos: Event termination
atropos.terminate_event(event_id, reason="completed")
```

## Use Cases

### 1. Distributed System Debugging
Track causality across microservices to debug distributed failures.

### 2. Root Cause Analysis
Identify which events led to a particular outcome by tracing causal chains.

### 3. Audit Trail Verification
Verify that audit logs maintain temporal consistency.

### 4. Performance Analysis
Identify events with high temporal weight (bottlenecks or critical points).

### 5. Anomaly Detection
Find unusual patterns: clock drift, temporal violations, orphaned events.

### 6. Event Prioritization
Use temporal weights to prioritize event processing or retention.

## Testing

Comprehensive test suite in `tests/cognition/test_chronos.py`:

```bash
# Run tests
pytest tests/cognition/test_chronos.py -v

# Run specific test class
pytest tests/cognition/test_chronos.py::TestChronos -v

# Run with coverage
pytest tests/cognition/test_chronos.py --cov=src.cognition.temporal --cov-report=term-missing
```

**Test Coverage:**
- Vector clock operations
- Causality graph construction
- Event recording and tracking
- Consistency verification
- Weight computation
- Drift detection
- Anomaly detection
- State persistence
- Integration scenarios

## API Reference

### VectorClock

```python
class VectorClock:
    def __init__(self, process_id: str, initial_clock: Optional[Dict[str, int]] = None)
    def tick(self) -> VectorClock
    def merge(self, other: VectorClock) -> VectorClock
    def happens_before(self, other: VectorClock) -> bool
    def concurrent_with(self, other: VectorClock) -> bool
    def compare(self, other: VectorClock) -> str
    def equals(self, other: VectorClock) -> bool
    def copy(self) -> VectorClock
    def to_dict(self) -> Dict[str, Any]
    def to_json(self) -> str
    @classmethod from_dict(cls, data: Dict[str, Any]) -> VectorClock
    @classmethod from_json(cls, json_str: str) -> VectorClock
```

### CausalityGraph

```python
class CausalityGraph:
    def __init__(self)
    def add_event(self, event_id: str, event_data: Dict[str, Any], 
                  vector_clock: VectorClock, causes: Optional[List[str]] = None,
                  timestamp: Optional[datetime] = None) -> bool
    def add_causal_link(self, cause_id: str, effect_id: str) -> bool
    def get_causal_chain(self, event_id: str) -> List[str]
    def get_descendants(self, event_id: str) -> Set[str]
    def get_concurrent_events(self, event_id: str) -> Set[str]
    def verify_consistency(self) -> Tuple[bool, List[str]]
    def get_stats(self) -> Dict[str, Any]
    def to_dict(self) -> Dict[str, Any]
    def to_json(self) -> str
    @classmethod from_dict(cls, data: Dict[str, Any]) -> CausalityGraph
    @classmethod from_json(cls, json_str: str) -> CausalityGraph
```

### Chronos

```python
class Chronos:
    def __init__(self, instance_id: str, enable_audit: bool = True,
                 drift_threshold_seconds: float = 5.0,
                 state_file: Optional[Path] = None)
    def record_event(self, event_id: str, event_type: str, agent_id: str,
                    data: Optional[Dict[str, Any]] = None,
                    causes: Optional[List[str]] = None,
                    timestamp: Optional[datetime] = None) -> TemporalEvent
    def verify_consistency(self) -> Tuple[bool, List[str]]
    def detect_anomalies(self) -> List[Dict[str, Any]]
    def get_causal_chain(self, event_id: str) -> List[str]
    def get_concurrent_events(self, event_id: str) -> Set[str]
    def get_statistics(self) -> Dict[str, Any]
    def export_state(self) -> Dict[str, Any]
    def import_state(self, state: Dict[str, Any]) -> None
    def save_state(self) -> bool
```

## Performance Considerations

### Time Complexity

- **Record Event**: O(|causes| + log n) for merging clocks and graph insertion
- **Verify Consistency**: O(n + e) where n = nodes, e = edges
- **Get Causal Chain**: O(n + e) for ancestor traversal + topological sort
- **Detect Anomalies**: O(n) for iterating events

### Space Complexity

- **Vector Clocks**: O(a × n) where a = agents, n = events
- **Causality Graph**: O(n + e) for nodes and edges
- **Events**: O(n) for event storage

### Optimizations

1. **Lazy Weight Computation**: Weights computed on-demand when needed
2. **Incremental Consistency**: Check only new events since last verification
3. **Graph Pruning**: Archive old events beyond retention window
4. **Clock Compression**: Merge inactive agent entries

## References

- Lamport, L. (1978). "Time, clocks, and the ordering of events in a distributed system"
- Fidge, C.J. (1988). "Timestamps in message-passing systems that preserve the partial ordering"
- Mattern, F. (1989). "Virtual time and global states of distributed systems"

## License

Part of the Sovereign Governance Substrate.
Licensed under the terms specified in the project LICENSE file.
