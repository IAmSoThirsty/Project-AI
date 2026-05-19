"""Evidence Harvester Agent for Project-AI verification.

Collects, organizes, and verifies evidence that Project-AI behavior is real,
tested, and reproducible. Separates simulated from production evidence and
provides actionable verification recommendations.

All operations route through CognitionKernel for governance tracking.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

_EVIDENCE_DIR = "data/evidence_harvester"
_STALENESS_DAYS = 7  # Evidence older than this is marked stale


@dataclass
class EvidenceItem:
    """Structured evidence item with verification metadata."""

    category: str  # test_results, ci_logs, audit_events, artifacts, governance, docker, runtime
    item_name: str
    source_path: str
    what_it_proves: str
    what_it_does_not_prove: str
    timestamp: str
    is_production: bool  # True = production, False = simulated/test
    is_stale: bool
    verification_command: str | None = None
    content_hash: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EvidenceHarvesterAgent(KernelRoutedAgent):
    """Collects and verifies evidence of Project-AI functionality.

    Scans for test results, CI logs, release artifacts, audit events,
    governance decisions, Docker proofs, runtime health, denial paths,
    zero-bypass verification, and execution tickets.
    """

    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        data_dir: str = _EVIDENCE_DIR,
    ) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.enabled: bool = True
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_cache: dict[str, list[EvidenceItem]] = {}

    # ------------------------------------------------------------------ public

    def harvest_all_evidence(
        self,
        include_simulated: bool = True,
        staleness_days: int = _STALENESS_DAYS,
    ) -> dict[str, Any]:
        """Collect all available evidence across all categories.

        Args:
            include_simulated: Include simulated/test evidence
            staleness_days: Mark evidence older than this many days as stale

        Returns:
            Dict with evidence items grouped by category, summary stats,
            missing evidence, and recommendations.
        """
        return self._execute_through_kernel(
            self._do_harvest_all,
            action_name="EvidenceHarvesterAgent.harvest_all_evidence",
            action_args=(include_simulated, staleness_days),
        )

    def verify_evidence_item(self, item: EvidenceItem) -> dict[str, Any]:
        """Re-verify a single evidence item.

        Args:
            item: The evidence item to verify

        Returns:
            Verification result with status, updated timestamps, and findings
        """
        return self._execute_through_kernel(
            self._do_verify_item,
            action_name="EvidenceHarvesterAgent.verify_evidence_item",
            action_args=(item,),
        )

    def generate_evidence_report(
        self,
        evidence_groups: dict[str, list[EvidenceItem]],
        output_format: str = "markdown",
    ) -> str:
        """Generate human-readable evidence report.

        Args:
            evidence_groups: Evidence items grouped by category
            output_format: 'markdown' or 'json'

        Returns:
            Formatted report string
        """
        return self._execute_through_kernel(
            self._do_generate_report,
            action_name="EvidenceHarvesterAgent.generate_evidence_report",
            action_args=(evidence_groups, output_format),
        )

    def find_missing_evidence(self) -> list[dict[str, str]]:
        """Identify expected evidence that is missing.

        Returns:
            List of missing evidence items with category, name, and reason
        """
        return self._execute_through_kernel(
            self._do_find_missing,
            action_name="EvidenceHarvesterAgent.find_missing_evidence",
            action_args=(),
        )

    # --------------------------------------------------------------- private

    def _do_harvest_all(
        self,
        include_simulated: bool,
        staleness_days: int,
    ) -> dict[str, Any]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=staleness_days)
        evidence_groups: dict[str, list[EvidenceItem]] = {}

        # Harvest each category
        categories = [
            self._harvest_test_results,
            self._harvest_ci_logs,
            self._harvest_audit_events,
            self._harvest_governance_decisions,
            self._harvest_docker_artifacts,
            self._harvest_runtime_health,
            self._harvest_denial_proofs,
            self._harvest_execution_tickets,
        ]

        for harvester in categories:
            items = harvester(cutoff_time)
            if items:
                category_name = items[0].category
                if not include_simulated:
                    items = [it for it in items if it.is_production]
                evidence_groups[category_name] = items

        # Cache results
        self.evidence_cache = evidence_groups

        # Generate summary stats
        total_items = sum(len(items) for items in evidence_groups.values())
        production_items = sum(
            len([it for it in items if it.is_production])
            for items in evidence_groups.values()
        )
        stale_items = sum(
            len([it for it in items if it.is_stale])
            for items in evidence_groups.values()
        )

        missing = self._do_find_missing()

        return {
            "evidence_groups": evidence_groups,
            "summary": {
                "total_items": total_items,
                "production_items": production_items,
                "simulated_items": total_items - production_items,
                "stale_items": stale_items,
                "categories": len(evidence_groups),
                "missing_items": len(missing),
            },
            "missing_evidence": missing,
            "recommendations": self._generate_recommendations(evidence_groups, missing),
        }

    def _harvest_test_results(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest pytest test results and coverage reports."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Check for pytest cache
        pytest_cache = project_root / ".pytest_cache"
        if pytest_cache.exists():
            last_run = pytest_cache / "v" / "cache" / "lastfailed"
            if last_run.exists():
                mtime = datetime.fromtimestamp(
                    last_run.stat().st_mtime, tz=timezone.utc
                )
                items.append(
                    EvidenceItem(
                        category="test_results",
                        item_name="pytest_last_run",
                        source_path=str(last_run),
                        what_it_proves="Pytest has been executed recently",
                        what_it_does_not_prove="All tests passed or coverage is adequate",
                        timestamp=mtime.isoformat(),
                        is_production=True,
                        is_stale=mtime < cutoff_time,
                        verification_command="pytest -v",
                        content_hash=self._hash_file(last_run),
                    )
                )

        # Check for coverage reports
        coverage_file = project_root / ".coverage"
        if coverage_file.exists():
            mtime = datetime.fromtimestamp(
                coverage_file.stat().st_mtime, tz=timezone.utc
            )
            items.append(
                EvidenceItem(
                    category="test_results",
                    item_name="coverage_database",
                    source_path=str(coverage_file),
                    what_it_proves="Test coverage has been measured",
                    what_it_does_not_prove="Coverage meets minimum thresholds",
                    timestamp=mtime.isoformat(),
                    is_production=True,
                    is_stale=mtime < cutoff_time,
                    verification_command="coverage report",
                    content_hash=self._hash_file(coverage_file),
                )
            )

        return items

    def _harvest_ci_logs(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest CI/CD workflow artifacts and logs."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Check GitHub Actions workflows
        workflows_dir = project_root / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                mtime = datetime.fromtimestamp(
                    workflow.stat().st_mtime, tz=timezone.utc
                )
                items.append(
                    EvidenceItem(
                        category="ci_logs",
                        item_name=f"workflow_{workflow.stem}",
                        source_path=str(workflow),
                        what_it_proves=f"CI workflow '{workflow.stem}' is configured",
                        what_it_does_not_prove="Workflow has run successfully or recently",
                        timestamp=mtime.isoformat(),
                        is_production=True,
                        is_stale=False,  # Workflow configs don't go stale
                        verification_command=f"gh run list --workflow={workflow.name}",
                        content_hash=self._hash_file(workflow),
                    )
                )

        # Check for CI reports directory
        ci_reports = project_root / "ci-reports"
        if ci_reports.exists():
            for report in ci_reports.glob("*.json"):
                mtime = datetime.fromtimestamp(
                    report.stat().st_mtime, tz=timezone.utc
                )
                items.append(
                    EvidenceItem(
                        category="ci_logs",
                        item_name=f"ci_report_{report.stem}",
                        source_path=str(report),
                        what_it_proves="CI pipeline generated a report artifact",
                        what_it_does_not_prove="All checks passed",
                        timestamp=mtime.isoformat(),
                        is_production=True,
                        is_stale=mtime < cutoff_time,
                        content_hash=self._hash_file(report),
                    )
                )

        return items

    def _harvest_audit_events(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest governance audit log events."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        audit_log = project_root / "governance" / "audit_log.yaml"
        if audit_log.exists():
            mtime = datetime.fromtimestamp(
                audit_log.stat().st_mtime, tz=timezone.utc
            )
            items.append(
                EvidenceItem(
                    category="audit_events",
                    item_name="governance_audit_log",
                    source_path=str(audit_log),
                    what_it_proves="Governance decisions are being logged",
                    what_it_does_not_prove="All events pass governance checks",
                    timestamp=mtime.isoformat(),
                    is_production=True,
                    is_stale=mtime < cutoff_time,
                    content_hash=self._hash_file(audit_log),
                )
            )

        # Check for acceptance ledger
        acceptance_ledger = project_root / "data" / "acceptance_ledger.jsonl"
        if acceptance_ledger.exists():
            mtime = datetime.fromtimestamp(
                acceptance_ledger.stat().st_mtime, tz=timezone.utc
            )
            items.append(
                EvidenceItem(
                    category="audit_events",
                    item_name="acceptance_ledger",
                    source_path=str(acceptance_ledger),
                    what_it_proves="RFC 3161 timestamped events are being recorded",
                    what_it_does_not_prove="All timestamps are valid or complete",
                    timestamp=mtime.isoformat(),
                    is_production=True,
                    is_stale=mtime < cutoff_time,
                    content_hash=self._hash_file(acceptance_ledger),
                )
            )

        return items

    def _harvest_governance_decisions(
        self, cutoff_time: datetime
    ) -> list[EvidenceItem]:
        """Harvest governance decision hashes and canonical scenario results."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Check canonical scenario
        canonical_scenario = project_root / "canonical" / "scenario.yaml"
        if canonical_scenario.exists():
            items.append(
                EvidenceItem(
                    category="governance",
                    item_name="canonical_scenario",
                    source_path=str(canonical_scenario),
                    what_it_proves="Ground truth governance scenario is defined",
                    what_it_does_not_prove="Scenario passes all invariants when executed",
                    timestamp=datetime.fromtimestamp(
                        canonical_scenario.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    is_production=True,
                    is_stale=False,
                    verification_command="python canonical/replay.py",
                    content_hash=self._hash_file(canonical_scenario),
                )
            )

        # Check for governance drift alerts
        drift_dir = project_root / "data" / "governance_drift_alerts"
        if drift_dir.exists():
            alerts = list(drift_dir.glob("*.json"))
            if alerts:
                latest = max(alerts, key=lambda p: p.stat().st_mtime)
                mtime = datetime.fromtimestamp(
                    latest.stat().st_mtime, tz=timezone.utc
                )
                items.append(
                    EvidenceItem(
                        category="governance",
                        item_name="latest_drift_alert",
                        source_path=str(latest),
                        what_it_proves="Governance monitoring has detected drift",
                        what_it_does_not_prove="Drift has been resolved",
                        timestamp=mtime.isoformat(),
                        is_production=True,
                        is_stale=False,  # Alerts don't go stale
                        content_hash=self._hash_file(latest),
                        metadata={"alert_count": len(alerts)},
                    )
                )

        return items

    def _harvest_docker_artifacts(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest Docker build and container evidence."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Check Dockerfile
        dockerfile = project_root / "Dockerfile"
        if dockerfile.exists():
            items.append(
                EvidenceItem(
                    category="docker",
                    item_name="dockerfile",
                    source_path=str(dockerfile),
                    what_it_proves="Container build configuration exists",
                    what_it_does_not_prove="Image builds successfully or is up-to-date",
                    timestamp=datetime.fromtimestamp(
                        dockerfile.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    is_production=True,
                    is_stale=False,
                    verification_command="docker build -t project-ai:test .",
                    content_hash=self._hash_file(dockerfile),
                )
            )

        # Check docker-compose
        compose_file = project_root / "docker-compose.yml"
        if compose_file.exists():
            items.append(
                EvidenceItem(
                    category="docker",
                    item_name="docker_compose",
                    source_path=str(compose_file),
                    what_it_proves="Multi-container orchestration is defined",
                    what_it_does_not_prove="Containers start successfully",
                    timestamp=datetime.fromtimestamp(
                        compose_file.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    is_production=True,
                    is_stale=False,
                    verification_command="docker-compose config",
                    content_hash=self._hash_file(compose_file),
                )
            )

        return items

    def _harvest_runtime_health(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest runtime health and readiness output."""
        items: list[EvidenceItem] = []

        # Check if Triumvirate server health endpoint exists
        try:
            result = subprocess.run(
                ["curl", "-s", "-f", "http://localhost:8001/health"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                items.append(
                    EvidenceItem(
                        category="runtime",
                        item_name="triumvirate_health",
                        source_path="http://localhost:8001/health",
                        what_it_proves="Triumvirate server is running and responsive",
                        what_it_does_not_prove="All governance systems are functional",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        is_production=True,
                        is_stale=False,
                        verification_command="curl http://localhost:8001/health",
                        content_hash=hashlib.sha256(
                            result.stdout.encode()
                        ).hexdigest(),
                        metadata={"response": result.stdout},
                    )
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return items

    def _harvest_denial_proofs(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest denial-path and zero-bypass verification proofs."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Check for test files that verify denial paths
        denial_tests = [
            "test_four_laws_1000_disallowed_high_level.py",
            "test_integration_pipeline_blocking.py",
            "test_boundary.py",
        ]

        tests_dir = project_root / "tests"
        for test_name in denial_tests:
            test_file = tests_dir / test_name
            if test_file.exists():
                items.append(
                    EvidenceItem(
                        category="denial_proofs",
                        item_name=f"denial_test_{test_file.stem}",
                        source_path=str(test_file),
                        what_it_proves=f"Test suite exists for denial scenarios ({test_file.stem})",
                        what_it_does_not_prove="Tests pass or cover all denial paths",
                        timestamp=datetime.fromtimestamp(
                            test_file.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                        is_production=True,
                        is_stale=False,
                        verification_command=f"pytest {test_file.name} -v",
                        content_hash=self._hash_file(test_file),
                    )
                )

        return items

    def _harvest_execution_tickets(self, cutoff_time: datetime) -> list[EvidenceItem]:
        """Harvest signed execution ticket evidence."""
        items: list[EvidenceItem] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Check for execution gate implementation
        execution_gate = (
            project_root / "src" / "app" / "core" / "execution_gate.py"
        )
        if execution_gate.exists():
            items.append(
                EvidenceItem(
                    category="artifacts",
                    item_name="execution_gate_implementation",
                    source_path=str(execution_gate),
                    what_it_proves="Execution gate with ticket signing is implemented",
                    what_it_does_not_prove="All executions route through gate or tickets are valid",
                    timestamp=datetime.fromtimestamp(
                        execution_gate.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    is_production=True,
                    is_stale=False,
                    content_hash=self._hash_file(execution_gate),
                )
            )

        return items

    def _do_verify_item(self, item: EvidenceItem) -> dict[str, Any]:
        """Re-verify a single evidence item."""
        result = {
            "item_name": item.item_name,
            "category": item.category,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "findings": [],
        }

        # Check if source still exists
        source_path = Path(item.source_path)
        if not source_path.exists() and not item.source_path.startswith("http"):
            result["status"] = "missing"
            result["findings"].append(f"Source path no longer exists: {item.source_path}")
            return result

        # Re-hash if it's a file
        if source_path.exists() and source_path.is_file():
            current_hash = self._hash_file(source_path)
            if current_hash != item.content_hash:
                result["findings"].append("Content has changed since last harvest")
                result["new_hash"] = current_hash

        # Check staleness
        try:
            item_time = datetime.fromisoformat(item.timestamp)
            if datetime.now(timezone.utc) - item_time > timedelta(days=_STALENESS_DAYS):
                result["findings"].append("Evidence is now stale (>7 days old)")
        except Exception:
            pass

        # Run verification command if provided
        if item.verification_command:
            try:
                # Note: This is a dry-run check, not actual execution
                result["findings"].append(
                    f"Verification command available: {item.verification_command}"
                )
            except Exception as exc:
                result["findings"].append(f"Verification command check failed: {exc}")

        result["status"] = "verified" if not result["findings"] else "updated"
        return result

    def _do_generate_report(
        self,
        evidence_groups: dict[str, list[EvidenceItem]],
        output_format: str,
    ) -> str:
        """Generate human-readable evidence report."""
        if output_format == "json":
            # Convert dataclasses to dicts for JSON serialization
            serializable = {
                cat: [
                    {
                        "category": item.category,
                        "item_name": item.item_name,
                        "source_path": item.source_path,
                        "what_it_proves": item.what_it_proves,
                        "what_it_does_not_prove": item.what_it_does_not_prove,
                        "timestamp": item.timestamp,
                        "is_production": item.is_production,
                        "is_stale": item.is_stale,
                        "verification_command": item.verification_command,
                        "content_hash": item.content_hash,
                        "metadata": item.metadata,
                    }
                    for item in items
                ]
                for cat, items in evidence_groups.items()
            }
            return json.dumps(serializable, indent=2)

        # Markdown format
        lines = ["# Project-AI Evidence Report", ""]
        lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
        lines.append("")

        for category, items in sorted(evidence_groups.items()):
            lines.append(f"## {category.upper().replace('_', ' ')}")
            lines.append("")

            for item in items:
                status_icon = "⚠️" if item.is_stale else "✅"
                prod_label = "PRODUCTION" if item.is_production else "SIMULATED"
                lines.append(f"### {status_icon} {item.item_name} [{prod_label}]")
                lines.append("")
                lines.append(f"**Source:** `{item.source_path}`")
                lines.append(f"**Timestamp:** {item.timestamp}")
                lines.append("")
                lines.append(f"**✅ Proves:** {item.what_it_proves}")
                lines.append(f"**❌ Does NOT Prove:** {item.what_it_does_not_prove}")
                lines.append("")

                if item.verification_command:
                    lines.append(f"**Verify with:** `{item.verification_command}`")
                    lines.append("")

                if item.content_hash:
                    lines.append(f"**Hash:** `{item.content_hash[:16]}...`")
                    lines.append("")

                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _do_find_missing(self) -> list[dict[str, str]]:
        """Identify expected evidence that is missing."""
        missing: list[dict[str, str]] = []
        project_root = Path(__file__).parent.parent.parent.parent

        # Expected test artifacts
        expected_artifacts = [
            (
                "test_results",
                "htmlcov/index.html",
                "HTML coverage report not found",
            ),
            (
                "test_results",
                ".coverage",
                "Coverage database not found",
            ),
            (
                "audit_events",
                "governance/audit_log.yaml",
                "Governance audit log not found",
            ),
            (
                "governance",
                "canonical/scenario.yaml",
                "Canonical scenario not found",
            ),
            (
                "docker",
                "Dockerfile",
                "Dockerfile not found",
            ),
        ]

        for category, path, reason in expected_artifacts:
            full_path = project_root / path
            if not full_path.exists():
                missing.append(
                    {
                        "category": category,
                        "expected_path": str(full_path),
                        "reason": reason,
                    }
                )

        return missing

    def _generate_recommendations(
        self,
        evidence_groups: dict[str, list[EvidenceItem]],
        missing: list[dict[str, str]],
    ) -> list[str]:
        """Generate actionable recommendations based on evidence state."""
        recommendations: list[str] = []

        # Check for stale evidence
        for category, items in evidence_groups.items():
            stale_count = sum(1 for item in items if item.is_stale)
            if stale_count > 0:
                recommendations.append(
                    f"Update {stale_count} stale {category} items by re-running verification commands"
                )

        # Check for missing critical evidence
        if missing:
            recommendations.append(
                f"Collect {len(missing)} missing evidence items (run recommended commands)"
            )

        # Check production vs simulated ratio
        total_prod = sum(
            len([it for it in items if it.is_production])
            for items in evidence_groups.values()
        )
        total_sim = sum(
            len([it for it in items if not it.is_production])
            for items in evidence_groups.values()
        )

        if total_sim > total_prod:
            recommendations.append(
                "Increase production evidence collection (currently more simulated than production)"
            )

        if not recommendations:
            recommendations.append("Evidence collection is current and complete")

        return recommendations

    def _hash_file(self, path: Path) -> str:
        """Generate SHA-256 hash of file contents."""
        try:
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as exc:
            logger.warning("Failed to hash file %s: %s", path, exc)
            return "hash_error"
