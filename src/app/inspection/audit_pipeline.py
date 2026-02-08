"""
Audit Pipeline - Orchestration of Complete Inspection System

This module orchestrates the full audit pipeline, coordinating:
- Repository inspection
- Integrity checking
- Quality analysis
- Lint checking
- Report generation
- Catalog building

Provides a single entry point for complete repository auditing with
production-grade error handling, logging, and progress tracking.

Integration with CognitionKernel for governance and audit trails.

Author: Project-AI Team
Date: 2026-02-08
"""

import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.inspection.catalog_builder import CatalogBuilder
from app.inspection.integrity_checker import IntegrityChecker
from app.inspection.lint_checker import LintChecker
from app.inspection.quality_analyzer import QualityAnalyzer
from app.inspection.report_generator import ReportGenerator
from app.inspection.repository_inspector import RepositoryInspector

try:
    from app.core.cognition_kernel import CognitionKernel, ExecutionType
    from app.core.kernel_integration import KernelRoutedAgent

    KERNEL_AVAILABLE = True
except ImportError:
    KERNEL_AVAILABLE = False
    KernelRoutedAgent = object  # Fallback for when kernel is not available

logger = logging.getLogger(__name__)


@dataclass
class AuditConfig:
    """Configuration for audit pipeline."""

    repo_root: str | Path
    output_dir: str | Path = "audit_reports"
    exclusions: list[str] | None = None
    enable_lint: bool = True
    enable_quality: bool = True
    enable_integrity: bool = True
    include_git_metadata: bool = True
    generate_reports: bool = True
    generate_catalog: bool = True
    test_results: dict[str, Any] | None = None


@dataclass
class AuditResults:
    """Complete audit results."""

    success: bool
    timestamp: str
    execution_time_seconds: float
    inspection: dict[str, Any] | None = None
    integrity: dict[str, Any] | None = None
    quality: dict[str, Any] | None = None
    lint: dict[str, Any] | None = None
    reports: dict[str, str] | None = None
    catalog_path: str | None = None
    overall_assessment: dict[str, Any] | None = None
    error: str | None = None


