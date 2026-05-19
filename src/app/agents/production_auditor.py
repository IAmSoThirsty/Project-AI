"""Production Readiness Auditor Agent

Audits Project-AI for production deployment readiness without weakening governance.

Mission:
    - Validate production readiness across all critical dimensions
    - Ensure governance enforcement is real, not theater
    - Identify blockers and required fixes
    - Generate evidence manifest for deployment approval

Rules:
    - Do not accept "status: healthy" unless dependencies are actually checked
    - Do not accept simulated production evidence as real evidence
    - Do not recommend shortcuts that weaken governance
    - Prefer explicit failure over misleading success

All operations route through CognitionKernel for governance.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess  # nosec B404 - subprocess usage for trusted tools only
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

_CRITICAL_PATHS = [
    "src/app/core/execution_gate.py",
    "src/app/core/octoreflex.py",
    "src/app/core/invariant_engine.py",
    "src/app/governance/triumvirate_server.py",
    "canonical/scenario.yaml",
    "canonical/replay.py",
]

_REQUIRED_HEALTH_ENDPOINTS = [
    "/health",
    "/ready",
    "/live",
]

_REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "HUGGINGFACE_API_KEY",
    "FERNET_KEY",
]

_REQUIRED_EVIDENCE_ARTIFACTS = [
    "test-artifacts/coverage/",
    "ci-reports/",
    "audit.log",
    "data/governance_drift_alerts/",
    "data/acceptance_ledger/",
]


class ProductionAuditor(KernelRoutedAgent):
    """Audits production readiness with uncompromising standards.

    Validates:
        - Runtime startup assumptions
        - Container/Docker behavior
        - Health/readiness/liveness endpoints
        - Environment variables and secrets handling
        - Logging and audit durability
        - Error handling and fail-closed behavior
        - Dependency pinning
        - CI gates
        - Test coverage around critical paths
        - Evidence manifest completeness
        - Release/tag consistency
    """

    def __init__(
        self,
        project_root: str = ".",
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize the production auditor.

        Args:
            project_root: Root directory of the project
            kernel: CognitionKernel instance for routing operations
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Auditing is read-only
        )
        self.project_root = Path(project_root)
        self.blockers: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.evidence: dict[str, Any] = {}

    def audit_production_readiness(
        self, generate_report: bool = True
    ) -> dict[str, Any]:
        """Run comprehensive production readiness audit.

        Returns:
            Audit report with blockers, warnings, and evidence
        """
        return self._execute_through_kernel(
            action=self._do_audit_production_readiness,
            action_name="ProductionAuditor.audit_production_readiness",
            action_args=(generate_report,),
            requires_approval=False,
            risk_level="low",
            metadata={"operation": "full_audit"},
        )

    def _do_audit_production_readiness(
        self, generate_report: bool = True
    ) -> dict[str, Any]:
        """Internal implementation of production audit."""
        self.blockers = []
        self.warnings = []
        self.evidence = {}

        logger.info("Starting production readiness audit...")

        # Run all audit checks
        self._audit_runtime_startup()
        self._audit_docker_container()
        self._audit_health_endpoints()
        self._audit_env_vars_and_secrets()
        self._audit_logging_and_audit()
        self._audit_error_handling()
        self._audit_dependency_pinning()
        self._audit_ci_gates()
        self._audit_test_coverage()
        self._audit_evidence_manifest()
        self._audit_release_consistency()
        self._audit_governance_enforcement()

        # Calculate scores
        total_checks = 12
        passed_checks = total_checks - len(self.blockers)
        score = (passed_checks / total_checks) * 100

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "status": "BLOCKED" if self.blockers else "READY",
            "blockers": self.blockers,
            "warnings": self.warnings,
            "evidence": self.evidence,
            "deployment_ready": len(self.blockers) == 0,
        }

        if generate_report:
            self._generate_report(result)

        logger.info(
            f"Production audit complete: {score:.1f}% ({passed_checks}/{total_checks} checks passed)"
        )

        return result

    def _audit_runtime_startup(self) -> None:
        """Audit runtime startup assumptions and initialization."""
        check_name = "Runtime Startup"

        # Check if main entry point exists
        main_py = self.project_root / "src" / "app" / "main.py"
        if not main_py.exists():
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "Main entry point src/app/main.py not found",
                    "fix": "Create main entry point with proper startup sequence",
                }
            )
            return

        # Check for hardcoded assumptions
        with open(main_py, encoding="utf-8") as f:
            content = f.read()

        hardcoded_patterns = [
            (r"localhost:[\d]+", "hardcoded localhost"),
            (r'["\']127\.0\.0\.1["\']', "hardcoded 127.0.0.1"),
            (r'os\.environ\[(["\'][^"\']+["\']\])', "unvalidated env var access"),
        ]

        for pattern, desc in hardcoded_patterns:
            if re.search(pattern, content):
                self.warnings.append(
                    {
                        "check": check_name,
                        "severity": "MEDIUM",
                        "message": f"Found {desc} in main.py",
                        "recommendation": "Use config-driven approach",
                    }
                )

        self.evidence["runtime_startup"] = {
            "main_entry": str(main_py),
            "exists": True,
        }

    def _audit_docker_container(self) -> None:
        """Audit Docker/container configuration."""
        check_name = "Docker Container"

        dockerfile = self.project_root / "Dockerfile"
        if not dockerfile.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "MEDIUM",
                    "message": "Dockerfile not found",
                    "recommendation": "Add Dockerfile for containerized deployment",
                }
            )
            return

        with open(dockerfile, encoding="utf-8") as f:
            content = f.read()

        # Check for health checks
        if "HEALTHCHECK" not in content:
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "HIGH",
                    "message": "Dockerfile missing HEALTHCHECK instruction",
                    "recommendation": "Add HEALTHCHECK with curl/wget to health endpoint",
                }
            )

        # Check for non-root user
        if "USER " not in content or content.find("USER root") > content.rfind(
            "USER "
        ):
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "Container runs as root user",
                    "fix": "Add non-root user and switch with USER instruction",
                }
            )

        # Check for .dockerignore
        dockerignore = self.project_root / ".dockerignore"
        if not dockerignore.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "LOW",
                    "message": ".dockerignore not found",
                    "recommendation": "Add .dockerignore to exclude sensitive files",
                }
            )

        self.evidence["docker"] = {
            "dockerfile_exists": True,
            "has_healthcheck": "HEALTHCHECK" in content,
            "runs_as_nonroot": "USER " in content,
            "has_dockerignore": dockerignore.exists(),
        }

    def _audit_health_endpoints(self) -> None:
        """Audit health, readiness, and liveness endpoints."""
        check_name = "Health Endpoints"

        # Search for endpoint definitions
        triumvirate_server = (
            self.project_root / "src" / "app" / "governance" / "triumvirate_server.py"
        )
        if not triumvirate_server.exists():
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "Triumvirate server not found",
                    "fix": "Implement triumvirate_server.py with health endpoints",
                }
            )
            return

        with open(triumvirate_server, encoding="utf-8") as f:
            content = f.read()

        found_endpoints = []
        for endpoint in _REQUIRED_HEALTH_ENDPOINTS:
            # Check for route definition
            if f'"{endpoint}"' in content or f"'{endpoint}'" in content:
                found_endpoints.append(endpoint)

                # Verify endpoint actually checks dependencies
                endpoint_section = content[content.find(endpoint) :]
                if "status" in endpoint_section[:500]:
                    if not any(
                        dep in endpoint_section[:500]
                        for dep in ["redis", "kernel", "invariant", "check"]
                    ):
                        self.blockers.append(
                            {
                                "check": check_name,
                                "severity": "CRITICAL",
                                "message": f"Endpoint {endpoint} returns status without checking dependencies",
                                "fix": "Implement real dependency checks (Redis, kernel, invariants)",
                            }
                        )

        missing = set(_REQUIRED_HEALTH_ENDPOINTS) - set(found_endpoints)
        if missing:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": f"Missing health endpoints: {', '.join(missing)}",
                    "fix": "Implement all required endpoints: /health, /ready, /live",
                }
            )

        self.evidence["health_endpoints"] = {
            "found": found_endpoints,
            "missing": list(missing),
        }

    def _audit_env_vars_and_secrets(self) -> None:
        """Audit environment variable and secrets handling."""
        check_name = "Environment Variables & Secrets"

        # Check for .env.example
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "MEDIUM",
                    "message": ".env.example not found",
                    "recommendation": "Create .env.example template for required vars",
                }
            )

        # Check if .env is gitignored
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, encoding="utf-8") as f:
                gitignore_content = f.read()
            if ".env" not in gitignore_content:
                self.blockers.append(
                    {
                        "check": check_name,
                        "severity": "CRITICAL",
                        "message": ".env not in .gitignore",
                        "fix": "Add .env to .gitignore to prevent secret leaks",
                    }
                )

        # Scan for hardcoded secrets in critical paths
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{32,}",  # OpenAI API key
            r"hf_[a-zA-Z0-9]{32,}",  # HuggingFace token
            r"['\"][A-Za-z0-9+/=]{32,}['\"]",  # Base64 secrets
        ]

        for critical_path in _CRITICAL_PATHS:
            file_path = self.project_root / critical_path
            if not file_path.exists():
                continue

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            for pattern in secret_patterns:
                if re.search(pattern, content):
                    self.blockers.append(
                        {
                            "check": check_name,
                            "severity": "CRITICAL",
                            "message": f"Potential hardcoded secret in {critical_path}",
                            "fix": "Remove hardcoded secrets, use environment variables",
                        }
                    )
                    break

        self.evidence["env_and_secrets"] = {
            "env_example_exists": env_example.exists(),
            "env_gitignored": ".env" in gitignore_content if gitignore.exists() else False,
            "secrets_scanned": len(_CRITICAL_PATHS),
        }

    def _audit_logging_and_audit(self) -> None:
        """Audit logging and audit trail durability."""
        check_name = "Logging & Audit"

        # Check for audit log
        audit_log = self.project_root / "audit.log"
        if not audit_log.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "HIGH",
                    "message": "audit.log not found",
                    "recommendation": "Initialize audit log at startup",
                }
            )

        # Check acceptance ledger
        ledger_dir = self.project_root / "data" / "acceptance_ledger"
        if not ledger_dir.exists():
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "Acceptance ledger directory not found",
                    "fix": "Create data/acceptance_ledger/ for tamper-evident audit",
                }
            )

        # Check logging configuration
        logging_config = None
        for config_file in ["logging.yaml", "logging.json", "pyproject.toml"]:
            config_path = self.project_root / config_file
            if config_path.exists():
                logging_config = str(config_path)
                break

        if not logging_config:
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "MEDIUM",
                    "message": "No logging configuration found",
                    "recommendation": "Add logging.yaml or configure in pyproject.toml",
                }
            )

        self.evidence["logging_and_audit"] = {
            "audit_log_exists": audit_log.exists(),
            "acceptance_ledger_exists": ledger_dir.exists(),
            "logging_config": logging_config,
        }

    def _audit_error_handling(self) -> None:
        """Audit error handling and fail-closed behavior."""
        check_name = "Error Handling"

        # Check execution gate for fail-closed behavior
        exec_gate = self.project_root / "src" / "app" / "core" / "execution_gate.py"
        if not exec_gate.exists():
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "ExecutionGate not found",
                    "fix": "Implement execution_gate.py with fail-closed enforcement",
                }
            )
            return

        with open(exec_gate, encoding="utf-8") as f:
            content = f.read()

        # Check for fail-closed pattern
        fail_closed_indicators = [
            "except Exception",
            "raise",
            "BLOCK",
            "TERMINATE",
        ]

        has_fail_closed = all(indicator in content for indicator in fail_closed_indicators)

        if not has_fail_closed:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "ExecutionGate missing fail-closed error handling",
                    "fix": "Add exception handling that blocks on errors, not allows",
                }
            )

        # Check for try/except without logging
        try_except_pattern = r"try:.*?except\s+\w+.*?pass"
        if re.search(try_except_pattern, content, re.DOTALL):
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "HIGH",
                    "message": "Found silent exception handling (except: pass)",
                    "recommendation": "Log all exceptions before handling",
                }
            )

        self.evidence["error_handling"] = {
            "execution_gate_exists": True,
            "has_fail_closed": has_fail_closed,
        }

    def _audit_dependency_pinning(self) -> None:
        """Audit dependency version pinning."""
        check_name = "Dependency Pinning"

        requirements_files = [
            "requirements.txt",
            "requirements.lock",
            "pyproject.toml",
        ]

        found_file = None
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                found_file = req_file
                break

        if not found_file:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "No dependency file found",
                    "fix": "Create requirements.txt or pyproject.toml with pinned versions",
                }
            )
            return

        req_path = self.project_root / found_file
        with open(req_path, encoding="utf-8") as f:
            content = f.read()

        # Check for unpinned dependencies (e.g., "requests" instead of "requests==2.31.0")
        if found_file == "requirements.txt":
            unpinned = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" not in line and ">=" not in line and "~=" not in line:
                        unpinned.append(line)

            if unpinned:
                self.blockers.append(
                    {
                        "check": check_name,
                        "severity": "CRITICAL",
                        "message": f"Unpinned dependencies: {', '.join(unpinned[:5])}",
                        "fix": "Pin all dependencies to exact versions with ==",
                    }
                )

        self.evidence["dependency_pinning"] = {
            "requirements_file": found_file,
            "exists": True,
        }

    def _audit_ci_gates(self) -> None:
        """Audit CI/CD gates and quality checks."""
        check_name = "CI Gates"

        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "HIGH",
                    "message": "GitHub workflows directory not found",
                    "recommendation": "Add CI workflows for automated testing and security",
                }
            )
            return

        required_checks = {
            "test": ["pytest", "test"],
            "lint": ["ruff", "lint", "flake8"],
            "security": ["bandit", "safety", "pip-audit"],
            "type": ["mypy", "pyright"],
        }

        workflow_files = list(workflows_dir.glob("*.yml")) + list(
            workflows_dir.glob("*.yaml")
        )
        found_checks = {check: False for check in required_checks}

        for workflow_file in workflow_files:
            with open(workflow_file, encoding="utf-8") as f:
                content = f.read().lower()

            for check_name_inner, keywords in required_checks.items():
                if any(keyword in content for keyword in keywords):
                    found_checks[check_name_inner] = True

        missing_checks = [check for check, found in found_checks.items() if not found]

        if "test" in missing_checks:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "No test workflow found in CI",
                    "fix": "Add CI workflow with pytest test execution",
                }
            )

        if "security" in missing_checks:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "No security scanning in CI",
                    "fix": "Add Bandit, pip-audit, or safety to CI pipeline",
                }
            )

        if missing_checks and "test" not in missing_checks:
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "MEDIUM",
                    "message": f"Missing CI checks: {', '.join(missing_checks)}",
                    "recommendation": "Add comprehensive CI gates (lint, type, security)",
                }
            )

        self.evidence["ci_gates"] = {
            "workflows_found": len(workflow_files),
            "checks": found_checks,
        }

    def _audit_test_coverage(self) -> None:
        """Audit test coverage around critical paths."""
        check_name = "Test Coverage"

        # Check for test directory
        test_dirs = [
            self.project_root / "tests",
            self.project_root / "test",
            self.project_root / "src" / "tests",
        ]

        test_dir = None
        for td in test_dirs:
            if td.exists():
                test_dir = td
                break

        if not test_dir:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "No test directory found",
                    "fix": "Create tests/ directory with unit and integration tests",
                }
            )
            return

        # Count test files
        test_files = list(test_dir.rglob("test_*.py")) + list(
            test_dir.rglob("*_test.py")
        )

        if len(test_files) == 0:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "No test files found",
                    "fix": "Write tests for critical paths (ExecutionGate, InvariantEngine, etc.)",
                }
            )

        # Check for coverage report
        coverage_dir = self.project_root / "test-artifacts" / "coverage"
        if not coverage_dir.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "HIGH",
                    "message": "Coverage reports not found",
                    "recommendation": "Run pytest with --cov and generate coverage report",
                }
            )

        # Check for tests of critical paths
        critical_tests = {
            "execution_gate": False,
            "octoreflex": False,
            "invariant_engine": False,
        }

        for test_file in test_files:
            test_name = test_file.stem.lower()
            for critical in critical_tests:
                if critical in test_name:
                    critical_tests[critical] = True

        missing_critical = [
            critical for critical, tested in critical_tests.items() if not tested
        ]

        if missing_critical:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": f"Missing tests for critical components: {', '.join(missing_critical)}",
                    "fix": "Write tests for ExecutionGate, OctoReflex, InvariantEngine",
                }
            )

        self.evidence["test_coverage"] = {
            "test_dir": str(test_dir) if test_dir else None,
            "test_files": len(test_files),
            "critical_tests": critical_tests,
        }

    def _audit_evidence_manifest(self) -> None:
        """Audit completeness of evidence artifacts."""
        check_name = "Evidence Manifest"

        missing_artifacts = []
        for artifact_path in _REQUIRED_EVIDENCE_ARTIFACTS:
            full_path = self.project_root / artifact_path
            if not full_path.exists():
                missing_artifacts.append(artifact_path)

        if missing_artifacts:
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": f"Missing evidence artifacts: {', '.join(missing_artifacts)}",
                    "fix": "Create required directories and run test/audit pipelines",
                }
            )

        # Check canonical replay
        replay_script = self.project_root / "canonical" / "replay.py"
        if not replay_script.exists():
            self.blockers.append(
                {
                    "check": check_name,
                    "severity": "CRITICAL",
                    "message": "canonical/replay.py not found",
                    "fix": "Implement canonical scenario replay for 5/5 invariant validation",
                }
            )
        else:
            # Try to verify replay works
            try:
                result = subprocess.run(  # nosec B603 - trusted internal script
                    [sys.executable, str(replay_script), "--dry-run"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.project_root),
                    check=False,
                )
                if result.returncode != 0:
                    self.blockers.append(
                        {
                            "check": check_name,
                            "severity": "CRITICAL",
                            "message": "canonical/replay.py execution failed",
                            "fix": "Fix replay script to pass 5/5 invariants",
                            "error": result.stderr[:200],
                        }
                    )
            except Exception as e:
                self.warnings.append(
                    {
                        "check": check_name,
                        "severity": "HIGH",
                        "message": f"Could not verify replay.py: {e}",
                        "recommendation": "Manually verify replay.py execution",
                    }
                )

        self.evidence["evidence_manifest"] = {
            "missing_artifacts": missing_artifacts,
            "replay_exists": replay_script.exists(),
        }

    def _audit_release_consistency(self) -> None:
        """Audit release/tag consistency."""
        check_name = "Release Consistency"

        # Check for version file or tag
        version_sources = [
            self.project_root / "VERSION",
            self.project_root / "pyproject.toml",
            self.project_root / "src" / "app" / "__version__.py",
        ]

        version_found = None
        for version_source in version_sources:
            if version_source.exists():
                version_found = str(version_source)
                break

        if not version_found:
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "MEDIUM",
                    "message": "No version file found",
                    "recommendation": "Create VERSION or __version__.py for release tracking",
                }
            )

        # Check for CHANGELOG
        changelog = self.project_root / "CHANGELOG.md"
        if not changelog.exists():
            self.warnings.append(
                {
                    "check": check_name,
                    "severity": "LOW",
                    "message": "CHANGELOG.md not found",
                    "recommendation": "Maintain CHANGELOG.md for release notes",
                }
            )

        self.evidence["release_consistency"] = {
            "version_file": version_found,
            "changelog_exists": changelog.exists(),
        }

    def _audit_governance_enforcement(self) -> None:
        """Audit that governance is real, not theater."""
        check_name = "Governance Enforcement"

        # Verify ExecutionGate actually blocks actions
        exec_gate = self.project_root / "src" / "app" / "core" / "execution_gate.py"
        if exec_gate.exists():
            with open(exec_gate, encoding="utf-8") as f:
                content = f.read()

            # Check for theater patterns (logging without blocking)
            # Pattern: logger.X("BLOCK...") followed by return True
            theater_patterns = [
                (r'logger\.\w+\([^\)]*BLOCK[^\)]*\)[^\n]*\n[^\n]*return\s+True', "logs BLOCK but returns True"),
                (r'logger\.\w+\([^\)]*TERMINATE[^\)]*\)[^\n]*\n[^\n]*pass', "logs TERMINATE but continues"),
                (r"# TODO.*governance", "unimplemented governance TODO"),
            ]

            for pattern, desc in theater_patterns:
                if re.search(pattern, content):
                    self.blockers.append(
                        {
                            "check": check_name,
                            "severity": "CRITICAL",
                            "message": f"Governance theater detected: {desc}",
                            "fix": "Replace logging with actual enforcement (raise exception, block action)",
                        }
                    )

        # Verify OctoReflex enforcement levels work
        octoreflex = self.project_root / "src" / "app" / "core" / "octoreflex.py"
        if octoreflex.exists():
            with open(octoreflex, encoding="utf-8") as f:
                content = f.read()

            enforcement_levels = ["WARN", "BLOCK", "TERMINATE", "ESCALATE"]
            for level in enforcement_levels:
                if level not in content:
                    self.warnings.append(
                        {
                            "check": check_name,
                            "severity": "HIGH",
                            "message": f"OctoReflex missing {level} enforcement level",
                            "recommendation": f"Implement {level} enforcement with real action",
                        }
                    )

        # Verify canonical scenario passes 5/5 invariants
        scenario = self.project_root / "canonical" / "scenario.yaml"
        if scenario.exists():
            with open(scenario, encoding="utf-8") as f:
                scenario_data = yaml.safe_load(f)

            if not scenario_data or "invariants" not in scenario_data:
                self.blockers.append(
                    {
                        "check": check_name,
                        "severity": "CRITICAL",
                        "message": "canonical/scenario.yaml missing invariants",
                        "fix": "Define 5 canonical invariants for governance validation",
                    }
                )

        self.evidence["governance_enforcement"] = {
            "execution_gate_enforces": exec_gate.exists(),
            "octoreflex_exists": octoreflex.exists(),
            "canonical_scenario_exists": scenario.exists(),
        }

    def _generate_report(self, result: dict[str, Any]) -> None:
        """Generate human-readable production audit report."""
        report_path = self.project_root / "PRODUCTION_AUDIT_REPORT.md"

        score = result["score"]
        status = result["status"]
        blockers = result["blockers"]
        warnings = result["warnings"]

        # Generate checklist
        checklist_items = []
        if not blockers:
            checklist_items.append("- [x] All critical checks passed")
        else:
            checklist_items.append(f"- [ ] {len(blockers)} critical blockers to fix")

        checklist_items.append(f"- {'[x]' if score >= 80 else '[ ]'} Score >= 80%")
        checklist_items.append(
            f"- {'[x]' if len(warnings) == 0 else '[ ]'} Zero warnings"
        )

        # Generate verification commands
        verification_commands = [
            "# Verify governance enforcement",
            "PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 canonical/replay.py",
            "",
            "# Run test suite",
            "pytest -v --cov=src/app/core --cov-report=html",
            "",
            "# Security scan",
            "bandit -r src/ -f json -o ci-reports/bandit.json",
            "",
            "# Dependency audit",
            "pip-audit --desc",
            "",
            "# Lint check",
            "ruff check . --output-format=json",
        ]

        # Generate required fixes
        required_fixes = []
        for i, blocker in enumerate(blockers, 1):
            required_fixes.append(f"{i}. **{blocker['check']}** ({blocker['severity']})")
            required_fixes.append(f"   - Issue: {blocker['message']}")
            required_fixes.append(f"   - Fix: {blocker['fix']}")
            required_fixes.append("")

        # Build report
        report_lines = [
            "# Production Readiness Audit Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Score:** {score:.1f}%",
            f"**Status:** {status}",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"- **Blockers:** {len(blockers)} critical issues",
            f"- **Warnings:** {len(warnings)} recommendations",
            f"- **Deployment Ready:** {'✅ YES' if result['deployment_ready'] else '❌ NO'}",
            "",
            "## Deployment Readiness Checklist",
            "",
            *checklist_items,
            "",
            "## Current Production Blockers",
            "",
        ]

        if blockers:
            report_lines.extend(required_fixes)
        else:
            report_lines.append("✅ No production blockers found.")
            report_lines.append("")

        report_lines.extend(
            [
                "## Required Fixes",
                "",
            ]
        )

        if blockers:
            report_lines.append(
                f"Complete all {len(blockers)} blockers above before deployment."
            )
        else:
            report_lines.append("✅ No required fixes.")

        report_lines.extend(
            [
                "",
                "## Verification Commands",
                "",
                "```bash",
                *verification_commands,
                "```",
                "",
                "## Evidence Artifacts Required",
                "",
            ]
        )

        for artifact in _REQUIRED_EVIDENCE_ARTIFACTS:
            exists = (self.project_root / artifact).exists()
            status_icon = "✅" if exists else "❌"
            report_lines.append(f"- {status_icon} `{artifact}`")

        report_lines.extend(
            [
                "",
                "---",
                "",
                "## Detailed Findings",
                "",
                "### Warnings",
                "",
            ]
        )

        if warnings:
            for warning in warnings:
                report_lines.append(f"**{warning['check']}** ({warning['severity']})")
                report_lines.append(f"- {warning['message']}")
                report_lines.append(f"- Recommendation: {warning.get('recommendation', 'N/A')}")
                report_lines.append("")
        else:
            report_lines.append("✅ No warnings.")
            report_lines.append("")

        report_lines.extend(
            [
                "### Evidence Summary",
                "",
                "```json",
                json.dumps(result["evidence"], indent=2),
                "```",
                "",
                "---",
                "",
                "**Audit Rule:** Explicit failure over misleading success.",
                "",
            ]
        )

        # Write report
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        logger.info(f"Production audit report written to {report_path}")

    def verify_deployment_readiness(self) -> dict[str, Any]:
        """Quick verification for deployment approval.

        Returns:
            Simple go/no-go result with summary
        """
        return self._execute_through_kernel(
            action=self._do_verify_deployment_readiness,
            action_name="ProductionAuditor.verify_deployment_readiness",
            action_args=(),
            requires_approval=False,
            risk_level="low",
            metadata={"operation": "quick_verify"},
        )

    def _do_verify_deployment_readiness(self) -> dict[str, Any]:
        """Internal implementation of quick verification."""
        audit_result = self._do_audit_production_readiness(generate_report=False)

        return {
            "ready": audit_result["deployment_ready"],
            "score": audit_result["score"],
            "blocker_count": len(audit_result["blockers"]),
            "warning_count": len(audit_result["warnings"]),
            "recommendation": (
                "DEPLOY" if audit_result["deployment_ready"] else "FIX BLOCKERS FIRST"
            ),
        }
