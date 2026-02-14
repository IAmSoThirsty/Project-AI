#!/usr/bin/env python3
"""
Comprehensive Code Validation Script for Project-AI

This script runs all validation checks on the codebase:
- Ruff linting (style, imports, complexity)
- Pytest (all test suites)
- MyPy (type checking)
- Bandit (security scanning)
- Black (code formatting)

Usage:
    python scripts/validate_all_code.py [--fix] [--fast] [--report]

Options:
    --fix       Auto-fix issues where possible
    --fast      Skip slow checks (e.g., full test suite)
    --report    Generate detailed validation report
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    """Result of a validation check."""

    name: str
    passed: bool
    errors: int
    warnings: int
    duration: float
    details: str
    fixable: int = 0


class CodeValidator:
    """Comprehensive code validation runner."""

    def __init__(self, fix: bool = False, fast: bool = False, report: bool = False):
        self.fix = fix
        self.fast = fast
        self.report = report
        self.results: list[ValidationResult] = []
        self.start_time = datetime.now()

    def run_command(
        self, cmd: list[str], name: str, timeout: int = 300
    ) -> ValidationResult:
        """Run a validation command and capture results."""
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*70}\n")

        start = datetime.now()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            duration = (datetime.now() - start).total_seconds()

            # Parse output for error/warning counts
            output = result.stdout + result.stderr
            errors = output.lower().count("error")
            warnings = output.lower().count("warning")

            passed = result.returncode == 0

            print(output[:2000])  # Print first 2000 chars
            if len(output) > 2000:
                print(f"\n... (truncated {len(output) - 2000} characters)")

            return ValidationResult(
                name=name,
                passed=passed,
                errors=errors,
                warnings=warnings,
                duration=duration,
                details=output[:5000],  # Store first 5000 chars
            )

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start).total_seconds()
            return ValidationResult(
                name=name,
                passed=False,
                errors=1,
                warnings=0,
                duration=duration,
                details=f"Timeout after {timeout}s",
            )
        except Exception as e:
            duration = (datetime.now() - start).total_seconds()
            return ValidationResult(
                name=name,
                passed=False,
                errors=1,
                warnings=0,
                duration=duration,
                details=str(e),
            )

    def validate_ruff(self) -> ValidationResult:
        """Run Ruff linting."""
        cmd = ["ruff", "check", ".", "--statistics"]
        if self.fix:
            cmd.extend(["--fix", "--unsafe-fixes"])

        result = self.run_command(cmd, "Ruff Linting")

        # Parse fixable count from output
        if "[*]" in result.details:
            try:
                fixable_line = [
                    line
                    for line in result.details.split("\n")
                    if "fixable with" in line.lower()
                ][0]
                result.fixable = int(
                    fixable_line.split("fixable")[0].strip().split()[-1]
                )
            except (IndexError, ValueError):
                pass

        return result

    def validate_black(self) -> ValidationResult:
        """Run Black formatting check."""
        cmd = ["black", "--check", "src/", "tests/", "scripts/"]
        if self.fix:
            cmd.remove("--check")

        return self.run_command(cmd, "Black Code Formatting")

    def validate_mypy(self) -> ValidationResult:
        """Run MyPy type checking."""
        cmd = [
            "mypy",
            "src/app/",
            "--ignore-missing-imports",
            "--no-error-summary",
            "--show-error-codes",
        ]

        return self.run_command(cmd, "MyPy Type Checking")

    def validate_bandit(self) -> ValidationResult:
        """Run Bandit security scanning."""
        cmd = [
            "bandit",
            "-r",
            "src/",
            "scripts/",
            "--severity-level",
            "medium",
            "--confidence-level",
            "medium",
            "-f",
            "screen",
        ]

        return self.run_command(cmd, "Bandit Security Scan")

    def validate_tests(self) -> ValidationResult:
        """Run pytest test suite."""
        if self.fast:
            # Fast mode: only run quick unit tests
            cmd = [
                "pytest",
                "tests/test_ai_systems.py",
                "tests/test_user_manager.py",
                "-v",
                "--tb=short",
            ]
            name = "Pytest (Fast - Core Tests Only)"
        else:
            # Full test suite
            cmd = [
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--maxfail=10",
                "-x",
            ]
            name = "Pytest (Full Test Suite)"

        return self.run_command(cmd, name, timeout=600)

    def validate_pytest_markers(self) -> ValidationResult:
        """Validate pytest configuration and markers."""
        cmd = ["pytest", "--collect-only", "-q"]
        return self.run_command(cmd, "Pytest Collection Check")

    def print_summary(self):
        """Print validation summary."""
        total_duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        passed_count = sum(1 for r in self.results if r.passed)
        failed_count = len(self.results) - passed_count
        total_errors = sum(r.errors for r in self.results)
        total_warnings = sum(r.warnings for r in self.results)

        print(f"\nTotal Checks: {len(self.results)}")
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"🔴 Total Errors: {total_errors}")
        print(f"⚠️  Total Warnings: {total_warnings}")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")

        print("\nDetailed Results:")
        print("-" * 70)

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"\n{status} - {result.name}")
            print(f"  Duration: {result.duration:.2f}s")
            print(f"  Errors: {result.errors}, Warnings: {result.warnings}")
            if result.fixable > 0:
                print(f"  Fixable: {result.fixable} (use --fix)")

        print("\n" + "=" * 70)

        if failed_count == 0:
            print("🎉 ALL VALIDATIONS PASSED!")
        else:
            print(f"⚠️  {failed_count} VALIDATION(S) FAILED")

        print("=" * 70 + "\n")

    def generate_report(self):
        """Generate JSON validation report."""
        if not self.report:
            return

        report_data = {
            "timestamp": self.start_time.isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "summary": {
                "total_checks": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "total_errors": sum(r.errors for r in self.results),
                "total_warnings": sum(r.warnings for r in self.results),
            },
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "errors": r.errors,
                    "warnings": r.warnings,
                    "duration": r.duration,
                    "fixable": r.fixable,
                }
                for r in self.results
            ],
        }

        report_path = Path("validation_report.json")
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📊 Validation report saved to: {report_path}")

    def run_all(self) -> int:
        """Run all validation checks and return exit code."""
        print(f"\n🚀 Starting Comprehensive Code Validation")
        print(f"Mode: {'Fix' if self.fix else 'Check'}")
        print(f"Speed: {'Fast' if self.fast else 'Full'}")
        print(f"Report: {'Yes' if self.report else 'No'}\n")

        # Run all validation checks
        self.results.append(self.validate_ruff())
        self.results.append(self.validate_black())
        self.results.append(self.validate_mypy())
        self.results.append(self.validate_bandit())
        self.results.append(self.validate_pytest_markers())
        self.results.append(self.validate_tests())

        # Print summary
        self.print_summary()

        # Generate report if requested
        self.generate_report()

        # Return exit code (0 if all passed, 1 if any failed)
        return 0 if all(r.passed for r in self.results) else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive code validation for Project-AI"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix issues where possible"
    )
    parser.add_argument("--fast", action="store_true", help="Run fast checks only")
    parser.add_argument(
        "--report", action="store_true", help="Generate JSON validation report"
    )

    args = parser.parse_args()

    validator = CodeValidator(fix=args.fix, fast=args.fast, report=args.report)
    exit_code = validator.run_all()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
