"""
Inspection, Audit, and Cataloging Subsystem for Project-AI

This module provides institution-grade inspection, audit, and cataloging capabilities
for the entire Project-AI monolith, including:

- Full repository-wide inventory and classification
- Automated file errors, lint, markdown, and syntax checks
- End-to-end integrity checks with dependency analysis
- Comprehensive audit pipeline with machine-readable and human-readable reports
- Strict modular integration with Project-AI's config-driven infrastructure

All components are production-grade with full error handling, logging, and testing.

Key Components:
    - RepositoryInspector: File inventory and classification
    - IntegrityChecker: Cross-reference catalog and dependency analysis
    - QualityAnalyzer: Code coverage, documentation, and architectural rigor assessment
    - LintChecker: Automated linting and syntax validation
    - AuditPipeline: Orchestration of all inspection operations
    - ReportGenerator: Machine-readable report generation (JSON/YAML)
    - CatalogBuilder: Human-readable markdown index generation

Author: Project-AI Team
Date: 2026-02-08
Version: 1.0.0
"""

from app.inspection.audit_pipeline import AuditPipeline
from app.inspection.catalog_builder import CatalogBuilder
from app.inspection.integrity_checker import IntegrityChecker
from app.inspection.lint_checker import LintChecker
from app.inspection.quality_analyzer import QualityAnalyzer
from app.inspection.report_generator import ReportGenerator
from app.inspection.repository_inspector import RepositoryInspector

__all__ = [
    "AuditPipeline",
    "CatalogBuilder",
    "IntegrityChecker",
    "LintChecker",
    "QualityAnalyzer",
    "ReportGenerator",
    "RepositoryInspector",
]

__version__ = "1.0.0"
