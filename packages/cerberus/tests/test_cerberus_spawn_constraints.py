"""Unit tests for cerberus.spawn_constraints.SpawnConstraints."""

from __future__ import annotations

import pytest

from cerberus import (
    ALLOWED_AGENT_TYPES,
    SpawnConstraintError,
    SpawnConstraints,
    default_spawn_policy,
)

# ---------------------------------------------------------------------------
# Default policy
# ---------------------------------------------------------------------------


def test_default_policy_accepts_valid_spawn() -> None:
    assert default_spawn_policy("primary", "cap.execute", []) is True


def test_default_policy_rejects_unknown_agent_type() -> None:
    assert default_spawn_policy("wonderful", "cap.execute", []) is False


def test_default_policy_rejects_empty_capability() -> None:
    assert default_spawn_policy("primary", "", []) is False
    assert default_spawn_policy("primary", "   ", []) is False


def test_default_policy_rejects_cycle_in_parent_chain() -> None:
    assert default_spawn_policy("primary", "cap.x", ["a", "b", "a"]) is False


def test_default_policy_accepts_long_no_cycle_chain() -> None:
    assert default_spawn_policy("primary", "cap.x", ["a", "b", "c", "d", "e"]) is True


def test_allowed_agent_types_includes_required_set() -> None:
    for t in ("primary", "auxiliary", "observer", "executor", "scout"):
        assert t in ALLOWED_AGENT_TYPES


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


def test_constraints_starts_armed() -> None:
    c = SpawnConstraints()
    assert c.status == "armed"
    assert c.history == []


def test_evaluate_does_not_mutate_state() -> None:
    c = SpawnConstraints()
    initial_rev = c.snapshot().revision
    c.evaluate(agent_type="primary", requested_capability="cap.x", parent_chain=[])
    assert c.snapshot().revision == initial_rev
    assert c.history == []


def test_request_spawn_appends_to_history_on_approval() -> None:
    c = SpawnConstraints()
    snap = c.request_spawn(
        agent_id="a-1",
        agent_type="primary",
        requested_capability="cap.execute",
        parent_chain=[],
        expected_revision=0,
    )
    assert snap.revision == 1
    assert len(c.history) == 1
    assert c.history[0]["agent_id"] == "a-1"


def test_request_spawn_raises_on_policy_denial() -> None:
    c = SpawnConstraints()
    with pytest.raises(SpawnConstraintError, match="spawn denied"):
        c.request_spawn(
            agent_id="a-2",
            agent_type="unknown_type",
            requested_capability="cap.execute",
            parent_chain=[],
            expected_revision=0,
        )
    assert c.history == []


def test_request_spawn_rejects_empty_agent_id() -> None:
    c = SpawnConstraints()
    with pytest.raises(SpawnConstraintError, match="agent_id"):
        c.request_spawn(
            agent_id="",
            agent_type="primary",
            requested_capability="cap.x",
            parent_chain=[],
            expected_revision=0,
        )


def test_request_spawn_rejects_cycle_in_parent_chain() -> None:
    c = SpawnConstraints()
    with pytest.raises(SpawnConstraintError):
        c.request_spawn(
            agent_id="a-3",
            agent_type="primary",
            requested_capability="cap.x",
            parent_chain=["parent-1", "parent-1"],
            expected_revision=0,
        )


def test_request_spawn_atomic_denied_does_not_bump_revision() -> None:
    c = SpawnConstraints()
    initial_rev = c.snapshot().revision
    with pytest.raises(SpawnConstraintError):
        c.request_spawn(
            agent_id="a-bad",
            agent_type="primary",
            requested_capability="",
            parent_chain=[],
            expected_revision=0,
        )
    assert c.snapshot().revision == initial_rev


def test_pluggable_policy_can_be_strict() -> None:
    """A custom policy that returns False should deny everything."""

    def deny_all(_t: str, _c: str, _p: list[str]) -> bool:
        return False

    c = SpawnConstraints(policy=deny_all)  # type: ignore[arg-type]
    with pytest.raises(SpawnConstraintError):
        c.request_spawn(
            agent_id="x",
            agent_type="primary",
            requested_capability="cap.x",
            parent_chain=[],
            expected_revision=0,
        )


def test_pluggable_policy_can_be_permissive() -> None:
    """A custom policy that returns True should allow everything."""

    def allow_all(_t: str, _c: str, _p: list[str]) -> bool:
        return True

    c = SpawnConstraints(policy=allow_all)  # type: ignore[arg-type]
    snap = c.request_spawn(
        agent_id="y",
        agent_type="unknown",  # default policy would deny, but allow_all accepts
        requested_capability="cap.x",
        parent_chain=[],
        expected_revision=0,
    )
    assert snap.revision == 1
