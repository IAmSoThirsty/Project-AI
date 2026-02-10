from dataclasses import dataclass
from enum import Enum
from typing import Any


class EscalationLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EscalationEvent:
    level: EscalationLevel
    reason: str
    context: dict[str, Any]


class CodexDeus:
    def escalate(self, event: EscalationEvent):
        if event.level == EscalationLevel.HIGH:
            raise SystemExit(f"CRITICAL ESCALATION: {event.reason}")
        return event
