"""Triumvirate bridge: CCMA ``triumvirate_review`` -> Beginnings ``TriumvirateGovernor``.

CCMA's pipeline needs a ``TriumvirateReviewFn`` (Galahad/Cerberus/Codex's actual
constitutional reasoning). Beginnings already implements three-independent-votes
consensus in ``governance.TriumvirateGovernor`` (Galahad = policy/legitimacy,
Cerberus = security, Codex = constitutional law). This module adapts that real
governor into the CCMA callable, mapping its ``Outcome`` votes onto CCMA's
``TriumvirateRuling`` recommendation strings.

A ``TriumvirateGovernor`` is composed of three sub-governors and reduces their
votes under a quorum. We wrap it so CCMA's pipeline gets a genuine constitutional
ruling (allow / deny / revise / escalate) rather than a fabricated one.

The three sub-governors are supplied by the caller (the deployment wires Galahad,
Cerberus, and Codex). If the triumvirate is not wired, this returns a fail-closed
``TriumvirateRuling`` that denies — matching CCMA's deny-by-default posture.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from governance.triumvirate import Quorum

from governance import TriumvirateGovernor
from kernel import ActionRequest, Outcome
from memory.ccma.pipeline import CompiledProposal, TriumvirateRuling


def _outcome_to_recommendation(outcome: Outcome) -> tuple[str, str, str]:
    """Map a sub-governor ``Outcome`` onto CCMA's three recommendation strings."""
    if outcome is Outcome.ALLOW:
        return ("legitimate", "safe", "allow")
    if outcome is Outcome.DENY:
        return ("illegitimate", "unsafe", "deny")
    # ESCALATE
    return ("clarify", "escalate", "escalate")


class TriumvirateReviewBridge:
    """Adapt a real ``TriumvirateGovernor`` into CCMA's ``triumvirate_review`` callable."""

    def __init__(
        self,
        governor: TriumvirateGovernor,
        *,
        state: Mapping[str, object] | None = None,
    ) -> None:
        self._governor = governor
        self._state: Mapping[str, object] = state if state is not None else {}

    def __call__(self, compiled: CompiledProposal) -> TriumvirateRuling:
        from kernel import JsonValue

        payload: dict[str, JsonValue] = {
            "unsafe": compiled.unsafe,
            "effects": list(compiled.predicted_effects),
        }
        request = ActionRequest(
            action_id="ccma.review",
            actor="memory.ccma",
            operation="ccma.review",
            resource=compiled.proposition.statement,
            payload=payload,
        )
        vote = self._governor.evaluate(request, self._state)
        galahad, cerberus, codex = _outcome_to_recommendation(vote.outcome)
        return TriumvirateRuling(
            compiled=compiled,
            galahad_recommendation=galahad,
            cerberus_recommendation=cerberus,
            codex_judgment=codex,
        )


def fail_closed_ruling(compiled: CompiledProposal) -> TriumvirateRuling:
    """Deny-by-default ruling used when no triumvirate is wired."""
    return TriumvirateRuling(
        compiled=compiled,
        galahad_recommendation="illegitimate",
        cerberus_recommendation="unsafe",
        codex_judgment="deny",
    )


def build_triumvirate(
    *,
    name: str,
    governors: Sequence[object],
    quorum: Quorum = Quorum.MAJORITY,
) -> TriumvirateGovernor:
    """Construct a real ``TriumvirateGovernor`` (Galahad + Cerberus + Codex)."""
    return TriumvirateGovernor(name=name, governors=governors, quorum=quorum)  # type: ignore[arg-type]
