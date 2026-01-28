from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class EscalationLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EscalationEvent:
    level: EscalationLevel
    reason: str
    context: Dict[str, Any]


class CodexDeus:
    def escalate(self, event: EscalationEvent):
        if event.level == EscalationLevel.HIGH:
            raise SystemExit(f"CRITICAL ESCALATION: {event.reason}")
        return event
