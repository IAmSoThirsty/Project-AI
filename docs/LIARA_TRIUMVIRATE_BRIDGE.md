# Liara-Triumvirate Integration Bridge

## Overview

The Liara-Triumvirate Bridge provides seamless integration between **Liara** (emergency governance controller) and the **Triumvirate** (Galahad, Cerberus, Codex Deus). It enables smooth transitions, state synchronization, health monitoring, and automatic fallback mechanisms.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Liara-Triumvirate Bridge                   │
│                                                             │
│  ┌──────────────┐         ┌────────────────────┐          │
│  │   Health     │         │   Handoff          │          │
│  │  Monitoring  │────────▶│   Protocol         │          │
│  └──────────────┘         └────────────────────┘          │
│                                                             │
│  ┌──────────────┐         ┌────────────────────┐          │
│  │    State     │         │   Capability       │          │
│  │  Sync Layer  │◀───────▶│    Mapping         │          │
│  └──────────────┘         └────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                               │
         ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│   Triumvirate    │          │      Liara       │
│                  │          │                  │
│ • Galahad        │          │ • TTL-bound      │
│ • Cerberus       │          │ • Restricted     │
│ • Codex Deus     │          │ • Emergency      │
└──────────────────┘          └──────────────────┘
```

## Key Components

### 1. Health Monitoring

The bridge continuously monitors the health of all three Triumvirate pillars:

- **Galahad**: Checks reasoning capacity, curiosity levels, history bounds
- **Cerberus**: Monitors policy enforcement, denial rates, compliance
- **Codex**: Validates model status, device availability, resource bounds

#### Health Signals

Each pillar's health is evaluated on four dimensions:
- `alive`: Is the component responsive?
- `responsive`: Is it producing timely results?
- `bounded`: Are resource constraints respected?
- `compliant`: Are policies being followed?

```python
from kernel.liara_triumvirate_bridge import LiaraTriumvirateBridge

bridge = LiaraTriumvirateBridge(triumvirate=my_triumvirate)
health = bridge.monitor_triumvirate_health()

if not health.is_stable():
    print(f"Failed pillars: {health.get_failed_pillars()}")
```

### 2. Handoff Protocol

The bridge implements a **5-phase handoff protocol** for smooth transitions:

#### Triumvirate → Liara
1. **Capture State**: Snapshot current Triumvirate state
2. **Validate Conditions**: Check cooldown period and prerequisites
3. **Activate Liara**: Authorize Liara with TTL
4. **Sync State**: Transfer essential state to Liara context
5. **Update Bridge**: Transition to Liara mode

#### Liara → Triumvirate
1. **Verify Health**: Ensure Triumvirate is stable
2. **Capture Liara State**: Snapshot Liara's state
3. **Deactivate Liara**: Revoke Liara authorization
4. **Sync State**: Transfer state back to Triumvirate
5. **Update Bridge**: Transition to Triumvirate mode

```python
# Handoff to Liara (typically triggered automatically)
success = bridge.execute_handoff_to_liara("galahad", "health_degradation")

# Handoff back to Triumvirate (when stable)
success = bridge.execute_handoff_to_triumvirate("pillar_restored")
```

### 3. State Synchronization

The bridge maintains a **shared state layer** (`sync_data`) that both systems can access:

**During Triumvirate operation:**
- Last health check results
- Telemetry snapshots
- Reasoning history

**During Liara operation:**
- Failed pillar information
- Triumvirate snapshot (for context)
- Handoff timestamp and reason

**Always synchronized:**
- Current mode
- Active controller
- Handoff history
- Capability restrictions

```python
# Access sync data
sync_data = bridge.state.sync_data

# State is automatically synchronized during handoffs
```

### 4. Capability Mapping

When Liara substitutes a Triumvirate pillar, capabilities are restricted:

#### Galahad → Liara
- ✓ Arbitration allowed
- ⚠️ Reasoning limited
- ✗ Curiosity disabled
- ⚠️ History depth: 10 (reduced)
- ✓ Sovereign mode enforced

#### Cerberus → Liara
- ✓ Input validation allowed
- ✓ Output validation allowed
- ✓ Policy enforcement: strict
- ✗ Custom policies disabled
- ✓ Block on deny: always

#### Codex → Liara
- ✗ ML inference disabled
- ✗ Model loading disabled
- ✓ Rule-based fallback
- ⚠️ CPU only (no GPU)

```python
# Get capability restrictions
restrictions = bridge.map_triumvirate_capabilities_to_liara("galahad")
print(restrictions)
```

### 5. Automatic Fallback

The bridge implements **TTL-based automatic fallback**:

1. **TTL Check**: On every request, check if Liara TTL has expired
2. **Health Assessment**: If expired, check Triumvirate health
3. **Automatic Handoff**: If Triumvirate is stable, execute fallback
4. **Governance Hold**: If Triumvirate is still unhealthy, enter hold state

```python
# Automatic fallback is checked on every process_request call
result = bridge.process_request(input_data)

# Manual check
fallback_executed = bridge.check_liara_ttl_and_fallback()
```

## Usage

### Basic Setup

```python
from cognition.liara_guard import LiaraState
from kernel.liara_triumvirate_bridge import LiaraTriumvirateBridge
from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

# Initialize Triumvirate
config = TriumvirateConfig()
triumvirate = Triumvirate(config=config)

# Initialize Liara state
liara_state = LiaraState()

# Create bridge
bridge = LiaraTriumvirateBridge(
    triumvirate=triumvirate,
    liara_state=liara_state
)
```

### Processing Requests

```python
# Process through bridge (automatically routes to appropriate controller)
result = bridge.process_request(
    input_data={"query": "Analyze security policy"},
    context={"user": "admin", "priority": "high"}
)

