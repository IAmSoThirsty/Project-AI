# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / tarl_codex_bridge.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / tarl_codex_bridge.py

#
# COMPLIANCE: Sovereign Substrate / tarl_codex_bridge.py


from src.cognition.codex.escalation import CodexDeus, EscalationEvent, EscalationLevel
from tarl.spec import TarlVerdict


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
