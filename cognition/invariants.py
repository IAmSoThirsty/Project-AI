# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / invariants.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Formal Invariants for Project-AI
Mechanically enforceable constraints that must hold true for all substrate states.
"""


def invariant_single_authority(active_roles: list[str]) -> bool:
    """Ensure that no more than one authority role is active at any time."""
    return len(active_roles) <= 1


def invariant_kernel_mediation(executed_via_kernel: bool) -> bool:
    """Ensure all high-privilege operations are mediated by the Sovereign Kernel."""
    return executed_via_kernel is True


def invariant_no_role_stacking(liara_active: bool, active_roles: list[str]) -> bool:
    """Prevent role stacking when Liara is active."""
    return not liara_active or len(active_roles) == 1


def invariant_contraction_on_failure(expanded: bool) -> bool:
    """Ensure automated contraction (safe-mode) on any detected failure."""
    return expanded is False
