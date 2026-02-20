"""Adapter to expose Cerberus Guard Bot to Project-AI.

This module provides a thin wrapper around the Cerberus HubCoordinator so the
main application can initialize and use the guard bot safely.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class CerberusAdapter:
    """Thin adapter for Cerberus HubCoordinator.

    Usage:
        adapter = CerberusAdapter(enabled=True)
        adapter.initialize()
        result = adapter.analyze("some content")
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and os.getenv("ENABLE_CERBERUS", "1") != "0"
        self._hub = None

    def initialize(self) -> bool:
        """Initialize Cerberus if enabled. Returns True if ready."""
        if not self.enabled:
            logger.info("Cerberus adapter disabled by configuration")
            return False

        try:
            # Configure Cerberus logging if available
            try:
                from cerberus.logging_config import configure_logging

                configure_logging()
            except Exception:
                logger.debug("Cerberus logging_config not available or failed to configure")

            from cerberus.hub import HubCoordinator

            self._hub = HubCoordinator()
            logger.info("Cerberus hub initialized", guardian_count=self._hub.guardian_count)
            return True
        except Exception as exc:  # pragma: no cover - runtime integration
            logger.exception("Failed to initialize Cerberus: %s", exc)
            self._hub = None
            return False

    def analyze(self, content: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze content via Cerberus hub. If not enabled, return a permissive result."""
        if not self.enabled or self._hub is None:
            return {
                "decision": "allowed",
                "is_safe": True,
                "guardian_count": 0,
                "results": [],
            }
        return self._hub.analyze(content, context)

    def get_status(self) -> dict[str, Any]:
        """Return hub status or a disabled placeholder."""
        if not self.enabled or self._hub is None:
            return {"hub_status": "disabled", "guardian_count": 0}
        return self._hub.get_status()
