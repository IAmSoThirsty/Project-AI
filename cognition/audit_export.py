# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / audit_export.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
Audit Export Utility
Provides controlled access to the Sovereign Accountability Ledger for reporting.
"""

from cognition.audit import AUDIT_LOG


def export_audit() -> list[str]:
    """Export the current audit log as a list of standardized strings."""
    if not AUDIT_LOG.exists():
        return []

    try:
        return AUDIT_LOG.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ["ERROR: Accountability Ledger Unreachable"]
