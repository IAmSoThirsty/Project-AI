"""
cerberus.security.modules.sandbox — Restricted-execution helpers.

Ported from the standalone guard-bot repo (``cerberus-guard-bot``
``src/cerberus/security/modules/sandbox.py``, HEAD ``4d3400c``), completing
the deferral previously documented in ``cerberus.security``.

Honest scope (this is NOT a security boundary):

- :class:`AgentSandbox` applies POSIX resource limits (a no-op on Windows)
  to the **current process** while invoking a callable in-process — it
  constrains resources, it does not isolate. The prior limits are restored
  after the call so later work in the host process is not starved.
- :class:`PluginSandbox` screens plugin source with a regex blocklist and
  executes it under restricted builtins. Blocklists are bypassable by
  construction; treat this as a guard rail against accidents, not against
  a determined adversary.
- :meth:`AgentSandbox.execute_code` (fresh subprocess, minimal environment)
  and :class:`ContainerSandbox` (Docker: no network, read-only rootfs,
  memory/CPU caps; fail-closed when Docker is absent) are the isolation
  forms of this module.

Under the PAB constitution, consequential execution routes exclusively
through governance -> capability -> ``ExecutionGate``; nothing here grants
or replaces that authority.
"""

from __future__ import annotations

import builtins
import importlib
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SandboxConfig:
    """Sandbox configuration."""

    max_memory_mb: int = 512
    max_cpu_time_seconds: int = 30
    max_file_size_mb: int = 10
    max_processes: int = 10
    allowed_syscalls: set[str] | None = None
    network_enabled: bool = False
    filesystem_readonly: bool = True
    temp_dir_only: bool = True


class SandboxViolation(Exception):
    """Raised when sandbox limits or rules are violated."""


