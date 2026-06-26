"""Unit tests for cerberus.agent.CerberusAgent."""

from __future__ import annotations

import pytest

from cerberus import (
    ALLOWED_AGENT_STATES,
    ALLOWED_ROLES,
    CerberusAgent,
    CerberusAgentError,
)


def _valid_kwargs() -> dict[str, str]:
    return {"agent_id": "agent-1", "role": "primary"}


def test_agent_constructs_with_valid_inputs() -> None:
    a = CerberusAgent(**_valid_kwargs())
    assert a.agent_id == "agent-1"
    assert a.role == "primary"
    assert a.current_state == "initializing"


def test_agent_rejects_empty_agent_id() -> None:
    with pytest.raises(CerberusAgentError, match="agent_id"):
        CerberusAgent(agent_id="", role="primary")


def test_agent_rejects_unknown_role() -> None:
    with pytest.raises(CerberusAgentError, match="role"):
        CerberusAgent(agent_id="a", role="god")


def test_agent_rejects_unknown_initial_state() -> None:
    with pytest.raises(CerberusAgentError, match="initial_state"):
        CerberusAgent(agent_id="a", role="primary", initial_state="yolo")


def test_agent_accepts_explicit_initial_state() -> None:
    a = CerberusAgent(agent_id="a", role="primary", initial_state="active")
    assert a.current_state == "active"


def test_agent_transition_is_atomic() -> None:
    a = CerberusAgent(**_valid_kwargs())
    snap = a.transition("active", expected_revision=0)
    assert a.current_state == "active"
    assert snap.revision == 1


def test_agent_transition_rejects_unknown_state() -> None:
    a = CerberusAgent(**_valid_kwargs())
    with pytest.raises(CerberusAgentError, match="target_state"):
        a.transition("flying", expected_revision=0)
    assert a.current_state == "initializing"


def test_agent_transition_with_stale_revision_raises() -> None:
    from kernel import RevisionConflictError

    a = CerberusAgent(**_valid_kwargs())
    a.transition("active", expected_revision=0)
    with pytest.raises(RevisionConflictError):
        a.transition("paused", expected_revision=0)


def test_allowed_roles_includes_required_set() -> None:
    for r in ("primary", "auxiliary", "observer", "executor"):
        assert r in ALLOWED_ROLES


def test_allowed_agent_states_includes_required_set() -> None:
    for s in ("initializing", "active", "paused", "retiring", "retired"):
        assert s in ALLOWED_AGENT_STATES
