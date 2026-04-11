"""
Test Suite for Temporal Module Import Paths

Verifies that all consensus protocol components are properly exported
through the temporal module __init__.py.
"""

import pytest


class TestTemporalImports:
    """Test that all components are importable from the temporal module."""
    
    def test_import_lamport_components(self):
        """Test importing Lamport clock components."""
        from src.cognition.temporal import LamportClockNew, LamportTimestamp
        
        # Test LamportClockNew
        clock = LamportClockNew("test_agent")
        assert clock.agent_id == "test_agent"
        assert clock.counter == 0
        
        # Test LamportTimestamp
        ts = LamportTimestamp(1, "test_agent")
        assert ts.counter == 1
        assert ts.agent_id == "test_agent"
    
    def test_import_consensus_components(self):
        """Test importing consensus protocol components."""
        from src.cognition.temporal import (
            EventRecord,
            EventType,
            ConflictResolver,
            ConsensusProtocol,
            BFTConsensus,
        )
        
        # Test EventType enum
        assert EventType.STATE_TRANSITION.value == "state_transition"
        assert EventType.PROPOSAL.value == "proposal"
        
        # Test ConflictResolver
        resolver = ConflictResolver()
        assert resolver is not None
        
        # Test ConsensusProtocol
        protocol = ConsensusProtocol("test_agent")
        assert protocol.agent_id == "test_agent"
        
        # Test BFTConsensus
        bft = BFTConsensus("test_agent", ["agent1", "agent2"])
        assert bft.agent_id == "test_agent"
    
    def test_import_all_components_together(self):
        """Test importing all consensus components in one statement."""
        from src.cognition.temporal import (
            LamportClockNew,
            LamportTimestamp,
            EventRecord,
            EventType,
            ConflictResolver,
            ConsensusProtocol,
            BFTConsensus,
        )
        
        # Verify all imports are available
        assert LamportClockNew is not None
        assert LamportTimestamp is not None
        assert EventRecord is not None
        assert EventType is not None
        assert ConflictResolver is not None
        assert ConsensusProtocol is not None
        assert BFTConsensus is not None
    
    def test_lamport_clock_new_alias(self):
        """Test that LamportClockNew is properly aliased from LamportClock."""
        from src.cognition.temporal import LamportClockNew
        from src.cognition.temporal.lamport import LamportClock
        
        # Should be the same class
        assert LamportClockNew is LamportClock
    
    def test_event_record_creation(self):
        """Test creating an EventRecord with imported components."""
        from src.cognition.temporal import (
            EventRecord,
            EventType,
            LamportTimestamp,
            VectorClockImpl,
        )
        
        # Create vector clock
        vc = VectorClockImpl("test_agent")
        vc.tick()
        
        # Create Lamport timestamp
        ts = LamportTimestamp(1, "test_agent")
        
        # Create event record
        event = EventRecord(
            event_id="test_event",
            agent_id="test_agent",
            event_type=EventType.STATE_TRANSITION,
            vector_clock=vc,
            lamport_timestamp=ts,
            payload={"test": "data"},
        )
        
        assert event.event_id == "test_event"
        assert event.agent_id == "test_agent"
        assert event.payload["test"] == "data"
    
    def test_conflict_resolver_usage(self):
        """Test using ConflictResolver with imported components."""
        from src.cognition.temporal import (
            ConflictResolver,
            EventRecord,
            EventType,
            LamportTimestamp,
            VectorClockImpl,
        )
        
        # Create two events
        vc1 = VectorClockImpl("agent1")
        vc1.tick()
        e1 = EventRecord(
            event_id="e1",
            agent_id="agent1",
            event_type=EventType.PROPOSAL,
            vector_clock=vc1,
            lamport_timestamp=LamportTimestamp(1, "agent1"),
        )
        
        vc2 = VectorClockImpl("agent2")
        vc2.tick()
        e2 = EventRecord(
            event_id="e2",
            agent_id="agent2",
            event_type=EventType.PROPOSAL,
            vector_clock=vc2,
            lamport_timestamp=LamportTimestamp(2, "agent2"),
        )
        
        # Resolve conflict
        resolver = ConflictResolver()
        result = resolver.resolve(e1, e2)
        
        # e1 should come before e2 (lower Lamport timestamp)
        assert result == -1
    
    def test_consensus_protocol_usage(self):
        """Test using ConsensusProtocol with imported components."""
        from src.cognition.temporal import (
            ConsensusProtocol,
            EventType,
        )
        
        # Create protocol
        protocol = ConsensusProtocol("test_agent", ["peer1", "peer2"])
        
        # Record local event
        event = protocol.record_local_event(
            EventType.STATE_TRANSITION,
            {"state": "active"}
        )
        
        assert event.agent_id == "test_agent"
        assert event.payload["state"] == "active"
        assert len(protocol.events) == 1
    
    def test_bft_consensus_usage(self):
        """Test using BFTConsensus with imported components."""
        from src.cognition.temporal import (
            BFTConsensus,
            EventRecord,
            EventType,
            LamportTimestamp,
            VectorClockImpl,
        )
        
        agents = ["agent1", "agent2", "agent3", "agent4"]
        bft = BFTConsensus("agent1", agents)
        
        # Create event
        vc = VectorClockImpl("agent1")
        vc.tick()
        event = EventRecord(
            event_id="proposal1",
            agent_id="agent1",
            event_type=EventType.PROPOSAL,
            vector_clock=vc,
            lamport_timestamp=LamportTimestamp(1, "agent1"),
            payload={"value": 42},
        )
        
        # Propose
        success = bft.propose(event)
        assert success
        assert event.event_id in bft.proposals


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
