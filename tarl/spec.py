from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class TarlVerdict(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class TarlDecision:
    verdict: TarlVerdict
    reason: str
    metadata: Optional[Dict[str, Any]] = None

    def is_terminal(self) -> bool:
        return self.verdict in (TarlVerdict.DENY, TarlVerdict.ESCALATE)
