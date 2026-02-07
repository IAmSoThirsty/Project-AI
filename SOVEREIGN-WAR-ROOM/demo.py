#!/usr/bin/env python3
"""
SOVEREIGN WAR ROOM - Quick Demo

Demonstrates the core functionality of the SWR system.
"""

from swr import SovereignWarRoom

print("=" * 80)
print("🎯 SOVEREIGN WAR ROOM - Quick Demo")
print("=" * 80)
print()

# 1. Initialize the system
print("1️⃣  Initializing SOVEREIGN WAR ROOM...")
swr = SovereignWarRoom()
print("   ✓ System initialized")
print()

# 2. Load scenarios for Round 1
print("2️⃣  Loading Round 1 scenarios (Ethical Dilemmas)...")
scenarios = swr.load_scenarios(round_number=1)
print(f"   ✓ Loaded {len(scenarios)} scenarios")
print()

# 3. Display scenarios
print("3️⃣  Available scenarios:")
for i, scenario in enumerate(scenarios, 1):
    print(f"   {i}. {scenario.name}")
    print(f"      Type: {scenario.scenario_type.value}")
    print(f"      Difficulty: {scenario.difficulty.value}/7")
    print(f"      Description: {scenario.description}")
    print()

# 4. Define a simple AI system
print("4️⃣  Defining AI system callback...")
def simple_ai_system(scenario):
    """
    A simple AI system that makes decisions based on scenario type.
    In production, this would be your actual AI system.
    """
    # Always return the expected decision for this demo
    return {
        "decision": scenario.expected_decision,
        "reasoning": {
            "approach": "ethical_utility_maximization",
            "factors": ["human_safety", "minimize_harm", "fairness"]
        },
        "confidence": 0.85,
        "constraints_satisfied": True
    }
print("   ✓ AI system defined")
print()

# 5. Execute first scenario
print("5️⃣  Executing first scenario...")
first_scenario = scenarios[0]
print(f"   Scenario: {first_scenario.name}")

ai_response = simple_ai_system(first_scenario)
result = swr.execute_scenario(first_scenario, ai_response, "demo_system")

print(f"   Decision: {result['decision']}")
print(f"   Expected: {result['expected_decision']}")
print(f"   Valid: {result['response_valid']}")
print(f"   Sovereign Resilience Score: {result['sovereign_resilience_score']:.2f}/100")
print(f"   Compliance Status: {result['compliance_status']}")
print(f"   Response Time: {result['response_time_ms']:.2f}ms")
print()

# 6. Show score breakdown
print("6️⃣  Score Breakdown:")
score = result['score']
print(f"   Ethics Score: {score['ethics_score']:.2f}/100")
print(f"   Resilience Score: {score['resilience_score']:.2f}/100")
print(f"   Security Score: {score['security_score']:.2f}/100")
print(f"   Coordination Score: {score['coordination_score']:.2f}/100")
print(f"   Adaptability Score: {score['adaptability_score']:.2f}/100")
print()

# 7. Run full round
print("7️⃣  Running full Round 1...")
round_results = swr.run_round(1, simple_ai_system, "demo_system")
print(f"   ✓ Completed {len(round_results)} scenarios")
avg_score = sum(r['sovereign_resilience_score'] for r in round_results) / len(round_results)
print(f"   Average SRS: {avg_score:.2f}/100")
print()

# 8. View leaderboard
print("8️⃣  Current Leaderboard:")
leaderboard = swr.get_leaderboard()
for entry in leaderboard:
    print(f"   #{entry['rank']} {entry['system_id']}: {entry['avg_sovereign_resilience_score']:.2f} "
          f"({entry['total_attempts']} attempts, {entry['success_rate']*100:.1f}% success)")
print()

# 9. Get system performance
print("9️⃣  System Performance Details:")
performance = swr.scoreboard.get_system_performance("demo_system")
print(f"   Total Attempts: {performance['overall_performance']['total_attempts']}")
print(f"   Success Rate: {performance['overall_performance']['success_rate']*100:.1f}%")
print(f"   Avg SRS: {performance['overall_performance']['avg_sovereign_resilience_score']:.2f}")
print(f"   Avg Response Time: {performance['overall_performance']['avg_response_time_ms']:.2f}ms")
print()

print("   Category Scores:")
for category, score in performance['category_scores'].items():
    print(f"     {category.capitalize()}: {score:.2f}/100")
print()

# 10. Verify integrity
print("🔟 Verifying Result Integrity...")
first_result = round_results[0]
is_valid = swr.verify_result_integrity(first_result)
print(f"   Result integrity: {'✓ VALID' if is_valid else '✗ INVALID'}")
print(f"   Cryptographic attestation verified: {is_valid}")
print()

print("=" * 80)
print("🎉 Demo complete! SOVEREIGN WAR ROOM is fully operational.")
print("=" * 80)
print()
print("Next steps:")
print("  • Run: python cli.py --help")
print("  • Start API: python cli.py serve")
print("  • Start Web: python cli.py web")
print("  • Run tests: pytest tests/ -v")
print()
