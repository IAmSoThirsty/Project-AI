"""
Kernel-owned Liara orchestration.
"""

from datetime import datetime
from cognition.liara_guard import authorize_liara, revoke_liara, LiaraViolation
from cognition.audit import audit

COOLDOWN_SECONDS = 300
_last_revocation = None

def kernel_health_check(pillar_status: dict):
    for pillar, ok in pillar_status.items():
        if not ok:
            return pillar
    return None

def maybe_activate_liara(pillar_status: dict):
    global _last_revocation

    failed = kernel_health_check(pillar_status)
    if not failed:
        return None

    now = datetime.utcnow()
    if _last_revocation and (now - _last_revocation).total_seconds() < COOLDOWN_SECONDS:
        audit("LIARA_BLOCKED", "cooldown_active")
        return None

    try:
        authorize_liara(failed, ttl_seconds=900)
        audit("LIARA_ACTIVATED", failed)
        return failed
    except LiaraViolation as e:
        audit("LIARA_VIOLATION", str(e))
        return None

def restore_pillar():
    global _last_revocation
    revoke_liara("pillar_restored")
    _last_revocation = datetime.utcnow()
    audit("LIARA_REVOKED", "pillar_restored")
