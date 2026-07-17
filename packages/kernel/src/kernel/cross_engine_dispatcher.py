"""Phase 3: Cross-engine event dispatcher.

Cascades an originating engine event to subscribed downstream engines
through the kernel's authority model. Every cascade hop is recorded on the
hash-chained ``EventSpine`` for auditability, and a ``DENY``/``ESCALATE``
authority decision halts the cascade at that hop (fail-closed).

Design constraints (per continuity map authority review):
- Downward-only: an engine may emit downstream events, never pull authority.
- Deterministic: cascade order follows subscriber registration order.
- Auditable: each hop is an ``Event`` on the spine with ``cascade`` metadata.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from kernel.event_spine import Event, EventSpine
from kernel.types import Decision, Outcome

# An engine handler receives a cascaded Event and returns zero or more
# downstream events (as (event_type, payload) tuples) to propagate further.
EngineHandler = Callable[[Event], Sequence[tuple[str, Mapping[str, Any]]]]


@dataclass
class CascadeResult:
    """Outcome of dispatching one originating event through the cascade."""

    origin_event: Event
    hops: list[Event] = field(default_factory=list)
    halted_by: Outcome | None = None
    halted_reason: str | None = None

    @property
    def propagated(self) -> int:
        return len(self.hops)


class CrossEngineDispatcher:
    """Routes events between registered engines under kernel authority."""

    def __init__(
        self,
        spine: EventSpine,
        authority: Callable[[Event], Decision] | None = None,
    ) -> None:
        """
        Args:
            spine: hash-chained event log; every cascade hop is appended here.
            authority: optional gate. Given a would-be cascaded event, returns a
                ``Decision``. ``DENY``/``ESCALATE`` halts the cascade (fail-closed);
                ``ALLOW`` permits the hop. If ``None``, all hops are permitted.
        """
        self._spine = spine
        self._authority = authority
        self._subscribers: list[EngineHandler] = []
        self._sequence = 0

    def register(self, handler: EngineHandler) -> None:
        """Register a downstream engine handler (subscriber)."""
        self._subscribers.append(handler)

    def _check_authority(self, event: Event) -> Decision | None:
        if self._authority is None:
            return None
        return self._authority(event)

    def dispatch(
        self,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> CascadeResult:
        """Dispatch an originating event and cascade to all subscribers.

        Returns a ``CascadeResult`` describing the hops taken and whether the
        cascade was halted by authority.
        """
        origin = self._spine.append(event_type, dict(payload))
        result = CascadeResult(origin_event=origin)

        pending: list[tuple[str, Mapping[str, Any]]] = [(event_type, dict(payload))]

        # Bounded cascade to prevent runaway loops (each subscriber may emit
        # at most once per originating dispatch round; depth + total-hop capped).
        max_depth = len(self._subscribers) + 1
        max_total_hops = 50
        depth = 0
        while pending and depth <= max_depth and len(result.hops) < max_total_hops:
            depth += 1
            next_pending: list[tuple[str, Mapping[str, Any]]] = []
            for handler in self._subscribers:
                for ev_type, ev_payload in pending:
                    cascade_payload = {
                        "cascade_from": ev_type,
                        "cascade_depth": depth,
                        **dict(ev_payload),
                    }
                    decision = self._check_authority(
                        Event(
                            sequence=0,
                            event_type=ev_type,
                            payload=MappingProxyLike(dict(cascade_payload)),
                            timestamp=origin.timestamp,
                            previous_hash=origin.previous_hash,
                            event_hash=origin.event_hash,
                        )
                    )
                    if decision is not None and decision.outcome in (
                        Outcome.DENY,
                        Outcome.ESCALATE,
                    ):
                        result.halted_by = decision.outcome
                        result.halted_reason = "; ".join(decision.reasons) or None
                        # Fail-closed: stop the entire cascade.
                        return result

                    hop = self._spine.append(
                        f"cascade:{ev_type}",
                        cascade_payload,
                    )
                    result.hops.append(hop)
                    emitted = handler(hop)
                    for child_type, child_payload in emitted:
                        next_pending.append((child_type, dict(child_payload)))
            pending = next_pending

        return result


def MappingProxyLike(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    """Thin wrapper so callers need not import MappingProxyType directly."""
    from types import MappingProxyType

    return MappingProxyType(dict(mapping))
