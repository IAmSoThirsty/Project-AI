#!/usr/bin/env python3
#                                           [2026-04-11 01:44]
#                                          Productivity: Active
"""
Atropos Demonstration Script

Demonstrates the Atropos fate engine's capabilities:
1. Deterministic event ordering
2. Anti-rollback protection
3. Hash chain integrity
4. Replay attack detection
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.cognition.temporal.atropos import (
    Atropos,
    AtroposConfig,
    TemporalIntegrityError,
)


def demo_basic_usage():
    """Demonstrate basic event creation and ordering."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Event Creation and Ordering")
    print("=" * 60)

    atropos = Atropos()

    # Create events
    events = []
    for i in range(5):
        event = atropos.create_event(
            event_id=f"txn_{i:03d}",
            event_type="transaction",
            payload={"amount": i * 100, "user": f"user_{i}"},
            metadata={"priority": "normal"},
        )
        events.append(event)
        print(
            f"Created: {event.event_id} | "
            f"Lamport: {event.lamport_timestamp} | "
            f"Sequence: {event.monotonic_sequence} | "
            f"Hash: {event.event_hash[:16]}..."
        )

    # Verify ordering
    print("\nVerifying temporal ordering...")
    for i in range(len(events) - 1):
        assert events[i].lamport_timestamp < events[i + 1].lamport_timestamp
        assert events[i].monotonic_sequence < events[i + 1].monotonic_sequence
    print("✓ All events properly ordered")

    # Show statistics
    stats = atropos.get_statistics()
    print(f"\nStatistics:")
    print(f"  Events processed: {stats['events_processed']}")
    print(f"  Lamport time: {stats['lamport_time']}")
    print(f"  Monotonic sequence: {stats['monotonic_sequence']}")
    print(f"  Chain length: {stats['chain_length']}")


def demo_hash_chain_integrity():
    """Demonstrate hash chain and tamper detection."""
    print("\n" + "=" * 60)
    print("DEMO 2: Hash Chain Integrity and Tamper Detection")
    print("=" * 60)

    atropos = Atropos()

    # Create events
    event1 = atropos.create_event(
        event_id="payment_001",
        event_type="payment",
        payload={"amount": 1000},
    )
    print(f"Event 1: {event1.event_id} | Hash: {event1.event_hash[:16]}...")

    event2 = atropos.create_event(
        event_id="payment_002",
        event_type="payment",
        payload={"amount": 2000},
    )
    print(f"Event 2: {event2.event_id} | Hash: {event2.event_hash[:16]}...")

    # Verify hash integrity
    print("\nVerifying hash integrity...")
    assert event1.verify_hash()
    assert event2.verify_hash()
    print("✓ All hashes valid")

    # Attempt tampering
    print("\nAttempting to tamper with event payload...")
    original_amount = event1.payload["amount"]
    event1.payload["amount"] = 1000000  # Change amount!

    if not event1.verify_hash():
        print("✗ Hash verification failed (tampering detected)")
        print(f"  Original: {original_amount}")
        print(f"  Tampered: {event1.payload['amount']}")
    else:
        print("✓ Hash still valid (should not happen!)")


def demo_replay_detection():
    """Demonstrate replay attack detection."""
    print("\n" + "=" * 60)
    print("DEMO 3: Replay Attack Detection")
    print("=" * 60)

    config = AtroposConfig(strict_mode=True)
    atropos = Atropos(config)

    # Create legitimate event
    event = atropos.create_event(
        event_id="transfer_001",
        event_type="transfer",
        payload={"from": "alice", "to": "bob", "amount": 500},
    )
    print(f"Created: {event.event_id}")

    # Attempt to replay same event
    print("\nAttempting replay attack...")
    try:
        atropos.verify_event(event)
        print("✗ Replay succeeded (should not happen!)")
    except TemporalIntegrityError as e:
        print(f"✓ Replay blocked: {e}")

    stats = atropos.get_statistics()
    print(f"\nDuplicates detected: {stats['duplicates_detected']}")


