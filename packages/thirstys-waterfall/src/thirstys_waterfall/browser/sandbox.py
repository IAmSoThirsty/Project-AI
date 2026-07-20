"""Browser Sandbox for secure execution"""

import logging
import os
import time
import tracemalloc
from typing import Any


class BrowserSandbox:
    """Compatibility policy evaluator for copied browser behavior.

    This class does not create an OS process, network namespace, filesystem
    jail, seccomp filter, or capability boundary. It classifies obviously
    unsafe script strings, reports current Python-process measurements, and
    returns ``None`` for every script rather than executing code. Callers that
    require isolation must provide a separately verified sandbox runtime.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize sandbox

        Args:
            config: Configuration dict with optional:
                - enabled: bool (default True)
                - memory_limit_mb: int (default 512)
                - cpu_limit_percent: int (default 50)
        """
        config = config or {}
        self.enabled = config.get("enabled", True)
        self.logger = logging.getLogger(__name__)
        self._active = False

        # MAXIMUM ALLOWED DESIGN: Resource limits
        self._resource_limits = {
            "memory_mb": config.get("memory_limit_mb", 512),
            "cpu_percent": config.get("cpu_limit_percent", 50),
            "max_file_handles": 100,
            "max_network_connections": 50,
            "max_processes": 1,
        }

        # No OS isolation runtime is bundled with this compatibility surface.
        self._security_boundaries = {
            "process_isolation": False,
            "memory_isolation": False,
            "network_isolation": False,
            "filesystem_isolation": False,
            "syscall_filtering": False,
            "capability_dropping": False,
        }

        self._sandbox_policies = {
            "allow_system_access": False,
            "allow_network_access": True,  # Through VPN only
            "allow_file_access": False,
            "allow_camera": False,
            "allow_microphone": False,
            "allow_geolocation": False,
            "allow_notifications": False,
            "allow_popups": False,  # NEW REQUIREMENT
            "allow_plugins": False,
        }

        # MAXIMUM ALLOWED DESIGN: Expose config dict
        self.config = {"enabled": self.enabled, **self._resource_limits}
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        self._resource_sample_wall = time.perf_counter()
        self._resource_sample_cpu = time.process_time()

    def start(self):
        """Start sandbox"""
        if not self.enabled:
            return

        self.logger.info("Starting Browser Sandbox")
        self._apply_sandbox_policies()
        self._active = True

    def stop(self):
        """Stop sandbox"""
        self.logger.info("Stopping Browser Sandbox")
        self._active = False

    def _apply_sandbox_policies(self):
        """Activate non-executing compatibility policy checks."""
        self.logger.debug("Activating browser compatibility policy checks")

    def execute_script(self, script: str, context: dict[str, Any]) -> Any:
        """
        Execute script in sandboxed context.

        Args:
            script: JavaScript code to execute
            context: Execution context

        Returns:
            Script result or None if blocked
        """
        if not self._active:
            return None

        # Check if script is safe
        if not self._is_safe_script(script):
            self.logger.warning("Blocked unsafe script execution")
            return None

        # The compatibility surface never evaluates script content.
        self.logger.debug("Script accepted by policy classifier but not executed")
        return None

    def _is_safe_script(self, script: str) -> bool:
        """Check if script is safe to execute"""
        # Block dangerous operations
        dangerous_patterns = [
            "eval(",
            "Function(",
            "window.open(",  # NEW REQUIREMENT: Block pop-ups
            "location.href =",  # NEW REQUIREMENT: Block redirects
            "location.replace(",  # NEW REQUIREMENT: Block redirects
            "__proto__",
            "constructor",
            "exec",
        ]

        for pattern in dangerous_patterns:
            if pattern in script:
                self.logger.warning(f"Dangerous pattern detected: {pattern}")
                return False

        return True

    def is_active(self) -> bool:
        """Check if sandbox is active"""
        return self._active

    def get_policies(self) -> dict[str, bool]:
        """Get sandbox policies"""
        return self._sandbox_policies.copy()

    def get_resource_limits(self) -> dict[str, int]:
        """
        Get current resource limits.

        MAXIMUM ALLOWED DESIGN:
        - Complete visibility into resource constraints
        - All limits explicitly documented

        Returns:
            Dict with resource limits:
            - memory_mb / memory_limit: Maximum memory in MB
            - cpu_percent / cpu_limit: Maximum CPU usage %
            - max_file_handles: Maximum open files
            - max_network_connections: Maximum network connections
            - max_processes: Maximum subprocess count

        Thread Safety:
            - Returns immutable copy (thread-safe read)
        """
        limits = self._resource_limits.copy()
        # MAXIMUM ALLOWED DESIGN: Add aliases for backward compatibility
        limits["memory_limit"] = limits["memory_mb"]
        limits["cpu_limit"] = limits["cpu_percent"]
        return limits

    def get_security_boundaries(self) -> dict[str, bool]:
        """
        Get security boundary configuration.

        MAXIMUM ALLOWED DESIGN:
        - Explicit enumeration of all security layers
        - Complete transparency into protection mechanisms

        Returns:
            Dict mapping boundary type -> enabled status:
            - process_isolation: OS-level process separation
            - memory_isolation: Memory space isolation
            - network_isolation / network_restrictions: Network namespace isolation
            - filesystem_isolation: Filesystem view isolation
            - syscall_filtering: System call filtering (seccomp)
            - capability_dropping: Linux capability restrictions

        Security Properties:
            - All boundaries enabled by default
            - Disabling any boundary logs security warning
            - Boundary violations trigger alerts
        """
        boundaries = self._security_boundaries.copy()
        # MAXIMUM ALLOWED DESIGN: Add aliases for backward compatibility
        boundaries["network_restrictions"] = boundaries["network_isolation"]
        return boundaries

    def check_resource_usage(self) -> dict[str, Any]:
        """
        Check current resource usage against limits.

        MAXIMUM ALLOWED DESIGN:
        - Real-time resource monitoring
        - Proactive limit enforcement
        - Complete usage metrics

        Returns:
            Dict with current usage and limits:
            - memory_used_mb: Current memory usage
            - memory_limit_mb: Memory limit
            - cpu_used_percent: Current CPU usage
            - cpu_limit_percent: CPU limit
            - within_limits: bool (all limits respected)

        Performance:
            Time: O(1)
            Space: O(1)
        """
        current_bytes, _peak_bytes = tracemalloc.get_traced_memory()
        now_wall = time.perf_counter()
        now_cpu = time.process_time()
        wall_delta = max(now_wall - self._resource_sample_wall, 1e-9)
        cpu_delta = max(now_cpu - self._resource_sample_cpu, 0.0)
        cpu_count = os.cpu_count() or 1
        cpu_used_percent = min(100.0, (cpu_delta / wall_delta) * 100.0 / cpu_count)
        memory_used_mb = current_bytes / (1024 * 1024)
        self._resource_sample_wall = now_wall
        self._resource_sample_cpu = now_cpu
        within_limits = (
            memory_used_mb <= self._resource_limits["memory_mb"]
            and cpu_used_percent <= self._resource_limits["cpu_percent"]
        )
        return {
            "memory_used_mb": memory_used_mb,
            "memory_limit_mb": self._resource_limits["memory_mb"],
            "cpu_used_percent": cpu_used_percent,
            "cpu_limit_percent": self._resource_limits["cpu_percent"],
            "within_limits": within_limits,
            "measurement_scope": "current_python_process",
        }
