# Enhanced Triumvirate Coordination System

## Overview

The Enhanced Triumvirate Coordination System provides advanced real-time coordination between the three pillars of the Sovereign Governance architecture: **Galahad** (Ethics), **Cerberus** (Security), and **Codex** (Consistency).

## Key Features

### 1. **Real-Time Voting Protocol**
- **Sub-millisecond voting target** for policy decisions
- Asynchronous and synchronous modes
- Concurrent vote collection from all pillars
- Configurable timeout handling

### 2. **Deadlock Resolution**
- **Automatic tiebreaking** when pillars disagree
- Three strategies available:
  - **Priority-based** (default): Uses configurable pillar priority order
  - **Highest-confidence**: Selects vote with highest confidence score
  - **Random**: Last resort randomized selection

### 3. **Priority-Based Arbitration**
- **Default Priority**: Security > Ethics > Consistency
  - `Cerberus` (Security) - `CRITICAL` priority
  - `Galahad` (Ethics) - `HIGH` priority
  - `Codex` (Consistency) - `NORMAL` priority
- **Fully Configurable**: Set custom priority orders
- **Weighted Voting**: Confidence scores influence final decisions

### 4. **Performance Monitoring**
- **Latency Tracking**: Min, max, and average voting latency
- **Decision Quality Metrics**: Confidence scores, unanimous rate
- **Vote Distribution**: Track ALLOW/DENY/MODIFY/ABSTAIN counts
- **Resolution Analytics**: Monitor deadlock frequency, priority overrides

### 5. **Graceful Degradation**
- **Pillar Failure Handling**: Continue with remaining healthy pillars
- **Automatic Health Checks**: Periodic pillar health monitoring
- **Liara Failover**: Emergency governance when all pillars fail
- **Manual Restoration**: Restore failed pillars when recovered

## Architecture

### Pillar Types

```python
class PillarType(Enum):
    GALAHAD = "galahad"   # Ethics - Reasoning and ethical oversight
    CERBERUS = "cerberus" # Security - Policy enforcement
    CODEX = "codex"       # Consistency - ML inference and consistency
```

### Vote Types

```python
class VoteType(Enum):
    ALLOW = "allow"       # Approve the request
    DENY = "deny"         # Reject the request
    MODIFY = "modify"     # Approve with modifications
    ABSTAIN = "abstain"   # No decision (neutral)
```

### Priority Levels

```python
class Priority(Enum):
    CRITICAL = 3  # Security-critical decisions (Cerberus)
    HIGH = 2      # Ethics-related decisions (Galahad)
    NORMAL = 1    # Consistency and optimization (Codex)
    LOW = 0       # Advisory votes
```

## Usage

### Basic Setup

```python
from src.cognition.triumvirate_coordination_enhanced import (
    CoordinationConfig,
    EnhancedTriumvirateCoordinator,
    PillarType
)
from src.cognition.galahad.engine import GalahadEngine, GalahadConfig
from src.cognition.cerberus.engine import CerberusEngine, CerberusConfig
from src.cognition.codex.engine import CodexEngine, CodexConfig

# Initialize engines
galahad = GalahadEngine(GalahadConfig())
cerberus = CerberusEngine(CerberusConfig())
codex = CodexEngine(CodexConfig())

# Create coordinator with default config
coordinator = EnhancedTriumvirateCoordinator(
    galahad_engine=galahad,
    cerberus_engine=cerberus,
    codex_engine=codex
)

# Perform synchronous vote
context = {
    'data': 'Request to process',
    'user_id': 'user_123',
    'action': 'read'
}
result = coordinator.vote_sync('decision_001', context)

print(f"Decision: {result.decision.value}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Latency: {result.latency_ms:.3f}ms")
```

### Asynchronous Voting (Low Latency)

```python
import asyncio

# Configure for async with sub-millisecond target
config = CoordinationConfig(
    async_voting=True,
    voting_timeout=0.001  # 1ms timeout
)

coordinator = EnhancedTriumvirateCoordinator(
    config=config,
    galahad_engine=galahad,
    cerberus_engine=cerberus,
    codex_engine=codex
)

async def vote():
    result = await coordinator.vote_async('async_001', context)
    print(f"Decision made in {result.latency_ms:.3f}ms")

asyncio.run(vote())
```

