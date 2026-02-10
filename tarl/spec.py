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
