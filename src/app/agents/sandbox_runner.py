"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).
"""

from __future__ import annotations

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class SandboxRunner:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        try:
            res = subprocess.run(
                ["python", module_path], capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
