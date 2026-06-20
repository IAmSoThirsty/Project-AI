from __future__ import annotations

from pathlib import Path

import pytest
from tools.legacy_source_guard import LegacySourceGuard


def test_source_rejects_escape(tmp_path: Path) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    guard = LegacySourceGuard(root)
    with pytest.raises(ValueError, match="escapes root"):
        guard.source("../outside.txt")


def test_source_requires_existing_path(tmp_path: Path) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    guard = LegacySourceGuard(root)
    with pytest.raises(FileNotFoundError):
        guard.source("missing.txt")


def test_destination_rejects_legacy_path(tmp_path: Path) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    guard = LegacySourceGuard(root)
    with pytest.raises(PermissionError, match="forbidden"):
        guard.destination(root / "output.txt")


def test_git_rejects_mutating_commands(tmp_path: Path) -> None:
    guard = LegacySourceGuard(tmp_path)
    with pytest.raises(PermissionError, match="not read-only"):
        guard.git("commit", "-m", "forbidden")
