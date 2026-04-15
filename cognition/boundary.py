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
    """Compatibility boundary check for cognition engines.

    Some subsystems expect a lightweight numeric guard function named
    ``check_boundary``. This implementation preserves that contract while
    retaining the existing TARL boundary model.

    Args:
        operation: Logical operation name being checked.
        magnitude: Numeric workload magnitude for the operation.
        limit: Upper bound considered safe.

    Returns:
        ``True`` when within boundary limits, otherwise ``False``.
    """
    try:
        numeric_value = float(magnitude)
    except (TypeError, ValueError):
        audit("BOUNDARY_NUMERIC_BLOCK", {"operation": operation, "magnitude": magnitude})
        return False

    if numeric_value < 0:
        audit("BOUNDARY_NUMERIC_BLOCK", {"operation": operation, "magnitude": numeric_value})
        return False

    allowed = numeric_value <= float(limit)
    audit(
        "BOUNDARY_NUMERIC_CHECK",
        {
            "operation": operation,
            "magnitude": numeric_value,
            "limit": limit,
            "allowed": allowed,
        },
    )
    return allowed
