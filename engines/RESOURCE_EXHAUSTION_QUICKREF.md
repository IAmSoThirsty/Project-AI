# Enhanced Resource Exhaustion Engine - Quick Reference

## Quick Start

```python
from engines.resource_exhaustion_enhanced import EnhancedResourceExhaustionEngine

# Start monitoring with auto-recovery
engine = EnhancedResourceExhaustionEngine(auto_recovery=True)
engine.start_monitoring()
```

## CLI Commands

```bash
# Test all scenarios
python engines/resource_exhaustion_enhanced.py --test

# Validate quotas
python engines/resource_exhaustion_enhanced.py --validate

# Monitor for 60 seconds
python engines/resource_exhaustion_enhanced.py --monitor --duration 60

# Monitor without auto-recovery
python engines/resource_exhaustion_enhanced.py --monitor --no-auto-recovery
```

## Detection Examples

### Fork Bomb Detection
```python
from engines.resource_exhaustion_enhanced import ForkBombDetector

detector = ForkBombDetector()

# Track process creation
detector.track_process_creation(pid=1234, parent_pid=1233)

# Detect attack
result = detector.detect()
print(f"Detected: {result.detected}, Confidence: {result.confidence:.2%}")
```

### Memory Exhaustion Detection
```python
from engines.resource_exhaustion_enhanced import MemoryExhaustionDetector

detector = MemoryExhaustionDetector()

# Track allocation
detector.track_allocation(size_bytes=10 * 1024 * 1024)  # 10MB

# Detect attack
result = detector.detect()
print(f"Attack Type: {result.attack_type}")
```

### CPU Exhaustion Detection
```python
from engines.resource_exhaustion_enhanced import CPUExhaustionDetector

detector = CPUExhaustionDetector()

# Detect current state
result = detector.detect()
print(f"CPU: {result.evidence['cpu_percent']}%")
```

## Recovery Examples

### Manual Recovery
```python
from engines.resource_exhaustion_enhanced import AttackType, ThreatLevel

# Trigger recovery for fork bomb
recovery = engine.manual_recovery(
    attack_type=AttackType.FORK_BOMB,
    threat_level=ThreatLevel.CRITICAL,
)

print(f"Success: {recovery.success}")
print(f"Actions: {[a.value for a in recovery.actions_taken]}")
print(f"Resources Freed: {recovery.resources_freed}")
```

## Quota Configuration

```python
from engines.resource_exhaustion_enhanced import QuotaConfig

config = QuotaConfig(
    max_processes=1000,
    max_memory_mb=8192.0,
    max_cpu_percent=80.0,
    max_file_descriptors=10000,
    max_process_creation_rate=10,
)

engine = EnhancedResourceExhaustionEngine(quota_config=config)
```

## Quota Validation

```python
# Validate all quotas
validation = engine.validate_quotas()

if not validation['compliant']:
    for name, result in validation['validations'].items():
        if not result.get('compliant', True):
            print(f"{name}: {result}")

# Enforce quotas
enforcement = engine.enforce_quotas()
print(f"Enforced: {enforcement['success']}")
```

## Status Monitoring

```python
# Get current status
status = engine.get_status()

print(f"Monitoring: {status['monitoring_active']}")
print(f"Detections: {status['detection_count']}")
print(f"Recent: {len(status['recent_detections'])}")

# Get current metrics
metrics = status['current_metrics']
print(f"CPU: {metrics['cpu_percent']}%")
print(f"Memory: {metrics['memory_percent']}%")
print(f"Processes: {metrics['process_count']}")
```

## Attack Types

```python
from engines.resource_exhaustion_enhanced import AttackType

AttackType.FORK_BOMB         # Rapid process creation
AttackType.MEMORY_LEAK       # Gradual memory consumption
AttackType.OOM_ATTACK        # Out-of-memory condition
AttackType.HEAP_SPRAY        # Many large allocations
AttackType.CPU_PINNING       # CPU core exhaustion
AttackType.CACHE_POISON      # Cache thrashing
AttackType.DISK_FILL         # Disk space exhaustion
AttackType.FILE_DESCRIPTOR_LEAK  # FD exhaustion
AttackType.THREAD_BOMB       # Thread creation attack
```

