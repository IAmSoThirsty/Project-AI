"""Canonical Atlas replay bundle verification.

Replay bundles are portable evidence packages for reconstructing Atlas analysis
surfaces from immutable JSON-compatible records. This module verifies and
summarizes bundles; it does not grant authority or execute actions.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from atlas.analysis import SUBORDINATION_NOTICE
from atlas.audit import AuditCategory, AuditLevel, AuditTrail
from kernel import JsonValue


class ReplaySystemError(Exception):
    """Raised when replay bundle validation or replay fails."""


JsonObject = dict[str, JsonValue]

_BUNDLE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_COUNT_KEYS = ("audit_events", "checkpoints", "claims", "graph_snapshots", "projections")


@dataclass(frozen=True, init=False)
class ReplayBundle:
    """Immutable, hash-bound Atlas replay bundle."""

    bundle_id: str
    created_at: str
    atlas_version: str
    config_hashes: tuple[tuple[str, str], ...]
    baseline_hashes: tuple[tuple[str, str], ...]
    data_hashes: tuple[tuple[str, str], ...]
    seeds: tuple[tuple[str, str], ...]
    checkpoints: tuple[JsonObject, ...]
    graph_snapshots: tuple[JsonObject, ...]
    audit_events: tuple[JsonObject, ...]
    projections: tuple[JsonObject, ...]
    claims: tuple[JsonObject, ...]
    bundle_hash: str
    subordination_notice: str

    def __init__(
        self,
        *,
        bundle_id: str,
        created_at: str,
        atlas_version: str = "0.0.0.dev0",
        config_hashes: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        baseline_hashes: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        data_hashes: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        seeds: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        checkpoints: Sequence[Mapping[str, JsonValue]] = (),
        graph_snapshots: Sequence[Mapping[str, JsonValue]] = (),
        audit_events: Sequence[Mapping[str, JsonValue]] = (),
        projections: Sequence[Mapping[str, JsonValue]] = (),
        claims: Sequence[Mapping[str, JsonValue]] = (),
        bundle_hash: str | None = None,
        subordination_notice: str = SUBORDINATION_NOTICE,
    ) -> None:
        _validate_bundle_id(bundle_id)
        _validate_non_empty_string("created_at", created_at)
        try:
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError as error:
            raise ReplaySystemError(f"created_at must be ISO 8601, got {created_at!r}") from error
        _validate_non_empty_string("atlas_version", atlas_version)
        if subordination_notice != SUBORDINATION_NOTICE:
            raise ReplaySystemError("subordination_notice mismatch")

        object.__setattr__(self, "bundle_id", bundle_id)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "atlas_version", atlas_version)
        object.__setattr__(
            self, "config_hashes", _normalize_hash_pairs("config_hashes", config_hashes)
        )
        object.__setattr__(
            self, "baseline_hashes", _normalize_hash_pairs("baseline_hashes", baseline_hashes)
        )
        object.__setattr__(self, "data_hashes", _normalize_hash_pairs("data_hashes", data_hashes))
        object.__setattr__(self, "seeds", _normalize_string_pairs("seeds", seeds))
        object.__setattr__(self, "checkpoints", _normalize_objects("checkpoints", checkpoints))
        object.__setattr__(
            self, "graph_snapshots", _normalize_objects("graph_snapshots", graph_snapshots)
        )
        object.__setattr__(self, "audit_events", _normalize_objects("audit_events", audit_events))
        object.__setattr__(self, "projections", _normalize_objects("projections", projections))
        object.__setattr__(self, "claims", _normalize_objects("claims", claims))
        object.__setattr__(self, "subordination_notice", subordination_notice)

        expected = compute_replay_bundle_hash(self)
        if bundle_hash is not None and bundle_hash != expected:
            raise ReplaySystemError("bundle_hash mismatch")
        object.__setattr__(self, "bundle_hash", expected)

    @classmethod
    def model_validate(cls, data: Mapping[str, object]) -> ReplayBundle:
        """Construct a bundle from a JSON-like mapping."""
        if not isinstance(data, Mapping):
            raise ReplaySystemError("bundle data must be a mapping")
        return cls(
            bundle_id=_require_string(data, "bundle_id"),
            created_at=_require_string(data, "created_at"),
            atlas_version=_optional_string(data, "atlas_version", "0.0.0.dev0"),
            config_hashes=_mapping_or_pairs(data.get("config_hashes", ()), "config_hashes"),
            baseline_hashes=_mapping_or_pairs(data.get("baseline_hashes", ()), "baseline_hashes"),
            data_hashes=_mapping_or_pairs(data.get("data_hashes", ()), "data_hashes"),
            seeds=_mapping_or_pairs(data.get("seeds", ()), "seeds"),
            checkpoints=_object_sequence(data.get("checkpoints", ()), "checkpoints"),
            graph_snapshots=_object_sequence(data.get("graph_snapshots", ()), "graph_snapshots"),
            audit_events=_object_sequence(data.get("audit_events", ()), "audit_events"),
            projections=_object_sequence(data.get("projections", ()), "projections"),
            claims=_object_sequence(data.get("claims", ()), "claims"),
            bundle_hash=_optional_nullable_string(data, "bundle_hash"),
            subordination_notice=_optional_string(
                data, "subordination_notice", SUBORDINATION_NOTICE
            ),
        )

    def to_canonical_dict(self, *, include_hash: bool = True) -> dict[str, JsonValue]:
        """Return a JSON-serializable canonical bundle dictionary."""
        body: dict[str, JsonValue] = {
            "atlas_version": self.atlas_version,
            "audit_events": list(self.audit_events),
            "baseline_hashes": dict(self.baseline_hashes),
            "bundle_id": self.bundle_id,
            "checkpoints": list(self.checkpoints),
            "claims": list(self.claims),
            "config_hashes": dict(self.config_hashes),
            "created_at": self.created_at,
            "data_hashes": dict(self.data_hashes),
            "graph_snapshots": list(self.graph_snapshots),
            "projections": list(self.projections),
            "seeds": dict(self.seeds),
            "subordination_notice": self.subordination_notice,
        }
        if include_hash:
            body["bundle_hash"] = self.bundle_hash
        return body


@dataclass(frozen=True)
class ReplayVerification:
    """Verification result for an Atlas replay bundle."""

    bundle_id: str
    is_valid: bool
    bundle_hash: str
    item_counts: dict[str, int]
    issues: tuple[str, ...] = ()
    subordination_notice: str = SUBORDINATION_NOTICE


@dataclass(frozen=True)
class ReplaySummary:
    """Deterministic reconstruction summary for a replay bundle."""

    bundle_id: str
    bundle_hash: str
    events_replayed: int
    checkpoints_replayed: int
    graph_snapshots_replayed: int
    projections_replayed: int
    claims_replayed: int
    reconstructed_state_hash: str
    subordination_notice: str = SUBORDINATION_NOTICE


class ReplaySystem:
    """Verify and replay Atlas verification bundles."""

    def __init__(
        self,
        bundle_dir: Path | None = None,
        *,
        audit_trail: AuditTrail | None = None,
    ) -> None:
        if bundle_dir is not None and not isinstance(bundle_dir, Path):
            raise ReplaySystemError(
                f"bundle_dir must be Path or None, got {type(bundle_dir).__name__}"
            )
        if audit_trail is not None and not isinstance(audit_trail, AuditTrail):
            raise ReplaySystemError(
                f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}"
            )
        self.bundle_dir = bundle_dir
        self._audit_trail = audit_trail
        self._lock = threading.Lock()

    def create_bundle(
        self,
        *,
        bundle_id: str,
        created_at: str,
        config_hashes: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        baseline_hashes: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        data_hashes: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        seeds: Mapping[str, str] | Sequence[tuple[str, str]] = (),
        checkpoints: Sequence[Mapping[str, JsonValue]] = (),
        graph_snapshots: Sequence[Mapping[str, JsonValue]] = (),
        audit_events: Sequence[Mapping[str, JsonValue]] = (),
        projections: Sequence[Mapping[str, JsonValue]] = (),
        claims: Sequence[Mapping[str, JsonValue]] = (),
    ) -> ReplayBundle:
        """Create a canonical replay bundle."""
        return ReplayBundle(
            bundle_id=bundle_id,
            created_at=created_at,
            config_hashes=config_hashes,
            baseline_hashes=baseline_hashes,
            data_hashes=data_hashes,
            seeds=seeds,
            checkpoints=checkpoints,
            graph_snapshots=graph_snapshots,
            audit_events=audit_events,
            projections=projections,
            claims=claims,
        )

    def verify_bundle(self, bundle: ReplayBundle) -> ReplayVerification:
        """Verify hash binding and reconstructable item counts."""
        if not isinstance(bundle, ReplayBundle):
            raise ReplaySystemError(f"bundle must be ReplayBundle, got {type(bundle).__name__}")
        issues: list[str] = []
        computed = compute_replay_bundle_hash(bundle)
        if computed != bundle.bundle_hash:
            issues.append("bundle_hash mismatch")
        if bundle.subordination_notice != SUBORDINATION_NOTICE:
            issues.append("subordination_notice mismatch")
        return ReplayVerification(
            bundle_id=bundle.bundle_id,
            is_valid=not issues,
            bundle_hash=bundle.bundle_hash,
            item_counts=_item_counts(bundle),
            issues=tuple(issues),
        )

    def replay_bundle(self, bundle: ReplayBundle) -> ReplaySummary:
        """Replay a bundle into a deterministic reconstruction summary."""
        verification = self.verify_bundle(bundle)
        if not verification.is_valid:
            raise ReplaySystemError("; ".join(verification.issues))
        body = {
            "audit_events": bundle.audit_events,
            "bundle_hash": bundle.bundle_hash,
            "checkpoints": bundle.checkpoints,
            "claims": bundle.claims,
            "graph_snapshots": bundle.graph_snapshots,
            "projections": bundle.projections,
            "subordination_notice": SUBORDINATION_NOTICE,
        }
        reconstructed_hash = _sha256(body)
        summary = ReplaySummary(
            bundle_id=bundle.bundle_id,
            bundle_hash=bundle.bundle_hash,
            events_replayed=len(bundle.audit_events),
            checkpoints_replayed=len(bundle.checkpoints),
            graph_snapshots_replayed=len(bundle.graph_snapshots),
            projections_replayed=len(bundle.projections),
            claims_replayed=len(bundle.claims),
            reconstructed_state_hash=reconstructed_hash,
        )
        self._audit_replay(summary)
        return summary

    def save_bundle(self, bundle: ReplayBundle, path: Path | None = None) -> Path:
        """Save a bundle to an explicit file or configured bundle directory."""
        if not isinstance(bundle, ReplayBundle):
            raise ReplaySystemError(f"bundle must be ReplayBundle, got {type(bundle).__name__}")
        target = path or self._default_bundle_path(bundle)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = bundle.to_canonical_dict()
        if target.suffix == ".gz":
            with gzip.open(target, "wt", encoding="utf-8") as stream:
                json.dump(data, stream, sort_keys=True, separators=(",", ":"))
        else:
            target.write_text(
                json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
        return target

    def load_bundle(self, path: Path) -> ReplayBundle:
        """Load and verify a replay bundle from JSON or gzipped JSON."""
        if not isinstance(path, Path):
            raise ReplaySystemError(f"path must be Path, got {type(path).__name__}")
        if not path.is_file():
            raise ReplaySystemError(f"bundle file not found: {path}")
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                data = json.load(stream)
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, Mapping):
            raise ReplaySystemError("bundle file must contain a JSON object")
        return ReplayBundle.model_validate(data)

    def _default_bundle_path(self, bundle: ReplayBundle) -> Path:
        if self.bundle_dir is None:
            raise ReplaySystemError("bundle_dir is required when path is not provided")
        return self.bundle_dir / f"bundle_{bundle.bundle_id}.json"

    def _audit_replay(self, summary: ReplaySummary) -> None:
        if self._audit_trail is None:
            return
        self._audit_trail.append(
            level=AuditLevel.HIGH_PRIORITY,
            category=AuditCategory.VALIDATION,
            actor="REPLAY_SYSTEM",
            action="atlas.replay_bundle",
            resource=f"atlas:replay:{summary.bundle_id}",
            outcome="ALLOW",
            rationale="Atlas replay bundle verified and replayed deterministically",
            evidence={
                "bundle_hash": summary.bundle_hash,
                "events_replayed": str(summary.events_replayed),
                "reconstructed_state_hash": summary.reconstructed_state_hash,
            },
        )


_replay_system: ReplaySystem | None = None
_replay_system_lock = threading.Lock()


def compute_replay_bundle_hash(bundle: ReplayBundle) -> str:
    """Compute the canonical SHA-256 hash for a replay bundle."""
    return _sha256(bundle.to_canonical_dict(include_hash=False))


def get_replay_system(
    bundle_dir: Path | None = None,
    *,
    audit_trail: AuditTrail | None = None,
) -> ReplaySystem:
    """Return the process-local replay system singleton."""
    global _replay_system
    with _replay_system_lock:
        if _replay_system is None:
            _replay_system = ReplaySystem(bundle_dir=bundle_dir, audit_trail=audit_trail)
        return _replay_system


def reset_replay_system() -> None:
    """Clear the process-local replay system singleton."""
    global _replay_system
    with _replay_system_lock:
        _replay_system = None


def _validate_bundle_id(value: str) -> None:
    _validate_non_empty_string("bundle_id", value)
    if not _BUNDLE_ID_RE.fullmatch(value):
        raise ReplaySystemError(
            "bundle_id may contain only letters, numbers, dots, dashes, and underscores"
        )


def _validate_non_empty_string(field_name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReplaySystemError(f"{field_name} must be non-empty string")


def _validate_hash(field_name: str, value: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ReplaySystemError(f"{field_name} must be 64-char hex string")
    for char in value:
        if char not in "0123456789abcdef":
            raise ReplaySystemError(f"{field_name} must be 64-char hex string")


def _normalize_hash_pairs(
    field_name: str,
    values: Mapping[str, str] | Sequence[tuple[str, str]],
) -> tuple[tuple[str, str], ...]:
    pairs = _normalize_string_pairs(field_name, values)
    for key, value in pairs:
        _validate_hash(f"{field_name}.{key}", value)
    return pairs


def _normalize_string_pairs(
    field_name: str,
    values: Mapping[str, str] | Sequence[tuple[str, str]],
) -> tuple[tuple[str, str], ...]:
    items = values.items() if isinstance(values, Mapping) else values
    pairs: list[tuple[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, tuple) or len(item) != 2:
            raise ReplaySystemError(f"{field_name}[{index}] must be a string pair")
        key, value = item
        if not isinstance(key, str) or not key.strip():
            raise ReplaySystemError(f"{field_name}[{index}] key must be non-empty string")
        if not isinstance(value, str) or not value.strip():
            raise ReplaySystemError(f"{field_name}[{index}] value must be non-empty string")
        pairs.append((key, value))
    return tuple(sorted(pairs))


def _normalize_objects(
    field_name: str,
    values: Sequence[Mapping[str, JsonValue]],
) -> tuple[JsonObject, ...]:
    objects: list[JsonObject] = []
    for index, value in enumerate(values):
        if not isinstance(value, Mapping) or not value:
            raise ReplaySystemError(f"{field_name}[{index}] must be a non-empty mapping")
        normalized = dict(value)
        for key, item in normalized.items():
            if not isinstance(key, str) or not key.strip():
                raise ReplaySystemError(f"{field_name}[{index}] keys must be non-empty strings")
            _validate_json_value(f"{field_name}[{index}].{key}", item)
        objects.append(normalized)
    return tuple(objects)


def _validate_json_value(field_name: str, value: JsonValue) -> None:
    if value is None or isinstance(value, str | int | float | bool):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(f"{field_name}[{index}]", item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ReplaySystemError(f"{field_name} object keys must be strings")
            _validate_json_value(f"{field_name}.{key}", item)
        return
    raise ReplaySystemError(f"{field_name} must be JSON-compatible")


def _mapping_or_pairs(
    value: object, field_name: str
) -> Mapping[str, str] | Sequence[tuple[str, str]]:
    if isinstance(value, Mapping):
        return {str(key): _string_value(field_name, item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        pairs: list[tuple[str, str]] = []
        for index, item in enumerate(value):
            if not isinstance(item, Sequence) or isinstance(item, str | bytes) or len(item) != 2:
                raise ReplaySystemError(f"{field_name}[{index}] must be a two-item sequence")
            key = item[0]
            raw_value = item[1]
            if not isinstance(key, str):
                raise ReplaySystemError(f"{field_name}[{index}] key must be string")
            pairs.append((key, _string_value(field_name, raw_value)))
        return tuple(pairs)
    raise ReplaySystemError(f"{field_name} must be a mapping or string-pair sequence")


def _object_sequence(value: object, field_name: str) -> tuple[Mapping[str, JsonValue], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ReplaySystemError(f"{field_name} must be a sequence")
    objects: list[Mapping[str, JsonValue]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ReplaySystemError(f"{field_name}[{index}] must be a mapping")
        objects.append(_json_mapping(item, f"{field_name}[{index}]"))
    return tuple(objects)


def _json_mapping(value: Mapping[object, object], field_name: str) -> JsonObject:
    normalized: JsonObject = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ReplaySystemError(f"{field_name} keys must be strings")
        normalized[key] = _json_value(item, f"{field_name}.{key}")
    return normalized


def _json_value(value: object, field_name: str) -> JsonValue:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, list):
        return [_json_value(item, f"{field_name}[]") for item in value]
    if isinstance(value, Mapping):
        return _json_mapping(value, field_name)
    raise ReplaySystemError(f"{field_name} must be JSON-compatible")


def _require_string(data: Mapping[str, object], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ReplaySystemError(f"{field_name} must be non-empty string")
    return value


def _optional_string(data: Mapping[str, object], field_name: str, default: str) -> str:
    value = data.get(field_name, default)
    if not isinstance(value, str) or not value.strip():
        raise ReplaySystemError(f"{field_name} must be non-empty string")
    return value


def _optional_nullable_string(data: Mapping[str, object], field_name: str) -> str | None:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ReplaySystemError(f"{field_name} must be non-empty string or null")
    return value


def _string_value(field_name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReplaySystemError(f"{field_name} values must be non-empty strings")
    return value


def _item_counts(bundle: ReplayBundle) -> dict[str, int]:
    return {
        "audit_events": len(bundle.audit_events),
        "checkpoints": len(bundle.checkpoints),
        "claims": len(bundle.claims),
        "graph_snapshots": len(bundle.graph_snapshots),
        "projections": len(bundle.projections),
    }


def _sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


__all__ = [
    "ReplayBundle",
    "ReplaySummary",
    "ReplaySystem",
    "ReplaySystemError",
    "ReplayVerification",
    "compute_replay_bundle_hash",
    "get_replay_system",
    "reset_replay_system",
]
