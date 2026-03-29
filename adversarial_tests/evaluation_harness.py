#!/usr/bin/env python3
"""Compatibility entrypoint for the PA-SHIELD evaluation harness."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
for path in (REPO_ROOT, SRC_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from app.testing.pa_shield.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