class AgentSandbox:
    """Resource-limited execution for agent callables and code snippets."""

    def __init__(self, config: SandboxConfig | None = None) -> None:
        """Initialize with an optional configuration."""
        self.config = config or SandboxConfig()

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a callable in-process under POSIX resource limits.

        No-op limits on Windows; on POSIX the prior limits are restored after
        the call so a sandboxed callable cannot disable later host operations.

        Raises:
            SandboxViolation: When a resource limit is exceeded.
        """
        previous_limits = self._set_resource_limits()
        try:
            return func(*args, **kwargs)
        except MemoryError as exc:
            raise SandboxViolation("Memory limit exceeded") from exc
        except Exception as exc:
            if "CPU time limit exceeded" in str(exc):
                raise SandboxViolation("CPU time limit exceeded") from exc
            raise
        finally:
            self._restore_resource_limits(previous_limits)

    def _set_resource_limits(self) -> dict[int, tuple[int, int]]:
        if sys.platform == "win32":  # Resource limits are POSIX-only.
            return {}
        import resource

        requested = {
            resource.RLIMIT_AS: self.config.max_memory_mb * 1024 * 1024,
            resource.RLIMIT_CPU: self.config.max_cpu_time_seconds,
            resource.RLIMIT_FSIZE: self.config.max_file_size_mb * 1024 * 1024,
            resource.RLIMIT_NPROC: self.config.max_processes,
        }
        previous: dict[int, tuple[int, int]] = {}
        for limit, soft_requested in requested.items():
            soft_current, hard_current = resource.getrlimit(limit)
            previous[limit] = (soft_current, hard_current)
            soft_limit = (
                soft_requested
                if hard_current == resource.RLIM_INFINITY
                else min(soft_requested, hard_current)
            )
            resource.setrlimit(limit, (soft_limit, hard_current))
        return previous

    @staticmethod
    def _restore_resource_limits(previous: dict[int, tuple[int, int]]) -> None:
        if sys.platform == "win32":
            return
        import resource

        for limit, values in previous.items():
            resource.setrlimit(limit, values)

    def execute_code(self, code: str, timeout: int | None = None) -> dict[str, Any]:
        """Execute Python code in a fresh subprocess with a minimal environment.

        Returns a dict with ``stdout``, ``stderr``, ``returncode``, ``success``.

        Raises:
            SandboxViolation: On execution timeout.
        """
        timeout = timeout or self.config.max_cpu_time_seconds

        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = Path(temp_dir) / "script.py"
            code_file.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    capture_output=True,
                    timeout=timeout,
                    cwd=temp_dir,
                    env=self._get_sandboxed_env(),
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise SandboxViolation("Execution timeout") from exc

            return {
                "stdout": result.stdout.decode("utf-8", errors="replace"),
                "stderr": result.stderr.decode("utf-8", errors="replace"),
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }

    def _get_sandboxed_env(self) -> dict[str, str]:
        """Return a minimal environment without loader-injection variables."""
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": "",
            "HOME": tempfile.gettempdir(),
        }
        if sys.platform == "win32":
            # CPython on Windows needs SYSTEMROOT to initialize (os.urandom et al.).
            env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
        for var in ("LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES"):
            env.pop(var, None)
        return env


class PluginSandbox:
    """Restricted-builtins execution for plugin code (guard rail, not isolation)."""

    def __init__(self, config: SandboxConfig | None = None) -> None:
        """Initialize with an optional configuration."""
        self.config = config or SandboxConfig()
        self.allowed_modules: set[str] = {
            "json",
            "re",
            "math",
            "datetime",
            "collections",
            "itertools",
        }
        self.blocked_functions: set[str] = {
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "input",
        }

    def execute_plugin(self, plugin_code: str, plugin_input: Any) -> Any:
        """Validate, then execute plugin code; the plugin must define ``process``.

        Raises:
            SandboxViolation: On blocklist match or a missing ``process`` function.
        """
        self._validate_code(plugin_code)
        restricted_globals = self._get_restricted_globals()
        agent_sandbox = AgentSandbox(self.config)

        def run_plugin() -> Any:
            exec(plugin_code, restricted_globals)
            process = restricted_globals.get("process")
            if not callable(process):
                raise SandboxViolation("Plugin must define 'process' function")
            return process(plugin_input)

        return agent_sandbox.execute(run_plugin)

    def _validate_code(self, code: str) -> None:
        """Reject code matching the blocklist (word-boundary regexes)."""
        # Word-boundary match so 'input' does not trip on 'input_data' and
        # 'exec' does not trip on 'execute'.
        for func in self.blocked_functions:
            if re.search(r"(?<![\w.])" + re.escape(func) + r"(?![\w])", code):
                raise SandboxViolation(f"Blocked function: {func}")

        dangerous_imports = ("os", "sys", "subprocess", "socket", "shutil")
        for module in dangerous_imports:
            if re.search(r"(?:^|;|import\s+)" + re.escape(module) + r"(?!\w)", code):
                raise SandboxViolation(f"Blocked import: {module}")

    def _get_restricted_globals(self) -> dict[str, Any]:
        """Build a globals dict with safe builtins and allowed modules only."""
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
        restricted_builtins = {name: getattr(builtins, name) for name in safe_builtins}
        restricted: dict[str, Any] = {"__builtins__": restricted_builtins}

        for module_name in self.allowed_modules:
            try:
                restricted[module_name] = importlib.import_module(module_name)
            except ImportError:  # pragma: no cover — stdlib modules
                continue
        return restricted

    def add_allowed_module(self, module_name: str) -> None:
        """Add a module to the allowed list."""
        self.allowed_modules.add(module_name)

    def remove_allowed_module(self, module_name: str) -> None:
        """Remove a module from the allowed list."""
        self.allowed_modules.discard(module_name)


class ContainerSandbox:
    """Container-based isolation (requires Docker; fail-closed when absent)."""

    def __init__(
        self,
        image: str = "python:3.12-slim",
        memory_limit: str = "512m",
        cpu_limit: str = "1",
    ) -> None:
        """Initialize with an image and resource caps."""
        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit

    def execute(self, command: list[str], timeout: int = 30) -> dict[str, Any]:
        """Execute a command in an isolated container.

        No network, read-only rootfs, tmpfs ``/tmp``, memory/CPU caps.

        Raises:
            SandboxViolation: On timeout or when Docker is not available.
        """
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--network=none",
            f"--memory={self.memory_limit}",
            f"--cpus={self.cpu_limit}",
            "--read-only",
            "--tmpfs",
            "/tmp",
            self.image,
            *command,
        ]

        try:
            result = subprocess.run(docker_cmd, capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise SandboxViolation("Container execution timeout") from exc
        except FileNotFoundError as exc:
            raise SandboxViolation("Docker not available") from exc

        return {
            "stdout": result.stdout.decode("utf-8", errors="replace"),
            "stderr": result.stderr.decode("utf-8", errors="replace"),
            "returncode": result.returncode,
            "success": result.returncode == 0,
        }


__all__ = [
    "AgentSandbox",
    "ContainerSandbox",
    "PluginSandbox",
    "SandboxConfig",
    "SandboxViolation",
]
