#                                           [2026-04-09 04:26]
#                                          Productivity: Active
"""
Temporal Consistency Tests

Tests for causal ordering, anti-rollback, and clock synchronization
in the Temporal/Liara agent system.
"""

import pytest
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from dataclasses import dataclass, field
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import asyncio


@dataclass
class Event:
    """Represents a temporal event with causal ordering."""
    event_id: str
    timestamp: datetime
    causal_dependencies: List[str] = field(default_factory=list)
    vector_clock: Dict[str, int] = field(default_factory=dict)
    agent_id: str = "default"


class VectorClock:
    """Vector clock for causal ordering."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.clock: Dict[str, int] = {agent_id: 0}
        self._lock = Lock()
    
    def tick(self) -> Dict[str, int]:
        """Increment local clock."""
        with self._lock:
            self.clock[self.agent_id] = self.clock.get(self.agent_id, 0) + 1
            return self.clock.copy()
    
    def update(self, other_clock: Dict[str, int]) -> None:
        """Update clock with received vector clock."""
        with self._lock:
            for agent_id, timestamp in other_clock.items():
                self.clock[agent_id] = max(
                    self.clock.get(agent_id, 0), 
                    timestamp
                )
            self.clock[self.agent_id] = self.clock.get(self.agent_id, 0) + 1
    
    def happens_before(self, clock_a: Dict[str, int], clock_b: Dict[str, int]) -> bool:
        """Check if clock_a happens before clock_b."""
        all_agents = set(clock_a.keys()) | set(clock_b.keys())
        less_or_equal = all(
            clock_a.get(agent, 0) <= clock_b.get(agent, 0) 
            for agent in all_agents
        )
        strictly_less = any(
            clock_a.get(agent, 0) < clock_b.get(agent, 0) 
            for agent in all_agents
        )
        return less_or_equal and strictly_less


class TemporalStateManager:
    """Manages temporal state with anti-rollback guarantees."""
    
    def __init__(self):
        self.states: List[Dict[str, Any]] = []
        self.current_version = 0
        self._lock = Lock()
        self.committed_versions = set()
    
    def append_state(self, state: Dict[str, Any]) -> int:
        """Append new state and return version number."""
        with self._lock:
            version = len(self.states)
            state['version'] = version
            state['timestamp'] = datetime.now(timezone.utc)
            self.states.append(state)
            self.current_version = version
            return version
    
    def commit_version(self, version: int) -> bool:
        """Commit a version (prevents rollback)."""
        with self._lock:
            if version > self.current_version:
                return False
            self.committed_versions.add(version)
            return True
    
    def can_rollback_to(self, version: int) -> bool:
        """Check if rollback to version is allowed."""
        with self._lock:
            if version in self.committed_versions:
                return False
            if version >= self.current_version:
                return False
            return True
    
    def get_state(self, version: int) -> Dict[str, Any]:
        """Get state at specific version."""
        with self._lock:
            if version < 0 or version >= len(self.states):
                raise ValueError(f"Invalid version: {version}")
            return self.states[version].copy()


class TestCausalOrdering:
    """Test causal ordering of events."""
    
    def test_vector_clock_initialization(self):
        """Test vector clock initializes correctly."""
        vc = VectorClock("agent-1")
        assert vc.agent_id == "agent-1"
        assert vc.clock == {"agent-1": 0}
    
    def test_vector_clock_tick(self):
        """Test vector clock tick increments local time."""
        vc = VectorClock("agent-1")
        clock1 = vc.tick()
        clock2 = vc.tick()
        
        assert clock1["agent-1"] == 1
        assert clock2["agent-1"] == 2
    
    def test_vector_clock_update(self):
        """Test vector clock update merges clocks."""
        vc1 = VectorClock("agent-1")
        vc2 = VectorClock("agent-2")
        
        vc1.tick()
        vc1.tick()
        clock1 = vc1.clock.copy()
        
        vc2.tick()
        vc2.update(clock1)
        
        assert vc2.clock["agent-1"] == 2
        assert vc2.clock["agent-2"] == 2
    
    def test_happens_before_relation(self):
        """Test happens-before relationship detection."""
        vc = VectorClock("agent-1")
        
        clock1 = {"agent-1": 1, "agent-2": 0}
        clock2 = {"agent-1": 2, "agent-2": 1}
        clock3 = {"agent-1": 1, "agent-2": 1}
        
        assert vc.happens_before(clock1, clock2)
        assert not vc.happens_before(clock2, clock1)
        assert not vc.happens_before(clock1, clock3)
        assert not vc.happens_before(clock3, clock1)
    
    def test_concurrent_events_detection(self):
        """Test detection of concurrent (causally independent) events."""
        vc = VectorClock("agent-1")
        
        clock1 = {"agent-1": 2, "agent-2": 0}
        clock2 = {"agent-1": 0, "agent-2": 2}
        
        # Neither happens before the other = concurrent
        assert not vc.happens_before(clock1, clock2)
        assert not vc.happens_before(clock2, clock1)
    
    def test_causal_chain_ordering(self):
        """Test ordering of causal chain of events."""
        events = []
        vc = VectorClock("agent-1")
        
        for i in range(5):
            clock = vc.tick()
            events.append(Event(
                event_id=f"event-{i}",
                timestamp=datetime.now(timezone.utc),
                vector_clock=clock.copy(),
                agent_id="agent-1"
            ))
        
        for i in range(len(events) - 1):
            assert vc.happens_before(
                events[i].vector_clock,
                events[i + 1].vector_clock
            )
    
    def test_multi_agent_causal_ordering(self):
        """Test causal ordering across multiple agents."""
        vc1 = VectorClock("agent-1")
        vc2 = VectorClock("agent-2")
        
        # Agent 1 creates event
        clock1 = vc1.tick()
        
        # Agent 2 receives and creates dependent event
        vc2.update(clock1)
        clock2 = vc2.tick()
        
        # Agent 1 receives agent 2's event
        vc1.update(clock2)
        clock3 = vc1.tick()
        
        assert vc1.happens_before(clock1, clock2)
        assert vc1.happens_before(clock2, clock3)
        assert vc1.happens_before(clock1, clock3)


class TestAntiRollback:
    """Test anti-rollback guarantees."""
    
    def test_state_append_increments_version(self):
        """Test state append increments version number."""
        manager = TemporalStateManager()
        
        v1 = manager.append_state({"data": "state1"})
        v2 = manager.append_state({"data": "state2"})
        v3 = manager.append_state({"data": "state3"})
        
        assert v1 == 0
        assert v2 == 1
        assert v3 == 2
    
    def test_state_includes_timestamp(self):
        """Test appended states include timestamps."""
        manager = TemporalStateManager()
        
        before = datetime.now(timezone.utc)
        version = manager.append_state({"data": "test"})
        after = datetime.now(timezone.utc)
        
        state = manager.get_state(version)
        timestamp = state['timestamp']
        
        assert before <= timestamp <= after
    
    def test_commit_prevents_rollback(self):
        """Test committed versions cannot be rolled back."""
        manager = TemporalStateManager()
        
        v1 = manager.append_state({"data": "state1"})
        v2 = manager.append_state({"data": "state2"})
        
        manager.commit_version(v1)
        
        assert not manager.can_rollback_to(v1)
        assert manager.can_rollback_to(v2)
    
    def test_cannot_commit_future_version(self):
        """Test cannot commit versions that don't exist yet."""
        manager = TemporalStateManager()
        
        manager.append_state({"data": "state1"})
        
        result = manager.commit_version(99)
        assert result is False
    
    def test_multiple_commits(self):
        """Test multiple version commits."""
        manager = TemporalStateManager()
        
        versions = [
            manager.append_state({"data": f"state{i}"})
            for i in range(5)
        ]
        
        manager.commit_version(versions[0])
        manager.commit_version(versions[2])
        
        assert not manager.can_rollback_to(versions[0])
        assert manager.can_rollback_to(versions[1])
        assert not manager.can_rollback_to(versions[2])
        assert manager.can_rollback_to(versions[3])
    
    def test_concurrent_state_appends(self):
        """Test thread-safe state appending."""
        manager = TemporalStateManager()
        versions = []
        
        def append_states(thread_id: int, count: int):
            for i in range(count):
                version = manager.append_state({
                    "thread": thread_id,
                    "index": i
                })
                versions.append(version)
        
        threads = [
            Thread(target=append_states, args=(i, 10))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All versions should be unique
        assert len(versions) == 50
        assert len(set(versions)) == 50
        assert max(versions) == 49


class TestClockSynchronization:
    """Test clock synchronization mechanisms."""
    
    def test_logical_clock_monotonicity(self):
        """Test logical clock always increases."""
        vc = VectorClock("agent-1")
        
        clocks = [vc.tick() for _ in range(100)]
        
        for i in range(len(clocks) - 1):
            assert clocks[i]["agent-1"] < clocks[i + 1]["agent-1"]
    
    def test_clock_synchronization_after_update(self):
        """Test clock synchronization between agents."""
        vc1 = VectorClock("agent-1")
        vc2 = VectorClock("agent-2")
        
        for _ in range(5):
            vc1.tick()
        
        clock1 = vc1.clock.copy()
        vc2.update(clock1)
        
        assert vc2.clock["agent-1"] == 5
        assert vc2.clock["agent-2"] == 1
    
    def test_clock_drift_detection(self):
        """Test detection of clock drift between agents."""
        vc1 = VectorClock("agent-1")
        vc2 = VectorClock("agent-2")
        
        for _ in range(100):
            vc1.tick()
        
        for _ in range(10):
            vc2.tick()
        
        clock1 = vc1.clock["agent-1"]
        clock2 = vc2.clock["agent-2"]
        
        drift = abs(clock1 - clock2)
        assert drift == 90
    
    def test_ntp_like_synchronization(self):
        """Test NTP-like clock synchronization."""
        class NTPClock:
            def __init__(self, agent_id: str):
                self.agent_id = agent_id
                self.offset = 0
                self.local_time = 0
            
            def get_time(self) -> float:
                return self.local_time + self.offset
            
            def tick(self) -> None:
                self.local_time += 1
            
            def sync_with(self, remote_time: float, rtt: float) -> None:
                """Synchronize with remote clock (NTP algorithm)."""
                local_receive = self.local_time
                estimated_remote = remote_time + (rtt / 2)
                self.offset = estimated_remote - local_receive
        
        clock1 = NTPClock("agent-1")
        clock2 = NTPClock("agent-2")
        
        # Clock 1 is ahead by 10
        for _ in range(10):
            clock1.tick()
        
        # Simulate NTP sync
        t1 = clock1.get_time()
        rtt = 2.0
        clock2.sync_with(t1, rtt)
        
        # Clocks should be close after sync
        assert abs(clock1.get_time() - clock2.get_time()) < rtt
    
    def test_hybrid_logical_clock(self):
        """Test Hybrid Logical Clock (HLC) for combined physical/logical time."""
        class HybridLogicalClock:
            def __init__(self):
                self.physical_time = 0
                self.logical_counter = 0
            
            def tick(self, wall_clock: int) -> tuple:
                """Update HLC based on wall clock time."""
                if wall_clock > self.physical_time:
                    self.physical_time = wall_clock
                    self.logical_counter = 0
                else:
                    self.logical_counter += 1
                return (self.physical_time, self.logical_counter)
            
            def update(self, remote_pt: int, remote_lc: int, wall_clock: int) -> tuple:
                """Update HLC based on received timestamp."""
                max_pt = max(wall_clock, self.physical_time, remote_pt)
                
                if max_pt == self.physical_time == remote_pt:
                    self.logical_counter = max(self.logical_counter, remote_lc) + 1
                elif max_pt == self.physical_time:
                    self.logical_counter += 1
                elif max_pt == remote_pt:
                    self.logical_counter = remote_lc + 1
                else:
                    self.logical_counter = 0
                
                self.physical_time = max_pt
                return (self.physical_time, self.logical_counter)
        
        hlc1 = HybridLogicalClock()
        hlc2 = HybridLogicalClock()
        
        # Initial tick
        t1 = hlc1.tick(100)
        assert t1 == (100, 0)
        
        # Logical counter increments if physical time doesn't advance
        t2 = hlc1.tick(100)
        assert t2 == (100, 1)
        
        # Physical time advances, counter resets
        t3 = hlc1.tick(101)
        assert t3 == (101, 0)
        
        # Update from remote clock
        t4 = hlc2.update(101, 0, 95)
        assert t4[0] == 101  # Takes max physical time
    
    @pytest.mark.asyncio
    async def test_async_clock_synchronization(self):
        """Test clock synchronization in async environment."""
        async def agent_tick(vc: VectorClock, count: int) -> List[Dict[str, int]]:
            clocks = []
            for _ in range(count):
                await asyncio.sleep(0.001)
                clocks.append(vc.tick())
            return clocks
        
        vc = VectorClock("agent-1")
        
        results = await asyncio.gather(
            agent_tick(vc, 10),
            agent_tick(vc, 10),
            agent_tick(vc, 10)
        )
        
        all_clocks = [clock for result in results for clock in result]
        
        # All ticks should have unique, increasing values
        agent_values = [c["agent-1"] for c in all_clocks]
        assert len(set(agent_values)) == 30
        assert max(agent_values) == 30


class TestTemporalInvariants:
    """Test temporal invariants and consistency properties."""
    
    def test_causality_preservation(self):
        """Test causality is preserved across operations."""
        vc1 = VectorClock("agent-1")
        vc2 = VectorClock("agent-2")
        
        events = []
        
        # Create causal chain
        c1 = vc1.tick()
        events.append(("e1", c1.copy()))
        
        vc2.update(c1)
        c2 = vc2.tick()
        events.append(("e2", c2.copy()))
        
        vc1.update(c2)
        c3 = vc1.tick()
        events.append(("e3", c3.copy()))
        
        # Verify causal order preserved
        assert vc1.happens_before(events[0][1], events[1][1])
        assert vc1.happens_before(events[1][1], events[2][1])
    
    def test_no_time_travel(self):
        """Test events cannot travel back in time."""
        manager = TemporalStateManager()
        
        states = []
        for i in range(5):
            version = manager.append_state({"index": i})
            state = manager.get_state(version)
            states.append(state)
        
        # Timestamps must be monotonically increasing
        for i in range(len(states) - 1):
            assert states[i]['timestamp'] <= states[i + 1]['timestamp']
    
    def test_deterministic_replay(self):
        """Test deterministic replay of events."""
        manager = TemporalStateManager()
        
        operations = [
            {"op": "add", "value": 10},
            {"op": "multiply", "value": 2},
            {"op": "subtract", "value": 5},
        ]
        
        result = 0
        for op in operations:
            if op["op"] == "add":
                result += op["value"]
            elif op["op"] == "multiply":
                result *= op["value"]
            elif op["op"] == "subtract":
                result -= op["value"]
            
            manager.append_state({"result": result, "op": op})
        
        # Replay should produce same results
        replay_result = 0
        for i in range(len(operations)):
            state = manager.get_state(i)
            if state["op"]["op"] == "add":
                replay_result += state["op"]["value"]
            elif state["op"]["op"] == "multiply":
                replay_result *= state["op"]["value"]
            elif state["op"]["op"] == "subtract":
                replay_result -= state["op"]["value"]
        
        assert result == replay_result == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
