# Clotho - Distributed Transaction Coordinator

**Named after the Greek Fate who spins the thread of life**, Clotho coordinates distributed transactions across multiple agents, ensuring ACID guarantees and orchestrating complex multi-agent workflows.

## Overview

Clotho is the distributed coordination component of the Temporal Cognition Module (The Fates). It provides:

- **Two-Phase Commit (2PC)** and **Three-Phase Commit (3PC)** protocols
- **ACID guarantees**: Atomicity, Consistency, Isolation, Durability
- **Multi-agent synchronization** across Chronos, Atropos, and other agents
- **Distributed deadlock detection** and resolution
- **Saga pattern** for long-running distributed workflows

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLOTHO                              │
│                    (Thread-Spinner)                         │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌─────────────────┐  ┌──────────────┐
│ Transaction   │  │    Deadlock     │  │    Saga      │
│ Coordinator   │  │    Detector     │  │ Orchestrator │
│  (2PC/3PC)    │  │ (Wait-for Graph)│  │(Compensation)│
└───────────────┘  └─────────────────┘  └──────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Chronos │        │ Atropos │        │ Other   │
   │ (Time)  │        │ (Fate)  │        │ Agents  │
   └─────────┘        └─────────┘        └─────────┘
```

## Components

### 1. TransactionCoordinator

Coordinates distributed transactions using 2PC or 3PC protocols.

#### Two-Phase Commit (2PC)

```
Phase 1: PREPARE
    Coordinator → Participants: PREPARE?
    Participants → Coordinator: YES/NO vote

Phase 2: COMMIT/ABORT
    If all YES → Coordinator → Participants: COMMIT
    If any NO  → Coordinator → Participants: ABORT
```

#### Three-Phase Commit (3PC)

Adds a pre-commit phase to reduce the window of uncertainty:

```
Phase 1: PREPARE
    Coordinator → Participants: PREPARE?
    Participants → Coordinator: YES/NO vote

Phase 2: PRE-COMMIT
    Coordinator → Participants: PRE-COMMIT
    (Reduces uncertainty window)

Phase 3: COMMIT
    Coordinator → Participants: COMMIT
```

### 2. DeadlockDetector

Detects and resolves distributed deadlocks using wait-for graph analysis.

**Wait-For Graph (WFG)**:
- Nodes: Transactions
- Edges: T1 → T2 means T1 is waiting for T2
- Cycle: Indicates deadlock

**Resolution Strategy**:
1. Detect cycles in WFG
2. Select victim (default: youngest transaction)
3. Abort victim and release all its locks
4. Other transactions can proceed

### 3. SagaOrchestrator

Orchestrates long-running distributed workflows using the Saga pattern.

**Saga Pattern**:
```
Forward: Step1 → Step2 → Step3 → ... → StepN
         ↓ (if fails)
Compensate: CompN ← ... ← Comp3 ← Comp2 ← Comp1
```

**Key Properties**:
- Each step has a compensating transaction
- Steps execute sequentially
- On failure, compensations execute in reverse order
- Each operation must be idempotent

## Usage

### Basic 2PC Transaction

```python
from cognition.temporal.clotho import Clotho, Participant

# Initialize Clotho
clotho = Clotho()
clotho.start()

# Define participants
def chronos_prepare(txn):
    # Validate transaction
    return True  # Vote YES

def chronos_commit(txn):
    # Commit changes
    pass

def chronos_abort(txn):
    # Rollback changes
    pass

participants = [
    Participant(
        participant_id="chronos-1",
        agent_name="chronos",
        prepare_callback=chronos_prepare,
        commit_callback=chronos_commit,
        abort_callback=chronos_abort,
    ),
]

# Execute transaction
transaction_data = {"key": "value"}
txn_id, success = clotho.execute_distributed_transaction(
    participants=participants,
    use_3pc=False,  # Use 2PC
    data=transaction_data
)

if success:
    print(f"Transaction {txn_id} committed!")
else:
    print(f"Transaction {txn_id} aborted")

clotho.stop()
```

### Three-Phase Commit

```python
# Same as 2PC, but with use_3pc=True
txn_id, success = clotho.execute_distributed_transaction(
    participants=participants,
    use_3pc=True,  # Use 3PC instead
    data=transaction_data
)
```

### Saga Workflow

```python
from cognition.temporal.clotho import SagaStep

def step1_forward():
    # Execute step 1
    print("Step 1 executed")
    return {"result": "step1_done"}

def step1_compensate():
    # Undo step 1
    print("Step 1 compensated")

def step2_forward():
    # Execute step 2
    print("Step 2 executed")
    return {"result": "step2_done"}

def step2_compensate():
    # Undo step 2
    print("Step 2 compensated")

