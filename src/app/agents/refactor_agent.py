"""Refactoring / Style Harmonizer agent

Performs formatting and safe refactor suggestions using ruff and black.
"""
from __future__ import annotations

import logging
import subprocess  # nosec B404 - Used for internal code formatting tools only
from typing import Any

logger = logging.getLogger(__name__)


class RefactorAgent:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def suggest_refactor(self, path: str) -> dict[str, Any]:
        try:
            res_black = subprocess.run(["black", "--check", path], capture_output=True, text=True)  # nosec B603, B607
            res_ruff = subprocess.run(["ruff", "check", path], capture_output=True, text=True)  # nosec B603, B607
            return {"black_check": res_black.returncode == 0, "ruff_out": res_ruff.stdout}
        except Exception as e:
            logger.exception("Refactor check failed: %s", e)
            return {"success": False, "error": str(e)}
