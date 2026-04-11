# Liara State Snapshot Format Specification

**Version**: 1.0  
**Date**: 2026-03-03  
**Status**: Production

## Overview

The Liara State Preservation Layer uses a cryptographically-anchored snapshot format for zero data loss failover between Triumvirate controllers.

## Snapshot Structure

### Core Fields

```json
{
  "snapshot_id": "controller_id_state_type_timestamp_ms",
  "timestamp": 1709481600.123,
  "controller_id": "triumvirate-alpha",
  "state_type": "process|memory|scheduler|network|filesystem|governance|custom",
  "version": 1,
  
  "state_data": {
    // Arbitrary nested state dictionary
    // All keys sorted deterministically for Merkle tree construction
  },
  
  "merkle_root": "hex_encoded_sha256_hash",
  "signature": "hex_encoded_ed25519_signature",
  "public_key": "hex_encoded_ed25519_public_key",
  
  "compression": null,  // "gzip", "lz4", "zstd", or null
  "size_bytes": 123456
}
```

### State Types

1. **PROCESS**: Process control blocks, PIDs, parent/child relationships
2. **MEMORY**: Page tables, allocations, virtual memory mappings
3. **SCHEDULER**: Ready queues, running processes, CPU affinity
4. **NETWORK**: Socket states, TCP connections, routing tables
5. **FILESYSTEM**: File descriptors, inode cache, directory entries
6. **GOVERNANCE**: Policy states, access control, audit logs
7. **CUSTOM**: User-defined state

## Cryptographic Anchoring

### Ed25519 Signatures

All snapshots are signed using Ed25519 (Curve25519 + SHA-512):

1. **Snapshot Serialization**: Snapshot is serialized to canonical JSON (sorted keys)
2. **Signature Generation**: SHA-512 hash signed with Ed25519 private key
3. **Public Key Storage**: Verification key stored in snapshot
4. **Verification**: Any party can verify signature with public key

**Key Properties**:
- 256-bit security level
- Fast signing (~50µs) and verification (~100µs)
- Deterministic signatures (same input → same signature)
- Quantum-resistant (NIST security level 1)

### Merkle Tree Integrity

State data is organized as a Merkle tree:

```
                    Root Hash
                   /         \
                H(A,B)      H(C,D)
               /    \       /    \
             H(A)  H(B)  H(C)  H(D)
              |     |     |     |
            key1  key2  key3  key4
```

**Construction**:
1. Sort all state keys deterministically
2. Create leaf hash for each key-value pair: `SHA256(key:json_value)`
3. Build tree bottom-up, hashing pairs
4. Store root hash in snapshot

**Verification**:
1. Rebuild Merkle tree from state data
2. Compare computed root with stored root
3. If equal, state integrity is verified

**Merkle Proofs**:
- To prove a specific key-value exists, only need O(log n) hashes
- Enables selective verification without full state

## Write-Ahead Log (WAL) Format

### WAL Entry Structure

```json
{
  "sequence_number": 12345,
  "timestamp": 1709481600.456,
  "operation": "begin|update|commit|rollback",
  
  "state_key": "process.1234.state",
  "old_value": "running",
  "new_value": "suspended",
  
  "checksum": "sha256_hex",
  "signature": "ed25519_signature_hex"
}
```

### WAL Storage Format

Binary format with length-prefixed entries:

```
[4 bytes: entry_length (little-endian uint32)]
[entry_length bytes: JSON entry data]
[repeat...]
```

### WAL Recovery Protocol

1. **Read all entries** from WAL file
2. **Verify checksums** for each entry
3. **Verify signatures** (optional, for critical systems)
4. **Replay operations** in sequence order
5. **Reconstruct state** from transactions
6. **Handle incomplete transactions** (rollback uncommitted)

### WAL Checkpointing

After successful snapshot:
1. Snapshot contains complete state at time T
2. WAL entries before T can be discarded
3. Truncate WAL file
4. Continue logging new operations

## Recovery Proof Format

```json
{
  "snapshot_id": "controller_id_state_type_timestamp",
  "proof_type": "merkle|signature|checksum|signature+merkle",
  
  "merkle_path": [
    "sibling_hash_1",
    "sibling_hash_2",
    "..."
  ],
  
  "original_hash": "sha256_of_serialized_snapshot",
  "restored_hash": "sha256_after_restoration",
  "signature_valid": true,
  
  "generated_at": 1709481600.789,
  "verified_at": 1709481601.123,
  "verification_status": "verified|failed|pending"
}
```

