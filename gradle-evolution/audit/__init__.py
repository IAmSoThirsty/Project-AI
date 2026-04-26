#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Audit & Accountability System
=============================

Complete audit trail with human accountability interfaces.
"""

from .accountability import AccountabilitySystem
from .audit_integration import BuildAuditIntegration

# Backward-compatible alias for older imports/tests.
AccountabilityManager = AccountabilitySystem

__all__ = [
    "BuildAuditIntegration",
    "AccountabilityManager",
    "AccountabilitySystem",
]
