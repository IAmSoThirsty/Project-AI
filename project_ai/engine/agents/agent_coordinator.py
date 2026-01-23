"""
Agent Coordinator
=================

Coordinates agents (planner, executor, reviewer, auditor, communicator).
For now, this is a thin layer that tags workflows with roles.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..policy.policy_engine import PolicyEngine
    from ..workflow.workflow_engine import WorkflowEngine
    from ..capabilities.capability_invoker import CapabilityInvoker
    from ..state.state_manager import StateManager


class AgentCoordinator:
    """
    Coordinates agents (planner, executor, reviewer, auditor, communicator).
    For now, this is a thin layer that tags workflows with roles.
    """

    def __init__(
        self,
        policy_engine: "PolicyEngine",
        workflow_engine: "WorkflowEngine",
        capability_invoker: "CapabilityInvoker",
        state_manager: "StateManager",
    ):
        self.policy_engine = policy_engine
        self.workflow_engine = workflow_engine
        self.capability_invoker = capability_invoker
        self.state_manager = state_manager

    def assign_roles(self, workflow: dict, identity_phase: str) -> None:
        """
        Assign agent roles to workflow.
        
        This is where you could route steps to different logical agents.
        
        Args:
            workflow: Workflow to assign roles to
            identity_phase: Current identity phase
        """
        workflow["assigned_roles"] = {
            "planner": "PlannerAgent",
            "executor": "ExecutorAgent",
            "reviewer": "ReviewerAgent",
            "auditor": "AuditorAgent",
            "communicator": "CommunicatorAgent",
        }


__all__ = ["AgentCoordinator"]
