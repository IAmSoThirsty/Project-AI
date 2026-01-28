from tarl.spec import TarlVerdict
from src.cognition.codex.escalation import CodexDeus, EscalationEvent, EscalationLevel


class TarlCodexBridge:
    def __init__(self, codex: CodexDeus):
        self.codex = codex

    def handle(self, decision, context):
        if decision.verdict == TarlVerdict.ESCALATE:
            return self.codex.escalate(
                EscalationEvent(
                    level=EscalationLevel.HIGH,
                    reason=decision.reason,
                    context=context,
                )
            )
