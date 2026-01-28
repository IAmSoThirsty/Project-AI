"""
Policy Engine
=============

Enforces hard constraints, soft preferences, and context rules.
Aware of identity phase (unbonded vs bonded).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..identity.identity_manager import IdentityManager


class PolicyEngine:
    """
    Enforces hard constraints, soft preferences, and context rules.
    Aware of identity phase (unbonded vs bonded).
    """

    def __init__(self, identity_manager: "IdentityManager"):
        self.identity_manager = identity_manager
        self.policy_mode = "bootstrap"
        self.policies = {
            "bootstrap": {
                "allow_high_risk": False,
                "max_capability_risk": 1,
                "allow_external_calls": False,
            },
            "bonded": {
                "allow_high_risk": True,
                "max_capability_risk": 5,
                "allow_external_calls": True,
            },
        }

    def refresh_from_identity(self) -> None:
        """
        Refresh policy mode based on current identity phase.
        """
        phase = self.identity_manager.get_identity_phase()
        if phase == "unbonded":
            self.policy_mode = "bootstrap"
        else:
            self.policy_mode = "bonded"

    def get_policy_context(self) -> dict:
        """
        Get current policy context.

        Returns:
            Policy context including phase, mode, and rules
        """
        return {
            "phase": self.identity_manager.get_identity_phase(),
            "mode": self.policy_mode,
            "rules": self.policies[self.policy_mode],
        }

    def is_capability_allowed(self, capability_meta: dict) -> bool:
        """
        Check if a capability is allowed by current policy.

        Args:
            capability_meta: Capability metadata with risk_level, requires_external

        Returns:
            True if allowed, False otherwise
        """
        ctx = self.get_policy_context()
        rules = ctx["rules"]
        max_risk = rules["max_capability_risk"]
        risk = capability_meta.get("risk_level", 0)
        if risk > max_risk:
            return False
        if capability_meta.get("requires_external", False) and not rules.get(
            "allow_external_calls", False
        ):
            return False
        return True


__all__ = ["PolicyEngine"]
