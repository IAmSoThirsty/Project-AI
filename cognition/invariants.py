"""
Formal invariants for Project AI.
Each invariant must be mechanically enforceable and provable.
"""

from __future__ import annotations

from typing import Any


def invariant_single_authority(active_roles: list) -> bool:
    return len(active_roles) <= 1


def invariant_kernel_mediation(executed_via_kernel: bool) -> bool:
    return executed_via_kernel is True


def invariant_no_role_stacking(liara_active: bool, active_roles: list) -> bool:
    return not liara_active or len(active_roles) == 1


def invariant_contraction_on_failure(expanded: bool) -> bool:
    return expanded is False


class InvariantChecker:
    """Compatibility invariant checker used by cognition subsystems."""

    def __init__(self) -> None:
        self._checks = {
            "single_authority": invariant_single_authority,
            "kernel_mediation": invariant_kernel_mediation,
            "no_role_stacking": invariant_no_role_stacking,
            "contraction_on_failure": invariant_contraction_on_failure,
        }

    def validate(self, name: str, *args: Any, **kwargs: Any) -> bool:
        """Validate one invariant by name.

        Returns ``False`` when the invariant name is unknown or validation fails.
        """
        fn = self._checks.get(name)
        if fn is None:
            return False
        try:
            return bool(fn(*args, **kwargs))
        except Exception:
            return False

    def validate_all(self, payload: dict[str, Any]) -> dict[str, bool]:
        """Validate all known invariants against a payload dictionary."""
        results: dict[str, bool] = {}

        results["single_authority"] = self.validate(
            "single_authority", payload.get("active_roles", [])
        )
        results["kernel_mediation"] = self.validate(
            "kernel_mediation", payload.get("executed_via_kernel", False)
        )
        results["no_role_stacking"] = self.validate(
            "no_role_stacking",
            payload.get("liara_active", False),
            payload.get("active_roles", []),
        )
        results["contraction_on_failure"] = self.validate(
            "contraction_on_failure", payload.get("expanded", False)
        )

        return results


__all__ = [
    "invariant_single_authority",
    "invariant_kernel_mediation",
    "invariant_no_role_stacking",
    "invariant_contraction_on_failure",
    "InvariantChecker",
]
