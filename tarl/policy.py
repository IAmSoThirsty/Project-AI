from typing import Callable, Dict, Any
from .spec import TarlDecision


class TarlPolicy:
    def __init__(self, name: str, rule: Callable[[Dict[str, Any]], TarlDecision]):
        self.name = name
        self.rule = rule

    def evaluate(self, context: Dict[str, Any]) -> TarlDecision:
        return self.rule(context)
