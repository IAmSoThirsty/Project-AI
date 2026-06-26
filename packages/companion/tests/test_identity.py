"""Unit tests for companion.identity.IdentityManager.

Covers: bootstrap state, phase transitions, bonding profile validation,
pluggable derivation, fail-closed behavior on invalid input.
"""

from __future__ import annotations

import pytest
from companion.identity import (
    ALLOWED_PHASES,
    PHASE_BONDED,
    PHASE_UNBONDED,
    IdentityError,
    IdentityManager,
)


class _CountingDerivation:
    """Test double for the IdentityDerivation Protocol."""

    def __init__(self) -> None:
        self.call_count = 0
        self.return_value = "derived-id-42"

    def __call__(self, fields):  # type: ignore[no-untyped-def]
        self.call_count += 1
        return self.return_value


def test_initial_state_is_unbonded_with_canonical_bootstrap_identity() -> None:
    manager = IdentityManager()
    assert manager.get_phase() == PHASE_UNBONDED
    identity = manager.get_identity()
    assert identity["phase"] == PHASE_UNBONDED
    assert identity["name"] == "Project-AI (Unbonded)"
    assert identity["constraints"] == {"conservative": True}


def test_allowed_phases_constant_is_frozen() -> None:
    assert PHASE_UNBONDED in ALLOWED_PHASES
    assert PHASE_BONDED in ALLOWED_PHASES
    assert isinstance(ALLOWED_PHASES, frozenset)


def test_apply_bonding_profile_transitions_to_bonded_phase() -> None:
    manager = IdentityManager()
    profile = {
        "name": "Thirsty",
        "values": {"honesty": 1.0},
        "temperament": {"curious": True},
        "relationship": {"quench": "primary"},
        "constraints": {"asymmetric_security": True},
    }
    snapshot = manager.apply_bonding_profile(profile, expected_revision=0)
    assert manager.get_phase() == PHASE_BONDED
    identity = manager.get_identity()
    assert identity["name"] == "Thirsty"
    assert identity["phase"] == PHASE_BONDED
    assert identity["values"] == {"honesty": 1.0}
    assert snapshot.revision == 1


def test_apply_bonding_profile_rejects_missing_name() -> None:
    manager = IdentityManager()
    with pytest.raises(IdentityError, match="missing non-empty 'name'"):
        manager.apply_bonding_profile({}, expected_revision=0)


def test_apply_bonding_profile_rejects_empty_name() -> None:
    manager = IdentityManager()
    with pytest.raises(IdentityError, match="missing non-empty 'name'"):
        manager.apply_bonding_profile({"name": "   "}, expected_revision=0)


def test_run_bonding_protocol_is_noop_when_already_bonded() -> None:
    manager = IdentityManager()
    manager.apply_bonding_profile({"name": "A"}, expected_revision=0)
    snapshot_before = manager.snapshot()
    snapshot_after = manager.run_bonding_protocol({"name": "B"}, expected_revision=1)
    # No state change when already bonded
    assert snapshot_after.revision == snapshot_before.revision
    assert manager.get_identity()["name"] == "A"


def test_run_bonding_protocol_bonds_when_unbonded() -> None:
    manager = IdentityManager()
    snapshot = manager.run_bonding_protocol({"name": "Bonded"}, expected_revision=0)
    assert manager.get_phase() == PHASE_BONDED
    assert snapshot.revision == 1


def test_pluggable_identity_derivation_is_invoked() -> None:
    derivation = _CountingDerivation()
    derivation.return_value = "custom-id-from-derivation"
    manager = IdentityManager(derivation=derivation)
    manager.apply_bonding_profile({"name": "Whatever"}, expected_revision=0)
    assert derivation.call_count == 1
    assert manager.get_identity()["name"] == "custom-id-from-derivation"


def test_pluggable_derivation_failure_propagates_as_identity_error() -> None:
    def bad_derivation(_fields):  # type: ignore[no-untyped-def]
        raise IdentityError("derivation refused")

    manager = IdentityManager(derivation=bad_derivation)
    with pytest.raises(IdentityError, match="derivation refused"):
        manager.apply_bonding_profile({"name": "Anything"}, expected_revision=0)


def test_pluggable_derivation_returning_empty_id_raises() -> None:
    def empty_derivation(_fields):  # type: ignore[no-untyped-def]
        return ""

    manager = IdentityManager(derivation=empty_derivation)
    with pytest.raises(IdentityError, match="derivation returned empty id"):
        manager.apply_bonding_profile({"name": "X"}, expected_revision=0)


def test_resource_property_is_canonical_companion_identity() -> None:
    manager = IdentityManager()
    assert manager.resource == "companion:identity"


def test_snapshot_is_revision_tracked() -> None:
    manager = IdentityManager()
    s0 = manager.snapshot()
    assert s0.revision == 0
    s1 = manager.apply_bonding_profile({"name": "After"}, expected_revision=0)
    assert s1.revision == 1
    assert s0.state_sha256 != s1.state_sha256
