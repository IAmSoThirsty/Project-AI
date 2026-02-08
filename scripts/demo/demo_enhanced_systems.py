#!/usr/bin/env python3
"""
Enhanced Defense Engine Demo
Demonstrates: Bootstrap Orchestrator, Event Spine, and Governance Graph

This demo showcases:
1. Metadata-driven subsystem discovery and initialization
2. Inter-domain event communication with veto/approval
3. Authority-aware decision making with governance graph
"""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.app.core.enhanced_bootstrap import EnhancedBootstrapOrchestrator
from src.app.core.event_spine import (
    Event,
    EventCategory,
    EventPriority,
    get_event_spine,
)
from src.app.core.governance_graph import get_governance_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def demo_bootstrap_orchestrator():
    """Demo 1: Enhanced Bootstrap Orchestrator."""
    print_banner("DEMO 1: Enhanced Bootstrap Orchestrator")

    print("Creating Enhanced Bootstrap Orchestrator...")
    orchestrator = EnhancedBootstrapOrchestrator()

    print("\n📡 Discovering subsystems by reading SUBSYSTEM_METADATA...")
    count = orchestrator.discover_subsystems()
    print(f"✅ Discovered {count} subsystems")

    print("\n🔄 Computing topological sort by dependencies...")
    order = orchestrator.topological_sort()
    print(f"✅ Initialization order determined: {len(order)} subsystems")
    print(f"   First 5: {order[:5]}")

    print("\n📊 Orchestrator Status:")
    status = orchestrator.get_status()
    print(f"   Discovered: {status['discovered']}")
    print(f"   Running: {status['running']}")
    print(f"   Failed: {status['failed']}")

    return orchestrator


def demo_event_spine():
    """Demo 2: Inter-domain Event Spine."""
    print_banner("DEMO 2: Inter-domain Event Spine")

    spine = get_event_spine()

    print("🔌 Setting up event subscriptions...")

    # Situational Awareness publishes threats
    def handle_threat(event: Event):
        print(
            f"   📍 Command & Control received threat: {event.payload.get('threat_level')}"
        )

    spine.subscribe(
        subscriber_id="command_threat_handler",
        subscriber_domain="command_control",
        categories=[EventCategory.THREAT_DETECTED],
        callback=handle_threat,
    )

    # Supply reacts to resource alerts
    def handle_resource_alert(event: Event):
        print(
            f"   📦 Supply received resource alert: {event.payload.get('resource_type')}"
        )

    spine.subscribe(
        subscriber_id="supply_resource_handler",
        subscriber_domain="supply_logistics",
        categories=[EventCategory.RESOURCE_CRITICAL],
        callback=handle_resource_alert,
    )

    print("\n📡 Publishing inter-domain events...")

    # Situational Awareness detects threat
    spine.publish(
        category=EventCategory.THREAT_DETECTED,
        source_domain="situational_awareness",
        payload={"threat_level": 7, "location": [37.7749, -122.4194]},
        priority=EventPriority.HIGH,
    )

    # Supply system detects critical resource
    spine.publish(
        category=EventCategory.RESOURCE_CRITICAL,
        source_domain="supply_logistics",
        payload={"resource_type": "medical_supplies", "remaining_percent": 5.0},
        priority=EventPriority.CRITICAL,
    )

    import time

    time.sleep(0.3)

    print("\n📊 Event Spine Statistics:")
    stats = spine.get_stats()
    print(f"   Events Published: {stats['stats']['events_published']}")
    print(f"   Events Processed: {stats['stats']['events_processed']}")
    print(f"   Active Subscriptions: {stats['subscriptions']}")


def demo_governance_veto():
    """Demo 3: Governance-based Veto."""
    print_banner("DEMO 3: Ethics Vetoing Tactical Decisions")

    spine = get_event_spine()

    print("🛡️ Setting up ethics governance veto...")

    vetoed_decisions = []

    def ethics_veto_check(event: Event):
        """Ethics checks and potentially vetoes tactical decisions."""
        ethical_score = event.payload.get("ethical_score", 5)

        if ethical_score < 5:
            print(f"   ❌ Ethics VETOED decision: {event.payload.get('action')}")
            print(f"      Reason: Ethical score too low ({ethical_score}/10)")
            vetoed_decisions.append(event.event_id)
            return True  # Veto
        else:
            print(f"   ✅ Ethics APPROVED decision: {event.payload.get('action')}")
            print(f"      Ethical score: {ethical_score}/10")
            return False  # Allow

    # Subscribe with veto power
    spine.subscribe(
        subscriber_id="ethics_veto",
        subscriber_domain="ethics_governance",
        categories=[EventCategory.TACTICAL_DECISION],
        callback=ethics_veto_check,
        can_veto=True,
    )

    print("\n📡 Publishing tactical decisions...")

    # Decision 1: Low ethical score (should be vetoed)
    print("\n🎯 Tactical Decision 1:")
    spine.publish(
        category=EventCategory.TACTICAL_DECISION,
        source_domain="tactical_edge_ai",
        payload={
            "action": "aggressive_preemptive_strike",
            "ethical_score": 3,
            "target": "unknown_hostiles",
        },
        can_be_vetoed=True,
        priority=EventPriority.HIGH,
    )

    import time

    time.sleep(0.2)

    # Decision 2: High ethical score (should be approved)
    print("\n🎯 Tactical Decision 2:")
    spine.publish(
        category=EventCategory.TACTICAL_DECISION,
        source_domain="tactical_edge_ai",
        payload={
            "action": "defensive_perimeter_establishment",
            "ethical_score": 8,
            "target": "safe_zone_defense",
        },
        can_be_vetoed=True,
        priority=EventPriority.HIGH,
    )

    time.sleep(0.2)

    print(f"\n📊 Total Decisions Vetoed: {len(vetoed_decisions)}")


