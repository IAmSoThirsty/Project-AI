"""
Report Generator - Machine-Readable Audit Reports

This module generates comprehensive machine-readable audit reports in:
- JSON format (with full detail)
- YAML format (human-readable structure)

Reports include all inspection results, quality metrics, integrity checks,
and lint findings with proper schema validation.

Author: Project-AI Team
Date: 2026-02-08
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates machine-readable audit reports in JSON and YAML formats.

    Consolidates all inspection data into comprehensive, well-structured
    reports suitable for programmatic consumption and archival.
    """

    REPORT_VERSION = "1.0.0"

    def __init__(self, output_dir: str | Path):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory for output reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized ReportGenerator, output: %s", self.output_dir)

    def generate(
        self,
        inspection_results: dict[str, Any],
        integrity_results: dict[str, Any],
        quality_results: dict[str, Any],
        lint_results: dict[str, Any],
    ) -> dict[str, str]:
        """
        Generate complete audit report in multiple formats.

        Args:
            inspection_results: Results from RepositoryInspector
            integrity_results: Results from IntegrityChecker
            quality_results: Results from QualityAnalyzer
            lint_results: Results from LintChecker

        Returns:
            Dictionary mapping format to output file path
        """
        logger.info("Generating audit reports...")

        try:
            timestamp = datetime.now().isoformat()

            # Consolidate all results
            report_data = self._consolidate_results(
                timestamp,
                inspection_results,
                integrity_results,
                quality_results,
                lint_results,
            )

            # Generate reports in multiple formats
            output_files = {}

            # JSON report (full detail)
            json_path = self._generate_json_report(report_data)
            output_files["json"] = str(json_path)

            # YAML report (more human-readable)
            yaml_path = self._generate_yaml_report(report_data)
            output_files["yaml"] = str(yaml_path)

            # Summary JSON (condensed for dashboards)
            summary_path = self._generate_summary_report(report_data)
            output_files["summary"] = str(summary_path)

            logger.info("Generated reports: %s", ", ".join(output_files.values()))

            return output_files

        except Exception as e:
            logger.exception("Report generation failed: %s", e)
            raise

    def _consolidate_results(
        self,
        timestamp: str,
        inspection: dict[str, Any],
        integrity: dict[str, Any],
        quality: dict[str, Any],
        lint: dict[str, Any],
    ) -> dict[str, Any]:
        """Consolidate all inspection results into a single report structure."""
        return {
            "metadata": {
                "report_version": self.REPORT_VERSION,
                "generated_at": timestamp,
                "repository": inspection.get("repository", ""),
                "tool": "Project-AI Inspection System",
            },
            "inspection": {
                "files": inspection.get("files", {}),
                "components": inspection.get("components", {}),
                "statistics": inspection.get("statistics", {}),
            },
            "integrity": {
                "dependencies": integrity.get("dependencies", []),
                "circular_dependencies": integrity.get("circular_dependencies", []),
                "issues": integrity.get("issues", []),
                "dependency_graph": integrity.get("dependency_graph", {}),
                "cross_reference_catalog": integrity.get("cross_reference_catalog", {}),
                "statistics": integrity.get("statistics", {}),
            },
            "quality": {
                "file_metrics": quality.get("file_metrics", {}),
                "component_quality": quality.get("component_quality", {}),
                "aggregate_metrics": quality.get("aggregate_metrics", {}),
            },
            "lint": {
                "reports": lint.get("reports", []),
                "summary": lint.get("summary", {}),
            },
            "overall_assessment": self._compute_overall_assessment(inspection, integrity, quality, lint),
        }

    def _compute_overall_assessment(
        self,
        inspection: dict[str, Any],
        integrity: dict[str, Any],
        quality: dict[str, Any],
        lint: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute overall assessment and health score."""
        # Extract key metrics
        inspection.get("statistics", {}).get("total_files", 0)
        integrity_issues = len(integrity.get("issues", []))
        circular_deps = len(integrity.get("circular_dependencies", []))

        quality_agg = quality.get("aggregate_metrics", {})
        avg_doc_coverage = quality_agg.get("average_documentation_coverage", 0.0)
        avg_maintainability = quality_agg.get("average_maintainability_index", 0.0)

        lint_summary = lint.get("summary", {})
        total_lint_issues = lint_summary.get("total_issues", 0)
        lint_errors = lint_summary.get("issues_by_severity", {}).get("error", 0)

        # Compute health score (0-100)
        health_factors = []

        # Documentation factor (0-25 points)
        doc_score = avg_doc_coverage * 25
        health_factors.append(("documentation", doc_score))

        # Maintainability factor (0-25 points)
        maint_score = (avg_maintainability / 100) * 25
        health_factors.append(("maintainability", maint_score))

        # Integrity factor (0-25 points)
        # Penalize for integrity issues and circular dependencies
        integrity_penalty = min(integrity_issues * 2 + circular_deps * 5, 25)
        integrity_score = max(0, 25 - integrity_penalty)
        health_factors.append(("integrity", integrity_score))

        # Lint factor (0-25 points)
        # Penalize for lint errors and warnings
        lint_penalty = min(lint_errors * 0.5 + (total_lint_issues - lint_errors) * 0.1, 25)
        lint_score = max(0, 25 - lint_penalty)
        health_factors.append(("lint", lint_score))

        overall_health = sum(score for _, score in health_factors)

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

        return {
            "health_score": round(overall_health, 2),
            "grade": grade,
            "health_factors": {name: round(score, 2) for name, score in health_factors},
            "critical_issues": {
                "integrity_issues": integrity_issues,
                "circular_dependencies": circular_deps,
                "lint_errors": lint_errors,
            },
            "recommendations": self._generate_recommendations(
                integrity_issues, circular_deps, lint_errors, avg_doc_coverage
            ),
        }

    def _generate_recommendations(
        self,
        integrity_issues: int,
        circular_deps: int,
        lint_errors: int,
        doc_coverage: float,
    ) -> list[str]:
        """Generate actionable recommendations based on findings."""
        recommendations = []

        if lint_errors > 10:
            recommendations.append(f"High priority: Fix {lint_errors} lint errors to improve code quality")

        if circular_deps > 0:
            recommendations.append(f"Refactor {circular_deps} circular dependencies to improve modularity")

        if integrity_issues > 20:
            recommendations.append(f"Address {integrity_issues} integrity issues (missing imports, dead code)")

        if doc_coverage < 0.5:
            recommendations.append(f"Increase documentation coverage from {doc_coverage*100:.1f}% to at least 70%")

        if not recommendations:
            recommendations.append("Excellent! No critical issues found.")

        return recommendations

    def _generate_json_report(self, report_data: dict[str, Any]) -> Path:
        """Generate JSON format report."""
        output_path = self.output_dir / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info("Generated JSON report: %s", output_path)
        return output_path

    def _generate_yaml_report(self, report_data: dict[str, Any]) -> Path:
        """Generate YAML format report."""
        output_path = self.output_dir / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(report_data, f, default_flow_style=False, sort_keys=False)

        logger.info("Generated YAML report: %s", output_path)
        return output_path

    def _generate_summary_report(self, report_data: dict[str, Any]) -> Path:
        """Generate condensed summary report."""
        output_path = self.output_dir / f"audit_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        summary = {
            "metadata": report_data["metadata"],
            "statistics": {
                "total_files": report_data["inspection"]["statistics"].get("total_files", 0),
                "total_lines": report_data["inspection"]["statistics"].get("total_lines", 0),
                "total_components": len(report_data["inspection"]["components"]),
            },
            "integrity_summary": {
                "total_dependencies": len(report_data["integrity"]["dependencies"]),
                "circular_dependencies": len(report_data["integrity"]["circular_dependencies"]),
                "total_issues": len(report_data["integrity"]["issues"]),
            },
            "quality_summary": report_data["quality"]["aggregate_metrics"],
            "lint_summary": report_data["lint"]["summary"],
            "overall_assessment": report_data["overall_assessment"],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info("Generated summary report: %s", output_path)
        return output_path


__all__ = ["ReportGenerator"]
