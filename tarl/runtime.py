from typing import List, Dict, Any
from .spec import TarlDecision, TarlVerdict
from .policy import TarlPolicy


class TarlRuntime:
    def __init__(self, policies: List[TarlPolicy]):
        self.policies = policies

    def evaluate(self, context: Dict[str, Any]) -> TarlDecision:
        for policy in self.policies:
            decision = policy.evaluate(context)
            if decision.is_terminal():
                return decision
        return TarlDecision(TarlVerdict.ALLOW, "All TARL policies satisfied")
