# Enhanced STATE_REGISTER - Distributed Synchronization

## Overview

The Enhanced STATE_REGISTER provides a distributed, causally-consistent state management system with cryptographic audit trails. It implements a conflict-free replicated data type (CRDT) with vector clock-based causality tracking and Merkle tree anchoring.

## Features

### 1. Distributed Multi-Node Synchronization
- **Anti-Entropy Gossip Protocol**: Nodes periodically exchange state to ensure eventual consistency
- **Peer Discovery**: Automatic peer awareness and management
- **Bidirectional Sync**: Full state synchronization between any pair of nodes
- **Partition Tolerance**: Handles network partitions and heals automatically

### 2. Vector Clock Integration
- **Causal Ordering**: Precise tracking of happens-before relationships
- **Lamport Timestamps**: Logical time tracking per node
- **Concurrent Detection**: Identifies truly concurrent (non-causal) updates
- **Clock Merging**: Efficient vector clock synchronization

### 3. Causal Consistency Verification
- **Happens-Before Proofs**: Verifiable causal relationships between operations
- **Hash Chain Integrity**: Cryptographic verification of operation ordering
- **Consistency Checks**: Automated detection of causality violations
- **Vector Clock Monotonicity**: Ensures logical time never goes backward

### 4. Audit Trail Anchoring
- **Merkle Tree Checkpoints**: Periodic state snapshots with cryptographic proofs
- **Temporal Audit Ledger Integration**: All state changes logged immutably
- **Hash Chain Linking**: Each state version cryptographically linked to previous
- **Non-Repudiation**: Ed25519 signatures on audit entries

### 5. Deterministic Conflict Resolution
- **LWW-Vector-Clock**: Last-writer-wins using vector clock ordering + node ID tiebreaker
- **LWW-Timestamp**: Last-writer-wins using wall-clock timestamps
- **MAX_VALUE**: Choose maximum value (useful for counters)
- **MIN_VALUE**: Choose minimum value (useful for rate limits)
- **Custom Strategies**: Extensible conflict resolution framework

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Distributed State Register                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Node 1     │  │   Node 2     │  │   Node 3     │    │
│  │              │  │              │  │              │    │
│  │  State +     │◄─┤  State +     │◄─┤  State +     │    │
│  │  VectorClock │──┤  VectorClock │──┤  VectorClock │    │
│  │              │  │              │  │              │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │             │
│         └─────────────────┴─────────────────┘             │
│                           │                               │
│                           ▼                               │
│              ┌─────────────────────────┐                  │
│              │  Temporal Audit Ledger  │                  │
│              │  • Hash Chains          │                  │
│              │  • Merkle Trees         │                  │
│              │  • Ed25519 Signatures   │                  │
│              │  • RFC 3161 Timestamps  │                  │
│              └─────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### StateValue
Each state value is a versioned, causally-tracked object:

```python
StateValue {
    key: str                    # Unique key
    value: Any                  # Actual value
    value_type: StateValueType  # Type information
    version: int                # Monotonic version number
    vector_clock: VectorClock   # Causal timestamp
    node_id: str                # Originating node
    timestamp: datetime         # Wall-clock time
    prev_hash: str              # Hash of previous version
    merkle_root: str            # Checkpoint Merkle root
    metadata: dict              # Extensible metadata
}
```

### Vector Clock
Causality tracking using Lamport vector clocks:

```python
VectorClock {
    process_id: str
    clock: Dict[str, int]  # Map of node_id -> logical_time
}
```

## API Reference

### Creating a State Register

```python
from pathlib import Path
from governance.state_register_enhanced import (
    DistributedStateRegister,
    StateValueType,
    ConflictResolutionStrategy,
)
from governance.temporal_audit_ledger import TemporalAuditLedger

# Create audit ledger
audit_ledger = TemporalAuditLedger(Path("audit.json"))

# Create state register
state_register = DistributedStateRegister(
    node_id="node1",
    storage_path=Path("state_node1.json"),
    audit_ledger=audit_ledger,
    conflict_strategy=ConflictResolutionStrategy.LWW_VECTOR_CLOCK,
    checkpoint_interval=100,  # Checkpoint every 100 operations
    sync_interval_seconds=30.0,
)
```

