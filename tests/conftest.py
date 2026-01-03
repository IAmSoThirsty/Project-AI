"""Pytest configuration: ensure repository root (for non-src packages like `web`) is importable.

This adds the project root to sys.path so tests can import the top-level `web` package.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# Provide fixtures for common test resources
import pytest  # noqa: E402

from app.core.ai_systems import LearningRequestManager  # noqa: E402


@pytest.fixture
def learning_manager(tmp_path: Path):
    mgr = LearningRequestManager(data_dir=str(tmp_path))
    try:
        yield mgr
    finally:
        try:
            mgr.shutdown()
        except Exception:
            pass
