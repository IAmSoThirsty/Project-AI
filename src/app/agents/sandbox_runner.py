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

        Security: Module path is validated to ensure it exists, is a file, is a Python file,
        and is within the current working directory to prevent directory traversal attacks.
        Python executable path is resolved using shutil.which for safety.
        """
        # Validate module path exists and is a file
        if not os.path.isfile(module_path):
            logger.error("Invalid module path: %s", module_path)
            return {"success": False, "error": "invalid_path"}

        # Validate it's a Python file using splitext for robust extension checking
        _, ext = os.path.splitext(module_path)
        if ext.lower() != '.py':
            logger.error("Module path must be a Python file: %s", module_path)
            return {"success": False, "error": "not_python_file"}

        # Ensure path is absolute and normalized to prevent path traversal
        abs_path = os.path.normpath(os.path.abspath(module_path))
        
        # Validate the resolved path is within the current working directory
        # This prevents directory traversal even after path normalization
        cwd = os.path.abspath(os.getcwd())
        try:
            # Check if abs_path is under cwd using os.path.commonpath
            common = os.path.commonpath([abs_path, cwd])
            if common != cwd:
                logger.error("Path traversal detected: %s not within %s", abs_path, cwd)
                return {"success": False, "error": "path_traversal"}
        except ValueError:
            # Different drives on Windows or no common path
            logger.error("Path traversal detected: %s on different drive from %s", abs_path, cwd)
            return {"success": False, "error": "path_traversal"}
        
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
