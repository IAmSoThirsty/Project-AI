"""
Audit & Accountability System
=============================

Complete audit trail with human accountability interfaces.
"""

# Backward-compatible name: AccountabilityManager was renamed to
# AccountabilitySystem in implementation.
from .accountability import AccountabilitySystem
from .audit_integration import BuildAuditIntegration

AccountabilityManager = AccountabilitySystem

__all__ = [
    "BuildAuditIntegration",
    "AccountabilityManager",
    "AccountabilitySystem",
]
