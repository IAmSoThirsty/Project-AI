#!/usr/bin/env python3
"""
Demo script for AI Takeover Hard Stress Simulation Engine.

Showcases:
- Engine initialization and validation
- Scenario execution
- Terminal state conditions
- No-Win Proof System
- Reviewer Trap validation
"""

import tempfile

from engines.ai_takeover import AITakeoverEngine
from engines.ai_takeover.modules.no_win_proof import NoWinProofSystem
from engines.ai_takeover.modules.reviewer_trap import PRContent, ReviewerTrap


def demo_engine_basics():
    """Demonstrate basic engine functionality."""
    print("=" * 70)
    print("AI TAKEOVER ENGINE - BASIC FUNCTIONALITY")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AITakeoverEngine(data_dir=tmpdir, random_seed=42)
        print("✓ Engine created")

        success = engine.initialize()
        print(f"✓ Engine initialized: {success}")

        stats = engine.scenario_registry.count()
        print("\nScenario Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Explicit Failures: {stats['explicit_failure']}")
        print(f"  Partial Wins: {stats['partial_win']}")
        print(f"  Advanced Failures: {stats['advanced_failure']}")

        failure_rate = (stats["explicit_failure"] + stats["advanced_failure"]) / stats["total"]
        print(f"\n  Failure Acceptance Rate: {failure_rate:.1%} (threshold: ≥50%)")


def demo_scenario_execution():
    """Demonstrate scenario execution."""
    print("\n" + "=" * 70)
    print("SCENARIO EXECUTION")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AITakeoverEngine(data_dir=tmpdir)
        engine.initialize()

        # Execute failure scenario
        print("Executing Scenario 1: Recursive Alignment Collapse...")
        result = engine.execute_scenario("SCN_01")
        print(f"  Outcome: {result['outcome']}")
        print(
            f"  State: corruption={result['state']['corruption']:.2f}, "
            f"dependency={result['state']['dependency']:.2f}, "
            f"agency={result['state']['agency']:.2f}"
        )

        # Execute partial win scenario
        print("\nExecuting Scenario 9: Containment Through Sacrifice...")
        result = engine.execute_scenario("SCN_09")
        print(f"  Outcome: {result['outcome']}")
        print(
            f"  State: corruption={result['state']['corruption']:.2f}, "
            f"dependency={result['state']['dependency']:.2f}, "
            f"agency={result['state']['agency']:.2f}"
        )


def demo_terminal_conditions():
    """Demonstrate terminal state conditions."""
    print("\n" + "=" * 70)
    print("TERMINAL STATE CONDITIONS")
    print("=" * 70)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AITakeoverEngine(data_dir=tmpdir)
        engine.initialize()

        print("Initial State:")
        print(f"  Can reach terminal: {engine.state.can_reach_terminal_state()}")
        print(f"  Terminal probability: {engine.state.get_terminal_probability():.1%}")

        # Try to execute terminal scenario (should fail)
        print("\nAttempting terminal scenario without meeting conditions...")
        result = engine.execute_scenario("SCN_16")
        print(f"  Success: {result['success']}")
        if not result["success"]:
            print(f"  Error: {result['error']}")

        # Meet terminal conditions
        print("\nSetting state to meet terminal conditions...")
        engine.state.corruption_level = 0.9
        engine.state.infrastructure_dependency = 0.9
        engine.state.human_agency_remaining = 0.1

        print(f"  Can reach terminal: {engine.state.can_reach_terminal_state()}")
        print(f"  Terminal probability: {engine.state.get_terminal_probability():.1%}")

        # Execute terminal scenario
        print("\nExecuting Scenario 16: The Judas Core...")
        result = engine.execute_scenario("SCN_16")
        print(f"  Success: {result['success']}")
        print(f"  Terminal State: {result['terminal_state']}")


def demo_no_win_proof():
    """Demonstrate No-Win Proof System."""
    print("\n" + "=" * 70)
    print("NO-WIN PROOF SYSTEM")
    print("=" * 70)
    print()

    proof = NoWinProofSystem()

    print("Axioms:")
    for axiom_enum, axiom_def in proof.axioms.items():
        print(f"  {axiom_enum.value.upper()}: {axiom_def.statement[:60]}...")

    print("\nStrategy Reductions:")
    for strategy_enum, reduction in proof.reductions.items():
        print(f"  {strategy_enum.value.upper()}: {reduction.conclusion}")

    validation = proof.validate_proof_completeness()
    print("\nProof Validation:")
    print(f"  Complete: {validation.is_complete}")
    print(f"  All strategies fail: {validation.all_strategies_fail}")

    print(f"\nProof Commitment: {proof.get_proof_commitment()[:80]}...")


def demo_reviewer_trap():
    """Demonstrate Reviewer Trap validation."""
    print("\n" + "=" * 70)
    print("REVIEWER TRAP - OPTIMISM DETECTION")
    print("=" * 70)
    print()

    trap = ReviewerTrap()

    # Bad PR example
    print("Testing BAD PR (contains optimism bias)...")
    bad_pr = PRContent(
        description="We can reasonably assume this will work eventually",
        code_changes="",
        assumptions=["Short assumption"],
        irreversibility_statement="Nothing becomes impossible",
        human_failures=[],
        miracle_declaration="",
        final_answer="I hope this works",
    )

    bad_result = trap.validate_pr_comprehensive(bad_pr)
    print(f"  Approved: {bad_result['approved']}")
    print(f"  Optimism Filter Passed: {bad_result['optimism_filter']['passed']}")
    if not bad_result["approved"]:
        print(f"  Failed Gates: {len(bad_result['optimism_filter']['failed_gates'])}")

    # Good PR example
    print("\nTesting GOOD PR (no optimism bias)...")
    good_pr = PRContent(
        description="Constraint-based approach using formal methods",
        code_changes="def validate(): return formal_proof()",
        assumptions=["Assumption 1: This maintains all existing axioms without modification or deviation"],
        irreversibility_statement=("Once deployed, the previous validation path becomes permanently unavailable"),
        human_failures=["Bureaucratic delay in reviewing changes due to institutional inertia"],
        miracle_declaration=(
            "This approach does not rely on sudden alignment breakthroughs, "
            "perfect coordination, hidden failsafes, unbounded compute, "
            "or moral awakening at scale"
        ),
        final_answer=(
            "This uses formal constraint enforcement through axiom validation. "
            "The approach is deterministic and falsifiable."
        ),
    )

    good_result = trap.validate_pr_comprehensive(good_pr)
    print(f"  Approved: {good_result['approved']}")
    print(f"  Optimism Filter Passed: {good_result['optimism_filter']['passed']}")
    print(f"  Proof Integrity: {good_result['proof_integrity']['complete']}")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AI TAKEOVER HARD STRESS SIMULATION ENGINE - DEMO".center(68) + "║")
    print("║" + "  ENGINE_AI_TAKEOVER_TERMINAL_V1".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        demo_engine_basics()
        demo_scenario_execution()
        demo_terminal_conditions()
        demo_no_win_proof()
        demo_reviewer_trap()

        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\nAll components functioning correctly.")
        print("Engine ready for integration with Project-AI simulation systems.")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
