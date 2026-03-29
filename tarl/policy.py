# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / policy.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / policy.py

#
# COMPLIANCE: Sovereign Substrate / policy.py


from collections.abc import Callable
from typing import Any

from .spec import TarlDecision


class TarlPolicy:
    def __init__(self, name: str, rule: Callable[[dict[str, Any]], TarlDecision]):
        self.name = name
        self.rule = rule

    def evaluate(self, context: dict[str, Any]) -> TarlDecision:
        return self.rule(context)
