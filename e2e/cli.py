"""
E2E Test Orchestration CLI

Production-grade CLI for running comprehensive E2E test suites with:
- Test discovery and filtering
- Parallel execution
- Coverage reporting
- HTML/JSON report generation
- Artifact management
- CI/CD integration
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from e2e.reporting.artifact_manager import ArtifactManager
from e2e.reporting.coverage_reporter import CoverageReporter
from e2e.reporting.html_reporter import HTMLReporter
from e2e.reporting.json_reporter import JSONReporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class E2EOrchestrator:
    """Orchestrates E2E test execution and reporting."""

    def __init__(
        self,
        test_paths: list[str] | None = None,
        markers: list[str] | None = None,
        parallel: bool = False,
        workers: int = 4,
        coverage: bool = True,
        html_report: bool = True,
        json_report: bool = True,
        verbose: bool = False,
    ):
        """Initialize E2E orchestrator.

        Args:
            test_paths: Paths to test files/directories
            markers: Pytest markers to filter tests
            parallel: Enable parallel execution
            workers: Number of parallel workers
            coverage: Enable coverage reporting
            html_report: Generate HTML report
            json_report: Generate JSON report
            verbose: Verbose output
        """
        self.test_paths = test_paths or ["e2e/scenarios"]
        self.markers = markers or []
        self.parallel = parallel
        self.workers = workers
        self.coverage = coverage
        self.html_report = html_report
        self.json_report = json_report
        self.verbose = verbose

        # Initialize managers
        self.artifact_mgr = ArtifactManager()
        self.coverage_reporter = CoverageReporter()
        self.html_reporter = HTMLReporter()
        self.json_reporter = JSONReporter()

        logger.info("E2E Orchestrator initialized")

    def run_tests(self) -> int:
        """Run E2E tests and generate reports.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        logger.info("=" * 70)
        logger.info("Starting E2E Test Execution")
        logger.info("=" * 70)

        start_time = datetime.now()

        # Build pytest command
        pytest_cmd = self._build_pytest_command()

        logger.info("Pytest command: %s", " ".join(pytest_cmd))

        # Execute tests
        import subprocess

        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("Test execution completed in %ss", duration)

        # Parse test results
        test_results = self._parse_pytest_output(result.stdout, duration)

        # Save logs
        self.artifact_mgr.save_log("pytest_stdout", result.stdout)
        self.artifact_mgr.save_log("pytest_stderr", result.stderr)

        # Generate coverage report
        coverage_metrics = None
        if self.coverage:
            coverage_metrics = self._generate_coverage_report()

        # Generate HTML report
        if self.html_report:
            self._generate_html_report(test_results, coverage_metrics)

        # Generate JSON report
        if self.json_report:
            self._generate_json_report(test_results, coverage_metrics)

        # Print summary
        self._print_summary(test_results, coverage_metrics)

        # Cleanup old artifacts
        self.artifact_mgr.cleanup_old_artifacts(keep_last=10)

        logger.info("=" * 70)
        logger.info("E2E Test Execution Complete")
        logger.info("=" * 70)

        return result.returncode

    def _build_pytest_command(self) -> list[str]:
        """Build pytest command with all options.

        Returns:
            List of command arguments
        """
        cmd = ["pytest"]

        # Add test paths
        cmd.extend(self.test_paths)

        # Add markers
        if self.markers:
            marker_expr = " and ".join(self.markers)
            cmd.extend(["-m", marker_expr])

        # Verbose output
        if self.verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")

        # Parallel execution
        if self.parallel:
            cmd.extend(["-n", str(self.workers)])

        # Coverage
        if self.coverage:
            source_paths = ["src", "e2e"]
            cmd.append(f"--cov={','.join(source_paths)}")
            cmd.append("--cov-report=json")
            cmd.append("--cov-report=html")
            cmd.append("--cov-report=xml")

        # Test output options
        cmd.extend(
            [
                "--tb=short",
                "--strict-markers",
                f"--junit-xml={self.artifact_mgr.current_run_dir}/junit.xml",
            ]
        )

        return cmd

    def _parse_pytest_output(self, output: str, duration: float) -> dict:
        """Parse pytest output to extract results.

        Args:
            output: Pytest stdout
            duration: Test execution duration

        Returns:
            Dictionary with test results
        """
        # Parse test counts from output
        import re

        passed = 0
        failed = 0
        skipped = 0
        errors = 0

        # Look for pytest summary line
        summary_pattern = r"(\d+) passed"
        match = re.search(summary_pattern, output)
        if match:
            passed = int(match.group(1))

        failed_pattern = r"(\d+) failed"
        match = re.search(failed_pattern, output)
        if match:
            failed = int(match.group(1))

        skipped_pattern = r"(\d+) skipped"
        match = re.search(skipped_pattern, output)
        if match:
            skipped = int(match.group(1))

        error_pattern = r"(\d+) error"
        match = re.search(error_pattern, output)
        if match:
            errors = int(match.group(1))

        total = passed + failed + skipped + errors

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total_duration": duration,
            "test_suites": [],  # Would parse detailed results
        }

    def _generate_coverage_report(self) -> dict | None:
        """Generate coverage report.

        Returns:
            Coverage metrics dictionary
        """
        try:
            logger.info("Generating coverage report...")

            # Coverage was already run with pytest
            # Just parse the results
            import json

            coverage_file = Path("e2e/coverage/coverage.json")
            if not coverage_file.exists():
                coverage_file = Path("coverage.json")

            if coverage_file.exists():
                data = json.loads(coverage_file.read_text())
                totals = data.get("totals", {})

                return {
                    "total_statements": totals.get("num_statements", 0),
                    "covered_statements": totals.get("covered_lines", 0),
                    "missing_statements": totals.get("missing_lines", 0),
                    "coverage_percentage": totals.get("percent_covered", 0.0),
                }

            logger.warning("Coverage file not found")
            return None

        except Exception as e:
            logger.error("Failed to generate coverage report: %s", e)
            return None

    def _generate_html_report(
        self,
        test_results: dict,
        coverage_metrics: dict | None,
    ) -> None:
        """Generate HTML report.

        Args:
            test_results: Test execution results
            coverage_metrics: Coverage metrics
        """
        try:
            logger.info("Generating HTML report...")

            artifacts = self.artifact_mgr.get_artifact_summary()

            report_path = self.html_reporter.generate_report(
                test_results,
                coverage_metrics,
                artifacts,
            )

            logger.info("HTML report: %s", report_path)

        except Exception as e:
            logger.error("Failed to generate HTML report: %s", e)

    def _generate_json_report(
        self,
        test_results: dict,
        coverage_metrics: dict | None,
    ) -> None:
        """Generate JSON report.

        Args:
            test_results: Test execution results
            coverage_metrics: Coverage metrics
        """
        try:
            logger.info("Generating JSON report...")

            run_id = self.artifact_mgr.run_id
            artifacts = self.artifact_mgr.get_artifact_summary()

            # Create empty test suite for now
            test_suite = self.json_reporter.create_test_suite(
                suite_name="E2E Tests",
                tests=[],
            )

            report = self.json_reporter.create_report(
                run_id=run_id,
                environment="e2e",
                test_suites=[test_suite],
                coverage_percentage=(
                    coverage_metrics.get("coverage_percentage")
                    if coverage_metrics
                    else None
                ),
                artifacts_summary=artifacts,
            )

            report_path = self.json_reporter.save_report(report)
            logger.info("JSON report: %s", report_path)

        except Exception as e:
            logger.error("Failed to generate JSON report: %s", e)

    def _print_summary(
        self,
        test_results: dict,
        coverage_metrics: dict | None,
    ) -> None:
        """Print test summary.

        Args:
            test_results: Test execution results
            coverage_metrics: Coverage metrics
        """
        print("\n" + "=" * 70)
        print("E2E TEST SUMMARY")
        print("=" * 70)

        total = test_results["total_tests"]
        passed = test_results["passed"]
        failed = test_results["failed"]
        skipped = test_results["skipped"]
        duration = test_results["total_duration"]

        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests:    {total}")
        print(f"Passed:         {passed} ({pass_rate:.1f}%)")
        print(f"Failed:         {failed}")
        print(f"Skipped:        {skipped}")
        print(f"Duration:       {duration:.2f}s")

        if coverage_metrics:
            print("\nCoverage:")
            print(f"  Percentage:   {coverage_metrics['coverage_percentage']:.2f}%")
            print(
                f"  Statements:   {coverage_metrics['covered_statements']}/{coverage_metrics['total_statements']}"
            )

        artifacts = self.artifact_mgr.get_artifact_summary()
        print("\nArtifacts:")
        print(f"  Logs:         {artifacts['logs']}")
        print(f"  Screenshots:  {artifacts['screenshots']}")
        print(f"  Dumps:        {artifacts['dumps']}")
        print(f"  Errors:       {artifacts['errors']}")

        print("\nReports:")
        print(f"  Directory:    {self.artifact_mgr.current_run_dir}")

        print("=" * 70)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Project-AI E2E Test Orchestration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all E2E tests
  python -m e2e.cli

  # Run specific test markers
  python -m e2e.cli -m e2e -m api

  # Run with parallel execution
  python -m e2e.cli --parallel --workers 8

  # Run without coverage
  python -m e2e.cli --no-coverage

  # Verbose output
  python -m e2e.cli -vv
        """,
    )

    parser.add_argument(
        "paths",
        nargs="*",
        default=["e2e/scenarios"],
        help="Test paths (default: e2e/scenarios)",
    )

    parser.add_argument(
        "-m",
        "--marker",
        action="append",
        dest="markers",
        help="Pytest markers to filter tests",
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel test execution",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )

    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting",
    )

    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Disable HTML report generation",
    )

    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Disable JSON report generation",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "-vv",
        "--very-verbose",
        action="store_true",
        help="Very verbose output",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = E2EOrchestrator(
        test_paths=args.paths,
        markers=args.markers,
        parallel=args.parallel,
        workers=args.workers,
        coverage=not args.no_coverage,
        html_report=not args.no_html,
        json_report=not args.no_json,
        verbose=args.verbose or args.very_verbose,
    )

    # Run tests
    exit_code = orchestrator.run_tests()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
