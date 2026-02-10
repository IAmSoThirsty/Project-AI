from collections.abc import Callable
from typing import Any

from .spec import TarlDecision


class TarlPolicy:
    def __init__(self, name: str, rule: Callable[[dict[str, Any]], TarlDecision]):
        self.name = name
        self.rule = rule

    def evaluate(self, context: dict[str, Any]) -> TarlDecision:
        return self.rule(context)
