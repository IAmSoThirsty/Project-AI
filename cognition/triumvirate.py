from cognition.audit import audit
from cognition.kernel_liara import maybe_activate_liara, restore_pillar

ACTIVE_SUBSTITUTION = None


def evaluate_triumvirate(health: dict):
    global ACTIVE_SUBSTITUTION
    failed = [p for p, h in health.items() if not h.healthy]

    if len(failed) == 0:
        if ACTIVE_SUBSTITUTION:
            restore_pillar()
            audit("TRIUMVIRATE_RESTORED", ACTIVE_SUBSTITUTION)
            ACTIVE_SUBSTITUTION = None
        return "STABLE"

    if len(failed) == 1 and ACTIVE_SUBSTITUTION is None:
        role = maybe_activate_liara({failed[0]: False})
        ACTIVE_SUBSTITUTION = role
        audit("TRIUMVIRATE_SUBSTITUTION", role)
        return "SUBSTITUTED"

    audit("GOVERNANCE_HOLD", failed)
    raise RuntimeError("Governance Hold: Multiple pillar degradation")
