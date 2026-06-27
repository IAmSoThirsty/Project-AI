"""Execution-gated Atlas projection persistence."""

from __future__ import annotations

from atlas.analysis import Projection
from atlas.audit import AuditCategory, AuditLevel, AuditTrail
from execution import ExecutionGate, ExecutionResult
from kernel import ActionRequest, JsonValue

RECORD_OPERATION = "atlas.projection.record"


class Atlas:
    def __init__(
        self,
        execution: ExecutionGate,
        audit_trail: AuditTrail | None = None,
    ) -> None:
        self._execution = execution
        self._projections: list[Projection] = []
        # Audit trail is OPTIONAL. If provided, every decision is recorded
        # with full rationale. This implements the "explanation chain" — the
        # system can answer "why was reality allowed to continue?" by
        # replaying the audit trail.
        self._audit_trail = audit_trail

    def attach_audit_trail(self, audit_trail: AuditTrail) -> None:
        """Attach an audit trail. Idempotent — replaces existing trail."""
        if not isinstance(audit_trail, AuditTrail):
            raise TypeError(f"audit_trail must be AuditTrail, got {type(audit_trail).__name__}")
        self._audit_trail = audit_trail

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

        result = self._execution.submit_action(
            request,
            capability_token=capability_token,
            executor=persist,
        )

        # Emit audit event if trail is attached. This records WHY reality
        # was allowed (or denied) to continue.
        if self._audit_trail is not None:
            self._emit_audit_event(analyst_id, projection, result)

        return result

    def _emit_audit_event(
        self,
        analyst_id: str,
        projection: Projection,
        result: ExecutionResult,
    ) -> None:
        """Emit an audit event for a record() decision.

        The rationale includes the decision outcome and supporting context.
        Level is HIGH_PRIORITY for denials, STANDARD otherwise.
        """
        # ExecutionResult is intentionally not imported directly here; we
        # access .outcome.value dynamically to avoid circular imports.
        outcome_str = str(getattr(result.outcome, "value", result.outcome))
        is_deny = outcome_str.upper() == "DENY"

        # Build rationale based on outcome
        if is_deny:
            rationale = (
                f"record() denied for analyst_id={analyst_id!r}: "
                f"{getattr(result, 'reason', '') or 'unspecified reason'}"
            )
            level = AuditLevel.HIGH_PRIORITY
        else:
            rationale = (
                f"record() allowed for analyst_id={analyst_id!r}: "
                "capability token valid + governance rule passed"
            )
            level = AuditLevel.STANDARD

        # Emit the event (this will fail-closed on invalid inputs)
        self._audit_trail.append(  # type: ignore[union-attr]
            level=level,
            category=AuditCategory.OPERATION,
            actor=analyst_id,
            action=RECORD_OPERATION,
            resource=f"atlas:{projection.projection_sha256}",
            outcome=outcome_str,
            rationale=rationale,
            evidence={
                "claim_id": projection.claim_id,
                "projection_sha256": projection.projection_sha256,
                "posterior": str(projection.posterior),
            },
        )

    def projections(self) -> tuple[Projection, ...]:
        return tuple(self._projections)
