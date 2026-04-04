"""Compatibility package for legacy ``app.*`` imports.

The recovered codebase now lives under ``src.app``. Some modules still use the
older top-level ``app`` package path, so this shim redirects import resolution to
``src/app`` without requiring a broad rewrite.
"""

from __future__ import annotations

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "src" / "app")]
