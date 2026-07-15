"""Phase 3 tests: cross-engine event dispatcher cascade + authority gate."""

from __future__ import annotations

from kernel.cross_engine_dispatcher import CrossEngineDispatcher
from kernel.event_spine import EventSpine
from kernel.types import Decision, Outcome


def _allow(event):  # pragma: no cover - trivial
    return Decision(outcome=Outcome.ALLOW, reasons=("ok",), policy_version="p1")


def test_cascade_propagates_to_all_subscribers():
    spine = EventSpine()
    disp = CrossEngineDispatcher(spine, authority=_allow)

    seen = []

    def engine_a(event):
        seen.append(("A", event.event_type))
        return [("downstream_x", {"v": 1})]

    def engine_b(event):
        seen.append(("B", event.event_type))
        return []

    disp.register(engine_a)
    disp.register(engine_b)

    result = disp.dispatch("origin", {"seed": 42})
    # Both subscribers receive the wrapped cascade event for the origin.
    assert ("A", "cascade:origin") in seen
    assert ("B", "cascade:origin") in seen
    # Cascade hop recorded on the spine.
    assert result.propagated >= 1
    assert result.halted_by is None
    # Spine contains the origin + at least one cascade hop.
    assert len(spine.events()) >= 2


def test_fail_closed_on_deny():
    spine = EventSpine()

    def deny(event):
        return Decision(
            outcome=Outcome.DENY, reasons=("blocked by authority",), policy_version="p1"
        )

    disp = CrossEngineDispatcher(spine, authority=deny)
    fired = []

    def engine_a(event):
        fired.append(event.event_type)
        return []

    disp.register(engine_a)

    result = disp.dispatch("origin", {"seed": 1})
    # No subscriber fired; cascade halted before any hop.
    assert fired == []
    assert result.halted_by is Outcome.DENY
    assert "blocked by authority" in (result.halted_reason or "")
    # Only the origin event is on the spine; no cascade hop emitted.
    assert len(spine.events()) == 1


def test_escalate_halts_cascade():
    spine = EventSpine()

    def escalate(event):
        return Decision(
            outcome=Outcome.ESCALATE, reasons=("needs human review",), policy_version="p1"
        )

    disp = CrossEngineDispatcher(spine, authority=escalate)
    fired = []

    def engine_a(event):
        fired.append(event.event_type)
        return []

    disp.register(engine_a)

    result = disp.dispatch("origin", {})
    assert fired == []
    assert result.halted_by is Outcome.ESCALATE
    assert len(spine.events()) == 1
