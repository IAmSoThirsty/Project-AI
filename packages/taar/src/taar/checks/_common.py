"""Shared helpers for TAAR built-in checks."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from pathlib import Path

from taar.models import Finding

IGNORE_DIR_PARTS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ps1",
    ".sh",
    ".txt",
    ".cfg",
    ".ini",
    ".env",
}

MAX_SCAN_BYTES = 1_000_000


def make_finding(
    severity: str, message: str, path: str | None = None, line: int | None = None
) -> Finding:
    return Finding(
        finding_id=uuid.uuid4().hex[:12], severity=severity, path=path, line=line, message=message
    )


def iter_text_files(repo_root: Path, suffixes: set[str] | None = None) -> Iterator[Path]:
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIR_PARTS for part in path.parts):
            continue
        if suffixes is not None and path.suffix.lower() not in suffixes and path.name != ".env":
            continue
        try:
            if path.stat().st_size > MAX_SCAN_BYTES:
                continue
        except OSError:
            continue
        yield path
