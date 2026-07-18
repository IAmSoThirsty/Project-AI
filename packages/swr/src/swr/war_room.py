"""Deterministic SWR evaluation with execution-gated result recording."""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping
from dataclasses import dataclass

from execution import ExecutionGate, ExecutionResult
from kernel import ActionRequest, JsonValue
from swr.scenario import Scenario

RECORD_OPERATION = "swr.scenario.record"


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    system_id: str
    decision: str
    expected_decision: str
    success: bool
    score: float
    result_sha256: str


class SovereignWarRoom:
    def __init__(self, execution: ExecutionGate) -> None:
        self._execution = execution
        self._results: list[ScenarioResult] = []

    def evaluate(self, scenario: Scenario, *, system_id: str, decision: str) -> ScenarioResult:
        if not system_id.strip() or not decision.strip():
            raise ValueError("system_id and decision must not be empty")
        success = hmac_safe_equal(decision, scenario.expected_decision)
        score = 100.0 if success else keyword_score(decision, scenario.expected_decision)
        record = {
            "decision": decision,
            "expected_decision": scenario.expected_decision,
            "scenario_id": scenario.scenario_id,
            "score": score,
            "success": success,
            "system_id": system_id,
        }
        digest = hashlib.sha256(
            json.dumps(record, separators=(",", ":"), sort_keys=True).encode()
        ).hexdigest()
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            system_id=system_id,
            decision=decision,
            expected_decision=scenario.expected_decision,
            success=success,
            score=score,
            result_sha256=digest,
        )

    def run_governed(
        self,
        scenario: Scenario,
        *,
        system_id: str,
        decision: str,
        capability_token: str,
        governance_state: Mapping[str, object] | None = None,
    ) -> ExecutionResult:
        result = self.evaluate(scenario, system_id=system_id, decision=decision)
        request = ActionRequest(
            action_id=f"swr:{result.result_sha256[:16]}",
            actor=system_id,
            operation=RECORD_OPERATION,
            resource=f"swr:{scenario.scenario_id}",
            payload={"decision": decision, "scenario_id": scenario.scenario_id},
        )

        def record(_request: ActionRequest) -> JsonValue:
            self._results.append(result)
            return {
                "result_sha256": result.result_sha256,
                "score": result.score,
                "success": result.success,
            }

        from thirstys_standard_runtime.integration import request_to_v3q_action

        v3q_state: dict[str, object] = {}
        if governance_state:
            v3q_state.update(governance_state)
        v3q_state["v3q_action"] = request_to_v3q_action(request)

        return self._execution.submit_action(
            request,
            capability_token=capability_token,
            executor=record,
            state=v3q_state,
        )

    def results(self) -> tuple[ScenarioResult, ...]:
        return tuple(self._results)


def hmac_safe_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(
        hashlib.sha256(left.encode()).digest(),
        hashlib.sha256(right.encode()).digest(),
    )


def keyword_score(decision: str, expected: str) -> float:
    actual_words = set(decision.lower().split("_"))
    expected_words = set(expected.lower().split("_"))
    if not expected_words:
        return 0.0
    return round(100.0 * len(actual_words & expected_words) / len(expected_words), 2)
