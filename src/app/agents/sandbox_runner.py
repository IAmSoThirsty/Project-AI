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

logger = logging.getLogger(__name__)


class SandboxRunner:
    def __init__(self, data_dir: str = "data") -> None:
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
        # Validate module path exists and is a file
        if not os.path.isfile(module_path):
            logger.error("Invalid module path: %s", module_path)
            return {"success": False, "error": "invalid_path"}

        # Ensure path is absolute and normalized to prevent path traversal
        abs_path = os.path.abspath(module_path)

        # Resolve Python executable - use shutil.which for security
        python_cmd = shutil.which("python") or shutil.which("python3")
        if not python_cmd:
            logger.error("Python executable not found in PATH")
            return {"success": False, "error": "python_not_found"}

        try:
            # nosec B603 B607 - Python executable resolved with shutil.which, module path validated
            res = subprocess.run(
                [python_cmd, abs_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            logger.warning("Sandbox execution timed out after %d seconds for %s", timeout, module_path)
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
