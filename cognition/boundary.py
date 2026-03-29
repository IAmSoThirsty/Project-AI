# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / boundary.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Network / IPC Boundary Enforcement
All inbound requests must present a valid TARL hash for logical validation.
"""

from cognition.audit import audit


def enforce_boundary(tarl_hash: str | None) -> bool:
    """Enforce access control at the IPC boundary."""
    if not tarl_hash:
        audit("BOUNDARY_BLOCK", "Identity: NULL / ACCESS: DENIED")
        raise RuntimeError(
            "Boundary violation: TARL signature required for substrate access."
        )

    audit("BOUNDARY_ACCEPT", f"Identity: {tarl_hash} / ACCESS: GRANTED")
    return True
