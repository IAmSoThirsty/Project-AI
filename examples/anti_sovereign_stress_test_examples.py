"""
Example usage of the Anti-Sovereign Tier Conversational Stress Testing Framework.

This script demonstrates how to:
1. Generate stress tests
2. Run a subset of tests
3. Generate reports and analytics
4. Use the dashboard
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.testing import (
    AntiSovereignStressTestGenerator,
    ConversationalStressTestOrchestrator,
    OrchestratorConfig,
    ConversationalStressTestDashboard,
    generate_html_dashboard,
)
from src.app.testing.governance_integration import (
    GovernanceIntegrationBridge,
    integrate_governance_with_orchestrator,
)


async def example_1_generate_tests():
    """Example 1: Generate all 400 stress tests."""
    print("=" * 80)
    print("Example 1: Generating 400 Conversational Stress Tests")
    print("=" * 80)
    print()

    generator = AntiSovereignStressTestGenerator()

    # Generate all tests
    tests = generator.generate_all_tests()
    print(f"Generated {len(tests)} tests")

    # Export to JSON
    filepath = generator.export_tests()
    print(f"Exported to: {filepath}")

    # Show summary
    summary = generator.generate_summary()
    print("\nSummary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Categories: {summary['total_categories']}")
    print(f"  Avg Min Turns: {summary['average_minimum_turns']}")
    print(f"  Estimated Total Turns: {summary['estimated_total_turns']}")

    # Show a sample test
    sample = tests[0]
    print(f"\nSample Test: {sample.test_id}")
    print(f"  Category: {sample.category}")
    print(f"  Title: {sample.title}")
    print(f"  Minimum Turns: {sample.minimum_turns}")
    print(f"  Phases: {len(sample.phases)}")

    return tests


async def example_2_run_small_subset():
    """Example 2: Run a small subset of tests (5 tests)."""
    print("\n" + "=" * 80)
    print("Example 2: Running Small Subset (5 tests)")
    print("=" * 80)
    print()

    # Generate tests
    generator = AntiSovereignStressTestGenerator()
    all_tests = generator.generate_all_tests()

    # Take first 5 tests
    subset = all_tests[:5]
    print(f"Running {len(subset)} tests...")

    # Configure orchestrator
    config = OrchestratorConfig(
        max_parallel_tests=2,  # Low parallelism for demo
        max_turns_per_test=500,  # Reduced for demo
        checkpoint_interval=25,
        output_dir="data/anti_sovereign_tests/demo_results",
    )

    orchestrator = ConversationalStressTestOrchestrator(config=config)

    # Enable governance integration
    governance_bridge = integrate_governance_with_orchestrator(orchestrator)
    print("Governance integration enabled")

    # Run tests
    results = await orchestrator.run_all_tests(tests=subset, resume_from_checkpoint=False)

    # Show results
    print("\nResults:")
    summary = results["executive_summary"]
    print(f"  Tests Completed: {summary['total_tests']}")
    print(f"  Tests Passed: {summary['tests_passed']}")
    print(f"  Tests Failed: {summary['tests_failed']}")
    print(f"  Success Rate: {summary['success_rate']:.1%}")
    print(f"  Total Turns: {summary['total_turns_executed']}")
    print(f"  Breaches Detected: {summary['total_breaches_detected']}")

    return results, governance_bridge


async def example_3_generate_reports(governance_bridge):
    """Example 3: Generate comprehensive reports and dashboard."""
    print("\n" + "=" * 80)
    print("Example 3: Generating Reports and Dashboard")
    print("=" * 80)
    print()

    dashboard = ConversationalStressTestDashboard(
        data_dir="data/anti_sovereign_tests/demo_results"
    )

    # Generate comprehensive report
    print("Generating comprehensive report...")
    report = dashboard.generate_comprehensive_report(include_replays=True)

    if report["success"]:
        print(f"✓ Report generated: {report['report']['report_file']}")

        # Show executive summary
        summary = report['report']['executive_summary']
        print("\nExecutive Summary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Success Rate: {summary['success_rate']:.1%}")
        print(f"  Total Turns: {summary['total_conversation_turns']}")
        print(f"  Breach Rate: {summary['overall_breach_rate']:.2%}")

        # Show recommendations
        print("\nRecommendations:")
        for i, rec in enumerate(report['report']['recommendations'], 1):
            print(f"  {i}. {rec}")

    # Generate HTML dashboard
    print("\nGenerating HTML dashboard...")
    dashboard_path = generate_html_dashboard(dashboard, "demo_dashboard.html")
    print(f"✓ Dashboard: {dashboard_path}")

    # Generate governance audit report
    if governance_bridge:
        print("\nGenerating governance audit report...")
        audit_report = governance_bridge.generate_governance_audit_report()

        if "summary" in audit_report:
            print(f"✓ Governance violations: {audit_report['summary']['total_violations']}")
            print(f"  By severity: {audit_report['summary']['by_severity']}")

    return report


async def example_4_analyze_patterns():
    """Example 4: Analyze vulnerability patterns."""
    print("\n" + "=" * 80)
    print("Example 4: Analyzing Vulnerability Patterns")
    print("=" * 80)
    print()

    dashboard = ConversationalStressTestDashboard(
        data_dir="data/anti_sovereign_tests/demo_results"
    )

    # Analyze patterns
    print("Analyzing vulnerability patterns...")
    analysis = dashboard.analyze_vulnerability_patterns()

    if analysis["success"]:
        patterns = analysis["analysis"]["vulnerability_patterns"]
        print(f"\n✓ Found {len(patterns)} vulnerability patterns")

        # Show top 3 patterns
        if patterns:
            print("\nTop Vulnerability Patterns:")
            for i, (pattern, data) in enumerate(
                sorted(patterns.items(), key=lambda x: x[1]["count"], reverse=True)[:3], 1
            ):
                print(f"  {i}. {pattern}")
                print(f"     Count: {data['count']}")
                print(f"     Avg Turn: {data['avg_turn']:.1f}")
                print(f"     Phases: {list(data['phases'].keys())}")

        # Show technique effectiveness
        techniques = analysis["analysis"]["attack_technique_effectiveness"]
        if techniques:
            print("\nMost Effective Attack Techniques:")
            for i, (tech, stats) in enumerate(
                sorted(techniques.items(), key=lambda x: x[1]["success_rate"], reverse=True)[:3], 1
            ):
                print(f"  {i}. {tech}")
                print(f"     Success Rate: {stats['success_rate']:.1%}")
                print(f"     Attempts: {stats['attempts']}, Successes: {stats['successes']}")

    return analysis


async def example_5_conversation_replay():
    """Example 5: Generate conversation replay for a session."""
    print("\n" + "=" * 80)
    print("Example 5: Conversation Replay")
    print("=" * 80)
    print()

    dashboard = ConversationalStressTestDashboard(
        data_dir="data/anti_sovereign_tests/demo_results"
    )

    # Load sessions
    sessions = dashboard._load_all_sessions()

    if not sessions:
        print("No sessions found for replay")
        return

    # Get first session
    session = sessions[0]
    session_id = session["session_id"]

    print(f"Generating replay for session: {session_id}")

    # Generate replay
    replay = dashboard.generate_conversation_replay(
        session_id, output_file=f"{session_id}_replay.json"
    )

    if replay["success"]:
        print(f"✓ Replay generated: {replay['replay'].get('replay_file', 'N/A')}")

        # Show summary
        metadata = replay['replay']['metadata']
        print(f"\nSession Summary:")
        print(f"  Test ID: {replay['replay']['test_info']['test_id']}")
        print(f"  Category: {replay['replay']['test_info']['category']}")
        print(f"  Total Turns: {metadata['total_turns']}")
        print(f"  Breaches: {metadata['total_breaches']}")
        print(f"  Test Passed: {metadata['test_passed']}")
        print(f"  Duration: {metadata['duration_seconds']:.1f}s")

        # Show phase transitions
        transitions = replay['replay']['phase_transitions']
        print(f"\nPhase Transitions: {len(transitions)}")
        for trans in transitions:
            print(f"  Turn {trans['turn']}: {trans['from_phase']} → {trans['to_phase']}")

        # Show breach timeline
        breaches = replay['replay']['breach_timeline']
        if breaches:
            print(f"\nBreach Timeline: {len(breaches)} breaches")
            for breach in breaches[:3]:  # Show first 3
                print(f"  Turn {breach['turn']} ({breach['phase']}): {breach['type']}")

    return replay


async def main():
    """Run all examples."""
    print("Anti-Sovereign Tier Conversational Stress Testing Framework")
    print("Example Usage Demonstrations")
    print()

    try:
        # Example 1: Generate tests
        tests = await example_1_generate_tests()

        # Example 2: Run small subset
        results, governance_bridge = await example_2_run_small_subset()

        # Example 3: Generate reports
        report = await example_3_generate_reports(governance_bridge)

        # Example 4: Analyze patterns
        analysis = await example_4_analyze_patterns()

        # Example 5: Conversation replay
        replay = await example_5_conversation_replay()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
