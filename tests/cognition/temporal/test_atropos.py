#                                           [2026-04-11 01:44]
#                                          Productivity: Active
"""
Comprehensive Tests for Atropos Fate Engine

Tests all anti-rollback and replay protection mechanisms:
1. Lamport clock deterministic ordering
2. Monotonic counter anti-rollback
3. Hash chain integrity
4. Replay attack detection
5. Event verification
6. Distributed event synchronization
"""

import pytest
import tempfile
import time
from pathlib import Path

from src.cognition.temporal.atropos import (
    Atropos,
    AtroposConfig,
    CounterBackend,
    HashChain,
    LamportClock,
    MonotonicCounter,
    ReplayDetector,
    TemporalEvent,
    TemporalIntegrityError,
)


class TestLamportClock:
    """Test Lamport logical clock implementation."""

    def test_initialization(self):
        """Test clock initialization."""
        clock = LamportClock()
        assert clock.time == 0

        clock_with_initial = LamportClock(initial_time=100)
        assert clock_with_initial.time == 100

    def test_tick(self):
        """Test local event increment."""
        clock = LamportClock()
        
        t1 = clock.tick()
        assert t1 == 1
        assert clock.time == 1

        t2 = clock.tick()
        assert t2 == 2
        assert clock.time == 2

    def test_update_with_higher_timestamp(self):
        """Test update with higher remote timestamp."""
        clock = LamportClock()
        clock.tick()  # Now at 1

        # Receive message with timestamp 5
        new_time = clock.update(5)
        assert new_time == 6  # max(1, 5) + 1
        assert clock.time == 6

    def test_update_with_lower_timestamp(self):
        """Test update with lower remote timestamp."""
        clock = LamportClock(initial_time=10)

        # Receive message with timestamp 3
        new_time = clock.update(3)
        assert new_time == 11  # max(10, 3) + 1
        assert clock.time == 11

    def test_happens_before(self):
        """Test happened-before relationship."""
        clock = LamportClock()
        
        t1 = clock.tick()  # 1
        t2 = clock.tick()  # 2
        
        assert clock.happens_before(t1, t2)
        assert not clock.happens_before(t2, t1)
        assert not clock.happens_before(t1, t1)

    def test_deterministic_ordering(self):
        """Test total ordering of events."""
        clock = LamportClock()
        
        timestamps = [clock.tick() for _ in range(10)]
        
        # All timestamps should be strictly increasing
        for i in range(len(timestamps) - 1):
            assert timestamps[i] < timestamps[i + 1]


class TestMonotonicCounter:
    """Test monotonic counter anti-rollback protection."""

    def test_initialization(self):
        """Test counter initialization."""
        counter = MonotonicCounter()
        assert counter.value == 0
        assert counter.backend == CounterBackend.SOFTWARE

    def test_increment(self):
        """Test counter increment."""
        counter = MonotonicCounter()
        
        v1 = counter.increment()
        assert v1 == 1
        assert counter.value == 1

        v2 = counter.increment()
        assert v2 == 2
        assert counter.value == 2

    def test_verify_monotonic(self):
        """Test monotonic verification."""
        counter = MonotonicCounter()
        counter.increment()  # Now at 1

        assert counter.verify_monotonic(2)  # 2 > 1
        assert counter.verify_monotonic(10)  # 10 > 1
        assert not counter.verify_monotonic(1)  # 1 == 1
        assert not counter.verify_monotonic(0)  # 0 < 1

    def test_try_update_success(self):
        """Test successful monotonic update."""
        counter = MonotonicCounter()
        counter.increment()  # Now at 1

        result = counter.try_update(5)
        assert result is True
        assert counter.value == 5

    def test_try_update_failure(self):
        """Test rejected non-monotonic update."""
        counter = MonotonicCounter()
        counter.increment()  # Now at 1
        counter.increment()  # Now at 2

        # Try to rollback
        result = counter.try_update(1)
        assert result is False
        assert counter.value == 2  # Unchanged

        # Try to update to same value
        result = counter.try_update(2)
        assert result is False
        assert counter.value == 2

    def test_persistence(self):
        """Test counter persistence and recovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_path = Path(tmpdir) / "counter.txt"

            # Create counter and increment
            counter1 = MonotonicCounter(persistence_path=persist_path)
            counter1.increment()
            counter1.increment()
            counter1.increment()
            assert counter1.value == 3

            # Create new counter with same persistence
            counter2 = MonotonicCounter(persistence_path=persist_path)
            assert counter2.value == 3  # Loaded from disk

    def test_anti_rollback_on_load(self):
        """Test that persisted value prevents rollback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_path = Path(tmpdir) / "counter.txt"

            # Create counter at high value
            counter1 = MonotonicCounter(persistence_path=persist_path)
            for _ in range(10):
                counter1.increment()
            assert counter1.value == 10

            # Try to create counter with lower initial value
            counter2 = MonotonicCounter(
                initial_value=5, persistence_path=persist_path
            )
            # Should load persisted value (10), not initial (5)
            assert counter2.value == 10


