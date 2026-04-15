"""Compatibility package for the Gradle Evolution substrate.

The implementation currently lives under ``gradle-evolution/`` (hyphenated
folder name), while Python imports across the codebase use
``gradle_evolution.*``. This package bridges that naming mismatch by extending
its package search path to the legacy directory.
"""

from __future__ import annotations

import pkgutil
from pathlib import Path

__path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore[name-defined]

_legacy_root = Path(__file__).resolve().parent.parent / "gradle-evolution"
if _legacy_root.exists():
    _legacy_root_str = str(_legacy_root)
    if _legacy_root_str not in __path__:
        __path__.append(_legacy_root_str)
