# Triumvirate Coordination Enhanced

Real-time coordination system for Galahad/Cerberus/Codex pillars with sub-millisecond voting, deadlock resolution, and graceful degradation.

## Quick Start

```python
from src.cognition.triumvirate_coordination_enhanced import (
    EnhancedTriumvirateCoordinator,
    CoordinationConfig
)
from src.cognition.galahad.engine import GalahadEngine
from src.cognition.cerberus.engine import CerberusEngine
from src.cognition.codex.engine import CodexEngine

# Initialize
coordinator = EnhancedTriumvirateCoordinator(
    galahad_engine=GalahadEngine(),
    cerberus_engine=CerberusEngine(),
    codex_engine=CodexEngine()
)

# Vote (sync)
result = coordinator.vote_sync('decision_id', {'data': 'request'})
print(f"{result.decision.value} ({result.confidence:.2f}) - {result.latency_ms:.3f}ms")

# Vote (async - faster)
result = await coordinator.vote_async('decision_id', {'data': 'request'})
```

## Features

✅ **Sub-millisecond voting** (async mode target)  
✅ **Automatic deadlock resolution** (priority-based)  
✅ **Configurable priority**: Security > Ethics > Consistency  
✅ **Performance metrics**: Latency, quality, throughput  
✅ **Graceful degradation**: Continues with healthy pillars  
✅ **Liara failover**: Emergency governance on total failure  

## Documentation

- **Full Documentation**: [docs/TRIUMVIRATE_COORDINATION_ENHANCED.md](../docs/TRIUMVIRATE_COORDINATION_ENHANCED.md)
- **Examples**: [examples/triumvirate_coordination_demo.py](../examples/triumvirate_coordination_demo.py)
- **Tests**: [tests/test_triumvirate_coordination_enhanced.py](../tests/test_triumvirate_coordination_enhanced.py)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│   EnhancedTriumvirateCoordinator                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Galahad  │  │ Cerberus │  │  Codex   │         │
│  │ (Ethics) │  │(Security)│  │(Consist.)│         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │                │
│       └─────────────┴─────────────┘                │
│                     │                              │
│              Voting Protocol                       │
│         (Async/Sync, <1ms target)                 │
│                     │                              │
│         ┌───────────┴───────────┐                 │
│         │  Resolution Engine    │                 │
│         │  - Unanimous          │                 │
│         │  - Majority           │                 │
│         │  - Deadlock → Priority│                 │
│         └───────────┬───────────┘                 │
│                     │                              │
│              ┌──────┴──────┐                      │
│              │   Metrics    │                      │
│              │  - Latency   │                      │
│              │  - Quality   │                      │
│              └──────────────┘                      │
│                                                     │
│         Failover: Liara (on total failure)         │
└─────────────────────────────────────────────────────┘
```

## Performance

| Mode | Latency Target | Throughput |
|------|---------------|------------|
| Async | <1ms | 1000+ votes/sec |
| Sync | <10ms | 100-500 votes/sec |
| Degraded (2 pillars) | <15ms | ~66% normal |
| Degraded (1 pillar) | <20ms | ~33% normal |

## Configuration

```python
config = CoordinationConfig(
    priority_order=[PillarType.CERBERUS, PillarType.GALAHAD, PillarType.CODEX],
    voting_timeout=0.001,  # 1ms
    min_confidence=0.5,
    enable_liara_failover=True,
    health_check_interval=1.0,
    enable_metrics=True,
    deadlock_strategy="priority",  # or "highest_confidence", "random"
    async_voting=True
)
```

## Vote Resolution

### Unanimous (All Agree)
```
Galahad: ALLOW (0.8)
Cerberus: ALLOW (0.9)  →  ALLOW (0.83)
Codex: ALLOW (0.7)
```

### Majority (>50% Agree)
```
Galahad: ALLOW (0.8)
Cerberus: ALLOW (0.9)  →  ALLOW (0.85)
Codex: DENY (0.7)
```

### Deadlock (Priority Tiebreaker)
```
Galahad: ALLOW (0.8)
Cerberus: DENY (0.9)   →  DENY (0.72) - Cerberus wins
Codex: MODIFY (0.7)        (CRITICAL priority)
```

## Testing

```bash
# Run all tests
pytest tests/test_triumvirate_coordination_enhanced.py -v

# Run specific test
pytest tests/test_triumvirate_coordination_enhanced.py::test_async_unanimous_vote -v

# Run demo
python examples/triumvirate_coordination_demo.py
```

## Monitoring

```python
# Check health
health = coordinator.get_health_status()
print(f"Healthy: {health['healthy_count']}/3")

# Get metrics
metrics = coordinator.get_metrics()
print(f"Avg latency: {metrics.avg_latency_ms:.3f}ms")
print(f"Unanimous rate: {metrics.unanimous_decisions}/{metrics.total_votes}")

# Analyze history
history = coordinator.get_vote_history(limit=100)
for result in history[-10:]:
    print(f"{result.decision.value}: {result.latency_ms:.3f}ms")
```

## Integration

### With Original Triumvirate

```python
from src.cognition.triumvirate import Triumvirate

# Use both systems
classic = Triumvirate()
enhanced = EnhancedTriumvirateCoordinator(...)

# Classic for full pipeline
result = classic.process(input_data, context)

# Enhanced for fast decisions
vote = enhanced.vote_sync('quick_decision', context)
```

### With Liara Bridge

```python
from kernel.liara_triumvirate_bridge import LiaraTriumvirateBridge

liara_bridge = LiaraTriumvirateBridge()
coordinator = EnhancedTriumvirateCoordinator(
    ...,
    liara_bridge=liara_bridge
)
```

## License

Sovereign Governance Substrate - See LICENSE

## Version

Enhanced: 2026-04-09  
Original Triumvirate: 2026-03-04
