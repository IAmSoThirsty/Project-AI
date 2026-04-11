#                                           [2026-04-11]
#                                          Productivity: Active
"""
Test Suite for Temporal Consensus Protocol

Tests vector clocks, Lamport timestamps, causal ordering,
conflict resolution, and Byzantine fault tolerance.
"""

import logging
import pytest
from datetime import datetime

from src.cognition.temporal.vector_clock import VectorClock as VectorClockImpl
from src.cognition.temporal.lamport import LamportClock, LamportTimestamp
from src.cognition.temporal.consensus import (
    EventRecord,
    EventType,
    ConflictResolver,
    ConsensusProtocol,
    BFTConsensus,
)

logger = logging.getLogger(__name__)


class TestVectorClock:
    """Test vector clock operations."""
    
    def test_initialization(self):
        """Test vector clock initialization."""
        vc = VectorClockImpl("chronos")
        assert vc.process_id == "chronos"
        assert vc.clock["chronos"] == 0
    
    def test_tick(self):
        """Test local clock increment."""
        vc = VectorClockImpl("chronos")
        vc.tick()
        assert vc.clock["chronos"] == 1
        vc.tick()
        assert vc.clock["chronos"] == 2
    
    def test_update_merge(self):
        """Test merging vector clocks."""
        chronos = VectorClockImpl("chronos")
        atropos = VectorClockImpl("atropos")
        
        chronos.tick()  # chronos: 1, atropos: 0
        chronos_snapshot = chronos.copy()
        
        atropos.merge(chronos_snapshot)  # atropos: chronos=1, atropos=1
        
        assert atropos.clock["chronos"] == 1
        assert atropos.clock["atropos"] == 1
    
    def test_happens_before(self):
        """Test happens-before relationship."""
        chronos = VectorClockImpl("chronos")
        atropos = VectorClockImpl("atropos")
        
        # Chronos sends to Atropos
        chronos.tick()
        snapshot = chronos.copy()
        chronos.tick()
        
        atropos.merge(snapshot)
        
        # snapshot happens before atropos
        assert snapshot.happens_before(atropos)
        assert not atropos.happens_before(snapshot)
    
    def test_concurrent_events(self):
        """Test concurrent event detection."""
        chronos = VectorClockImpl("chronos")
        atropos = VectorClockImpl("atropos")
        
        # Both tick independently
        chronos.tick()
        atropos.tick()
        
        # They are concurrent
        assert chronos.concurrent_with(atropos)
        assert atropos.concurrent_with(chronos)
    
    def test_causal_equality(self):
        """Test causal equality."""
        vc1 = VectorClockImpl("chronos")
        vc2 = VectorClockImpl("chronos")
        
        assert vc1.equals(vc2)
        
        vc1.tick()
        assert not vc1.equals(vc2)
    
    def test_serialization(self):
        """Test vector clock serialization."""
        vc = VectorClockImpl("chronos")
        vc.tick()
        vc.tick()
        
        data = vc.to_dict()
        vc2 = VectorClockImpl.from_dict(data)
        
        assert vc.equals(vc2)


class TestLamportClock:
    """Test Lamport timestamp operations."""
    
    def test_initialization(self):
        """Test Lamport clock initialization."""
        lc = LamportClock("chronos")
        assert lc.agent_id == "chronos"
        assert lc.counter == 0
    
    def test_tick(self):
        """Test clock tick."""
        lc = LamportClock("chronos")
        
        ts1 = lc.tick()
        assert ts1.counter == 1
        assert ts1.agent_id == "chronos"
        
        ts2 = lc.tick()
        assert ts2.counter == 2
    
    def test_update(self):
        """Test clock update on message receive."""
        chronos = LamportClock("chronos")
        atropos = LamportClock("atropos")
        
        # Chronos sends
        ts1 = chronos.tick()
        
        # Atropos receives and updates
        ts2 = atropos.update(ts1)
        
        # Atropos clock should be max(0, 1) + 1 = 2
        assert ts2.counter == 2
    
    def test_total_ordering(self):
        """Test total ordering of timestamps."""
        t1 = LamportTimestamp(1, "chronos")
        t2 = LamportTimestamp(2, "atropos")
        t3 = LamportTimestamp(1, "atropos")
        
        # Ordered by counter first
        assert t1 < t2
        assert t3 < t2
        
        # Tiebreaker by agent ID
        assert t3 < t1  # "atropos" < "chronos"
    
    def test_serialization(self):
        """Test timestamp serialization."""
        ts = LamportTimestamp(5, "chronos")
        
        data = ts.to_dict()
        ts2 = LamportTimestamp.from_dict(data)
        
        assert ts == ts2


