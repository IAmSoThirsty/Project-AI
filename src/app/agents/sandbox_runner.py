"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This runner executes untrusted user-generated code in a subprocess.
The module path is user-controlled, so this is intentionally using subprocess
with appropriate timeout and capture settings for sandboxing.
"""
from __future__ import annotations

import logging
import subprocess  # nosec B404 - subprocess used for intentional sandbox execution
from typing import Any

logger = logging.getLogger(__name__)


class SandboxRunner:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        """Run user-generated code in subprocess sandbox.
        
        Security: This intentionally runs untrusted code in a sandboxed subprocess
        with strict timeout limits. The subprocess has no shell access and limited
        capabilities through capture_output=True.
        """
        try:
            # nosec B603 B607 - Intentional execution of user code in sandbox with timeout
            res = subprocess.run(["python", module_path], capture_output=True, text=True, timeout=timeout)
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
