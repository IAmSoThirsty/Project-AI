"""Tests for ``kernel.tarl_bridge`` (rebuilt legacy TARL gate)."""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from kernel.tarl_bridge import (
    TarlEnforcementError,
    TarlGate,
    TarlVerdictView,
)
from kernel.types import JsonValue

from kernel import EventSpine


def test_verdict_view_accepts_allow_deny_escalate() -> None:
    assert TarlVerdictView.from_payload({"verdict": "ALLOW", "reason": "ok"}).verdict == "ALLOW"
    assert TarlVerdictView.from_payload({"verdict": "DENY"}).reason == ""


def test_verdict_view_rejects_unknown_verdict() -> None:
    with pytest.raises(ValueError, match="invalid TARL verdict"):
        TarlVerdictView.from_payload({"verdict": "MAYBE"})


def test_gate_allows_on_allow_and_records_event() -> None:
    spine = EventSpine()
    gate = TarlGate(spine)
    event = gate.enforce({"actor": "alice", "op": "read"}, {"verdict": "ALLOW", "reason": "ok"})
    assert event.event_type == TarlGate.GATE_EVENT_TYPE
    assert spine.events()[0].event_hash == event.event_hash


def test_gate_raises_on_deny() -> None:
    spine = EventSpine()
    gate = TarlGate(spine)
    with pytest.raises(TarlEnforcementError, match="DENY"):
        gate.enforce({"actor": "alice"}, {"verdict": "DENY", "reason": "policy_violation"})
    # Event was still recorded before raising
    assert len(spine.events()) == 1


def test_gate_raises_on_escalate_and_invokes_handler() -> None:
    spine = EventSpine()
    captured: list[tuple[TarlVerdictView, Mapping[str, JsonValue]]] = []

    def handler(v: TarlVerdictView, ctx: Mapping[str, JsonValue]) -> None:
        captured.append((v, ctx))

    gate = TarlGate(spine, escalation_handler=handler)
    with pytest.raises(TarlEnforcementError, match="ESCALATE"):
        gate.enforce(
            {"actor": "bob", "sensitive": True}, {"verdict": "ESCALATE", "reason": "needs review"}
        )
    assert len(captured) == 1
    view, ctx = captured[0]
    assert view.verdict == "ESCALATE"
    assert ctx["actor"] == "bob"


def test_default_escalation_handler_is_noop() -> None:
    spine = EventSpine()
    gate = TarlGate(spine)  # no handler → default
    with pytest.raises(TarlEnforcementError):
        gate.enforce({}, {"verdict": "ESCALATE", "reason": "review"})


def test_gate_records_context_keys_not_values() -> None:
    """Security: gate must not leak context values into the audit event."""
    spine = EventSpine()
    gate = TarlGate(spine)
    secret_ctx = {"api_key": "sk-very-secret", "user": "alice"}
    gate.enforce(secret_ctx, {"verdict": "ALLOW", "reason": "ok"})
    event = spine.events()[0]
    # event.payload["context_keys"] should list keys only
    keys = [str(k) for k in event.payload["context_keys"]]  # type: ignore[union-attr]
    assert "api_key" in keys
    assert "user" in keys
    # And no raw values
    payload_str = str(dict(event.payload))
    assert "sk-very-secret" not in payload_str
    assert "alice" not in payload_str


def test_gate_event_payload_contains_verdict_severity_reason() -> None:
    spine = EventSpine()
    gate = TarlGate(spine)
    # DENY raises, so we catch and inspect the recorded event
    with pytest.raises(TarlEnforcementError):
        gate.enforce({}, {"verdict": "DENY", "reason": "test"})
    payload = dict(spine.events()[0].payload)
    assert payload["verdict"] == "DENY"
    assert payload["reason"] == "test"
    assert payload["severity"] == 30  # InvariantSeverity.BLOCKING


def test_gate_enforce_requires_nonempty_context_to_meaningfully_raise() -> None:
    """Empty context should still be enforceable; this just confirms the path."""
    spine = EventSpine()
    gate = TarlGate(spine)
    event = gate.enforce({}, {"verdict": "ALLOW"})
    assert event is not None
    assert [str(k) for k in event.payload["context_keys"]] == []  # type: ignore[union-attr]