class TestEventRecord:
    """Test event record operations."""
    
    def test_event_creation(self):
        """Test creating event record."""
        vc = VectorClockImpl("chronos")
        vc.tick()
        
        lc = LamportClock("chronos")
        ts = lc.tick()
        
        event = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.STATE_TRANSITION,
            vector_clock=vc,
            lamport_timestamp=ts,
            payload={"state": "active"},
        )
        
        assert event.event_id == "e1"
        assert event.agent_id == "chronos"
        assert event.payload["state"] == "active"
    
    def test_event_hash(self):
        """Test event hash computation."""
        vc = VectorClockImpl("chronos")
        vc.tick()
        
        ts = LamportTimestamp(1, "chronos")
        
        event = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.PROPOSAL,
            vector_clock=vc,
            lamport_timestamp=ts,
        )
        
        hash1 = event.compute_hash()
        hash2 = event.compute_hash()
        
        # Hash should be deterministic
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256
    
    def test_event_serialization(self):
        """Test event serialization."""
        vc = VectorClockImpl("chronos")
        vc.tick()
        
        ts = LamportTimestamp(1, "chronos")
        
        event = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.DECISION,
            vector_clock=vc,
            lamport_timestamp=ts,
        )
        
        data = event.to_dict()
        event2 = EventRecord.from_dict(data)
        
        assert event.event_id == event2.event_id
        assert event.agent_id == event2.agent_id


class TestConflictResolver:
    """Test conflict resolution."""
    
    def test_causal_ordering(self):
        """Test resolving causally ordered events."""
        # Create two agents
        chronos_vc = VectorClockImpl("chronos")
        atropos_vc = VectorClockImpl("atropos")
        
        chronos_lc = LamportClock("chronos")
        atropos_lc = LamportClock("atropos")
        
        # Chronos event
        chronos_vc.tick()
        chronos_ts = chronos_lc.tick()
        e1 = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.STATE_TRANSITION,
            vector_clock=chronos_vc.copy(),
            lamport_timestamp=chronos_ts,
        )
        
        # Atropos receives and responds
        atropos_vc.merge(chronos_vc)
        atropos_ts = atropos_lc.update(chronos_ts)
        e2 = EventRecord(
            event_id="e2",
            agent_id="atropos",
            event_type=EventType.STATE_TRANSITION,
            vector_clock=atropos_vc.copy(),
            lamport_timestamp=atropos_ts,
        )
        
        # e1 should happen before e2
        resolver = ConflictResolver()
        assert resolver.resolve(e1, e2) == -1
        assert resolver.resolve(e2, e1) == 1
    
    def test_concurrent_resolution(self):
        """Test resolving concurrent events using Lamport timestamps."""
        # Two independent events
        chronos_vc = VectorClockImpl("chronos")
        atropos_vc = VectorClockImpl("atropos")
        
        chronos_lc = LamportClock("chronos")
        atropos_lc = LamportClock("atropos")
        
        chronos_vc.tick()
        chronos_ts = chronos_lc.tick()
        e1 = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.STATE_TRANSITION,
            vector_clock=chronos_vc,
            lamport_timestamp=chronos_ts,
        )
        
        atropos_vc.tick()
        atropos_ts = atropos_lc.tick()
        e2 = EventRecord(
            event_id="e2",
            agent_id="atropos",
            event_type=EventType.STATE_TRANSITION,
            vector_clock=atropos_vc,
            lamport_timestamp=atropos_ts,
        )
        
        # Events are concurrent, use Lamport tiebreaker
        resolver = ConflictResolver()
        
        # Both have counter=1, so alphabetical: "atropos" < "chronos"
        assert resolver.resolve(e1, e2) == 1
        assert resolver.resolve(e2, e1) == -1
    
    def test_linearization(self):
        """Test event linearization."""
        events = []
        
        # Create events with different orderings
        for i, agent_id in enumerate(["chronos", "atropos", "clotho"]):
            vc = VectorClockImpl(agent_id)
            vc.tick()
            
            ts = LamportTimestamp(i + 1, agent_id)
            
            events.append(
                EventRecord(
                    event_id=f"e{i}",
                    agent_id=agent_id,
                    event_type=EventType.STATE_TRANSITION,
                    vector_clock=vc,
                    lamport_timestamp=ts,
                )
            )
        
        # Linearize
        resolver = ConflictResolver()
        ordered = resolver.linearize(events)
        
        # Should be ordered by Lamport timestamp
        assert ordered[0].lamport_timestamp.counter == 1
        assert ordered[1].lamport_timestamp.counter == 2
        assert ordered[2].lamport_timestamp.counter == 3


