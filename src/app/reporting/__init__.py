#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Security Agent Reporting Module

Provides SARIF report generation and artifact management
for security agent findings.
"""

from .sarif_generator import SARIFGenerator

__all__ = ["SARIFGenerator"]