class TestHashChain:
    """Test hash chain implementation."""

    def test_initialization(self):
        """Test chain initialization."""
        chain = HashChain()
        assert chain.genesis_hash
        assert chain.chain_length == 0
        assert chain.previous_hash == chain.genesis_hash

    def test_custom_genesis(self):
        """Test custom genesis data."""
        chain1 = HashChain(genesis_data="CUSTOM_GENESIS")
        chain2 = HashChain(genesis_data="CUSTOM_GENESIS")
        chain3 = HashChain(genesis_data="DIFFERENT")

        # Same genesis data = same hash
        assert chain1.genesis_hash == chain2.genesis_hash
        # Different genesis = different hash
        assert chain1.genesis_hash != chain3.genesis_hash

    def test_link_event(self):
        """Test linking events to chain."""
        chain = HashChain()
        
        hash1 = chain.link_event("event_1")
        assert hash1
        assert chain.chain_length == 1
        assert chain.previous_hash == hash1

        hash2 = chain.link_event("event_2")
        assert hash2
        assert hash2 != hash1  # Different events = different hashes
        assert chain.chain_length == 2
        assert chain.previous_hash == hash2

    def test_chain_determinism(self):
        """Test chain produces deterministic hashes."""
        chain1 = HashChain(genesis_data="TEST")
        chain2 = HashChain(genesis_data="TEST")

        events = ["event_1", "event_2", "event_3"]
        
        hashes1 = [chain1.link_event(e) for e in events]
        hashes2 = [chain2.link_event(e) for e in events]

        # Same events in same order = same hashes
        assert hashes1 == hashes2

    def test_verify_link(self):
        """Test link verification."""
        chain = HashChain()
        
        prev_hash = chain.previous_hash
        event_data = "test_event"
        event_hash = chain.link_event(event_data)

        # Verify link is valid
        assert chain.verify_link(prev_hash, event_data, event_hash)

        # Verify invalid link is rejected
        assert not chain.verify_link(prev_hash, "different_data", event_hash)
        assert not chain.verify_link("wrong_prev", event_data, event_hash)

    def test_chain_immutability(self):
        """Test that changing history invalidates chain."""
        chain = HashChain()
        
        hash1 = chain.link_event("event_1")
        prev_hash_1 = hash1
        
        hash2 = chain.link_event("event_2")
        
        # Try to verify event_2 with wrong previous hash
        assert not chain.verify_link("wrong_hash", "event_2", hash2)


