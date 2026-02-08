"""
Catalog Builder - Institutional-Grade Markdown Index

This module generates comprehensive human-readable markdown catalogs
for peer review, QA, and compliance workflows.

Output includes:
- Executive summary with key metrics
- File inventory with classification
- Component dependency graph
- Quality assessment
- Issue catalog with severity ranking
- Actionable recommendations

Author: Project-AI Team
Date: 2026-02-08
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CatalogBuilder:
    """
    Generates institutional-grade markdown catalog and index.

    Creates comprehensive, well-structured markdown documentation
    suitable for human review, compliance audits, and peer review.
    """

    def __init__(self, output_dir: str | Path):
        """
        Initialize the catalog builder.

        Args:
            output_dir: Directory for output catalogs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized CatalogBuilder, output: %s", self.output_dir)

    def build(
        self,
        inspection_results: dict[str, Any],
        integrity_results: dict[str, Any],
        quality_results: dict[str, Any],
        lint_results: dict[str, Any],
        overall_assessment: dict[str, Any],
    ) -> str:
        """
        Build comprehensive markdown catalog.

        Args:
            inspection_results: Results from RepositoryInspector
            integrity_results: Results from IntegrityChecker
            quality_results: Results from QualityAnalyzer
            lint_results: Results from LintChecker
            overall_assessment: Overall health assessment

        Returns:
            Path to generated catalog file
        """
        logger.info("Building markdown catalog...")

        try:
            output_path = self.output_dir / f"AUDIT_CATALOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            with open(output_path, "w", encoding="utf-8") as f:
                # Write sections
                self._write_header(f, inspection_results)
                self._write_executive_summary(f, overall_assessment)
                self._write_statistics(f, inspection_results, integrity_results, quality_results, lint_results)
                self._write_file_inventory(f, inspection_results)
                self._write_component_catalog(f, inspection_results)
                self._write_dependency_analysis(f, integrity_results)
                self._write_quality_assessment(f, quality_results)
                self._write_lint_report(f, lint_results)
                self._write_integrity_issues(f, integrity_results)
                self._write_recommendations(f, overall_assessment)
                self._write_footer(f)

            logger.info("Generated markdown catalog: %s", output_path)
            return str(output_path)

        except Exception as e:
            logger.exception("Catalog building failed: %s", e)
            raise

    def _write_header(self, f, inspection: dict[str, Any]) -> None:
        """Write document header."""
        repo = inspection.get("repository", "Unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        f.write("# Repository Audit Catalog\n\n")
        f.write("## Institutional-Grade Inspection Report\n\n")
        f.write(f"**Repository:** `{repo}`\n\n")
        f.write(f"**Generated:** {timestamp}\n\n")
        f.write(f"**Tool:** Project-AI Inspection & Audit System v1.0.0\n\n")
        f.write("---\n\n")

    def _write_executive_summary(self, f, assessment: dict[str, Any]) -> None:
        """Write executive summary section."""
        f.write("## Executive Summary\n\n")

        health_score = assessment.get("health_score", 0)
        grade = assessment.get("grade", "N/A")
        factors = assessment.get("health_factors", {})

        f.write(f"### Overall Health Score: **{health_score:.1f}/100** (Grade: **{grade}**)\n\n")

        f.write("#### Health Factor Breakdown\n\n")
        f.write("| Factor | Score | Status |\n")
        f.write("|--------|-------|--------|\n")

        for factor_name, score in factors.items():
            status = self._get_status_emoji(score, 25)
            f.write(f"| {factor_name.capitalize()} | {score:.1f}/25 | {status} |\n")

        f.write("\n")

        # Critical issues
        critical = assessment.get("critical_issues", {})
        f.write("#### Critical Issues\n\n")
        f.write(f"- **Integrity Issues:** {critical.get('integrity_issues', 0)}\n")
        f.write(f"- **Circular Dependencies:** {critical.get('circular_dependencies', 0)}\n")
        f.write(f"- **Lint Errors:** {critical.get('lint_errors', 0)}\n\n")

        f.write("---\n\n")

    def _write_statistics(
        self, f, inspection: dict[str, Any], integrity: dict[str, Any],
        quality: dict[str, Any], lint: dict[str, Any]
    ) -> None:
        """Write repository statistics."""
        f.write("## Repository Statistics\n\n")

        stats = inspection.get("statistics", {})
        quality_agg = quality.get("aggregate_metrics", {})
        lint_sum = lint.get("summary", {})

        f.write("### Inventory\n\n")
        f.write(f"- **Total Files:** {stats.get('total_files', 0)}\n")
        f.write(f"- **Total Lines of Code:** {stats.get('total_lines', 0):,}\n")
        f.write(f"- **Components:** {len(inspection.get('components', {}))}\n\n")

        f.write("### Files by Type\n\n")
        by_type = stats.get("by_type", {})
        for file_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{file_type}:** {count}\n")
        f.write("\n")

        f.write("### Files by Status\n\n")
        by_status = stats.get("by_status", {})
        for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{status}:** {count}\n")
        f.write("\n")

        f.write("### Quality Metrics\n\n")
        f.write(f"- **Documentation Coverage:** {quality_agg.get('average_documentation_coverage', 0)*100:.1f}%\n")
        f.write(f"- **Code Coverage:** {quality_agg.get('average_code_coverage', 0)*100:.1f}%\n")
        f.write(f"- **Maintainability Index:** {quality_agg.get('average_maintainability_index', 0):.1f}/100\n")
        f.write(f"- **Average Cohesion:** {quality_agg.get('average_cohesion_score', 0)*100:.1f}%\n\n")

        f.write("### Integrity\n\n")
        int_stats = integrity.get("statistics", {})
        f.write(f"- **Total Dependencies:** {int_stats.get('total_dependencies', 0)}\n")
        f.write(f"- **Integrity Issues:** {int_stats.get('total_issues', 0)}\n")
        f.write(f"- **Circular Dependencies:** {len(integrity.get('circular_dependencies', []))}\n\n")

        f.write("### Linting\n\n")
        f.write(f"- **Files Checked:** {lint_sum.get('total_files_checked', 0)}\n")
        f.write(f"- **Total Issues:** {lint_sum.get('total_issues', 0)}\n")
        f.write(f"- **Errors:** {lint_sum.get('issues_by_severity', {}).get('error', 0)}\n")
        f.write(f"- **Warnings:** {lint_sum.get('issues_by_severity', {}).get('warning', 0)}\n\n")

        f.write("---\n\n")

    def _write_file_inventory(self, f, inspection: dict[str, Any]) -> None:
        """Write file inventory section."""
        f.write("## File Inventory\n\n")
        f.write("Complete catalog of all files with classification and status.\n\n")

        files = inspection.get("files", {})
        by_type = {}

        for path, info in files.items():
            file_type = info.get("file_type", "other")
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append((path, info))

        for file_type in sorted(by_type.keys()):
            f.write(f"### {file_type.upper()} Files\n\n")
            f.write("| File | Status | LOC | Complexity |\n")
            f.write("|------|--------|-----|------------|\n")

            for path, info in sorted(by_type[file_type], key=lambda x: x[0]):
                status = info.get("status", "unknown")
                loc = info.get("lines_of_code", 0)
                complexity = info.get("complexity_score", 0)
                f.write(f"| `{path}` | {status} | {loc} | {complexity} |\n")

            f.write("\n")

        f.write("---\n\n")

    def _write_component_catalog(self, f, inspection: dict[str, Any]) -> None:
        """Write component catalog section."""
        f.write("## Component Catalog\n\n")
        f.write("Logical components and subsystems identified in the repository.\n\n")

        components = inspection.get("components", {})

        f.write("| Component | Type | Status | Files |\n")
        f.write("|-----------|------|--------|-------|\n")

        for name, info in sorted(components.items()):
            comp_type = info.get("component_type", "unknown")
            status = info.get("status", "unknown")
            file_count = len(info.get("files", []))
            f.write(f"| `{name}` | {comp_type} | {status} | {file_count} |\n")

        f.write("\n---\n\n")

    def _write_dependency_analysis(self, f, integrity: dict[str, Any]) -> None:
        """Write dependency analysis section."""
        f.write("## Dependency Analysis\n\n")

        stats = integrity.get("statistics", {})

        f.write("### Most Dependent Modules\n\n")
        f.write("Modules with the highest number of dependencies.\n\n")

        most_dependent = stats.get("most_dependent_modules", [])[:10]
        if most_dependent:
            f.write("| Module | Dependency Count |\n")
            f.write("|--------|------------------|\n")
            for item in most_dependent:
                f.write(f"| `{item.get('module', '')}` | {item.get('dependency_count', 0)} |\n")
            f.write("\n")
        else:
            f.write("*No dependency data available.*\n\n")

        f.write("### Most Imported Modules\n\n")
        f.write("Modules most frequently imported by others.\n\n")

        most_imported = stats.get("most_imported_modules", [])[:10]
        if most_imported:
            f.write("| Module | Import Count |\n")
            f.write("|--------|-------------|\n")
            for item in most_imported:
                f.write(f"| `{item.get('module', '')}` | {item.get('import_count', 0)} |\n")
            f.write("\n")
        else:
            f.write("*No import data available.*\n\n")

        # Circular dependencies
        circular = integrity.get("circular_dependencies", [])
        if circular:
            f.write("### Circular Dependencies ⚠️\n\n")
            f.write(f"Found {len(circular)} circular dependency chains.\n\n")

            for i, circ in enumerate(circular[:10], 1):
                cycle = circ.get("cycle", [])
                severity = circ.get("severity", "medium")
                f.write(f"{i}. **{severity.upper()}**: {' → '.join(cycle)}\n")

            if len(circular) > 10:
                f.write(f"\n*...and {len(circular) - 10} more circular dependencies.*\n")

            f.write("\n")

        f.write("---\n\n")

    def _write_quality_assessment(self, f, quality: dict[str, Any]) -> None:
        """Write quality assessment section."""
        f.write("## Quality Assessment\n\n")

        component_quality = quality.get("component_quality", {})

        if not component_quality:
            f.write("*No component quality data available.*\n\n")
            return

        f.write("### Component Quality Scores\n\n")
        f.write("| Component | Overall | Documentation | Integration | Cohesion | Rigor |\n")
        f.write("|-----------|---------|---------------|-------------|----------|-------|\n")

        for name, cq in sorted(
            component_quality.items(),
            key=lambda x: x[1].get("overall_score", 0),
            reverse=True
        ):
            overall = cq.get("overall_score", 0)
            doc = cq.get("documentation_score", 0)
            integration = cq.get("integration_score", 0)
            cohesion = cq.get("cohesion_score", 0)
            rigor = cq.get("rigor_score", 0)

            f.write(
                f"| `{name}` | {overall:.1f} | {doc:.1f} | "
                f"{integration:.1f} | {cohesion:.1f} | {rigor:.1f} |\n"
            )

        f.write("\n")

        # Components with issues
        f.write("### Components Requiring Attention\n\n")
        needs_attention = [
            (name, cq)
            for name, cq in component_quality.items()
            if cq.get("overall_score", 100) < 60
        ]

        if needs_attention:
            for name, cq in needs_attention:
                f.write(f"#### `{name}` (Score: {cq.get('overall_score', 0):.1f})\n\n")
                issues = cq.get("issues", [])
                recommendations = cq.get("recommendations", [])

                if issues:
                    f.write("**Issues:**\n")
                    for issue in issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")

                if recommendations:
                    f.write("**Recommendations:**\n")
                    for rec in recommendations:
                        f.write(f"- {rec}\n")
                    f.write("\n")
        else:
            f.write("*All components meet quality standards!* ✅\n\n")

        f.write("---\n\n")

    def _write_lint_report(self, f, lint: dict[str, Any]) -> None:
        """Write lint report section."""
        f.write("## Lint Report\n\n")

        summary = lint.get("summary", {})
        reports = lint.get("reports", [])

        f.write("### Summary\n\n")
        f.write(f"- **Files Checked:** {summary.get('total_files_checked', 0)}\n")
        f.write(f"- **Passed:** {summary.get('passed_files', 0)}\n")
        f.write(f"- **Failed:** {summary.get('failed_files', 0)}\n")
        f.write(f"- **Total Issues:** {summary.get('total_issues', 0)}\n")
        f.write(f"- **Fixable Issues:** {summary.get('fixable_issues', 0)}\n\n")

        issues_by_severity = summary.get("issues_by_severity", {})
        f.write("### Issues by Severity\n\n")
        f.write("| Severity | Count |\n")
        f.write("|----------|-------|\n")
        for severity in ["error", "warning", "info"]:
            count = issues_by_severity.get(severity, 0)
            emoji = "🔴" if severity == "error" else "🟡" if severity == "warning" else "🔵"
            f.write(f"| {emoji} {severity.capitalize()} | {count} |\n")
        f.write("\n")

        # Top files with most issues
        file_issue_counts = {}
        for report in reports:
            file = report.get("file", "")
            issue_count = len(report.get("issues", []))
            if issue_count > 0:
                file_issue_counts[file] = file_issue_counts.get(file, 0) + issue_count

        if file_issue_counts:
            f.write("### Files with Most Issues\n\n")
            top_files = sorted(
                file_issue_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]

            f.write("| File | Issue Count |\n")
            f.write("|------|-------------|\n")
            for file, count in top_files:
                f.write(f"| `{file}` | {count} |\n")
            f.write("\n")

        f.write("---\n\n")

    def _write_integrity_issues(self, f, integrity: dict[str, Any]) -> None:
        """Write integrity issues section."""
        f.write("## Integrity Issues\n\n")

        issues = integrity.get("issues", [])

        if not issues:
            f.write("*No integrity issues found!* ✅\n\n")
            return

        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for issue in issues:
            severity = issue.get("severity", "medium")
            by_severity[severity].append(issue)

        for severity in ["critical", "high", "medium", "low"]:
            issues_list = by_severity[severity]
            if not issues_list:
                continue

            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[severity]
            f.write(f"### {emoji} {severity.upper()} Issues ({len(issues_list)})\n\n")

            for issue in issues_list[:20]:  # Show top 20 per severity
                issue_type = issue.get("issue_type", "unknown")
                file = issue.get("file", "")
                line = issue.get("line", 0)
                description = issue.get("description", "")
                suggestion = issue.get("suggestion", "")

                f.write(f"#### {issue_type} - `{file}:{line}`\n\n")
                f.write(f"**Description:** {description}\n\n")
                if suggestion:
                    f.write(f"**Suggestion:** {suggestion}\n\n")

            if len(issues_list) > 20:
                f.write(f"*...and {len(issues_list) - 20} more {severity} issues.*\n\n")

        f.write("---\n\n")

    def _write_recommendations(self, f, assessment: dict[str, Any]) -> None:
        """Write recommendations section."""
        f.write("## Actionable Recommendations\n\n")

        recommendations = assessment.get("recommendations", [])

        if not recommendations:
            f.write("*No specific recommendations at this time.*\n\n")
            return

        f.write("Based on the audit findings, we recommend the following actions:\n\n")

        for i, rec in enumerate(recommendations, 1):
            f.write(f"{i}. {rec}\n")

        f.write("\n---\n\n")

    def _write_footer(self, f) -> None:
        """Write document footer."""
        f.write("## Appendix\n\n")
        f.write("### Methodology\n\n")
        f.write("This audit was conducted using the Project-AI Inspection & Audit System, ")
        f.write("which employs best-of-breed tools and institutional-grade standards:\n\n")
        f.write("- **Repository Inspection:** Automated file discovery and classification\n")
        f.write("- **Integrity Checking:** Dependency analysis, circular dependency detection\n")
        f.write("- **Quality Analysis:** Documentation coverage, maintainability index, cohesion scoring\n")
        f.write("- **Lint Checking:** Ruff, Flake8, Mypy, Bandit, YAML/JSON validation\n\n")

        f.write("### Report Version\n\n")
        f.write("- **Report Format Version:** 1.0.0\n")
        f.write("- **Tool Version:** Project-AI Inspection System 1.0.0\n\n")

        f.write("---\n\n")
        f.write(f"*Generated by Project-AI Inspection & Audit System - {datetime.now().strftime('%Y-%m-%d')}*\n")

    def _get_status_emoji(self, score: float, max_score: float) -> str:
        """Get status emoji based on score."""
        percentage = (score / max_score) * 100
        if percentage >= 80:
            return "✅ Excellent"
        elif percentage >= 60:
            return "🟢 Good"
        elif percentage >= 40:
            return "🟡 Fair"
        else:
            return "🔴 Needs Work"


__all__ = ["CatalogBuilder"]
