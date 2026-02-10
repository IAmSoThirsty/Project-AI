"""
Capability Invoker
==================

Mediates capability calls, enforcing policy and logging usage.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..policy.policy_engine import PolicyEngine
    from ..state.state_manager import StateManager


class CapabilityInvoker:
    """
    Mediates capability calls, enforcing policy and logging usage.
    """

    def __init__(
        self, policy_engine: "PolicyEngine", state_manager: "StateManager", config: dict
    ):
        self.policy_engine = policy_engine
        self.state_manager = state_manager
        self.registry: dict[str, dict[str, Any]] = self._load_registry(config)

    def _load_registry(self, config: dict) -> dict[str, dict[str, Any]]:
        """
        Load capability registry.

        Args:
            config: Configuration dict

        Returns:
            Registry of capabilities
        """
        registry: dict[str, dict[str, Any]] = {}

        # Core built-in capabilities
        registry["analyze_goal"] = {
            "name": "analyze_goal",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_analyze_goal,
        }
        registry["summarize_context"] = {
            "name": "summarize_context",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_summarize_context,
        }
        registry["evaluate_risk"] = {
            "name": "evaluate_risk",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_evaluate_risk,
        }
        registry["policy_check"] = {
            "name": "policy_check",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_policy_check,
        }
        registry["memory_read"] = {
            "name": "memory_read",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_memory_read,
        }
        registry["memory_write"] = {
            "name": "memory_write",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_memory_write,
        }
        registry["external_stub"] = {
            "name": "external_stub",
            "risk_level": 2,
            "requires_external": True,
            "fn": self._cap_external_stub,
        }
        registry["handle_goal_step"] = {
            "name": "handle_goal_step",
            "risk_level": 1,
            "requires_external": False,
            "fn": self._cap_handle_goal_step,
        }

        # Merge custom capabilities from config
        registry.update(config.get("custom_capabilities", {}))
        return registry

    def invoke(self, capability_name: str, inputs: dict) -> Any:
        """
        Invoke a capability.

        Args:
            capability_name: Name of capability to invoke
            inputs: Input parameters

        Returns:
            Capability result

        Raises:
            ValueError: If capability not found
            PermissionError: If capability not allowed by policy
        """
        cap = self.registry.get(capability_name)
        if not cap:
            raise ValueError(f"Unknown capability: {capability_name}")
        if not self.policy_engine.is_capability_allowed(cap):
            raise PermissionError(
                f"Capability not allowed by policy: {capability_name}"
            )
        fn: Callable[[dict], Any] = cap["fn"]
        return fn(inputs)

    # -------- Built-in capability implementations --------

    def _cap_analyze_goal(self, inputs: dict) -> dict:
        """Analyze a goal and determine complexity."""
        goal = inputs.get("goal", {})
        goal_type = goal.get("type", "unknown")
        content = goal.get("content", {})
        complexity = "low"
        if isinstance(content, dict) and len(str(content)) > 500:
            complexity = "medium"
        if isinstance(content, dict) and len(str(content)) > 2000:
            complexity = "high"
        return {
            "goal_type": goal_type,
            "complexity": complexity,
            "raw": goal,
        }

    def _cap_summarize_context(self, inputs: dict) -> dict:
        """Summarize context information."""
        context = inputs.get("context", {})
        episodes = context.get("recent_episodes", [])
        summary = f"{len(episodes)} recent episodes"
        return {
            "summary": summary,
            "episode_count": len(episodes),
        }

    def _cap_evaluate_risk(self, inputs: dict) -> dict:
        """Evaluate risk based on goal analysis."""
        goal_analysis = inputs.get("goal_analysis", {})
        complexity = goal_analysis.get("complexity", "low")
        risk_score = {"low": 1, "medium": 2, "high": 3}.get(complexity, 1)
        return {
            "risk_score": risk_score,
            "complexity": complexity,
        }

    def _cap_policy_check(self, inputs: dict) -> dict:
        """Check if requested risk level is allowed by policy."""
        policy_context = self.policy_engine.get_policy_context()
        requested_risk = inputs.get("requested_risk", 1)
        allowed = requested_risk <= policy_context["rules"]["max_capability_risk"]
        return {
            "allowed": allowed,
            "requested_risk": requested_risk,
            "policy_mode": policy_context["mode"],
        }

    def _cap_memory_read(self, inputs: dict) -> dict:
        """Read from state memory."""
        key = inputs.get("key")
        value = self.state_manager.load_state(key)
        return {"key": key, "value": value}

    def _cap_memory_write(self, inputs: dict) -> dict:
        """Write to state memory."""
        key = inputs.get("key")
        value = inputs.get("value")
        self.state_manager.save_state(key, value)
        return {"key": key, "written": True}

    def _cap_external_stub(self, inputs: dict) -> dict:
        """Placeholder for external integration (H.323/API/etc.)."""
        target = inputs.get("target", "unknown")
        action = inputs.get("action", "noop")
        return {
            "status": "stub",
            "target": target,
            "action": action,
            "note": "External call not implemented in this stub.",
        }

    def _cap_handle_goal_step(self, inputs: dict) -> dict:
        """Handle a goal step."""
        step = inputs.get("step", {})
        return {
            "handled_step": step.get("name"),
            "status": "ok",
            "echo": step,
        }


__all__ = ["CapabilityInvoker"]
