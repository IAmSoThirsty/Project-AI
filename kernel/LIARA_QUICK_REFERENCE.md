# Liara Kernel Quick Reference

## Installation & Setup

```python
from kernel import LiaraKernel, TriumviratePillar
from kernel.liara_kernel import LiaraCapability
from kernel.health import HealthMonitor
```

## Quick Start

### 1. Basic Failover (Manual)
```python
# Create kernel with 15-minute TTL
liara = LiaraKernel(ttl_seconds=900)

# Activate for degraded pillar
liara.activate_failover(TriumviratePillar.GALAHAD, reason="manual_intervention")

# Check status
print(f"Active: {liara.get_active_role()}")
print(f"TTL: {liara.get_remaining_ttl()}s")

# Deactivate when done
liara.deactivate_failover()
```

### 2. Automatic Failover
```python
# Setup health monitoring
health_monitor = HealthMonitor()
liara = LiaraKernel(health_monitor=health_monitor, failover_threshold=3)

# Register health checks
liara.register_pillar_health_check(
    TriumviratePillar.GALAHAD,
    lambda: galahad_service.is_healthy()
)

# Start monitoring (auto-failover when degraded)
health_monitor.start_monitoring()
```

### 3. Execute Limited Operations
```python
liara.activate_failover(TriumviratePillar.GALAHAD, reason="ops")

# Execute basic reasoning
result = liara.execute_limited_operation(
    LiaraCapability.BASIC_REASONING,
    {"input": "data"}
)
```

### 4. Graceful Handoff
```python
# When pillar recovers
if liara.handoff_to_pillar(TriumviratePillar.GALAHAD):
    print("✅ Handoff complete")
```

## Key Methods

| Method | Purpose |
|--------|---------|
| `activate_failover(pillar, reason)` | Activate for degraded pillar |
| `deactivate_failover(reason)` | Stop failover |
| `check_pillar_health(pillar)` | Check pillar health status |
| `get_active_role()` | Get current active role |
| `get_remaining_ttl()` | Get TTL remaining in seconds |
| `verify_ttl_proof()` | Verify cryptographic TTL proof |
| `has_capability(capability)` | Check if capability available |
| `execute_limited_operation(cap, data)` | Execute limited operation |
| `handoff_to_pillar(pillar)` | Hand off to recovered pillar |
| `get_status()` | Get comprehensive status |

## Pillars & Capabilities

### Triumvirate Pillars
- `GALAHAD` - Reasoning and arbitration
- `CERBERUS` - Policy enforcement  
- `CODEX_DEUS` - ML inference

### Liara Capabilities (by Role)

**Galahad Role:**
- `BASIC_REASONING`
- `HEALTH_MONITORING`
- `EMERGENCY_SHUTDOWN`

**Cerberus Role:**
- `POLICY_CHECK`
- `HEALTH_MONITORING`
- `EMERGENCY_SHUTDOWN`

**Codex Deus Role:**
- `SIMPLE_INFERENCE`
- `HEALTH_MONITORING`
- `EMERGENCY_SHUTDOWN`

## Configuration

```python
LiaraKernel(
    health_monitor=None,         # Optional HealthMonitor
    ttl_seconds=900,             # 15 minutes default
    failover_threshold=3         # 3 failures trigger failover
)
```

## Status Checks

```python
status = liara.get_status()
# Returns:
# {
#     "active": bool,
#     "active_role": str or None,
#     "ttl_remaining": float or None,
#     "ttl_proof_valid": bool,
#     "pillar_health": {...},
#     "statistics": {...}
# }
```

## Statistics

```python
liara.stats
# {
#     "total_activations": int,
#     "total_shutdowns": int,
#     "total_handoffs": int,
#     "ttl_violations_prevented": int,
#     "role_stacking_prevented": int
# }
```

## Callbacks

```python
def on_activate(pillar, reason):
    print(f"Activated: {pillar.value}")

def on_shutdown(pillar, reason, duration):
    print(f"Shutdown: {pillar.value} ({duration}s)")

liara.register_activation_callback(on_activate)
liara.register_shutdown_callback(on_shutdown)
```

## Error Handling

```python
try:
    liara.activate_failover(TriumviratePillar.GALAHAD, "test")
except Exception as e:
    print(f"Activation failed: {e}")

# Check before operations
if not liara.verify_ttl_proof():
    print("⚠️  TTL violation detected")
```

## Best Practices

1. **Always set reason**: Provide descriptive reason for audit trail
2. **Monitor TTL**: Check `get_remaining_ttl()` regularly  
3. **Use auto-failover**: Register health checks for automatic activation
4. **Test handoff**: Verify pillar health before handoff
5. **Handle callbacks**: Register callbacks for visibility
6. **Check capabilities**: Verify capability before execution

## Common Patterns

### Pattern: Monitored Failover with Callbacks
```python
def on_failover(pillar, reason):
    alert_ops_team(f"{pillar.value} failover: {reason}")

def on_recovery(pillar, reason, duration):
    log_incident(pillar, duration)

health_monitor = HealthMonitor()
liara = LiaraKernel(health_monitor=health_monitor)
liara.register_activation_callback(on_failover)
liara.register_shutdown_callback(on_recovery)

liara.register_pillar_health_check(
    TriumviratePillar.GALAHAD,
    check_galahad_health
)

health_monitor.start_monitoring()
```

### Pattern: Manual Intervention with TTL Monitoring
```python
liara = LiaraKernel(ttl_seconds=900)
liara.activate_failover(TriumviratePillar.CERBERUS, "manual_debug")

while liara.get_active_role():
    remaining = liara.get_remaining_ttl()
    if remaining and remaining < 60:
        print(f"⚠️  {remaining}s remaining - prepare handoff")
    time.sleep(10)
```

### Pattern: Capability-Based Operation
```python
liara.activate_failover(TriumviratePillar.GALAHAD, "ops")

if liara.has_capability(LiaraCapability.BASIC_REASONING):
    result = liara.execute_limited_operation(
        LiaraCapability.BASIC_REASONING,
        {"query": "analyze_situation"}
    )
    if result["success"]:
        process_result(result["result"])
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Failover not activating | Check health check registration and threshold |
| Role stacking prevented | Deactivate current role first |
| TTL expired | Increase ttl_seconds or prepare handoff sooner |
| Handoff failed | Verify pillar health status |
| Capability unavailable | Check active role and capability mapping |

## Testing

```bash
# Run unit tests
python kernel/test_liara_kernel.py

# Run demonstration
python kernel/liara_demo.py

# Quick integration test
python -c "from kernel import LiaraKernel; print(LiaraKernel())"
```

## Further Reading

- `kernel/README_LIARA.md` - Full documentation
- `kernel/LIARA_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `kernel/test_liara_kernel.py` - Test examples
- `kernel/liara_demo.py` - Live demonstrations
