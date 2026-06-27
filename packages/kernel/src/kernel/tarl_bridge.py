"""Kernel bridge for TARL enforcement events.

Refactored from legacy ``kernel/tarl_gate.py`` + ``kernel/tarl_codex_bridge.py``.
The legacy code imported directly from ``tarl`` (TARL runtime) and
``src.cognition.codex.escalation`` (CodexDeus escalation). Beginnings now has
``packages/tarl/``, but this bridge intentionally accepts a verdict-shaped
payload instead of importing that package directly.

This bridge provides the **seam** the legacy code assumed: it accepts a TARL
verdict-shaped object (a mapping containing ``verdict`` + ``reason``), and:

* If ``verdict == "ALLOW"`` → returns the verdict unchanged.
* If ``verdict == "DENY"`` → raises :class:`TarlEnforcementError`.
* If ``verdict == "ESCALATE"`` → appends an escalation event to the
  :class:`EventSpine` and raises :class:`TarlEnforcementError` so callers
  see a fail-closed signal.

The bridge has **no runtime dependency on TARL or CodexDeus**. It is wired
through :class:`EventSpine` and an injectable ``escalation_handler`` so that
``packages/tarl/`` and ``packages/companion/`` cognitive services can plug in
concrete implementations without changing this file. This is the Beginnings
pattern: explicit seams, no hidden imports.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Final, Literal, cast

from kernel.event_spine import Event, EventSpine
from kernel.invariant_severity import InvariantSeverity
from kernel.types import JsonValue

TarlVerdictValue = Literal["ALLOW", "DENY", "ESCALATE"]


class TarlEnforcementError(Exception):
    """Raised when TARL policy enforcement blocks (DENY) or escalates an action."""


@dataclass(frozen=True)
class TarlVerdictView:
    """Lightweight view over a TARL verdict payload.

    The legacy ``tarl.spec.TarlVerdict`` enum had three members. This view
    accepts the same shape (a Mapping or dataclass-like object with
    ``verdict`` and ``reason`` attributes) without depending on the TARL
    package itself.
    """

    verdict: TarlVerdictValue
    reason: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> TarlVerdictView:
        verdict_raw = payload.get("verdict")
        if verdict_raw not in ("ALLOW", "DENY", "ESCALATE"):
            raise ValueError(f"invalid TARL verdict: {verdict_raw!r}")
        reason_raw = payload.get("reason", "")
        return cls(verdict=verdict_raw, reason=str(reason_raw))


type EscalationHandler = Callable[[TarlVerdictView, Mapping[str, JsonValue]], None]
"""Callback invoked when an ESCALATE verdict is observed. Returns nothing; side effects only."""


def _default_escalation_handler(verdict: TarlVerdictView, context: Mapping[str, JsonValue]) -> None:
    """Built-in no-op escalation handler. Real implementations would dispatch
    to the cognitive services package (``packages/companion/``) or write to
    an external escalation channel. Keeping this in-process by default means
    :class:`TarlGate` is usable in tests and CI without external services.
    """


def _verdict_to_severity(verdict: TarlVerdictValue) -> InvariantSeverity:
    if verdict == "DENY":
        return InvariantSeverity.BLOCKING
    if verdict == "ESCALATE":
        return InvariantSeverity.BLOCKING
    return InvariantSeverity.INFO


class TarlGate:
    """Apply a TARL verdict to an execution context, fail-closed on DENY/ESCALATE."""

    GATE_EVENT_TYPE: Final[str] = "tarl.gate"

    def __init__(
        self,
        spine: EventSpine,
        *,
        escalation_handler: EscalationHandler | None = None,
    ) -> None:
        self._spine = spine
        self._handle_escalation: EscalationHandler = (
            escalation_handler or _default_escalation_handler
        )

    def enforce(
        self, execution_context: Mapping[str, JsonValue], verdict: Mapping[str, Any]
    ) -> Event:
        """Enforce a TARL verdict against an execution context.

        Returns the recorded gate event. Raises :class:`TarlEnforcementError`
        on DENY or ESCALATE so callers see a fail-closed signal.
        """
        view = TarlVerdictView.from_payload(verdict)

        gate_event = self._spine.append(
            event_type=self.GATE_EVENT_TYPE,
            payload={
                "verdict": view.verdict,
                "reason": view.reason,
                "context_keys": cast("list[JsonValue]", sorted(str(k) for k in execution_context)),
                "severity": int(_verdict_to_severity(view.verdict)),
            },
        )

        if view.verdict == "ALLOW":
            return gate_event

        if view.verdict == "ESCALATE":
            self._handle_escalation(view, execution_context)

        raise TarlEnforcementError(f"{view.verdict}: {view.reason}")


__all__ = [
    "EscalationHandler",
    "TarlEnforcementError",
    "TarlGate",
    "TarlVerdictValue",
    "TarlVerdictView",
]
