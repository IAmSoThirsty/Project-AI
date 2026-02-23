"""
TAAR Dependency Graph — Cross-language impact analysis.

Maps changed files to the set of runners and test files that need
to execute. Uses glob pattern matching against the impact map defined
in taar.toml, plus heuristic same-name matching (e.g., src/core/audit.py
→ tests/test_audit.py).
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

from taar.config import TaarConfig


@dataclass
class ImpactResult:
    """The result of impact analysis for a set of changed files."""

    # Which runners are affected, mapped to the files that triggered them
    affected_runners: dict[str, list[Path]] = field(default_factory=dict)

    # Additional test files to run based on impact map
    extra_test_files: list[Path] = field(default_factory=list)

    @property
    def runner_names(self) -> list[str]:
        """Names of all affected runners."""
        return list(self.affected_runners.keys())

    @property
    def is_empty(self) -> bool:
        return not self.affected_runners


def analyze_impact(
    changed_files: list[Path],
    config: TaarConfig,
) -> ImpactResult:
    """
    Determine which runners and test files are impacted by a set of
    changed files.

    The algorithm:
    1. For each changed file, check which runner path globs match it.
    2. For each changed file, check the impact map for extra test files.
    3. Auto-discover test files by name heuristic (foo.py → test_foo.py).

    Args:
        changed_files: Absolute paths of files that changed.
        config: Loaded TAAR configuration.

    Returns:
        ImpactResult with affected runners and extra test files.
    """
    result = ImpactResult()

    for changed in changed_files:
        # Get relative path for glob matching
        try:
            rel = changed.relative_to(config.project_root)
        except ValueError:
            continue
        rel_str = rel.as_posix()

        # 1. Match against runner path globs
        for runner_name, runner in config.enabled_runners.items():
            if _matches_any_glob(rel_str, runner.paths):
                if runner_name not in result.affected_runners:
                    result.affected_runners[runner_name] = []
                result.affected_runners[runner_name].append(changed)

        # 2. Check impact map for extra test files
        for source_pattern, test_patterns in config.impact_map.items():
            if _matches_glob(rel_str, source_pattern):
                for test_pattern in test_patterns:
                    # Resolve glob pattern to actual files
                    matched_tests = list(config.project_root.glob(test_pattern))
                    for test_file in matched_tests:
                        if test_file not in result.extra_test_files:
                            result.extra_test_files.append(test_file)

        # 3. Heuristic: source file → test file name matching
        heuristic_tests = _heuristic_test_discovery(changed, config.project_root)
        for test_file in heuristic_tests:
            if test_file not in result.extra_test_files:
                result.extra_test_files.append(test_file)

    return result


def _matches_any_glob(path: str, patterns: tuple[str, ...]) -> bool:
    """Check if a path matches any of the given glob patterns."""
    return any(_matches_glob(path, pattern) for pattern in patterns)


def _matches_glob(path: str, pattern: str) -> bool:
    """
    Check if a path matches a glob pattern.

    Supports ** for recursive matching via fnmatch-style patterns.
    Converts ** patterns into a form fnmatch can handle.
    """
    # Normalize separators
    path = path.replace("\\", "/")
    pattern = pattern.replace("\\", "/")

    # fnmatch doesn't natively support **
    # Split pattern by ** and check each segment
    if "**" in pattern:
        # Convert "src/**/*.py" to match any depth
        parts = pattern.split("**/")
        if len(parts) == 2:
            prefix, suffix = parts
            # Check if path starts with prefix (or prefix is empty)
            if prefix and not path.startswith(prefix):
                return False
            # Check if the remaining path matches the suffix
            remaining = path[len(prefix):] if prefix else path
            return fnmatch.fnmatch(remaining, suffix) or fnmatch.fnmatch(
                path, pattern.replace("**/", "*/")
            )
    return fnmatch.fnmatch(path, pattern)


def _heuristic_test_discovery(changed_file: Path, project_root: Path) -> list[Path]:
    """
    Auto-discover test files by name convention.

    For a file like `src/core/audit.py`, looks for:
    - tests/test_audit.py
    - tests/test_audit_*.py

    Only returns files that actually exist.
    """
    if not changed_file.suffix == ".py":
        return []

    stem = changed_file.stem
    if stem.startswith("test_") or stem.startswith("__"):
        return []  # Don't recurse on test files or dunder files

    tests_dir = project_root / "tests"
    if not tests_dir.is_dir():
        return []

    discovered = []

    # Direct match: test_{name}.py
    direct = tests_dir / f"test_{stem}.py"
    if direct.is_file():
        discovered.append(direct)

    # Wildcard match: test_{name}_*.py
    for match in tests_dir.glob(f"test_{stem}_*.py"):
        if match not in discovered:
            discovered.append(match)

    return discovered
