"""Tests for Production Readiness Auditor Agent"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest

from app.agents.production_auditor import ProductionAuditor


class TestProductionAuditor:
    """Test suite for ProductionAuditor agent."""

    @pytest.fixture
    def temp_project(self) -> Path:
        """Create a temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create basic structure
            (project_root / "src" / "app" / "core").mkdir(parents=True)
            (project_root / "src" / "app" / "governance").mkdir(parents=True)
            (project_root / "tests").mkdir(parents=True)
            (project_root / ".github" / "workflows").mkdir(parents=True)
            (project_root / "data" / "acceptance_ledger").mkdir(parents=True)
            (project_root / "canonical").mkdir(parents=True)

            # Create minimal files
            (project_root / "src" / "app" / "main.py").write_text(
                "# Main entry point\nimport os\n", encoding="utf-8"
            )

            (project_root / ".gitignore").write_text(".env\n", encoding="utf-8")

            (project_root / "requirements.txt").write_text(
                "pytest==7.4.0\nrequests==2.31.0\n", encoding="utf-8"
            )

            (project_root / "Dockerfile").write_text(
                "FROM python:3.11\nUSER appuser\nHEALTHCHECK CMD curl /health\n",
                encoding="utf-8",
            )

            yield project_root

    @pytest.fixture
    def auditor(self, temp_project: Path) -> ProductionAuditor:
        """Create ProductionAuditor instance."""
        return ProductionAuditor(project_root=str(temp_project), kernel=None)

    def test_initialization(self, auditor: ProductionAuditor) -> None:
        """Test auditor initializes correctly."""
        assert auditor is not None
        assert auditor.project_root.exists()
        assert isinstance(auditor.blockers, list)
        assert isinstance(auditor.warnings, list)

    def test_audit_runtime_startup(self, auditor: ProductionAuditor) -> None:
        """Test runtime startup audit."""
        auditor._audit_runtime_startup()

        # Should have evidence
        assert "runtime_startup" in auditor.evidence
        assert auditor.evidence["runtime_startup"]["exists"] is True

    def test_audit_docker_container_with_valid_dockerfile(
        self, auditor: ProductionAuditor
    ) -> None:
        """Test Docker audit with valid Dockerfile."""
        auditor._audit_docker_container()

        # Should have evidence
        assert "docker" in auditor.evidence
        assert auditor.evidence["docker"]["dockerfile_exists"] is True
        assert auditor.evidence["docker"]["has_healthcheck"] is True
        assert auditor.evidence["docker"]["runs_as_nonroot"] is True

    def test_audit_docker_container_missing_healthcheck(
        self, temp_project: Path
    ) -> None:
        """Test Docker audit catches missing HEALTHCHECK."""
        # Create Dockerfile without HEALTHCHECK
        (temp_project / "Dockerfile").write_text(
            "FROM python:3.11\nUSER appuser\n", encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_docker_container()

        # Should have warning
        warnings = [w for w in auditor.warnings if w["check"] == "Docker Container"]
        assert len(warnings) > 0
        assert any("HEALTHCHECK" in w["message"] for w in warnings)

    def test_audit_docker_container_root_user(self, temp_project: Path) -> None:
        """Test Docker audit catches root user."""
        # Create Dockerfile running as root
        (temp_project / "Dockerfile").write_text(
            "FROM python:3.11\nHEALTHCHECK CMD curl /health\n", encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_docker_container()

        # Should have blocker
        blockers = [b for b in auditor.blockers if b["check"] == "Docker Container"]
        assert len(blockers) > 0
        assert any("root" in b["message"] for b in blockers)

    def test_audit_env_vars_detects_gitignore_missing(
        self, temp_project: Path
    ) -> None:
        """Test env var audit detects .env not in .gitignore."""
        # Remove .env from .gitignore
        (temp_project / ".gitignore").write_text("*.pyc\n", encoding="utf-8")

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_env_vars_and_secrets()

        # Should have blocker
        blockers = [
            b
            for b in auditor.blockers
            if b["check"] == "Environment Variables & Secrets"
        ]
        assert len(blockers) > 0
        assert any(".env" in b["message"] and "gitignore" in b["message"] for b in blockers)

    def test_audit_dependency_pinning_detects_unpinned(
        self, temp_project: Path
    ) -> None:
        """Test dependency audit catches unpinned packages."""
        # Create requirements.txt with unpinned dependency
        (temp_project / "requirements.txt").write_text(
            "pytest==7.4.0\nrequests\n", encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_dependency_pinning()

        # Should have blocker
        blockers = [b for b in auditor.blockers if b["check"] == "Dependency Pinning"]
        assert len(blockers) > 0
        assert any("Unpinned" in b["message"] for b in blockers)

    def test_audit_test_coverage_missing_tests(self, temp_project: Path) -> None:
        """Test coverage audit catches missing test files."""
        # tests/ directory exists but is empty

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_test_coverage()

        # Should have blocker
        blockers = [b for b in auditor.blockers if b["check"] == "Test Coverage"]
        assert len(blockers) > 0
        assert any("No test files" in b["message"] for b in blockers)

    def test_audit_test_coverage_with_tests(self, temp_project: Path) -> None:
        """Test coverage audit with test files present."""
        # Create test files
        (temp_project / "tests" / "test_execution_gate.py").write_text(
            "def test_gate(): pass\n", encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_test_coverage()

        # Should have evidence
        assert "test_coverage" in auditor.evidence
        assert auditor.evidence["test_coverage"]["test_files"] == 1

    def test_audit_ci_gates_missing_workflows(self, temp_project: Path) -> None:
        """Test CI audit catches missing workflows."""
        # .github/workflows exists but is empty

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_ci_gates()

        # Should have blockers
        blockers = [b for b in auditor.blockers if b["check"] == "CI Gates"]
        assert len(blockers) > 0

    def test_audit_ci_gates_with_workflows(self, temp_project: Path) -> None:
        """Test CI audit with proper workflows."""
        # Create CI workflow
        workflow = """
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pytest
      - run: bandit -r src/
"""
        (temp_project / ".github" / "workflows" / "ci.yml").write_text(
            workflow, encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_ci_gates()

        # Should have evidence
        assert "ci_gates" in auditor.evidence
        assert auditor.evidence["ci_gates"]["workflows_found"] == 1
        assert auditor.evidence["ci_gates"]["checks"]["test"] is True
        assert auditor.evidence["ci_gates"]["checks"]["security"] is True

    def test_audit_production_readiness_full(self, auditor: ProductionAuditor) -> None:
        """Test full production readiness audit."""
        result = auditor.audit_production_readiness(generate_report=False)

        # Should return complete result
        assert "timestamp" in result
        assert "score" in result
        assert "status" in result
        assert "blockers" in result
        assert "warnings" in result
        assert "evidence" in result
        assert "deployment_ready" in result

        # Score should be between 0-100
        assert 0 <= result["score"] <= 100

    def test_verify_deployment_readiness(self, auditor: ProductionAuditor) -> None:
        """Test quick deployment verification."""
        result = auditor.verify_deployment_readiness()

        # Should return go/no-go
        assert "ready" in result
        assert "score" in result
        assert "blocker_count" in result
        assert "recommendation" in result
        assert isinstance(result["ready"], bool)

    def test_governance_theater_detection(self, temp_project: Path) -> None:
        """Test detection of governance theater patterns."""
        # Create execution_gate.py with theater pattern
        exec_gate_content = '''import logging
logger = logging.getLogger(__name__)

def execute(action):
    try:
        logger.info("BLOCK: Action denied")
        return True  # Theater: logs BLOCK but allows
    except Exception:
        pass  # Theater: silent failure
'''
        (temp_project / "src" / "app" / "core" / "execution_gate.py").write_text(
            exec_gate_content, encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_governance_enforcement()

        # Should detect theater
        blockers = [
            b for b in auditor.blockers if b["check"] == "Governance Enforcement"
        ]
        assert len(blockers) > 0
        assert any("theater" in b["message"].lower() for b in blockers)

    def test_fail_closed_behavior_detection(self, temp_project: Path) -> None:
        """Test detection of proper fail-closed error handling."""
        # Create execution_gate.py with proper fail-closed
        exec_gate_content = '''
class ExecutionGate:
    def execute(self, action):
        try:
            # Check invariants
            if not self._check_invariants():
                raise Exception("BLOCK: Invariant violation")
            return self._do_execute(action)
        except Exception as e:
            # Fail closed: raise instead of allow
            raise Exception("TERMINATE: Execution failed") from e
'''
        (temp_project / "src" / "app" / "core" / "execution_gate.py").write_text(
            exec_gate_content, encoding="utf-8"
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        auditor._audit_error_handling()

        # Should have evidence of fail-closed
        assert "error_handling" in auditor.evidence
        assert auditor.evidence["error_handling"]["has_fail_closed"] is True

    def test_report_generation(self, temp_project: Path) -> None:
        """Test production audit report generation."""
        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        result = auditor.audit_production_readiness(generate_report=True)

        # Should create report file
        report_path = temp_project / "PRODUCTION_AUDIT_REPORT.md"
        assert report_path.exists()

        # Report should contain key sections
        report_content = report_path.read_text(encoding="utf-8")
        assert "Production Readiness Audit Report" in report_content
        assert "Deployment Readiness Checklist" in report_content
        assert "Verification Commands" in report_content
        assert "Evidence Artifacts Required" in report_content

    def test_blocking_on_missing_critical_paths(self, temp_project: Path) -> None:
        """Test auditor blocks when critical paths missing."""
        # Remove execution_gate.py
        (temp_project / "src" / "app" / "core" / "execution_gate.py").unlink(
            missing_ok=True
        )

        auditor = ProductionAuditor(project_root=str(temp_project), kernel=None)
        result = auditor.audit_production_readiness(generate_report=False)

        # Should not be deployment ready
        assert result["deployment_ready"] is False
        assert len(result["blockers"]) > 0
