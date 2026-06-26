"""Unit tests for cerberus.lockdown.LockdownController."""

from __future__ import annotations

import pytest

from cerberus import (
    ALLOWED_LOCKDOWN_REASONS,
    LockdownController,
    LockdownError,
    default_lockdown_trigger,
)

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def test_controller_starts_armed() -> None:
    c = LockdownController()
    assert c.is_active is False
    assert c.reason == ""


def test_controller_rejects_unknown_initial_state() -> None:
    with pytest.raises(LockdownError, match="initial_state"):
        LockdownController(initial_state="yolo")


# ---------------------------------------------------------------------------
# Manual activation
# ---------------------------------------------------------------------------


def test_activate_sets_active_and_reason() -> None:
    c = LockdownController()
    snap = c.activate(reason="policy_violation", expected_revision=0)
    assert c.is_active is True
    assert c.reason == "policy_violation"
    assert snap.revision == 1


def test_activate_rejects_unknown_reason() -> None:
    c = LockdownController()
    with pytest.raises(LockdownError, match="reason"):
        c.activate(reason="because_i_said_so", expected_revision=0)


def test_allowed_reasons_includes_required_set() -> None:
    for r in ("policy_violation", "external_halt", "manual", "threshold_breach"):
        assert r in ALLOWED_LOCKDOWN_REASONS


# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------


def test_release_returns_to_released() -> None:
    c = LockdownController()
    c.activate(reason="manual", expected_revision=0)
    snap = c.release(expected_revision=1)
    assert c.is_active is False
    assert c.reason == ""
    assert snap.revision == 2


# ---------------------------------------------------------------------------
# check_or_raise (auto-activation + blocking)
# ---------------------------------------------------------------------------


def test_check_or_raise_passes_when_armed() -> None:
    c = LockdownController()
    c.check_or_raise()  # should not raise


def test_evaluate_and_activate_on_high_denial_count() -> None:
    c = LockdownController()
    activated = c.evaluate_and_activate(recent_denial_count=5, signal_active=False)
    assert activated is True
    assert c.is_active is True
    assert c.reason == "threshold_breach"


def test_evaluate_and_activate_on_signal() -> None:
    c = LockdownController()
    activated = c.evaluate_and_activate(recent_denial_count=0, signal_active=True)
    assert activated is True
    assert c.is_active is True


def test_check_or_raise_blocks_when_already_active() -> None:
    c = LockdownController()
    c.activate(reason="manual", expected_revision=0)
    with pytest.raises(LockdownError, match="locked down"):
        c.check_or_raise()


def test_evaluate_and_activate_no_op_below_threshold() -> None:
    c = LockdownController()
    activated = c.evaluate_and_activate(recent_denial_count=2, signal_active=False)
    assert activated is False
    assert c.is_active is False


# ---------------------------------------------------------------------------
# Default trigger
# ---------------------------------------------------------------------------


def test_default_trigger_threshold_is_3() -> None:
    assert default_lockdown_trigger(2, False) is False
    assert default_lockdown_trigger(3, False) is True
    assert default_lockdown_trigger(100, False) is True


def test_default_trigger_signal_overrides_count() -> None:
    assert default_lockdown_trigger(0, True) is True
    assert default_lockdown_trigger(-5, True) is True  # negative doesn't matter
