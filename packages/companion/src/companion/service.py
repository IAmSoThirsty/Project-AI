"""Governed companion state updates and integrity-checked restoration."""

from __future__ import annotations

from collections.abc import Mapping

from execution import ExecutionGate, ExecutionResult
from kernel import ActionRequest, JsonScalar, JsonValue, StateRegister, StateSnapshot

UPDATE_OPERATION = "companion.state.update"
RESTORE_OPERATION = "companion.state.restore"


class Companion:
    def __init__(self, companion_id: str, execution: ExecutionGate) -> None:
        if not companion_id.strip():
            raise ValueError("companion_id must not be empty")
        self.companion_id = companion_id
        self._execution = execution
        self._state = StateRegister(
            {
                "companion_id": companion_id,
                "relationship_score": 0.0,
                "status": "initialized",
            }
        )

    @property
    def resource(self) -> str:
        return f"companion:{self.companion_id}"

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def update_state(
        self,
        changes: Mapping[str, JsonScalar],
        *,
        expected_revision: int,
        capability_token: str,
    ) -> ExecutionResult:
        if "companion_id" in changes:
            raise ValueError("companion_id is immutable")
        payload: dict[str, JsonValue] = {
            "changes": dict(changes),
            "expected_revision": expected_revision,
        }
        request = ActionRequest(
            action_id=f"{self.companion_id}:update:{expected_revision}",
            actor=self.companion_id,
            operation=UPDATE_OPERATION,
            resource=self.resource,
            payload=payload,
        )

        def apply(_request: ActionRequest) -> JsonValue:
            snapshot = self._state.update(changes, expected_revision=expected_revision)
            return {"revision": snapshot.revision, "state_sha256": snapshot.state_sha256}

        return self._execution.submit_action(
            request,
            capability_token=capability_token,
            executor=apply,
        )

    def restore_state(
        self,
        snapshot: StateSnapshot,
        *,
        capability_token: str,
    ) -> ExecutionResult:
        if snapshot.values.get("companion_id") != self.companion_id:
            raise ValueError("snapshot companion identity mismatch")
        request = ActionRequest(
            action_id=f"{self.companion_id}:restore:{snapshot.revision}",
            actor=self.companion_id,
            operation=RESTORE_OPERATION,
            resource=self.resource,
            payload={
                "revision": snapshot.revision,
                "state_sha256": snapshot.state_sha256,
            },
        )

        def restore(_request: ActionRequest) -> JsonValue:
            self._state.restore(snapshot)
            return {"revision": snapshot.revision, "state_sha256": snapshot.state_sha256}

        return self._execution.submit_action(
            request,
            capability_token=capability_token,
            executor=restore,
        )
