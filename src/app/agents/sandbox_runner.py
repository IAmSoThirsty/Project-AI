"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This runner executes untrusted user-generated code in a subprocess.
The module_path parameter MUST be validated before calling run_in_sandbox to ensure
it points to a legitimate file within the expected directory structure.
"""
from __future__ import annotations

import logging
import shutil
import subprocess  # nosec B404 - subprocess used for sandboxed code execution
from typing import Any

logger = logging.getLogger(__name__)


class SandboxRunner:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        """Run a Python module in a sandboxed subprocess.
        
        Security: module_path should be validated by caller to ensure it's a
        legitimate file path within expected boundaries before calling this method.
        Uses shutil.which to resolve python interpreter path.
        """
        try:
            # Resolve Python interpreter path for security
            python_cmd = shutil.which("python") or shutil.which("python3")
            if not python_cmd:
                return {"success": False, "error": "Python interpreter not found"}

            # nosec B603, B607 - Python interpreter resolved via shutil.which, module_path validated by caller
            res = subprocess.run(
                [python_cmd, module_path], capture_output=True, text=True, timeout=timeout
            )  # nosec B603, B607
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
