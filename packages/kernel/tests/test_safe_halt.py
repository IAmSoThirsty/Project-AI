"""Unit tests for kernel.safe_halt.SafeHaltController.

Honest scope:
- Covered: write-block while halted, read passthrough, monotonic re-trigger,
  authorized reset (including fail-closed blank rejection), idempotent reset,
  entered/exited event emission with an intact hash chain, and the history trail.
- Not covered: integration with ExecutionGate (see
  packages/execution/tests/test_gate.py) and any InvariantEngine wiring
  (INV-ROOT-9), which is a deferred hook, not implemented here.
"""

from __future__ import annotations

import pytest
from kernel.safe_halt import HALT_ENTERED_EVENT, HALT_EXITED_EVENT

from kernel import (
    EventSpine,
    HaltReason,
    SafeHaltController,
    SafeHaltError,
    verify_event_chain,
)


def test_new_controller_is_not_halted() -> None:
    controller = SafeHaltController("node-1")
    assert controller.is_halted is False
    assert controller.active_halt is None
    controller.check_write_allowed()  # does not raise


def test_rejects_blank_node_id() -> None:
    with pytest.raises(ValueError, match="node_id"):
        SafeHaltController("   ")


def test_trigger_halt_blocks_writes_reads_pass() -> None:
    controller = SafeHaltController("node-1")
    controller.trigger_halt(HaltReason.SECURITY_INCIDENT, "intrusion", "sentinel")
    assert controller.is_halted is True
    controller.check_read_allowed()  # reads always pass
    with pytest.raises(SafeHaltError, match="SAFE-HALT"):
        controller.check_write_allowed()


def test_trigger_halt_requires_triggered_by() -> None:
    controller = SafeHaltController("node-1")
    with pytest.raises(ValueError, match="triggered_by"):
        controller.trigger_halt(HaltReason.ADMINISTRATIVE, "manual", "")


def test_reset_clears_halt_and_resumes() -> None:
    controller = SafeHaltController("node-1")
    controller.trigger_halt(HaltReason.ADMINISTRATIVE, "manual stop", "operator")
    assert controller.reset(authorized_by="operator") is True
    assert controller.is_halted is False
    assert controller.active_halt is None
    controller.check_write_allowed()  # no longer raises


def test_reset_requires_non_blank_authorized_by() -> None:
    controller = SafeHaltController("node-1")
    controller.trigger_halt(HaltReason.ADMINISTRATIVE, "manual stop", "operator")
    with pytest.raises(SafeHaltError, match="authorizing identity"):
        controller.reset(authorized_by="  ")
    assert controller.is_halted is True  # still halted after a rejected reset


def test_reset_when_not_halted_is_idempotent_false() -> None:
    controller = SafeHaltController("node-1")
    assert controller.reset(authorized_by="operator") is False


def test_halt_is_monotonic_first_reason_retained() -> None:
    controller = SafeHaltController("node-1")
    controller.trigger_halt(HaltReason.INVARIANT_VIOLATION, "first", "engine")
    controller.trigger_halt(HaltReason.KEY_COMPROMISE, "second", "sentinel")
    active = controller.active_halt
    assert active is not None
    assert active.reason is HaltReason.INVARIANT_VIOLATION  # first halt stays active
    # A single reset clears the active halt even though two triggers were recorded.
    assert controller.reset(authorized_by="operator") is True
    assert controller.is_halted is False


def test_history_records_full_halt_reset_trail() -> None:
    controller = SafeHaltController("node-1")
    controller.trigger_halt(HaltReason.ADMINISTRATIVE, "stop", "operator")
    controller.reset(authorized_by="operator")
    kinds = [event.kind for event in controller.history]
    assert kinds == ["entered", "exited"]
    assert controller.history[0].reason is HaltReason.ADMINISTRATIVE
    assert controller.history[1].reason is None


def test_events_emitted_to_spine_with_valid_chain() -> None:
    events = EventSpine()
    controller = SafeHaltController("node-1", events=events)
    controller.trigger_halt(HaltReason.CHAIN_CORRUPTION, "ledger break", "auditor")
    controller.reset(authorized_by="operator")
    types = [event.event_type for event in events.events()]
    assert types == [HALT_ENTERED_EVENT, HALT_EXITED_EVENT]
    assert verify_event_chain(events.events()).valid is True
