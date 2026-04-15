"""Project-AI integrations namespace.

This package includes compatibility wiring so imports using
``integrations.<module>`` can resolve modules that currently live under
``src/integrations``.
"""

from __future__ import annotations

import pkgutil
from pathlib import Path

__version__ = "1.0.0"

# Make this package a namespace-compatible package and include src/integrations
# so imports such as ``integrations.temporal`` resolve correctly.
__path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore[name-defined]

_src_integrations = Path(__file__).resolve().parent.parent / "src" / "integrations"
if _src_integrations.exists():
	_src_integrations_str = str(_src_integrations)
	if _src_integrations_str not in __path__:
		__path__.append(_src_integrations_str)
