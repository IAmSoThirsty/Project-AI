"""
RepairCrew — self-healing diagnostics and repair for Project-AI's Miniature Office.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class IssueSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Issue:
    issue_id: str
    category: str
    severity: IssueSeverity
    file_path: str
    line: int
    description: str
    suggested_fix: str = ""


@dataclass
class DiagnosticReport:
    report_id: str
    files_scanned: int
    issues: list[Issue] = field(default_factory=list)


@dataclass
class Patch:
    issue_id: str
    description: str
    confidence: float


@dataclass
class RepairReport:
    repair_id: str
    diagnostic_report_id: str
    patches: list[Patch] = field(default_factory=list)


_BARE_EXCEPT = re.compile(r"^\s*except\s*:\s*$", re.MULTILINE)
_HARDCODED_SECRET = re.compile(
    r'(?i)\b(password|secret|passwd|api_key|token|auth_key)\s*=\s*["\'][^"\']{3,}["\']'
)
_TODO = re.compile(r"#\s*TODO\b", re.IGNORECASE)


def _scan_file(fpath: Path) -> list[Issue]:
    issues: list[Issue] = []
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return issues

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        if _BARE_EXCEPT.match(line):
            issues.append(Issue(
                issue_id=str(uuid.uuid4()),
                category="style",
                severity=IssueSeverity.WARNING,
                file_path=str(fpath),
                line=lineno,
                description="Bare except clause catches all exceptions",
                suggested_fix="Replace `except:` with `except Exception:`",
            ))
        if _HARDCODED_SECRET.search(line):
            issues.append(Issue(
                issue_id=str(uuid.uuid4()),
                category="security",
                severity=IssueSeverity.CRITICAL,
                file_path=str(fpath),
                line=lineno,
                description="Hardcoded secret detected in source",
                suggested_fix="Move secret to environment variable or secrets manager",
            ))
        if _TODO.search(line):
            issues.append(Issue(
                issue_id=str(uuid.uuid4()),
                category="technical_debt",
                severity=IssueSeverity.INFO,
                file_path=str(fpath),
                line=lineno,
                description="TODO comment found",
                suggested_fix="",
            ))
    return issues


class RepairCrew:
    def __init__(self) -> None:
        self._last_report: DiagnosticReport | None = None

    def diagnose(self, path: str) -> DiagnosticReport:
        root = Path(path)
        py_files = list(root.rglob("*.py")) if root.is_dir() else [root]
        all_issues: list[Issue] = []
        for fpath in py_files:
            all_issues.extend(_scan_file(fpath))
        report = DiagnosticReport(
            report_id=f"diag_{uuid.uuid4().hex[:8]}",
            files_scanned=len(py_files),
            issues=all_issues,
        )
        self._last_report = report
        return report

    def repair(self, report: DiagnosticReport) -> RepairReport:
        patches: list[Patch] = []
        for issue in report.issues:
            if issue.suggested_fix:
                confidence = 0.9 if issue.severity == IssueSeverity.CRITICAL else 0.7
                patches.append(Patch(
                    issue_id=issue.issue_id,
                    description=issue.suggested_fix,
                    confidence=confidence,
                ))
        return RepairReport(
            repair_id=f"repair_{uuid.uuid4().hex[:8]}",
            diagnostic_report_id=report.report_id,
            patches=patches,
        )

    def get_health_report(self) -> dict:
        if self._last_report is None:
            return {
                "last_diagnosis": {
                    "report_id": None,
                    "summary": "No scan run yet",
                }
            }
        return {
            "last_diagnosis": {
                "report_id": self._last_report.report_id,
                "files_scanned": self._last_report.files_scanned,
                "issue_count": len(self._last_report.issues),
            }
        }
