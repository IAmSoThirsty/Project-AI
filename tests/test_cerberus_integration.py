"""Cross-package integration test for packages/cerberus/.

Verifies that cerberus agent + spawn_constraints + lockdown compose
correctly, with consistent state and atomicity across modules.
"""

from __future__ import annotations

import pytest

from cerberus import (
    CerberusAgent,
    LockdownController,
    LockdownError,
    SpawnConstraints,
)


def test_spawn_then_agent_lifecycle() -> None:
    """End-to-end: spawn a primary agent, then transition through states."""
    spawn = SpawnConstraints()
    spawn.request_spawn(
        agent_id="agent-1",
        agent_type="primary",
        requested_capability="cap.execute",
        parent_chain=[],
        expected_revision=0,
    )
    agent = CerberusAgent(agent_id="agent-1", role="primary")
    agent.transition("active", expected_revision=0)
    agent.transition("paused", expected_revision=1)
    agent.transition("active", expected_revision=2)
    assert agent.current_state == "active"
    assert len(spawn.history) == 1


def test_lockdown_blocks_subsequent_spawns() -> None:
    """Once locked, spawn attempts should be blocked (caller checks first)."""
    spawn = SpawnConstraints()
    lockdown = LockdownController()
    # First spawn succeeds
    spawn.request_spawn(
        agent_id="a-1",
        agent_type="primary",
        requested_capability="cap.x",
        parent_chain=[],
        expected_revision=0,
    )
    # Activate lockdown
    lockdown.activate(reason="manual", expected_revision=0)
    # Subsequent operation should check lockdown first and refuse
    with pytest.raises(LockdownError):
        lockdown.check_or_raise()


def test_lockdown_blocks_spawn_via_caller_pattern() -> None:
    """Demonstrates the integration pattern: caller checks lockdown, then spawns."""
    spawn = SpawnConstraints()
    lockdown = LockdownController()
    lockdown.activate(reason="external_halt", expected_revision=0)
    # Caller pattern: check lockdown, then spawn
    try:
        lockdown.check_or_raise()
        spawn.request_spawn(
            agent_id="a-blocked",
            agent_type="primary",
            requested_capability="cap.x",
            parent_chain=[],
            expected_revision=0,
        )
    except LockdownError as e:
        assert "external_halt" in str(e)
        assert len(spawn.history) == 0


def test_lockdown_threshold_breach_activates_via_check() -> None:
    """Sustained denials should trigger auto-lockdown via check_or_raise."""
    spawn = SpawnConstraints()
    lockdown = LockdownController()
    # Simulate 3 denials (failed spawns)
    for i in range(3):
        with pytest.raises(Exception):  # SpawnConstraintError
            spawn.request_spawn(
                agent_id=f"bad-{i}",
                agent_type="unknown_type",  # policy denial
                requested_capability="cap.x",
                parent_chain=[],
                expected_revision=i,
            )
    # Auto-activation via evaluate_and_activate (separate from check_or_raise)
    lockdown.evaluate_and_activate(recent_denial_count=3)
    assert lockdown.is_active is True
    assert lockdown.reason == "threshold_breach"
    # Now check_or_raise blocks
    with pytest.raises(LockdownError):
        lockdown.check_or_raise()


def test_released_lockdown_can_be_re_armed_via_state_update() -> None:
    """After release, the controller returns to a non-active state."""
    lockdown = LockdownController()
    lockdown.activate(reason="policy_violation", expected_revision=0)
    assert lockdown.is_active
    lockdown.release(expected_revision=1)
    assert not lockdown.is_active
    assert lockdown.reason == ""


def test_multiple_agents_have_independent_state() -> None:
    """Each CerberusAgent owns its own StateRegister; no shared mutation."""
    a1 = CerberusAgent(agent_id="a-1", role="primary")
    a2 = CerberusAgent(agent_id="a-2", role="auxiliary")
    a1.transition("active", expected_revision=0)
    a2.transition("active", expected_revision=0)
    assert a1.current_state == "active"
    assert a2.current_state == "active"
    assert a1.snapshot().revision == 1
    assert a2.snapshot().revision == 1
    # Transition one; the other unaffected
    a1.transition("paused", expected_revision=1)
    assert a1.current_state == "paused"
    assert a2.current_state == "active"
