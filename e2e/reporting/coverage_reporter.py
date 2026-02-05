"""
Coverage Reporter for E2E Tests

Provides coverage analysis and reporting for E2E test execution.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Coverage metrics data."""

    total_statements: int
    covered_statements: int
    missing_statements: int
    coverage_percentage: float
    branch_coverage: float | None = None
    file_coverage: dict[str, float] | None = None


class CoverageReporter:
    """Generates coverage reports for E2E tests."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize coverage reporter.

        Args:
            output_dir: Directory for coverage reports
        """
        self.output_dir = output_dir or Path(__file__).parent.parent / "coverage"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_coverage(
        self, test_paths: list[str], source_paths: list[str]
    ) -> CoverageMetrics:
        """Run coverage analysis on test paths.

        Args:
            test_paths: Paths to test files/directories
            source_paths: Paths to source code to measure coverage

        Returns:
            Coverage metrics
        """
        try:
            # Run pytest with coverage
            cmd = [
                "pytest",
                *test_paths,
                f"--cov={','.join(source_paths)}",
                f"--cov-report=json:{self.output_dir}/coverage.json",
                f"--cov-report=html:{self.output_dir}/html",
                f"--cov-report=xml:{self.output_dir}/coverage.xml",
                "--cov-report=term-missing",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.warning(
                    f"Coverage run had non-zero exit code: {result.returncode}"
                )
                logger.debug(f"STDOUT: {result.stdout}")
                logger.debug(f"STDERR: {result.stderr}")

            # Parse coverage.json
            coverage_file = self.output_dir / "coverage.json"
            if coverage_file.exists():
                return self._parse_coverage_json(coverage_file)
            else:
                logger.error("Coverage JSON file not generated")
                return CoverageMetrics(0, 0, 0, 0.0)

        except Exception as e:
            logger.error(f"Failed to run coverage: {e}")
            return CoverageMetrics(0, 0, 0, 0.0)

    def _parse_coverage_json(self, coverage_file: Path) -> CoverageMetrics:
        """Parse coverage JSON file.

        Args:
            coverage_file: Path to coverage.json

        Returns:
            Parsed coverage metrics
        """
        try:
            data = json.loads(coverage_file.read_text())

            totals = data.get("totals", {})
            files = data.get("files", {})

            # Calculate file-level coverage
            file_coverage = {}
            for filepath, file_data in files.items():
                summary = file_data.get("summary", {})
                covered = summary.get("covered_lines", 0)
                total = summary.get("num_statements", 1)
                file_coverage[filepath] = (covered / total) * 100 if total > 0 else 0.0

            return CoverageMetrics(
                total_statements=totals.get("num_statements", 0),
                covered_statements=totals.get("covered_lines", 0),
                missing_statements=totals.get("missing_lines", 0),
                coverage_percentage=totals.get("percent_covered", 0.0),
                branch_coverage=totals.get("percent_covered_display", None),
                file_coverage=file_coverage,
            )

        except Exception as e:
            logger.error(f"Failed to parse coverage JSON: {e}")
            return CoverageMetrics(0, 0, 0, 0.0)

    def generate_summary_report(self, metrics: CoverageMetrics) -> str:
        """Generate text summary report.

        Args:
            metrics: Coverage metrics

        Returns:
            Formatted summary report
        """
        report = []
        report.append("=" * 70)
        report.append("E2E Test Coverage Summary")
        report.append("=" * 70)
        report.append(f"Total Statements:      {metrics.total_statements}")
        report.append(f"Covered Statements:    {metrics.covered_statements}")
        report.append(f"Missing Statements:    {metrics.missing_statements}")
        report.append(f"Coverage Percentage:   {metrics.coverage_percentage:.2f}%")

        if metrics.branch_coverage:
            report.append(f"Branch Coverage:       {metrics.branch_coverage:.2f}%")

        report.append("")
        report.append("File Coverage:")
        report.append("-" * 70)

        if metrics.file_coverage:
            # Sort by coverage percentage (ascending)
            sorted_files = sorted(
                metrics.file_coverage.items(),
                key=lambda x: x[1],
            )

            for filepath, coverage in sorted_files[:10]:  # Show worst 10
                report.append(f"  {filepath:<50} {coverage:>6.2f}%")

        report.append("=" * 70)

        return "\n".join(report)

    def check_threshold(
        self, metrics: CoverageMetrics, threshold: float = 80.0
    ) -> bool:
        """Check if coverage meets threshold.

        Args:
            metrics: Coverage metrics
            threshold: Minimum required coverage percentage

        Returns:
            True if threshold met, False otherwise
        """
        meets_threshold = metrics.coverage_percentage >= threshold

        if not meets_threshold:
            logger.warning(
                f"Coverage {metrics.coverage_percentage:.2f}% below threshold {threshold}%"
            )
        else:
            logger.info(
                f"Coverage {metrics.coverage_percentage:.2f}% meets threshold {threshold}%"
            )

        return meets_threshold

    def save_report(self, metrics: CoverageMetrics, filename: str = "coverage_report.txt") -> Path:
        """Save coverage report to file.

        Args:
            metrics: Coverage metrics
            filename: Output filename

        Returns:
            Path to saved report
        """
        report = self.generate_summary_report(metrics)
        report_file = self.output_dir / filename
        report_file.write_text(report)
        logger.info(f"Saved coverage report: {report_file}")
        return report_file
