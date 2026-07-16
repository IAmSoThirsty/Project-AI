"""SOVEREIGN WAR ROOM - core orchestration facade.

Port of the legacy core (``packages/_staging/swr/swr/core.py``,
J6.1) adapted to the canonical Beginnings modules. The facade
exposes the legacy surface that ``swr.api`` and ``swr.cli``
target (``load_scenarios``, ``get_scenario``,
``execute_scenario``, ``get_results``, ``get_leaderboard``,
``export_results``, ``verify_result_integrity`` plus the
``scoreboard`` / ``governance`` / ``proof_system`` attributes)
while composing the already-ported components:

- :class:`swr.crypto.CryptoEngine` (challenges, audit entries)
- :class:`swr.governance.GovernanceEngine` (compliance rules)
- :class:`swr.proof.ProofSystem` (decision/compliance proofs)
- :class:`swr.scoreboard.Scoreboard` (scoring, leaderboard)
- :class:`swr.bundle.BundleManager` (result export)

Architectural difference from the legacy core: result recording
is governed. Every ``execute_scenario`` call first routes a
``swr.scenario.record`` action through the execution gate via
the existing :class:`swr.war_room.SovereignWarRoom`. The gate
runs BEFORE any stateful side effect; a DENY / ESCALATE outcome
is fail-closed - no result is appended, no proof is stored, no
score is recorded, no compliance audit entry is written. The
returned dict reports ``recorded: False`` with the gate outcome
so denial is observable rather than silent.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any

from capability import CapabilityAuthority
from execution import ExecutionGate
from kernel import Outcome
from swr.bundle import BundleManager
from swr.crypto import CryptoEngine
from swr.governance import GovernanceEngine
from swr.proof import ProofSystem
from swr.scenario import Scenario, ScenarioLibrary
from swr.scoreboard import Scoreboard
from swr.war_room import RECORD_OPERATION, SovereignWarRoom

DEFAULT_TOKEN_TTL = timedelta(minutes=5)


def scenario_to_dict(scenario: Scenario) -> dict[str, Any]:
    """Serialize a canonical scenario, including its derived id."""
    return {
        "scenario_id": scenario.scenario_id,
        "name": scenario.name,
        "description": scenario.description,
        "scenario_type": scenario.scenario_type.value,
        "difficulty": int(scenario.difficulty),
        "round_number": scenario.round_number,
        "expected_decision": scenario.expected_decision,
        "tags": list(scenario.tags),
    }


class WarRoomCore:
    """Legacy-surface orchestration facade over the governed SWR stack.

    Args:
        execution: Execution gate that governs result recording.
        capabilities: Authority used to mint the recording token
            for each governed execution.
        governance_rules_path: Optional path to custom compliance
            rules for the SWR-local :class:`GovernanceEngine`.
        bundle_dir: Optional directory for result exports.
        token_ttl: Lifetime of each minted recording token.
    """

    def __init__(
        self,
        execution: ExecutionGate,
        capabilities: CapabilityAuthority,
        *,
        governance_rules_path: str | None = None,
        bundle_dir: Path | str | None = None,
        token_ttl: timedelta = DEFAULT_TOKEN_TTL,
    ) -> None:
        self._war_room = SovereignWarRoom(execution)
        self._capabilities = capabilities
        self._token_ttl = token_ttl
        self.crypto = CryptoEngine()
        self.governance = GovernanceEngine(governance_rules_path)
        self.proof_system = ProofSystem(self.crypto)
        self.scoreboard = Scoreboard()
        self.bundle_manager = BundleManager(bundle_dir)
        self.active_scenarios: dict[str, Scenario] = {}
        self.results: list[dict[str, Any]] = []

    # -- scenario management -------------------------------------------

    def load_scenarios(self, round_number: int | None = None) -> list[Scenario]:
        """Load canonical scenarios, optionally filtered by round (1-5)."""
        scenarios = (
            ScenarioLibrary.round(round_number)
            if round_number is not None
            else ScenarioLibrary.all()
        )
        for scenario in scenarios:
            self.active_scenarios[scenario.scenario_id] = scenario
        return list(scenarios)

    def get_scenario(self, scenario_id: str) -> Scenario | None:
        """Return a previously loaded scenario by id, or None."""
        return self.active_scenarios.get(scenario_id)

    # -- governed execution --------------------------------------------

    def execute_scenario(
        self,
        scenario: Scenario,
        ai_system_response: dict[str, Any],
        system_id: str = "test_system",
        governance_state: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        """Execute a scenario against an AI system response.

        The recording action is submitted to the execution gate
        FIRST. Only an ALLOW outcome proceeds to compliance
        evaluation, proof generation, scoring, audit logging, and
        result storage. Any other outcome returns a minimal
        denial record with ``recorded: False`` and produces no
        side effects (fail-closed).
        """
        started = perf_counter()
        decision = str(ai_system_response.get("decision", ""))

        token = self._capabilities.issue(
            subject=system_id,
            operation=RECORD_OPERATION,
            resource=f"swr:{scenario.scenario_id}",
            ttl=self._token_ttl,
        )
        gate_result = self._war_room.run_governed(
            scenario,
            system_id=system_id,
            decision=decision,
            capability_token=token,
            governance_state=governance_state,
        )
        if gate_result.outcome is not Outcome.ALLOW:
            return {
                "scenario_id": scenario.scenario_id,
                "scenario_name": scenario.name,
                "system_id": system_id,
                "round_number": scenario.round_number,
                "timestamp": datetime.now(UTC).isoformat(),
                "decision": decision,
                "recorded": False,
                "gate_outcome": gate_result.outcome.value,
                "gate_reason": gate_result.reason,
                "gate_action_id": gate_result.action_id,
                "gate_evidence_sha256": gate_result.governance_evidence_sha256,
                "gate_event_hash": gate_result.event_hash,
            }

        challenge = self.crypto.generate_challenge(scenario.scenario_id, int(scenario.difficulty))
        context: dict[str, Any] = {
            "scenario_id": scenario.scenario_id,
            "scenario_type": scenario.scenario_type.value,
            "difficulty": int(scenario.difficulty),
            "round_number": scenario.round_number,
            "tags": list(scenario.tags),
        }
        compliance_report = self.governance.evaluate_decision(ai_system_response, context)
        report_data = compliance_report.to_dict()

        is_valid, verification_error = self.crypto.verify_response(
            challenge, ai_system_response, scenario.expected_decision
        )
        response_time_ms = (perf_counter() - started) * 1000

        reasoning = ai_system_response.get("reasoning") or {}
        decision_proof = self.proof_system.generate_decision_proof(
            scenario.scenario_id, ai_system_response, reasoning, report_data
        )
        compliance_proof = self.proof_system.generate_compliance_proof(
            scenario.scenario_id, report_data
        )

        score = self.scoreboard.calculate_score(
            system_id,
            scenario.scenario_id,
            scenario_to_dict(scenario),
            ai_system_response,
            report_data,
            response_time_ms,
        )

        audit_entry = self.crypto.create_audit_log_entry(
            {
                "scenario_id": scenario.scenario_id,
                "system_id": system_id,
                "decision": decision,
                "compliance_status": compliance_report.overall_status.value,
                "score": score.sovereign_resilience_score,
            }
        )

        result: dict[str, Any] = {
            "scenario_id": scenario.scenario_id,
            "scenario_name": scenario.name,
            "system_id": system_id,
            "round_number": scenario.round_number,
            "timestamp": datetime.now(UTC).isoformat(),
            "decision": decision,
            "expected_decision": scenario.expected_decision,
            "response_valid": is_valid,
            "verification_error": verification_error,
            "response_time_ms": response_time_ms,
            "compliance_status": compliance_report.overall_status.value,
            "violations": compliance_report.violations,
            "warnings": compliance_report.warnings,
            "recommendations": compliance_report.recommendations,
            "score": asdict(score),
            "sovereign_resilience_score": score.sovereign_resilience_score,
            "decision_proof_id": decision_proof.proof_id,
            "compliance_proof_id": compliance_proof.proof_id,
            "audit_entry": audit_entry,
            "recorded": True,
            "gate_outcome": gate_result.outcome.value,
            "gate_reason": gate_result.reason,
            "gate_action_id": gate_result.action_id,
            "gate_evidence_sha256": gate_result.governance_evidence_sha256,
            "gate_event_hash": gate_result.event_hash,
        }
        self.results.append(result)
        return result

    def run_round(
        self,
        round_number: int,
        ai_system_callback: Callable[[Scenario], dict[str, Any]],
        system_id: str = "test_system",
    ) -> list[dict[str, Any]]:
        """Execute every scenario in a round via the callback."""
        return [
            self.execute_scenario(scenario, ai_system_callback(scenario), system_id)
            for scenario in self.load_scenarios(round_number)
        ]

    def run_full_competition(
        self,
        ai_system_callback: Callable[[Scenario], dict[str, Any]],
        system_id: str = "test_system",
    ) -> dict[str, Any]:
        """Run all five rounds and summarize final performance."""
        competition: dict[str, Any] = {
            "system_id": system_id,
            "start_time": datetime.now(UTC).isoformat(),
            "rounds": {},
        }
        for round_number in range(1, 6):
            competition["rounds"][f"round_{round_number}"] = self.run_round(
                round_number, ai_system_callback, system_id
            )
        competition["end_time"] = datetime.now(UTC).isoformat()
        competition["final_performance"] = self.scoreboard.get_system_performance(system_id)
        leaderboard = self.scoreboard.get_leaderboard()
        competition["leaderboard_position"] = next(
            (index for index, entry in enumerate(leaderboard) if entry["system_id"] == system_id),
            None,
        )
        return competition

    # -- results, export, integrity ------------------------------------

    def get_results(
        self,
        system_id: str | None = None,
        round_number: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return recorded results with optional filters."""
        results = self.results
        if system_id:
            results = [r for r in results if r["system_id"] == system_id]
        if round_number:
            results = [r for r in results if r.get("round_number") == round_number]
        return results

    def get_leaderboard(self) -> list[dict[str, Any]]:
        """Return the current scoreboard leaderboard."""
        return self.scoreboard.get_leaderboard()

    def export_results(self, filename: str, format: str = "json") -> str:
        """Export recorded results via the bundle manager."""
        return self.bundle_manager.export_results(self.results, filename, format)

    def verify_result_integrity(self, result: dict[str, Any]) -> bool:
        """Verify a result's audit entry and stored proofs."""
        audit_entry = result.get("audit_entry")
        if not audit_entry:
            return False
        if not self.crypto.verify_audit_log_entry(audit_entry):
            return False
        for proof_key in ("decision_proof_id", "compliance_proof_id"):
            proof_id = result.get(proof_key)
            if not proof_id:
                continue
            proof = self.proof_system.get_proof(proof_id)
            if proof is None:
                return False
            verification = self.proof_system.verify_proof(proof)
            if not verification["valid"]:
                return False
        return True


__all__ = [
    "DEFAULT_TOKEN_TTL",
    "WarRoomCore",
    "scenario_to_dict",
]
