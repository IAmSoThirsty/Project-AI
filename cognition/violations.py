# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / violations.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Substrate Violation Reporter
Standardized reporting for security and architectural boundary violations.
"""

from typing import Any

from cognition.audit import audit


def attempted_violation(kind: str, detail: Any = None) -> None:
    """Report an attempted architectural or security violation to the audit ledger."""
    audit("ATTEMPTED_VIOLATION", f"Type: {kind} / Details: {detail}")
