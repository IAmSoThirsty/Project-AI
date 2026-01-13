from __future__ import annotations

import logging
from typing import Any

from app.core.access_control import get_access_control

logger = logging.getLogger(__name__)


class ExpertAgent:
    """An expert AI agent with elevated permissions to review audits and approve integrations."""

    def __init__(self, name: str = "expert") -> None:
        self.name = name
        self.access = get_access_control()
        # ensure expert role
        self.access.grant_role(self.name, "expert")

    def export_and_review(self, codex) -> dict[str, Any]:
        # Request audit export from codex
        res = codex.export_audit(requester=self.name)
        if not res.get("success"):
            return res
        # For demonstration, just log path
        logger.info("Expert %s exported audit to %s", self.name, res.get("out"))
        return {"success": True, "out": res.get("out")}
