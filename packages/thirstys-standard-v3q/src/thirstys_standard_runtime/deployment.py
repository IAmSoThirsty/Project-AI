"""Production deployment configuration for the Thirsty's Standard V3 + Q gate.

Enforcement is **config-driven and fail-safe**:

* A trusted-key registry contains public verification keys only. The online runtime
  never loads an owner private key and cannot mint its own authority or approval.
  Development stays dormant unless a registry is explicitly configured. Production
  sets ``THIRSTYS_V3Q_REQUIRED=true`` so the packaged or configured public registry
  is mandatory and missing external proofs deny at the execution gate.

* Configuration is read from environment variables (12-factor), with an optional
  JSON override file for the operation-to-action map:

  - ``THIRSTYS_V3Q_REGISTRY``   -> path to the trusted-key registry JSON
                                  ``{"keys": [public_doc, ...]}``. If unset, the
                                  packaged ``trusted-keys.json`` is used.
  - ``THIRSTYS_V3Q_OP_MAP``     -> optional path to a JSON ``{op: [class, type]}``
                                  map overriding the built-in per-domain defaults.

This module deliberately performs no network IO. Development remains dormant when
configuration is absent. Production sets ``THIRSTYS_V3Q_REQUIRED=true`` so missing,
malformed, or mismatched signing configuration raises before the application starts.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class V3QGateConfig:
    """Resolved, deployment-ready configuration for ``build_gate``."""

    trusted_keys: dict[str, Any]
    operation_to_action: dict[str, tuple[str, str]]


class V3QConfigurationError(RuntimeError):
    """Raised when explicitly required V3Q enforcement cannot be configured."""


def _required() -> bool:
    raw = os.environ.get("THIRSTYS_V3Q_REQUIRED", "false").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"", "0", "false", "no", "off"}:
        return False
    raise V3QConfigurationError(
        "THIRSTYS_V3Q_REQUIRED must be one of true/false, 1/0, yes/no, or on/off"
    )


def _unavailable(message: str, *, required: bool) -> None:
    if required:
        raise V3QConfigurationError(message)


def _load_json(path: str | Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return cast(dict[str, Any], loaded) if isinstance(loaded, dict) else None


def load_gate_config() -> V3QGateConfig | None:
    """Discover the production V3Q configuration from the environment.

    Returns ``None`` in development unless a registry path is explicitly configured.
    When ``THIRSTYS_V3Q_REQUIRED=true``, the packaged registry is accepted as the
    default and invalid or missing public verification configuration raises
    :class:`V3QConfigurationError` so startup fails closed.
    """
    required = _required()
    registry_path = os.environ.get("THIRSTYS_V3Q_REGISTRY")
    if registry_path:
        registry = _load_json(registry_path)
    elif required:
        registry = _load_json(_PACKAGE_ROOT / "trusted-keys.json")
    else:
        return None
    if not isinstance(registry, dict) or not registry.get("keys"):
        _unavailable("V3Q trusted-key registry is unreadable or empty", required=required)
        return None

    op_map_path = os.environ.get("THIRSTYS_V3Q_OP_MAP")
    operation_to_action: dict[str, tuple[str, str]] = {}
    if op_map_path:
        raw = _load_json(op_map_path)
        if not isinstance(raw, dict):
            _unavailable("THIRSTYS_V3Q_OP_MAP is unreadable or invalid", required=required)
            return None
        for op, pair in raw.items():
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                _unavailable(
                    f"THIRSTYS_V3Q_OP_MAP entry {op!r} must contain exactly two values",
                    required=required,
                )
                return None
            operation_to_action[op] = (str(pair[0]), str(pair[1]))

    return V3QGateConfig(
        trusted_keys=registry,
        operation_to_action=operation_to_action,
    )
