#                                           [2026-03-05 08:49]
#                                          Productivity: Active
"""
Network / IPC Boundary Enforcement
All inbound requests must present a valid TARL hash.
"""

from cognition.audit import audit


def enforce_boundary(tarl_hash: str | None):
    if not tarl_hash:
        audit("BOUNDARY_BLOCK", "missing_tarl")
        raise RuntimeError("Boundary violation: TARL required")

    audit("BOUNDARY_ACCEPT", tarl_hash)
    return True


def check_boundary(operation: str, magnitude: int | float, limit: int = 10000) -> bool:
    """Compatibility numeric boundary guard used by cognition integrations."""
    try:
        value = float(magnitude)
    except (TypeError, ValueError):
        audit(
            "BOUNDARY_NUMERIC_BLOCK",
            {"operation": operation, "magnitude": magnitude, "reason": "non_numeric"},
        )
        return False

    if value < 0:
        audit(
            "BOUNDARY_NUMERIC_BLOCK",
            {"operation": operation, "magnitude": value, "reason": "negative"},
        )
        return False

    allowed = value <= float(limit)
    audit(
        "BOUNDARY_NUMERIC_CHECK",
        {
            "operation": operation,
            "magnitude": value,
            "limit": limit,
            "allowed": allowed,
        },
    )
    return allowed
