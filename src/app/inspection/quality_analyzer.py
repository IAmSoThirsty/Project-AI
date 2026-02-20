"""
Quality Analyzer - Institutional Density Assessment

This module provides comprehensive quality metrics and density assessment for:
- Code coverage analysis
- Documentation coverage
- Integration completeness
- Logical cohesion
- Architectural rigor

Produces institutional-grade quality metrics conforming to best-of-breed standards.

Author: Project-AI Team
Date: 2026-02-08
"""

import ast
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Quality metrics for a file or component."""

    file: str
    documentation_coverage: float  # 0.0 to 1.0
    code_coverage: float  # 0.0 to 1.0 (if available)
    complexity_score: int
    maintainability_index: float  # 0.0 to 100.0
    cohesion_score: float  # 0.0 to 1.0
    has_docstring: bool
    has_tests: bool
    has_type_hints: bool
    lines_of_code: int
    comment_ratio: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentQuality:
    """Quality assessment for a component/subsystem."""

    component: str
    overall_score: float  # 0.0 to 100.0
    documentation_score: float
    integration_score: float
    cohesion_score: float
    rigor_score: float
    file_count: int
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class QualityAnalyzer:
    """
    Comprehensive quality analyzer for institutional density assessment.

    Analyzes code quality, documentation coverage, integration completeness,
    and architectural rigor across the entire repository.
    """

    def __init__(
        self,
        repo_root: str | Path,
        file_inventory: dict[str, Any],
        test_results: dict[str, Any] | None = None,
    ):
        """
        Initialize the quality analyzer.

        Args:
            repo_root: Root directory of the repository
            file_inventory: File inventory from RepositoryInspector
            test_results: Optional test coverage data
        """
        self.repo_root = Path(repo_root).resolve()
        self.file_inventory = file_inventory
        self.test_results = test_results or {}
        self.metrics: dict[str, QualityMetrics] = {}
        self.component_quality: dict[str, ComponentQuality] = {}

        logger.info("Initialized QualityAnalyzer for: %s", self.repo_root)

    def analyze(self) -> dict[str, Any]:
        """
        Perform comprehensive quality analysis.

        Returns:
            Dictionary containing quality metrics and assessments
        """
        logger.info("Starting quality analysis...")

        try:
            # Phase 1: Analyze each file
            self._analyze_files()

            # Phase 2: Analyze components
            self._analyze_components()

            # Phase 3: Compute aggregate metrics
            aggregate = self._compute_aggregate_metrics()

            logger.info(
                "Quality analysis complete: %d files analyzed, %d components assessed",
                len(self.metrics),
                len(self.component_quality),
            )

            return {
                "file_metrics": {k: asdict(v) for k, v in self.metrics.items()},
                "component_quality": {k: asdict(v) for k, v in self.component_quality.items()},
                "aggregate_metrics": aggregate,
            }

        except Exception as e:
            logger.exception("Quality analysis failed: %s", e)
            raise

    def _analyze_files(self) -> None:
        """Analyze quality metrics for each file."""
        logger.info("Analyzing file quality metrics...")

        for file_path, file_info in self.file_inventory.get("files", {}).items():
            if file_info.get("file_type") not in ["python_module", "python_test"]:
                continue

            try:
                full_path = self.repo_root / file_path
                if not full_path.exists():
                    continue

                with open(full_path, encoding="utf-8") as f:
                    content = f.read()

                metrics = self._compute_file_metrics(content, file_info)
                self.metrics[file_path] = metrics

            except Exception as e:
                logger.debug("Error analyzing %s: %s", file_path, e)

    def _compute_file_metrics(self, content: str, file_info: dict[str, Any]) -> QualityMetrics:
        """Compute quality metrics for a single file."""
        lines = content.splitlines()
        total_lines = len([line for line in lines if line.strip()])

        # Documentation coverage
        doc_coverage = self._compute_doc_coverage(content, file_info)

        # Comment ratio
        comment_lines = len([line for line in lines if line.strip().startswith("#")])
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0.0

        # Complexity score (from file_info or compute)
        complexity = file_info.get("complexity_score", 0)

        # Maintainability index (simplified Halstead)
        maintainability = self._compute_maintainability_index(total_lines, complexity, comment_ratio)

        # Cohesion score
        cohesion = self._compute_cohesion_score(file_info)

        # Type hints check
        has_type_hints = self._check_type_hints(content)

        # Check if tests exist
        has_tests = self._check_has_tests(file_info)

        # Code coverage (from test results if available)
        code_coverage = self._get_code_coverage(file_info.get("path", ""))

        return QualityMetrics(
            file=file_info.get("path", ""),
            documentation_coverage=doc_coverage,
            code_coverage=code_coverage,
            complexity_score=complexity,
            maintainability_index=maintainability,
            cohesion_score=cohesion,
            has_docstring=bool(file_info.get("docstring")),
            has_tests=has_tests,
            has_type_hints=has_type_hints,
            lines_of_code=total_lines,
            comment_ratio=comment_ratio,
        )

    def _compute_doc_coverage(self, content: str, file_info: dict[str, Any]) -> float:
        """Compute documentation coverage for a file."""
        try:
            tree = ast.parse(content)

            documented_items = 0
            total_items = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1

            return documented_items / total_items if total_items > 0 else 0.0

        except Exception:
            return 0.0

    def _compute_maintainability_index(self, lines: int, complexity: int, comment_ratio: float) -> float:
        """
        Compute maintainability index (simplified).

        Based on Microsoft's maintainability index formula (simplified version).
        Scale: 0-100, where higher is better.
        """
        if lines == 0:
            return 100.0

        # Simplified formula
        volume = lines * 1.5  # Simplified volume metric
        mi = 171 - 5.2 * (complexity / max(lines, 1)) - 0.23 * volume
        mi += 16.2 * comment_ratio * 100

        # Normalize to 0-100
        mi = max(0.0, min(100.0, mi))

        return round(mi, 2)

    def _compute_cohesion_score(self, file_info: dict[str, Any]) -> float:
        """
        Compute cohesion score based on class/function organization.

        Higher score indicates better organization and single responsibility.
        """
        classes = len(file_info.get("classes", []))
        functions = len(file_info.get("functions", []))
        lines = file_info.get("lines_of_code", 1)

        # Ideal: 1-3 classes per file, reasonable function count
        if classes == 0:
            # Module with only functions
            if functions <= 10:
                return 0.9
            elif functions <= 20:
                return 0.7
            else:
                return 0.5
        elif classes <= 3:
            # Good organization
            if lines / classes < 500:  # Not too large per class
                return 0.9
            else:
                return 0.7
        else:
            # Too many classes in one file
            return 0.5

    def _check_type_hints(self, content: str) -> bool:
        """Check if the file uses type hints."""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for return type or argument annotations
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        return True

            return False

        except Exception:
            return False

    def _check_has_tests(self, file_info: dict[str, Any]) -> bool:
        """Check if the file has associated tests."""
        file_path = file_info.get("relative_path", "")

        # Check if it's a test file itself
        if file_info.get("is_test"):
            return True

        # Check if there's a corresponding test file
        for test_path in self.file_inventory.get("files", {}):
            test_info = self.file_inventory["files"][test_path]
            if test_info.get("is_test") and file_path.replace(".", "_") in test_path:
                return True

        return False

    def _get_code_coverage(self, file_path: str) -> float:
        """Get code coverage for a file from test results."""
        if not self.test_results:
            return 0.0

        coverage_data = self.test_results.get("coverage", {})
        return coverage_data.get(file_path, 0.0)

    def _analyze_components(self) -> None:
        """Analyze quality for each component."""
        logger.info("Analyzing component quality...")

        components = self.file_inventory.get("components", {})

        for comp_name, comp_info in components.items():
            comp_files = comp_info.get("files", [])

            # Get metrics for all files in component
            file_metrics = [self.metrics[f] for f in comp_files if f in self.metrics]

            if not file_metrics:
                continue

            # Compute component quality
            quality = self._compute_component_quality(comp_name, comp_info, file_metrics)
            self.component_quality[comp_name] = quality

    def _compute_component_quality(
        self,
        comp_name: str,
        comp_info: dict[str, Any],
        file_metrics: list[QualityMetrics],
    ) -> ComponentQuality:
        """Compute quality assessment for a component."""
        if not file_metrics:
            return ComponentQuality(
                component=comp_name,
                overall_score=0.0,
                documentation_score=0.0,
                integration_score=0.0,
                cohesion_score=0.0,
                rigor_score=0.0,
                file_count=0,
            )

        # Average documentation coverage
        doc_score = (sum(m.documentation_coverage for m in file_metrics) / len(file_metrics)) * 100

        # Integration score (has tests + type hints + low complexity)
        integration_factors = [
            sum(1 for m in file_metrics if m.has_tests) / len(file_metrics),
            sum(1 for m in file_metrics if m.has_type_hints) / len(file_metrics),
            sum(1 for m in file_metrics if m.complexity_score < 20) / len(file_metrics),
        ]
        integration_score = (sum(integration_factors) / len(integration_factors)) * 100

        # Average cohesion
        cohesion_score = (sum(m.cohesion_score for m in file_metrics) / len(file_metrics)) * 100

        # Rigor score (maintainability + documentation + type hints)
        rigor_factors = [
            sum(m.maintainability_index for m in file_metrics) / len(file_metrics) / 100,
            sum(1 for m in file_metrics if m.has_docstring) / len(file_metrics),
            sum(1 for m in file_metrics if m.has_type_hints) / len(file_metrics),
        ]
        rigor_score = (sum(rigor_factors) / len(rigor_factors)) * 100

        # Overall score (weighted average)
        overall_score = doc_score * 0.25 + integration_score * 0.25 + cohesion_score * 0.25 + rigor_score * 0.25

        # Generate issues and recommendations
        issues = []
        recommendations = []

        if doc_score < 50:
            issues.append("Low documentation coverage")
            recommendations.append("Add docstrings to classes and functions")

        if integration_score < 50:
            issues.append("Insufficient test coverage")
            recommendations.append("Increase test coverage and add type hints")

        if cohesion_score < 60:
            issues.append("Low cohesion")
            recommendations.append("Refactor large files into smaller, focused modules")

        return ComponentQuality(
            component=comp_name,
            overall_score=round(overall_score, 2),
            documentation_score=round(doc_score, 2),
            integration_score=round(integration_score, 2),
            cohesion_score=round(cohesion_score, 2),
            rigor_score=round(rigor_score, 2),
            file_count=len(file_metrics),
            issues=issues,
            recommendations=recommendations,
        )

    def _compute_aggregate_metrics(self) -> dict[str, Any]:
        """Compute aggregate quality metrics across the repository."""
        if not self.metrics:
            return {}

        total_files = len(self.metrics)
        all_metrics = list(self.metrics.values())

        return {
            "total_files_analyzed": total_files,
            "average_documentation_coverage": round(
                sum(m.documentation_coverage for m in all_metrics) / total_files, 3
            ),
            "average_code_coverage": round(sum(m.code_coverage for m in all_metrics) / total_files, 3),
            "average_maintainability_index": round(sum(m.maintainability_index for m in all_metrics) / total_files, 2),
            "average_cohesion_score": round(sum(m.cohesion_score for m in all_metrics) / total_files, 3),
            "files_with_docstrings": sum(1 for m in all_metrics if m.has_docstring),
            "files_with_tests": sum(1 for m in all_metrics if m.has_tests),
            "files_with_type_hints": sum(1 for m in all_metrics if m.has_type_hints),
            "total_lines_of_code": sum(m.lines_of_code for m in all_metrics),
            "average_complexity": round(sum(m.complexity_score for m in all_metrics) / total_files, 2),
            "component_count": len(self.component_quality),
            "component_quality_distribution": self._get_quality_distribution(),
        }

    def _get_quality_distribution(self) -> dict[str, int]:
        """Get distribution of component quality scores."""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}

        for comp_quality in self.component_quality.values():
            score = comp_quality.overall_score

            if score >= 80:
                distribution["excellent"] += 1
            elif score >= 60:
                distribution["good"] += 1
            elif score >= 40:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1

        return distribution


__all__ = ["QualityAnalyzer", "QualityMetrics", "ComponentQuality"]
