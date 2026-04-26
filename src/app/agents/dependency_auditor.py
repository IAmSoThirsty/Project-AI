"""Dependency & Security Auditor agent

Runs pip-audit and basic dependency checks on newly generated files.

All audit operations route through CognitionKernel for governance.

Security Note: This agent uses subprocess to run pip-audit, a trusted
security auditing tool. Commands are hardcoded and do not accept external input.
"""

from __future__ import annotations

import logging
import shutil
import subprocess  # nosec B404 - subprocess usage for trusted security tool only
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class DependencyAuditor(KernelRoutedAgent):
    """Audits dependencies and security issues.

    All audit operations route through CognitionKernel for tracking.
    """

    def __init__(
        self, data_dir: str = "data", kernel: CognitionKernel | None = None
    ) -> None:
        """Initialize the dependency auditor.

        Args:
            data_dir: Data directory for storing audit results
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Auditing is read-only, low risk
        )

        self.data_dir = data_dir

    def analyze_new_module(self, module_path: str) -> dict[str, Any]:
        """Analyze a module for security issues.

        Routes through kernel for tracking and governance.

        Security: Runs pip-audit with hardcoded arguments. The module_path
        is only used for reading file content, not passed to subprocess.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self._do_analyze_new_module,
            action_name="DependencyAuditor.analyze_new_module",
            action_args=(module_path,),
            requires_approval=False,
            risk_level="low",
            metadata={"module_path": module_path, "operation": "analyze"},
        )

    def _do_analyze_new_module(self, module_path: str) -> dict[str, Any]:
        """Internal implementation of module analysis."""
        # For now, scan imports and report them; run pip-audit for environment vulnerabilities
        try:
            with open(module_path, encoding="utf-8") as f:
                txt = f.read()
            imports = [
                line
                for line in txt.splitlines()
                if line.strip().startswith("import ")
                or line.strip().startswith("from ")
            ]

            # Run pip-audit (best-effort) - validate tool exists
            pip_audit_cmd = shutil.which("pip-audit")
            if pip_audit_cmd:
                try:
                    # nosec B603 B607 - pip-audit is a trusted security tool, path resolved with shutil.which
                    res = subprocess.run(
                        [pip_audit_cmd, "--format", "json"],
                        capture_output=True,
                        text=True,
                        timeout=60,  # 1 minute timeout
                    )
                    audit_json = res.stdout
                except subprocess.TimeoutExpired:
                    logger.warning("pip-audit command timed out after 60 seconds")
                    audit_json = None
                except Exception as e:
                    logger.debug("pip-audit execution failed: %s", e)
                    audit_json = None
            else:
                logger.debug("pip-audit not found in PATH, skipping audit")
                audit_json = None
            return {"success": True, "imports": imports, "pip_audit": audit_json}
        except Exception as e:
            logger.exception("Dependency audit failed for %s: %s", module_path, e)
            return {"success": False, "error": str(e)}
