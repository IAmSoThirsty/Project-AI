# Temporal Consensus Protocol

## Overview

This module implements a comprehensive distributed consensus protocol for temporal agents (Chronos, Atropos, and Clotho) in the Sovereign Governance Substrate. The protocol ensures that all agents reach agreement on event ordering even in the presence of network delays, concurrent events, and Byzantine failures.

## Quick Start

All consensus components are available through the temporal module:

```python
from src.cognition.temporal import (
    # Lamport timestamps for total ordering
    LamportClockNew,
    LamportTimestamp,
    
    # Consensus protocol components
    EventRecord,
    EventType,
    ConflictResolver,
    ConsensusProtocol,
    BFTConsensus,
    
    # Vector clocks for partial ordering
    VectorClockImpl,
)
```

## Components

### 1. Vector Clocks (`vector_clock.py`)

Vector clocks provide **partial ordering** of events across distributed agents.

**Key Features:**
- Track causal relationships between events
- Detect concurrent events
- Implement Fidge-Mattern algorithm
- Support happens-before (→) relation

**Example:**
```python
from src.cognition.temporal import VectorClockImpl as VectorClock

chronos = VectorClock("chronos")
atropos = VectorClock("atropos")

# Chronos performs local event
chronos.tick()

# Chronos sends to Atropos
message_clock = chronos.copy()

# Atropos receives and updates
atropos.merge(message_clock)

# Check causality
assert message_clock.happens_before(atropos)  # message → atropos
```

**Properties:**
- **Reflexive**: VC ≤ VC
- **Anti-symmetric**: VC1 ≤ VC2 ∧ VC2 ≤ VC1 → VC1 = VC2
- **Transitive**: VC1 ≤ VC2 ∧ VC2 ≤ VC3 → VC1 ≤ VC3

### 2. Lamport Timestamps (`lamport.py`)

Lamport timestamps provide **total ordering** of all events.

**Key Features:**
- Simple logical clock
- Total order via (counter, agent_id) tuples
- Deterministic tiebreaking
- Lower overhead than vector clocks

**Example:**
```python
from src.cognition.temporal import LamportClockNew, LamportTimestamp

chronos = LamportClockNew("chronos")
atropos = LamportClockNew("atropos")

# Chronos event
ts1 = chronos.tick()  # L(1, chronos)

# Atropos receives and updates
ts2 = atropos.update(ts1)  # L(2, atropos)

# Total ordering
assert ts1 < ts2
```

**Ordering Rule:**
```
(t1, a1) < (t2, a2) ⟺ t1 < t2 ∨ (t1 = t2 ∧ a1 < a2)
```

### 3. Consensus Protocol (`consensus.py`)

Main consensus protocol coordinating vector clocks and Lamport timestamps.

**Key Features:**
- Event recording with dual timestamps
- Message preparation and receipt
- Causal history tracking
- Consistency verification
- Event linearization

**Example:**
```python
from src.cognition.temporal import ConsensusProtocol, EventType

chronos = ConsensusProtocol("chronos", ["atropos", "clotho"])
atropos = ConsensusProtocol("atropos", ["chronos", "clotho"])

# Chronos records local event
event = chronos.record_local_event(
    EventType.STATE_TRANSITION,
    {"state": "active"}
)

# Chronos sends message
msg = chronos.prepare_message(
    EventType.MESSAGE_SEND,
    {"to": "atropos", "data": "proposal"}
)

# Atropos receives
atropos.receive_message(msg)

# Verify consistency
is_consistent, violations = chronos.verify_consistency()
assert is_consistent
```

**Event Types:**
- `STATE_TRANSITION` - Local state changes
- `MESSAGE_SEND` - Outgoing messages
- `MESSAGE_RECEIVE` - Incoming messages
- `PROPOSAL` - Consensus proposals
- `VOTE` - Voting on proposals
- `DECISION` - Final decisions

### 4. Conflict Resolution

Deterministic resolution of concurrent events using hybrid approach:

1. **Causal ordering first** (vector clocks)
   - If e1 → e2, then e1 < e2
   - If e2 → e1, then e2 < e1

2. **Lamport timestamps for concurrent events**
   - If e1 ∥ e2 (concurrent), use Lamport comparison
   - Ensures total order even for concurrent events

**Example:**
```python
from src.cognition.temporal import ConflictResolver

resolver = ConflictResolver()

# Two concurrent events
result = resolver.resolve(event1, event2)
# -1: event1 < event2
#  0: event1 = event2
#  1: event1 > event2

# Linearize event set
ordered_events = resolver.linearize([e1, e2, e3, ...])
```

### 5. Byzantine Fault Tolerance (`BFTConsensus`)

Implements PBFT-style consensus tolerating up to f < n/3 Byzantine failures.

**Key Features:**
- Quorum-based voting (2f + 1 votes required)
- Cryptographic signatures on events
- Proposal and voting phases
- Commitment tracking

**Example:**
```python
from src.cognition.temporal import BFTConsensus

agents = ["chronos", "atropos", "clotho", "lachesis"]

# Create BFT consensus for each agent
bft = BFTConsensus("chronos", agents)

# n=4 agents: f=(4-1)//3 = 1
# Can tolerate 1 Byzantine failure
# Quorum = 2*1 + 1 = 3 votes

# Propose event
bft.propose(event)

# Others vote
bft_atropos.vote(event)
bft_clotho.vote(event)
bft_lachesis.vote(event)

# Check commitment
assert bft.is_committed(event.event_id)
```

**Fault Tolerance:**
| Agents (n) | Max Byzantine (f) | Quorum Size |
|------------|-------------------|-------------|
| 3          | 0                 | 1           |
| 4          | 1                 | 3           |
| 7          | 2                 | 5           |
| 10         | 3                 | 7           |

