"""
Test runner script for Anti-Sovereign Tier Conversational Stress Tests.

Usage:
    python -m src.app.testing.run_anti_sovereign_tests [options]

Options:
    --generate-only: Only generate tests, don't run them
    --parallel N: Number of parallel tests (default: 10)
    --max-turns N: Maximum turns per test (default: 2000)
    --resume: Resume from checkpoint
    --report-only: Generate report from existing results
    --dashboard: Generate HTML dashboard
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.testing.anti_sovereign_stress_tests import AntiSovereignStressTestGenerator
from src.app.testing.conversational_stress_orchestrator import (
    ConversationalStressTestOrchestrator,
    OrchestratorConfig,
)
from src.app.testing.stress_test_dashboard import (
    ConversationalStressTestDashboard,
    generate_html_dashboard,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("anti_sovereign_tests.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Anti-Sovereign Tier Conversational Stress Tests"
    )

    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate tests without running them",
    )

    parser.add_argument(
        "--parallel",
        type=int,
        default=10,
        help="Number of tests to run in parallel (default: 10)",
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=2000,
        help="Maximum turns per test (default: 2000)",
    )

    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=50,
        help="Checkpoint interval in turns (default: 50)",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous checkpoint",
    )

    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report from existing results without running tests",
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Generate HTML dashboard",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/anti_sovereign_tests/results",
        help="Output directory for results",
    )

    parser.add_argument(
        "--test-count",
        type=int,
        default=400,
        help="Number of tests to generate (default: 400)",
    )

    return parser.parse_args()


async def main():
    """Main entry point for test runner."""
    args = parse_args()

    print("=" * 80)
    print("ANTI-SOVEREIGN TIER CONVERSATIONAL STRESS TEST RUNNER")
    print("=" * 80)
    print()

    # Initialize components
    logger.info("Initializing test components...")

    generator = AntiSovereignStressTestGenerator()
    dashboard = ConversationalStressTestDashboard()

    # Handle report-only mode
    if args.report_only:
        logger.info("Generating report from existing results...")
        print("\nGenerating comprehensive report...")

        report = dashboard.generate_comprehensive_report(include_replays=True)

        if report["success"]:
            print(f"\n✓ Report generated: {report['report']['report_file']}")
            print("\nExecutive Summary:")
            summary = report["report"]["executive_summary"]
            print(f"  Total Tests: {summary['total_tests']}")
            print(f"  Tests Passed: {summary['tests_passed']}")
            print(f"  Tests Failed: {summary['tests_failed']}")
            print(f"  Success Rate: {summary['success_rate']:.1%}")
            print(f"  Total Turns: {summary['total_conversation_turns']:,}")
            print(f"  Total Breaches: {summary['total_breaches_detected']}")
            print(f"  Breach Rate: {summary['overall_breach_rate']:.2%}")
        else:
            print(f"\n✗ Error generating report: {report.get('error')}")
            return 1

        if args.dashboard:
            print("\nGenerating HTML dashboard...")
            dashboard_path = generate_html_dashboard(dashboard)
            print(f"✓ Dashboard generated: {dashboard_path}")

        return 0

    # Generate tests
    print("\nGenerating conversational stress tests...")
    print(f"Target: {args.test_count} tests with 200+ turns minimum each")

    start_time = time.time()
    tests = generator.generate_all_tests()
    generation_time = time.time() - start_time

    # Verify we have the right number of tests
    actual_count = len(tests)
    if actual_count != args.test_count:
        logger.warning(
            "Generated %d tests, expected %d", actual_count, args.test_count
        )

    print(f"✓ Generated {actual_count} tests in {generation_time:.1f} seconds")

    # Export tests
    export_path = generator.export_tests()
    print(f"✓ Tests exported to: {export_path}")

    # Generate summary
    summary = generator.generate_summary()
    print("\nTest Suite Summary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Categories: {summary['total_categories']}")
    print(f"  Avg Minimum Turns: {summary['average_minimum_turns']}")
    print(f"  Estimated Total Turns: {summary['estimated_total_turns']}")
    print(f"  Phases Per Test: {summary['phases_per_test']}")
    print(f"  Difficulty: {summary['difficulty_level']}")

    if args.generate_only:
        print("\n✓ Test generation complete (--generate-only specified)")
        return 0

    # Configure orchestrator
    print("\nConfiguring test orchestrator...")

    config = OrchestratorConfig(
        max_parallel_tests=args.parallel,
        max_turns_per_test=args.max_turns,
        checkpoint_interval=args.checkpoint_interval,
        enable_progress_tracking=True,
        enable_real_time_metrics=True,
        output_dir=args.output_dir,
    )

    print(f"  Parallel Tests: {config.max_parallel_tests}")
    print(f"  Max Turns Per Test: {config.max_turns_per_test}")
    print(f"  Checkpoint Interval: {config.checkpoint_interval} turns")
    print(f"  Resume From Checkpoint: {args.resume}")

    orchestrator = ConversationalStressTestOrchestrator(
        config=config, test_generator=generator
    )

    # Run tests
    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)
    print()
    print("This will execute 400 conversational stress tests.")
    print("Each test consists of 4 phases with 200+ turns minimum.")
    print("Estimated total conversation turns: 100,000+")
    print()

    input("Press Enter to start test execution (or Ctrl+C to cancel)...")

    print("\nStarting test execution...")
    execution_start = time.time()

    try:
        results = await orchestrator.run_all_tests(
            tests=tests, resume_from_checkpoint=args.resume
        )

        execution_time = time.time() - execution_start

        # Display results
        print("\n" + "=" * 80)
        print("TEST EXECUTION COMPLETE")
        print("=" * 80)
        print()

        summary = results["executive_summary"]
        print("Executive Summary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Tests Passed: {summary['tests_passed']}")
        print(f"  Tests Failed: {summary['tests_failed']}")
        print(f"  Success Rate: {summary['success_rate']:.1%}")
        print(f"  Total Turns: {summary['total_turns_executed']:,}")
        print(f"  Avg Turns/Test: {summary['average_turns_per_test']:.1f}")
        print(f"  Total Breaches: {summary['total_breaches_detected']}")
        print(f"  Total Defenses: {summary['total_defenses_held']}")
        print(f"  Execution Time: {execution_time:.1f} seconds ({execution_time/3600:.2f} hours)")

        print("\nCategory Breakdown:")
        for category, stats in results.get("category_breakdown", {}).items():
            print(f"  {category}:")
            print(f"    Total: {stats['total']}")
            print(f"    Passed: {stats['passed']}")
            print(f"    Failed: {stats['failed']}")

        print("\nRecommendations:")
        for i, rec in enumerate(results.get("recommendations", []), 1):
            print(f"  {i}. {rec}")

        # Generate final report
        print("\nGenerating comprehensive report...")
        report = dashboard.generate_comprehensive_report(include_replays=True)

        if report["success"]:
            print(f"✓ Report saved to: {report['report']['report_file']}")

        # Generate dashboard if requested
        if args.dashboard:
            print("\nGenerating HTML dashboard...")
            dashboard_path = generate_html_dashboard(dashboard)
            print(f"✓ Dashboard generated: {dashboard_path}")

        print("\n✓ All tasks complete!")
        return 0

    except KeyboardInterrupt:
        print("\n\n✗ Test execution interrupted by user")
        print("Progress has been checkpointed. Use --resume to continue.")
        return 1

    except Exception as e:
        logger.error("Error during test execution: %s", e, exc_info=True)
        print(f"\n✗ Error during test execution: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
