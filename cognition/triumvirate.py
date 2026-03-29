# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / triumvirate.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
The Triumvirate Governance Orchestrator
Manages pillar health and failsafe substitution via the Liara Guard.
"""

from typing import Any

from cognition.audit import audit
from cognition.kernel_liara import maybe_activate_liara, restore_pillar

# Minimum confidence required before predictive escalation
PREDICTIVE_WARNING_THRESHOLD = 0.50
PREDICTIVE_CRITICAL_THRESHOLD = 0.20

# Global state tracker for active governance substitutions
ACTIVE_SUBSTITUTION: str | None = None


def evaluate_triumvirate(health: dict[str, Any], predictive_signal: float = 1.0) -> str:
    """
    Evaluate the health and predictive risk of the Triumvirate pillars.
    Triggers failsafes via Liara if pillars degrade or predictive confidence collapses.
    """
    global ACTIVE_SUBSTITUTION

    # 📈 1. Predictive Risk Assessment
    if predictive_signal < PREDICTIVE_CRITICAL_THRESHOLD:
        audit(
            "TRIUMVIRATE_PREDICTIVE_CRITICAL",
            f"SIGNAL: {predictive_signal:.4f} / ACTION: LOCKDOWN",
        )
        # Trigger immediate failsafe even if pillars are technically "up"
        if ACTIVE_SUBSTITUTION is None:
            # Substitution logic for generic failure
            role = maybe_activate_liara({"PREDICTIVE_FAIL": False})
            ACTIVE_SUBSTITUTION = role
            return "PREDICTIVE_FAILOVER"

    # 🏥 2. Reactive Health Assessment
    # Identify degraded pillars
    failed = [p for p, h in health.items() if not getattr(h, "healthy", h)]

    if not failed:
        if ACTIVE_SUBSTITUTION:
            restore_pillar()
            audit(
                "TRIUMVIRATE_RESTORED", f"Role: {ACTIVE_SUBSTITUTION} / STATUS: NORMAL"
            )
            ACTIVE_SUBSTITUTION = None

        if predictive_signal < PREDICTIVE_WARNING_THRESHOLD:
            return "PREDICTIVE_WARNING"
        return "STABLE"

    if len(failed) == 1 and ACTIVE_SUBSTITUTION is None:
        role = maybe_activate_liara({failed[0]: False})
        ACTIVE_SUBSTITUTION = role
        audit("TRIUMVIRATE_SUBSTITUTION", f"Role: {role} / SIGNAL: FAILSAFE")
        return "SUBSTITUTED"

    # 🚨 3. Critical Failure
    # Multiple pillars or unrecoverable state
    audit("GOVERNANCE_HOLD", f"Degraded Pillars: {failed} / SIGNAL: HALT")
    raise RuntimeError(
        f"Governance Hold: Multiple pillar degradation detected in {failed}"
    )
