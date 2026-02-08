"""
Repository Inspector - Full File Inventory and Classification

This module provides comprehensive repository-wide inventory and classification
of all files, modules, components, and subsystems with detailed status labeling.

Capabilities:
- Recursive directory traversal with configurable exclusions
- File type classification and categorization
- Status labeling (implemented, planned, future, deprecated, etc.)
- Module and component identification
- Size and complexity metrics
- Integration with version control metadata

Status Classifications:
- IMPLEMENTED: Fully implemented and in active use
- PLANNED: Documented but not yet implemented
- FUTURE_UPDATE: Implemented but marked for updates
- NOT_IN_USE: Implemented but not currently utilized
- WOULD_BE_NICE: Desirable enhancement
- COULD_BE_NICE: Optional enhancement
- SHOULD_HAVE: Important missing component
- DEPRECATED: Marked for removal
- UNKNOWN: Status cannot be determined

Author: Project-AI Team
Date: 2026-02-08
"""

import ast
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FileStatus(str, Enum):
    """Status classification for files and components."""

    IMPLEMENTED = "implemented"
    PLANNED = "planned"
    FUTURE_UPDATE = "future_update"
    NOT_IN_USE = "not_in_use"
    WOULD_BE_NICE = "would_be_nice"
    COULD_BE_NICE = "could_be_nice"
    SHOULD_HAVE = "should_have"
    DEPRECATED = "deprecated"
    UNKNOWN = "unknown"


class FileType(str, Enum):
    """File type classifications."""

    PYTHON_MODULE = "python_module"
    PYTHON_TEST = "python_test"
    PYTHON_SCRIPT = "python_script"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    RUST = "rust"
    CONFIG = "config"
    MARKDOWN = "markdown"
    YAML = "yaml"
    JSON = "json"
    DOCKER = "docker"
    SHELL = "shell"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    OTHER = "other"