steps = [
    SagaStep(
        step_id="step1",
        name="Initialize",
        forward_action=step1_forward,
        compensate_action=step1_compensate,
        agent_name="chronos",
    ),
    SagaStep(
        step_id="step2",
        name="Execute",
        forward_action=step2_forward,
        compensate_action=step2_compensate,
        agent_name="atropos",
    ),
]

saga_id, success = clotho.execute_saga("My Workflow", steps)

if success:
    print(f"Saga {saga_id} completed!")
else:
    print(f"Saga {saga_id} compensated")
```

### Deadlock Detection

```python
# Acquire locks (built into transaction coordinator)
detector = clotho.deadlock_detector

# Acquire locks
detector.acquire_lock("resource_a", "txn1", "participant1")
detector.acquire_lock("resource_b", "txn2", "participant2")

# Create circular wait (deadlock)
detector.acquire_lock("resource_b", "txn1", "participant1")  # Wait
detector.acquire_lock("resource_a", "txn2", "participant2")  # Deadlock!

# Detect cycle
cycle = detector.detect_cycle()
if cycle:
    print(f"Deadlock detected: {cycle}")
    
    # Resolve by aborting victim
    victim = detector.resolve_deadlock(cycle)
    print(f"Aborted victim: {victim}")
```

## Multi-Agent Integration

### Example: Coordinating Chronos and Atropos

```python
class ChronosAgent:
    def __init__(self):
        self.temporal_weight = 0
        
    def prepare_update(self, txn):
        new_weight = txn.data.get("weight")
        if new_weight < 0:
            return False  # Vote NO
        return True  # Vote YES
        
    def commit_update(self, txn):
        self.temporal_weight = txn.data.get("weight")
        
    def abort_update(self, txn):
        # Rollback to previous state
        pass

class AtroposAgent:
    def __init__(self):
        self.fate_chain = []
        
    def prepare_record(self, txn):
        event = txn.data.get("event")
        if not event:
            return False
        return True
        
    def commit_record(self, txn):
        event = txn.data.get("event")
        self.fate_chain.append(event)
        
    def abort_record(self, txn):
        # Rollback
        pass

# Create agents
chronos = ChronosAgent()
atropos = AtroposAgent()

# Create participants
participants = [
    Participant(
        participant_id="chronos-1",
        agent_name="chronos",
        prepare_callback=chronos.prepare_update,
        commit_callback=chronos.commit_update,
        abort_callback=chronos.abort_update,
    ),
    Participant(
        participant_id="atropos-1",
        agent_name="atropos",
        prepare_callback=atropos.prepare_record,
        commit_callback=atropos.commit_record,
        abort_callback=atropos.abort_record,
    ),
]

# Execute distributed transaction
txn_data = {
    "weight": 42,
    "event": "temporal_sync"
}

txn_id, success = clotho.execute_distributed_transaction(
    participants=participants,
    data=txn_data
)

print(f"Chronos weight: {chronos.temporal_weight}")
print(f"Atropos chain: {atropos.fate_chain}")
```

## Statistics and Monitoring

```python
# Get comprehensive statistics
stats = clotho.get_statistics()

print(f"Coordinator ID: {stats['coordinator_id']}")
print(f"Uptime: {stats['uptime_seconds']} seconds")
print(f"Transactions: {stats['transactions']}")
print(f"Sagas: {stats['sagas']}")
print(f"Deadlocks: {stats['deadlocks']}")

# Health check
health = clotho.health_check()
print(f"Status: {health['status']}")
print(f"Components: {health['components']}")
```

## Security Invariants

### INV-CLOTHO-1: Consensus Required
All distributed transactions must achieve consensus among participants. No partial commits allowed.

### INV-CLOTHO-2: Complete Rollback
Failed transactions must be completely rolled back. No orphaned state.

### INV-CLOTHO-3: Deadlock Detection
Deadlocks must be detected within timeout threshold (default: 1 second).

### INV-CLOTHO-4: Idempotent Compensation
Saga compensations must be idempotent to handle retries safely.

## Best Practices

### 1. Use 3PC for Critical Transactions
3PC reduces the window of uncertainty and is more resilient to coordinator failures.

```python
txn_id, success = clotho.execute_distributed_transaction(
    participants=participants,
    use_3pc=True,  # More resilient
    timeout=120.0,  # Longer timeout for critical ops
)
```

### 2. Implement Proper Rollback
Always implement abort callbacks to ensure clean rollback:

```python
class MyAgent:
    def __init__(self):
        self.state = {}
        self._snapshots = {}
        
    def prepare(self, txn):
        # Save snapshot before committing
        self._snapshots[txn.transaction_id] = self.state.copy()
        return True
        
    def commit(self, txn):
        # Apply changes
        self.state.update(txn.data)
        del self._snapshots[txn.transaction_id]
        
    def abort(self, txn):
        # Restore from snapshot
        if txn.transaction_id in self._snapshots:
            self.state = self._snapshots[txn.transaction_id]
            del self._snapshots[txn.transaction_id]