### Basic Operations

```python
# Store a value
state_value = state_register.put(
    key="config.timeout",
    value=30,
    value_type=StateValueType.INTEGER,
    metadata={"description": "API timeout in seconds"}
)

# Retrieve current value
current = state_register.get("config.timeout")
print(f"Current value: {current.value}, version: {current.version}")

# Retrieve specific version
v1 = state_register.get_version("config.timeout", version=1)

# Delete (creates tombstone)
state_register.delete("config.timeout")
```

### Synchronization

```python
# Create sync message
sync_msg = state_register.create_sync_message()

# Send to peer (via network, queue, etc.)
# ... network transmission ...

# Process incoming sync message
updated_keys = peer_register.process_sync_message(sync_msg)
print(f"Updated keys: {updated_keys}")
```

### Cluster Management

```python
from governance.state_register_enhanced import DistributedStateRegisterCluster

# Create cluster
cluster = DistributedStateRegisterCluster(audit_ledger)

# Add nodes
cluster.add_node(node1)
cluster.add_node(node2)
cluster.add_node(node3)

# Perform gossip round (syncs all pairs)
updates = cluster.gossip_round()

# Verify cluster consistency
is_consistent, violations = cluster.verify_cluster_consistency()
```

### Causal Consistency

```python
# Verify happens-before relationship
result = state_register.verify_happens_before("key1", "key2")
# Returns:
#   True if key1 -> key2 (key1 happens before key2)
#   False if key2 -> key1
#   None if concurrent or keys don't exist

# Verify overall consistency
is_consistent, violations = state_register.verify_causal_consistency()
if not is_consistent:
    for violation in violations:
        print(f"Violation: {violation}")
```

### Statistics

```python
stats = state_register.get_statistics()
print(f"Operations: {stats['operation_count']}")
print(f"Syncs: {stats['sync_count']}")
print(f"Conflicts: {stats['conflict_count']}")
print(f"Checkpoints: {stats['checkpoint_count']}")
```

## Conflict Resolution Strategies

### LWW-Vector-Clock (Recommended)
Uses vector clock comparison with node ID as tiebreaker:
- If clocks show happens-before, choose the later one
- If concurrent, choose the one from lexicographically larger node ID
- Deterministic and partition-tolerant

```python
conflict_strategy=ConflictResolutionStrategy.LWW_VECTOR_CLOCK
```

### LWW-Timestamp
Uses wall-clock timestamps:
- Simpler but susceptible to clock skew
- Useful when wall-clock time is trusted

```python
conflict_strategy=ConflictResolutionStrategy.LWW_TIMESTAMP
```

### MAX_VALUE / MIN_VALUE
Choose maximum or minimum value:
- Useful for counters, priorities, or monotonic values
- Falls back to timestamp for non-comparable values

```python
conflict_strategy=ConflictResolutionStrategy.MAX_VALUE
# or
conflict_strategy=ConflictResolutionStrategy.MIN_VALUE
```

## Causal Consistency Guarantees

The system provides **causal consistency** with the following guarantees:

1. **Happens-Before Preservation**: If operation A happens before operation B on any node, all nodes will see A before B
2. **Read-Your-Writes**: A node always sees its own writes
3. **Monotonic Reads**: Once a node observes a value version, it never sees an older version
4. **Monotonic Writes**: A node's writes are ordered by its local vector clock

### Verification

The system can prove causality violations:

```python
# Hash chain verification
for key in state_register.history:
    for i in range(1, len(state_register.history[key])):
        prev = state_register.history[key][i-1]
        curr = state_register.history[key][i]
        assert curr.prev_hash == prev.compute_hash()

# Vector clock monotonicity
for key in state_register.history:
    for i in range(1, len(state_register.history[key])):
        prev = state_register.history[key][i-1]
        curr = state_register.history[key][i]
        assert prev.vector_clock.happens_before(curr.vector_clock)
```

