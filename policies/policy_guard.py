# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / policy_guard.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / policy_guard.py


"""
Policy Guard
All policies must be explicitly declared and kernel-approved.
"""

from cognition.audit import audit

ALLOWED_POLICY_ACTIONS = {
    "read",
    "compute",
    "analyze",
}


def enforce_policy(action: str):
    if action not in ALLOWED_POLICY_ACTIONS:
        audit("POLICY_BLOCK", action)
        raise RuntimeError("Policy violation")

    audit("POLICY_ALLOW", action)
    return True
