# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / sandbox.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / sandbox.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Sandbox Module

Agent and plugin encapsulation and isolation with:
- Restricted execution environments
- Resource limits
- Capability controls
- Process isolation
"""

import os
import resource
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SandboxConfig:
    """Sandbox configuration"""

    max_memory_mb: int = 512  # Maximum memory in MB
    max_cpu_time_seconds: int = 30  # Maximum CPU time
    max_file_size_mb: int = 10  # Maximum file size
    max_processes: int = 10  # Maximum number of processes
    allowed_syscalls: set[str] | None = None  # Allowed system calls
    network_enabled: bool = False  # Allow network access
    filesystem_readonly: bool = True  # Read-only filesystem
    temp_dir_only: bool = True  # Only access temp directory


class SandboxViolation(Exception):
    """Exception raised when sandbox limits are violated"""

    pass


class AgentSandbox:
    """
    Sandbox for agent execution with resource limits
    """

    def __init__(self, config: SandboxConfig | None = None):
        """
        Initialize agent sandbox

        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()

    def execute(
        self, func: Callable, *args, **kwargs
    ) -> Any:
        """
        Execute function in sandbox

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function return value

        Raises:
            SandboxViolation: If sandbox limits are violated
        """
        # Set resource limits before execution
        self._set_resource_limits()

        try:
            result = func(*args, **kwargs)
            return result
        except MemoryError:
            raise SandboxViolation("Memory limit exceeded")
        except Exception as e:
            if "CPU time limit exceeded" in str(e):
                raise SandboxViolation("CPU time limit exceeded")
            raise

    def _set_resource_limits(self):
        """Set resource limits using resource module"""
        if sys.platform != "win32":  # Resource limits not supported on Windows
            # Set memory limit
            max_memory_bytes = self.config.max_memory_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes)
            )

            # Set CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.config.max_cpu_time_seconds, self.config.max_cpu_time_seconds),
            )

            # Set file size limit
            max_file_bytes = self.config.max_file_size_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_FSIZE, (max_file_bytes, max_file_bytes)
            )

            # Set process limit
            resource.setrlimit(
                resource.RLIMIT_NPROC,
                (self.config.max_processes, self.config.max_processes),
            )

    def execute_code(self, code: str, timeout: int | None = None) -> dict:
        """
        Execute Python code in sandbox

        Args:
            code: Python code to execute
            timeout: Timeout in seconds

        Returns:
            Dictionary with stdout, stderr, and return code
        """
        timeout = timeout or self.config.max_cpu_time_seconds

        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to file
            code_file = Path(temp_dir) / "script.py"
            code_file.write_text(code)

            # Execute in subprocess with limits
            try:
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    timeout=timeout,
                    cwd=temp_dir,
                    env=self._get_sandboxed_env(),
                )

                return {
                    "stdout": result.stdout.decode("utf-8"),
                    "stderr": result.stderr.decode("utf-8"),
                    "returncode": result.returncode,
                    "success": result.returncode == 0,
                }
            except subprocess.TimeoutExpired:
                raise SandboxViolation("Execution timeout")

    def _get_sandboxed_env(self) -> dict[str, str]:
        """Get sandboxed environment variables"""
        # Start with minimal environment
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": "",
            "HOME": tempfile.gettempdir(),
        }

        # Remove potentially dangerous variables
        dangerous_vars = [
            "LD_PRELOAD",
            "LD_LIBRARY_PATH",
            "DYLD_INSERT_LIBRARIES",
        ]

        for var in dangerous_vars:
            env.pop(var, None)

        return env


class PluginSandbox:
    """
    Sandbox for plugin execution with capability controls
    """

    def __init__(self, config: SandboxConfig | None = None):
        """
        Initialize plugin sandbox

        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()
        self.allowed_modules: set[str] = {
            "json",
            "re",
            "math",
            "datetime",
            "collections",
            "itertools",
        }
        self.blocked_functions = {
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "input",
        }

    def execute_plugin(self, plugin_code: str, plugin_input: Any) -> Any:
        """
        Execute plugin code with input

        Args:
            plugin_code: Plugin Python code
            plugin_input: Input data for plugin

        Returns:
            Plugin output

        Raises:
            SandboxViolation: If plugin violates sandbox rules
        """
        # Validate plugin code
        self._validate_code(plugin_code)

        # Create restricted globals
        restricted_globals = self._get_restricted_globals()

        # Execute plugin
        agent_sandbox = AgentSandbox(self.config)

        def run_plugin():
            exec(plugin_code, restricted_globals)
            if "process" not in restricted_globals:
                raise SandboxViolation("Plugin must define 'process' function")

            return restricted_globals["process"](plugin_input)

        return agent_sandbox.execute(run_plugin)

    def _validate_code(self, code: str):
        """Validate plugin code for dangerous patterns"""
        # Check for blocked functions
        for func in self.blocked_functions:
            if func in code:
                raise SandboxViolation(f"Blocked function: {func}")

        # Check for dangerous imports
        dangerous_imports = ["os", "sys", "subprocess", "socket", "shutil"]
        for module in dangerous_imports:
            if f"import {module}" in code or f"from {module}" in code:
                raise SandboxViolation(f"Blocked import: {module}")

    def _get_restricted_globals(self) -> dict:
        """Get restricted global namespace for plugin execution"""
        # Start with empty globals
        restricted = {"__builtins__": {}}

        # Add safe builtins
        safe_builtins = {
            "abs",
            "all",
            "any",
            "bool",
            "dict",
            "enumerate",
            "filter",
            "float",
            "int",
            "len",
            "list",
            "map",
            "max",
            "min",
            "range",
            "reversed",
            "round",
            "set",
            "sorted",
            "str",
            "sum",
            "tuple",
            "zip",
        }

        for name in safe_builtins:
            restricted["__builtins__"][name] = getattr(__builtins__, name)

        # Add allowed modules
        import importlib

        for module_name in self.allowed_modules:
            try:
                restricted[module_name] = importlib.import_module(module_name)
            except ImportError:
                pass

        return restricted

    def add_allowed_module(self, module_name: str):
        """Add module to allowed list"""
        self.allowed_modules.add(module_name)

    def remove_allowed_module(self, module_name: str):
        """Remove module from allowed list"""
        self.allowed_modules.discard(module_name)


class ContainerSandbox:
    """
    Container-based sandbox (requires Docker/Podman)
    """

    def __init__(
        self,
        image: str = "python:3.10-slim",
        memory_limit: str = "512m",
        cpu_limit: str = "1",
    ):
        """
        Initialize container sandbox

        Args:
            image: Container image to use
            memory_limit: Memory limit (e.g., "512m")
            cpu_limit: CPU limit (e.g., "1" for 1 core)
        """
        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit

    def execute(self, command: list[str], timeout: int = 30) -> dict:
        """
        Execute command in container

        Args:
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            Dictionary with stdout, stderr, and return code
        """
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--network=none",  # No network
            f"--memory={self.memory_limit}",
            f"--cpus={self.cpu_limit}",
            "--read-only",  # Read-only filesystem
            "--tmpfs",
            "/tmp",  # Writable temp
            self.image,
        ] + command

        try:
            result = subprocess.run(
                docker_cmd, capture_output=True, timeout=timeout
            )

            return {
                "stdout": result.stdout.decode("utf-8"),
                "stderr": result.stderr.decode("utf-8"),
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            raise SandboxViolation("Container execution timeout")
        except FileNotFoundError:
            raise SandboxViolation("Docker not available")
