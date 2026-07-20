#!/usr/bin/env python3
"""Run the complete tracked pytest suite in memory-bounded coverage batches."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

COVERAGE_SOURCES = (
    "kernel",
    "security",
    "governance",
    "capability",
    "execution",
    "companion",
    "swr",
    "atlas",
    "arbiter_gov",
    "rlp",
    "project_ai_api",
    "project_ai_cli",
    "project_ai_desktop",
    "project_ai_services",
    "sovereign_vault",
)


def _is_test_file(path: PurePosixPath) -> bool:
    return path.suffix == ".py" and (
        path.name.startswith("test_") or path.name.endswith("_test.py")
    )


def _is_collectable_test_file(
    path: PurePosixPath,
    test_paths: Sequence[PurePosixPath],
    ignored_directories: frozenset[str],
) -> bool:
    return (
        _is_test_file(path)
        and any(path.is_relative_to(test_path) for test_path in test_paths)
        and ignored_directories.isdisjoint(path.parts)
    )


def candidate_test_files(root: Path = ROOT) -> tuple[PurePosixPath, ...]:
    """Return versioned and untracked candidate tests selected by pytest policy.

    CI checkouts contain only versioned files. A release candidate can also
    contain not-yet-committed tests, and local evidence must cover those files
    before they become part of the immutable successor commit.
    """
    configuration = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_options = configuration["tool"]["pytest"]["ini_options"]
    test_paths = tuple(PurePosixPath(path) for path in pytest_options["testpaths"])
    ignored_directories = frozenset(pytest_options.get("norecursedirs", ()))
    result = subprocess.run(
        (
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ),
        check=True,
        capture_output=True,
    )
    paths = (PurePosixPath(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw)
    return tuple(
        sorted(
            path
            for path in paths
            if _is_collectable_test_file(path, test_paths, ignored_directories)
        )
    )


def _group_key(path: PurePosixPath) -> str:
    if len(path.parts) >= 3 and path.parts[0] in {"apps", "packages"}:
        return "/".join(path.parts[:2])
    return path.parts[0]


def balanced_batches(
    paths: Sequence[PurePosixPath],
    batch_count: int,
) -> tuple[tuple[PurePosixPath, ...], ...]:
    """Keep subsystem tests together while greedily balancing batch file counts."""
    if batch_count < 1:
        raise ValueError("batch_count must be at least 1")
    grouped: dict[str, list[PurePosixPath]] = defaultdict(list)
    for path in paths:
        grouped[_group_key(path)].append(path)

    batches: list[list[PurePosixPath]] = [[] for _ in range(batch_count)]
    for _key, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        target = min(range(batch_count), key=lambda index: (len(batches[index]), index))
        batches[target].extend(sorted(group))
    return tuple(tuple(batch) for batch in batches if batch)


def _run(arguments: Sequence[str]) -> None:
    print("+", " ".join(arguments), flush=True)
    subprocess.run(arguments, cwd=ROOT, check=True)


def _pytest_arguments(batch: Sequence[PurePosixPath]) -> tuple[str, ...]:
    source_args = tuple(f"--cov={source}" for source in COVERAGE_SOURCES)
    return (
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--tb=short",
        *source_args,
        "--cov-branch",
        "--cov-append",
        "--cov-report=",
        # pyproject.toml applies an 80% threshold globally. Individual batches
        # are intentionally partial; enforce 80% only on the combined report.
        "--cov-fail-under=0",
        *(path.as_posix() for path in batch),
    )


def run(batch_count: int) -> None:
    tests = candidate_test_files()
    if not tests:
        raise RuntimeError("no candidate pytest files found")

    _run((sys.executable, "-m", "coverage", "erase"))
    batches = balanced_batches(tests, batch_count)
    for index, batch in enumerate(batches, start=1):
        print(
            f"coverage batch {index}/{len(batches)}: {len(batch)} candidate test files", flush=True
        )
        _run(_pytest_arguments(batch))
    _run((sys.executable, "-m", "coverage", "report", "--show-missing", "--fail-under=80"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batches", type=int, default=8)
    arguments = parser.parse_args()
    try:
        run(arguments.batches)
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print(f"CI coverage failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
