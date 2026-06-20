"""Composable governor protocol and deterministic rule governor."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from governance.types import Vote
from kernel import ActionRequest, Outcome


class Governor(Protocol):
    @property
    def name(self) -> str: ...

    def evaluate(self, request: ActionRequest, state: Mapping[str, object]) -> Vote: ...


type RulePredicate = Callable[[ActionRequest, Mapping[str, object]], bool]


@dataclass(frozen=True)
class Rule:
    name: str
    predicate: RulePredicate
    failure_outcome: Outcome
    failure_reason: str

    def __post_init__(self) -> None:
        if self.failure_outcome is Outcome.ALLOW:
            raise ValueError("rule failure outcome cannot be ALLOW")


class RuleGovernor:
    def __init__(self, name: str, rules: Sequence[Rule]) -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        self._name = name
        self._rules = tuple(rules)

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, request: ActionRequest, state: Mapping[str, object]) -> Vote:
        failures = tuple(rule for rule in self._rules if not rule.predicate(request, state))
        denials = tuple(rule for rule in failures if rule.failure_outcome is Outcome.DENY)
        if denials:
            return Vote(self.name, Outcome.DENY, "; ".join(rule.failure_reason for rule in denials))
        escalations = tuple(rule for rule in failures if rule.failure_outcome is Outcome.ESCALATE)
        if escalations:
            return Vote(
                self.name,
                Outcome.ESCALATE,
                "; ".join(rule.failure_reason for rule in escalations),
            )
        return Vote(self.name, Outcome.ALLOW)