@dataclass
class FileInfo:
    """Detailed information about a file in the repository."""

    path: str
    relative_path: str
    name: str
    extension: str
    file_type: FileType
    status: FileStatus
    size_bytes: int
    lines_of_code: int = 0
    is_test: bool = False
    is_executable: bool = False
    module_name: str = ""
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    docstring: str = ""
    complexity_score: int = 0
    last_modified: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentInfo:
    """Information about a logical component or subsystem."""

    name: str
    path: str
    component_type: str  # module, subsystem, service, agent, etc.
    status: FileStatus
    files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RepositoryInspector:
    """
    Comprehensive repository inspector for file inventory and classification.

    This class provides deep analysis of the repository structure, including
    file classification, status determination, and component identification.
    """

    # Default exclusion patterns
    DEFAULT_EXCLUSIONS = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".hypothesis",
        "node_modules",
        ".venv",
        "venv",
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
        ".mypy_cache",
        ".ruff_cache",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
    ]

    # File type mappings
    EXTENSION_MAP = {
        ".py": FileType.PYTHON_MODULE,
        ".js": FileType.JAVASCRIPT,
        ".jsx": FileType.JAVASCRIPT,
        ".ts": FileType.TYPESCRIPT,
        ".tsx": FileType.TYPESCRIPT,
        ".java": FileType.JAVA,
        ".rs": FileType.RUST,
        ".yaml": FileType.YAML,
        ".yml": FileType.YAML,
        ".json": FileType.JSON,
        ".md": FileType.MARKDOWN,
        ".sh": FileType.SHELL,
        ".bash": FileType.SHELL,
        ".sql": FileType.SQL,
        ".html": FileType.HTML,
        ".css": FileType.CSS,
        ".scss": FileType.CSS,
        "Dockerfile": FileType.DOCKER,
        ".toml": FileType.CONFIG,
        ".ini": FileType.CONFIG,
        ".cfg": FileType.CONFIG,
        ".conf": FileType.CONFIG,
    }

    # Status detection patterns in comments/docstrings
    STATUS_PATTERNS = {
        FileStatus.PLANNED: [
            r"TODO",
            r"PLANNED",
            r"NOT YET IMPLEMENTED",
            r"STUB IMPLEMENTATION",
        ],
        FileStatus.FUTURE_UPDATE: [
            r"FUTURE ENHANCEMENT",
            r"FUTURE UPDATE",
            r"TO BE IMPROVED",
            r"NEEDS REFACTORING",
        ],
        FileStatus.DEPRECATED: [
            r"DEPRECATED",
            r"DO NOT USE",
            r"OBSOLETE",
            r"LEGACY",
        ],
        FileStatus.NOT_IN_USE: [
            r"NOT IN USE",
            r"UNUSED",
            r"DISABLED",
        ],
    }

    def __init__(
        self,
        repo_root: str | Path,
        exclusions: list[str] | None = None,
        include_git_metadata: bool = True,
    ):
        """
        Initialize the repository inspector.

        Args:
            repo_root: Root directory of the repository
            exclusions: Additional exclusion patterns (adds to defaults)
            include_git_metadata: Whether to include git metadata in analysis
        """
        self.repo_root = Path(repo_root).resolve()
        self.exclusions = self.DEFAULT_EXCLUSIONS.copy()
        if exclusions:
            self.exclusions.extend(exclusions)
        self.include_git_metadata = include_git_metadata

        self.files: dict[str, FileInfo] = {}
        self.components: dict[str, ComponentInfo] = {}
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "by_type": {},
            "by_status": {},
            "by_component": {},
        }

        logger.info("Initialized RepositoryInspector for: %s", self.repo_root)

    def inspect(self) -> dict[str, Any]:
        """
        Perform full repository inspection.

        Returns:
            Dictionary containing complete inspection results including
            files, components, and statistics
        """
        logger.info("Starting repository inspection...")

        try:
            # Phase 1: Discover all files
            self._discover_files()

            # Phase 2: Analyze each file
            self._analyze_files()

            # Phase 3: Identify components and subsystems
            self._identify_components()

            # Phase 4: Compute statistics
            self._compute_statistics()

            logger.info(
                "Inspection complete: %d files, %d components",
                self.stats["total_files"],
                len(self.components),
            )

            return self.get_results()

        except Exception as e:
            logger.exception("Repository inspection failed: %s", e)
            raise

    def _discover_files(self) -> None:
        """Discover all files in the repository."""
        logger.info("Discovering files in repository...")

        for root, dirs, files in os.walk(self.repo_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]

            rel_root = Path(root).relative_to(self.repo_root)

            for filename in files:
                if self._should_exclude(filename):
                    continue

                filepath = Path(root) / filename
                rel_path = rel_root / filename

                # Create basic file info
                file_info = FileInfo(
                    path=str(filepath),
                    relative_path=str(rel_path),
                    name=filename,
                    extension=filepath.suffix.lower(),
                    file_type=self._determine_file_type(filepath),
                    status=FileStatus.UNKNOWN,
                    size_bytes=filepath.stat().st_size,
                    is_test=self._is_test_file(filepath),
                    is_executable=os.access(filepath, os.X_OK),
                )

                self.files[str(rel_path)] = file_info

        logger.info("Discovered %d files", len(self.files))

    def _analyze_files(self) -> None:
        """Analyze each discovered file in detail."""
        logger.info("Analyzing discovered files...")

        for rel_path, file_info in self.files.items():
            try:
                # Analyze based on file type
                if file_info.file_type == FileType.PYTHON_MODULE:
                    self._analyze_python_file(file_info)
                elif file_info.file_type == FileType.MARKDOWN:
                    self._analyze_markdown_file(file_info)
                elif file_info.file_type in [FileType.YAML, FileType.JSON]:
                    self._analyze_config_file(file_info)

                # Determine status
                file_info.status = self._determine_status(file_info)

            except Exception as e:
                logger.debug("Error analyzing %s: %s", rel_path, e)
                file_info.metadata["analysis_error"] = str(e)

    def _analyze_python_file(self, file_info: FileInfo) -> None:
        """Analyze a Python file for detailed information."""
        try:
            with open(file_info.path, encoding="utf-8") as f:
                content = f.read()

            file_info.lines_of_code = len(
                [line for line in content.splitlines() if line.strip()]
            )

            # Parse AST for structure
            try:
                tree = ast.parse(content, filename=file_info.path)

                # Extract module docstring
                if (
                    ast.get_docstring(tree)
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                ):
                    file_info.docstring = ast.get_docstring(tree) or ""

                # Extract classes and functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        file_info.classes.append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        file_info.functions.append(node.name)
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                file_info.imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            file_info.imports.append(node.module)

                # Simple complexity score (number of classes + functions)
                file_info.complexity_score = len(file_info.classes) + len(
                    file_info.functions
                )

                # Module name from path
                file_info.module_name = self._path_to_module_name(
                    file_info.relative_path
                )

            except SyntaxError as e:
                logger.debug("Syntax error in %s: %s", file_info.path, e)
                file_info.metadata["syntax_error"] = str(e)

        except Exception as e:
            logger.debug("Error reading Python file %s: %s", file_info.path, e)
            file_info.metadata["read_error"] = str(e)

    def _analyze_markdown_file(self, file_info: FileInfo) -> None:
        """Analyze a markdown file."""
        try:
            with open(file_info.path, encoding="utf-8") as f:
                content = f.read()

            file_info.lines_of_code = len(content.splitlines())

            # Extract first heading as description
            for line in content.splitlines():
                if line.startswith("# "):
                    file_info.docstring = line[2:].strip()
                    break

        except Exception as e:
            logger.debug("Error reading markdown file %s: %s", file_info.path, e)

    def _analyze_config_file(self, file_info: FileInfo) -> None:
        """Analyze a configuration file."""
        try:
            with open(file_info.path, encoding="utf-8") as f:
                content = f.read()

            file_info.lines_of_code = len(
                [line for line in content.splitlines() if line.strip()]
            )

        except Exception as e:
            logger.debug("Error reading config file %s: %s", file_info.path, e)

    def _identify_components(self) -> None:
        """Identify logical components and subsystems."""
        logger.info("Identifying components and subsystems...")

        # Group files by directory to identify components
        component_dirs: dict[str, list[str]] = {}

        for rel_path in self.files:
            parts = Path(rel_path).parts
            if len(parts) > 1:
                # Use top-level directory or module as component
                if parts[0] in ["src", "tests", "web"]:
                    component_key = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
                else:
                    component_key = parts[0]

                if component_key not in component_dirs:
                    component_dirs[component_key] = []
                component_dirs[component_key].append(rel_path)

        # Create component info for each directory group
        for component_name, file_list in component_dirs.items():
            component_type = self._determine_component_type(component_name)
            status = self._determine_component_status(file_list)

            self.components[component_name] = ComponentInfo(
                name=component_name,
                path=component_name,
                component_type=component_type,
                status=status,
                files=file_list,
                description=f"Component: {component_name}",
            )

        logger.info("Identified %d components", len(self.components))

    def _compute_statistics(self) -> None:
        """Compute aggregate statistics."""
        self.stats["total_files"] = len(self.files)
        self.stats["total_lines"] = sum(f.lines_of_code for f in self.files.values())

        # By file type
        for file_info in self.files.values():
            ftype = file_info.file_type.value
            self.stats["by_type"][ftype] = self.stats["by_type"].get(ftype, 0) + 1

        # By status
        for file_info in self.files.values():
            status = file_info.status.value
            self.stats["by_status"][status] = self.stats["by_status"].get(status, 0) + 1

        # By component
        for component_name, component_info in self.components.items():
            self.stats["by_component"][component_name] = {
                "file_count": len(component_info.files),
                "status": component_info.status.value,
                "type": component_info.component_type,
            }

    def _determine_file_type(self, filepath: Path) -> FileType:
        """Determine the type of a file."""
        # Check filename patterns
        if filepath.name == "Dockerfile" or filepath.name.startswith("Dockerfile."):
            return FileType.DOCKER

        # Check extension
        ext = filepath.suffix.lower()
        if ext in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[ext]

        # Check if it's a Python test
        if ext == ".py" and self._is_test_file(filepath):
            return FileType.PYTHON_TEST

        return FileType.OTHER

    def _determine_status(self, file_info: FileInfo) -> FileStatus:
        """Determine the status of a file based on content analysis."""
        # Check docstring and comments for status keywords
        content_to_check = file_info.docstring.upper()

        for status, patterns in self.STATUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_to_check):
                    return status

        # If it's a test file with tests, it's implemented
        if file_info.is_test and file_info.functions:
            return FileStatus.IMPLEMENTED

        # If it has classes or functions, assume implemented
        if file_info.classes or file_info.functions:
            return FileStatus.IMPLEMENTED

        # If it's a config file with content, it's implemented
        if file_info.file_type in [FileType.CONFIG, FileType.YAML, FileType.JSON]:
            if file_info.lines_of_code > 0:
                return FileStatus.IMPLEMENTED

        return FileStatus.UNKNOWN

    def _determine_component_type(self, component_name: str) -> str:
        """Determine the type of a component based on its name."""
        name_lower = component_name.lower()

        if "agent" in name_lower:
            return "agent"
        elif "test" in name_lower:
            return "test_suite"
        elif "api" in name_lower:
            return "api"
        elif "gui" in name_lower or "ui" in name_lower:
            return "ui"
        elif "core" in name_lower:
            return "core_system"
        elif "config" in name_lower:
            return "configuration"
        elif "tool" in name_lower or "script" in name_lower:
            return "tooling"
        elif "doc" in name_lower:
            return "documentation"
        else:
            return "module"

    def _determine_component_status(self, file_list: list[str]) -> FileStatus:
        """Determine the status of a component based on its files."""
        statuses = [self.files[f].status for f in file_list if f in self.files]

        if not statuses:
            return FileStatus.UNKNOWN

        # If all are implemented, component is implemented
        if all(s == FileStatus.IMPLEMENTED for s in statuses):
            return FileStatus.IMPLEMENTED

        # If any are deprecated, component might be deprecated
        if any(s == FileStatus.DEPRECATED for s in statuses):
            return FileStatus.DEPRECATED

        # If any are planned, component is in development
        if any(s == FileStatus.PLANNED for s in statuses):
            return FileStatus.PLANNED

        # Mixed status - assume in active development
        return FileStatus.FUTURE_UPDATE

    def _is_test_file(self, filepath: Path) -> bool:
        """Check if a file is a test file."""
        return (
            "test" in str(filepath).lower()
            or filepath.name.startswith("test_")
            or "spec" in filepath.name.lower()
        )

    def _should_exclude(self, name: str) -> bool:
        """Check if a file or directory should be excluded."""
        for pattern in self.exclusions:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or name.startswith(pattern):
                return True
        return False

    def _path_to_module_name(self, rel_path: str) -> str:
        """Convert a relative path to a Python module name."""
        parts = Path(rel_path).parts
        if parts and parts[-1].endswith(".py"):
            module_parts = list(parts[:-1]) + [parts[-1][:-3]]
            return ".".join(module_parts)
        return ""

    def get_results(self) -> dict[str, Any]:
        """
        Get the complete inspection results.

        Returns:
            Dictionary with files, components, and statistics
        """
        return {
            "repository": str(self.repo_root),
            "files": {k: asdict(v) for k, v in self.files.items()},
            "components": {k: asdict(v) for k, v in self.components.items()},
            "statistics": self.stats,
            "inspection_metadata": {
                "version": "1.0.0",
                "exclusions": self.exclusions,
            },
        }

    def export_json(self, output_path: str | Path) -> None:
        """Export results to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.get_results(), f, indent=2)

        logger.info("Exported inspection results to %s", output_path)


__all__ = ["RepositoryInspector", "FileInfo", "ComponentInfo", "FileStatus", "FileType"]
