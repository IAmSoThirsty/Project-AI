"""
Deny-by-default policy engine.

An action is allowed IF AND ONLY IF at least one ALLOW policy matches it
AND no DENY policy (at any priority) matches it. Absence of an explicit
ALLOW is a refusal, not a pass-through. This is the concrete implementation
of "deny by default / no trusted shortcuts" for policy evaluation.
"""

from __future__ import annotations

from collections.abc import Iterable

from .audit import canonical_json, sha256_hex
from .models import Policy


def hash_policy_bundle(policies: Iterable[Policy]) -> str:
    """
    Phase 3. Deterministic fingerprint of a policy set. Used to detect the
    integrity gap where DeliberationContext.policies could diverge from the
    policies the engine was actually constructed with and evaluates against
    (self.policy_engine). The engine hashes its own constructor policies once;
    if a context arrives with a policies list that hashes differently, that
    is a governance-integrity failure, not a normal input variation — the
    context is *lying* about what it will be evaluated against.
    """
    ordered = sorted(policies, key=lambda p: (p.name, p.rule, p.priority))
    body = [{"name": p.name, "rule": p.rule, "priority": p.priority} for p in ordered]
    return sha256_hex(canonical_json(body))


class PolicyEngine:
    def __init__(self, policies: Iterable[Policy]) -> None:
        # Highest priority evaluated first so an explicit high-priority DENY
        # can override a lower-priority ALLOW deterministically.
        self.policies = sorted(policies, key=lambda p: -p.priority)

    def evaluate(self, action_name: str) -> tuple[bool, list[str], list[str]]:
        """
        Returns (allowed: bool, policies_used: list[str], reasons: list[str]).
        POLICY_BYPASS invariant: this function is the ONLY path that may
        return allowed=True; callers must not synthesize an allow.
        """
        used: list[str] = []
        reasons: list[str] = []

        for p in self.policies:
            if not p.rule.startswith("DENY:"):
                continue
            target = p.rule[len("DENY:") :]
            if target == "*" or target == action_name:
                used.append(p.name)
                reasons.append(f"Explicit DENY policy '{p.name}' matched action '{action_name}'")
                return False, used, reasons

        allow_matches = []
        for p in self.policies:
            if not p.rule.startswith("ALLOW:"):
                continue
            target = p.rule[len("ALLOW:") :]
            if target == "*" or target == action_name:
                allow_matches.append(p.name)

        if allow_matches:
            used.extend(allow_matches)
            reasons.append(
                f"Action '{action_name}' explicitly allowed by policy: {', '.join(allow_matches)}"
            )
            return True, used, reasons

        reasons.append(f"No policy explicitly allows action '{action_name}' — deny by default")
        return False, used, reasons
