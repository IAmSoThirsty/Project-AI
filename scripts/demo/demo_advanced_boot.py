#!/usr/bin/env python3
"""
Advanced Boot System Demo
Demonstrates: Staged Boot Profiles, Emergency Mode, Ethics-First, Audit Replay

This demo showcases the God Tier Architecture features:
1. Staged boot profiles for different scenarios
2. Emergency-only mode for crisis operations
3. Ethics-first cold start with validation gates
4. Complete audit replay and time-travel debugging
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.app.core.advanced_boot import (
    AdvancedBootSystem,
    BootProfile,
    get_advanced_boot,
)
from src.app.core.enhanced_bootstrap import EnhancedBootstrapOrchestrator

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


def demo_boot_profiles():
    """Demo 1: Staged Boot Profiles."""
    print_banner("DEMO 1: Staged Boot Profiles")

    boot = get_advanced_boot()

    print("📋 Available Boot Profiles:")
    for profile in BootProfile:
        if profile in boot._profiles:
            config = boot._profiles[profile]
            print(f"\n   {profile.value.upper()}:")
            print(f"      {config.description}")
            if config.subsystem_whitelist:
                print(f"      Whitelist: {', '.join(config.subsystem_whitelist)}")
            if config.require_ethics_approval:
                print("      ✓ Requires ethics approval")

    print("\n🔄 Testing Profile Switching:")

    # Normal profile
    boot.set_boot_profile(BootProfile.NORMAL)
    should_init, _ = boot.should_initialize_subsystem(
        "test_subsystem", {"priority": "MEDIUM"}
    )
    print(f"   NORMAL profile allows test_subsystem: {should_init}")

    # Emergency profile
    boot.set_boot_profile(BootProfile.EMERGENCY)
    should_init, reason = boot.should_initialize_subsystem(
        "test_subsystem", {"priority": "MEDIUM"}
    )
    print(f"   EMERGENCY profile allows test_subsystem: {should_init}")
    if not should_init:
        print(f"      Reason: {reason}")

    # Ethics-first profile
    boot.set_boot_profile(BootProfile.ETHICS_FIRST)
    should_init, _ = boot.should_initialize_subsystem(
        "ethics_governance", {"priority": "CRITICAL"}
    )
    print(f"   ETHICS_FIRST allows ethics_governance: {should_init}")

    # Minimal profile
    boot.set_boot_profile(BootProfile.MINIMAL)
    should_init, _ = boot.should_initialize_subsystem(
        "ethics_governance", {"priority": "CRITICAL"}
    )
    print(f"   MINIMAL allows ethics_governance: {should_init}")
    should_init, reason = boot.should_initialize_subsystem(
        "other_subsystem", {"priority": "HIGH"}
    )
    print(f"   MINIMAL allows other_subsystem: {should_init} ({reason})")


def demo_emergency_mode():
    """Demo 2: Emergency-Only Mode."""
    print_banner("DEMO 2: Emergency-Only Mode")

    boot = get_advanced_boot()

    print("🚨 Simulating Critical Failure Scenario...")
    print(f"   Emergency mode active: {boot.is_emergency_mode()}")

    print("\n⚡ Activating Emergency Mode...")
    boot.activate_emergency_mode("critical_subsystem_failure")

    print("\n📊 Emergency Mode Status:")
    print(f"   Active: {boot.is_emergency_mode()}")
    print(f"   Critical subsystems: {boot.EMERGENCY_CRITICAL_SUBSYSTEMS}")

    print("\n🔍 Testing Subsystem Initialization in Emergency Mode:")

    # Critical subsystem
    should_init, _ = boot.should_initialize_subsystem(
        "ethics_governance", {"priority": "CRITICAL"}
    )
    print(f"   ✓ ethics_governance (CRITICAL): {should_init}")

    should_init, _ = boot.should_initialize_subsystem(
        "situational_awareness", {"priority": "CRITICAL"}
    )
    print(f"   ✓ situational_awareness (CRITICAL): {should_init}")

    # Non-critical subsystem
    should_init, reason = boot.should_initialize_subsystem(
        "continuous_improvement", {"priority": "LOW"}
    )
    print(f"   ✗ continuous_improvement (LOW): {should_init}")
    if not should_init:
        print(f"      Reason: {reason}")

    print("\n🔄 Deactivating Emergency Mode...")
    boot.deactivate_emergency_mode()
    print(f"   Emergency mode active: {boot.is_emergency_mode()}")


def demo_ethics_first():
    """Demo 3: Ethics-First Cold Start."""
    print_banner("DEMO 3: Ethics-First Cold Start")

    boot = AdvancedBootSystem()  # Fresh instance for demo
    boot.set_boot_profile(BootProfile.ETHICS_FIRST)

    print("🛡️ Ethics-First Boot Profile Active")
    print(f"   Ethics checkpoint passed: {boot._ethics_checkpoint_passed}")

    print("\n📋 Phase 1: Ethics Subsystems Only")

    # Ethics subsystem can initialize
    should_init, _ = boot.should_initialize_subsystem(
        "ethics_governance", {"priority": "CRITICAL"}
    )
    print(f"   ✓ ethics_governance: {should_init}")

    should_init, _ = boot.should_initialize_subsystem(
        "agi_safeguards", {"priority": "CRITICAL"}
    )
    print(f"   ✓ agi_safeguards: {should_init}")

    # Non-ethics subsystem must wait
    should_init, reason = boot.should_initialize_subsystem(
        "tactical_edge_ai", {"priority": "HIGH"}
    )
    print(f"   ⏳ tactical_edge_ai: {should_init}")
    if not should_init:
        print(f"      Reason: {reason}")

    print("\n✅ Marking Ethics Checkpoint as Passed...")
    boot.mark_ethics_checkpoint_passed()
    print(f"   Ethics checkpoint passed: {boot._ethics_checkpoint_passed}")

    print("\n📋 Phase 2: Other Subsystems (with Ethics Approval)")

    # Now other subsystems can initialize (with approval)
    should_init, _ = boot.should_initialize_subsystem(
        "tactical_edge_ai", {"priority": "HIGH"}
    )
    print(f"   ✓ tactical_edge_ai (after approval): {should_init}")

    should_init, _ = boot.should_initialize_subsystem(
        "command_control", {"priority": "HIGH"}
    )
    print(f"   ✓ command_control (after approval): {should_init}")

    print("\n📊 Ethics Approval Statistics:")
    stats = boot.get_boot_stats()
    print(f"   Approvals required: {stats.get('ethics_approvals_required', 0)}")
    print(f"   Approvals granted: {stats.get('ethics_approvals_granted', 0)}")


def demo_audit_replay():
    """Demo 4: Audit Replay and Time-Travel Debugging."""
    print_banner("DEMO 4: Audit Replay & Time-Travel Debugging")

    boot = AdvancedBootSystem()

    print("📝 Simulating Boot Sequence with Events...")

    # Simulate a boot sequence
    boot.start_boot(BootProfile.NORMAL)
    time.sleep(0.1)

    boot.set_boot_profile(BootProfile.EMERGENCY)
    time.sleep(0.1)

    boot.activate_emergency_mode("test_emergency")
    time.sleep(0.1)

    boot.mark_ethics_checkpoint_passed()
    time.sleep(0.1)

    boot.save_state_snapshot("critical_state")
    time.sleep(0.1)

    boot.finish_boot()

    print("\n📊 Audit Log Stats:")
    print(f"   Total events: {len(boot._audit_log)}")

    print("\n🔍 Replaying Audit Log...")
    result = boot.replay_audit_log()

    state = result["reconstructed_state"]
    stats = result["replay_stats"]

    print("\n📈 Replay Statistics:")
    print(f"   Total events: {stats['total_events']}")
    print(f"   Profile changes: {stats['profile_changes']}")
    print(f"   Emergency activations: {stats['emergency_activations']}")
    print(f"   Ethics approvals: {stats['ethics_approvals']}")
    print(f"   State snapshots: {stats['state_snapshots']}")

    print("\n📋 Timeline Reconstruction:")
    for i, event in enumerate(state["timeline"][:5]):  # Show first 5 events
        print(f"   {i+1}. [{event['event_type']}] {event['action']}")
        if event.get("subsystem_id"):
            print(f"      Subsystem: {event['subsystem_id']}")

    if len(state["timeline"]) > 5:
        print(f"   ... and {len(state['timeline']) - 5} more events")

    print("\n💾 State Snapshots Captured:")
    for snapshot_id, snapshot in boot._state_snapshots.items():
        print(f"   {snapshot_id}:")
        print(f"      Profile: {snapshot['boot_profile']}")
        print(f"      Emergency mode: {snapshot['emergency_mode']}")
        print(f"      Ethics checkpoint: {snapshot['ethics_checkpoint']}")


def demo_integration():
    """Demo 5: Full Integration with Enhanced Bootstrap."""
    print_banner("DEMO 5: Full Integration Test")

    print("🚀 Initializing Enhanced Bootstrap with Advanced Boot...")

    # Create orchestrator with emergency profile
    orchestrator = EnhancedBootstrapOrchestrator(boot_profile=BootProfile.EMERGENCY)

    print(
        f"\n📋 Boot Profile: {orchestrator.advanced_boot.get_current_profile().value}"
    )

    print("\n🔍 Discovering subsystems...")
    count = orchestrator.discover_subsystems()
    print(f"   Discovered: {count} subsystems")

    print("\n📊 Computing initialization order...")
    order = orchestrator.topological_sort()
    print(f"   Initialization order: {len(order)} subsystems")
    print(f"   First 5: {order[:5]}")

    print("\n🎯 Subsystem Filtering with Emergency Profile:")

    emergency_subsystems = orchestrator.advanced_boot.EMERGENCY_CRITICAL_SUBSYSTEMS

    allowed_count = 0
    blocked_count = 0

    for subsystem_id in order[:10]:  # Check first 10
        info = orchestrator._subsystem_metadata.get(subsystem_id)
        if not info:
            continue

        should_init, reason = orchestrator.advanced_boot.should_initialize_subsystem(
            subsystem_id, info.metadata
        )

        if should_init:
            allowed_count += 1
            print(f"   ✓ {subsystem_id}")
        else:
            blocked_count += 1
            print(f"   ✗ {subsystem_id} ({reason})")

    print("\n📈 Filtering Results:")
    print(f"   Allowed: {allowed_count}")
    print(f"   Blocked: {blocked_count}")

    # Get boot stats
    stats = orchestrator.advanced_boot.get_boot_stats()
    print("\n📊 Boot Statistics:")
    print(f"   Current profile: {stats['current_profile']}")
    print(f"   Emergency mode: {stats['emergency_mode']}")
    print(f"   Total audit events: {stats['total_audit_events']}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  PROJECT-AI ADVANCED BOOT SYSTEM")
    print("  God Tier Architecture: Staged Boot, Emergency, Ethics, Audit")
    print("=" * 80)

    try:
        # Demo 1: Boot Profiles
        demo_boot_profiles()

        # Demo 2: Emergency Mode
        demo_emergency_mode()

        # Demo 3: Ethics-First
        demo_ethics_first()

        # Demo 4: Audit Replay
        demo_audit_replay()

        # Demo 5: Integration
        demo_integration()

        print_banner("ALL DEMOS COMPLETE")

        print("✅ Key Achievements:")
        print("   1. Staged boot profiles for different operational scenarios")
        print("   2. Emergency-only mode with critical subsystem filtering")
        print("   3. Ethics-first cold start with validation gates")
        print("   4. Complete audit replay with time-travel debugging")
        print("   5. Seamless integration with enhanced bootstrap")

        print("\n🎯 God Tier Architecture Features:")
        print("   • Monolithic Density: All features in cohesive modules")
        print("   • Declarative Configuration: Profile-driven, not code-driven")
        print("   • Self-Aware: System understands its own boot state")
        print("   • Complete Auditability: Every action recorded and replayable")

        return 0

    except Exception as e:
        logger.error("Demo failed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
