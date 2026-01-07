"""Refactoring / Style Harmonizer agent

Performs formatting and safe refactor suggestions using ruff and black.

Security Note: This agent uses subprocess to run black and ruff, which are
trusted code formatting tools. Commands are hardcoded and do not accept
external input beyond validated file paths.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess  # nosec B404 - subprocess usage for trusted dev tools only
from typing import Any

logger = logging.getLogger(__name__)


class RefactorAgent:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def suggest_refactor(self, path: str) -> dict[str, Any]:
        """Suggest refactoring for a file using black and ruff.

        Security: File path is validated to exist before being passed to
        subprocess. Commands use trusted dev tools with hardcoded arguments.
        """
        # Validate path exists and is a file
        if not os.path.isfile(path):
            logger.error("Invalid file path: %s", path)
            return {"success": False, "error": "invalid_path"}

        # Resolve tool paths
        black_cmd = shutil.which("black") or "black"
        ruff_cmd = shutil.which("ruff") or "ruff"

        try:
            # nosec B603 B607 - black is a trusted dev tool, path is validated
            res_black = subprocess.run(
                [black_cmd, "--check", path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # nosec B603 B607 - ruff is a trusted dev tool, path is validated
            res_ruff = subprocess.run(
                [ruff_cmd, "check", path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {"black_check": res_black.returncode == 0, "ruff_out": res_ruff.stdout}
        except subprocess.TimeoutExpired:
            logger.warning("Refactor check timed out for %s", path)
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Refactor check failed: %s", e)
            return {"success": False, "error": str(e)}
