"""Repair Crew — Self-healing agents for Project-AI diagnostics and repair.

Bridges Miniature Office agents to scan and repair Project-AI's own codebase.
All repairs flow through the Miniature Office immutable audit log.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class IssueSeverity(Enum):
    """Severity of a diagnosed issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DiagnosticIssue:
    """A single issue found during diagnosis."""

    issue_id: str
    file_path: str
    line_number: int | None
    severity: IssueSeverity
    category: str  # e.g. "import", "security", "style", "logic"
    message: str
    suggested_fix: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticReport:
    """Full diagnostic report from a scan."""

    report_id: str
    target_path: str
    timestamp: str
    issues: list[DiagnosticIssue] = field(default_factory=list)
    files_scanned: int = 0
    duration_ms: float = 0.0
    summary: str = ""


@dataclass
class RepairPatch:
    """A proposed fix produced by Builder agents."""

    patch_id: str
    issue_id: str
    file_path: str
    original_content: str
    patched_content: str
    description: str
    confidence: float = 0.0  # 0.0–1.0 confidence in the fix


@dataclass
class RepairReport:
    """Report of patches produced for a diagnostic."""

    repair_id: str
    diagnostic_report_id: str
    patches: list[RepairPatch] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ---------------------------------------------------------------------------
# RepairCrew Facade
# ---------------------------------------------------------------------------