```

### 3. Use Sagas for Long-Running Operations
For workflows that take minutes/hours, use Sagas instead of 2PC/3PC:

```python
# Good: Saga for long-running workflow
saga_id, success = clotho.execute_saga("ETL Pipeline", long_running_steps)

# Bad: 2PC for long operation (will timeout)
# txn_id, success = clotho.execute_distributed_transaction(...)
```

### 4. Monitor Deadlocks
Regularly check for deadlocks in production:

```python
deadlocks = clotho.deadlock_detector.get_deadlocks()
if deadlocks:
    logger.warning(f"Deadlocks detected: {deadlocks}")
    # Alert operations team
```

### 5. Set Appropriate Timeouts
Configure timeouts based on operation characteristics:

```python
# Fast operation
txn_id, success = clotho.execute_distributed_transaction(
    participants=participants,
    timeout=30.0  # 30 seconds
)

# Slow operation
txn_id, success = clotho.execute_distributed_transaction(
    participants=participants,
    timeout=300.0  # 5 minutes
)
```

## Error Handling

### Transaction Failures

```python
txn_id, success = clotho.execute_distributed_transaction(participants)

if not success:
    txn = clotho.transaction_coordinator.get_transaction(txn_id)
    
    if txn.status == TransactionStatus.TIMEOUT:
        print("Transaction timed out")
    elif txn.status == TransactionStatus.ABORTED:
        print(f"Transaction aborted: {txn.error}")
    elif txn.status == TransactionStatus.FAILED:
        print(f"Transaction failed: {txn.error}")
    
    # Check logs for details
    for log_entry in txn.logs:
        print(log_entry)
```

### Saga Failures

```python
saga_id, success = clotho.execute_saga("Workflow", steps)

if not success:
    saga = clotho.saga_orchestrator.get_saga(saga_id)
    
    if saga.status == SagaStatus.COMPENSATED:
        print("Saga compensated successfully")
    elif saga.status == SagaStatus.FAILED:
        print("Saga and compensation failed!")
        # Alert ops team - manual intervention needed
```

## Performance Considerations

### 1. Minimize Participants
Fewer participants = faster consensus:

```python
# Good: Only necessary participants
participants = [chronos, atropos]

# Bad: Unnecessary participants slow down consensus
participants = [chronos, atropos, unnecessary1, unnecessary2, ...]
```

### 2. Batch Operations
Group related operations into single transaction:

```python
# Good: Batch update
transaction_data = {
    "chronos_updates": [...],
    "atropos_updates": [...],
}

# Bad: Multiple transactions
for update in updates:
    clotho.execute_distributed_transaction(...)  # N transactions
```

### 3. Use Shared Locks When Possible
Shared locks allow concurrent reads:

```python
# Read-only operations can use shared locks
detector.acquire_lock(resource_id, txn_id, participant_id, lock_type="shared")
```

## Testing

Run the test suite:

```bash
pytest src/cognition/temporal/test_clotho.py -v
```

Run examples:

```bash
python src/cognition/temporal/clotho_example.py
```

## Production Deployment

### Persistence
In production, persist transaction logs to durable storage:

```python
# Production: Use persistent storage
class PersistentTransactionCoordinator(TransactionCoordinator):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        
    def begin_transaction(self, participants, **kwargs):
        txn_id = super().begin_transaction(participants, **kwargs)
        # Persist to database
        self.db.save_transaction(self.transactions[txn_id])
        return txn_id
```

### Distributed Consensus
Use distributed consensus protocols (Raft, Paxos) for coordinator HA:

```python
# Production: Distributed coordinator
class RaftCoordinator(TransactionCoordinator):
    def __init__(self, raft_cluster):
        super().__init__()
        self.raft = raft_cluster
```

### Monitoring
Integrate with monitoring systems:

```python
# Production: Metrics export
from prometheus_client import Counter, Histogram

txn_commits = Counter('clotho_transactions_committed', 'Committed transactions')
txn_aborts = Counter('clotho_transactions_aborted', 'Aborted transactions')
txn_duration = Histogram('clotho_transaction_duration', 'Transaction duration')
```

## See Also

- [Chronos](chronos.md) - Temporal weight engine
- [Atropos](atropos.md) - Fate engine with anti-rollback protection
- [Temporal Cognition Module](README.md) - The Fates overview

## References

- **Two-Phase Commit**: Gray, J. (1978). "Notes on Data Base Operating Systems"
- **Three-Phase Commit**: Skeen, D. (1981). "Nonblocking Commit Protocols"
- **Saga Pattern**: Garcia-Molina, H. & Salem, K. (1987). "Sagas"
- **Deadlock Detection**: Knapp, E. (1987). "Deadlock Detection in Distributed Databases"
