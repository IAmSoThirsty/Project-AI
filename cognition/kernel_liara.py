# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / kernel_liara.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Kernel-Owned Liara Orchestration (KOLO)
Orchestrates the lifecycle of the Liara subsystem based on pillar health.
"""

from datetime import UTC, datetime

from cognition.audit import audit
from cognition.liara_guard import LiaraViolationError, authorize_liara, revoke_liara

# Configuration constants
COOLDOWN_SECONDS: int = 300
_last_revocation: datetime | None = None


def kernel_health_check(pillar_status: dict[str, bool]) -> str | None:
    """Audit the status of all pillars and identify the first point of failure."""
    for pillar, ok in pillar_status.items():
        if not ok:
            return pillar
    return None


def maybe_activate_liara(pillar_status: dict[str, bool]) -> str | None:
    """Attempt to activate Liara if a pillar failure is detected."""
    global _last_revocation

    failed_pillar = kernel_health_check(pillar_status)
    if not failed_pillar:
        return None

    now = datetime.now(UTC)
    if _last_revocation and (now - _last_revocation).total_seconds() < COOLDOWN_SECONDS:
        audit("LIARA_BLOCKED", f"cooldown_active_for_{failed_pillar}")
        return None

    try:
        if authorize_liara(failed_pillar, ttl_seconds=900):
            audit("LIARA_ACTIVATED", f"PILLAR: {failed_pillar} / TTL: 900s")
            return failed_pillar
        return None
    except LiaraViolationError as e:
        audit("LIARA_VIOLATION", f"failed_to_activate_{failed_pillar}: {e}")
        return None


def restore_pillar() -> None:
    """Manually restore a pillar and revoke Liara authority."""
    global _last_revocation
    revoke_liara("pillar_restored")
    _last_revocation = datetime.now(UTC)
    audit("LIARA_REVOKED", "pillar_restored")
