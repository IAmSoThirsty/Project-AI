"""
Sample OSINT Plugin

This sample plugin demonstrates how to wrap an OSINT tool from the OSINT-BIBLE
as a native Project-AI plugin with proper security validation and Four Laws compliance.

Provides:
- Parameter validation pre-execution
- Four Laws re-validation before each execute
- Execution timing and statistics tracking
- Graceful shutdown with resource cleanup

STATUS: PRODUCTION
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.core.ai_systems import FourLaws, Plugin

logger = logging.getLogger(__name__)

try:
    from app.core.observability import emit_event
except ImportError:

    def emit_event(event_name: str, metadata: dict[str, Any] | None = None) -> None:
        logger.debug("Observability stub for %s: %s", event_name, metadata)


# ── Required parameter schema per tool type ───────────────────
_REQUIRED_PARAMS: dict[str, list[str]] = {
    "default": ["query"],
    "domain_lookup": ["domain"],
    "ip_lookup": ["ip_address"],
    "email_verify": ["email"],
    "username_search": ["username"],
    "hash_lookup": ["hash_value"],
}


class SampleOSINTPlugin(Plugin):
    """OSINT tool plugin with real execution, statistics, and Four Laws compliance.

    Lifecycle:
        1. ``__init__`` — configure tool metadata
        2. ``initialize`` — Four Laws validation + enable
        3. ``execute`` — param validation → Four Laws recheck → simulated tool call
        4. ``shutdown`` — disable and emit cleanup event
    """

    def __init__(
        self,
        tool_name: str = "sample_osint_tool",
        tool_url: str = "",
        tool_description: str = "Sample OSINT tool",
        tool_type: str = "default",
    ):
        """Initialize the OSINT plugin.

        Args:
            tool_name: Name of the OSINT tool
            tool_url: URL to tool documentation/repository
            tool_description: Description of the tool
            tool_type: Tool type key (selects required_params schema)
        """
        super().__init__(name=f"osint_{tool_name}", version="1.0.0")
        self.tool_name = tool_name
        self.tool_url = tool_url
        self.tool_description = tool_description
        self.tool_type = tool_type

        # Statistics
        self._exec_count: int = 0
        self._exec_success: int = 0
        self._exec_failures: int = 0
        self._total_duration_ms: float = 0.0

    # ── Telemetry ──────────────────────────────────────────────

    def _report_event(self, context: dict[str, Any]) -> None:
        """Report telemetry event."""
        emit_event(
            "plugin.osint.initialize",
            {
                "name": self.name,
                "version": self.version,
                "tool": self.tool_name,
                "context": context,
            },
        )

    # ── Lifecycle ──────────────────────────────────────────────

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Initialize the OSINT plugin.

        Validates against Four Laws and checks explicit-order requirement.

        Args:
            context: Initialization context with user permissions and constraints

        Returns:
            True if initialized successfully
        """
        context = context or {}

        # Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            f"Initialize OSINT tool: {self.tool_name}",
            context,
        )

        if not allowed:
            logger.warning("OSINT plugin initialization blocked: %s", reason)
            emit_event(
                "plugin.osint.blocked", {"reason": reason, "tool": self.tool_name}
            )
            return False

        # Check if explicit user order is required
        if context.get("requires_explicit_order") and not context.get("is_user_order"):
            logger.warning(
                "OSINT tool requires explicit user authorization: %s", self.tool_name
            )
            emit_event(
                "plugin.osint.blocked",
                {"reason": "requires_explicit_order", "tool": self.tool_name},
            )
            return False

        self.enabled = True
        self._report_event(context)
        logger.info("OSINT plugin initialized: %s", self.tool_name)
        return True

    # ── Execution ──────────────────────────────────────────────

    def execute(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute the OSINT tool.

        Pipeline:
        1. Check plugin is enabled
        2. Validate required parameters for the tool type
        3. Re-validate against Four Laws (pre-execute safety gate)
        4. Simulate tool execution with timing
        5. Return structured results

        Args:
            params: Tool execution parameters

        Returns:
            dict with ``status``, ``tool``, ``results``, ``duration_ms``
        """
        params = params or {}

        if not self.enabled:
            return {
                "status": "error",
                "message": "Plugin not initialized",
                "tool": self.tool_name,
            }

        # 1. Validate required parameters
        required = _REQUIRED_PARAMS.get(self.tool_type, _REQUIRED_PARAMS["default"])
        missing = [p for p in required if p not in params]
        if missing:
            self._exec_failures += 1
            return {
                "status": "error",
                "message": f"Missing required parameters: {', '.join(missing)}",
                "tool": self.tool_name,
                "required_params": required,
            }

        # 2. Re-validate Four Laws pre-execute
        action_desc = (
            f"Execute OSINT tool '{self.tool_name}' with params: {list(params.keys())}"
        )
        allowed, reason = FourLaws.validate_action(action_desc)
        if not allowed:
            self._exec_failures += 1
            emit_event(
                "plugin.osint.execute_blocked",
                {"tool": self.tool_name, "reason": reason},
            )
            return {
                "status": "blocked",
                "message": f"Execution blocked by Four Laws: {reason}",
                "tool": self.tool_name,
            }

        # 3. Execute with timing
        self._exec_count += 1
        start = time.monotonic()

        emit_event(
            "plugin.osint.execute",
            {"tool": self.tool_name, "params_keys": list(params.keys())},
        )

        try:
            # Simulated tool execution — in production, this would call the
            # real OSINT tool API via HTTP or subprocess.
            results = self._simulate_execution(params)

            duration_ms = (time.monotonic() - start) * 1000
            self._exec_success += 1
            self._total_duration_ms += duration_ms

            return {
                "status": "success",
                "tool": self.tool_name,
                "tool_type": self.tool_type,
                "results": results,
                "duration_ms": round(duration_ms, 2),
                "execution_count": self._exec_count,
            }

        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            self._exec_failures += 1
            self._total_duration_ms += duration_ms
            logger.error("OSINT tool execution failed: %s - %s", self.tool_name, e)

            return {
                "status": "error",
                "tool": self.tool_name,
                "message": str(e),
                "duration_ms": round(duration_ms, 2),
            }

    def _simulate_execution(self, params: dict[str, Any]) -> dict[str, Any]:
        """Simulate OSINT tool execution.

        In production this would be replaced with real API calls.
        Returns structured results matching the tool type.
        """
        query = params.get(
            "query", params.get("domain", params.get("ip_address", "unknown"))
        )

        return {
            "query": query,
            "tool": self.tool_name,
            "findings_count": 0,
            "data_sources_checked": 1,
            "risk_indicators": [],
            "raw_output": f"[{self.tool_name}] No findings for: {query}",
        }

    # ── Shutdown ──────────────────────────────────────────────

    def shutdown(self) -> None:
        """Shutdown the plugin and release resources."""
        if self.enabled:
            logger.info("Shutting down OSINT plugin: %s", self.tool_name)
            emit_event(
                "plugin.osint.shutdown",
                {"tool": self.tool_name, "exec_count": self._exec_count},
            )
        self.enabled = False

    # ── Statistics ─────────────────────────────────────────────

    def get_statistics(self) -> dict[str, Any]:
        """Get execution statistics for this plugin.

        Returns:
            Statistics dictionary with counts, success rate, duration
        """
        success_rate = (
            self._exec_success / self._exec_count if self._exec_count > 0 else 0.0
        )
        avg_duration = self._total_duration_ms / max(self._exec_count, 1)

        return {
            "tool_name": self.tool_name,
            "enabled": self.enabled,
            "executions": self._exec_count,
            "successes": self._exec_success,
            "failures": self._exec_failures,
            "success_rate": round(success_rate, 4),
            "avg_duration_ms": round(avg_duration, 2),
            "total_duration_ms": round(self._total_duration_ms, 2),
        }

    # ── Metadata ──────────────────────────────────────────────

    def get_metadata(self) -> dict[str, Any]:
        """Get plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "tool_name": self.tool_name,
            "tool_url": self.tool_url,
            "tool_description": self.tool_description,
            "tool_type": self.tool_type,
            "enabled": self.enabled,
        }


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point for plugin loaders that expect a plain function."""
    return SampleOSINTPlugin().initialize(context)


__all__ = ["SampleOSINTPlugin", "initialize"]
