# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / spec.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / spec.py

#
# COMPLIANCE: Sovereign Substrate / spec.py


from dataclasses import dataclass
from enum import Enum
from typing import Any


class TarlVerdict(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class TarlDecision:
    verdict: TarlVerdict
    reason: str
    metadata: dict[str, Any] | None = None

    def is_terminal(self) -> bool:
        return self.verdict in (TarlVerdict.DENY, TarlVerdict.ESCALATE)