### Custom Priority Configuration

```python
# Configure Ethics > Security > Consistency
config = CoordinationConfig(
    priority_order=[
        PillarType.GALAHAD,   # Ethics first
        PillarType.CERBERUS,  # Security second
        PillarType.CODEX      # Consistency third
    ]
)

coordinator = EnhancedTriumvirateCoordinator(
    config=config,
    galahad_engine=galahad,
    cerberus_engine=cerberus,
    codex_engine=codex
)
```

### Performance Monitoring

```python
# Enable metrics collection
config = CoordinationConfig(enable_metrics=True)
coordinator = EnhancedTriumvirateCoordinator(config=config, ...)

# Perform votes
for i in range(100):
    coordinator.vote_sync(f'test_{i}', context)

# Retrieve metrics
metrics = coordinator.get_metrics()
print(f"Total votes: {metrics.total_votes}")
print(f"Average latency: {metrics.avg_latency_ms:.3f}ms")
print(f"Unanimous decisions: {metrics.unanimous_decisions}")
print(f"Deadlocks resolved: {metrics.deadlocks_resolved}")
```

### Handling Pillar Failures

```python
# Check health status
health = coordinator.get_health_status()
print(f"Healthy pillars: {health['healthy_count']}/3")
print(f"Overall healthy: {health['overall_healthy']}")

# System automatically continues with healthy pillars
result = coordinator.vote_sync('degraded_001', context)

# Manually restore a failed pillar
coordinator.restore_pillar(PillarType.CODEX)
```

## Configuration Options

### CoordinationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `priority_order` | `list[PillarType]` | `[CERBERUS, GALAHAD, CODEX]` | Priority order for deadlock resolution |
| `voting_timeout` | `float` | `0.001` | Voting timeout in seconds (1ms) |
| `min_confidence` | `float` | `0.5` | Minimum confidence threshold |
| `enable_liara_failover` | `bool` | `True` | Enable Liara emergency failover |
| `health_check_interval` | `float` | `1.0` | Pillar health check interval (seconds) |
| `enable_metrics` | `bool` | `True` | Enable performance monitoring |
| `deadlock_strategy` | `str` | `"priority"` | Strategy: `"priority"`, `"highest_confidence"`, `"random"` |
| `async_voting` | `bool` | `True` | Enable async voting mode |

## Performance Characteristics

### Latency Targets

- **Async Mode**: Sub-millisecond target (actual: ~0.1-1ms with mocks)
- **Sync Mode**: 1-10ms typical
- **With Real Engines**: 10-100ms depending on engine complexity

### Throughput

- **Async Mode**: 1000+ votes/second
- **Sync Mode**: 100-500 votes/second
- **Degraded Mode**: Scales with healthy pillar count

### Scalability

- Linear scaling with healthy pillars
- 1 pillar: ~33% throughput, higher latency
- 2 pillars: ~66% throughput
- 3 pillars: 100% throughput (optimal)

## Resolution Strategies

### 1. Unanimous Decision
All pillars agree → Use common decision with averaged confidence

```
Galahad: ALLOW (0.8)
Cerberus: ALLOW (0.9)
Codex: ALLOW (0.7)
→ Result: ALLOW (0.83 confidence)
```

### 2. Majority Decision
More than half agree → Use majority decision with their average confidence

```
Galahad: ALLOW (0.8)
Cerberus: ALLOW (0.9)
Codex: DENY (0.7)
→ Result: ALLOW (0.85 confidence)
```

### 3. Deadlock (Priority-Based)
No majority → Use highest priority pillar's vote

```
Galahad: ALLOW (0.8)
Cerberus: DENY (0.9)
Codex: MODIFY (0.7)
→ Result: DENY (0.72 confidence) - Cerberus has CRITICAL priority
```

### 4. Deadlock (Highest Confidence)
No majority → Use vote with highest confidence

```
Galahad: ALLOW (0.95)  ← Highest confidence
Cerberus: DENY (0.8)
Codex: MODIFY (0.7)
→ Result: ALLOW (0.86 confidence)
```

