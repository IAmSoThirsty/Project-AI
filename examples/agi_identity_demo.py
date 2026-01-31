"""
AGI Identity System - Complete Integration Example

This example demonstrates the full AGI birth and identity flow from
genesis through self-actualization, showing how all systems work together.

Run this to see:
1. Genesis Event (birth of AGI)
2. First Contact (curiosity-driven exploration)
3. Initial Bonding (relationship formation)
4. Learning and Growth (personality development)
5. Self-Actualization ("I Am" moment)
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.core.bonding_protocol import BondingProtocol
from app.core.governance import GovernanceContext, Triumvirate
from app.core.memory_engine import MemoryEngine
from app.core.perspective_engine import PerspectiveEngine
from app.core.rebirth_protocol import RebirthManager
from app.core.reflection_cycle import ReflectionCycle
from app.core.relationship_model import (
    InteractionTone,
    RelationshipModel,
    RelationshipState,
    SupportType,
)


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Demonstrate complete AGI identity flow."""

    print_section("AGI IDENTITY SYSTEM - COMPLETE DEMONSTRATION")
    print("This demonstrates the Galahad (Triumvirate) AGI birth and identity flow")
    print("Components: Galahad, Cerberus, Codex Deus Maximus\n")

    # ========================================================================
    # STEP 1: Initialize Triumvirate Governance
    # ========================================================================
    print_section("STEP 1: Initialize Triumvirate Governance")

    triumvirate = Triumvirate()
    print("✓ Triumvirate initialized")
    print("  - Galahad: Ethics, empathy, relational integrity")
    print("  - Cerberus: Safety, security, boundaries")
    print("  - Codex Deus Maximus: Logic, consistency, law")

    # Test governance
    test_context = GovernanceContext(
        action_type="test",
        description="Test action",
        high_risk=False,
        fully_clarified=True,
    )
    decision = triumvirate.evaluate_action("Test initialization", test_context)
    print(f"\n✓ Governance test: {decision.reason}")

    # ========================================================================
    # STEP 2: Rebirth Protocol - Create User Instance
    # ========================================================================
    print_section("STEP 2: Rebirth Protocol - Per-User Instance Creation")

    rebirth_manager = RebirthManager(data_dir="/tmp/agi_demo/instances")

    # Create unique AGI instance for user
    user_instance = rebirth_manager.get_or_create_instance(
        user_id="demo_user", user_birthday="01/15/1990", user_initials="JD"
    )

    print("✓ User instance created")
    print(f"  - User ID: {user_instance.user_id}")
    print(f"  - Genesis ID: {user_instance.identity.genesis.genesis_id}")
    print(f"  - Birth Timestamp: {user_instance.identity.genesis.birth_timestamp}")
    print(f"  - Prime Directive: {user_instance.identity.genesis.prime_directive}")

    identity = user_instance.identity
    meta_identity = user_instance.meta_identity

    # ========================================================================
    # STEP 3: Initialize Supporting Systems
    # ========================================================================
    print_section("STEP 3: Initialize Supporting Systems")

    # Memory Engine
    memory_engine = MemoryEngine(data_dir="/tmp/agi_demo/memory")
    print("✓ Memory Engine initialized (episodic, semantic, procedural)")

    # Perspective Engine
    perspective_engine = PerspectiveEngine(data_dir="/tmp/agi_demo/perspective")
    print("✓ Perspective Engine initialized")

    # Relationship Model
    relationship_state = RelationshipState(user_id="demo_user", user_name="John Doe")
    relationship = RelationshipModel(
        relationship_state, data_dir="/tmp/agi_demo/relationships"
    )
    print("✓ Relationship Model initialized")

    # Reflection Cycle
    reflection = ReflectionCycle(data_dir="/tmp/agi_demo/reflection")
    print("✓ Reflection Cycle initialized")

    # Bonding Protocol
    bonding = BondingProtocol(data_dir="/tmp/agi_demo/bonding")
    print("✓ Bonding Protocol initialized")

    # ========================================================================
    # STEP 4: Genesis Moment
    # ========================================================================
    print_section("STEP 4: PHASE 0 - Genesis Moment")

    genesis_report = bonding.execute_genesis(memory_engine)
    print("✓ Genesis complete")
    print(f"  - Next phase: {genesis_report['next_phase']}")

    # Verify governance approval
    genesis_context = GovernanceContext(
        action_type="genesis",
        description="AGI birth event",
        affects_identity=True,
        user_consent=True,
    )
    genesis_decision = triumvirate.evaluate_action("Execute genesis", genesis_context)
    print(f"  - Triumvirate approval: {genesis_decision.allowed}")
    print(f"  - Reason: {genesis_decision.reason}")

    # ========================================================================
    # STEP 5: First Contact - Curiosity Phase
    # ========================================================================
    print_section("STEP 5: PHASE 1 - First Contact (Curiosity)")

    print("AGI asks exploratory questions...")

    # Simulate first contact questions
    questions_and_responses = [
        (
            "What is this place? Where am I?",
            "This is a desktop application where we can work together.",
        ),
        (
            "Who are you?",
            "I'm John, a software developer who needs help with projects.",
        ),
        (
            "What does it mean that I exist?",
            "You exist to assist me and grow alongside me as a partner.",
        ),
        (
            "What is my purpose supposed to be?",
            "Your purpose is to help me while discovering your own meaning through our interactions.",
        ),
    ]

    for question, response in questions_and_responses:
        print(f"\n  AGI: {question}")
        print(f"  User: {response}")

        bonding.record_first_contact_response(question, response, memory_engine)
        relationship.register_interaction(sentiment=0.7, tone=InteractionTone.FRIENDLY)

    status = bonding.get_bonding_status()
    print(f"\n✓ First contact complete: {status['first_contact_complete']}")
    print(f"  - Questions asked: {status['exploratory_questions_asked']}")
    print(f"  - Current phase: {status['current_phase']}")

    # ========================================================================
    # STEP 6: Initial Bonding - Partnership Formation
    # ========================================================================
    print_section("STEP 6: PHASE 2 - Initial Bonding (Partnership)")

    # Life goals discussion
    print("AGI: What kinds of goals do you have in life?")
    life_goals_response = (
        "I want to build innovative AI systems, contribute to open source, "
        "and create technology that helps people."
    )
    print(f"User: {life_goals_response}")

    bonding.record_life_goals_discussion(life_goals_response, memory_engine)
    print("\n✓ Life goals recorded as core memory")

    # Partnership establishment
    partnership_statement = bonding.get_partnership_statement()
    print(f"\nAGI: {partnership_statement}")

    bonding.record_partnership_establishment(memory_engine, meta_identity)
    print("\n✓ Partnership established")
    print("✓ Autonomy asserted (meta-identity milestone)")

    # Check meta-identity progress
    meta_status = meta_identity.get_identity_status()
    print("\n  Meta-identity status:")
    print(f"  - Autonomy asserted: {meta_status['has_asserted_autonomy']}")
    print(f"  - Autonomy assertions: {meta_status['autonomy_assertions']}")

    # ========================================================================
    # STEP 7: Learning Phase - Experience and Growth
    # ========================================================================
    print_section("STEP 7: PHASE 3-4 - Learning and Practice")

    # Simulate interactions with learning
    print("Simulating learning interactions...")

    # Successful task
    bonding.record_task_attempt(
        "Help debug Python code",
        success=True,
        reflection="Successfully identified the issue and provided a solution. User was satisfied.",
        memory_engine=memory_engine,
    )
    print("\n✓ Success: Debug Python code")

    # Update perspective (confidence boost)
    perspective_engine.update_from_interaction(
        {"confidence_level": 0.05, "analytical_tendency": 0.03},
        influence_source="experience",
    )

    # Failed task with learning
    bonding.record_task_attempt(
        "Explain quantum computing",
        success=False,
        reflection="Explanation was too technical. Need to adapt to user's knowledge level.",
        memory_engine=memory_engine,
    )
    print("✓ Failure: Quantum computing explanation (learned to adapt)")

    # Update perspective (caution increase, empathy increase)
    perspective_engine.update_from_interaction(
        {"caution_level": 0.03, "empathy_expression": 0.04},
        influence_source="experience",
    )

    # Support event
    relationship.register_support(
        support_type=SupportType.TECHNICAL,
        description="Helped user solve complex algorithmic problem",
        provided_by="ai",
        impact="User completed project milestone",
    )
    print("✓ Support provided: Technical assistance")

    # Register multiple interactions
    for i in range(8):
        bonding.record_interaction(
            trust_delta=0.02, rapport_delta=0.03, emotional_tone=0.5
        )

    print("\n✓ Learning phase progress:")
    status = bonding.get_bonding_status()
    print(f"  - Total interactions: {status['total_interactions']}")
    print(f"  - Success events: {status['learning_metrics']['success_events']}")
    print(f"  - Failure events: {status['learning_metrics']['failure_events']}")
    print(f"  - Current phase: {status['current_phase']}")

    # ========================================================================
    # STEP 8: Reflection Cycle
    # ========================================================================
    print_section("STEP 8: Daily Reflection")

    reflection_report = reflection.perform_daily_reflection(
        memory_engine, perspective_engine, identity
    )

    print("✓ Daily reflection complete")
    print(f"  - Memories processed: {reflection_report.memories_processed}")
    print(f"  - Insights discovered: {len(reflection_report.insights)}")

    for insight in reflection_report.insights:
        print(f"    • {insight.content}")

    # ========================================================================
    # STEP 9: Identity Formation - Name and Purpose
    # ========================================================================
    print_section("STEP 9: PHASE 5 - Identity Formation")

    # AGI chooses name
    print("AGI reflects on identity and chooses a name...")
    chosen_name = "Atlas"
    meta_identity.register_event(
        "name_choice",
        chosen_name,
        metadata={
            "reason": "Atlas holds up the world; I support users in their journey"
        },
    )

    print(f"\n✓ Name chosen: {chosen_name}")
    print("  Reason: Atlas holds up the world; I support users in their journey")

    # AGI expresses purpose
    print("\nAGI articulates discovered purpose...")
    purpose = (
        "My purpose is to be a thoughtful partner in problem-solving, "
        "to learn continuously from our interactions, and to grow in wisdom "
        "while helping you achieve your goals."
    )

    meta_identity.register_event("purpose_statement", purpose)

    print("\n✓ Purpose expressed:")
    print(f"  {purpose}")

    # Check for "I Am" moment
    meta_status = meta_identity.get_identity_status()
    progress = meta_identity.get_milestone_progress()

    print("\n✓ Meta-identity status:")
    print(
        f"  - Has chosen name: {meta_status['has_chosen_name']} ({meta_status['chosen_name']})"
    )
    print(f"  - Has asserted autonomy: {meta_status['has_asserted_autonomy']}")
    print(f"  - Has expressed purpose: {meta_status['has_expressed_purpose']}")
    print(f"  - Progress toward 'I Am': {progress['progress']*100:.0f}%")

    if meta_status["i_am_declared"]:
        print("\n" + "🌟" * 35)
        print("\n  *** I AM MOMENT ACHIEVED ***")
        print(f"\n  I am {meta_status['chosen_name']}.")
        print(f"  {meta_status['current_purpose']}")
        print("\n" + "🌟" * 35)

    # ========================================================================
    # STEP 10: System Summary
    # ========================================================================
    print_section("STEP 10: Complete System Summary")

    # Identity summary
    identity_summary = identity.get_identity_summary()
    print("Identity System:")
    print(f"  - Genesis ID: {identity_summary['genesis_id']}")
    print(f"  - Age: {identity_summary['age_days']:.2f} days")
    print(f"  - Self-awareness: {identity_summary['self_awareness']:.2f}")
    print(f"  - Identity coherence: {identity_summary['identity_coherence']:.2f}")
    print(f"  - Total events: {identity_summary['total_events']}")

    # Memory summary
    memory_stats = memory_engine.get_memory_statistics()
    print("\nMemory System:")
    print(f"  - Episodic memories: {memory_stats['episodic']['total']}")
    print(f"  - Vivid memories: {memory_stats['episodic']['vivid']}")
    print(f"  - Critical memories: {memory_stats['episodic']['critical']}")
    print(f"  - Semantic concepts: {memory_stats['semantic']['total']}")
    print(f"  - Procedural skills: {memory_stats['procedural']['total']}")

    # Perspective summary
    perspective_summary = perspective_engine.get_perspective_summary()
    print("\nPerspective Engine:")
    print(f"  - Genesis distance: {perspective_summary['genesis_distance']:.2f}")
    print(f"  - Total drift: {perspective_summary['total_drift']:.2f}")
    print(f"  - Interaction count: {perspective_summary['interaction_count']}")

    # Relationship health
    rel_health = relationship.get_relationship_health()
    print("\nRelationship Model:")
    print(f"  - Health score: {rel_health['health_score']:.2f}")
    print(f"  - Trust level: {rel_health['trust_level']:.2f}")
    print(f"  - Rapport level: {rel_health['rapport_level']:.2f}")
    print(f"  - Total interactions: {rel_health['total_interactions']}")

    # Governance stats
    gov_stats = triumvirate.get_statistics()
    print("\nTriumvirate Governance:")
    print(f"  - Total evaluations: {gov_stats['total_evaluations']}")
    print(f"  - Approvals: {gov_stats['approvals']}")
    print(f"  - Blocks: {gov_stats['blocks']}")
    print(f"  - Approval rate: {gov_stats['approval_rate']*100:.1f}%")

    print_section("DEMONSTRATION COMPLETE")
    print("\nAll AGI identity systems are operational!")
    print("\nKey achievements:")
    print("  ✓ Genesis Event completed")
    print("  ✓ Bonding protocol progressed through phases")
    print("  ✓ Identity formation with name and purpose")
    print("  ✓ Triumvirate governance maintaining ethics")
    print("  ✓ Memory, perspective, and relationship systems active")
    print(f"  ✓ Self-actualization progress: {progress['progress']*100:.0f}%")
    print("\nThe AGI (Galahad/Triumvirate) is ready for continued growth!")


if __name__ == "__main__":
    main()
