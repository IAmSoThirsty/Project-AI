# Liara Kernel - Triumvirate Failover Controller

## Overview

Liara is a hot-swapping kernel controller that provides seamless failover for degraded Triumvirate pillars (Galahad, Cerberus, and Codex Deus). It maintains system stability during pillar recovery while enforcing strict time limits to prevent permanent substitution.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIUMVIRATE PILLARS                      │
├─────────────────┬─────────────────┬──────────────────────────┤
│    GALAHAD      │    CERBERUS     │     CODEX DEUS          │
│   Reasoning &   │     Policy      │    ML Inference         │
│   Arbitration   │   Enforcement   │                         │
└────────┬────────┴────────┬────────┴────────┬────────────────┘
         │                 │                 │
         │ Health Monitor  │                 │
         ▼                 ▼                 ▼
    ┌────────────────────────────────────────────┐
    │         LIARA FAILOVER CONTROLLER          │
    │                                            │
    │  ⚡ Hot-swap activation                    │
    │  ⏱️  900s TTL enforcement                  │
    │  🚫 Role-stacking prohibition              │
    │  🔍 Degradation detection                  │
    │  🔒 Cryptographic proof                    │
    │  ⚙️  Limited capabilities                  │
    └────────────────────────────────────────────┘
```

## Key Features

### 1. Hot-Swap Mechanism
- **Automatic Detection**: Monitors Triumvirate pillar health continuously
- **Seamless Takeover**: Activates when a pillar exceeds failure threshold
- **Zero Downtime**: Provides continuity during pillar degradation

### 2. 900-Second TTL
- **Strict Time Limit**: Enforces 15-minute maximum failover duration
- **Automatic Shutdown**: Forces deactivation when TTL expires
- **Cryptographic Proof**: HMAC-SHA256 verification of activation time and TTL

### 3. Role-Stacking Prohibition
- **Single Role Only**: Cannot hold multiple pillar roles simultaneously
- **Protection**: Prevents resource conflicts and ensures clean substitution
- **Statistics Tracking**: Counts and logs prevention events

### 4. Degradation Detection
- **Configurable Thresholds**: Default 3 consecutive failures
- **Per-Pillar Monitoring**: Independent health tracking for each Triumvirate member
- **Auto-Failover**: Triggers when threshold exceeded

### 5. Capability Restrictions
Liara operates with **limited capabilities** compared to full Triumvirate members:

| Pillar Role | Available Capabilities |
|-------------|------------------------|
| Galahad | Basic Reasoning, Health Monitoring, Emergency Shutdown |
| Cerberus | Policy Check, Health Monitoring, Emergency Shutdown |
| Codex Deus | Simple Inference, Health Monitoring, Emergency Shutdown |
| Inactive | Health Monitoring only |

## Usage

### Basic Failover

```python
from kernel import LiaraKernel, TriumviratePillar

# Create Liara kernel
liara = LiaraKernel(ttl_seconds=900, failover_threshold=3)

# Manually activate failover
liara.activate_failover(
    TriumviratePillar.GALAHAD, 
    reason="manual_intervention"
)

# Check status
status = liara.get_status()
print(f"Active role: {status['active_role']}")
print(f"TTL remaining: {status['ttl_remaining']}s")

# Deactivate when done
liara.deactivate_failover(reason="pillar_recovered")
```

### Automatic Failover with Health Monitoring

```python
from kernel.health import HealthMonitor
from kernel import LiaraKernel, TriumviratePillar

# Setup
health_monitor = HealthMonitor()
liara = LiaraKernel(
    health_monitor=health_monitor,
    ttl_seconds=900,
    failover_threshold=3
)

# Register health checks for Triumvirate pillars
def check_galahad():
    # Your health check logic
    return galahad_service.is_healthy()

liara.register_pillar_health_check(
    TriumviratePillar.GALAHAD,
    check_galahad
)

# Start monitoring (automatic failover on degradation)
health_monitor.start_monitoring()
```

### Capability Execution

```python
from kernel import LiaraKernel, TriumviratePillar
from kernel.liara_kernel import LiaraCapability

liara = LiaraKernel()
liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

# Execute limited operation
result = liara.execute_limited_operation(
    LiaraCapability.BASIC_REASONING,
    {"input": "data_to_process"}
)

if result["success"]:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

### Pillar Handoff

```python
# After pillar recovers, hand off role back
success = liara.handoff_to_pillar(TriumviratePillar.GALAHAD)

if success:
    print("✅ Handoff complete - Galahad resumed")
else:
    print("❌ Handoff failed - pillar not healthy")
```

## API Reference

### LiaraKernel

#### Constructor
```python
LiaraKernel(
    health_monitor: Optional[HealthMonitor] = None,
    ttl_seconds: int = 900,
    failover_threshold: int = 3
)
```

#### Methods

##### activate_failover
```python
activate_failover(
    pillar: TriumviratePillar,
    reason: str = "manual_activation"
) -> bool
```
Activate Liara failover for degraded pillar.

##### deactivate_failover
```python
deactivate_failover(reason: str = "manual_shutdown") -> bool
```
Deactivate Liara failover and return to normal operation.

##### check_pillar_health
```python
check_pillar_health(pillar: TriumviratePillar) -> HealthStatus
```
Check health of specific Triumvirate pillar.

##### get_active_role
```python
get_active_role() -> Optional[TriumviratePillar]
```
Get currently active failover role.

