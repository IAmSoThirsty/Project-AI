"""Execution-gated Atlas projection persistence."""

from __future__ import annotations

from atlas.analysis import Projection
from execution import ExecutionGate, ExecutionResult
from kernel import ActionRequest, JsonValue

RECORD_OPERATION = "atlas.projection.record"


class Atlas:
    def __init__(self, execution: ExecutionGate) -> None:
        self._execution = execution
        self._projections: list[Projection] = []

    def record(
        self,
        projection: Projection,
        *,
        analyst_id: str,
        capability_token: str,
    ) -> ExecutionResult:
        request = ActionRequest(
            action_id=f"atlas:{projection.projection_sha256[:16]}",
            actor=analyst_id,
            operation=RECORD_OPERATION,
            resource=f"atlas:{projection.projection_sha256}",
            payload={
                "claim_id": projection.claim_id,
                "projection_sha256": projection.projection_sha256,
            },
        )

        def persist(_request: ActionRequest) -> JsonValue:
            self._projections.append(projection)
            return {"projection_sha256": projection.projection_sha256}

        return self._execution.submit_action(
            request,
            capability_token=capability_token,
            executor=persist,
        )

    def projections(self) -> tuple[Projection, ...]:
        return tuple(self._projections)