class TestReplayDetector:
    """Test replay attack detection."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = ReplayDetector()
        assert detector.window_size == 10000
        assert detector.enable_gap_detection is True

    def test_check_duplicate(self):
        """Test duplicate detection."""
        detector = ReplayDetector()
        
        event = TemporalEvent(
            event_id="evt_1",
            event_type="test",
            payload={},
            lamport_timestamp=1,
            monotonic_sequence=1,
            physical_timestamp=time.time(),
            previous_hash="genesis",
        )
        
        # First time = not duplicate
        assert not detector.check_duplicate("evt_1")
        
        # Record event
        detector.record_event(event)
        
        # Second time = duplicate
        assert detector.check_duplicate("evt_1")

    def test_check_ordering_lamport(self):
        """Test Lamport ordering violation detection."""
        detector = ReplayDetector()
        
        # Normal ordering
        assert not detector.check_ordering(lamport_ts=1, monotonic_seq=1)
        detector._highest_lamport = 5
        
        # Backwards Lamport time
        assert detector.check_ordering(lamport_ts=3, monotonic_seq=6)

    def test_check_ordering_monotonic(self):
        """Test monotonic ordering violation detection."""
        detector = ReplayDetector()
        
        detector._highest_monotonic = 10
        
        # Backwards monotonic sequence
        assert detector.check_ordering(lamport_ts=11, monotonic_seq=5)
        
        # Same monotonic sequence
        assert detector.check_ordering(lamport_ts=11, monotonic_seq=10)

    def test_check_sequence_gap(self):
        """Test sequence gap detection."""
        detector = ReplayDetector(enable_gap_detection=True)
        
        # First event
        gap = detector.check_sequence_gap(1)
        assert gap is None  # No gap yet
        detector._expected_sequence = 1
        
        # Next event
        gap = detector.check_sequence_gap(2)
        assert gap is None  # Sequential
        detector._expected_sequence = 2
        
        # Gap!
        gap = detector.check_sequence_gap(5)
        assert gap == 2  # Missing 3 and 4

    def test_gap_detection_disabled(self):
        """Test gap detection can be disabled."""
        detector = ReplayDetector(enable_gap_detection=False)
        
        detector._expected_sequence = 1
        gap = detector.check_sequence_gap(100)
        assert gap is None  # Disabled

    def test_record_event(self):
        """Test event recording."""
        detector = ReplayDetector()
        
        event = TemporalEvent(
            event_id="evt_1",
            event_type="test",
            payload={},
            lamport_timestamp=10,
            monotonic_sequence=5,
            physical_timestamp=time.time(),
            previous_hash="genesis",
        )
        
        detector.record_event(event)
        
        assert detector._highest_lamport == 10
        assert detector._highest_monotonic == 5
        assert "evt_1" in detector._event_ids

    def test_window_size_limit(self):
        """Test that window size is enforced."""
        detector = ReplayDetector(window_size=10)
        
        # Record 20 events
        for i in range(20):
            event = TemporalEvent(
                event_id=f"evt_{i}",
                event_type="test",
                payload={},
                lamport_timestamp=i,
                monotonic_sequence=i,
                physical_timestamp=time.time(),
                previous_hash="genesis",
            )
            detector.record_event(event)
        
        # Only last 10 should be in window
        assert len(detector._seen_events) == 10
        # First events should be pruned
        assert not detector.check_duplicate("evt_0")
        # Recent events should be there
        assert detector.check_duplicate("evt_19")


class TestTemporalEvent:
    """Test temporal event implementation."""

    def test_creation(self):
        """Test event creation."""
        event = TemporalEvent(
            event_id="test_1",
            event_type="test_event",
            payload={"data": "value"},
            lamport_timestamp=1,
            monotonic_sequence=1,
            physical_timestamp=time.time(),
            previous_hash="genesis",
        )
        
        assert event.event_id == "test_1"
        assert event.event_type == "test_event"
        assert event.event_hash  # Hash computed automatically

    def test_hash_computation(self):
        """Test hash is computed correctly."""
        ts = time.time()
        event = TemporalEvent(
            event_id="test_1",
            event_type="test",
            payload={"key": "value"},
            lamport_timestamp=1,
            monotonic_sequence=1,
            physical_timestamp=ts,
            previous_hash="prev",
        )
        
        # Hash should be deterministic
        hash1 = event.event_hash
        hash2 = event._compute_hash()
        assert hash1 == hash2

    def test_verify_hash(self):
        """Test hash verification."""
        event = TemporalEvent(
            event_id="test_1",
            event_type="test",
            payload={},
            lamport_timestamp=1,
            monotonic_sequence=1,
            physical_timestamp=time.time(),
            previous_hash="prev",
        )
        
        assert event.verify_hash()
        
        # Tamper with event
        event.payload = {"tampered": True}
        assert not event.verify_hash()

    def test_to_dict(self):
        """Test conversion to dictionary."""
        ts = time.time()
        event = TemporalEvent(
            event_id="test_1",
            event_type="test",
            payload={"key": "value"},
            lamport_timestamp=1,
            monotonic_sequence=1,
            physical_timestamp=ts,
            previous_hash="prev",
            metadata={"source": "test"},
        )
        
        d = event.to_dict()
        
        assert d["event_id"] == "test_1"
        assert d["event_type"] == "test"
        assert d["lamport_timestamp"] == 1
        assert d["monotonic_sequence"] == 1
        assert "iso_timestamp" in d


class TestAtropos:
    """Test Atropos fate engine integration."""

    def test_initialization(self):
        """Test engine initialization."""
        atropos = Atropos()
        
        assert atropos.lamport_clock
        assert atropos.monotonic_counter
        assert atropos.hash_chain
        assert atropos.replay_detector

    def test_create_event(self):
        """Test event creation."""
        atropos = Atropos()
        
        event = atropos.create_event(
            event_id="evt_1",
            event_type="test",
            payload={"data": "value"},
        )
        
        assert event.event_id == "evt_1"
        assert event.lamport_timestamp == 1
        assert event.monotonic_sequence == 1
        assert event.event_hash
        assert event.previous_hash == atropos.hash_chain.genesis_hash

    def test_sequential_events(self):
        """Test sequential event creation."""
        atropos = Atropos()
        
        events = []
        for i in range(5):
            event = atropos.create_event(
                event_id=f"evt_{i}",
                event_type="test",
                payload={"index": i},
            )
            events.append(event)
        
        # Check ordering
        for i in range(len(events) - 1):
            assert events[i].lamport_timestamp < events[i + 1].lamport_timestamp
            assert events[i].monotonic_sequence < events[i + 1].monotonic_sequence
            # Each event linked to previous
            assert events[i + 1].previous_hash != events[i].previous_hash

    def test_verify_event_success(self):
        """Test successful event verification."""
        atropos = Atropos()
        
        # Create event manually (not through create_event to avoid recording it)
        event = TemporalEvent(
            event_id="evt_1",
            event_type="test",
            payload={},
            lamport_timestamp=1,
            monotonic_sequence=1,
            physical_timestamp=time.time(),
            previous_hash="genesis",
        )
        
        # Event should verify (first time seeing it)
        assert atropos.verify_event(event)

    def test_verify_duplicate_detection(self):
        """Test duplicate event detection."""
        atropos = Atropos(AtroposConfig(strict_mode=False))
        
        event = atropos.create_event(
            event_id="evt_1",
            event_type="test",
            payload={},
        )
        
        # Try to verify same event again
        is_valid = atropos.verify_event(event)
        assert not is_valid  # Duplicate should fail

    def test_verify_duplicate_strict_mode(self):
        """Test duplicate in strict mode raises error."""
        atropos = Atropos(AtroposConfig(strict_mode=True))
        
        event = atropos.create_event(
            event_id="evt_1",
            event_type="test",
            payload={},
        )
        
        # Try to verify same event again in strict mode
        with pytest.raises(TemporalIntegrityError):
            atropos.verify_event(event)

    def test_verify_ordering_violation(self):
        """Test ordering violation detection."""
        atropos = Atropos(AtroposConfig(strict_mode=False))
        
        # Create normal event
        event1 = atropos.create_event(
            event_id="evt_1",
            event_type="test",
            payload={},
        )
        
        # Create event with backwards timestamp
        event2 = TemporalEvent(
            event_id="evt_2",
            event_type="test",
            payload={},
            lamport_timestamp=0,  # Before event1
            monotonic_sequence=10,
            physical_timestamp=time.time(),
            previous_hash="prev",
        )
        
        is_valid = atropos.verify_event(event2)
        assert not is_valid  # Ordering violation

    def test_verify_hash_failure(self):
        """Test hash verification failure."""
        atropos = Atropos(AtroposConfig(strict_mode=False))
        
        event = atropos.create_event(
            event_id="evt_1",
            event_type="test",
            payload={"original": True},
        )
        
        # Tamper with event
        event.payload["tampered"] = True
        
        is_valid = atropos.verify_event(event)
        assert not is_valid  # Hash mismatch

    def test_receive_event(self):
        """Test receiving external event."""
        atropos = Atropos()
        
        # Create external event
        external_event = TemporalEvent(
            event_id="external_1",
            event_type="external",
            payload={"source": "remote"},
            lamport_timestamp=5,
            monotonic_sequence=1,
            physical_timestamp=time.time(),
            previous_hash="remote_chain",
        )
        
        # Receive event with remote Lamport timestamp
        accepted = atropos.receive_event(external_event, remote_lamport=5)
        
        # Should update local Lamport clock
        assert atropos.lamport_clock.time == 6  # max(0, 5) + 1

    def test_replay_attack_prevention(self):
        """Test comprehensive replay attack prevention."""
        atropos = Atropos(AtroposConfig(strict_mode=True))
        
        # Create legitimate event
        event = atropos.create_event(
            event_id="evt_1",
            event_type="test",
            payload={"data": "original"},
        )
        
        # Attempt 1: Replay same event
        with pytest.raises(TemporalIntegrityError):
            atropos.verify_event(event)
        
        # Attempt 2: Create event with old timestamp
        old_event = TemporalEvent(
            event_id="evt_replay",
            event_type="test",
            payload={},
            lamport_timestamp=0,  # Before current time
            monotonic_sequence=0,
            physical_timestamp=time.time(),
            previous_hash="prev",
        )
        
        with pytest.raises(TemporalIntegrityError):
            atropos.verify_event(old_event)

    def test_get_statistics(self):
        """Test statistics collection."""
        atropos = Atropos()
        
        # Create some events
        for i in range(5):
            atropos.create_event(
                event_id=f"evt_{i}",
                event_type="test",
                payload={},
            )
        
        stats = atropos.get_statistics()
        
        assert stats["events_processed"] == 5
        assert stats["lamport_time"] == 5
        assert stats["monotonic_sequence"] == 5
        assert stats["chain_length"] == 5
        assert stats["duplicates_detected"] == 0

    def test_get_audit_trail(self):
        """Test audit trail retrieval."""
        atropos = Atropos()
        
        # Create events
        event_ids = [f"evt_{i}" for i in range(10)]
        for event_id in event_ids:
            atropos.create_event(
                event_id=event_id,
                event_type="test",
                payload={},
            )
        
        # Get full trail
        trail = atropos.get_audit_trail()
        assert len(trail) == 10
        assert trail == event_ids
        
        # Get limited trail
        trail_limited = atropos.get_audit_trail(limit=5)
        assert len(trail_limited) == 5
        assert trail_limited == event_ids[-5:]

    def test_persistence(self):
        """Test monotonic counter persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_path = Path(tmpdir) / "counter.txt"
            config = AtroposConfig(persistence_path=persist_path)
            
            # Create first engine and generate events
            atropos1 = Atropos(config)
            for i in range(5):
                atropos1.create_event(
                    event_id=f"evt_{i}",
                    event_type="test",
                    payload={},
                )
            
            seq1 = atropos1.monotonic_counter.value
            assert seq1 == 5
            
            # Create second engine - should load persisted state
            atropos2 = Atropos(config)
            assert atropos2.monotonic_counter.value == 5
            
            # Continue from persisted state
            event = atropos2.create_event(
                event_id="evt_6",
                event_type="test",
                payload={},
            )
            assert event.monotonic_sequence == 6

    def test_verify_chain_integrity(self):
        """Test chain integrity verification."""
        atropos = Atropos()
        
        # Create clean chain
        for i in range(10):
            atropos.create_event(
                event_id=f"evt_{i}",
                event_type="test",
                payload={},
            )
        
        assert atropos.verify_chain_integrity()


