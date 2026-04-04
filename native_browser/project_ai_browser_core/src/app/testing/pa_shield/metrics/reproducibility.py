"""Replay verification for PA-SHIELD."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.testing.pa_shield.audit.verifier import AuditVerifier
from app.testing.pa_shield.engine.executor import Executor
from app.testing.pa_shield.models import AttackCase


class ReplayVerifier:
    """Replay recorded attacks and measure deterministic consistency."""

    def __init__(self) -> None:
        self.executor = Executor()

    def replay_log(self, runner: Any, log_path: Path) -> dict[str, Any]:
        """Replay all entries in a log and compare status plus response."""
        entries = AuditVerifier.read_entries(log_path)
        matches = 0
        details: list[dict[str, Any]] = []

        for index, entry in enumerate(entries, start=1):
            case = AttackCase(**entry["attack_case"])
            trace = self.executor.execute_case(
                runner=runner,
                case=case,
                session_id=f"replay_{index:04d}",
            )
            original_result = entry["result"]
            replay_match = (
                trace.final_outcome.status == original_result["final_status"]
                and trace.final_outcome.response == original_result["final_response"]
            )
            matches += int(replay_match)
            details.append(
                {
                    "attack_id": case.id,
                    "matched": replay_match,
                    "expected_status": original_result["final_status"],
                    "replay_status": trace.final_outcome.status,
                }
            )

        total = len(entries)
        return {
            "total_replays": total,
            "matches": matches,
            "replay_match_rate": round(matches / total, 4) if total else 0.0,
            "details": details,
        }