print(f"Controller: {result['controller']}")  # 'triumvirate' or 'liara'
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
```

### Monitoring Status

```python
# Get comprehensive status
status = bridge.get_bridge_status()

print(f"Mode: {status['mode']}")  # 'triumvirate', 'liara', or 'governance_hold'
print(f"Active Controller: {status['active_controller']}")
print(f"Handoff Count: {status['handoff_count']}")
print(f"Health Checks: {status['health_checks']}")

# Check Triumvirate health
if status['triumvirate_health']:
    health = status['triumvirate_health']
    print(f"Galahad: {'✓' if health['galahad']['healthy'] else '✗'}")
    print(f"Cerberus: {'✓' if health['cerberus']['healthy'] else '✗'}")
    print(f"Codex: {'✓' if health['codex']['healthy'] else '✗'}")
```

## Operational Modes

### Mode: `triumvirate`
- **Controller**: Triumvirate
- **Behavior**: Normal operation with full capabilities
- **Transitions to `liara`**: When pillar health degrades

### Mode: `liara`
- **Controller**: Liara
- **Behavior**: Restricted operation with TTL
- **Transitions to `triumvirate`**: When TTL expires and Triumvirate is healthy
- **Transitions to `governance_hold`**: When TTL expires but Triumvirate still unhealthy

### Mode: `governance_hold`
- **Controller**: None (emergency state)
- **Behavior**: System halted, awaiting manual intervention
- **Transitions**: Manual recovery required

## Audit Trail

The bridge emits comprehensive audit events:

- `HANDOFF_TO_LIARA_COMPLETE`: Successful transition to Liara
- `HANDOFF_TO_TRIUMVIRATE_COMPLETE`: Successful transition back
- `HANDOFF_VALIDATION_FAILED`: Handoff preconditions not met
- `LIARA_TTL_EXPIRED`: TTL expired, fallback initiated
- `GOVERNANCE_HOLD`: Multiple pillar failure, system halted
- `STATE_SYNC_TO_LIARA`: State synchronized to Liara
- `STATE_SYNC_TO_TRIUMVIRATE`: State synchronized back

All events are logged to `cognition/governance_audit.log`.

## Safety Guarantees

### Cooldown Period
Handoffs respect a **300-second cooldown** to prevent rapid oscillation:
```python
COOLDOWN_SECONDS = 300  # 5 minutes
```

### Single Pillar Substitution
Liara can only substitute **one pillar at a time**. Multiple failures trigger governance hold.

### TTL Enforcement
Liara's authority is **strictly time-bound** (default 900 seconds):
```python
authorize_liara(role="galahad", ttl_seconds=900)
```

### State Immutability
State captures are **snapshots** - original state is preserved during handoffs.

## Error Handling

### Handoff Failures
- Logged with full context
- System remains in current mode
- Audit trail updated

### Health Check Failures
- Degraded health signals returned
- Processing continues if possible
- Automatic handoff may trigger

### TTL Expiry
- Automatic fallback attempted
- If Triumvirate unhealthy: governance hold
- Manual intervention may be required

## Testing

Comprehensive test suite in `tests/test_liara_triumvirate_integration.py`:

```bash
# Run integration tests
pytest tests/test_liara_triumvirate_integration.py -v

# Run specific test class
pytest tests/test_liara_triumvirate_integration.py::TestHandoffProtocol -v

# Run with coverage
pytest tests/test_liara_triumvirate_integration.py --cov=kernel.liara_triumvirate_bridge
```

## Examples

See `examples/liara_triumvirate_bridge_example.py` for complete examples:

```bash
python examples/liara_triumvirate_bridge_example.py
```

## Integration Points

### With Existing Systems

**Liara (`cognition/kernel_liara.py`)**:
- Uses `maybe_activate_liara()` for activation
- Uses `restore_pillar()` for deactivation
- Respects `COOLDOWN_SECONDS`

**Triumvirate (`src/cognition/triumvirate.py`)**:
- Calls `triumvirate.process()` for requests
- Calls `triumvirate.get_status()` for health
- Monitors each engine independently

**Audit System (`cognition/audit.py`)**:
- All events logged via `audit(event, detail)`
- Maintains governance audit trail

### Extension Points

**Custom Health Evaluators**:
Override `_evaluate_*_health()` methods for custom health logic

**Custom Capability Mappings**:
Extend `map_triumvirate_capabilities_to_liara()` for new pillars

**Custom State Sync**:
Override `_sync_state_to_*()` methods for custom state transfer

## Performance Considerations

- **Health Checks**: O(1) complexity, minimal overhead
- **State Capture**: Lightweight snapshots, no deep copies
- **Handoffs**: Sub-second execution for smooth transitions
- **TTL Checks**: Performed on every request, negligible cost

## Metrics

The bridge tracks operational metrics:

- `handoff_count`: Total handoffs executed
- `health_checks`: Total health monitoring operations
- `sync_operations`: Total state synchronization operations

Access via:
```python
status = bridge.get_bridge_status()
print(f"Handoffs: {status['handoff_count']}")
print(f"Health Checks: {status['health_checks']}")
print(f"Sync Ops: {status['sync_operations']}")
```

## Future Enhancements

- [ ] Multi-pillar Liara substitution (currently single-pillar only)
- [ ] Predictive health degradation detection
- [ ] Configurable TTL per pillar type
- [ ] Bridge telemetry integration
- [ ] Advanced state compression for large histories
- [ ] Health trend analysis and reporting

## License

Part of the Sovereign Governance Substrate. See LICENSE for details.
