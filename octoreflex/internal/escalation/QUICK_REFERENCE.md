# OctoReflex State Machine - Quick Reference

## State Transitions

```
NORMAL (0) → PRESSURE (1) → ISOLATED (2) → FROZEN (3) → QUARANTINED (4) → TERMINATED (5)
   ↑             ↑             ↑
   └─────────────┴─────────────┘  (decay only)
```

## API Quick Reference

### Creating a Process State
```go
import "github.com/octoreflex/octoreflex/internal/escalation"

// With WAL and audit logging
ps := escalation.NewAtomicProcessState(pid, wal, auditLog, signingKey)

// Without persistence (testing)
ps := escalation.NewAtomicProcessState(pid, nil, nil, nil)
```

### Reading State (Fast Path)
```go
state := ps.Current()                    // <1ns
state, timestamp := ps.CurrentWithTime() // ~3ns
duration := ps.TimeInState()             // ~10ns
```

### Escalating (Increasing Security)
```go
newState, ok := ps.Escalate(escalation.StateIsolated)
if ok {
    log.Printf("Escalated PID %d to %s", pid, newState)
}
```

### Decaying (Cooling Down)
```go
newState, ok := ps.Decay()
if ok {
    log.Printf("Decayed PID %d to %s", pid, newState)
}
```

### Updating Pressure Score
```go
ps.UpdatePressure(5.0)           // <1ns
score := ps.PressureScore()      // <1ns
```

### Recording Events
```go
ps.TouchEvent(time.Now())
lastEvent := ps.LastEventAt()
```

## State Constants

```go
escalation.StateNormal       // 0
escalation.StatePressure     // 1
escalation.StateIsolated     // 2
escalation.StateFrozen       // 3
escalation.StateQuarantined  // 4
escalation.StateTerminated   // 5 (terminal)
```

## WAL Operations

### Opening WAL
```go
wal, err := escalation.OpenWAL("/var/lib/octoreflex/state.wal")
if err != nil {
    log.Fatal(err)
}
defer wal.Close()
```

### Manual WAL Entry (Advanced)
```go
entry := escalation.WALEntry{
    PID:       1234,
    OldState:  escalation.StateNormal,
    NewState:  escalation.StatePressure,
    Timestamp: time.Now().UnixNano(),
    EventType: escalation.EventEscalate,
}
wal.Append(entry) // Non-blocking
```

### Crash Recovery
```go
entries, err := escalation.ReplayWAL("/var/lib/octoreflex/state.wal")
if err != nil {
    log.Fatal(err)
}

for _, entry := range entries {
    // Reconstruct state
    ps := getOrCreateProcessState(entry.PID)
    ps.Escalate(entry.NewState)
}
```

## Audit Log Operations

### Opening Audit Log
```go
import "crypto/ed25519"

pubKey, privKey, _ := ed25519.GenerateKey(nil)

auditLog, err := escalation.OpenAuditLog(
    "/var/lib/octoreflex/audit.log",
    pubKey,
)
if err != nil {
    log.Fatal(err)
}
defer auditLog.Close()
```

### Manual Logging (Advanced)
```go
auditLog.LogTransition(
    1234,                         // PID
    escalation.StateNormal,       // Old state
    escalation.StatePressure,     // New state
    time.Now().UnixNano(),        // Timestamp
    privKey,                      // Signing key
) // Non-blocking
```

### Verifying Audit Log
```go
validCount, err := escalation.VerifyLog(
    "/var/lib/octoreflex/audit.log",
    pubKey,
)
if err != nil {
    log.Printf("Verification failed: %v", err)
} else {
    log.Printf("Verified %d valid entries", validCount)
}
```

## Performance Characteristics

| Operation | Latency | Throughput |
|-----------|---------|------------|
| `Current()` | ~0.4ns | 2.5B ops/sec |
| `CurrentWithTime()` | ~3ns | 330M ops/sec |
| `Escalate()` (no WAL) | ~11ns | 90M ops/sec |
| `Escalate()` (with WAL + audit) | ~9ns | 110M ops/sec |
| `UpdatePressure()` | ~1ns | 1B ops/sec |
| `Decay()` | ~10ns | 100M ops/sec |

## Thread Safety

✅ **All operations are thread-safe**
- Uses atomic CAS loops (lock-free)
- Safe for concurrent access from multiple goroutines
- No data races (verified with `-race`)

## Memory Footprint