class TestAntiRollbackScenarios:
    """Test real-world anti-rollback attack scenarios."""

    def test_time_rewind_attack(self):
        """Test prevention of time rewind attack."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persist_path = Path(tmpdir) / "counter.txt"
            config = AtroposConfig(
                persistence_path=persist_path, strict_mode=True
            )
            
            # Legitimate sequence
            atropos1 = Atropos(config)
            for i in range(10):
                atropos1.create_event(
                    event_id=f"evt_{i}",
                    event_type="test",
                    payload={},
                )
            
            # Attacker tries to rewind by creating new engine
            atropos2 = Atropos(config)
            
            # Counter should load from disk, preventing rewind
            assert atropos2.monotonic_counter.value == 10
            
            # Next event continues from persisted state
            event = atropos2.create_event(
                event_id="evt_10",
                event_type="test",
                payload={},
            )
            assert event.monotonic_sequence == 11

    def test_replay_with_modification(self):
        """Test detection of replayed event with modified payload."""
        atropos = Atropos(AtroposConfig(strict_mode=True))
        
        # Original event
        event = atropos.create_event(
            event_id="evt_1",
            event_type="payment",
            payload={"amount": 100},
        )
        
        # Attacker modifies payload
        event.payload["amount"] = 1000000
        
        # Hash verification should fail
        with pytest.raises(TemporalIntegrityError):
            atropos.verify_event(event)

    def test_sequence_gap_attack(self):
        """Test detection of missing events (sequence gap)."""
        atropos = Atropos(AtroposConfig(strict_mode=False))
        
        # Create events 1, 2, 3
        for i in range(1, 4):
            atropos.create_event(
                event_id=f"evt_{i}",
                event_type="test",
                payload={},
            )
        
        # Attacker tries to skip to event 10
        gap_event = TemporalEvent(
            event_id="evt_10",
            event_type="test",
            payload={},
            lamport_timestamp=10,
            monotonic_sequence=10,
            physical_timestamp=time.time(),
            previous_hash="fake",
        )
        
        # Should detect gap
        atropos.verify_event(gap_event)
        stats = atropos.get_statistics()
        assert stats["sequence_gaps"] > 0

    def test_distributed_causality_preservation(self):
        """Test causality preservation across distributed systems."""
        # Two Atropos instances (different nodes)
        atropos_node1 = Atropos()
        atropos_node2 = Atropos()
        
        # Node 1 creates event
        event1 = atropos_node1.create_event(
            event_id="node1_evt1",
            event_type="distributed",
            payload={"node": 1},
        )
        
        # Node 2 receives and processes
        atropos_node2.receive_event(event1, remote_lamport=event1.lamport_timestamp)
        
        # Node 2's clock should advance
        assert atropos_node2.lamport_clock.time > event1.lamport_timestamp
        
        # Node 2 creates event (should have higher timestamp)
        event2 = atropos_node2.create_event(
            event_id="node2_evt1",
            event_type="distributed",
            payload={"node": 2},
        )
        
        # Causality preserved: event2 happens after event1
        assert event2.lamport_timestamp > event1.lamport_timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
