"""
Lint Checker - Automated File Errors, Lint, Markdown, and Syntax Checks

This module provides comprehensive automated checking for:
- Python linting (ruff, flake8, mypy)
- Markdown linting
- YAML/JSON syntax validation
- File encoding and line ending checks
- Security scanning (bandit)
- Best-of-breed standards compliance

Author: Project-AI Team
Date: 2026-02-08
"""

import json
import logging
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class LintIssue:
    """Represents a linting issue."""

    file: str
    line: int
    column: int
    severity: str  # error, warning, info
    rule: str
    message: str
    source: str  # ruff, flake8, mypy, markdown, yaml, etc.
    fixable: bool = False


@dataclass
class LintReport:
    """Report for a single file's linting results."""

    file: str
    tool: str
    passed: bool
    issues: list[LintIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class LintChecker:
    """
    Comprehensive lint checker for all file types.

    Performs automated checking using best-of-breed tools and
    Project-AI custom requirements.
    """

    def __init__(self, repo_root: str | Path, file_inventory: dict[str, Any]):
        """
        Initialize the lint checker.

        Args:
            repo_root: Root directory of the repository
            file_inventory: File inventory from RepositoryInspector
        """
        self.repo_root = Path(repo_root).resolve()
        self.file_inventory = file_inventory
        self.reports: list[LintReport] = []
        self.available_tools = self._detect_available_tools()

        logger.info("Initialized LintChecker for: %s", self.repo_root)
        logger.info("Available tools: %s", ", ".join(self.available_tools))

    def check(self) -> dict[str, Any]:
        """
        Perform comprehensive linting checks.

        Returns:
            Dictionary containing all lint reports and summary
        """
        logger.info("Starting lint checks...")

        try:
            # Phase 1: Check Python files
            self._check_python_files()

            # Phase 2: Check Markdown files
            self._check_markdown_files()

            # Phase 3: Check YAML/JSON files
            self._check_config_files()

            # Phase 4: Check file encoding and line endings
            self._check_file_standards()

            # Phase 5: Run security scans
            self._run_security_scans()

            summary = self._compute_summary()

            logger.info(
                "Lint checks complete: %d files checked, %d issues found",
                len(self.reports),
                summary["total_issues"],
            )

            return {
                "reports": [asdict(r) for r in self.reports],
                "summary": summary,
            }

        except Exception as e:
            logger.exception("Lint checking failed: %s", e)
            raise

    def _detect_available_tools(self) -> list[str]:
        """Detect which linting tools are available."""
        tools = []

        tool_commands = {
            "ruff": "ruff",
            "flake8": "flake8",
            "mypy": "mypy",
            "bandit": "bandit",
            "yamllint": "yamllint",
        }

        for tool_name, command in tool_commands.items():
            if shutil.which(command):
                tools.append(tool_name)

        return tools

    def _check_python_files(self) -> None:
        """Check Python files with available linters."""
        logger.info("Checking Python files...")

        python_files = [
            info
            for info in self.file_inventory.get("files", {}).values()
            if info.get("file_type") in ["python_module", "python_test"]
        ]

        for file_info in python_files:
            file_path = Path(file_info["path"])

            # Run ruff if available
            if "ruff" in self.available_tools:
                self._run_ruff(file_path)

            # Run flake8 if available (and ruff not available)
            if "flake8" in self.available_tools and "ruff" not in self.available_tools:
                self._run_flake8(file_path)

            # Run mypy if available
            if "mypy" in self.available_tools:
                self._run_mypy(file_path)

    def _run_ruff(self, file_path: Path) -> None:
        """Run ruff linter on a Python file."""
        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            issues = []
            if result.stdout:
                try:
                    ruff_output = json.loads(result.stdout)
                    for item in ruff_output:
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=item.get("location", {}).get("row", 0),
                                column=item.get("location", {}).get("column", 0),
                                severity="error" if item.get("fix") else "warning",
                                rule=item.get("code", ""),
                                message=item.get("message", ""),
                                source="ruff",
                                fixable=bool(item.get("fix")),
                            )
                        )
                except json.JSONDecodeError:
                    logger.debug("Failed to parse ruff output for %s", file_path)

            report = LintReport(
                file=str(file_path),
                tool="ruff",
                passed=len(issues) == 0,
                issues=issues,
            )
            self.reports.append(report)

        except subprocess.TimeoutExpired:
            logger.warning("Ruff check timed out for %s", file_path)
        except Exception as e:
            logger.debug("Error running ruff on %s: %s", file_path, e)

    def _run_flake8(self, file_path: Path) -> None:
        """Run flake8 linter on a Python file."""
        try:
            result = subprocess.run(
                ["flake8", "--format=json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            issues = []
            # Parse flake8 output (simplified)
            for line in result.stdout.splitlines():
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 4:
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=int(parts[1]) if parts[1].isdigit() else 0,
                                column=int(parts[2]) if parts[2].isdigit() else 0,
                                severity="warning",
                                rule="",
                                message=parts[3].strip() if len(parts) > 3 else "",
                                source="flake8",
                                fixable=False,
                            )
                        )

            report = LintReport(
                file=str(file_path),
                tool="flake8",
                passed=len(issues) == 0,
                issues=issues,
            )
            self.reports.append(report)

        except subprocess.TimeoutExpired:
            logger.warning("Flake8 check timed out for %s", file_path)
        except Exception as e:
            logger.debug("Error running flake8 on %s: %s", file_path, e)

    def _run_mypy(self, file_path: Path) -> None:
        """Run mypy type checker on a Python file."""
        try:
            result = subprocess.run(
                ["mypy", "--show-column-numbers", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            issues = []
            # Parse mypy output
            for line in result.stdout.splitlines():
                if ":" in line and ("error:" in line or "note:" in line):
                    match = re.match(r"(.+):(\d+):(\d+):\s+(error|note):\s+(.+)", line)
                    if match:
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=int(match.group(2)),
                                column=int(match.group(3)),
                                severity=match.group(4),
                                rule="type-check",
                                message=match.group(5),
                                source="mypy",
                                fixable=False,
                            )
                        )

            report = LintReport(
                file=str(file_path),
                tool="mypy",
                passed=len(issues) == 0,
                issues=issues,
            )
            self.reports.append(report)

        except subprocess.TimeoutExpired:
            logger.warning("Mypy check timed out for %s", file_path)
        except Exception as e:
            logger.debug("Error running mypy on %s: %s", file_path, e)

    def _check_markdown_files(self) -> None:
        """Check Markdown files for common issues."""
        logger.info("Checking Markdown files...")

        markdown_files = [
            info
            for info in self.file_inventory.get("files", {}).values()
            if info.get("file_type") == "markdown"
        ]

        for file_info in markdown_files:
            file_path = Path(file_info["path"])
            issues = []

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Check for common issues
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    # Check for trailing whitespace
                    if line.endswith(" ") and line.strip():
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=i,
                                column=len(line),
                                severity="info",
                                rule="MD009",
                                message="Trailing whitespace",
                                source="markdown",
                                fixable=True,
                            )
                        )

                    # Check for hard tabs
                    if "\t" in line:
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=i,
                                column=line.index("\t"),
                                severity="warning",
                                rule="MD010",
                                message="Hard tabs found",
                                source="markdown",
                                fixable=True,
                            )
                        )

            except Exception as e:
                logger.debug("Error checking markdown file %s: %s", file_path, e)

            report = LintReport(
                file=str(file_path),
                tool="markdown",
                passed=len(issues) == 0,
                issues=issues,
            )
            self.reports.append(report)

    def _check_config_files(self) -> None:
        """Check YAML and JSON configuration files."""
        logger.info("Checking configuration files...")

        config_files = [
            info
            for info in self.file_inventory.get("files", {}).values()
            if info.get("file_type") in ["yaml", "json"]
        ]

        for file_info in config_files:
            file_path = Path(file_info["path"])
            issues = []

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if file_info["file_type"] == "yaml":
                    # Validate YAML
                    try:
                        yaml.safe_load(content)
                    except yaml.YAMLError as e:
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=(
                                    getattr(e, "problem_mark", None).line
                                    if hasattr(e, "problem_mark")
                                    else 0
                                ),
                                column=0,
                                severity="error",
                                rule="yaml-syntax",
                                message=str(e),
                                source="yaml",
                                fixable=False,
                            )
                        )
                elif file_info["file_type"] == "json":
                    # Validate JSON
                    try:
                        json.loads(content)
                    except json.JSONDecodeError as e:
                        issues.append(
                            LintIssue(
                                file=str(file_path),
                                line=e.lineno,
                                column=e.colno,
                                severity="error",
                                rule="json-syntax",
                                message=e.msg,
                                source="json",
                                fixable=False,
                            )
                        )

            except Exception as e:
                logger.debug("Error checking config file %s: %s", file_path, e)

            report = LintReport(
                file=str(file_path),
                tool=file_info["file_type"],
                passed=len(issues) == 0,
                issues=issues,
            )
            self.reports.append(report)

    def _check_file_standards(self) -> None:
        """Check file encoding and line ending standards."""
        logger.info("Checking file standards...")

        for file_info in self.file_inventory.get("files", {}).values():
            file_path = Path(file_info["path"])
            issues = []

            try:
                # Check encoding (should be UTF-8)
                with open(file_path, "rb") as f:
                    content = f.read()

                try:
                    content.decode("utf-8")
                except UnicodeDecodeError:
                    issues.append(
                        LintIssue(
                            file=str(file_path),
                            line=0,
                            column=0,
                            severity="warning",
                            rule="encoding",
                            message="File is not UTF-8 encoded",
                            source="encoding",
                            fixable=False,
                        )
                    )

                # Check for mixed line endings
                text = content.decode("utf-8", errors="ignore")
                has_crlf = "\r\n" in text
                has_lf = "\n" in text.replace("\r\n", "")

                if has_crlf and has_lf:
                    issues.append(
                        LintIssue(
                            file=str(file_path),
                            line=0,
                            column=0,
                            severity="info",
                            rule="line-endings",
                            message="Mixed line endings (CRLF and LF)",
                            source="encoding",
                            fixable=True,
                        )
                    )

            except Exception as e:
                logger.debug("Error checking file standards for %s: %s", file_path, e)

            if issues:
                report = LintReport(
                    file=str(file_path),
                    tool="encoding",
                    passed=False,
                    issues=issues,
                )
                self.reports.append(report)

    def _run_security_scans(self) -> None:
        """Run security scanning tools."""
        logger.info("Running security scans...")

        if "bandit" in self.available_tools:
            self._run_bandit()

    def _run_bandit(self) -> None:
        """Run bandit security scanner on Python files."""
        try:
            python_dirs = ["src", "tests", "api", "scripts"]
            existing_dirs = [d for d in python_dirs if (self.repo_root / d).exists()]

            if not existing_dirs:
                return

            result = subprocess.run(
                ["bandit", "-r", "-f", "json"] + existing_dirs,
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=60,
            )

            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    for item in bandit_output.get("results", []):
                        issue = LintIssue(
                            file=item.get("filename", ""),
                            line=item.get("line_number", 0),
                            column=0,
                            severity=item.get("issue_severity", "").lower(),
                            rule=item.get("test_id", ""),
                            message=item.get("issue_text", ""),
                            source="bandit",
                            fixable=False,
                        )

                        # Find or create report for this file
                        file_report = next(
                            (
                                r
                                for r in self.reports
                                if r.file == issue.file and r.tool == "bandit"
                            ),
                            None,
                        )

                        if file_report:
                            file_report.issues.append(issue)
                            file_report.passed = False
                        else:
                            self.reports.append(
                                LintReport(
                                    file=issue.file,
                                    tool="bandit",
                                    passed=False,
                                    issues=[issue],
                                )
                            )

                except json.JSONDecodeError:
                    logger.debug("Failed to parse bandit output")

        except subprocess.TimeoutExpired:
            logger.warning("Bandit scan timed out")
        except Exception as e:
            logger.debug("Error running bandit: %s", e)

    def _compute_summary(self) -> dict[str, Any]:
        """Compute summary statistics from lint reports."""
        total_files = len({r.file for r in self.reports})
        total_issues = sum(len(r.issues) for r in self.reports)
        passed_files = sum(1 for r in self.reports if r.passed)

        issues_by_severity = {"error": 0, "warning": 0, "info": 0}
        issues_by_source = {}

        for report in self.reports:
            for issue in report.issues:
                issues_by_severity[issue.severity] = (
                    issues_by_severity.get(issue.severity, 0) + 1
                )
                issues_by_source[issue.source] = (
                    issues_by_source.get(issue.source, 0) + 1
                )

        fixable_issues = sum(
            len([i for i in r.issues if i.fixable]) for r in self.reports
        )

        return {
            "total_files_checked": total_files,
            "total_issues": total_issues,
            "passed_files": passed_files,
            "failed_files": total_files - passed_files,
            "issues_by_severity": issues_by_severity,
            "issues_by_source": issues_by_source,
            "fixable_issues": fixable_issues,
            "tools_used": list(self.available_tools),
        }


__all__ = ["LintChecker", "LintIssue", "LintReport"]