class TestConsensusProtocol:
    """Test consensus protocol."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        protocol = ConsensusProtocol("chronos", ["atropos", "clotho"])
        
        assert protocol.agent_id == "chronos"
        assert len(protocol.peer_agents) == 2
    
    def test_local_event(self):
        """Test recording local event."""
        protocol = ConsensusProtocol("chronos")
        
        event = protocol.record_local_event(
            EventType.STATE_TRANSITION, {"state": "ready"}
        )
        
        assert event.agent_id == "chronos"
        assert event.payload["state"] == "ready"
        assert len(protocol.events) == 1
    
    def test_message_exchange(self):
        """Test message preparation and receipt."""
        chronos = ConsensusProtocol("chronos", ["atropos"])
        atropos = ConsensusProtocol("atropos", ["chronos"])
        
        # Chronos sends message
        msg = chronos.prepare_message(
            EventType.MESSAGE_SEND, {"to": "atropos", "data": "hello"}
        )
        
        # Atropos receives
        recv_event = atropos.receive_message(msg)
        
        assert recv_event.payload["source_agent"] == "chronos"
        assert atropos.vector_clock.clock["chronos"] == 1
    
    def test_causal_history(self):
        """Test getting causal history of event."""
        protocol = ConsensusProtocol("chronos")
        
        # Create chain of events
        e1 = protocol.record_local_event(EventType.STATE_TRANSITION, {"step": 1})
        e2 = protocol.record_local_event(EventType.STATE_TRANSITION, {"step": 2})
        e3 = protocol.record_local_event(EventType.STATE_TRANSITION, {"step": 3})
        
        # Get history of e3
        history = protocol.get_causal_history(e3)
        
        # e1 and e2 should be in history
        assert len(history) >= 2
    
    def test_consistency_verification(self):
        """Test consistency verification."""
        protocol = ConsensusProtocol("chronos")
        
        # Record some events
        protocol.record_local_event(EventType.STATE_TRANSITION)
        protocol.record_local_event(EventType.DECISION)
        
        # Should be consistent
        is_consistent, violations = protocol.verify_consistency()
        assert is_consistent
        assert len(violations) == 0


class TestBFTConsensus:
    """Test Byzantine fault tolerant consensus."""
    
    def test_initialization(self):
        """Test BFT initialization."""
        agents = ["chronos", "atropos", "clotho"]
        bft = BFTConsensus("chronos", agents)
        
        assert bft.n == 3
        assert bft.f == 0  # (3-1)//3 = 0
        assert bft.quorum_size == 1  # 2*0 + 1 = 1
    
    def test_proposal(self):
        """Test event proposal."""
        agents = ["chronos", "atropos", "clotho"]
        bft = BFTConsensus("chronos", agents)
        
        # Create event
        vc = VectorClockImpl("chronos")
        vc.tick()
        ts = LamportTimestamp(1, "chronos")
        
        event = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.PROPOSAL,
            vector_clock=vc,
            lamport_timestamp=ts,
        )
        
        # Propose
        success = bft.propose(event)
        assert success
        assert event.event_id in bft.proposals
    
    def test_voting_and_commit(self):
        """Test voting and commitment."""
        agents = ["chronos", "atropos", "clotho", "lachesis"]
        
        # Create BFT for all agents
        bft_nodes = {
            agent_id: BFTConsensus(agent_id, agents) for agent_id in agents
        }
        
        # Create event
        vc = VectorClockImpl("chronos")
        vc.tick()
        ts = LamportTimestamp(1, "chronos")
        
        event = EventRecord(
            event_id="e1",
            agent_id="chronos",
            event_type=EventType.PROPOSAL,
            vector_clock=vc,
            lamport_timestamp=ts,
        )
        
        # Chronos proposes
        bft_nodes["chronos"].propose(event)
        
        # Others vote (quorum is 3 for 4 agents: 2*1 + 1)
        bft_nodes["atropos"].vote(event)
        bft_nodes["clotho"].vote(event)
        
        # Should be committed with 3 votes
        assert len(bft_nodes["clotho"].votes[event.event_id]) >= bft_nodes["clotho"].quorum_size
    
    def test_fault_tolerance(self):
        """Test fault tolerance calculation."""
        # 4 agents: f = (4-1)//3 = 1
        agents = ["chronos", "atropos", "clotho", "lachesis"]
        bft = BFTConsensus("chronos", agents)
        
        assert bft.f == 1
        assert bft.can_tolerate_faults(0)
        assert bft.can_tolerate_faults(1)
        assert not bft.can_tolerate_faults(2)
        
        # 7 agents: f = (7-1)//3 = 2
        agents7 = [f"agent{i}" for i in range(7)]
        bft7 = BFTConsensus("agent0", agents7)
        
        assert bft7.f == 2
        assert bft7.can_tolerate_faults(2)
        assert not bft7.can_tolerate_faults(3)


class TestIntegration:
    """Integration tests for complete consensus system."""
    
    def test_three_agent_consensus(self):
        """Test consensus among Chronos, Atropos, and Clotho."""
        # Create three agents with consensus protocols
        chronos = ConsensusProtocol("chronos", ["atropos", "clotho"])
        atropos = ConsensusProtocol("atropos", ["chronos", "clotho"])
        clotho = ConsensusProtocol("clotho", ["chronos", "atropos"])
        
        # Chronos initiates
        msg1 = chronos.prepare_message(
            EventType.PROPOSAL, {"proposal": "new_state", "value": 42}
        )
        
        # Send to Atropos and Clotho
        atropos.receive_message(msg1)
        clotho.receive_message(msg1)
        
        # Atropos votes
        vote1 = atropos.prepare_message(EventType.VOTE, {"proposal_id": msg1.event_id, "vote": "yes"})
        chronos.receive_message(vote1)
        clotho.receive_message(vote1)
        
        # Clotho votes
        vote2 = clotho.prepare_message(EventType.VOTE, {"proposal_id": msg1.event_id, "vote": "yes"})
        chronos.receive_message(vote2)
        atropos.receive_message(vote2)
        
        # All agents should have consistent logs
        for agent in [chronos, atropos, clotho]:
            is_consistent, violations = agent.verify_consistency()
            assert is_consistent, f"{agent.agent_id} inconsistent: {violations}"
    
    def test_bft_integration(self):
        """Test full BFT consensus flow."""
        agents = ["chronos", "atropos", "clotho", "lachesis"]
        
        # Create consensus protocols
        protocols = {
            agent_id: ConsensusProtocol(agent_id, [a for a in agents if a != agent_id])
            for agent_id in agents
        }
        
        # Create BFT consensus
        bft_nodes = {
            agent_id: BFTConsensus(agent_id, agents) for agent_id in agents
        }
        
        # Chronos proposes
        event = protocols["chronos"].record_local_event(
            EventType.PROPOSAL, {"value": 123}
        )
        
        bft_nodes["chronos"].propose(event)
        
        # All vote
        for agent_id in agents:
            bft_nodes[agent_id].vote(event)
        
        # All should have quorum
        for agent_id in agents:
            assert len(bft_nodes[agent_id].votes[event.event_id]) >= bft_nodes[agent_id].quorum_size
        
        logger.info("BFT integration test passed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v"])