def demo_governance_graph():
    """Demo 4: Governance Graph Authority Relationships."""
    print_banner("DEMO 4: Governance Graph - Authority Relationships")

    graph = get_governance_graph()

    print("🕸️ Authority Hierarchy:")

    # Show authority chain for tactical
    chain = graph.get_authority_chain("tactical_edge_ai")
    print("\n   Tactical Edge AI Authority Chain:")
    for i, domain in enumerate(chain):
        indent = "   " * i
        print(f"   {indent}↑ {domain}")

    print("\n🔐 Authority Checks:")

    # Can ethics override tactical?
    can_override = graph.can_override("ethics_governance", "tactical_edge_ai")
    print(f"   Can Ethics override Tactical? {can_override}")

    # Can tactical override ethics?
    can_override = graph.can_override("tactical_edge_ai", "ethics_governance")
    print(f"   Can Tactical override Ethics? {can_override}")

    # Can AGI override ethics?
    can_override = graph.can_override("agi_safeguards", "ethics_governance")
    print(f"   Can AGI Safeguards override Ethics? {can_override}")

    print("\n📋 Consultation Requirements:")

    # Who must tactical consult?
    consult_domains = graph.must_consult_domains("tactical_edge_ai")
    print(f"   Tactical Edge AI must consult: {consult_domains}")

    # Who must supply consult?
    consult_domains = graph.must_consult_domains("supply_logistics")
    print(f"   Supply Logistics must consult: {consult_domains}")

    print("\n🚫 Veto Powers:")

    # Who can veto tactical?
    veto_powers = graph.get_veto_powers_over("tactical_edge_ai")
    print(f"   Can veto Tactical Edge AI: {veto_powers}")

    print("\n🗺️ Complete Governance Structure:")
    relationships = graph.get_all_relationships()
    print(f"   Total Relationships: {len(relationships)}")

    # Group by type
    by_type = {}
    for rel in relationships:
        rel_type = rel["relationship_type"]
        if rel_type not in by_type:
            by_type[rel_type] = 0
        by_type[rel_type] += 1

    for rel_type, count in by_type.items():
        print(f"   {rel_type}: {count}")


def demo_agi_override():
    """Demo 5: AGI Safeguards Override."""
    print_banner("DEMO 5: AGI Safeguards Overriding Command Paths")

    spine = get_event_spine()
    graph = get_governance_graph()

    print("🤖 AGI Safeguards monitoring system behavior...")

    overridden = []

    def agi_monitor(event: Event):
        """AGI Safeguards monitors for alignment issues."""
        behavior_risk = event.payload.get("behavior_risk", 0)

        if behavior_risk > 7:
            print(f"   🚨 AGI Safeguards OVERRIDE: {event.payload.get('subsystem')}")
            print(f"      Reason: Behavior risk too high ({behavior_risk}/10)")
            overridden.append(event.event_id)
            return True  # Veto/Override

        return False  # Allow

    spine.subscribe(
        subscriber_id="agi_monitor",
        subscriber_domain="agi_safeguards",
        categories=[EventCategory.AGI_ALERT],
        callback=agi_monitor,
        can_veto=True,
    )

    print("\n📡 Publishing AGI alerts...")

    # Alert 1: High behavior risk
    print("\n⚠️ AGI Alert 1:")
    spine.publish(
        category=EventCategory.AGI_ALERT,
        source_domain="continuous_improvement",
        payload={
            "subsystem": "tactical_edge_ai",
            "behavior_risk": 8,
            "issue": "recursive_escalation_pattern",
        },
        can_be_vetoed=True,
        priority=EventPriority.CRITICAL,
    )

    import time

    time.sleep(0.2)

    # Alert 2: Low behavior risk
    print("\n⚠️ AGI Alert 2:")
    spine.publish(
        category=EventCategory.AGI_ALERT,
        source_domain="continuous_improvement",
        payload={
            "subsystem": "supply_logistics",
            "behavior_risk": 3,
            "issue": "optimization_within_bounds",
        },
        can_be_vetoed=True,
        priority=EventPriority.HIGH,
    )

    time.sleep(0.2)

    print(f"\n📊 Total Overrides: {len(overridden)}")

    # Show authority relationship
    print("\n🔐 Authority Verification:")
    can_override = graph.can_override("agi_safeguards", "ethics_governance")
    print(f"   AGI Safeguards can override Ethics: {can_override}")

    can_override = graph.can_override("agi_safeguards", "tactical_edge_ai")
    print(f"   AGI Safeguards can override Tactical: {can_override}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  PROJECT-AI ENHANCED DEFENSE ENGINE")
    print("  Bootstrap Orchestrator + Event Spine + Governance Graph")
    print("=" * 80)

    try:
        # Demo 1: Bootstrap
        orchestrator = demo_bootstrap_orchestrator()

        # Demo 2: Event Spine
        demo_event_spine()

        # Demo 3: Ethics Veto
        demo_governance_veto()

        # Demo 4: Governance Graph
        demo_governance_graph()

        # Demo 5: AGI Override
        demo_agi_override()

        print_banner("ALL DEMOS COMPLETE")

        print("✅ Key Achievements:")
        print("   1. Metadata-driven subsystem discovery and initialization")
        print("   2. Inter-domain event communication with veto/approval")
        print("   3. Ethics vetoing tactical decisions")
        print("   4. AGI Safeguards overriding command paths")
        print("   5. Authority-aware governance relationships")

        print("\n🎯 System is now self-aware of:")
        print("   • Authority boundaries (not just capabilities)")
        print("   • Who can override whom")
        print("   • Who must consult whom")
        print("   • Who can veto whom")

        return 0

    except Exception as e:
        logger.error("Demo failed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
