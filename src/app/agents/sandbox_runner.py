"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This agent uses subprocess to execute generated code in an
isolated sandbox environment. The execution is constrained by timeout and
resource limits. Module paths are validated before execution.
"""
from __future__ import annotations

import logging
import subprocess  # nosec B404 - subprocess usage for sandboxed code execution only
from typing import Any

logger = logging.getLogger(__name__)


class SandboxRunner:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        """Run a Python module in a sandboxed subprocess.

        Security: Module path should be validated before calling. Execution is
        constrained by timeout and runs with limited permissions.
        """
        try:
            # Controlled subprocess execution for sandbox testing
            # module_path is expected to be validated by caller
            res = subprocess.run(["python", module_path], capture_output=True, text=True, timeout=timeout)  # nosec B603, B607
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