def demo_anti_rollback():
    """Demonstrate anti-rollback protection with persistence."""
    print("\n" + "=" * 60)
    print("DEMO 4: Anti-Rollback Protection")
    print("=" * 60)

    persist_path = Path("atropos_counter_demo.txt")

    # First session
    print("Session 1: Creating events...")
    config1 = AtroposConfig(persistence_path=persist_path, strict_mode=True)
    atropos1 = Atropos(config1)

    for i in range(10):
        atropos1.create_event(
            event_id=f"evt_{i}",
            event_type="demo",
            payload={"index": i},
        )

    seq1 = atropos1.monotonic_counter.value
    print(f"  Final sequence: {seq1}")

    # Second session (simulating restart)
    print("\nSession 2: Restarting system...")
    config2 = AtroposConfig(persistence_path=persist_path, strict_mode=True)
    atropos2 = Atropos(config2)

    seq2 = atropos2.monotonic_counter.value
    print(f"  Loaded sequence: {seq2}")

    if seq2 == seq1:
        print("✓ Counter persisted correctly")
    else:
        print("✗ Counter rollback detected!")

    # Continue from persisted state
    print("\nContinuing from persisted state...")
    event = atropos2.create_event(
        event_id="evt_10",
        event_type="demo",
        payload={"index": 10},
    )
    print(f"  New sequence: {event.monotonic_sequence}")

    if event.monotonic_sequence == seq1 + 1:
        print("✓ Sequence continues correctly")

    # Cleanup
    if persist_path.exists():
        persist_path.unlink()
        print(f"\nCleaned up: {persist_path}")


def demo_distributed_causality():
    """Demonstrate causality preservation in distributed systems."""
    print("\n" + "=" * 60)
    print("DEMO 5: Distributed System Causality")
    print("=" * 60)

    # Two independent nodes
    print("Initializing two independent nodes...")
    node1 = Atropos()
    node2 = Atropos()

    # Node 1 creates event
    print("\nNode 1: Creating event...")
    event1 = node1.create_event(
        event_id="node1_evt1",
        event_type="distributed",
        payload={"node": 1, "action": "start"},
    )
    print(
        f"  Event: {event1.event_id} | Lamport: {event1.lamport_timestamp}"
    )

    # Node 2 receives event from Node 1
    print("\nNode 2: Receiving event from Node 1...")
    node2.receive_event(event1, remote_lamport=event1.lamport_timestamp)
    print(f"  Node 2 Lamport time: {node2.lamport_clock.time}")

    # Node 2 creates event (should have higher timestamp)
    print("\nNode 2: Creating event...")
    event2 = node2.create_event(
        event_id="node2_evt1",
        event_type="distributed",
        payload={"node": 2, "action": "process"},
    )
    print(
        f"  Event: {event2.event_id} | Lamport: {event2.lamport_timestamp}"
    )

    # Verify causality
    print("\nVerifying causality...")
    if event2.lamport_timestamp > event1.lamport_timestamp:
        print("✓ Causality preserved: event2 happens after event1")
    else:
        print("✗ Causality violation!")


def demo_audit_trail():
    """Demonstrate immutable audit trail."""
    print("\n" + "=" * 60)
    print("DEMO 6: Immutable Audit Trail")
    print("=" * 60)

    atropos = Atropos()

    # Create sequence of events
    print("Creating event sequence...")
    event_types = ["login", "read", "write", "update", "delete", "logout"]
    for i, evt_type in enumerate(event_types):
        atropos.create_event(
            event_id=f"audit_{i:03d}",
            event_type=evt_type,
            payload={"user": "admin", "timestamp": time.time()},
        )
        print(f"  {i+1}. {evt_type}")

    # Get audit trail
    print("\nAudit trail (last 5 events):")
    trail = atropos.get_audit_trail(limit=5)
    for i, event_id in enumerate(trail, 1):
        print(f"  {i}. {event_id}")

    # Verify chain integrity
    print("\nVerifying chain integrity...")
    if atropos.verify_chain_integrity():
        print("✓ Audit trail intact")
    else:
        print("✗ Audit trail compromised!")

    stats = atropos.get_statistics()
    print(f"\nTotal events in trail: {stats['events_processed']}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("ATROPOS FATE ENGINE DEMONSTRATION")
    print("Anti-Rollback Protection & Deterministic Event Ordering")
    print("=" * 60)

    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Hash Chain Integrity", demo_hash_chain_integrity),
        ("Replay Detection", demo_replay_detection),
        ("Anti-Rollback", demo_anti_rollback),
        ("Distributed Causality", demo_distributed_causality),
        ("Audit Trail", demo_audit_trail),
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Demo '{name}' failed: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
