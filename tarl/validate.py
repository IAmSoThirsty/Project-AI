# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / validate.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / validate.py

#
# COMPLIANCE: Sovereign Substrate / validate.py


from tarl.core import TARL

ALLOWED_AUTHORITIES = {"Galahad", "Cerberus", "CodexDeus"}


def validate(t: TARL) -> None:
    if not t.intent or not t.scope:
        raise ValueError("Invalid TARL: intent and scope required")
    if t.authority not in ALLOWED_AUTHORITIES:
        raise ValueError("Invalid TARL authority")
