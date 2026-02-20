from __future__ import annotations

import logging
from typing import Any

from app.core.access_control import get_access_control
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class ExpertAgent(KernelRoutedAgent):
    """An expert AI agent with elevated permissions to review audits and approve integrations.

    All actions are routed through CognitionKernel for governance, memory, and reflection.
    """

    def __init__(self, name: str = "expert", kernel: CognitionKernel | None = None) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",  # Expert actions have moderate risk
        )

        self.name = name
        self.access = get_access_control()
        # ensure expert role
        self.access.grant_role(self.name, "expert")

    def export_and_review(self, codex) -> dict[str, Any]:
        """Export and review audit from codex.

        This method is routed through CognitionKernel for governance and tracking.
        """
        # Route through kernel for governance approval (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self._do_export_and_review,
            action_name=f"ExpertAgent.export_and_review[{self.name}]",
            action_args=(codex,),
            requires_approval=True,  # Expert actions require approval
            risk_level="medium",
            metadata={"agent_name": self.name, "operation": "export_and_review"},
        )

    def _do_export_and_review(self, codex) -> dict[str, Any]:
        """Internal implementation of export and review.

        This is the actual implementation that gets executed after kernel approval.
        """
        # Request audit export from codex
        res = codex.export_audit(requester=self.name)
        if not res.get("success"):
            return res
        # For demonstration, just log path
        logger.info("Expert %s exported audit to %s", self.name, res.get("out"))
        return {"success": True, "out": res.get("out")}
