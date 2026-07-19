"""Desktop client version, derived from installed distribution metadata."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    DESKTOP_VERSION = _pkg_version("project-ai-desktop")
except PackageNotFoundError:  # pragma: no cover
    DESKTOP_VERSION = "0.0.0.dev0"
