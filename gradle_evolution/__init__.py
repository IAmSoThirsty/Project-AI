"""Compatibility bridge for ``gradle_evolution`` imports.

Project-AI keeps the implementation under ``gradle-evolution/`` (hyphenated),
while tests and integrations import ``gradle_evolution.*`` (underscored). This
module extends package search paths so both naming conventions resolve.
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
