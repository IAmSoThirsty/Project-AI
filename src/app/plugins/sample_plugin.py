"""Sample marketplace plugin demonstrating metadata and safety checks."""

from __future__ import annotations

import logging
from typing import Any

from app.core.ai_systems import FourLaws, Plugin

logger = logging.getLogger(__name__)

try:
    from app.core.observability import emit_event
except ImportError:
    def emit_event(event_name: str, metadata: dict[str, Any] | None = None) -> None:
        logger.debug("Observability stub for %s: %s", event_name, metadata)


class MarketplaceSamplePlugin(Plugin):
    """A minimal plugin that shows how to validate actions against the Four Laws."""

    def __init__(self) -> None:
        super().__init__(name="marketplace_sample_plugin", version="0.1.0")

    def _report_event(self, context: dict[str, Any]) -> None:
        emit_event(
            "plugin.marketplace_sample.initialize",
            {"name": self.name, "version": self.version, "context": context},
        )

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Validate context, emit telemetry, and enable the plugin if allowed."""

        context = context or {}
        allowed, reason = FourLaws.validate_action(
            "Initialize marketplace sample plugin",
            context,
        )
        logger.info("Sample plugin validation result: %s", reason)
        if not allowed:
            emit_event("plugin.marketplace_sample.blocked", {"reason": reason})
            return False

        if context.get("requires_explicit_order") and not context.get("is_user_order"):
            emit_event(
                "plugin.marketplace_sample.blocked",
                {"reason": "requires_explicit_order without user order"},
            )
            return False

        self.enabled = True
        self._report_event(context)
        return True


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point used by loaders that expect a plain function."""

    return MarketplaceSamplePlugin().initialize(context)


__all__ = ["MarketplaceSamplePlugin", "initialize"]
