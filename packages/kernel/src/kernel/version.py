"""Single authoritative Project-AI version.

The released version is declared once per distribution in its ``pyproject.toml``
and is never duplicated in code. :data:`PROJECT_AI_VERSION` is the canonical
system version that health responses, OpenAPI declarations, and the
cross-service runtime guard report; :func:`distribution_version` lets an
individual package resolve its own installed metadata version through the same
code path so every package derives from one mechanism.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version
from typing import Final

# Last-resort value for an uninstalled source checkout, where no distribution
# metadata exists on disk. Installed wheels and editable installs always carry
# metadata, so CI and every container resolve the real released version and
# never reach this fallback.
_SOURCE_FALLBACK: Final[str] = "0.0.0.dev0"
_CANONICAL_DISTRIBUTION: Final[str] = "project-ai-kernel"


def distribution_version(distribution: str) -> str:
    """Return an installed distribution's version, or the source fallback."""
    try:
        return _distribution_version(distribution)
    except PackageNotFoundError:  # pragma: no cover - installed dists carry metadata
        return _SOURCE_FALLBACK


PROJECT_AI_VERSION: Final[str] = distribution_version(_CANONICAL_DISTRIBUTION)
"""Canonical Project-AI release version, derived from ``project-ai-kernel``."""
