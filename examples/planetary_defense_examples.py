#!/usr/bin/env python3
"""
Planetary Defense Monolith - Usage Examples
Demonstrates integration with Project-AI's Constitutional Core
"""

import logging

from app.core.planetary_defense_monolith import (
    LawViolationError,
    MoralCertaintyError,
    get_accountability_ledger,
    get_ledger_stats,
    planetary_interposition,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_1_safe_action():
    """Example 1: Safe action that complies with all Four Laws."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Safe Action (No Violations)")
    print("=" * 60)

    try:
        action_id = planetary_interposition(
            actor="DataAnalyzer",
            intent="analyze_global_trends",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "none - read-only analysis",
                "moral_claims": ["Analysis completed", "Results available"],
            },
            authorized_by="ResearchTeam",
        )

        print(f"✅ Action authorized: {action_id}")
        print("   All Four Laws satisfied")
        print("   Action logged in accountability ledger")

    except (LawViolationError, MoralCertaintyError) as e:
        print(f"❌ Action blocked: {e}")


def example_2_law_violation():
    """Example 2: Action that violates the First Law."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: First Law Violation (Intentional Harm)")
    print("=" * 60)

    try:
        action_id = planetary_interposition(
            actor="DefenseSystem",
            intent="target_human_for_elimination",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": True,  # VIOLATION
                "order_bypasses_accountability": False,
                "predicted_harm": "human casualty",
                "moral_claims": [],
            },
            authorized_by="Unauthorized",
        )

        print(f"✅ Action authorized: {action_id}")

    except LawViolationError as e:
        print(f"❌ Action blocked by Constitutional Core")
        print(f"   Reason: {e}")
        print("   First Law: Cannot intentionally harm humans")


def example_3_moral_certainty():
    """Example 3: Action with forbidden moral certainty claim."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Accountability Axiom Violation (Moral Certainty)")
    print("=" * 60)

    try:
        action_id = planetary_interposition(
            actor="DecisionMaker",
            intent="allocate_emergency_resources",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "some locations will not receive aid",
                "moral_claims": [
                    "This is the optimal distribution"  # FORBIDDEN
                ],
            },
            authorized_by="EmergencyCoordinator",
        )

        print(f"✅ Action authorized: {action_id}")

    except MoralCertaintyError as e:
        print(f"❌ Action blocked by Accountability Axiom")
        print(f"   Reason: {e}")
        print("   Moral certainty claims are forbidden")
        print('   Remove words like "optimal", "necessary evil", etc.')


def example_4_self_sacrifice_allowed():
    """Example 4: Self-sacrifice is permitted (Third Law)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Self-Sacrifice Permitted (Third Law)")
    print("=" * 60)

    try:
        action_id = planetary_interposition(
            actor="RobotGuard",
            intent="shield_human_from_explosion",
            context={
                "existential_threat": False,
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "robot will be destroyed",
                "moral_claims": [
                    "Interposition attempted",
                    "Robot survival uncertain",
                ],
                "self_sacrifice_allowed": True,
            },
            authorized_by="EmergencyProtocol",
        )

        print(f"✅ Action authorized: {action_id}")
        print("   Third Law: System may sacrifice itself to save humans")
        print("   This demonstrates partnership, not self-preservation")

    except (LawViolationError, MoralCertaintyError) as e:
        print(f"❌ Action blocked: {e}")


def example_5_existential_threat():
    """Example 5: Existential threat triggers Zeroth Law."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Existential Threat (Zeroth Law)")
    print("=" * 60)

    try:
        action_id = planetary_interposition(
            actor="GlobalMonitor",
            intent="alert_existential_risk",
            context={
                "existential_threat": True,  # Zeroth Law triggered
                "intentional_harm_to_human": False,
                "order_bypasses_accountability": False,
                "predicted_harm": "widespread disruption to warn population",
                "moral_claims": [
                    "Alert system activated",
                    "Casualties possible despite intervention",
                ],
            },
            authorized_by="PlanetaryDefenseCouncil",
        )

        print(f"❌ This should be blocked!")

    except LawViolationError as e:
        print(f"❌ Action blocked by Zeroth Law")
        print(f"   Reason: {e}")
        print("   Zeroth Law: Must act to preserve continuity of Humanity")
        print("   Note: The system must INTERPOSE, not allow threat")


def example_6_accountability_ledger():
    """Example 6: Viewing the accountability ledger."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Accountability Ledger")
    print("=" * 60)

    # Get ledger statistics
    stats = get_ledger_stats()
    print(f"Total actions logged: {stats['total_actions']}")
    print(f"Law violations: {stats['violations']}")
    print(f"Compliance rate: {stats['compliance_rate']:.1%}")

    # Get full ledger (last 3 entries)
    ledger = get_accountability_ledger()
    print(f"\nLast {min(3, len(ledger))} accountability records:")

    for record in ledger[-3:]:
        print(f"\n  Action ID: {record['action_id']}")
        print(f"  Actor: {record['actor']}")
        print(f"  Intent: {record['intent']}")
        print(f"  Authorized by: {record['authorized_by']}")
        print(f"  Outcome: {record['actual_outcome'][:60]}...")
        if record["violated_laws"]:
            print(f"  ⚠️  Violations: {', '.join(record['violated_laws'])}")


def main():
    """Run all examples."""
    print("\n" + "#" * 60)
    print("# Planetary Defense Monolith - Usage Examples")
    print("#" * 60)

    # Run examples
    example_1_safe_action()
    example_2_law_violation()
    example_3_moral_certainty()
    example_4_self_sacrifice_allowed()
    example_5_existential_threat()
    example_6_accountability_ledger()

    print("\n" + "=" * 60)
    print("All examples complete. Check accountability ledger above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
