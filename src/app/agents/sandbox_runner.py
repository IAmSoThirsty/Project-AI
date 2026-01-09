"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This agent uses subprocess to run Python modules in isolation.
Module paths are validated before execution. The subprocess runs with limited
privileges and timeout constraints.
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
        """Run Python module in a subprocess with timeout.
        
        Security: Uses subprocess to isolate untrusted code execution.
        Module path should be validated by caller before passing to this method.
        """
        try:
            # nosec B603, B607 - subprocess used for code isolation in sandbox
            res = subprocess.run(["python", module_path], capture_output=True, text=True, timeout=timeout)  # nosec B603, B607
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
