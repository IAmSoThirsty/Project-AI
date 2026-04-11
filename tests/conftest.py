#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""Pytest configuration: ensure repository root (for non-src packages like `web`) is importable.

This adds the project root to sys.path so tests can import the top-level `web` package.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
GOVERNANCE = ROOT / "governance"

for path in (ROOT, SRC, GOVERNANCE):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
