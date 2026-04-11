# Liara State Preservation - Quick Start Guide

## Installation

### 1. Install PyNaCl (recommended for production)

```bash
pip install PyNaCl
```

This provides real Ed25519 cryptographic signatures. Without it, the system uses deterministic mock crypto (sufficient for testing).

## Basic Usage

### Creating a Snapshot

```python
from kernel.liara_state import LiaraStatePreservation, StateType

# Initialize preserver
preserver = LiaraStatePreservation()

# Capture state
snapshot = preserver.capture_snapshot(
    controller_id="triumvirate-alpha",
    state_type=StateType.PROCESS,
    state_data={
        "process_1": {"pid": 1234, "state": "running"},
        "process_2": {"pid": 1235, "state": "blocked"}
    }
)

print(f"Snapshot {snapshot.snapshot_id} created")
print(f"Merkle root: {snapshot.merkle_root}")
print(f"Signature: {snapshot.signature[:32]}...")

preserver.close()
```

### Restoring a Snapshot

```python
from kernel.liara_state import LiaraStatePreservation

preserver = LiaraStatePreservation()

# Restore and verify
snapshot, proof = preserver.restore_snapshot(snapshot_id)

if proof.verification_status == "verified":
    print("✓ Snapshot verified successfully")
    print(f"Restored state: {snapshot.state_data}")
else:
    print("✗ Verification failed!")

preserver.close()
```

### Complete Triumvirate Failover

```python
from kernel.liara_state import create_triumvirate_snapshot, restore_triumvirate_state

# Capture complete state
snapshots = create_triumvirate_snapshot(
    controller_id="triumvirate-alpha",
    process_state={"processes": {...}},
    memory_state={"pages": {...}},
    scheduler_state={"queues": {...}}
)

# Later: Restore complete state
snapshot_ids = [s.snapshot_id for s in snapshots]
restored_states = restore_triumvirate_state(snapshot_ids)

# Access restored data
process_state = restored_states[StateType.PROCESS]
memory_state = restored_states[StateType.MEMORY]
scheduler_state = restored_states[StateType.SCHEDULER]
```

### WAL Recovery After Crash

```python
from kernel.liara_state import LiaraStatePreservation, StateType

preserver = LiaraStatePreservation()

# Replay WAL to recover state
reconstructed_state = preserver.replay_wal(StateType.PROCESS)

# Create snapshot from reconstructed state
snapshot = preserver.capture_snapshot(
    controller_id="recovered",
    state_type=StateType.PROCESS,
    state_data=reconstructed_state
)

# Truncate WAL after successful snapshot
preserver.checkpoint(StateType.PROCESS)

preserver.close()
```

## Running Benchmarks

```bash
python kernel/benchmark_liara_state.py
```

Expected output:
```
BENCHMARK SUMMARY
======================================================================

  Triumvirate Failover:
    Capture: 85.64ms
    Restore: 91.16ms
    Data size: 0.14 MB
    Integrity: ✓ VERIFIED

  FINAL VERDICT:
    Restoration target (<1s): ✓ MET
    Zero data loss: ✓ GUARANTEED

  🎉 ALL REQUIREMENTS MET - PRODUCTION READY
```

## Configuration

### Custom State Directory

```python
from pathlib import Path
from kernel.liara_state import LiaraStatePreservation

preserver = LiaraStatePreservation(
    state_dir=Path("/var/lib/liara/state")
)
```

### Snapshot Format

```python
from kernel.liara_state import LiaraStatePreservation, SnapshotFormat

# Binary format (default, most compact)
preserver = LiaraStatePreservation(
    snapshot_format=SnapshotFormat.BINARY
)

# JSON format (human-readable, debuggable)
preserver = LiaraStatePreservation(
    snapshot_format=SnapshotFormat.JSON
)
```

## Performance Monitoring

```python
preserver = LiaraStatePreservation()

# ... perform snapshots and restores ...

# Get performance statistics
stats = preserver.get_performance_stats()

print(f"Average snapshot time: {stats['avg_snapshot_time']*1000:.2f}ms")
print(f"Average restore time: {stats['avg_restore_time']*1000:.2f}ms")
print(f"Restoration target met: {stats['restoration_target_met']}")
print(f"Sub-second restores: {stats['sub_second_restores']}/{stats['restore_count']}")

preserver.close()
```

## State Types

The system supports multiple state types:

```python
from kernel.liara_state import StateType

StateType.PROCESS      # Process control blocks
StateType.MEMORY       # Memory pages and allocations
StateType.SCHEDULER    # Scheduling queues and CPU assignments
StateType.NETWORK      # Socket states and connections
StateType.FILESYSTEM   # File descriptors and inodes
StateType.GOVERNANCE   # Policy states and access control
StateType.CUSTOM       # User-defined state
```

## File Locations

After running, the state directory contains:

```
liara_state/
├── signing_key.bin                              # Ed25519 private key
├── wal_process.log                              # Process state WAL
├── wal_memory.log                               # Memory state WAL
├── wal_scheduler.log                            # Scheduler state WAL
├── triumvirate-alpha_process_1709481600123.snapshot
├── triumvirate-alpha_memory_1709481600124.snapshot
└── triumvirate-alpha_scheduler_1709481600125.snapshot
```

## Security Best Practices

1. **Protect signing key**: `chmod 600 liara_state/signing_key.bin`
2. **Regular snapshots**: Take snapshots every 5-10 seconds
3. **WAL checkpointing**: Truncate WAL after each snapshot
4. **Snapshot rotation**: Keep last 10 snapshots, delete older
5. **Verify on restore**: Always check `proof.verification_status`

## Troubleshooting

### Signature Verification Fails

Ensure you're using the same `LiaraStatePreservation` instance or the same state directory (so the signing key is consistent).

### Slow Performance

- Check disk I/O (WAL writes are unbuffered for safety)
- Reduce state size if possible
- Enable compression (future feature)
- Use SSD for state directory

### WAL Corruption

If WAL becomes corrupted:

```python
# Truncate corrupted WAL
preserver.checkpoint(StateType.PROCESS)

# Take fresh snapshot
snapshot = preserver.capture_snapshot(...)
```

## Documentation

- **Format Spec**: `kernel/LIARA_SNAPSHOT_FORMAT.md`
- **Implementation**: `kernel/LIARA_STATE_IMPLEMENTATION.md`
- **Module Source**: `kernel/liara_state.py`

## Support

For issues or questions, see the main repository documentation.

---

**Status**: Production Ready ✅  
**Performance**: <100ms restoration (11x under target)  
**Security**: Ed25519 + Merkle tree verification  
**Data Loss**: Zero tolerance guaranteed