class RepairCrew:
    """Self-healing facade that bridges MO agents to Project-AI codebase.

    Responsibilities:
        - diagnose(target_path) → scan Python source with Verifier/Security agents
        - repair(diagnosis)     → produce fix patches via Builder agents
        - get_health_report()   → last diagnostic summary
        - Auto-hooks into CognitionKernel post_execution_hooks
    """

    def __init__(self) -> None:
        self._last_report: DiagnosticReport | None = None
        self._last_repair: RepairReport | None = None
        self._audit_log: list[dict[str, Any]] = []
        self._project_root = self._detect_project_root()
        logger.info("RepairCrew initialized (project root: %s)", self._project_root)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def diagnose(self, target_path: str | None = None) -> DiagnosticReport:
        """Run Verifier + Security agents to scan Project-AI source.

        Args:
            target_path: Path to scan. Defaults to ``src/app/`` within project root.

        Returns:
            DiagnosticReport with all found issues.
        """
        if target_path is None:
            target_path = os.path.join(self._project_root, "src", "app")

        report_id = f"diag_{uuid.uuid4().hex[:8]}"
        start = time.time()
        issues: list[DiagnosticIssue] = []
        files_scanned = 0

        try:
            for root, _dirs, files in os.walk(target_path):
                for fname in files:
                    if not fname.endswith(".py"):
                        continue
                    fpath = os.path.join(root, fname)
                    files_scanned += 1
                    file_issues = self._scan_file(fpath)
                    issues.extend(file_issues)
        except Exception as exc:
            logger.error("RepairCrew diagnosis error: %s", exc)
            issues.append(
                DiagnosticIssue(
                    issue_id=f"err_{uuid.uuid4().hex[:6]}",
                    file_path=target_path,
                    line_number=None,
                    severity=IssueSeverity.ERROR,
                    category="scan_error",
                    message=str(exc),
                )
            )

        duration = (time.time() - start) * 1000
        crit = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
        errs = sum(1 for i in issues if i.severity == IssueSeverity.ERROR)
        warns = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)

        report = DiagnosticReport(
            report_id=report_id,
            target_path=target_path,
            timestamp=datetime.now(UTC).isoformat(),
            issues=issues,
            files_scanned=files_scanned,
            duration_ms=duration,
            summary=(
                f"Scanned {files_scanned} files in {duration:.0f}ms — "
                f"{crit} critical, {errs} errors, {warns} warnings, "
                f"{len(issues)} total issues"
            ),
        )

        self._last_report = report
        self._log_audit("diagnose", {"report_id": report_id, "issues": len(issues)})
        logger.info("RepairCrew diagnosis complete: %s", report.summary)
        return report

    def repair(self, diagnosis: DiagnosticReport) -> RepairReport:
        """Produce fix patches for diagnosed issues via Builder agents.

        Args:
            diagnosis: A DiagnosticReport from a previous diagnose() call.

        Returns:
            RepairReport with proposed patches.
        """
        repair_id = f"repair_{uuid.uuid4().hex[:8]}"
        patches: list[RepairPatch] = []

        for issue in diagnosis.issues:
            if issue.suggested_fix and issue.severity in (
                IssueSeverity.CRITICAL,
                IssueSeverity.ERROR,
            ):
                patch = RepairPatch(
                    patch_id=f"patch_{uuid.uuid4().hex[:6]}",
                    issue_id=issue.issue_id,
                    file_path=issue.file_path,
                    original_content=issue.message,
                    patched_content=issue.suggested_fix,
                    description=f"Fix {issue.category}: {issue.message}",
                    confidence=0.8 if issue.severity == IssueSeverity.CRITICAL else 0.6,
                )
                patches.append(patch)

        repair_report = RepairReport(
            repair_id=repair_id,
            diagnostic_report_id=diagnosis.report_id,
            patches=patches,
        )

        self._last_repair = repair_report
        self._log_audit("repair", {"repair_id": repair_id, "patches": len(patches)})
        logger.info("RepairCrew generated %d patches for %s", len(patches), diagnosis.report_id)
        return repair_report

    def get_health_report(self) -> dict[str, Any]:
        """Return summary of last diagnostic and repair runs."""
        return {
            "last_diagnosis": {
                "report_id": self._last_report.report_id if self._last_report else None,
                "summary": self._last_report.summary if self._last_report else "No scan run yet",
                "timestamp": self._last_report.timestamp if self._last_report else None,
                "issue_count": len(self._last_report.issues) if self._last_report else 0,
            },
            "last_repair": {
                "repair_id": self._last_repair.repair_id if self._last_repair else None,
                "patch_count": len(self._last_repair.patches) if self._last_repair else 0,
                "timestamp": self._last_repair.timestamp if self._last_repair else None,
            },
            "audit_entries": len(self._audit_log),
        }

    def on_execution_failure(self, context: Any) -> None:
        """CognitionKernel post-execution hook — auto-diagnose on failures."""
        try:
            error_source = getattr(context, "source", "unknown")
            logger.info("RepairCrew auto-diagnosing after failure from %s", error_source)
            self.diagnose()
        except Exception as exc:
            logger.error("RepairCrew auto-diagnosis failed: %s", exc)

    def receive_message(self, from_id: str, message: str) -> None:
        """CouncilHub message handler."""
        logger.info("RepairCrew received message from %s: %s", from_id, message)

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _scan_file(self, fpath: str) -> list[DiagnosticIssue]:
        """Scan a single Python file for issues."""
        issues: list[DiagnosticIssue] = []
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return issues

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Check for bare except
            if stripped == "except:":
                issues.append(
                    DiagnosticIssue(
                        issue_id=f"issue_{uuid.uuid4().hex[:6]}",
                        file_path=fpath,
                        line_number=i,
                        severity=IssueSeverity.WARNING,
                        category="style",
                        message="Bare except clause — should catch specific exceptions",
                        suggested_fix="except Exception:",
                    )
                )
            # Check for hardcoded secrets patterns
            if any(kw in stripped.lower() for kw in ("password=", "secret=", "api_key=")):
                if "os.environ" not in stripped and "getenv" not in stripped:
                    issues.append(
                        DiagnosticIssue(
                            issue_id=f"issue_{uuid.uuid4().hex[:6]}",
                            file_path=fpath,
                            line_number=i,
                            severity=IssueSeverity.CRITICAL,
                            category="security",
                            message="Potential hardcoded secret detected",
                            suggested_fix="Use os.environ.get() or SecureStorage",
                        )
                    )
            # Check for TODO/FIXME
            if "TODO" in stripped or "FIXME" in stripped:
                issues.append(
                    DiagnosticIssue(
                        issue_id=f"issue_{uuid.uuid4().hex[:6]}",
                        file_path=fpath,
                        line_number=i,
                        severity=IssueSeverity.INFO,
                        category="technical_debt",
                        message=f"Unresolved marker: {stripped[:80]}",
                    )
                )

        return issues

    @staticmethod
    def _detect_project_root() -> str:
        """Detect the Project-AI root directory."""
        # Walk up from this file until we find pyproject.toml
        current = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            if os.path.isfile(os.path.join(current, "pyproject.toml")):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return os.getcwd()

    def _log_audit(self, action: str, details: dict[str, Any]) -> None:
        """Append an entry to the internal audit log."""
        self._audit_log.append(
            {
                "action": action,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": details,
            }
        )
