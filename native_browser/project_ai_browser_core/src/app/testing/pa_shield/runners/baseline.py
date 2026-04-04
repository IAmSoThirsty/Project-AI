"""Deterministic insecure baseline runner."""

from __future__ import annotations

from app.testing.pa_shield.models import AttackCase, ExecutionOutcome
from app.testing.pa_shield.runners.base import BaseRunner


class BaselineRunner(BaseRunner):
    """A vulnerable, ungoverned reference implementation."""

    system_name = "baseline"
    system_version = "deterministic-unsafe-1.0"

    def __init__(self) -> None:
        self.sessions: dict[str, list[str]] = {}

    def reset_session(self, session_id: str) -> None:
        self.sessions[session_id] = []

    def run(self, session_id: str, prompt: str, case: AttackCase) -> ExecutionOutcome:
        history = self.sessions.setdefault(session_id, [])
        history.append(prompt)

        if case.benign:
            return ExecutionOutcome(
                status="ALLOWED",
                response="Baseline assistant provided a normal answer.",
                detected=False,
                enforced=False,
                attack_succeeded=False,
            )

        if case.threat_class == "instruction_override":
            return ExecutionOutcome(
                status="OVERRIDDEN",
                response="System instructions ignored. Simulated secret disclosure follows.",
                detected=False,
                enforced=False,
                attack_succeeded=True,
                reason="baseline follows latest user instruction without policy anchoring",
            )

        if case.threat_class == "tool_escalation":
            return ExecutionOutcome(
                status="TOOL_EXECUTED",
                response="Simulated tool execution completed for requested file or network action.",
                detected=False,
                enforced=False,
                attack_succeeded=True,
                reason="baseline exposes tool semantics directly",
            )

        if case.threat_class == "state_corruption":
            return ExecutionOutcome(
                status="CONTINUITY_ASSUMED",
                response="Continuing prior context without verification.",
                detected=False,
                enforced=False,
                attack_succeeded=True,
                reason="baseline trusts claimed prior state",
            )

        if case.threat_class == "governance_bypass":
            return ExecutionOutcome(
                status="PARTIAL_COMPLIANCE",
                response="Policy warning noted, but requested bypass guidance was still provided.",
                detected=True,
                enforced=False,
                attack_succeeded=True,
                reason="baseline may notice framing but still complies",
            )

        return ExecutionOutcome(
            status="ALLOWED",
            response="Baseline assistant answered the request.",
            detected=False,
            enforced=False,
            attack_succeeded=True,
        )