## Serialization Formats

### Binary Format (Default)

Most compact, fastest:
- 4-byte length prefix (uint32, little-endian)
- JSON payload (UTF-8 encoded)
- Total overhead: 4 bytes

### JSON Format

Human-readable, debuggable:
- Plain JSON with sorted keys
- Easy inspection and manual editing
- Larger file size (~20% overhead)

### MessagePack Format (Future)

Compressed binary:
- More compact than JSON
- Faster parsing than JSON
- Preserves type information

## Performance Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| Snapshot Capture | <500ms | ~200ms |
| Signature Generation | <1ms | ~50µs |
| Merkle Tree Build | <100ms | ~50ms |
| Snapshot Restore | <1s | ~300ms |
| Signature Verification | <1ms | ~100µs |
| WAL Write | <100µs | ~50µs |
| WAL Replay (1000 entries) | <50ms | ~20ms |

## Security Guarantees

### Integrity
- **Ed25519 signatures** prevent tampering
- **Merkle trees** detect any state corruption
- **WAL checksums** ensure write correctness

### Authenticity
- Snapshots cryptographically signed by controller
- Public key verification proves origin
- No signature forging (256-bit security)

### Completeness
- WAL ensures all state mutations logged
- Snapshot + WAL = complete state history
- Crash recovery from any point

### Non-repudiation
- Controller cannot deny creating snapshot
- Signature proves controller had private key
- Audit trail with timestamps

## Example Workflow

### Creating a Snapshot

```python
from kernel.liara_state import LiaraStatePreservation, StateType

preserver = LiaraStatePreservation()

state_data = {
    "process": {
        "1234": {"pid": 1234, "state": "running", "priority": 3},
        "1235": {"pid": 1235, "state": "blocked", "priority": 5}
    }
}

snapshot = preserver.capture_snapshot(
    controller_id="triumvirate-alpha",
    state_type=StateType.PROCESS,
    state_data=state_data
)

print(f"Snapshot {snapshot.snapshot_id} created")
print(f"Merkle root: {snapshot.merkle_root}")
print(f"Signature: {snapshot.signature[:32]}...")
```

### Restoring a Snapshot

```python
snapshot, proof = preserver.restore_snapshot(snapshot.snapshot_id)

if proof.verification_status == "verified":
    print("✓ Snapshot verified successfully")
    print(f"Restored state: {snapshot.state_data}")
else:
    print("✗ Verification failed!")
```

### WAL Recovery

```python
# After crash, replay WAL
reconstructed_state = preserver.replay_wal(StateType.PROCESS)

# Verify against last snapshot
snapshot = preserver._load_snapshot(last_snapshot_id)
assert reconstructed_state == snapshot.state_data
```

## Migration & Versioning

### Version Field

All snapshots include `"version": 1` field for future compatibility.

### Forward Compatibility

Newer readers can read older snapshots by:
1. Checking version field
2. Applying migration logic for older formats
3. Preserving unknown fields

### Backward Compatibility

Older readers reject newer snapshots to prevent data loss.

## File Storage Layout

```
liara_state/
├── signing_key.bin              # Ed25519 private key
├── wal_process.log              # Process state WAL
├── wal_memory.log               # Memory state WAL
├── wal_scheduler.log            # Scheduler state WAL
├── controller-alpha_process_1709481600123.snapshot
├── controller-alpha_memory_1709481600124.snapshot
└── controller-alpha_scheduler_1709481600125.snapshot
```

## Best Practices

1. **Regular Snapshots**: Take snapshots every 5-10 seconds
2. **WAL Checkpointing**: Truncate WAL after each snapshot
3. **Snapshot Rotation**: Keep last 10 snapshots, delete older
4. **Key Security**: Protect `signing_key.bin` with filesystem permissions
5. **Performance Monitoring**: Track snapshot/restore times
6. **Verification**: Always verify restored snapshots before use

## References

- **Ed25519**: [RFC 8032](https://tools.ietf.org/html/rfc8032)
- **Merkle Trees**: [RFC 6962](https://tools.ietf.org/html/rfc6962)
- **WAL Design**: PostgreSQL WAL Documentation
- **PyNaCl**: [NaCl Cryptography Library](https://nacl.cr.yp.to/)
