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

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class RefactorAgent(KernelRoutedAgent):
    def __init__(
        self, data_dir: str = "data", kernel: CognitionKernel | None = None
    ) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
        self.data_dir = data_dir

    def suggest_refactor(self, path: str) -> dict[str, Any]:
        """Suggest refactoring for a file using black and ruff.

        Security: File path is validated to exist and be within the working
        directory before being passed to subprocess. Commands use trusted
        dev tools with resolved absolute paths.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_suggest_refactor,
            path,
            operation_name="suggest_refactor",
            risk_level="medium",
            metadata={"file_path": path},
        )

    def _do_suggest_refactor(self, path: str) -> dict[str, Any]:
        """Internal implementation of refactor suggestion."""
        # Validate path exists, is a file, and is not a path traversal attempt
        if not os.path.isfile(path):
            logger.error("Invalid file path: %s", path)
            return {"success": False, "error": "invalid_path"}

        # Ensure path is absolute and normalized to prevent path traversal
        abs_path = os.path.abspath(path)
        cwd = os.getcwd()

        # Check that the resolved path is within current working directory
        # Uses os.path.commonpath for robust cross-platform validation
        try:
            common = os.path.commonpath([abs_path, cwd])
            # Path is valid if common path is cwd (abs_path is under cwd or is cwd)
            if common != cwd:
                logger.error("Path traversal detected: %s not within %s", abs_path, cwd)
                return {"success": False, "error": "path_traversal"}
        except ValueError:
            # Different drives on Windows or no common path
            logger.error(
                "Path traversal detected: %s on different drive from %s", abs_path, cwd
            )
            return {"success": False, "error": "path_traversal"}

        # Resolve tool paths - validate they exist
        black_cmd = shutil.which("black")
        ruff_cmd = shutil.which("ruff")

        if not black_cmd or not ruff_cmd:
            logger.error(
                "Required tools not found: black=%s, ruff=%s", black_cmd, ruff_cmd
            )
            return {"success": False, "error": "tools_not_found"}

        try:
            # black is a trusted dev tool, path resolved with shutil.which and validated
            res_black = subprocess.run(  # nosec B603 B607
                [black_cmd, "--check", abs_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # ruff is a trusted dev tool, path resolved with shutil.which and validated
            res_ruff = subprocess.run(  # nosec B603 B607
                [ruff_cmd, "check", abs_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "success": True,
                "black_check": res_black.returncode == 0,
                "ruff_out": res_ruff.stdout,
            }
        except subprocess.TimeoutExpired:
            logger.warning("Refactor check timed out for %s", path)
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Refactor check failed: %s", e)
            return {"success": False, "error": str(e)}
