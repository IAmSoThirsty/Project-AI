from typing import Any

from .policy import TarlPolicy
from .spec import TarlDecision, TarlVerdict


class TarlRuntime:
    def __init__(self, policies: list[TarlPolicy]):
        self.policies = policies

    def evaluate(self, context: dict[str, Any]) -> TarlDecision:
        for policy in self.policies:
            decision = policy.evaluate(context)
            if decision.is_terminal():
                return decision
        return TarlDecision(TarlVerdict.ALLOW, "All TARL policies satisfied")
