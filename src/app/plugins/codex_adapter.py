"""Adapter to connect Codex Deus Maximus to the Project-AI system.

This adapter registers Codex as an approval listener on the LearningRequestManager
so that when a request is approved, Codex will generate an implementation and
optionally integrate it into the project and request Cerberus style rotation.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.codex_deus_maximus import create_codex
from app.core.ai_systems import LearningRequestManager
from app.core.council_hub import get_council_hub

logger = logging.getLogger(__name__)


class CodexAdapter:
    def __init__(self):
        self.codex = create_codex()
        # Register Codex as a smaller agent shorthand in the CouncilHub
        hub = get_council_hub()
        hub.register_agent("codex", self)
        # learning manager will be set when register_with_manager is called
        self.learning_manager = None

    def register_with_manager(self, manager: LearningRequestManager) -> None:
        """Register Codex as a listener for approved learning requests."""
        manager.register_approval_listener(self._on_approved)
        # Keep reference to query pending/black vault
        self.learning_manager = manager
        self.codex.learning_manager = manager
        logger.info("CodexAdapter registered with LearningRequestManager")

    def _on_approved(self, req_id: str, request: dict[str, Any]) -> None:
        """Handle approved request: implement and integrate."""
        try:
            topic = request.get("topic", "automation")
            desc = request.get("description", "")
            # Only implement and integrate approved requests
            result = self.codex.implement_request(req_id, topic, desc)
            logger.info("Codex implemented request %s: %s", req_id, result.get("path"))

            if result.get("success"):
                # Automatically integrate approved artifacts immediately
                try:
                    report = self.codex.integrate_approved()
                    logger.info("Codex integration report: %s", report)
                except Exception:
                    logger.exception(
                        "Codex failed to auto-integrate approved request %s", req_id
                    )

            # Coordinate with Cerberus for style rotation (best-effort)
            coord = self.codex.coordinate_with_cerberus()
            logger.info("Cerberus coordination result: %s", coord)
        except Exception:
            logger.exception(
                "CodexAdapter failed to process approved request %s", req_id
            )

    def receive_message(self, from_id: str, message: str) -> None:
        # Codex may log or process messages from the hub
        logger.info("Codex received message from %s: %s", from_id, message)
