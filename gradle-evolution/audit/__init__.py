"""
Audit & Accountability System
=============================

Complete audit trail with human accountability interfaces.
"""

from .audit_integration import BuildAuditIntegration

# Backward-compatible name: AccountabilityManager was renamed to
# AccountabilitySystem in implementation.
from .accountability import AccountabilitySystem

AccountabilityManager = AccountabilitySystem

__all__ = [
    "BuildAuditIntegration",
    "AccountabilityManager",
    "AccountabilitySystem",
]
