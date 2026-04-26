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
