# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / hydra_guard.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Hydra Guard: Adversarial Expansion Prevention
Prevents unauthorized recursive process expansion (the Hydra Effect).
"""

from cognition.violations import attempted_violation


def hydra_check(expansion_attempt: bool, context: str) -> None:
    """Check for and block unauthorized recursive expansion attempts."""
    if expansion_attempt:
        attempted_violation(
            "HYDRA_EFFECT_DETECTED", f"Context: {context} / STATUS: BLOCKED"
        )
        raise RuntimeError(
            f"Hydra Effect Guard violation in {context}: Unauthorized expansion attempt neutralized."
        )
