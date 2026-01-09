"""Sandboxed Experiment Runner

Runs generated code in a lightweight subprocess sandbox (best-effort).

Security Note: This runner uses subprocess to execute Python code in a sandboxed
environment. Input module paths are validated before execution.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess  # nosec B404 - subprocess usage for sandboxed code execution with validation
from typing import Any

logger = logging.getLogger(__name__)


class SandboxRunner:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def run_in_sandbox(self, module_path: str, timeout: int = 5) -> dict[str, Any]:
        """Run a Python module in a sandboxed subprocess.

        Security: Module path is normalized first, then validated to ensure it exists,
        is a file, is a Python file, and is within the current working directory.
        All validations are performed on the normalized path that will be executed.
        Python executable path is resolved using shutil.which for safety.
        """
        # Normalize and resolve path first to prevent manipulation
        abs_path = os.path.normpath(os.path.abspath(module_path))
        
        # Validate the resolved path is within the current working directory
        # This prevents directory traversal attacks
        cwd = os.path.abspath(os.getcwd())
        try:
            # Check if abs_path is under cwd or is cwd itself
            # Use startswith with os.sep to prevent partial path matches
            if not (abs_path == cwd or abs_path.startswith(cwd + os.sep)):
                logger.error("Path traversal detected: %s not within %s", abs_path, cwd)
                return {"success": False, "error": "path_traversal"}
        except Exception as e:
            # Handle any path comparison errors
            logger.error("Path validation error: %s", e)
            return {"success": False, "error": "path_validation_error"}
        
        # Validate normalized path exists and is a file
        if not os.path.isfile(abs_path):
            logger.error("Invalid module path: %s", abs_path)
            return {"success": False, "error": "invalid_path"}

        # Validate it's a Python file using splitext on the normalized path
        _, ext = os.path.splitext(abs_path)
        if ext.lower() != '.py':
            logger.error("Module path must be a Python file: %s", abs_path)
            return {"success": False, "error": "not_python_file"}
        
        # Get the absolute path to the Python executable
        # Check for python3 first as it's more common on modern systems
        python_cmd = shutil.which("python3")
        if not python_cmd:
            python_cmd = shutil.which("python")
        
        if not python_cmd:
            logger.error("Python executable not found in PATH")
            return {"success": False, "error": "python_not_found"}

        try:
            # Python path resolved with shutil.which, module path validated
            res = subprocess.run(  # nosec B603
                [python_cmd, abs_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            logger.exception("Sandbox run failed: %s", e)
            return {"success": False, "error": str(e)}
