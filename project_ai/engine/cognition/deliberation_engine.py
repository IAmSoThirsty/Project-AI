"""
Deliberation Engine
===================

Interprets goals, assembles context, generates and scores plans,
and produces explanations.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..policy.policy_engine import PolicyEngine
    from ..state.state_manager import StateManager
    from ..capabilities.capability_invoker import CapabilityInvoker


class DeliberationEngine:
    """
    Interprets goals, assembles context, generates and scores plans,
    and produces explanations.
    """

    def __init__(
        self,
        policy_engine: "PolicyEngine",
        state_manager: "StateManager",
        capability_invoker: "CapabilityInvoker",
    ):
        self.policy_engine = policy_engine
        self.state_manager = state_manager
        self.capability_invoker = capability_invoker

    def interpret_goal(self, payload: dict, identity_phase: str) -> dict:
        """
        Interpret goal from input payload.
        
        Args:
            payload: Input payload
            identity_phase: Current identity phase
            
        Returns:
            Goal dictionary
        """
        goal_type = payload.get("type", "generic")
        return {
            "type": goal_type,
            "content": payload,
            "identity_phase": identity_phase,
        }

    def assemble_context(self, goal: dict, identity_phase: str) -> dict:
        """
        Assemble context for planning.
        
        Args:
            goal: Goal dictionary
            identity_phase: Current identity phase
            
        Returns:
            Context dictionary
        """
        return {
            "recent_episodes": self.state_manager.get_recent_episodes(limit=5),
            "identity_phase": identity_phase,
        }

    def generate_plan(self, goal: dict, context: dict) -> dict:
        """
        Generate a plan to achieve the goal.
        
        Args:
            goal: Goal to plan for
            context: Planning context
            
        Returns:
            Plan dictionary with steps
        """
        # Use capabilities to analyze goal and context
        goal_analysis = self.capability_invoker.invoke("analyze_goal", {"goal": goal})
        context_summary = self.capability_invoker.invoke(
            "summarize_context", {"context": context}
        )
        risk_eval = self.capability_invoker.invoke(
            "evaluate_risk", {"goal_analysis": goal_analysis}
        )

        steps = []

        # Step 1: policy check
        steps.append(
            {
                "name": "policy_check_step",
                "capability": "policy_check",
                "inputs": {"requested_risk": risk_eval["risk_score"]},
            }
        )

        # Step 2: main handling step
        steps.append(
            {
                "name": "handle_goal_step",
                "capability": "handle_goal_step",
                "inputs": {"goal": goal, "context": context},
            }
        )

        return {
            "goal": goal,
            "context": context,
            "goal_analysis": goal_analysis,
            "context_summary": context_summary,
            "risk_eval": risk_eval,
            "steps": steps,
        }

    def score_plan(self, plan: dict, policy_context: dict) -> dict:
        """
        Score a plan based on risk and policy.
        
        Args:
            plan: Plan to score
            policy_context: Policy context
            
        Returns:
            Scored plan
        """
        # Simple scoring: lower risk = higher score
        risk = plan["risk_eval"]["risk_score"]
        score = max(0.1, 1.0 - (risk * 0.2))
        plan["score"] = score
        plan["policy_mode"] = policy_context["mode"]
        return plan

    def explain_decision(
        self, goal: dict, plan: dict, result: dict, identity_phase: str
    ) -> str:
        """
        Generate explanation for a decision.
        
        Args:
            goal: Goal that was handled
            plan: Plan that was executed
            result: Execution result
            identity_phase: Identity phase during execution
            
        Returns:
            Human-readable explanation
        """
        return (
            f"Handled goal of type '{goal.get('type')}' in phase '{identity_phase}' "
            f"with risk '{plan['risk_eval']['complexity']}' and policy mode "
            f"'{plan.get('policy_mode')}'."
        )


__all__ = ["DeliberationEngine"]
