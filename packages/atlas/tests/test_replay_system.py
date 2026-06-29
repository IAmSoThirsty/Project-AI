"""Tests for canonical Atlas replay system (Phase J2.9)."""

from __future__ import annotations

from pathlib import Path

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    AuditCategory,
    AuditLevel,
    AuditTrail,
    ReplayBundle,
    ReplaySystem,
    ReplaySystemError,
    compute_replay_bundle_hash,
    get_replay_system,
    reset_replay_system,
)


def _bundle() -> ReplayBundle:
    return ReplayBundle(
        bundle_id="bundle-1",
        created_at="2026-06-29T00:00:00+00:00",
        config_hashes={"atlas": "a" * 64},
        data_hashes={"source": "b" * 64},
        seeds={"projection": "seed-1"},
        checkpoints=({"state": "baseline", "revision": 0},),
        graph_snapshots=({"graph_id": "g1", "nodes": 2},),
        audit_events=(
            {
                "sequence": 0,
                "action": "atlas.projection.record",
                "outcome": "ALLOW",
                "record_hash": "c" * 64,
            },
        ),
        projections=({"claim_id": "claim-1", "posterior": 0.42},),
        claims=({"claim_id": "claim-1", "statement": "source-backed"},),
    )


def test_bundle_hash_is_deterministic_and_bound_to_contents() -> None:
    bundle = _bundle()
    same = ReplayBundle.model_validate(bundle.to_canonical_dict())
    changed = ReplayBundle(
        bundle_id="bundle-1",
        created_at="2026-06-29T00:00:00+00:00",
        config_hashes={"atlas": "a" * 64},
        data_hashes={"source": "b" * 64},
        seeds={"projection": "seed-2"},
    )

    assert bundle.bundle_hash == same.bundle_hash
    assert bundle.bundle_hash == compute_replay_bundle_hash(bundle)
    assert changed.bundle_hash != bundle.bundle_hash
    assert bundle.subordination_notice == SUBORDINATION_NOTICE


def test_bundle_rejects_tampered_or_invalid_hash() -> None:
    bundle = _bundle()
    data = bundle.to_canonical_dict()
    data["bundle_hash"] = "f" * 64

    with pytest.raises(ReplaySystemError, match="bundle_hash mismatch"):
        ReplayBundle.model_validate(data)

    with pytest.raises(ReplaySystemError, match="64-char hex"):
        ReplayBundle(
            bundle_id="bad",
            created_at="2026-06-29T00:00:00+00:00",
            config_hashes={"atlas": "not-a-hash"},
        )


def test_replay_system_does_not_create_default_filesystem_path(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundles"

    system = ReplaySystem(bundle_dir=bundle_dir)

    assert system.bundle_dir == bundle_dir
    assert not bundle_dir.exists()


def test_verify_bundle_and_replay_summary_are_reconstructable() -> None:
    system = ReplaySystem()
    bundle = _bundle()

    verification = system.verify_bundle(bundle)
    summary = system.replay_bundle(bundle)

    assert verification.is_valid is True
    assert verification.bundle_hash == bundle.bundle_hash
    assert verification.item_counts == {
        "audit_events": 1,
        "checkpoints": 1,
        "claims": 1,
        "graph_snapshots": 1,
        "projections": 1,
    }
    assert summary.bundle_id == bundle.bundle_id
    assert summary.events_replayed == 1
    assert summary.projections_replayed == 1
    assert summary.claims_replayed == 1
    assert summary.reconstructed_state_hash
    assert summary.subordination_notice == SUBORDINATION_NOTICE


def test_replay_fails_closed_on_invalid_bundle() -> None:
    system = ReplaySystem()
    with pytest.raises(ReplaySystemError, match="bundle must be ReplayBundle"):
        system.replay_bundle("not-a-bundle")  # type: ignore[arg-type]


def test_save_and_load_bundle_are_explicit_filesystem_operations(tmp_path: Path) -> None:
    system = ReplaySystem(bundle_dir=tmp_path / "bundles")
    bundle = _bundle()

    path = system.save_bundle(bundle)
    loaded = system.load_bundle(path)

    assert path.is_file()
    assert path.name == "bundle_bundle-1.json"
    assert loaded == bundle


def test_replay_system_can_emit_audit_events() -> None:
    trail = AuditTrail()
    system = ReplaySystem(audit_trail=trail)
    bundle = _bundle()

    system.replay_bundle(bundle)

    events = trail.events
    assert len(events) == 1
    assert events[0].level is AuditLevel.HIGH_PRIORITY
    assert events[0].category is AuditCategory.VALIDATION
    assert events[0].action == "atlas.replay_bundle"
    assert dict(events[0].evidence)["bundle_hash"] == bundle.bundle_hash


def test_singleton_helpers_reset_replay_system() -> None:
    reset_replay_system()
    first = get_replay_system()
    second = get_replay_system()

    assert first is second

    reset_replay_system()
    assert get_replay_system() is not first
