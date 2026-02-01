#!/usr/bin/env python3
"""
Demo: Wired Ethics Approvals System
Shows how ethics approvals emit events and integrate with governance.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.core.advanced_boot import BootProfile, get_advanced_boot
from app.core.event_spine import EventCategory, get_event_spine
from app.core.governance_graph import RelationshipType, get_governance_graph


def demo_ethics_approval_events():
    """Demo 1: Ethics approvals emit events."""
    print("\n" + "=" * 80)
    print("DEMO 1: Ethics Approvals Emit Events")
    print("=" * 80)

    boot = get_advanced_boot()
    event_spine = get_event_spine()

    # Track received events
    received_events = []

    def event_callback(event):
        received_events.append(event)
        print("\n📡 Event Received:")
        print(f"   Category: {event.category.value}")
        print(f"   Source: {event.source_domain}")
        print(f"   Decision: {event.payload.get('decision_type')}")
        print(f"   Subsystem: {event.payload.get('subsystem_id')}")
        print(f"   Approved: {event.payload.get('approved')}")
        print(f"   Reasoning: {event.payload.get('reasoning')}")
        print(f"   Event ID: {event.metadata.get('event_id')}")

    # Subscribe to governance decisions
    event_spine.subscribe(
        subscriber_id="demo_subscriber",
        subscriber_domain="demo",
        categories=[EventCategory.GOVERNANCE_DECISION],
        callback=event_callback,
    )

    # Set ethics-first profile
    boot.set_boot_profile(BootProfile.ETHICS_FIRST)

    # Request approvals for different subsystems
    subsystems = [
        ("tactical_edge_ai", "HIGH"),
        ("supply_logistics", "MEDIUM"),
        ("command_control", "CRITICAL"),
    ]

    print("\n📋 Requesting Ethics Approvals...")
    for subsystem_id, priority in subsystems:
        print(f"\n🔍 Requesting approval for: {subsystem_id} (priority: {priority})")
        metadata = {
            "priority": priority,
            "description": f"{subsystem_id} initialization",
        }
        approved = boot._request_ethics_approval(subsystem_id, metadata)
        print(f"   ✅ Approval: {approved}")
        time.sleep(0.1)  # Allow event processing

    # Wait for events to be processed
    time.sleep(0.3)

    print("\n📊 Summary:")
    print(f"   Total approvals requested: {len(subsystems)}")
    print(f"   Events received: {len(received_events)}")
    print(
        f"   All approvals emitted as events: {len(received_events) == len(subsystems)}"
    )

    # Clean up
    event_spine.unsubscribe("demo_subscriber")

    return received_events


def demo_governance_integration():
    """Demo 2: Approvals check governance relationships."""
    print("\n" + "=" * 80)
    print("DEMO 2: Governance Integration")
    print("=" * 80)

    boot = get_advanced_boot()
    governance_graph = get_governance_graph()

    # Add governance relationships
    print("\n🏛️ Setting up governance relationships...")

    governance_graph.add_relationship(
        from_domain="tactical_edge_ai",
        to_domain="ethics_governance",
        relationship_type=RelationshipType.MUST_CONSULT,
        description="Tactical must consult ethics",
    )

    governance_graph.add_relationship(
        from_domain="supply_logistics",
        to_domain="ethics_governance",
        relationship_type=RelationshipType.MUST_CONSULT,
        description="Supply must consult ethics for fairness",
    )

    print("   ✓ tactical_edge_ai MUST_CONSULT ethics_governance")
    print("   ✓ supply_logistics MUST_CONSULT ethics_governance")

    # Check consultation requirements
    print("\n🔍 Checking consultation requirements...")

    for subsystem in ["tactical_edge_ai", "supply_logistics", "situational_awareness"]:
        must_consult = governance_graph.must_consult_domains(subsystem)
        print(f"   {subsystem}:")
        if must_consult:
            print(f"      MUST CONSULT: {', '.join(must_consult)}")
        else:
            print("      No consultation required")

    # Request approvals - they will check governance
    print("\n📋 Requesting approvals (will check governance)...")

    event_spine = get_event_spine()
    received_events = []

    def event_callback(event):
        received_events.append(event)
        must_consult = event.payload.get("must_consult", [])
        print(f"\n   📡 Approval event for {event.payload.get('subsystem_id')}:")
        print(
            f"      Must consult: {', '.join(must_consult) if must_consult else 'None'}"
        )

    event_spine.subscribe(
        subscriber_id="demo_governance",
        subscriber_domain="demo",
        categories=[EventCategory.GOVERNANCE_DECISION],
        callback=event_callback,
    )

    for subsystem in ["tactical_edge_ai", "supply_logistics"]:
        metadata = {"priority": "HIGH"}
        boot._request_ethics_approval(subsystem, metadata)

    time.sleep(0.3)

    # Clean up
    event_spine.unsubscribe("demo_governance")


def demo_emergency_and_checkpoint_events():
    """Demo 3: Emergency mode and checkpoint events."""
    print("\n" + "=" * 80)
    print("DEMO 3: Emergency Mode & Checkpoint Events")
    print("=" * 80)

    boot = get_advanced_boot()
    event_spine = get_event_spine()

    # Track all events
    all_events = []

    def track_all(event):
        all_events.append(event)
        print(f"\n📡 Event: {event.category.value}")
        print(
            f"   Type: {event.payload.get('event_type') or event.payload.get('decision_type')}"
        )
        print(f"   Priority: {event.priority.value}")

    # Subscribe to system health and governance
    event_spine.subscribe(
        subscriber_id="demo_all",
        subscriber_domain="demo",
        categories=[EventCategory.SYSTEM_HEALTH, EventCategory.GOVERNANCE_DECISION],
        callback=track_all,
    )

    # Activate emergency mode
    print("\n🚨 Activating emergency mode...")
    boot.activate_emergency_mode("demo_emergency_scenario")
    time.sleep(0.2)

    # Mark ethics checkpoint
    print("\n✅ Marking ethics checkpoint passed...")
    boot.mark_ethics_checkpoint_passed()
    time.sleep(0.2)

    # Deactivate emergency mode
    print("\n🔓 Deactivating emergency mode...")
    boot.deactivate_emergency_mode()
    time.sleep(0.2)

    print("\n📊 Summary:")
    print(f"   Total events emitted: {len(all_events)}")

    # Clean up
    event_spine.unsubscribe("demo_all")


def demo_audit_trail_linkage():
    """Demo 4: Events linked to audit trail."""
    print("\n" + "=" * 80)
    print("DEMO 4: Event-Audit Trail Linkage")
    print("=" * 80)

    boot = get_advanced_boot()
    event_spine = get_event_spine()

    # Track events
    events_with_ids = []

    def track_event_ids(event):
        event_id = event.metadata.get("event_id")
        if event_id:
            events_with_ids.append(
                {
                    "event_id": event_id,
                    "category": event.category.value,
                    "subsystem": event.payload.get("subsystem_id"),
                }
            )

    event_spine.subscribe(
        subscriber_id="demo_audit",
        subscriber_domain="demo",
        categories=[EventCategory.GOVERNANCE_DECISION],
        callback=track_event_ids,
    )

    # Request approval
    print("\n📋 Requesting approval...")
    metadata = {"priority": "HIGH", "description": "Demo subsystem"}
    boot._request_ethics_approval("demo_subsystem", metadata)
    time.sleep(0.2)

    # Check audit trail
    print("\n📜 Checking audit trail...")
    result = boot.replay_audit_log(event_types=["ethics_approval"])

    ethics_approvals = result["reconstructed_state"]["ethics_approvals"]
    print(f"   Ethics approvals in audit: {len(ethics_approvals)}")

    if ethics_approvals:
        latest = ethics_approvals[-1]
        print("   Latest approval:")
        print(f"      Subsystem: {latest.get('subsystem_id')}")
        print(f"      Approved: {latest.get('approved')}")
        print(f"      Timestamp: {latest.get('timestamp')}")

    # Show events have IDs
    print(f"\n📡 Events with linkage IDs: {len(events_with_ids)}")
    for event in events_with_ids:
        print(f"   Event ID: {event['event_id']}")
        print(f"      Category: {event['category']}")
        print(f"      Subsystem: {event['subsystem']}")

    # Clean up
    event_spine.unsubscribe("demo_audit")


def main():
    """Run all demos."""
    print("\n" + "🔗" * 40)
    print("WIRED ETHICS APPROVALS SYSTEM DEMO")
    print("Shows event emission and governance integration")
    print("🔗" * 40)

    # Run demos
    demo_ethics_approval_events()
    demo_governance_integration()
    demo_emergency_and_checkpoint_events()
    demo_audit_trail_linkage()

    print("\n" + "=" * 80)
    print("✅ All Demos Complete!")
    print("=" * 80)
    print("\nKey Achievements:")
    print("  ✓ Ethics approvals emit events through event spine")
    print("  ✓ Approvals check governance relationships")
    print("  ✓ Emergency mode and checkpoints emit events")
    print("  ✓ Events linked to audit trail for traceability")
    print("\nThe system is now fully wired:")
    print("  • Cross-domain visibility of all approvals")
    print("  • Governance-aware decision making")
    print("  • Complete auditability with event linkage")
    print()


if __name__ == "__main__":
    main()
