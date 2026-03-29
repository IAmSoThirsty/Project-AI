# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / liara_guard.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Liara Temporal Enforcement Guard (LTEG)
Kernel-side authority constraints and temporal role management.
"""

from datetime import UTC, datetime, timedelta

from cognition.audit import audit


class LiaraViolationError(Exception):
    """Exception raised for unauthorized Liara state transitions."""

    pass


class LiaraState:
    """Represents the current temporal state of the Liara subsystem."""

    def __init__(self) -> None:
        self.active_role: str | None = None
        self.expires_at: datetime | None = None


# Persistent singleton for substrate state
STATE = LiaraState()


def authorize_liara(role: str, ttl_seconds: int) -> bool:
    """
    Authorize a specific role for a limited Temporal TTL.
    Throws LiaraViolationError if a role is already active (Authority Stacking Prevention).
    """
    if STATE.active_role is not None:
        raise LiaraViolationError(
            f"Authority Stacking Prohibited. Active: {STATE.active_role}"
        )

    if ttl_seconds <= 0:
        raise LiaraViolationError("Temporal TTL must be positive.")

    STATE.active_role = role
    STATE.expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    audit("LIARA_AUTH_GRANTED", f"ROLE: {role} / EXPIRES: {STATE.expires_at}")
    return True


def revoke_liara(reason: str) -> bool:
    """Immediately revoke all Liara authority."""
    # Reason is logged manually by the caller for audit trail
    _ = reason
    STATE.active_role = None
    STATE.expires_at = None
    return True


def check_liara_state() -> None:
    """Enforce TTL expiration on the current active role."""
    if STATE.active_role and STATE.expires_at and datetime.now(UTC) > STATE.expires_at:
        revoke_liara("ttl_expired")
        audit("LIARA_TTL_EXPIRED", "Automatic revocation enforced.")
