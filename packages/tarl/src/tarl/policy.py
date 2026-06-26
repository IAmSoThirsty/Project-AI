"""
tarl.policy — TARL policy evaluator with pluggable decision rule.

A TARL policy reduces an input context (dict) to a TarlDecision via a
configurable rule function. The PolicyProtocol allows alternate
implementations without modifying this module.

This is the minimum surface from legacy `tarl/policy.py`:
- TarlPolicy (named evaluator wrapping a Callable[[dict], TarlDecision])
- PolicyProtocol (Protocol for pluggable implementations)

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.policy imports only tarl.spec + stdlib.
- Fail-closed: a policy whose rule raises surfaces the exception
  as TarlError (no silent ALLOW).
- Pluggable seams: PolicyProtocol allows alternate evaluator implementations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from tarl.spec import TarlDecision, TarlError, TarlVerdict, make_decision

# A TARL policy rule is a pure function from context dict to TarlDecision.
PolicyRule = Callable[[dict[str, Any]], TarlDecision]


class PolicyProtocol(Protocol):
    """Pluggable interface for a TARL policy evaluator."""

    name: str

    def evaluate(self, context: dict[str, Any]) -> TarlDecision: ...


class TarlPolicy:
    """Named TARL policy that wraps a rule function.

    Construction validates that the name is non-empty and that the rule
    is callable. Evaluation catches exceptions from the rule and wraps
    them in TarlError (fail-closed: no silent ALLOW on internal failure).
    """

    def __init__(self, name: str, rule: PolicyRule) -> None:
        if not isinstance(name, str) or not name.strip():
            raise TarlError("policy name must be a non-empty string")
        if not callable(rule):
            raise TarlError("rule must be callable")
        self.name = name
        self._rule = rule

    @property
    def rule(self) -> PolicyRule:
        return self._rule

    def evaluate(self, context: dict[str, Any]) -> TarlDecision:
        """Evaluate the policy against a context dict.

        Raises TarlError if context is not a dict or if the rule raises.
        """
        if not isinstance(context, dict):
            raise TarlError(f"context must be dict, got {type(context).__name__}")
        try:
            result = self._rule(context)
        except TarlError:
            raise
        except Exception as error:
            raise TarlError(
                f"policy {self.name!r} raised: {type(error).__name__}: {error}"
            ) from error
        if not isinstance(result, TarlDecision):
            raise TarlError(
                f"policy {self.name!r} returned non-TarlDecision: {type(result).__name__}"
            )
        return result


def allow_policy(name: str) -> TarlPolicy:
    """Build a policy that always returns ALLOW with a fixed reason.

    Useful as a default / fallback when no specific policy applies.
    """
    rule: PolicyRule = lambda _ctx: make_decision(  # noqa: E731
        verdict=TarlVerdict.ALLOW, reason="default-allow"
    )
    return TarlPolicy(name, rule)


def deny_policy(name: str, reason: str = "explicit-deny") -> TarlPolicy:
    """Build a policy that always returns DENY."""
    rule: PolicyRule = lambda _ctx: make_decision(  # noqa: E731
        verdict=TarlVerdict.DENY, reason=reason
    )
    return TarlPolicy(name, rule)


__all__ = [
    "PolicyProtocol",
    "PolicyRule",
    "TarlPolicy",
    "allow_policy",
    "deny_policy",
]