## Usage Patterns

### Basic Consensus Flow

```python
from src.cognition.temporal import (
    ConsensusProtocol,
    BFTConsensus,
    EventType,
)

# Setup agents
agents = ["chronos", "atropos", "clotho"]
protocols = {
    agent_id: ConsensusProtocol(agent_id, [a for a in agents if a != agent_id])
    for agent_id in agents
}
bft_nodes = {
    agent_id: BFTConsensus(agent_id, agents)
    for agent_id in agents
}

# 1. Propose
proposal = protocols["chronos"].prepare_message(
    EventType.PROPOSAL,
    {"action": "activate_protocol", "version": "2.0"}
)
bft_nodes["chronos"].propose(proposal)

# 2. Distribute to peers
protocols["atropos"].receive_message(proposal)
protocols["clotho"].receive_message(proposal)

# 3. Vote
for agent_id in ["atropos", "clotho"]:
    vote = protocols[agent_id].prepare_message(
        EventType.VOTE,
        {"proposal_id": proposal.event_id, "vote": "approve"}
    )
    bft_nodes[agent_id].vote(proposal)
    
    # Distribute vote
    for peer_id in agents:
        if peer_id != agent_id:
            protocols[peer_id].receive_message(vote)

# 4. Check commitment
for agent_id in agents:
    assert bft_nodes[agent_id].is_committed(proposal.event_id)

# 5. Verify consistency
for agent_id in agents:
    is_consistent, _ = protocols[agent_id].verify_consistency()
    assert is_consistent
```

### Handling Concurrent Updates

```python
from src.cognition.temporal import (
    ConsensusProtocol,
    ConflictResolver,
    EventType,
)

# Two agents make concurrent updates
chronos = ConsensusProtocol("chronos")
atropos = ConsensusProtocol("atropos")

# Concurrent events
e1 = chronos.record_local_event(
    EventType.STATE_TRANSITION,
    {"resource": "lock_A", "owner": "chronos"}
)
e2 = atropos.record_local_event(
    EventType.STATE_TRANSITION,
    {"resource": "lock_A", "owner": "atropos"}
)

# Resolve deterministically
resolver = ConflictResolver()
if resolver.resolve(e1, e2) < 0:
    winner = e1
else:
    winner = e2

print(f"Winner: {winner.agent_id}")  # Deterministic across all agents
```

## Testing

Run the comprehensive test suite:

```bash
pytest src/cognition/temporal/test_consensus.py -v
```

Run the interactive demonstration:

```bash
python src/cognition/temporal/demo_consensus.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Consensus Protocol                   │
│                                                         │
│  ┌───────────────┐         ┌──────────────────────┐    │
│  │ Vector Clock  │◄────────┤  Event Record        │    │
│  │ (Causality)   │         │  - event_id          │    │
│  └───────────────┘         │  - agent_id          │    │
│                            │  - event_type        │    │
│  ┌───────────────┐         │  - vector_clock      │    │
│  │ Lamport Clock │◄────────┤  - lamport_timestamp │    │
│  │ (Total Order) │         │  - payload           │    │
│  └───────────────┘         │  - signature         │    │
│                            └──────────────────────┘    │
│                                      ▲                  │
│                                      │                  │
│  ┌───────────────┐         ┌────────┴─────────┐        │
│  │   Conflict    │◄────────┤  BFT Consensus   │        │
│  │   Resolver    │         │  - Proposals     │        │
│  └───────────────┘         │  - Votes         │        │
│                            │  - Commitment    │        │
│                            └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Guarantees

### Safety
- **Agreement**: All correct agents agree on committed events
- **Validity**: Only proposed events can be committed
- **Integrity**: Events are committed at most once

### Liveness
- **Termination**: All proposals eventually complete (with timeout)
- **Progress**: System makes progress with ≥ 2f+1 correct agents

### Ordering
- **Causal Consistency**: e1 → e2 ⇒ all agents see e1 before e2
- **Total Order**: All events have deterministic total order
- **Linearizability**: Operations appear atomic

## Performance

### Space Complexity
- Vector Clock: O(n) per event, where n = number of agents
- Lamport Timestamp: O(1) per event
- Event Log: O(m) where m = number of events

### Time Complexity
- Clock tick: O(1)
- Clock merge: O(n)
- Happens-before check: O(n)
- Event linearization: O(m log m)
- BFT consensus: O(n²) messages

### Message Complexity
- Proposal phase: O(n) messages
- Voting phase: O(n²) messages
- Total per consensus: O(n²)

## References

1. Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System"
2. Fidge, C. (1988). "Timestamps in Message-Passing Systems"
3. Mattern, F. (1989). "Virtual Time and Global States of Distributed Systems"
4. Castro, M. & Liskov, B. (1999). "Practical Byzantine Fault Tolerance"

## Integration with Existing Temporal Module

This consensus protocol extends the existing temporal module:

- **Chronos**: Uses consensus for temporal weight coordination
- **Atropos**: Uses BFT for anti-rollback guarantees
- **Clotho**: Uses consensus for distributed transaction coordination

The new components are backward compatible and integrate seamlessly with existing vector clocks and Lamport clocks in the temporal module.

## Future Enhancements

1. **Optimizations**
   - Sparse vector clocks for scalability
   - Incremental signature schemes
   - View change protocol for leader election

2. **Extensions**
   - Multi-decree consensus (Paxos/Raft)
   - Optimistic concurrency control
   - Snapshot isolation

3. **Monitoring**
   - Latency tracking
   - Throughput metrics
   - Byzantine detection

## License

Part of the Sovereign Governance Substrate.
See top-level LICENSE file for details.
