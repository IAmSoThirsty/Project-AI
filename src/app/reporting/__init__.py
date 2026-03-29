# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py

"""
Security Agent Reporting Module

Provides SARIF report generation and artifact management
for security agent findings.
"""

from .sarif_generator import SARIFGenerator

__all__ = ["SARIFGenerator"]
