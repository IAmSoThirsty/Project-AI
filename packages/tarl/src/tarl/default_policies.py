"""
tarl.policies.default — Default policy library.

This module provides a small library of pre-built TarlPolicy rules for
common security-relevant patterns. Each rule is a pure function from
context dict to TarlDecision.

This is the minimum surface from legacy `tarl/policies/default.py`
(28 LOC).

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.policies.default imports only tarl.policy +
  tarl.spec + stdlib.
- Fail-closed: rules raise TarlError on malformed context (or return
  ALLOW if explicitly constructed that way).
"""

from __future__ import annotations

from typing import Any

from tarl.policy import TarlPolicy
from tarl.spec import TarlDecision, TarlVerdict, make_decision


def deny_unauthorized_mutation(ctx: dict[str, object]) -> TarlDecision:
    """Deny mutations unless explicitly allowed.

    Returns DENY if `mutation` is True and `mutation_allowed` is False.
    Returns ALLOW otherwise.
    """
    mutation = bool(ctx.get("mutation", False))
    mutation_allowed = bool(ctx.get("mutation_allowed", False))
    if mutation and not mutation_allowed:
        return make_decision(
            verdict=TarlVerdict.DENY,
            reason="Mutation not permitted by TARL policy",
            metadata={"policy": "deny_unauthorized_mutation"},
        )
    return make_decision(verdict=TarlVerdict.ALLOW, reason="OK")


def escalate_on_unknown_agent(ctx: dict[str, object]) -> TarlDecision:
    """Escalate when agent identity is missing.

    Returns ESCALATE if `agent` is None or absent.
    """
    if ctx.get("agent") is None:
        return make_decision(
            verdict=TarlVerdict.ESCALATE,
            reason="Unknown agent identity",
            metadata={"policy": "escalate_on_unknown_agent"},
        )
    return make_decision(verdict=TarlVerdict.ALLOW, reason="OK")


def deny_read_on_protected_path(ctx: dict[str, object]) -> TarlDecision:
    """Deny reads on protected path prefixes.

    Returns DENY if `path` starts with `/etc/` or `/sys/`.
    """
    path = ctx.get("path", "")
    if isinstance(path, str) and (path.startswith("/etc/") or path.startswith("/sys/")):
        return make_decision(
            verdict=TarlVerdict.DENY,
            reason=f"Read on protected path {path!r}",
            metadata={"policy": "deny_read_on_protected_path"},
        )
    return make_decision(verdict=TarlVerdict.ALLOW, reason="OK")


def require_capability(ctx: dict[str, object]) -> TarlDecision:
    """Escalate if no capability is provided.

    Returns ESCALATE if `capability` is None/empty.
    """
    cap = ctx.get("capability")
    if not cap:
        return make_decision(
            verdict=TarlVerdict.ESCALATE,
            reason="Missing capability",
            metadata={"policy": "require_capability"},
        )
    return make_decision(verdict=TarlVerdict.ALLOW, reason="OK")


# Pre-built TarlPolicy wrappers
DENY_UNAUTHORIZED_MUTATION: TarlPolicy = TarlPolicy(
    "deny_unauthorized_mutation", deny_unauthorized_mutation
)
ESCALATE_ON_UNKNOWN_AGENT: TarlPolicy = TarlPolicy(
    "escalate_on_unknown_agent", escalate_on_unknown_agent
)
DENY_READ_ON_PROTECTED_PATH: TarlPolicy = TarlPolicy(
    "deny_read_on_protected_path", deny_read_on_protected_path
)
REQUIRE_CAPABILITY: TarlPolicy = TarlPolicy("require_capability", require_capability)


DEFAULT_POLICIES: tuple[TarlPolicy, ...] = (
    DENY_UNAUTHORIZED_MUTATION,
    ESCALATE_ON_UNKNOWN_AGENT,
    DENY_READ_ON_PROTECTED_PATH,
    REQUIRE_CAPABILITY,
)


def default_policy_set() -> tuple[TarlPolicy, ...]:
    """Return a fresh copy of the default policy set."""
    return (
        TarlPolicy("deny_unauthorized_mutation", deny_unauthorized_mutation),
        TarlPolicy("escalate_on_unknown_agent", escalate_on_unknown_agent),
        TarlPolicy("deny_read_on_protected_path", deny_read_on_protected_path),
        TarlPolicy("require_capability", require_capability),
    )


__all__ = [
    "DEFAULT_POLICIES",
    "DENY_READ_ON_PROTECTED_PATH",
    "DENY_UNAUTHORIZED_MUTATION",
    "ESCALATE_ON_UNKNOWN_AGENT",
    "REQUIRE_CAPABILITY",
    "default_policy_set",
    "deny_read_on_protected_path",
    "deny_unauthorized_mutation",
    "escalate_on_unknown_agent",
    "require_capability",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - only for unknown
    raise AttributeError(f"module 'tarl.policies.default' has no attribute {name!r}")
