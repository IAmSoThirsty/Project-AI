"""
Workflow Engine
===============

Builds and executes workflows from plans.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..policy.policy_engine import PolicyEngine
    from ..capabilities.capability_invoker import CapabilityInvoker
    from ..state.state_manager import StateManager


class WorkflowEngine:
    """
    Builds and executes workflows from plans.
    """

    def __init__(
        self,
        policy_engine: "PolicyEngine",
        capability_invoker: "CapabilityInvoker",
        state_manager: "StateManager",
    ):
        self.policy_engine = policy_engine
        self.capability_invoker = capability_invoker
        self.state_manager = state_manager

    def build_workflow(self, plan: dict, identity_phase: str) -> dict:
        """
        Build a workflow from a plan.
        
        Args:
            plan: Plan dictionary
            identity_phase: Current identity phase
            
        Returns:
            Workflow dictionary
        """
        return {
            "identity_phase": identity_phase,
            "plan": plan,
            "steps": plan.get("steps", []),
        }

    def execute_workflow(self, workflow: dict) -> dict:
        """
        Execute a workflow.
        
        Args:
            workflow: Workflow to execute
            
        Returns:
            Execution results
        """
        results = []
        for step in workflow["steps"]:
            cap_name = step.get("capability")
            inputs = step.get("inputs", {})
            try:
                cap_result = self.capability_invoker.invoke(cap_name, inputs)
                results.append(
                    {
                        "step": step["name"],
                        "capability": cap_name,
                        "result": cap_result,
                        "status": "success",
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "step": step["name"],
                        "capability": cap_name,
                        "error": str(e),
                        "status": "error",
                    }
                )
                # In a more advanced version, we could apply compensation logic here.
        return {"workflow_results": results}


__all__ = ["WorkflowEngine"]
