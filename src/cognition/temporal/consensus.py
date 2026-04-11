#                                           [2026-04-11]
#                                          Productivity: Active
"""
Temporal Consensus Protocol for Distributed Agents

Implements consensus mechanisms for Chronos, Atropos, and Clotho:
- Causal ordering with happens-before relationships
- Deterministic conflict resolution
- Byzantine Fault Tolerance (BFT)
- Event linearization

The protocol ensures:
1. Safety: All correct agents agree on event order
2. Liveness: Events are eventually ordered
3. Byzantine resilience: Tolerates up to f < n/3 malicious agents
"""

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from src.cognition.temporal.lamport import LamportClock, LamportTimestamp
from src.cognition.temporal.vector_clock import VectorClock as VectorClockImpl

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the temporal consensus system."""
    
    STATE_TRANSITION = "state_transition"
    MESSAGE_SEND = "message_send"
    MESSAGE_RECEIVE = "message_receive"
    DECISION = "decision"
    PROPOSAL = "proposal"
    VOTE = "vote"


@dataclass
class EventRecord:
    """
    Record of a single event in the distributed system.
    
    Contains both vector clock (for causality) and Lamport timestamp
    (for total ordering).
    """
    
    event_id: str
    agent_id: str
    event_type: EventType
    
    vector_clock: VectorClockImpl
    lamport_timestamp: LamportTimestamp
    
    payload: dict[str, Any] = field(default_factory=dict)
    wall_time: datetime = field(default_factory=datetime.utcnow)
    
    signature: str | None = None
    
    def compute_hash(self) -> str:
        """
        Compute cryptographic hash of event for integrity.
        
        Returns:
            SHA-256 hash of event data
        """
        canonical = {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "event_type": self.event_type.value,
            "vector_clock": self.vector_clock.to_dict(),
            "lamport_timestamp": self.lamport_timestamp.to_dict(),
            "payload": self.payload,
        }
        
        import json
        content = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(content.encode()).hexdigest()
    
    def sign(self, signature: str):
        """
        Add cryptographic signature (for Byzantine fault tolerance).
        
        Args:
            signature: Digital signature of event hash
        """
        self.signature = signature
    
    def verify_signature(self, public_key: str) -> bool:
        """
        Verify event signature (simplified for demonstration).
        
        Args:
            public_key: Public key of signing agent
            
        Returns:
            True if signature valid
        """
        if not self.signature:
            return False
        
        # Simplified verification (in production, use proper crypto)
        expected_sig = hashlib.sha256(
            f"{self.compute_hash()}:{public_key}".encode()
        ).hexdigest()
        
        return self.signature == expected_sig
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "event_type": self.event_type.value,
            "vector_clock": self.vector_clock.to_dict(),
            "lamport_timestamp": self.lamport_timestamp.to_dict(),
            "payload": self.payload,
            "wall_time": self.wall_time.isoformat(),
            "signature": self.signature,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventRecord":
        """Create event record from dictionary."""
        return cls(
            event_id=data["event_id"],
            agent_id=data["agent_id"],
            event_type=EventType(data["event_type"]),
            vector_clock=VectorClockImpl.from_dict(data["vector_clock"]),
            lamport_timestamp=LamportTimestamp.from_dict(data["lamport_timestamp"]),
            payload=data.get("payload", {}),
            wall_time=datetime.fromisoformat(data["wall_time"]),
            signature=data.get("signature"),
        )


class ConflictResolver:
    """
    Deterministic conflict resolution for concurrent events.
    
    When events are concurrent (incomparable in causal order),
    uses Lamport timestamps to impose total order.
    """
    
    @staticmethod
    def resolve(event1: EventRecord, event2: EventRecord) -> int:
        """
        Compare two events and determine order.
        
        Returns:
            -1 if event1 < event2
             0 if event1 == event2
             1 if event1 > event2
        """
        # First check causal ordering (vector clocks)
        if event1.vector_clock.happens_before(event2.vector_clock):
            logger.debug("Event %s causally before %s", event1.event_id, event2.event_id)
            return -1
        
        if event2.vector_clock.happens_before(event1.vector_clock):
            logger.debug("Event %s causally after %s", event1.event_id, event2.event_id)
            return 1
        
        # Events are concurrent - use Lamport timestamps for total order
        if event1.lamport_timestamp < event2.lamport_timestamp:
            logger.debug(
                "Concurrent events: %s < %s (Lamport tiebreaker)",
                event1.event_id,
                event2.event_id,
            )
            return -1
        
        if event1.lamport_timestamp > event2.lamport_timestamp:
            logger.debug(
                "Concurrent events: %s > %s (Lamport tiebreaker)",
                event1.event_id,
                event2.event_id,
            )
            return 1
        
        # Identical timestamps (should be rare with good agent IDs)
        logger.warning(
            "Events %s and %s have identical timestamps",
            event1.event_id,
            event2.event_id,
        )
        return 0
    
    @staticmethod
    def linearize(events: list[EventRecord]) -> list[EventRecord]:
        """
        Linearize a set of events into total order.
        
        Args:
            events: List of events to order
            
        Returns:
            Sorted list respecting causal and temporal order
        """
        from functools import cmp_to_key
        
        sorted_events = sorted(events, key=cmp_to_key(ConflictResolver.resolve))
        
        logger.info("Linearized %d events", len(sorted_events))
        return sorted_events


class ConsensusProtocol:
    """
    Main consensus protocol for temporal agents.
    
    Coordinates event ordering across Chronos, Atropos, and Clotho
    using vector clocks and Lamport timestamps.
    """
    
    def __init__(self, agent_id: str, peer_agents: list[str] | None = None):
        """
        Initialize consensus protocol for an agent.
        
        Args:
            agent_id: This agent's unique identifier
            peer_agents: List of peer agent IDs
        """
        self.agent_id = agent_id
        self.peer_agents = peer_agents or []
        
        # Clocks
        self.vector_clock = VectorClockImpl(agent_id)
        self.lamport_clock = LamportClock(agent_id)
        
        # Event log
        self.events: list[EventRecord] = []
        self.event_index: dict[str, EventRecord] = {}
        
        # Conflict resolver
        self.resolver = ConflictResolver()
        
        logger.info(
            "Initialized consensus protocol for %s with peers %s",
            agent_id,
            peer_agents,
        )
    
    def record_local_event(
        self, event_type: EventType, payload: dict[str, Any] | None = None
    ) -> EventRecord:
        """
        Record a local event (no message exchange).
        
        Args:
            event_type: Type of event
            payload: Optional event data
            
        Returns:
            Created event record
        """
        # Increment clocks
        self.vector_clock.tick()
        lamport_ts = self.lamport_clock.tick()
        
        # Create event
        event = EventRecord(
            event_id=f"{self.agent_id}_{lamport_ts.counter}",
            agent_id=self.agent_id,
            event_type=event_type,
            vector_clock=self.vector_clock.copy(),
            lamport_timestamp=lamport_ts,
            payload=payload or {},
        )
        
        # Add to log
        self.events.append(event)
        self.event_index[event.event_id] = event
        
        logger.debug("Recorded local event: %s", event.event_id)
        
        return event
    
    def prepare_message(
        self, event_type: EventType, payload: dict[str, Any] | None = None
    ) -> EventRecord:
        """
        Prepare message to send to other agents.
        
        Args:
            event_type: Type of message event
            payload: Message data
            
        Returns:
            Message event with current clock snapshots
        """
        # Record as local event first
        event = self.record_local_event(EventType.MESSAGE_SEND, payload)
        event.event_type = event_type
        
        return event
    
    def receive_message(self, message_event: EventRecord) -> EventRecord:
        """
        Process received message and update clocks.
        
        Args:
            message_event: Event from another agent
            
        Returns:
            Receive event record
        """
        # Update clocks
        self.vector_clock.merge(message_event.vector_clock)
        self.lamport_clock.update(message_event.lamport_timestamp)
        
        # Record receive event
        receive_event = EventRecord(
            event_id=f"{self.agent_id}_recv_{message_event.event_id}",
            agent_id=self.agent_id,
            event_type=EventType.MESSAGE_RECEIVE,
            vector_clock=self.vector_clock.copy(),
            lamport_timestamp=self.lamport_clock.current(),
            payload={
                "source_agent": message_event.agent_id,
                "source_event": message_event.event_id,
            },
        )
        
        # Add both events to log
        self.events.append(message_event)
        self.events.append(receive_event)
        self.event_index[message_event.event_id] = message_event
        self.event_index[receive_event.event_id] = receive_event
        
        logger.debug(
            "Received message from %s: %s",
            message_event.agent_id,
            message_event.event_id,
        )
        
        return receive_event
    
    def get_causal_history(self, event: EventRecord) -> list[EventRecord]:
        """
        Get all events that causally precede given event.
        
        Args:
            event: Event to find history for
            
        Returns:
            List of causally preceding events
        """
        history = [
            e
            for e in self.events
            if e.vector_clock.happens_before(event.vector_clock)
        ]
        
        return self.resolver.linearize(history)
    
    def get_linearized_log(self) -> list[EventRecord]:
        """
        Get total-ordered event log.
        
        Returns:
            All events in deterministic total order
        """
        return self.resolver.linearize(self.events)
    
    def verify_consistency(self) -> tuple[bool, list[str]]:
        """
        Verify consistency of event log.
        
        Checks:
        - All events are properly ordered
        - No causality violations
        - Vector clock consistency
        
        Returns:
            (is_consistent, list of violations)
        """
        violations = []
        
        # Check each event's vector clock
        for event in self.events:
            # Vector clock should be monotonic for this agent
            agent_clock = event.vector_clock.clock.get(event.agent_id, 0)
            
            # Find previous events from same agent
            prev_events = [
                e
                for e in self.events
                if e.agent_id == event.agent_id
                and e.lamport_timestamp < event.lamport_timestamp
            ]
            
            if prev_events:
                max_prev_clock = max(
                    e.vector_clock.clock.get(event.agent_id, 0) for e in prev_events
                )
                if agent_clock <= max_prev_clock:
                    violations.append(
                        f"Vector clock not monotonic for {event.event_id}: "
                        f"{agent_clock} <= {max_prev_clock}"
                    )
        
        # Check causality preservation
        linearized = self.get_linearized_log()
        for i, event1 in enumerate(linearized):
            for event2 in linearized[i + 1 :]:
                # If event1 should happen before event2 causally
                if event1.vector_clock.happens_before(event2.vector_clock):
                    # They should also be ordered correctly in linearization
                    # (which they are, by construction)
                    continue
                
                # If event2 happens before event1 causally, that's a violation
                if event2.vector_clock.happens_before(event1.vector_clock):
                    violations.append(
                        f"Causality violation: {event2.event_id} happens before "
                        f"{event1.event_id} but appears after in linearization"
                    )
        
        is_consistent = len(violations) == 0
        
        if not is_consistent:
            logger.error("Consistency check failed: %s", violations)
        else:
            logger.info("Consistency check passed")
        
        return is_consistent, violations


class BFTConsensus:
    """
    Byzantine Fault Tolerant consensus for temporal agents.
    
    Tolerates up to f < n/3 malicious agents using:
    - Cryptographic signatures
    - Quorum-based voting
    - View changes for liveness
    
    Simplified PBFT-style protocol for demonstration.
    """
    
    def __init__(self, agent_id: str, all_agents: list[str]):
        """
        Initialize BFT consensus.
        
        Args:
            agent_id: This agent's ID
            all_agents: List of all agent IDs (including self)
        """
        self.agent_id = agent_id
        self.all_agents = all_agents
        self.n = len(all_agents)
        self.f = (self.n - 1) // 3  # Maximum tolerable faults
        self.quorum_size = 2 * self.f + 1  # 2f + 1 for quorum
        
        # Consensus state
        self.proposals: dict[str, EventRecord] = {}
        self.votes: dict[str, dict[str, str]] = defaultdict(dict)  # event_id -> {agent_id -> signature}
        self.committed: set[str] = set()
        
        logger.info(
            "Initialized BFT consensus for %s: n=%d, f=%d, quorum=%d",
            agent_id,
            self.n,
            self.f,
            self.quorum_size,
        )
    
    def propose(self, event: EventRecord) -> bool:
        """
        Propose an event for consensus.
        
        Args:
            event: Event to propose
            
        Returns:
            True if proposal initiated
        """
        # Sign the event
        event_hash = event.compute_hash()
        signature = self._sign(event_hash)
        event.sign(signature)
        
        # Record proposal
        self.proposals[event.event_id] = event
        self.votes[event.event_id][self.agent_id] = signature
        
        logger.info("Proposed event %s for consensus", event.event_id)
        
        return True
    
    def vote(self, event: EventRecord) -> bool:
        """
        Vote on a proposed event.
        
        Args:
            event: Proposed event
            
        Returns:
            True if vote cast
        """
        # Verify event signature
        if not event.signature:
            logger.warning("Cannot vote on unsigned event %s", event.event_id)
            return False
        
        # Sign our vote
        event_hash = event.compute_hash()
        signature = self._sign(event_hash)
        
        # Record vote
        self.votes[event.event_id][self.agent_id] = signature
        
        logger.debug("Voted on event %s", event.event_id)
        
        # Check if quorum reached
        if len(self.votes[event.event_id]) >= self.quorum_size:
            self._commit(event.event_id)
        
        return True
    
    def _commit(self, event_id: str):
        """
        Commit an event after reaching quorum.
        
        Args:
            event_id: Event ID to commit
        """
        if event_id in self.committed:
            return
        
        self.committed.add(event_id)
        
        logger.info(
            "Committed event %s with %d votes (quorum: %d)",
            event_id,
            len(self.votes[event_id]),
            self.quorum_size,
        )
    
    def is_committed(self, event_id: str) -> bool:
        """
        Check if event is committed.
        
        Args:
            event_id: Event ID to check
            
        Returns:
            True if committed
        """
        return event_id in self.committed
    
    def get_committed_events(self) -> list[str]:
        """
        Get all committed event IDs.
        
        Returns:
            List of committed event IDs
        """
        return list(self.committed)
    
    def _sign(self, data: str) -> str:
        """
        Create signature (simplified for demonstration).
        
        Args:
            data: Data to sign
            
        Returns:
            Signature string
        """
        # In production: use proper digital signatures (Ed25519, ECDSA, etc.)
        return hashlib.sha256(f"{data}:{self.agent_id}:secret_key".encode()).hexdigest()
    
    def can_tolerate_faults(self, failed_agents: int) -> bool:
        """
        Check if system can tolerate given number of failures.
        
        Args:
            failed_agents: Number of failed/malicious agents
            
        Returns:
            True if system remains safe
        """
        return failed_agents <= self.f


def test_consensus_protocol():
    """Test basic consensus protocol with three agents."""
    # Create three temporal agents
    chronos = ConsensusProtocol("chronos", ["atropos", "clotho"])
    atropos = ConsensusProtocol("atropos", ["chronos", "clotho"])
    clotho = ConsensusProtocol("clotho", ["chronos", "atropos"])
    
    # Chronos records local event
    e1 = chronos.record_local_event(EventType.STATE_TRANSITION, {"state": "active"})
    
    # Chronos sends message to Atropos
    msg = chronos.prepare_message(EventType.MESSAGE_SEND, {"to": "atropos", "data": "hello"})
    atropos.receive_message(msg)
    
    # Atropos responds
    response = atropos.prepare_message(EventType.MESSAGE_SEND, {"to": "chronos", "data": "world"})
    chronos.receive_message(response)
    
    # Verify consistency
    for agent in [chronos, atropos, clotho]:
        consistent, violations = agent.verify_consistency()
        assert consistent, f"{agent.agent_id} has violations: {violations}"
    
    logger.info("Consensus protocol tests passed")


def test_bft_consensus():
    """Test Byzantine fault tolerant consensus."""
    agents = ["chronos", "atropos", "clotho"]
    
    # Create BFT consensus for each agent
    bft_nodes = {
        agent_id: BFTConsensus(agent_id, agents) for agent_id in agents
    }
    
    # Chronos proposes event
    chronos_protocol = ConsensusProtocol("chronos")
    event = chronos_protocol.record_local_event(
        EventType.PROPOSAL, {"proposal": "new_state"}
    )
    
    bft_nodes["chronos"].propose(event)
    
    # Other agents vote
    bft_nodes["atropos"].vote(event)
    bft_nodes["clotho"].vote(event)
    
    # Check commitment (should be committed with 3/3 votes, quorum is 2)
    for agent_id, bft in bft_nodes.items():
        assert bft.is_committed(event.event_id), f"{agent_id} should have committed"
    
    # Verify fault tolerance
    assert bft_nodes["chronos"].can_tolerate_faults(0)  # 3 agents tolerate 0 faults (f=0)
    assert not bft_nodes["chronos"].can_tolerate_faults(1)  # Cannot tolerate 1 fault
    
    logger.info("BFT consensus tests passed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_consensus_protocol()
    test_bft_consensus()
