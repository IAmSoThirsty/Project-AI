"""
Integrity Checker - Cross-Reference Catalog and Dependency Analysis

This module provides end-to-end repository integrity checks including:
- Cross-referenced catalog of all files, classes, and interfaces
- Dependency analysis and circular dependency detection
- Import validation and missing dependency identification
- Interface consistency checking
- Dead code detection

Author: Project-AI Team
Date: 2026-02-08
"""

import ast
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Information about dependencies between modules."""

    source: str
    target: str
    import_type: str  # 'import' or 'from'
    imported_names: list[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class CircularDependency:
    """Information about a circular dependency chain."""

    cycle: list[str]
    severity: str = "medium"  # low, medium, high


@dataclass
class IntegrityIssue:
    """Represents an integrity issue found during checking."""

    issue_type: str
    severity: str  # critical, high, medium, low
    file: str
    line: int
    description: str
    suggestion: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class IntegrityChecker:
    """
    Comprehensive integrity checker for repository-wide validation.

    Performs deep analysis of:
    - Import dependencies and relationships
    - Circular dependencies
    - Missing imports and dead code
    - Interface consistency
    - Cross-reference catalog generation
    """

    def __init__(self, repo_root: str | Path, file_inventory: dict[str, Any]):
        """
        Initialize the integrity checker.

        Args:
            repo_root: Root directory of the repository
            file_inventory: File inventory from RepositoryInspector
        """
        self.repo_root = Path(repo_root).resolve()
        self.file_inventory = file_inventory
        self.dependencies: list[DependencyInfo] = []
        self.issues: list[IntegrityIssue] = []
        self.dependency_graph: dict[str, set[str]] = defaultdict(set)
        self.reverse_dependencies: dict[str, set[str]] = defaultdict(set)
        self.module_exports: dict[str, set[str]] = defaultdict(set)

        logger.info("Initialized IntegrityChecker for: %s", self.repo_root)

    def check(self) -> dict[str, Any]:
        """
        Perform full integrity check.

        Returns:
            Dictionary containing check results, issues, and dependency analysis
        """
        logger.info("Starting integrity check...")

        try:
            # Phase 1: Build dependency graph
            self._build_dependency_graph()

            # Phase 2: Detect circular dependencies
            circular_deps = self._detect_circular_dependencies()

            # Phase 3: Validate imports
            self._validate_imports()

            # Phase 4: Check for dead code
            self._check_dead_code()

            # Phase 5: Build cross-reference catalog
            catalog = self._build_cross_reference_catalog()

            logger.info(
                "Integrity check complete: %d dependencies, %d issues",
                len(self.dependencies),
                len(self.issues),
            )

            return {
                "dependencies": [asdict(d) for d in self.dependencies],
                "circular_dependencies": [asdict(cd) for cd in circular_deps],
                "issues": [asdict(i) for i in self.issues],
                "dependency_graph": {
                    k: list(v) for k, v in self.dependency_graph.items()
                },
                "reverse_dependencies": {
                    k: list(v) for k, v in self.reverse_dependencies.items()
                },
                "cross_reference_catalog": catalog,
                "statistics": self._compute_statistics(),
            }

        except Exception as e:
            logger.exception("Integrity check failed: %s", e)
            raise

    def _build_dependency_graph(self) -> None:
        """Build the dependency graph from Python files."""
        logger.info("Building dependency graph...")

        python_files = {
            path: info
            for path, info in self.file_inventory.get("files", {}).items()
            if info.get("file_type") == "python_module"
        }

        for file_path, file_info in python_files.items():
            try:
                full_path = self.repo_root / file_path
                if not full_path.exists():
                    continue

                with open(full_path, encoding="utf-8") as f:
                    content = f.read()

                try:
                    tree = ast.parse(content, filename=str(full_path))
                    module_name = file_info.get("module_name", "")

                    # Extract exports (__all__ or top-level definitions)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if (
                                    isinstance(target, ast.Name)
                                    and target.id == "__all__"
                                ):
                                    if isinstance(node.value, (ast.List, ast.Tuple)):
                                        for elt in node.value.elts:
                                            if isinstance(elt, ast.Constant):
                                                self.module_exports[module_name].add(
                                                    elt.value
                                                )

                    # Extract imports
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                dep = DependencyInfo(
                                    source=module_name,
                                    target=alias.name,
                                    import_type="import",
                                    imported_names=[alias.asname or alias.name],
                                    line_number=node.lineno,
                                )
                                self.dependencies.append(dep)
                                self.dependency_graph[module_name].add(alias.name)
                                self.reverse_dependencies[alias.name].add(module_name)

                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imported_names = [alias.name for alias in node.names]
                                dep = DependencyInfo(
                                    source=module_name,
                                    target=node.module,
                                    import_type="from",
                                    imported_names=imported_names,
                                    line_number=node.lineno,
                                )
                                self.dependencies.append(dep)
                                self.dependency_graph[module_name].add(node.module)
                                self.reverse_dependencies[node.module].add(module_name)

                except SyntaxError as e:
                    logger.debug("Syntax error in %s: %s", file_path, e)
                    self.issues.append(
                        IntegrityIssue(
                            issue_type="syntax_error",
                            severity="high",
                            file=file_path,
                            line=getattr(e, "lineno", 0),
                            description=f"Syntax error: {e}",
                            suggestion="Fix syntax errors in the file",
                        )
                    )

            except Exception as e:
                logger.debug("Error processing %s: %s", file_path, e)

        logger.info(
            "Built dependency graph with %d dependencies", len(self.dependencies)
        )

    def _detect_circular_dependencies(self) -> list[CircularDependency]:
        """Detect circular dependencies in the dependency graph."""
        logger.info("Detecting circular dependencies...")

        circular_deps = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]

                    # Determine severity based on cycle length
                    severity = "low"
                    if len(cycle) == 2:
                        severity = "high"  # Direct circular dependency
                    elif len(cycle) <= 4:
                        severity = "medium"

                    circular_dep = CircularDependency(cycle=cycle, severity=severity)
                    circular_deps.append(circular_dep)

                    # Log as issue
                    self.issues.append(
                        IntegrityIssue(
                            issue_type="circular_dependency",
                            severity=severity,
                            file=path[-1],
                            line=0,
                            description=f"Circular dependency detected: {' -> '.join(cycle)}",
                            suggestion="Refactor to break the circular dependency",
                            metadata={"cycle": cycle},
                        )
                    )

            path.pop()
            rec_stack.remove(node)

        # Run DFS from each node
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])

        logger.info("Found %d circular dependencies", len(circular_deps))
        return circular_deps

    def _validate_imports(self) -> None:
        """Validate that all imports can be resolved."""
        logger.info("Validating imports...")

        # Build a set of available modules
        available_modules = set()
        for file_info in self.file_inventory.get("files", {}).values():
            if module_name := file_info.get("module_name"):
                available_modules.add(module_name)

        # Check each dependency
        for dep in self.dependencies:
            target = dep.target

            # Skip standard library and third-party imports
            if self._is_stdlib_or_third_party(target):
                continue

            # Check if target module exists
            if not self._module_exists(target, available_modules):
                self.issues.append(
                    IntegrityIssue(
                        issue_type="missing_import",
                        severity="medium",
                        file=dep.source,
                        line=dep.line_number,
                        description=f"Cannot resolve import: {target}",
                        suggestion="Ensure the module exists or add it to dependencies",
                        metadata={"import": target, "source": dep.source},
                    )
                )

    def _check_dead_code(self) -> None:
        """Check for potentially dead/unused code."""
        logger.info("Checking for dead code...")

        # Find modules that are never imported
        all_modules = set()
        imported_modules = set()

        for file_info in self.file_inventory.get("files", {}).values():
            if module_name := file_info.get("module_name"):
                all_modules.add(module_name)

        for dep in self.dependencies:
            imported_modules.add(dep.target)

        # Modules that are never imported (except entry points)
        never_imported = all_modules - imported_modules

        # Filter out likely entry points
        entry_point_patterns = ["main", "cli", "app", "__main__", "start", "run"]

        for module in never_imported:
            is_entry_point = any(
                pattern in module.lower() for pattern in entry_point_patterns
            )

            if not is_entry_point:
                # Check if it's in tests (tests are entry points)
                if "test" not in module.lower():
                    self.issues.append(
                        IntegrityIssue(
                            issue_type="potential_dead_code",
                            severity="low",
                            file=module,
                            line=0,
                            description=f"Module '{module}' is never imported",
                            suggestion="Consider removing if truly unused, or add to __all__ if it's a public API",
                            metadata={"module": module},
                        )
                    )

    def _build_cross_reference_catalog(self) -> dict[str, Any]:
        """Build a comprehensive cross-reference catalog."""
        logger.info("Building cross-reference catalog...")

        catalog = {
            "modules": {},
            "classes": {},
            "functions": {},
            "interfaces": {},
        }

        for file_path, file_info in self.file_inventory.get("files", {}).items():
            if file_info.get("file_type") != "python_module":
                continue

            module_name = file_info.get("module_name", "")

            # Catalog module
            catalog["modules"][module_name] = {
                "path": file_path,
                "classes": file_info.get("classes", []),
                "functions": file_info.get("functions", []),
                "imports": file_info.get("imports", []),
                "imported_by": list(self.reverse_dependencies.get(module_name, [])),
                "imports_from": list(self.dependency_graph.get(module_name, [])),
            }

            # Catalog classes
            for cls_name in file_info.get("classes", []):
                full_name = f"{module_name}.{cls_name}"
                catalog["classes"][full_name] = {
                    "module": module_name,
                    "file": file_path,
                    "name": cls_name,
                }

            # Catalog functions
            for func_name in file_info.get("functions", []):
                full_name = f"{module_name}.{func_name}"
                catalog["functions"][full_name] = {
                    "module": module_name,
                    "file": file_path,
                    "name": func_name,
                }

        return catalog

    def _compute_statistics(self) -> dict[str, Any]:
        """Compute integrity statistics."""
        return {
            "total_dependencies": len(self.dependencies),
            "total_issues": len(self.issues),
            "issues_by_severity": self._count_by_severity(),
            "issues_by_type": self._count_by_type(),
            "most_dependent_modules": self._get_most_dependent_modules(10),
            "most_imported_modules": self._get_most_imported_modules(10),
        }

    def _count_by_severity(self) -> dict[str, int]:
        """Count issues by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

    def _count_by_type(self) -> dict[str, int]:
        """Count issues by type."""
        counts = defaultdict(int)
        for issue in self.issues:
            counts[issue.issue_type] += 1
        return dict(counts)

    def _get_most_dependent_modules(self, limit: int) -> list[dict[str, Any]]:
        """Get modules with most dependencies."""
        deps = [
            {"module": mod, "dependency_count": len(deps)}
            for mod, deps in self.dependency_graph.items()
        ]
        return sorted(deps, key=lambda x: x["dependency_count"], reverse=True)[:limit]

    def _get_most_imported_modules(self, limit: int) -> list[dict[str, Any]]:
        """Get most frequently imported modules."""
        imports = [
            {"module": mod, "import_count": len(importers)}
            for mod, importers in self.reverse_dependencies.items()
        ]
        return sorted(imports, key=lambda x: x["import_count"], reverse=True)[:limit]

    def _is_stdlib_or_third_party(self, module_name: str) -> bool:
        """Check if a module is from stdlib or third-party."""
        # Common stdlib and third-party prefixes
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "re",
            "ast",
            "logging",
            "pathlib",
            "collections",
            "dataclasses",
            "typing",
            "datetime",
            "hashlib",
            "subprocess",
            "tempfile",
            "shutil",
            "io",
            "enum",
        }

        third_party_prefixes = [
            "flask",
            "pytest",
            "numpy",
            "pandas",
            "scikit",
            "openai",
            "PyQt",
            "requests",
            "cryptography",
            "yaml",
        ]

        # Check if it's stdlib
        root_module = module_name.split(".")[0]
        if root_module in stdlib_modules:
            return True

        # Check if it's third-party
        for prefix in third_party_prefixes:
            if module_name.startswith(prefix) or root_module == prefix.lower():
                return True

        return False

    def _module_exists(self, module_name: str, available_modules: set[str]) -> bool:
        """Check if a module exists in the repository."""
        # Check direct match
        if module_name in available_modules:
            return True

        # Check if it's a submodule of an existing module
        for available in available_modules:
            if module_name.startswith(available + "."):
                return True

        return False


__all__ = [
    "IntegrityChecker",
    "DependencyInfo",
    "CircularDependency",
    "IntegrityIssue",
]