## Metrics Reference

### PerformanceMetrics

| Metric | Type | Description |
|--------|------|-------------|
| `total_votes` | `int` | Total number of votes processed |
| `avg_latency_ms` | `float` | Average voting latency in milliseconds |
| `min_latency_ms` | `float` | Minimum latency observed |
| `max_latency_ms` | `float` | Maximum latency observed |
| `decisions_by_type` | `dict` | Count of each decision type |
| `deadlocks_resolved` | `int` | Number of deadlocks resolved |
| `unanimous_decisions` | `int` | Number of unanimous decisions |
| `priority_overrides` | `int` | Times priority-based resolution used |
| `pillar_failures` | `dict` | Failure count per pillar |
| `liara_activations` | `int` | Emergency failover activations |
| `avg_confidence` | `float` | Average decision confidence |

## Integration with Liara

When all three pillars fail, the system can automatically failover to **Liara** (emergency governance):

```python
from kernel.liara_triumvirate_bridge import LiaraTriumvirateBridge

# Create coordinator with Liara bridge
liara_bridge = LiaraTriumvirateBridge()

coordinator = EnhancedTriumvirateCoordinator(
    config=CoordinationConfig(enable_liara_failover=True),
    galahad_engine=galahad,
    cerberus_engine=cerberus,
    codex_engine=codex,
    liara_bridge=liara_bridge
)

# On total failure, Liara makes emergency decision
result = await coordinator.vote_async('emergency', context)
# Result may have resolution_method='liara_emergency_failover'
```

## Best Practices

### 1. **Use Async Mode for High-Throughput Systems**
```python
config = CoordinationConfig(async_voting=True, voting_timeout=0.001)
```

### 2. **Enable Metrics in Production**
```python
config = CoordinationConfig(enable_metrics=True)
```

### 3. **Configure Appropriate Timeouts**
```python
# For fast decisions
config = CoordinationConfig(voting_timeout=0.001)  # 1ms

# For complex analysis
config = CoordinationConfig(voting_timeout=0.1)    # 100ms
```

### 4. **Monitor Pillar Health**
```python
# Periodic health checks
health = coordinator.get_health_status()
if not health['overall_healthy']:
    logger.warning(f"Degraded: {health['failed_count']} pillars down")
```

### 5. **Analyze Vote History for Trends**
```python
history = coordinator.get_vote_history(limit=1000)
deny_rate = sum(1 for r in history if r.decision == VoteType.DENY) / len(history)
if deny_rate > 0.5:
    logger.warning("High deny rate detected")
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_triumvirate_coordination_enhanced.py -v
```

Run the demo:

```bash
python examples/triumvirate_coordination_demo.py
```

## API Reference

### EnhancedTriumvirateCoordinator

#### Methods

##### `vote_async(decision_id: str, context: dict, timeout: Optional[float] = None) -> VotingResult`
Asynchronous voting protocol for sub-millisecond latency.

##### `vote_sync(decision_id: str, context: dict, timeout: Optional[float] = None) -> VotingResult`
Synchronous voting protocol (fallback when async not available).

##### `get_metrics() -> Optional[PerformanceMetrics]`
Get current performance metrics.

##### `get_health_status() -> dict`
Get health status of all pillars.

##### `get_vote_history(limit: int = 100) -> list[VotingResult]`
Get recent voting history.

##### `reset_metrics()`
Reset performance metrics.

##### `restore_pillar(pillar: PillarType)`
Manually restore a failed pillar.

## License

Part of the Sovereign Governance Substrate - See main repository LICENSE.

## Authors

- Enhanced Triumvirate Coordination System (2026-04-09)
- Original Triumvirate by Sovereign AI Team

## See Also

- `src/cognition/triumvirate.py` - Original Triumvirate implementation
- `src/cognition/galahad/engine.py` - Galahad Ethics Engine
- `src/cognition/cerberus/engine.py` - Cerberus Security Engine
- `src/cognition/codex/engine.py` - Codex Consistency Engine
- `kernel/liara_triumvirate_bridge.py` - Liara integration
