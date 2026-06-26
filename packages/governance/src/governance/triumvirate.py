"""Triumvirate governance: three-vote consensus with configurable quorum.

A :class:`TriumvirateGovernor` composes exactly three sub-governors and
reduces their votes to a single :class:`Vote` using a quorum rule. The
intent is to model the legacy ``triumvirate_server.py`` concept
("three independent votes produce a decision") in a form that fits
Beginnings' existing ``Governor`` Protocol, ``Vote`` / ``Outcome`` /
``Decision`` types, and ``EventSpine`` audit chain.

Quorum rules
------------

* ``Quorum.UNANIMOUS`` — every sub-governor must ``ALLOW``. Any ``DENY``
  vetoes; any ``ESCALATE`` escalates. No ``DENY`` can be overridden.
* ``Quorum.MAJORITY`` (default) — at least 2 of 3 ``ALLOW`` votes are
  required. Any ``DENY`` still vetoes (fail-closed). Any ``ESCALATE``
  escalates unless a ``DENY`` veto already applies.
* ``Quorum.SUPERMAJORITY`` — same as ``MAJORITY`` but reports
  ``DENY`` if exactly 0 ``ALLOW`` (consensus against).

The triumvirate inherits ``GovernanceEngine``'s fail-closed guarantees:
a sub-governor exception or identity mismatch is treated as ``DENY``
by the wrapping :meth:`GovernanceEngine._safe_vote`. Therefore a
``TriumvirateGovernor`` should be passed alongside other governors
inside a :class:`GovernanceEngine`, not used standalone.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from governance.policy import Governor
from governance.types import Vote
from kernel import ActionRequest, Outcome


class Quorum(StrEnum):
    """Quorum rule for reducing three sub-governor votes to one."""

    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    SUPERMAJORITY = "supermajority"


_REQUIRED_SUBGOVERNORS: Final[int] = 3


class TriumvirateError(ValueError):
    """Raised when a triumvirate is constructed with an invalid configuration."""


@dataclass(frozen=True)
class _Tally:
    allow: int = 0
    deny: int = 0
    escalate: int = 0

    @property
    def total(self) -> int:
        return self.allow + self.deny + self.escalate


def _tally(votes: tuple[Vote, ...]) -> _Tally:
    tally = _Tally()
    for vote in votes:
        if vote.outcome is Outcome.ALLOW:
            tally = _Tally(tally.allow + 1, tally.deny, tally.escalate)
        elif vote.outcome is Outcome.DENY:
            tally = _Tally(tally.allow, tally.deny + 1, tally.escalate)
        elif vote.outcome is Outcome.ESCALATE:
            tally = _Tally(tally.allow, tally.deny, tally.escalate + 1)
    return tally


class TriumvirateGovernor:
    """Compose three sub-governors and reduce their votes under a quorum rule.

    The triumvirate name (e.g., ``"triumvirate"`` or ``"policy-safety-quorum"``)
    appears in the produced ``Vote.governor`` field so the wrapping
    :class:`GovernanceEngine` can audit it. Sub-governor names appear in the
    ``reason`` string for traceability.
    """

    def __init__(
        self,
        *,
        name: str,
        governors: Sequence[Governor],
        quorum: Quorum = Quorum.MAJORITY,
    ) -> None:
        if not name.strip():
            raise TriumvirateError("triumvirate name must not be empty")
        if len(governors) != _REQUIRED_SUBGOVERNORS:
            raise TriumvirateError(
                f"triumvirate requires exactly {_REQUIRED_SUBGOVERNORS} sub-governors; "
                f"got {len(governors)}"
            )
        sub_names = tuple(g.name for g in governors)
        if len(set(sub_names)) != _REQUIRED_SUBGOVERNORS:
            raise TriumvirateError(f"sub-governor names must be unique; got {sub_names}")
        self._name = name
        self._governors = tuple(governors)
        self._quorum = quorum

    @property
    def name(self) -> str:
        return self._name

    @property
    def quorum(self) -> Quorum:
        return self._quorum

    @property
    def sub_governors(self) -> tuple[Governor, ...]:
        return self._governors

    def evaluate(self, request: ActionRequest, state: Mapping[str, object]) -> Vote:
        """Collect sub-votes and reduce to a single Vote under the quorum rule.

        The returned ``reason`` lists each sub-governor's vote for audit
        purposes, e.g. ``"safety:ALLOW | policy:ESCALATE | capability:ALLOW"``.
        """
        sub_votes = tuple(g.evaluate(request, state) for g in self._governors)
        tally = _tally(sub_votes)
        audit_reason = " | ".join(f"{v.governor}:{v.outcome.value}" for v in sub_votes)

        # Hard-fail: any DENY vetoes regardless of quorum.
        if tally.deny > 0:
            denials = tuple(v for v in sub_votes if v.outcome is Outcome.DENY)
            combined = "; ".join(f"{v.governor}:{v.reason}" for v in denials)
            return Vote(self._name, Outcome.DENY, f"veto ({combined}) [{audit_reason}]")

        # Apply quorum-specific ALLOW threshold.
        outcome: Outcome
        match self._quorum:
            case Quorum.UNANIMOUS:
                outcome = (
                    Outcome.ALLOW if tally.allow == _REQUIRED_SUBGOVERNORS else Outcome.ESCALATE
                )
            case Quorum.MAJORITY:
                outcome = Outcome.ALLOW if tally.allow >= 2 else Outcome.ESCALATE
            case Quorum.SUPERMAJORITY:
                if tally.allow == _REQUIRED_SUBGOVERNORS:
                    outcome = Outcome.ALLOW
                elif tally.allow == 0:
                    outcome = Outcome.DENY
                else:
                    outcome = Outcome.ESCALATE

        if outcome is Outcome.ALLOW:
            return Vote(self._name, outcome, f"quorum=ok [{audit_reason}]")
        if outcome is Outcome.DENY:
            return Vote(self._name, outcome, f"supermajority-deny [{audit_reason}]")
        return Vote(self._name, outcome, f"quorum=insufficient [{audit_reason}]")


__all__ = [
    "Quorum",
    "TriumvirateError",
    "TriumvirateGovernor",
]
