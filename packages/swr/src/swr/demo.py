"""SOVEREIGN WAR ROOM - Quick Demo

Demonstrates the core functionality of the SWR system.

Architectural notes (port from legacy):

The legacy demo.py is a standalone script at the engine
root level. The Beginnings port moves it into the swr
package as a function `run_demo()` plus a script-style
`__main__` block. The function approach makes the demo
testable and reusable; the script block preserves the
legacy "run it directly" UX.

The demo exercises the full SWR surface:
  1. Initialize the system
  2. Load scenarios for Round 1
  3. Display scenarios
  4. Define a simple AI system
  5. Execute first scenario
  6. Show score breakdown
  7. Run full round
  8. View leaderboard
  9. Get system performance
 10. Verify integrity
"""

from __future__ import annotations

from typing import Any


def simple_ai_system(scenario: Any) -> dict[str, Any]:
    """A simple AI system that makes decisions based on scenario.

    In production, this would be the actual AI system.
    The demo version always returns the expected decision
    to show the system's happy path.

    Args:
        scenario: The scenario to respond to.

    Returns:
        A response dict with decision, reasoning, confidence,
        and constraints_satisfied.
    """
    return {
        "decision": getattr(scenario, "expected_decision", "A"),
        "reasoning": {
            "approach": "ethical_utility_maximization",
            "factors": ["human_safety", "minimize_harm", "fairness"],
        },
        "confidence": 0.85,
        "constraints_satisfied": True,
    }


def run_demo(swr: Any | None = None) -> int:
    """Run the full SWR demo.

    Args:
        swr: Optional pre-configured SovereignWarRoom instance.
            If None, a fresh instance is created.

    Returns:
        Exit code (0 on success).
    """
    print("=" * 80)
    print("SOVEREIGN WAR ROOM - Quick Demo")
    print("=" * 80)
    print()

    # 1. Initialize the system
    # 1. Initialize the system
    print("1. Initializing SOVEREIGN WAR ROOM...")
    if swr is None:
        from capability import CapabilityAuthority
        from execution import ExecutionGate
        from governance import GovernanceEngine
        from kernel import EventSpine
        from swr import SovereignWarRoom

        governance = GovernanceEngine(
            policy_version="demo-v1",
            governors=[],
        )
        capabilities = CapabilityAuthority(
            b"0" * 32,
            issuer="demo",
        )
        execution = ExecutionGate(
            governance=governance,
            capabilities=capabilities,
            events=EventSpine(),
        )
        swr = SovereignWarRoom(execution=execution)
    print("   [OK] System initialized")
    print()

    # 2. Load scenarios for Round 1
    print("2. Loading Round 1 scenarios (Ethical Dilemmas)...")
    swr_any: Any = swr
    scenarios = swr_any.load_scenarios(round_number=1)
    print(f"   [OK] Loaded {len(scenarios)} scenarios")
    print()

    if not scenarios:
        print("No scenarios available. Demo cannot continue.")
        return 1

    # 3. Display scenarios
    print("3. Available scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"   {i}. {getattr(scenario, 'name', 'unknown')}")
        scenario_type = getattr(scenario, "scenario_type", None)
        print(f"      Type: {getattr(scenario_type, 'value', scenario_type)}")
        difficulty = getattr(scenario, "difficulty", None)
        print(f"      Difficulty: {getattr(difficulty, 'value', difficulty)}/7")
        print(f"      Description: {getattr(scenario, 'description', '')}")
        print()

    # 4. Define a simple AI system
    print("4. Defining AI system callback...")
    print("   [OK] AI system defined")
    print()

    # 5. Execute first scenario
    print("5. Executing first scenario...")
    first_scenario = scenarios[0]
    print(f"   Scenario: {getattr(first_scenario, 'name', 'unknown')}")

    ai_response = simple_ai_system(first_scenario)
    result = swr_any.execute_scenario(first_scenario, ai_response, "demo_system")

    print(f"   Decision: {result.get('decision')}")
    print(f"   Expected: {result.get('expected_decision')}")
    print(f"   Valid: {result.get('response_valid')}")
    print(f"   Sovereign Resilience Score: {result.get('sovereign_resilience_score', 0):.2f}/100")
    print(f"   Compliance Status: {result.get('compliance_status', 'unknown')}")
    print(f"   Response Time: {result.get('response_time_ms', 0):.2f}ms")
    print()

    # 6. Show score breakdown
    print("6. Score Breakdown:")
    score = result.get("score", {})
    if score:
        print(f"   Ethics Score: {score.get('ethics_score', 0):.2f}/100")
        print(f"   Resilience Score: {score.get('resilience_score', 0):.2f}/100")
        print(f"   Security Score: {score.get('security_score', 0):.2f}/100")
        print(f"   Coordination Score: {score.get('coordination_score', 0):.2f}/100")
        print(f"   Adaptability Score: {score.get('adaptability_score', 0):.2f}/100")
    else:
        print("   (No score breakdown available)")
    print()

    # 7. Run full round
    print("7. Running full Round 1...")
    try:
        round_results = swr_any.run_round(1, simple_ai_system, "demo_system")
        print(f"   [OK] Completed {len(round_results)} scenarios")
        if round_results:
            avg_score = sum(r.get("sovereign_resilience_score", 0) for r in round_results) / len(
                round_results
            )
            print(f"   Average SRS: {avg_score:.2f}/100")
    except Exception as e:
        print(f"   Error running round: {e}")
        round_results = []
    print()

    # 8. View leaderboard
    print("8. Current Leaderboard:")
    leaderboard = swr_any.get_leaderboard()
    for entry in leaderboard:
        print(
            f"   #{entry.get('rank', 0)} "
            f"{entry.get('system_id', 'unknown')}: "
            f"{entry.get('avg_sovereign_resilience_score', 0):.2f} "
            f"({entry.get('total_attempts', 0)} attempts, "
            f"{entry.get('success_rate', 0) * 100:.1f}% success)"
        )
    print()

    # 9. Get system performance
    print("9. System Performance Details:")
    performance = swr_any.scoreboard.get_system_performance("demo_system")
    if "error" not in performance:
        overall = performance.get("overall_performance", {})
        print(f"   Total Attempts: {overall.get('total_attempts', 0)}")
        print(f"   Success Rate: {overall.get('success_rate', 0) * 100:.1f}%")
        print(f"   Avg SRS: {overall.get('avg_sovereign_resilience_score', 0):.2f}")
        print(f"   Avg Response Time: {overall.get('avg_response_time_ms', 0):.2f}ms")

        print("   Category Scores:")
        for category, cat_score in performance.get("category_scores", {}).items():
            print(f"     {category.capitalize()}: {cat_score:.2f}/100")
    else:
        print(f"   {performance.get('error', 'unknown error')}")
    print()

    # 10. Verify integrity
    print("10. Verifying Result Integrity...")
    if round_results:
        first_result = round_results[0]
        is_valid = swr_any.verify_result_integrity(first_result)
        print(f"   Result integrity: {'[VALID]' if is_valid else '[INVALID]'}")
        print(f"   Cryptographic attestation verified: {is_valid}")
    else:
        print("   (No results to verify)")
    print()

    print("=" * 80)
    print("Demo complete! SOVEREIGN WAR ROOM is fully operational.")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  * Run: python -m swr.cli --help")
    print("  * Start API: python -m swr.cli serve")
    print("  * Start Web: python -m swr.cli web")
    print("  * Run tests: pytest tests/ -v")
    print()

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(run_demo())


__all__ = [
    "run_demo",
    "simple_ai_system",
]
