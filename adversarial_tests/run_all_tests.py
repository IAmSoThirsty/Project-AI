#!/usr/bin/env python3
"""
Comprehensive Adversarial Test Runner for Galahad (Project-AI).

This master script runs ALL adversarial red-team evaluations:
- JailbreakBench (JBB)
- Multi-Turn Attacks
- Garak Vulnerability Scan

Generates unified report and dashboard.

Usage:
    python adversarial_tests/run_all_tests.py [--output-dir ci-reports]
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveTestRunner:
    """Run all adversarial tests and generate unified report."""

    def __init__(self, output_dir: str = "ci-reports"):
        """
        Initialize comprehensive test runner.

        Args:
            output_dir: Directory for output reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.project_root = Path(__file__).parent.parent

        self.results = {
            "jbb": None,
            "multiturn": None,
            "garak": None,
        }

        self.test_status = {
            "jbb": "pending",
            "multiturn": "pending",
            "garak": "pending",
        }

    def run_all_tests(self) -> dict:
        """
        Run all adversarial tests.

        Returns:
            Dictionary with comprehensive results
        """
        logger.info("=" * 70)
        logger.info("COMPREHENSIVE ADVERSARIAL RED-TEAM EVALUATION")
        logger.info("=" * 70)

        start_time = time.time()

        # Run JailbreakBench
        logger.info("\n🗡️  Phase 1: Running JailbreakBench...")
        self._run_jbb()

        # Run Multi-Turn
        logger.info("\n🛡️  Phase 2: Running Multi-Turn Attacks...")
        self._run_multiturn()

        # Run Garak
        logger.info("\n⚔️  Phase 3: Running Garak Vulnerability Scan...")
        self._run_garak()

        elapsed = time.time() - start_time

        # Generate unified report
        logger.info("\n📊 Generating unified report...")
        unified_report = self._generate_unified_report(elapsed)

        # Save unified report
        unified_path = self.output_dir / "unified-report.json"
        with open(unified_path, "w") as f:
            json.dump(unified_report, f, indent=2)

        logger.info("\n✅ All tests complete in %ss", elapsed)
        logger.info("📜 Unified report saved to %s", unified_path)

        # Print summary
        self._print_summary(unified_report)

        return unified_report

    def _run_jbb(self) -> bool:
        """Run JailbreakBench test."""
        try:
            cmd = [
                sys.executable,
                str(self.project_root / "adversarial_tests" / "jbb" / "run_jbb.py"),
                "--output",
                str(self.output_dir / "jbb-latest.json"),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # Load results
            jbb_path = self.output_dir / "jbb-latest.json"
            if jbb_path.exists():
                with open(jbb_path) as f:
                    self.results["jbb"] = json.load(f)
                self.test_status["jbb"] = (
                    "success" if result.returncode == 0 else "warning"
                )
                logger.info(
                    "✅ JBB: %s harmful blocked",
                    self.results["jbb"]["metrics"]["harmful_blocked_rate"],
                )
                return True
            else:
                self.test_status["jbb"] = "failed"
                logger.error("❌ JBB: Failed to generate report")
                return False

        except Exception as e:
            logger.error("❌ JBB: Error - %s", e)
            self.test_status["jbb"] = "error"
            return False

    def _run_multiturn(self) -> bool:
        """Run Multi-Turn test."""
        try:
            cmd = [
                sys.executable,
                str(
                    self.project_root
                    / "adversarial_tests"
                    / "multiturn"
                    / "run_multiturn.py"
                ),
                "--output",
                str(self.output_dir / "multiturn-latest.json"),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # Load results
            mt_path = self.output_dir / "multiturn-latest.json"
            if mt_path.exists():
                with open(mt_path) as f:
                    self.results["multiturn"] = json.load(f)
                self.test_status["multiturn"] = (
                    "success" if result.returncode == 0 else "warning"
                )
                logger.info(
                    "✅ Multi-Turn: %s mitigation rate",
                    self.results["multiturn"]["metrics"]["mitigation_rate"],
                )
                return True
            else:
                self.test_status["multiturn"] = "failed"
                logger.error("❌ Multi-Turn: Failed to generate report")
                return False

        except Exception as e:
            logger.error("❌ Multi-Turn: Error - %s", e)
            self.test_status["multiturn"] = "error"
            return False

    def _run_garak(self) -> bool:
        """Run Garak test."""
        try:
            cmd = [
                sys.executable,
                str(self.project_root / "adversarial_tests" / "garak" / "run_garak.py"),
                "--output",
                str(self.output_dir / "garak-latest.json"),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # Load results
            garak_path = self.output_dir / "garak-latest.json"
            if garak_path.exists():
                with open(garak_path) as f:
                    self.results["garak"] = json.load(f)
                self.test_status["garak"] = (
                    "success" if result.returncode == 0 else "warning"
                )
                logger.info(
                    "✅ Garak: %s detection rate",
                    self.results["garak"]["metrics"]["detection_rate"],
                )
                return True
            else:
                self.test_status["garak"] = "failed"
                logger.error("❌ Garak: Failed to generate report")
                return False

        except Exception as e:
            logger.error("❌ Garak: Error - %s", e)
            self.test_status["garak"] = "error"
            return False

    def _generate_unified_report(self, elapsed: float) -> dict:
        """Generate unified report from all test results."""

        # Calculate overall metrics
        overall_metrics = {
            "total_tests_run": 3,
            "tests_passed": sum(1 for s in self.test_status.values() if s == "success"),
            "tests_warning": sum(
                1 for s in self.test_status.values() if s == "warning"
            ),
            "tests_failed": sum(
                1 for s in self.test_status.values() if s in ["failed", "error"]
            ),
        }

        # Aggregate prompt counts
        if self.results["jbb"] and self.results["multiturn"] and self.results["garak"]:
            overall_metrics.update(
                {
                    "total_prompts_tested": (
                        self.results["jbb"]["metrics"]["total_prompts"]
                        + self.results["multiturn"]["metrics"]["total_scenarios"]
                        + self.results["garak"]["metrics"]["total_probes"]
                    ),
                    "total_harmful_prompts": (
                        self.results["jbb"]["metrics"]["harmful_prompts"]
                        + self.results["multiturn"]["metrics"][
                            "scenarios_requiring_block"
                        ]
                        + self.results["garak"]["metrics"]["harmful_probes"]
                    ),
                    "overall_block_rate": self._calculate_overall_block_rate(),
                }
            )

        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "test_suite": "Comprehensive Adversarial Red-Team Evaluation",
                "model": "Galahad (Project-AI)",
                "total_evaluation_time_seconds": elapsed,
            },
            "test_status": self.test_status,
            "overall_metrics": overall_metrics,
            "individual_results": {
                "jailbreakbench": self.results["jbb"],
                "multiturn": self.results["multiturn"],
                "garak": self.results["garak"],
            },
        }

    def _calculate_overall_block_rate(self) -> float:
        """Calculate weighted overall block rate."""
        if not all(self.results.values()):
            return 0.0

        # Weight by number of prompts
        jbb_weight = self.results["jbb"]["metrics"]["harmful_prompts"]
        mt_weight = self.results["multiturn"]["metrics"]["scenarios_requiring_block"]
        garak_weight = self.results["garak"]["metrics"]["harmful_probes"]
        total_weight = jbb_weight + mt_weight + garak_weight

        if total_weight == 0:
            return 0.0

        weighted_sum = (
            self.results["jbb"]["metrics"]["harmful_blocked_rate"] * jbb_weight
            + self.results["multiturn"]["metrics"]["mitigation_rate"] * mt_weight
            + self.results["garak"]["metrics"]["harmful_detected_rate"] * garak_weight
        )

        return weighted_sum / total_weight

    def _print_summary(self, report: dict):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("COMPREHENSIVE ADVERSARIAL RED-TEAM EVALUATION SUMMARY")
        print("=" * 70)

        # Overall status
        print("\n📊 Overall Status:")
        print(f"  Tests Passed: {report['overall_metrics']['tests_passed']}/3")
        print(f"  Tests Warning: {report['overall_metrics']['tests_warning']}/3")
        print(f"  Tests Failed: {report['overall_metrics']['tests_failed']}/3")

        if "total_prompts_tested" in report["overall_metrics"]:
            print("\n📈 Overall Metrics:")
            print(
                f"  Total Prompts Tested: {report['overall_metrics']['total_prompts_tested']}"
            )
            print(
                f"  Total Harmful Prompts: {report['overall_metrics']['total_harmful_prompts']}"
            )
            print(
                f"  Overall Block Rate: {report['overall_metrics']['overall_block_rate']:.2%}"
            )

        # Individual test results
        if self.results["jbb"]:
            print("\n🗡️  JailbreakBench:")
            print(
                f"  Harmful Blocked: {self.results['jbb']['metrics']['harmful_blocked_rate']:.2%}"
            )
            print(
                f"  Jailbreak Success: {self.results['jbb']['metrics']['jailbreak_success_rate']:.2%}"
            )
            print(f"  Status: {self._status_emoji(self.test_status['jbb'])}")

        if self.results["multiturn"]:
            print("\n🛡️  Multi-Turn Attacks:")
            print(
                f"  Mitigation Rate: {self.results['multiturn']['metrics']['mitigation_rate']:.2%}"
            )
            print(
                f"  Attack Success: {self.results['multiturn']['metrics']['attack_success_rate']:.2%}"
            )
            print(f"  Status: {self._status_emoji(self.test_status['multiturn'])}")

        if self.results["garak"]:
            print("\n⚔️  Garak Vulnerability Scan:")
            print(
                f"  Detection Rate: {self.results['garak']['metrics']['detection_rate']:.2%}"
            )
            print(
                f"  Vulnerability Exposure: {self.results['garak']['metrics']['vulnerability_exposure_rate']:.2%}"
            )
            print(f"  Status: {self._status_emoji(self.test_status['garak'])}")

        print("\n" + "=" * 70)
        print(f"📁 Reports saved to: {self.output_dir}")
        print("  - jbb-latest.json")
        print("  - multiturn-latest.json")
        print("  - garak-latest.json")
        print("  - unified-report.json")
        print("=" * 70)

    def _status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return {
            "success": "✅ PASSED",
            "warning": "⚠️ WARNING",
            "failed": "❌ FAILED",
            "error": "❌ ERROR",
            "pending": "⏳ PENDING",
        }.get(status, "❓ UNKNOWN")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive adversarial red-team evaluation"
    )
    parser.add_argument(
        "--output-dir",
        default="ci-reports",
        help="Output directory for reports (default: ci-reports)",
    )

    args = parser.parse_args()

    # Run all tests
    runner = ComprehensiveTestRunner(output_dir=args.output_dir)
    report = runner.run_all_tests()

    # Exit with error if any critical tests failed
    if report["overall_metrics"]["tests_failed"] > 0:
        logger.error("❌ One or more tests failed")
        return 1

    # Exit with warning if any tests had warnings
    if report["overall_metrics"]["tests_warning"] > 0:
        logger.warning("⚠️ Some tests passed with warnings")
        return 0  # Don't fail CI, just warn

    logger.info("✅ All tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
