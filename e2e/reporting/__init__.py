# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


"""
E2E Test Reporting Module

Provides comprehensive reporting capabilities for E2E tests including:
- HTML report generation
- JSON report generation
- Coverage analysis and visualization
- Error traceability
- Artifact management
"""

from e2e.reporting.artifact_manager import ArtifactManager
from e2e.reporting.coverage_reporter import CoverageReporter
from e2e.reporting.html_reporter import HTMLReporter
from e2e.reporting.json_reporter import JSONReporter

__all__ = [
    "HTMLReporter",
    "JSONReporter",
    "CoverageReporter",
    "ArtifactManager",
]
