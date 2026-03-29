# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


"""
Project-AI Core Engine (PACE)
==============================

Orchestrates identity, cognition, workflow, capabilities, agents, state, and IO.
"""

from .agents.agent_coordinator import AgentCoordinator
from .capabilities.capability_invoker import CapabilityInvoker
from .cognition.deliberation_engine import DeliberationEngine
from .identity.identity_manager import IdentityManager
from .io.io_router import IORouter
from .policy.policy_engine import PolicyEngine
from .skills import SkillManager
from .state.state_manager import StateManager
from .workflow.workflow_engine import WorkflowEngine


class PACEEngine:
    """
    Project-AI Core Engine (PACE)
    Orchestrates identity, cognition, workflow, capabilities, agents, state, and IO.
    """

    def __init__(self, config=None):
        self.config = config or {}

        # Core subsystems
        self.identity_manager = IdentityManager(self.config.get("identity", {}))
        self.policy_engine = PolicyEngine(self.identity_manager)
        self.state_manager = StateManager(self.config.get("state", {}))

        # Skills subsystem — identity stays immutable, skills are additive
        self.skill_manager = SkillManager(
            self.state_manager,
            self.config.get("skills", {}),
        )

        self.capability_invoker = CapabilityInvoker(
            self.policy_engine,
            self.state_manager,
            self.config.get("capabilities", {}),
        )

        self.deliberation_engine = DeliberationEngine(
            self.policy_engine,
            self.state_manager,
            self.capability_invoker,
        )

        self.workflow_engine = WorkflowEngine(
            self.policy_engine,
            self.capability_invoker,
            self.state_manager,
        )

        self.agent_coordinator = AgentCoordinator(
            self.policy_engine,
            self.workflow_engine,
            self.capability_invoker,
            self.state_manager,
        )

        self.io_router = IORouter(self)

    # -------- Skills --------

    def acquire_skill(
        self,
        name: str,
        category: str = "general",
        description: str = "",
        knowledge: float = 0.1,
    ) -> dict:
        """Acquire a new skill or deepen existing knowledge."""
        skill = self.skill_manager.acquire(name, category, description, knowledge)
        return skill.to_dict()

    def practice_skill(self, name: str, success_rate: float = 0.5) -> dict:
        """Practice a skill to improve proficiency."""
        return self.skill_manager.practice(name, success_rate)

    def reflect_on_skills(self) -> list[dict]:
        """Run the offline reflection loop — practice weakest skills."""
        return self.skill_manager.reflect()

    def get_skill_inventory(self) -> dict:
        """Get a summary of all skills."""
        return self.skill_manager.get_inventory_summary()

    # -------- Identity / Bonding --------

    def get_identity_phase(self) -> str:
        """Get current identity phase (unbonded/bonded)."""
        return self.identity_manager.get_identity_phase()

    def run_bonding_protocol(self, bonding_input: dict) -> dict:
        """
        Execute bonding protocol, transitioning from unbonded to bonded.
        Returns summary of new identity.
        """
        self.identity_manager.run_bonding_protocol(bonding_input)
        self.policy_engine.refresh_from_identity()
        return self.identity_manager.load_identity()

    # -------- Main runtime entrypoint --------

    def handle_input(self, channel: str, payload: dict) -> dict:
        """
        Main runtime loop entrypoint.

        1) IO receives input
        2) Identity/policy check
        3) Cognitive planning
        4) Workflow construction
        5) Agent assignment and execution
        6) Output and explanation
        7) Episode recording
        """

        identity_phase = self.identity_manager.get_identity_phase()
        policy_context = self.policy_engine.get_policy_context()

        # Cognitive layer
        goal = self.deliberation_engine.interpret_goal(payload, identity_phase)
        context = self.deliberation_engine.assemble_context(goal, identity_phase)
        plan = self.deliberation_engine.generate_plan(goal, context)
        scored_plan = self.deliberation_engine.score_plan(plan, policy_context)

        # Workflow + agents
        workflow = self.workflow_engine.build_workflow(scored_plan, identity_phase)
        self.agent_coordinator.assign_roles(workflow, identity_phase)

        result = self.workflow_engine.execute_workflow(workflow)
        explanation = self.deliberation_engine.explain_decision(
            goal, scored_plan, result, identity_phase
        )

        # State / episode
        self.state_manager.record_episode(
            {
                "identity_phase": identity_phase,
                "goal": goal,
                "plan": scored_plan,
                "result": result,
                "explanation": explanation,
            }
        )

        return {
            "result": result,
            "explanation": explanation,
            "identity_phase": identity_phase,
        }


__all__ = [
    "PACEEngine",
    "IdentityManager",
    "PolicyEngine",
    "StateManager",
    "SkillManager",
    "CapabilityInvoker",
    "DeliberationEngine",
    "WorkflowEngine",
    "AgentCoordinator",
    "IORouter",
]