## Threat Levels

```python
from engines.resource_exhaustion_enhanced import ThreatLevel

ThreatLevel.LOW              # Minor issue
ThreatLevel.MEDIUM           # Moderate concern
ThreatLevel.HIGH             # Significant threat
ThreatLevel.CRITICAL         # Severe attack
ThreatLevel.CATASTROPHIC     # System failure imminent
```

## Recovery Actions

```python
from engines.resource_exhaustion_enhanced import RecoveryAction

RecoveryAction.KILL_PROCESS     # Terminate malicious process
RecoveryAction.CLEAR_CACHE      # Free system caches
RecoveryAction.FREE_MEMORY      # Force garbage collection
RecoveryAction.THROTTLE_CPU     # Lower process priority
RecoveryAction.CLEANUP_FDS      # Close file descriptors
RecoveryAction.QUARANTINE       # Suspend for forensics
RecoveryAction.RESTART_SERVICE  # Restart affected service
RecoveryAction.ROLLBACK         # Restore previous state
```

## Testing

```python
# Run built-in test scenarios
results = engine.run_test_scenarios()

for scenario, result in results['scenarios'].items():
    print(f"\n{scenario}:")
    if 'detected' in result:
        print(f"  Detected: {result['detected']}")
    if 'error' in result:
        print(f"  Error: {result['error']}")
```

## Error Handling

```python
try:
    engine.start_monitoring()
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.stop_monitoring()
```

## Common Patterns

### Pattern 1: Basic Monitoring
```python
engine = EnhancedResourceExhaustionEngine(auto_recovery=True)
engine.start_monitoring()
time.sleep(300)  # Monitor for 5 minutes
engine.stop_monitoring()
```

### Pattern 2: Detection Only
```python
engine = EnhancedResourceExhaustionEngine(auto_recovery=False)
detections = engine.detect_all()
for d in detections:
    if d.detected:
        print(f"ALERT: {d.attack_type.value} - {d.threat_level.name}")
```

### Pattern 3: Quota Enforcement
```python
config = QuotaConfig(max_memory_mb=4096.0, max_cpu_percent=75.0)
engine = EnhancedResourceExhaustionEngine(quota_config=config)
engine.enforce_quotas()
```

### Pattern 4: Recovery History
```python
history = engine.recovery_system.get_recovery_history(limit=10)
for recovery in history:
    print(f"Time: {recovery['timestamp']}")
    print(f"Actions: {recovery['actions_taken']}")
    print(f"Success: {recovery['success']}")
```

## Performance Tips

1. **Adjust monitoring interval**: Increase for lower overhead
   ```python
   engine = EnhancedResourceExhaustionEngine(monitoring_interval=5.0)
   ```

2. **Disable auto-recovery**: For detection-only mode
   ```python
   engine = EnhancedResourceExhaustionEngine(auto_recovery=False)
   ```

3. **Reset detectors**: Clear state between tests
   ```python
   engine.reset_all()
   ```

## Troubleshooting

### Issue: High false positive rate
```python
# Increase thresholds
fork_detector = ForkBombDetector(threshold_processes_per_second=20)
memory_detector = MemoryExhaustionDetector(leak_threshold_mb_per_second=20.0)
```

### Issue: Missing detections
```python
# Decrease thresholds
cpu_detector = CPUExhaustionDetector(cpu_threshold_percent=70.0)
```

### Issue: Recovery not working
```python
# Check recovery history for errors
history = engine.recovery_system.get_recovery_history()
for r in history:
    if not r['success']:
        print(f"Errors: {r['errors']}")
```

## Platform Notes

- **Windows**: Full detection, limited quota enforcement
- **Linux**: Full detection + cgroup/ulimit support
- **macOS**: Full detection + ulimit support

---

**Quick Reference v2.0.0**  
Enhanced Resource Exhaustion Engine  
Part of Sovereign Governance Substrate
