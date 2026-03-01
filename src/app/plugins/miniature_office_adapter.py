"""Adapter to connect Miniature Office to the Project-AI system.

Follows the established adapter pattern (see codex_adapter.py).
Controlled by the ENABLE_MINIATURE_OFFICE environment variable.

Exposes four sub-components:
  - CognitiveIDE:          Full spatial code environment
  - RepairCrew:            Self-healing diagnostics & repair
  - AgentLounge:           Off-duty social space
  - MetaSecurityDepartment: Tier-1 enforcement
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class MiniatureOfficeAdapter:
    """Adapter that connects the Miniature Office to Project-AI.

    Controlled by ``ENABLE_MINIATURE_OFFICE`` env var (default: ``1``).
    When disabled, all accessors return ``None`` and ``initialize()``
    returns ``False``, providing graceful degradation.
    """

    def __init__(self) -> None:
        self._enabled = os.environ.get("ENABLE_MINIATURE_OFFICE", "1") == "1"
        self._initialized = False

        # Sub-component instances (lazy, created on initialize)
        self._repair_crew = None
        self._agent_lounge = None
        self._meta_security = None
        self._cognitive_ide = None

        logger.info(
            "MiniatureOfficeAdapter created (enabled=%s)",
            self._enabled,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self, triumvirate: Any | None = None) -> bool:
        """Initialize all Miniature Office sub-components.

        Args:
            triumvirate: Optional Triumvirate reference for Meta Security.

        Returns:
            True if initialization succeeded, False if disabled or failed.
        """
        if not self._enabled:
            logger.info("MiniatureOffice disabled via ENABLE_MINIATURE_OFFICE=0")
            return False

        try:
            from app.miniature_office.agent_lounge import AgentLounge
            from app.miniature_office.cognitive_ide import CognitiveIDE
            from app.miniature_office.meta_security_dept import MetaSecurityDepartment
            from app.miniature_office.repair_crew import RepairCrew

            self._repair_crew = RepairCrew()
            self._agent_lounge = AgentLounge()
            self._meta_security = MetaSecurityDepartment(triumvirate=triumvirate)
            self._cognitive_ide = CognitiveIDE(
                agent_lounge=self._agent_lounge,
                meta_security=self._meta_security,
            )

            self._initialized = True
            logger.info(
                "✅ MiniatureOffice fully initialized (4 sub-components active)"
            )
            return True

        except Exception as exc:
            logger.error(
                "MiniatureOffice initialization failed: %s", exc, exc_info=True
            )
            self._initialized = False
            return False

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_cognitive_ide(self):
        """Return the CognitiveIDE facade (or None if disabled)."""
        return self._cognitive_ide

    def get_repair_crew(self):
        """Return the RepairCrew facade (or None if disabled)."""
        return self._repair_crew

    def get_agent_lounge(self):
        """Return the AgentLounge facade (or None if disabled)."""
        return self._agent_lounge

    def get_meta_security(self):
        """Return the MetaSecurityDepartment facade (or None if disabled)."""
        return self._meta_security

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Return component health summary."""
        if not self._initialized:
            return {
                "enabled": self._enabled,
                "initialized": False,
                "components": {},
            }

        lounge_state = None
        if self._agent_lounge:
            ls = self._agent_lounge.get_lounge_state()
            lounge_state = {
                "agents_present": len(ls.agents_present),
                "active_discussions": ls.active_discussions,
                "pending_proposals": ls.pending_proposals,
            }

        security_state = None
        if self._meta_security:
            ss = self._meta_security.get_security_state()
            security_state = {
                "alert_level": ss.alert_level.name,
                "active_violations": ss.active_violations,
                "system_integrity": ss.system_integrity,
            }

        return {
            "enabled": self._enabled,
            "initialized": self._initialized,
            "components": {
                "cognitive_ide": self._cognitive_ide is not None,
                "repair_crew": self._repair_crew is not None,
                "agent_lounge": lounge_state,
                "meta_security": security_state,
            },
        }

    # ------------------------------------------------------------------
    # CouncilHub interface
    # ------------------------------------------------------------------

    def receive_message(self, from_id: str, message: str) -> None:
        """CouncilHub message handler — routes to sub-components."""
        logger.info("MiniatureOffice received message from %s: %s", from_id, message)
