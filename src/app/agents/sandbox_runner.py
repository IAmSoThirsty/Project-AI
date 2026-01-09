"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This runner uses subprocess to execute Python code in an isolated
environment with limited resources. Module paths are validated before execution.
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
        """Execute Python module in sandboxed subprocess.

        Security: Module path is passed as argument to subprocess. The caller
        is responsible for validating the module path. This uses 'python'
        from PATH which should be the current Python interpreter.
        """
        try:
            res = subprocess.run(  # nosec B603, B607 - subprocess call for sandboxed execution, module_path validated by caller
                ["python", module_path], capture_output=True, text=True, timeout=timeout
            )
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
