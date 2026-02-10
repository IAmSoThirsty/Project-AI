"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This runner executes dynamically generated code in a subprocess.
The module_path parameter is validated to prevent path traversal attacks.
Python executable is resolved from system PATH for security.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess  # nosec B404 - subprocess used for controlled code execution in sandbox
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class SandboxRunner(KernelRoutedAgent):
    def __init__(
        self, data_dir: str = "data", kernel: CognitionKernel | None = None
    ) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",
        )
        self.data_dir = data_dir

    def run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        """Run a Python module in a sandboxed subprocess.

        Security: Validates module path exists and is not a path traversal attempt.
        Uses shutil.which to resolve Python executable from PATH.

        Args:
            module_path: Absolute path to Python module to execute
            timeout: Maximum execution time in seconds

        Returns:
            Dictionary with success status, stdout, stderr
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_run_in_sandbox,
            module_path,
            timeout,
            operation_name="run_in_sandbox",
            risk_level="high",
            metadata={"module_path": module_path, "timeout": timeout},
        )

    def _do_run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        """Internal implementation of sandbox execution."""
        # Validate module path exists and is a file
        if not os.path.isfile(module_path):
            logger.error("Invalid module path: %s", module_path)
            return {"success": False, "error": "invalid_path"}

        # Ensure path is absolute and normalized to prevent path traversal
        abs_path = os.path.abspath(os.path.normpath(module_path))

        # Validate the path is within the working directory (prevents traversal attacks)
        cwd = os.path.abspath(os.getcwd())
        try:
            common = os.path.commonpath([abs_path, cwd])
            if common != cwd:
                logger.error(
                    "Path traversal attempt detected: %s not within %s", abs_path, cwd
                )
                return {"success": False, "error": "path_traversal"}
        except ValueError:
            # Different drives on Windows or no common path
            logger.error(
                "Path traversal attempt: %s on different drive from %s", abs_path, cwd
            )
            return {"success": False, "error": "path_traversal"}

        # Resolve Python executable - use shutil.which for security
        python_cmd = shutil.which("python") or shutil.which("python3")
        if not python_cmd:
            logger.error("Python executable not found in PATH")
            return {"success": False, "error": "python_not_found"}

        try:
            # nosec B603 B607 - Python executable resolved with shutil.which, module path validated
            res = subprocess.run(
                [python_cmd, abs_path], capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
            }
        except subprocess.TimeoutExpired:
            logger.warning(
                "Sandbox execution timed out after %d seconds for %s",
                timeout,
                module_path,
            )
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