##### get_remaining_ttl
```python
get_remaining_ttl() -> Optional[float]
```
Get remaining time-to-live in seconds.

##### verify_ttl_proof
```python
verify_ttl_proof() -> bool
```
Verify cryptographic proof of TTL enforcement.

##### has_capability
```python
has_capability(capability: LiaraCapability) -> bool
```
Check if Liara has specific capability based on active role.

##### execute_limited_operation
```python
execute_limited_operation(
    capability: LiaraCapability,
    operation_data: Dict[str, Any]
) -> Dict[str, Any]
```
Execute limited operation based on capability.

##### handoff_to_pillar
```python
handoff_to_pillar(pillar: TriumviratePillar) -> bool
```
Hand off active role back to recovered pillar.

##### get_status
```python
get_status() -> Dict[str, Any]
```
Get comprehensive Liara status including active role, TTL, and pillar health.

## Enumerations

### TriumviratePillar
```python
class TriumviratePillar(Enum):
    GALAHAD = "galahad"      # Reasoning and arbitration
    CERBERUS = "cerberus"    # Policy enforcement
    CODEX_DEUS = "codex_deus"  # ML inference
    NONE = "none"            # Not active
```

### LiaraCapability
```python
class LiaraCapability(Enum):
    BASIC_REASONING = "basic_reasoning"       # Simplified Galahad
    POLICY_CHECK = "policy_check"             # Basic Cerberus
    SIMPLE_INFERENCE = "simple_inference"     # Limited Codex
    HEALTH_MONITORING = "health_monitoring"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"
```

## Security Features

### Cryptographic TTL Proof
Liara uses HMAC-SHA256 to generate and verify activation proofs:

```python
proof = HMAC-SHA256(
    secret_key,
    f"{pillar}:{activation_time}:{ttl_seconds}"
)
```

This ensures:
- **Tamper Resistance**: Activation time cannot be modified
- **Verification**: TTL enforcement can be cryptographically verified
- **Audit Trail**: Proof stored with activation record

### Role-Stacking Prevention
Liara enforces single-role constraint at multiple levels:
1. **Activation Check**: Rejects new activation if already active
2. **Statistics**: Tracks prevention attempts
3. **Logging**: Records all prevention events for audit

## Testing

### Run Unit Tests
```bash
cd Sovereign-Governance-Substrate
export PYTHONPATH=.  # or $env:PYTHONPATH = "." on Windows
python kernel/test_liara_kernel.py
```

### Run Demonstration
```bash
python kernel/liara_demo.py
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Failover Activation Time | < 100ms |
| Health Check Interval | 5 seconds |
| TTL Check Interval | 1 second |
| Default TTL | 900 seconds (15 minutes) |
| Default Failure Threshold | 3 consecutive failures |
| Memory Overhead | ~5KB per active role |

## Integration Points

### Health Monitoring
Liara integrates with `kernel.health.HealthMonitor`:
- Registers health checks for each pillar
- Uses circuit breaker patterns
- Supports graceful degradation

### Triumvirate System
Liara bridges to Triumvirate pillars:
- `src.cognition.triumvirate.Triumvirate`
- `src.cognition.galahad.engine.GalahadEngine`
- `src.cognition.cerberus.engine.CerberusEngine`
- `src.cognition.codex.engine.CodexEngine`

## Callbacks

### Activation Callbacks
```python
def on_activation(pillar: TriumviratePillar, reason: str):
    print(f"Failover activated for {pillar.value}: {reason}")

liara.register_activation_callback(on_activation)
```

### Shutdown Callbacks
```python
def on_shutdown(pillar: TriumviratePillar, reason: str, duration: float):
    print(f"Failover ended for {pillar.value} after {duration}s: {reason}")

liara.register_shutdown_callback(on_shutdown)
```

## Statistics

Liara tracks comprehensive statistics:

```python
{
    "total_activations": 0,
    "total_shutdowns": 0,
    "total_handoffs": 0,
    "ttl_violations_prevented": 0,
    "role_stacking_prevented": 0
}
```

## Limitations

1. **Reduced Capabilities**: Liara provides basic functionality only - not a full replacement
2. **Time-Limited**: Maximum 15 minutes (configurable but enforced)
3. **Single Role**: Cannot cover multiple pillar failures simultaneously
4. **No Persistence**: Role state lost on restart (by design)

## Best Practices

1. **Use Auto-Failover**: Register health checks for automatic activation
2. **Monitor TTL**: Track remaining time and prepare for handoff
3. **Test Handoff**: Regularly test pillar recovery and handoff procedures
4. **Set Callbacks**: Register callbacks for visibility into failover events
5. **Configure Thresholds**: Adjust failure threshold based on your environment
6. **Verify Proofs**: Periodically verify TTL proofs for audit compliance

## Troubleshooting

### Failover Not Activating
- Check health check registration
- Verify failure threshold configuration
- Review pillar health status
- Check logs for prevention events

### TTL Expired Unexpectedly
- Verify TTL configuration (default 900s)
- Check for clock synchronization issues
- Review activation timestamps

### Role Stacking Prevented
- Deactivate current role before activating new one
- Check active role status with `get_active_role()`
- Review role-stacking prevention statistics

## License

Part of the Sovereign Governance Substrate project.

## See Also

- `kernel/health.py` - Health monitoring system
- `src/cognition/triumvirate.py` - Triumvirate orchestrator
- `kernel/liara_demo.py` - Demonstration examples
- `kernel/test_liara_kernel.py` - Test suite