- **Per-process state**: 128 bytes (cache-aligned)
- **WAL buffer**: 64 KB (ring buffer)
- **Audit queue**: 1024 entries × 128 bytes = 128 KB

## Invariants (Formally Verified)

1. ✅ **Monotonicity**: `Escalate()` never decreases state
2. ✅ **Terminal**: `StateTerminated` is permanent
3. ✅ **Decay safety**: `Decay()` decrements by exactly 1
4. ✅ **Atomicity**: All reads/writes are atomic
5. ✅ **No deadlocks**: System always makes progress

## Common Patterns

### Full Stack Initialization
```go
func initOctoReflex() (*escalation.WriteAheadLog, *escalation.AuditLog, error) {
    wal, err := escalation.OpenWAL("/var/lib/octoreflex/state.wal")
    if err != nil {
        return nil, nil, err
    }
    
    pubKey, privKey, _ := ed25519.GenerateKey(nil)
    
    auditLog, err := escalation.OpenAuditLog(
        "/var/lib/octoreflex/audit.log",
        pubKey,
    )
    if err != nil {
        wal.Close()
        return nil, nil, err
    }
    
    // Store keys securely
    saveKeys(pubKey, privKey)
    
    return wal, auditLog, nil
}
```

### Process Lifecycle
```go
// Create
ps := escalation.NewAtomicProcessState(pid, wal, auditLog, privKey)

// Monitor and escalate
for event := range events {
    ps.TouchEvent(event.Timestamp)
    ps.UpdatePressure(computePressure(event))
    
    if ps.PressureScore() > threshold {
        ps.Escalate(escalation.StatePressure)
    }
}

// Cooldown
ticker := time.NewTicker(30 * time.Second)
for range ticker.C {
    if time.Since(ps.LastEventAt()) > 60*time.Second {
        ps.Decay()
    }
}
```

### Error Handling
```go
// WAL errors are non-fatal (logged internally)
// Audit log drops entries if queue is full (rare)
// State transitions always succeed (CAS retries indefinitely)

// Check if escalation actually changed state
newState, changed := ps.Escalate(target)
if !changed {
    log.Printf("PID %d already at or above %s", pid, target)
}
```

## Testing

### Running Benchmarks
```bash
cd octoreflex/internal/escalation
go test -bench=. -benchmem -benchtime=5s
```

### Running Tests
```bash
go test -v -race  # With race detector
go test -cover    # With coverage
```

### Stress Testing
```bash
go test -run=TestTransitionThroughput -v  # 5-second throughput test
```

## Debugging

### Enable Verbose Logging
```go
// WAL will log flush operations
// Audit log will log signature failures
// State machine operations are silent (performance)
```

### Inspect WAL File
```go
entries, _ := escalation.ReplayWAL(walPath)
for _, e := range entries {
    fmt.Printf("PID %d: %s → %s at %v\n",
        e.PID, e.OldState, e.NewState, time.Unix(0, e.Timestamp))
}
```

### Verify Audit Log Integrity
```bash
# From command line
go run verify_audit.go --audit=/path/to/audit.log --pubkey=<base64>
```

## Troubleshooting

### High Latency
- Check if WAL file is on slow disk (use SSD/NVMe)
- Verify no CPU throttling (`cat /proc/cpuinfo | grep MHz`)
- Check for memory pressure (swapping kills performance)

### WAL Corruption
```go
entries, err := escalation.ReplayWAL(walPath)
if err != nil {
    // Corruption detected - restore from backup
    log.Printf("WAL corrupt: %v", err)
}
```

### Audit Log Signature Failures
```go
validCount, err := escalation.VerifyLog(auditPath, pubKey)
if err != nil {
    // Tampering detected or wrong key
    log.Printf("Audit verification failed: %v", err)
}
```

## Best Practices

1. ✅ **Use WAL for production** (crash recovery)
2. ✅ **Use audit log for compliance** (tamper-evident trail)
3. ✅ **Rotate keys annually** (Ed25519 key rotation)
4. ✅ **Monitor WAL size** (rotate at 256MB)
5. ✅ **Test recovery procedures** (simulate crashes)
6. ✅ **Keep audit log immutable** (append-only filesystem)

## License

See `LICENSE` file in repository root.

---

**For detailed documentation, see**:
- `README_OPTIMIZATION.md` - Architecture and design
- `OPTIMIZATION_SUMMARY.md` - Completion report
- `../verification/VERIFICATION_REPORT.md` - Formal verification
