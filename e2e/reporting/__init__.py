"""
E2E Test Reporting Module

Provides comprehensive reporting capabilities for E2E tests including:
- HTML report generation
- JSON report generation
- Coverage analysis and visualization
- Error traceability
- Artifact management
"""

from e2e.reporting.html_reporter import HTMLReporter
from e2e.reporting.json_reporter import JSONReporter
from e2e.reporting.coverage_reporter import CoverageReporter
from e2e.reporting.artifact_manager import ArtifactManager

__all__ = [
    "HTMLReporter",
    "JSONReporter",
    "CoverageReporter",
    "ArtifactManager",
]
