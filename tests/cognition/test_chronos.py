"""
Unit tests for Chronos temporal weight engine and related components.

Tests cover:
- Vector clock operations
- Causality graph functionality
- Temporal event tracking
- Consistency verification
- Anomaly detection
- Weight computation
- Audit integration
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

from src.cognition.temporal.vector_clock import VectorClock
from src.cognition.temporal.causality_graph import CausalityGraph
from src.cognition.temporal.chronos import Chronos, TemporalEvent


class TestVectorClock:
    """Test vector clock functionality."""
    
    def test_initialization(self):
        """Test vector clock initialization."""
        vc = VectorClock("agent1")
        assert vc.process_id == "agent1"
        assert vc.clock == {"agent1": 0}
    
    def test_tick(self):
        """Test incrementing local clock."""
        vc = VectorClock("agent1")
        vc.tick()
        assert vc.clock["agent1"] == 1
        vc.tick()
        assert vc.clock["agent1"] == 2
    
    def test_merge(self):
        """Test merging vector clocks."""
        vc1 = VectorClock("agent1")
        vc1.tick()  # agent1: 1
        
        vc2 = VectorClock("agent2")
        vc2.tick()  # agent2: 1
        vc2.tick()  # agent2: 2
        
        vc1.merge(vc2)
        # After merge: agent1 should be 2 (max(1,0)+1), agent2 should be 2
        assert vc1.clock["agent1"] == 2
        assert vc1.clock["agent2"] == 2
    
    def test_happens_before(self):
        """Test happens-before relationship."""
        vc1 = VectorClock("agent1")
        vc1.tick()  # [agent1: 1]
        
        vc2 = VectorClock("agent1", {"agent1": 1})
        vc2.tick()  # [agent1: 2]
        
        assert vc1.happens_before(vc2)
        assert not vc2.happens_before(vc1)
    
    def test_concurrent(self):
        """Test concurrent events detection."""
        vc1 = VectorClock("agent1")
        vc1.tick()  # [agent1: 1]
        
        vc2 = VectorClock("agent2")
        vc2.tick()  # [agent2: 1]
        
        assert vc1.concurrent_with(vc2)
        assert vc2.concurrent_with(vc1)
    
    def test_compare(self):
        """Test clock comparison."""
        vc1 = VectorClock("agent1")
        vc1.tick()
        
        vc2 = vc1.copy()
        assert vc1.compare(vc2) == "equal"
        
        vc2.tick()
        assert vc1.compare(vc2) == "before"
        assert vc2.compare(vc1) == "after"
        
        vc3 = VectorClock("agent2")
        vc3.tick()
        assert vc1.compare(vc3) == "concurrent"
    
    def test_serialization(self):
        """Test serialization and deserialization."""
        vc1 = VectorClock("agent1")
        vc1.tick()
        vc1.tick()
        
        # Dict serialization
        vc_dict = vc1.to_dict()
        vc2 = VectorClock.from_dict(vc_dict)
        assert vc1.equals(vc2)
        
        # JSON serialization
        vc_json = vc1.to_json()
        vc3 = VectorClock.from_json(vc_json)
        assert vc1.equals(vc3)


class TestCausalityGraph:
    """Test causality graph functionality."""
    
    def test_initialization(self):
        """Test graph initialization."""
        graph = CausalityGraph()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_add_event(self):
        """Test adding events to graph."""
        graph = CausalityGraph()
        vc1 = VectorClock("agent1")
        vc1.tick()
        
        result = graph.add_event("e1", {"type": "test"}, vc1)
        assert result is True
        assert "e1" in graph.nodes
        assert "e1" in graph.vector_clocks
        
        # Adding same event again should fail
        result = graph.add_event("e1", {"type": "test2"}, vc1)
        assert result is False
    
    def test_add_causal_link(self):
        """Test adding causal links."""
        graph = CausalityGraph()
        vc1 = VectorClock("agent1")
        vc1.tick()
        
        graph.add_event("e1", {"type": "start"}, vc1)
        
        vc2 = vc1.copy()
        vc2.tick()
        graph.add_event("e2", {"type": "process"}, vc2)
        
        result = graph.add_causal_link("e1", "e2")
        assert result is True
        assert "e2" in graph.edges["e1"]
        assert "e1" in graph.reverse_edges["e2"]
    
    def test_cycle_detection(self):
        """Test that cycles are prevented."""
        graph = CausalityGraph()
        vc = VectorClock("agent1")
        
        graph.add_event("e1", {}, vc.copy())
        vc.tick()
        graph.add_event("e2", {}, vc.copy())
        vc.tick()
        graph.add_event("e3", {}, vc.copy())
        
        graph.add_causal_link("e1", "e2")
        graph.add_causal_link("e2", "e3")
        
        # This would create a cycle e3 -> e1 -> e2 -> e3
        result = graph.add_causal_link("e3", "e1")
        assert result is False
    
    def test_causal_chain(self):
        """Test retrieving causal chains."""
        graph = CausalityGraph()
        vc = VectorClock("agent1")
        
        graph.add_event("e1", {}, vc.copy(), causes=[])
        vc.tick()
        graph.add_event("e2", {}, vc.copy(), causes=["e1"])
        vc.tick()
        graph.add_event("e3", {}, vc.copy(), causes=["e2"])
        
        chain = graph.get_causal_chain("e3")
        assert chain == ["e1", "e2", "e3"]
    
    def test_descendants(self):
        """Test getting descendants."""
        graph = CausalityGraph()
        vc = VectorClock("agent1")
        
        graph.add_event("e1", {}, vc.copy())
        vc.tick()
        graph.add_event("e2", {}, vc.copy(), causes=["e1"])
        vc.tick()
        graph.add_event("e3", {}, vc.copy(), causes=["e1"])
        vc.tick()
        graph.add_event("e4", {}, vc.copy(), causes=["e2"])
        
        descendants = graph.get_descendants("e1")
        assert descendants == {"e2", "e3", "e4"}
    
    def test_consistency_verification(self):
        """Test temporal consistency verification."""
        graph = CausalityGraph()
        vc1 = VectorClock("agent1")
        vc1.tick()
        
        graph.add_event("e1", {}, vc1.copy())
        
        vc2 = vc1.copy()
        vc2.tick()
        graph.add_event("e2", {}, vc2, causes=["e1"])
        
        is_consistent, violations = graph.verify_consistency()
        assert is_consistent
        assert len(violations) == 0
    
    def test_concurrent_events(self):
        """Test finding concurrent events."""
        graph = CausalityGraph()
        
        vc1 = VectorClock("agent1")
        vc1.tick()
        graph.add_event("e1", {}, vc1)
        
        vc2 = VectorClock("agent2")
        vc2.tick()
        graph.add_event("e2", {}, vc2)
        
        concurrent = graph.get_concurrent_events("e1")
        assert "e2" in concurrent
    
    def test_serialization(self):
        """Test graph serialization."""
        graph = CausalityGraph()
        vc = VectorClock("agent1")
        
        graph.add_event("e1", {"data": "test"}, vc.copy())
        vc.tick()
        graph.add_event("e2", {"data": "test2"}, vc.copy(), causes=["e1"])
        
        # Dict serialization
        graph_dict = graph.to_dict()
        graph2 = CausalityGraph.from_dict(graph_dict)
        
        assert len(graph2.nodes) == 2
        assert "e1" in graph2.nodes
        assert "e2" in graph2.nodes
        
        # JSON serialization
        graph_json = graph.to_json()
        graph3 = CausalityGraph.from_json(graph_json)
        assert len(graph3.nodes) == 2
    
    def test_statistics(self):
        """Test graph statistics."""
        graph = CausalityGraph()
        vc = VectorClock("agent1")
        
        graph.add_event("e1", {}, vc.copy())
        vc.tick()
        graph.add_event("e2", {}, vc.copy(), causes=["e1"])
        vc.tick()
        graph.add_event("e3", {}, vc.copy(), causes=["e2"])
        
        stats = graph.get_stats()
        assert stats["event_count"] == 3
        assert stats["edge_count"] == 2
        assert stats["root_events"] == 1
        assert stats["leaf_events"] == 1


class TestTemporalEvent:
    """Test temporal event functionality."""
    
    def test_creation(self):
        """Test creating temporal events."""
        vc = VectorClock("agent1")
        vc.tick()
        
        event = TemporalEvent(
            event_id="e1",
            event_type="test_event",
            agent_id="agent1",
            data={"key": "value"},
            vector_clock=vc
        )
        
        assert event.event_id == "e1"
        assert event.event_type == "test_event"
        assert event.agent_id == "agent1"
        assert event.data["key"] == "value"
    
    def test_serialization(self):
        """Test event serialization."""
        vc = VectorClock("agent1")
        vc.tick()
        
        event1 = TemporalEvent(
            event_id="e1",
            event_type="test",
            agent_id="agent1",
            vector_clock=vc,
            causes=["e0"]
        )
        
        event_dict = event1.to_dict()
        event2 = TemporalEvent.from_dict(event_dict)
        
        assert event1.event_id == event2.event_id
        assert event1.event_type == event2.event_type
        assert event1.causes == event2.causes


class TestChronos:
    """Test Chronos temporal weight engine."""
    
    def test_initialization(self):
        """Test Chronos initialization."""
        chronos = Chronos("chronos-test")
        assert chronos.instance_id == "chronos-test"
        assert chronos.event_count == 0
        assert len(chronos.events) == 0
    
    def test_record_event(self):
        """Test recording events."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        event = chronos.record_event(
            event_id="e1",
            event_type="test_event",
            agent_id="agent1",
            data={"key": "value"}
        )
        
        assert event.event_id == "e1"
        assert chronos.event_count == 1
        assert "e1" in chronos.events
        assert "agent1" in chronos.agent_clocks
    
    def test_causal_recording(self):
        """Test recording causally related events."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        # Record first event
        e1 = chronos.record_event(
            event_id="e1",
            event_type="start",
            agent_id="agent1"
        )
        
        # Record dependent event
        e2 = chronos.record_event(
            event_id="e2",
            event_type="process",
            agent_id="agent1",
            causes=["e1"]
        )
        
        # Verify causality
        assert e1.vector_clock.happens_before(e2.vector_clock)
        chain = chronos.get_causal_chain("e2")
        assert chain == ["e1", "e2"]
    
    def test_temporal_weight_computation(self):
        """Test temporal weight computation."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        # Create a simple chain
        chronos.record_event("e1", "start", "agent1")
        chronos.record_event("e2", "process", "agent1", causes=["e1"])
        chronos.record_event("e3", "end", "agent1", causes=["e2"])
        
        # e1 should have higher weight (more descendants)
        weight_e1 = chronos.temporal_weights["e1"]
        weight_e3 = chronos.temporal_weights["e3"]
        
        assert weight_e1 > weight_e3
    
    def test_critical_event_weight(self):
        """Test that critical events get higher weights."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        normal_event = chronos.record_event(
            "e1", "normal_operation", "agent1"
        )
        
        security_event = chronos.record_event(
            "e2", "security_violation", "agent1"
        )
        
        # Security events should have higher weight
        assert security_event.temporal_weight > normal_event.temporal_weight
    
    def test_consistency_verification(self):
        """Test temporal consistency verification."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        chronos.record_event("e1", "start", "agent1")
        chronos.record_event("e2", "process", "agent1", causes=["e1"])
        
        is_consistent, violations = chronos.verify_consistency()
        assert is_consistent
        assert len(violations) == 0
    
    def test_drift_detection(self):
        """Test clock drift detection."""
        chronos = Chronos("chronos-test", enable_audit=False, drift_threshold_seconds=1.0)
        
        # Record first event
        now = datetime.now(timezone.utc)
        chronos.record_event("e1", "start", "agent1", timestamp=now)
        
        # Record second event with significant time gap
        later = now + timedelta(seconds=10)
        chronos.record_event("e2", "process", "agent1", causes=["e1"], timestamp=later)
        
        # Should detect drift
        assert len(chronos.drift_violations) > 0
    
    def test_concurrent_events(self):
        """Test detecting concurrent events."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        # Two events from different agents with no causal relationship
        chronos.record_event("e1", "task_a", "agent1")
        chronos.record_event("e2", "task_b", "agent2")
        
        concurrent = chronos.get_concurrent_events("e1")
        assert "e2" in concurrent
    
    def test_anomaly_detection(self):
        """Test anomaly detection."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        # Create events with varying weights - include a highly branched event
        chronos.record_event("e1", "start", "agent1")
        chronos.record_event("e2", "branch_1", "agent1", causes=["e1"])
        chronos.record_event("e3", "branch_2", "agent1", causes=["e1"])
        chronos.record_event("e4", "branch_3", "agent1", causes=["e1"])
        chronos.record_event("e5", "branch_4", "agent1", causes=["e1"])
        chronos.record_event("e6", "security_violation", "agent1", causes=["e2"])
        
        anomalies = chronos.detect_anomalies()
        
        # Should detect high-weight events (e1 has many descendants)
        high_weight_anomalies = [a for a in anomalies if a["type"] == "high_temporal_weight"]
        assert len(high_weight_anomalies) > 0
    
    def test_statistics(self):
        """Test getting statistics."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        chronos.record_event("e1", "start", "agent1")
        chronos.record_event("e2", "process", "agent2")
        
        stats = chronos.get_statistics()
        
        assert stats["total_events"] == 2
        assert stats["active_agents"] == 2
        assert "graph_stats" in stats
        assert "weight_stats" in stats
    
    def test_state_export_import(self):
        """Test state export and import."""
        chronos1 = Chronos("chronos-test", enable_audit=False)
        
        chronos1.record_event("e1", "start", "agent1")
        chronos1.record_event("e2", "process", "agent1", causes=["e1"])
        
        # Export state
        state = chronos1.export_state()
        
        # Import into new instance
        chronos2 = Chronos("chronos-test2", enable_audit=False)
        chronos2.import_state(state)
        
        assert chronos2.event_count == 2
        assert "e1" in chronos2.events
        assert "e2" in chronos2.events
        assert "agent1" in chronos2.agent_clocks
    
    def test_state_persistence(self, tmp_path):
        """Test state save and load from file."""
        state_file = tmp_path / "chronos_state.json"
        
        chronos1 = Chronos(
            "chronos-test",
            enable_audit=False,
            state_file=state_file
        )
        
        chronos1.record_event("e1", "start", "agent1")
        chronos1.record_event("e2", "process", "agent1", causes=["e1"])
        
        # Save state
        result = chronos1.save_state()
        assert result is True
        assert state_file.exists()
        
        # Load into new instance
        chronos2 = Chronos(
            "chronos-test",
            enable_audit=False,
            state_file=state_file
        )
        
        assert chronos2.event_count == 2
        assert "e1" in chronos2.events


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_distributed_event_tracking(self):
        """Test tracking events across multiple agents."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        # Agent 1 starts a task
        chronos.record_event("e1", "task_start", "agent1")
        
        # Agent 2 receives and processes
        chronos.record_event("e2", "task_received", "agent2", causes=["e1"])
        chronos.record_event("e3", "task_processing", "agent2", causes=["e2"])
        
        # Agent 3 receives results
        chronos.record_event("e4", "result_received", "agent3", causes=["e3"])
        
        # Verify causal chain
        chain = chronos.get_causal_chain("e4")
        assert chain == ["e1", "e2", "e3", "e4"]
        
        # Verify consistency
        is_consistent, _ = chronos.verify_consistency()
        assert is_consistent
        
        # Check statistics
        stats = chronos.get_statistics()
        assert stats["total_events"] == 4
        assert stats["active_agents"] == 3
    
    def test_complex_causality_graph(self):
        """Test complex causality patterns."""
        chronos = Chronos("chronos-test", enable_audit=False)
        
        # Create a branching pattern
        chronos.record_event("e1", "start", "agent1")
        
        # Two parallel branches
        chronos.record_event("e2", "branch_a", "agent2", causes=["e1"])
        chronos.record_event("e3", "branch_b", "agent3", causes=["e1"])
        
        # Both branches converge
        chronos.record_event("e4", "merge", "agent4", causes=["e2", "e3"])
        
        # Verify structure
        chain_to_e4 = chronos.get_causal_chain("e4")
        assert "e1" in chain_to_e4
        assert "e2" in chain_to_e4
        assert "e3" in chain_to_e4
        assert "e4" in chain_to_e4
        
        # e2 and e3 should be concurrent
        concurrent_with_e2 = chronos.get_concurrent_events("e2")
        assert "e3" in concurrent_with_e2
        
        # Verify weight (e1 should have high weight as it has multiple descendants)
        weight_e1 = chronos.temporal_weights["e1"]
        weight_e4 = chronos.temporal_weights["e4"]
        assert weight_e1 > weight_e4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
