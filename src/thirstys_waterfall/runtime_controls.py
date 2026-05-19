"""Runtime activation controls for host-affecting Waterfall operations."""

from __future__ import annotations

import os
from typing import Any

ACTIVE_CONTROLS_ENV = "THIRSTYS_WATERFALL_ENABLE_ACTIVE_CONTROLS"
DESTRUCTIVE_RESPONSES_ENV = "THIRSTYS_WATERFALL_ENABLE_DESTRUCTIVE_RESPONSES"


class WaterfallActivationRequired(RuntimeError):
    """Raised when a host-affecting Waterfall operation lacks explicit consent."""


def _enabled(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on", "allow", "enabled"}


def active_controls_enabled(config: dict[str, Any] | None = None) -> bool:
    """Return whether host/network controls may be activated."""
    if _enabled(os.environ.get(ACTIVE_CONTROLS_ENV)):
        return True
    if not config:
        return False
    project_ai = config.get("project_ai", {})
    return _enabled(project_ai.get("allow_active_controls"))


def destructive_responses_enabled(config: dict[str, Any] | None = None) -> bool:
    """Return whether destructive response actions may run."""
    if _enabled(os.environ.get(DESTRUCTIVE_RESPONSES_ENV)):
        return True
    if not config:
        return False
    project_ai = config.get("project_ai", {})
    return _enabled(project_ai.get("allow_destructive_responses"))


def require_active_controls(config: dict[str, Any] | None = None) -> None:
    """Require explicit activation before touching host network/security controls."""
    if not active_controls_enabled(config):
        raise WaterfallActivationRequired(
            "Thirstys Waterfall host/network controls require explicit activation. "
            f"Set {ACTIVE_CONTROLS_ENV}=1 or project_ai.allow_active_controls=true."
        )


def require_destructive_responses(config: dict[str, Any] | None = None) -> None:
    """Require explicit activation before destructive emergency responses."""
    if not destructive_responses_enabled(config):
        raise WaterfallActivationRequired(
            "Thirstys Waterfall destructive responses require explicit activation. "
            f"Set {DESTRUCTIVE_RESPONSES_ENV}=1 or "
            "project_ai.allow_destructive_responses=true."
        )


__all__ = [
    "ACTIVE_CONTROLS_ENV",
    "DESTRUCTIVE_RESPONSES_ENV",
    "WaterfallActivationRequired",
    "active_controls_enabled",
    "destructive_responses_enabled",
    "require_active_controls",
    "require_destructive_responses",
]
