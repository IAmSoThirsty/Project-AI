"""Production deployment configuration for the Thirsty's Standard V3 + Q gate.

Enforcement is **config-driven and fail-safe**:

* A trusted-key registry (public) and an owner private key (secret) must BOTH be
  present for enforcement to activate. If either is missing, ``load_gate_config``
  returns ``None`` and call sites treat that as "V3Q not configured" — the system
  keeps running on its existing Beginnings governance (safe default). This means a
  checkout with no secrets (CI, local dev) stays dormant and all tests stay green;
  a production deployment that provisions the secret turns enforcement on with no
  code change.

* Configuration is read from environment variables (12-factor), with an optional
  JSON override file for the operation-to-action map:

  - ``THIRSTYS_V3Q_OWNER_KEY``  -> path to the owner Ed25519 PRIVATE key JSON
                                  (secret; must never be committed).
  - ``THIRSTYS_V3Q_REGISTRY``   -> path to the trusted-key registry JSON
                                  ``{"keys": [public_doc, ...]}``. If unset, the
                                  packaged ``trusted-keys.json`` is used.
  - ``THIRSTYS_V3Q_OP_MAP``     -> optional path to a JSON ``{op: [class, type]}``
                                  map overriding the built-in per-domain defaults.

This module deliberately performs no network IO and raises nothing: a malformed or
partial config simply yields ``None`` so the caller falls back to dormant.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class V3QGateConfig:
    """Resolved, deployment-ready configuration for ``build_gate``."""

    trusted_keys: dict[str, Any]
    owner_private_key: dict[str, Any]
    operation_to_action: dict[str, tuple[str, str]]


def _load_json(path: str | Path) -> dict[str, Any] | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_gate_config() -> V3QGateConfig | None:
    """Discover the production V3Q configuration from the environment.

    Returns ``None`` (dormant) unless BOTH a trusted-key registry and a readable
    owner private key are present. Never raises.
    """
    owner_path = os.environ.get("THIRSTYS_V3Q_OWNER_KEY")
    if not owner_path:
        return None
    owner_key = _load_json(owner_path)
    if not isinstance(owner_key, dict) or "key_id" not in owner_key:
        return None

    registry_path = os.environ.get("THIRSTYS_V3Q_REGISTRY")
    if registry_path:
        registry = _load_json(registry_path)
    else:
        registry = _load_json(_PACKAGE_ROOT / "trusted-keys.json")
    if not isinstance(registry, dict) or not registry.get("keys"):
        return None

    op_map_path = os.environ.get("THIRSTYS_V3Q_OP_MAP")
    operation_to_action: dict[str, tuple[str, str]] = {}
    if op_map_path:
        raw = _load_json(op_map_path)
        if isinstance(raw, dict):
            for op, pair in raw.items():
                if isinstance(pair, (list, tuple)) and len(pair) == 2:
                    operation_to_action[op] = (str(pair[0]), str(pair[1]))

    return V3QGateConfig(
        trusted_keys=registry,
        owner_private_key=owner_key,
        operation_to_action=operation_to_action,
    )