## Audit Trail Integration

All state changes are logged to the Temporal Audit Ledger:

```python
# Every put/delete/sync creates audit entry
state_register.put("key", "value", StateValueType.STRING)

# View audit log
for entry in audit_ledger.entries:
    if entry.resource.startswith("state:"):
        print(f"{entry.action} on {entry.resource}")
        print(f"  Hash: {entry.entry_hash}")
        print(f"  Metadata: {entry.metadata}")
```

### Merkle Tree Checkpointing

Periodic checkpoints create Merkle roots:

```python
# Checkpoints are automatic based on operation count
# To force checkpoint:
state_register._create_checkpoint()

# View checkpoints
for seq, merkle_root in state_register.checkpoints:
    print(f"Checkpoint at operation {seq}: {merkle_root}")
```

## Security Considerations

1. **Cryptographic Integrity**: All state changes form hash chains
2. **Non-Repudiation**: Audit entries are Ed25519 signed
3. **Tamper Detection**: Instant detection via hash verification
4. **External Timestamping**: RFC 3161 timestamps for legal compliance
5. **Merkle Proofs**: Efficient verification of large state

## Performance Characteristics

- **Write Latency**: O(1) local writes
- **Sync Latency**: O(n) where n = number of state keys
- **Space**: O(k × v) where k = keys, v = average versions kept
- **Checkpoint**: O(k log k) for Merkle tree construction
- **Consistency Check**: O(k × v) for full verification

## Use Cases

1. **Distributed Configuration Management**
   - Multi-datacenter config sync
   - Feature flag coordination
   - Service discovery state

2. **Collaborative State**
   - Shared session state
   - Distributed caches
   - Multi-writer databases

3. **Compliance and Auditing**
   - Regulatory compliance tracking
   - Change management
   - Forensic investigation

4. **Event Sourcing**
   - Command and event log
   - Causal event ordering
   - Temporal queries

## Testing

Run the test suite:

```bash
pytest tests/test_state_register_enhanced.py -v
```

Run the demonstration:

```bash
python governance/demo_state_register_enhanced.py
```

## Example: Multi-Node Deployment

```python
# Node 1 (Primary datacenter)
node1 = DistributedStateRegister(
    node_id="dc1-node1",
    storage_path=Path("/var/state/node1.json"),
    audit_ledger=audit_ledger,
)

# Node 2 (Backup datacenter)
node2 = DistributedStateRegister(
    node_id="dc2-node1",
    storage_path=Path("/var/state/node2.json"),
    audit_ledger=audit_ledger,
)

# Periodic sync (e.g., every 30 seconds)
def sync_loop():
    while True:
        msg1 = node1.create_sync_message()
        msg2 = node2.create_sync_message()
        
        node2.process_sync_message(msg1)
        node1.process_sync_message(msg2)
        
        time.sleep(30)

# In production, run sync_loop in background thread/process
```

## Future Enhancements

- [ ] Network transport layer (gRPC, HTTP/2)
- [ ] Automatic peer discovery (mDNS, Consul)
- [ ] Compaction and garbage collection
- [ ] Read-only replicas
- [ ] Quorum-based writes
- [ ] Snapshot isolation for reads
- [ ] Time-travel queries

## References

1. **Vector Clocks**: Lamport, L. (1978). "Time, clocks, and the ordering of events"
2. **CRDTs**: Shapiro, M. et al. (2011). "Conflict-free Replicated Data Types"
3. **Merkle Trees**: Merkle, R. (1988). "A Digital Signature Based on a Conventional Encryption Function"
4. **Gossip Protocols**: Demers, A. et al. (1987). "Epidemic algorithms for replicated database maintenance"

## License

Part of the Sovereign Governance Substrate - See LICENSE file.

## Support

For issues, questions, or contributions, see the main repository documentation.