class AuditPipeline(KernelRoutedAgent if KERNEL_AVAILABLE else object):
    """
    Complete audit pipeline orchestrator.

    Coordinates all inspection, checking, analysis, and reporting
    components into a single cohesive audit workflow.

    Integrates with CognitionKernel for governance when available.
    """

    def __init__(
        self,
        config: AuditConfig | None = None,
        kernel: "CognitionKernel | None" = None,
    ):
        """
        Initialize the audit pipeline.

        Args:
            config: Audit configuration (uses defaults if None)
            kernel: Optional CognitionKernel instance for routing
        """
        # Initialize kernel routing if available
        self.kernel = None
        if KERNEL_AVAILABLE and kernel is not None:
            super().__init__(
                kernel=kernel,
                execution_type=ExecutionType.AGENT_ACTION,
                default_risk_level="low",  # Auditing is read-only
            )
            self.kernel = kernel

        self.config = config or AuditConfig(repo_root=Path.cwd())
        self.repo_root = Path(self.config.repo_root).resolve()
        self.output_dir = Path(self.config.output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.inspector: RepositoryInspector | None = None
        self.integrity_checker: IntegrityChecker | None = None
        self.quality_analyzer: QualityAnalyzer | None = None
        self.lint_checker: LintChecker | None = None
        self.report_generator: ReportGenerator | None = None
        self.catalog_builder: CatalogBuilder | None = None

        logger.info(
            "Initialized AuditPipeline for: %s, output: %s",
            self.repo_root,
            self.output_dir,
        )

    def run(self) -> AuditResults:
        """
        Execute the complete audit pipeline.

        Returns:
            AuditResults containing all inspection data and reports

        This is the main entry point for running a complete audit.
        """
        if KERNEL_AVAILABLE and self.kernel is not None and hasattr(self, "_execute_through_kernel"):
            # Route through kernel for governance
            return self._execute_through_kernel(
                action=self._do_run,
                action_name="AuditPipeline.run",
                action_args=(),
                requires_approval=False,
                risk_level="low",
                metadata={
                    "repo_root": str(self.repo_root),
                    "operation": "full_audit",
                },
            )
        else:
            return self._do_run()

    def _do_run(self) -> AuditResults:
        """Internal implementation of audit pipeline execution."""
        start_time = datetime.now()

        logger.info("=" * 70)
        logger.info("Starting Repository Audit Pipeline")
        logger.info("=" * 70)
        logger.info("Repository: %s", self.repo_root)
        logger.info("Output Directory: %s", self.output_dir)
        logger.info("=" * 70)

        try:
            results = {
                "inspection": None,
                "integrity": None,
                "quality": None,
                "lint": None,
                "reports": None,
                "catalog_path": None,
                "overall_assessment": None,
            }

            # Phase 1: Repository Inspection
            logger.info("\n[Phase 1/5] Repository Inspection")
            logger.info("-" * 70)
            results["inspection"] = self._run_inspection()

            # Phase 2: Integrity Checking
            if self.config.enable_integrity:
                logger.info("\n[Phase 2/5] Integrity Checking")
                logger.info("-" * 70)
                results["integrity"] = self._run_integrity_check(
                    results["inspection"]
                )
            else:
                logger.info("\n[Phase 2/5] Integrity Checking - SKIPPED")

            # Phase 3: Quality Analysis
            if self.config.enable_quality:
                logger.info("\n[Phase 3/5] Quality Analysis")
                logger.info("-" * 70)
                results["quality"] = self._run_quality_analysis(results["inspection"])
            else:
                logger.info("\n[Phase 3/5] Quality Analysis - SKIPPED")

            # Phase 4: Lint Checking
            if self.config.enable_lint:
                logger.info("\n[Phase 4/5] Lint Checking")
                logger.info("-" * 70)
                results["lint"] = self._run_lint_check(results["inspection"])
            else:
                logger.info("\n[Phase 4/5] Lint Checking - SKIPPED")

            # Phase 5: Report Generation
            logger.info("\n[Phase 5/5] Report Generation")
            logger.info("-" * 70)

            if self.config.generate_reports:
                results["reports"] = self._generate_reports(
                    results["inspection"],
                    results.get("integrity") or {},
                    results.get("quality") or {},
                    results.get("lint") or {},
                )

            if self.config.generate_catalog:
                results["overall_assessment"] = self._compute_overall_assessment(
                    results
                )
                results["catalog_path"] = self._build_catalog(
                    results["inspection"],
                    results.get("integrity") or {},
                    results.get("quality") or {},
                    results.get("lint") or {},
                    results["overall_assessment"],
                )

            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            logger.info("\n" + "=" * 70)
            logger.info("Audit Pipeline Complete!")
            logger.info("=" * 70)
            logger.info("Execution Time: %.2f seconds", execution_time)
            logger.info("=" * 70)

            # Save results summary
            self._save_results_summary(results, execution_time)

            return AuditResults(
                success=True,
                timestamp=start_time.isoformat(),
                execution_time_seconds=execution_time,
                **results,
            )

        except Exception as e:
            logger.exception("Audit pipeline failed: %s", e)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return AuditResults(
                success=False,
                timestamp=start_time.isoformat(),
                execution_time_seconds=execution_time,
                error=str(e),
            )

    def _run_inspection(self) -> dict[str, Any]:
        """Run repository inspection phase."""
        self.inspector = RepositoryInspector(
            repo_root=self.repo_root,
            exclusions=self.config.exclusions,
            include_git_metadata=self.config.include_git_metadata,
        )

        results = self.inspector.inspect()

        # Export to JSON for debugging
        output_file = self.output_dir / "inspection_results.json"
        self.inspector.export_json(output_file)

        logger.info("✓ Inspection complete")
        logger.info("  Files discovered: %d", results["statistics"]["total_files"])
        logger.info("  Components identified: %d", len(results["components"]))

        return results

    def _run_integrity_check(self, inspection_results: dict[str, Any]) -> dict[str, Any]:
        """Run integrity checking phase."""
        self.integrity_checker = IntegrityChecker(
            repo_root=self.repo_root,
            file_inventory=inspection_results,
        )

        results = self.integrity_checker.check()

        logger.info("✓ Integrity check complete")
        logger.info("  Dependencies analyzed: %d", len(results["dependencies"]))
        logger.info("  Issues found: %d", len(results["issues"]))
        logger.info("  Circular dependencies: %d", len(results["circular_dependencies"]))

        return results

    def _run_quality_analysis(self, inspection_results: dict[str, Any]) -> dict[str, Any]:
        """Run quality analysis phase."""
        self.quality_analyzer = QualityAnalyzer(
            repo_root=self.repo_root,
            file_inventory=inspection_results,
            test_results=self.config.test_results,
        )

        results = self.quality_analyzer.analyze()

        agg = results.get("aggregate_metrics", {})
        logger.info("✓ Quality analysis complete")
        logger.info(
            "  Documentation coverage: %.1f%%",
            agg.get("average_documentation_coverage", 0) * 100,
        )
        logger.info(
            "  Maintainability index: %.1f/100",
            agg.get("average_maintainability_index", 0),
        )
        logger.info("  Components assessed: %d", agg.get("component_count", 0))

        return results

    def _run_lint_check(self, inspection_results: dict[str, Any]) -> dict[str, Any]:
        """Run lint checking phase."""
        self.lint_checker = LintChecker(
            repo_root=self.repo_root,
            file_inventory=inspection_results,
        )

        results = self.lint_checker.check()

        summary = results.get("summary", {})
        logger.info("✓ Lint check complete")
        logger.info("  Files checked: %d", summary.get("total_files_checked", 0))
        logger.info("  Issues found: %d", summary.get("total_issues", 0))
        logger.info("  Errors: %d", summary.get("issues_by_severity", {}).get("error", 0))

        return results

    def _generate_reports(
        self,
        inspection: dict[str, Any],
        integrity: dict[str, Any],
        quality: dict[str, Any],
        lint: dict[str, Any],
    ) -> dict[str, str]:
        """Generate machine-readable reports."""
        self.report_generator = ReportGenerator(output_dir=self.output_dir)

        report_files = self.report_generator.generate(
            inspection, integrity, quality, lint
        )

        logger.info("✓ Reports generated")
        for format_type, path in report_files.items():
            logger.info("  %s: %s", format_type.upper(), path)

        return report_files

    def _build_catalog(
        self,
        inspection: dict[str, Any],
        integrity: dict[str, Any],
        quality: dict[str, Any],
        lint: dict[str, Any],
        overall_assessment: dict[str, Any],
    ) -> str:
        """Build human-readable markdown catalog."""
        self.catalog_builder = CatalogBuilder(output_dir=self.output_dir)

        catalog_path = self.catalog_builder.build(
            inspection, integrity, quality, lint, overall_assessment
        )

        logger.info("✓ Catalog generated")
        logger.info("  Path: %s", catalog_path)

        return catalog_path

    def _compute_overall_assessment(self, results: dict[str, Any]) -> dict[str, Any]:
        """Compute overall assessment for catalog."""
        # This is a simplified version; the full assessment is in ReportGenerator
        inspection = results.get("inspection") or {}
        integrity = results.get("integrity") or {}
        quality = results.get("quality") or {}
        lint = results.get("lint") or {}

        # Extract metrics
        total_files = inspection.get("statistics", {}).get("total_files", 0)
        integrity_issues = len(integrity.get("issues", []))
        circular_deps = len(integrity.get("circular_dependencies", []))

        quality_agg = quality.get("aggregate_metrics", {})
        avg_doc = quality_agg.get("average_documentation_coverage", 0.0)
        avg_maint = quality_agg.get("average_maintainability_index", 0.0)

        lint_summary = lint.get("summary", {})
        total_lint_issues = lint_summary.get("total_issues", 0)
        lint_errors = lint_summary.get("issues_by_severity", {}).get("error", 0)

        # Compute health score
        health_factors = {
            "documentation": avg_doc * 25,
            "maintainability": (avg_maint / 100) * 25,
            "integrity": max(0, 25 - min(integrity_issues * 2 + circular_deps * 5, 25)),
            "lint": max(0, 25 - min(lint_errors * 0.5 + (total_lint_issues - lint_errors) * 0.1, 25)),
        }

        overall_health = sum(health_factors.values())

        # Determine grade
        if overall_health >= 90:
            grade = "A"
        elif overall_health >= 80:
            grade = "B"
        elif overall_health >= 70:
            grade = "C"
        elif overall_health >= 60:
            grade = "D"
        else:
            grade = "F"

        # Generate recommendations
        recommendations = []
        if lint_errors > 10:
            recommendations.append(f"Fix {lint_errors} lint errors")
        if circular_deps > 0:
            recommendations.append(f"Refactor {circular_deps} circular dependencies")
        if integrity_issues > 20:
            recommendations.append(f"Address {integrity_issues} integrity issues")
        if avg_doc < 0.5:
            recommendations.append(f"Increase documentation from {avg_doc*100:.1f}% to 70%+")

        return {
            "health_score": round(overall_health, 2),
            "grade": grade,
            "health_factors": health_factors,
            "critical_issues": {
                "integrity_issues": integrity_issues,
                "circular_dependencies": circular_deps,
                "lint_errors": lint_errors,
            },
            "recommendations": recommendations or ["No critical issues found!"],
        }

    def _save_results_summary(
        self, results: dict[str, Any], execution_time: float
    ) -> None:
        """Save a brief summary of results."""
        import json

        summary_path = self.output_dir / "audit_summary_latest.json"

        summary = {
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": execution_time,
            "repository": str(self.repo_root),
            "files_analyzed": results["inspection"]["statistics"]["total_files"]
            if results.get("inspection")
            else 0,
            "components": len(results["inspection"]["components"])
            if results.get("inspection")
            else 0,
            "integrity_issues": len(results["integrity"]["issues"])
            if results.get("integrity")
            else 0,
            "lint_issues": results["lint"]["summary"]["total_issues"]
            if results.get("lint")
            else 0,
            "reports_generated": list(results.get("reports", {}).keys()),
            "catalog_path": results.get("catalog_path"),
        }

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info("Summary saved to: %s", summary_path)


# Convenience function for simple usage
def run_audit(
    repo_root: str | Path | None = None,
    output_dir: str | Path = "audit_reports",
    **kwargs,
) -> AuditResults:
    """
    Convenience function to run a complete audit.

    Args:
        repo_root: Repository root directory (defaults to current directory)
        output_dir: Output directory for reports
        **kwargs: Additional configuration options

    Returns:
        AuditResults containing all inspection data

    Example:
        >>> results = run_audit("/path/to/repo", enable_lint=True)
        >>> print(f"Health Score: {results.overall_assessment['health_score']}")
    """
    config = AuditConfig(
        repo_root=repo_root or Path.cwd(),
        output_dir=output_dir,
        **kwargs,
    )

    pipeline = AuditPipeline(config=config)
    return pipeline.run()


__all__ = ["AuditPipeline", "AuditConfig", "AuditResults", "run_audit"]
