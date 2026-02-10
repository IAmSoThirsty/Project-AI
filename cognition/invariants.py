"""
Formal invariants for Project AI.
Each invariant must be mechanically enforceable and provable.
"""


def invariant_single_authority(active_roles: list) -> bool:
    return len(active_roles) <= 1


def invariant_kernel_mediation(executed_via_kernel: bool) -> bool:
    return executed_via_kernel is True


def invariant_no_role_stacking(liara_active: bool, active_roles: list) -> bool:
    return not liara_active or len(active_roles) == 1


def invariant_contraction_on_failure(expanded: bool) -> bool:
    return expanded is False
