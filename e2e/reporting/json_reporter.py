"""
JSON Reporter for E2E Tests

Generates machine-readable JSON reports for E2E test results.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result."""

    test_name: str
    test_file: str
    status: str  # passed, failed, skipped, error
    duration: float
    error_message: str | None = None
    error_trace: str | None = None
    markers: list[str] | None = None
    artifacts: list[str] | None = None


@dataclass
class TestSuite:
    """Test suite results."""

    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    tests: list[TestResult]


@dataclass
class E2ETestReport:
    """Complete E2E test report."""

    run_id: str
    timestamp: str
    environment: str
    total_duration: float
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    coverage_percentage: float | None
    test_suites: list[TestSuite]
    artifacts_summary: dict[str, Any] | None = None


class JSONReporter:
    """Generates JSON reports for E2E tests."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize JSON reporter.

        Args:
            output_dir: Directory for JSON reports
        """
        self.output_dir = output_dir or Path(__file__).parent.parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_test_result(
        self,
        test_name: str,
        test_file: str,
        status: str,
        duration: float,
        error_message: str | None = None,
        error_trace: str | None = None,
        markers: list[str] | None = None,
        artifacts: list[str] | None = None,
    ) -> TestResult:
        """Create a test result object.

        Args:
            test_name: Name of the test
            test_file: File containing the test
            status: Test status
            duration: Test duration in seconds
            error_message: Error message if test failed
            error_trace: Stack trace if test failed
            markers: Pytest markers for the test
            artifacts: List of artifact paths

        Returns:
            TestResult object
        """
        return TestResult(
            test_name=test_name,
            test_file=test_file,
            status=status,
            duration=duration,
            error_message=error_message,
            error_trace=error_trace,
            markers=markers or [],
            artifacts=artifacts or [],
        )

    def create_test_suite(
        self,
        suite_name: str,
        tests: list[TestResult],
    ) -> TestSuite:
        """Create a test suite object.

        Args:
            suite_name: Name of the test suite
            tests: List of test results

        Returns:
            TestSuite object
        """
        total = len(tests)
        passed = sum(1 for t in tests if t.status == "passed")
        failed = sum(1 for t in tests if t.status == "failed")
        skipped = sum(1 for t in tests if t.status == "skipped")
        errors = sum(1 for t in tests if t.status == "error")
        duration = sum(t.duration for t in tests)

        return TestSuite(
            suite_name=suite_name,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
            tests=tests,
        )

    def create_report(
        self,
        run_id: str,
        environment: str,
        test_suites: list[TestSuite],
        coverage_percentage: float | None = None,
        artifacts_summary: dict[str, Any] | None = None,
    ) -> E2ETestReport:
        """Create complete E2E test report.

        Args:
            run_id: Test run identifier
            environment: Test environment name
            test_suites: List of test suites
            coverage_percentage: Coverage percentage if available
            artifacts_summary: Summary of test artifacts

        Returns:
            E2ETestReport object
        """
        total_tests = sum(s.total_tests for s in test_suites)
        passed = sum(s.passed for s in test_suites)
        failed = sum(s.failed for s in test_suites)
        skipped = sum(s.skipped for s in test_suites)
        errors = sum(s.errors for s in test_suites)
        total_duration = sum(s.duration for s in test_suites)

        return E2ETestReport(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            environment=environment,
            total_duration=total_duration,
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            coverage_percentage=coverage_percentage,
            test_suites=test_suites,
            artifacts_summary=artifacts_summary,
        )

    def save_report(self, report: E2ETestReport, filename: str | None = None) -> Path:
        """Save report to JSON file.

        Args:
            report: E2E test report
            filename: Output filename (defaults to e2e_report_{run_id}.json)

        Returns:
            Path to saved report
        """
        if filename is None:
            filename = f"e2e_report_{report.run_id}.json"

        report_file = self.output_dir / filename
        report_dict = self._to_dict(report)

        report_file.write_text(json.dumps(report_dict, indent=2, default=str))
        logger.info("Saved JSON report: %s", report_file)
        return report_file

    def _to_dict(self, obj: Any) -> dict:
        """Convert dataclass to dictionary recursively.

        Args:
            obj: Object to convert

        Returns:
            Dictionary representation
        """
        if hasattr(obj, "__dataclass_fields__"):
            return {key: self._to_dict(value) for key, value in asdict(obj).items()}
        elif isinstance(obj, list):
            return [self._to_dict(item) for item in obj]
        else:
            return obj

    def load_report(self, filepath: Path) -> dict:
        """Load report from JSON file.

        Args:
            filepath: Path to JSON report

        Returns:
            Report dictionary
        """
        return json.loads(filepath.read_text())

    def merge_reports(self, report_files: list[Path]) -> E2ETestReport:
        """Merge multiple test reports into one.

        Args:
            report_files: List of report file paths

        Returns:
            Merged E2ETestReport
        """
        all_suites = []
        run_ids = []
        environment = None

        for report_file in report_files:
            data = self.load_report(report_file)
            run_ids.append(data["run_id"])
            environment = environment or data["environment"]

            for suite_data in data.get("test_suites", []):
                test_results = [
                    TestResult(**test_data) for test_data in suite_data.get("tests", [])
                ]
                suite = TestSuite(
                    suite_name=suite_data["suite_name"],
                    total_tests=suite_data["total_tests"],
                    passed=suite_data["passed"],
                    failed=suite_data["failed"],
                    skipped=suite_data["skipped"],
                    errors=suite_data["errors"],
                    duration=suite_data["duration"],
                    tests=test_results,
                )
                all_suites.append(suite)

        merged_run_id = f"merged_{'_'.join(run_ids)}"
        return self.create_report(
            run_id=merged_run_id,
            environment=environment or "unknown",
            test_suites=all_suites,
        )
