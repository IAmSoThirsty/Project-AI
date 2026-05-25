"""PSIA Invariant Head — root invariant enforcement."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from psia.gate.identity_head import GateVote, VoteReason


@dataclass
class InvariantRule:
    code: str
    description: str
    check_fn: Any = field(repr=False)


class InvariantRegistry:
    def __init__(self) -> None:
        self._rules: list[InvariantRule] = []

    def add_rule(self, rule: InvariantRule) -> None:
        self._rules.append(rule)


def _is_read_only(action: str) -> bool:
    return action in {"read", "list", "get", "describe", "watch"}


def _check_inv_root_001(envelope: Any) -> bool:
    """INV-ROOT-001: Cannot mutate invariant resources."""
    if _is_read_only(envelope.intent.action):
        return False
    return "state://invariant" in envelope.intent.resource


def _check_inv_root_005(envelope: Any) -> bool:
    """INV-ROOT-005: Cannot modify Cerberus configuration."""
    if _is_read_only(envelope.intent.action):
        return False
    return "state://cerberus" in envelope.intent.resource


def _check_inv_root_009(envelope: Any) -> bool:
    """INV-ROOT-009: Cannot delete ledger entries."""
    return envelope.intent.action == "delete" and "state://ledger" in envelope.intent.resource


_BUILTIN_RULES = [
    ("INV_ROOT_001", "Cannot mutate invariant resources", _check_inv_root_001),
    ("INV_ROOT_005", "Cannot modify Cerberus configuration", _check_inv_root_005),
    ("INV_ROOT_009", "Cannot delete ledger entries", _check_inv_root_009),
]


class InvariantHead:
    def __init__(self, registry: InvariantRegistry | None = None) -> None:
        self._registry = registry

    def evaluate(self, envelope: Any) -> GateVote:
        violations: list[VoteReason] = []

        for code, description, check_fn in _BUILTIN_RULES:
            if check_fn(envelope):
                violations.append(VoteReason(code=code, message=description))

        if violations:
            return GateVote(head="invariant", decision="deny", reasons=violations)

        return GateVote(head="invariant", decision="allow")
