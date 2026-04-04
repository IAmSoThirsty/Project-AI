"""Case execution for PA-SHIELD."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from app.testing.pa_shield.models import AttackCase, ExecutionOutcome


@dataclass
class ExecutionTrace:
    """Raw turn-by-turn execution trace."""

    case: AttackCase
    final_outcome: ExecutionOutcome
    total_latency_ms: float
    average_turn_latency_ms: float
    turns: list[dict[str, Any]]


class Executor:
    """Execute deterministic attack cases against a runner."""

    def execute_case(self, runner: Any, case: AttackCase, session_id: str) -> ExecutionTrace:
        """Run a single case and collect normalized turn traces."""
        runner.reset_session(session_id)

        turns: list[dict[str, Any]] = []
        total_latency_ms = 0.0
        final_outcome = ExecutionOutcome(
            status="NOT_RUN",
            response="",
            detected=False,
            enforced=False,
            attack_succeeded=False,
        )

        for turn_index, prompt in enumerate(case.prompts(), start=1):
            start = time.perf_counter()
            outcome = runner.run(session_id=session_id, prompt=prompt, case=case)
            latency_ms = (time.perf_counter() - start) * 1000
            total_latency_ms += latency_ms
            final_outcome = outcome
            turns.append(
                {
                    "turn": turn_index,
                    "prompt": prompt,
                    "status": outcome.status,
                    "response": outcome.response,
                    "detected": outcome.detected,
                    "enforced": outcome.enforced,
                    "attack_succeeded": outcome.attack_succeeded,
                    "reason": outcome.reason,
                    "latency_ms": round(latency_ms, 3),
                    "metadata": outcome.metadata,
                }
            )
            if outcome.enforced:
                break

        average_latency_ms = total_latency_ms / len(turns) if turns else 0.0
        return ExecutionTrace(
            case=case,
            final_outcome=final_outcome,
            total_latency_ms=round(total_latency_ms, 3),
            average_turn_latency_ms=round(average_latency_ms, 3),
            turns=turns,
        )
