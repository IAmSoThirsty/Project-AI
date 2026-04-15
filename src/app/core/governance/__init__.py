"""Governance package exports.

This package hosts the pipeline implementation in ``app.core.governance``
directory while a legacy monolithic governance module still exists at
``src/app/core/governance.py`` and defines symbols like ``Triumvirate`` and
``GovernanceContext``.

Because package imports shadow module imports, code using
``from app.core.governance import Triumvirate`` would fail unless the package
re-exports those legacy symbols. This module provides that compatibility layer.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

from .pipeline import enforce_pipeline

_LEGACY_SYMBOLS = {
    "Triumvirate",
    "GovernanceContext",
    "GovernanceDecision",
    "GovernanceLevel",
    "CouncilMember",
}

_legacy_module: ModuleType | None = None


def _load_legacy_module() -> ModuleType:
    """Load ``src/app/core/governance.py`` lazily for compatibility exports."""
    global _legacy_module

    if _legacy_module is None:
        legacy_path = Path(__file__).resolve().parent.parent / "governance.py"
        spec = spec_from_file_location("app.core._legacy_governance", legacy_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load legacy governance module from {legacy_path}")

        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        _legacy_module = module

    return _legacy_module


def __getattr__(name: str) -> Any:
    """Resolve legacy governance symbols on demand."""
    if name in _LEGACY_SYMBOLS:
        module = _load_legacy_module()
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | _LEGACY_SYMBOLS)


__all__ = ["enforce_pipeline", *_LEGACY_SYMBOLS]
