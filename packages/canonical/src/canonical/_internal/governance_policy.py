from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

PolicyRule = tuple[str, str]


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


class StaticGovernancePolicy:
    def __init__(
        self,
        allow_rules: Iterable[PolicyRule] | None = None,
        deny_rules: Iterable[PolicyRule] | None = None,
    ) -> None:
        self._allow_rules = set(allow_rules or ())
        self._deny_rules = set(deny_rules or ())

    def allow_rules(self) -> list[PolicyRule]:
        return sorted(self._allow_rules)

    def deny_rules(self) -> list[PolicyRule]:
        return sorted(self._deny_rules)

    def to_record(self) -> dict[str, list[list[str]]]:
        return {
            "allow_rules": [[action, resource] for action, resource in self.allow_rules()],
            "deny_rules": [[action, resource] for action, resource in self.deny_rules()],
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> StaticGovernancePolicy:
        return cls(
            allow_rules=_rules_from_record(record.get("allow_rules", [])),
            deny_rules=_rules_from_record(record.get("deny_rules", [])),
        )

    def evaluate(
        self,
        actor_id: str,
        action: str,
        resource: str,
        context: Mapping[str, Any],
    ) -> PolicyDecision:
        if context.get("governance_uncertain"):
            return PolicyDecision(False, "governance uncertainty")
        if self._matches(self._deny_rules, action, resource):
            return PolicyDecision(False, "governance policy denied action")
        if self._matches(self._allow_rules, action, resource):
            return PolicyDecision(True, "governance policy allowed action")
        return PolicyDecision(False, "governance policy did not allow action")

    @staticmethod
    def _matches(rules: set[PolicyRule], action: str, resource: str) -> bool:
        candidates = {
            (action, resource),
            (action, "*"),
            ("*", resource),
            ("*", "*"),
        }
        return bool(rules & candidates)


def _rules_from_record(rules: Any) -> list[PolicyRule]:
    parsed = []
    for rule in rules:
        if len(rule) != 2:
            raise ValueError("policy rules must contain action and resource")
        parsed.append((str(rule[0]), str(rule[1])))
    return parsed
