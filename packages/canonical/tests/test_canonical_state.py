"""Tests for the canonical state composability (Phase B-3 recovery)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from canonical._internal.capability_tokens import CapabilityRegistry, CapabilityToken
from canonical._internal.governance_policy import StaticGovernancePolicy

from canonical import (
    CanonicalState,
    CanonicalStoreError,
    FileCanonicalStore,
)
from identity import IdentityRecord, IdentityRegistry

NOW = datetime(2026, 1, 1, tzinfo=UTC)
ACTOR = "actor-1"
TOKEN = "token-1"
ACTION = "test.echo"
RESOURCE = "resource-1"


def _make_state() -> CanonicalState:
    return CanonicalState(
        identities=IdentityRegistry([IdentityRecord(ACTOR, active=True)]),
        capabilities=CapabilityRegistry(
            [
                CapabilityToken.issue(
                    TOKEN,
                    ACTOR,
                    {ACTION},
                    {RESOURCE},
                    NOW + timedelta(minutes=5),
                ),
            ]
        ),
        policy=StaticGovernancePolicy(
            allow_rules={(ACTION, RESOURCE)},
        ),
    )


def test_empty_factory_creates_blank_state() -> None:
    """CanonicalState.empty() has empty identity/capability/policy."""
    state = CanonicalState.empty()
    assert state.identities.records() == []
    assert state.capabilities.tokens() == []
    assert state.policy.allow_rules() == []
    assert state.policy.deny_rules() == []


def test_canonical_state_to_record_has_three_keys() -> None:
    """to_record() yields identities, capabilities, policy."""
    state = _make_state()
    record = state.to_record()
    assert set(record.keys()) == {"identities", "capabilities", "policy"}
    assert len(record["identities"]) == 1
    assert len(record["capabilities"]) == 1
    assert "allow_rules" in record["policy"]


def test_canonical_state_round_trip_through_record() -> None:
    """from_record(to_record(state)) recreates an equivalent state."""
    state = _make_state()
    rebuilt = CanonicalState.from_record(state.to_record())
    # Compare semantically (the dataclass instances may differ in id)
    assert rebuilt.identities.records() == state.identities.records()
    assert rebuilt.capabilities.tokens() == state.capabilities.tokens()
    assert rebuilt.policy.allow_rules() == state.policy.allow_rules()
    assert rebuilt.policy.deny_rules() == state.policy.deny_rules()


def test_canonical_state_from_record_with_empty_data() -> None:
    """from_record({}) yields an empty canonical state."""
    rebuilt = CanonicalState.from_record({})
    assert rebuilt.identities.records() == []
    assert rebuilt.capabilities.tokens() == []
    assert rebuilt.policy.allow_rules() == []


def test_canonical_state_from_record_rejects_non_dict_policy() -> None:
    """from_record() raises ValueError if policy record isn't a dict."""
    with pytest.raises(ValueError, match="policy record must be an object"):
        CanonicalState.from_record({"policy": "not a dict"})


def test_file_canonical_store_save_creates_file(tmp_path: Path) -> None:
    """save() creates the file and parent directories."""
    path = tmp_path / "subdir" / "state.json"
    store = FileCanonicalStore(path)
    store.save(_make_state())
    assert path.exists()


def test_file_canonical_store_round_trip(tmp_path: Path) -> None:
    """save() then load() returns an equivalent state."""
    path = tmp_path / "state.json"
    source = _make_state()
    FileCanonicalStore(path).save(source)
    loaded = FileCanonicalStore(path).load()
    assert loaded.identities.records() == source.identities.records()
    assert loaded.capabilities.tokens() == source.capabilities.tokens()
    assert loaded.policy.allow_rules() == source.policy.allow_rules()


def test_file_canonical_store_load_missing_file_raises(tmp_path: Path) -> None:
    """load() raises CanonicalStoreError if the file doesn't exist."""
    path = tmp_path / "missing.json"
    with pytest.raises(CanonicalStoreError, match="not found"):
        FileCanonicalStore(path).load()


def test_file_canonical_store_load_corrupt_file_raises(tmp_path: Path) -> None:
    """load() raises CanonicalStoreError on JSON parse failure."""
    path = tmp_path / "corrupt.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(CanonicalStoreError, match="load failed"):
        FileCanonicalStore(path).load()


def test_file_canonical_store_load_non_object_raises(tmp_path: Path) -> None:
    """load() raises CanonicalStoreError on non-object JSON."""
    path = tmp_path / "array.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(CanonicalStoreError, match="must contain a JSON object"):
        FileCanonicalStore(path).load()


def test_file_canonical_store_atomic_write(tmp_path: Path) -> None:
    """save() uses tmp + replace so the final file is always complete."""
    path = tmp_path / "state.json"
    store = FileCanonicalStore(path)
    store.save(_make_state())
    # The temp file should not exist after a successful save
    assert not (path.with_name(f"{path.name}.tmp")).exists()


def test_canonical_state_with_no_identities_can_be_saved(tmp_path: Path) -> None:
    """An empty state can be persisted (edge case)."""
    state = CanonicalState.empty()
    path = tmp_path / "empty.json"
    FileCanonicalStore(path).save(state)
    loaded = FileCanonicalStore(path).load()
    assert loaded.identities.records() == []
    assert loaded.capabilities.tokens() == []
    assert loaded.policy.allow_rules() == []


def test_canonical_state_deny_rules_round_trip(tmp_path: Path) -> None:
    """Deny rules persist through save/load."""
    state = CanonicalState(
        identities=IdentityRegistry(),
        capabilities=CapabilityRegistry(),
        policy=StaticGovernancePolicy(
            allow_rules={("a", "r1")},
            deny_rules={("b", "r2")},
        ),
    )
    path = tmp_path / "state.json"
    FileCanonicalStore(path).save(state)
    loaded = FileCanonicalStore(path).load()
    assert loaded.policy.allow_rules() == [("a", "r1")]
    assert loaded.policy.deny_rules() == [("b", "r2")]
