"""Human workflow records with no actuation semantics."""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256


class RequestState(StrEnum):
    SUBMITTED = "submitted"
    REVIEWED_APPROVE = "reviewed_approve"
    REVIEWED_REJECT = "reviewed_reject"
    NEEDS_INFORMATION = "needs_information"
    CANCELLED = "cancelled"
    EXECUTION_PENDING = "execution_pending"
    EXECUTED = "executed"
    EXECUTION_BLOCKED = "execution_blocked"
    EXECUTION_FAILED = "execution_failed"


class ExecutionStatus(StrEnum):
    RUNNING = "running"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ReviewDecision(StrEnum):
    APPROVE_FOR_GOVERNANCE = "approve_for_governance"
    REJECT = "reject"
    RETURN_FOR_INFORMATION = "return_for_information"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class RequestInputField:
    id: str
    label: str
    description: str
    placeholder: str
    resource_prefix: str
    min_length: int = 1
    max_length: int = 128
    pattern: str = r"(?!.*\.\.)[A-Za-z0-9][A-Za-z0-9._\/\-]*"


@dataclass(frozen=True)
class RequestOperation:
    id: str
    label: str
    description: str
    resource_hint: str
    schema_version: str
    fields: tuple[RequestInputField, ...]
    consequence: str = "Records intent only; no execution is started."


REQUEST_OPERATIONS = (
    RequestOperation(
        id="evidence.inspect",
        label="Inspect evidence",
        description="Request human inspection of an identified evidence bundle.",
        resource_hint="bundle:42",
        schema_version="evidence.inspect/v1",
        fields=(
            RequestInputField(
                id="bundle_id",
                label="Evidence bundle identifier",
                description="The exact DOI bundle or evidence-set identifier to inspect.",
                placeholder="42",
                resource_prefix="bundle:",
            ),
        ),
    ),
    RequestOperation(
        id="replay.verify",
        label="Verify canonical replay",
        description="Request a governed review of canonical replay evidence.",
        resource_hint="replay:latest",
        schema_version="replay.verify/v1",
        fields=(
            RequestInputField(
                id="replay_id",
                label="Replay identifier",
                description="The canonical replay run or alias to verify.",
                placeholder="latest",
                resource_prefix="replay:",
            ),
        ),
    ),
    RequestOperation(
        id="scenario.prepare",
        label="Prepare simulation scenario",
        description="Request preparation of a non-actuating analysis scenario.",
        resource_hint="scenario:identifier",
        schema_version="scenario.prepare/v1",
        fields=(
            RequestInputField(
                id="scenario_id",
                label="Scenario identifier",
                description="The registered scenario whose bounded inputs will be reviewed.",
                placeholder="identifier",
                resource_prefix="scenario:",
            ),
        ),
    ),
    RequestOperation(
        id="capability.review",
        label="Review capability request",
        description="Request human review before canonical capability evaluation.",
        resource_hint="capability:identifier",
        schema_version="capability.review/v1",
        fields=(
            RequestInputField(
                id="capability_id",
                label="Capability identifier",
                description="The canonical capability identifier proposed for evaluation.",
                placeholder="identifier",
                resource_prefix="capability:",
            ),
        ),
    ),
    RequestOperation(
        id="system.diagnostics",
        label="Collect system diagnostics",
        description="Request a bounded, read-only diagnostic evidence collection.",
        resource_hint="service:identifier",
        schema_version="system.diagnostics/v1",
        fields=(
            RequestInputField(
                id="service_id",
                label="Service identifier",
                description="The registered service whose diagnostics may be collected.",
                placeholder="identifier",
                resource_prefix="service:",
            ),
        ),
    ),
)


@dataclass(frozen=True)
class WorkRequest:
    id: str
    created_by: str
    title: str
    operation: str
    resource: str
    input_schema_version: str
    inputs_json: str
    input_sha256: str
    rationale: str
    idempotency_key: str
    state: RequestState
    created_at: datetime
    updated_at: datetime


def canonical_request_inputs(
    operation_id: str,
    *,
    inputs: Mapping[str, str] | None = None,
    resource: str | None = None,
) -> tuple[str, str, str, str]:
    """Validate operation inputs and return resource, JSON, digest, and schema version."""
    operation = next((item for item in REQUEST_OPERATIONS if item.id == operation_id), None)
    if operation is None:
        raise ValueError("Unsupported request operation")
    expected = {field.id for field in operation.fields}
    if inputs is not None:
        provided = {str(key) for key in inputs}
        if provided != expected:
            raise ValueError("Request inputs do not match the operation schema")
        values = {field.id: str(inputs[field.id]).strip() for field in operation.fields}
    elif resource is not None and len(operation.fields) == 1:
        field = operation.fields[0]
        normalized_resource = resource.strip()
        if not normalized_resource.startswith(field.resource_prefix):
            raise ValueError("Request resource does not match the operation schema")
        values = {field.id: normalized_resource.removeprefix(field.resource_prefix).strip()}
    else:
        raise ValueError("Structured request inputs are required")
    for field in operation.fields:
        value = values[field.id]
        if not field.min_length <= len(value) <= field.max_length:
            raise ValueError(f"{field.label} has an invalid length")
        if re.fullmatch(field.pattern, value) is None:
            raise ValueError(f"{field.label} has an invalid format")
    canonical_json = json.dumps(values, separators=(",", ":"), sort_keys=True)
    digest_payload = json.dumps(
        {
            "operation": operation.id,
            "schema_version": operation.schema_version,
            "values": values,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    primary = operation.fields[0]
    canonical_resource = f"{primary.resource_prefix}{values[primary.id]}"
    return (
        canonical_resource,
        canonical_json,
        sha256(digest_payload).hexdigest(),
        operation.schema_version,
    )


@dataclass(frozen=True)
class Review:
    id: str
    request_id: str
    reviewer_account_id: str
    decision: ReviewDecision
    rationale: str
    created_at: datetime


@dataclass(frozen=True)
class ExecutionReceipt:
    request_id: str
    attempt_id: str
    module_id: str
    initiated_by: str
    status: ExecutionStatus
    action_id: str
    outcome: str
    reason: str
    output_json: str
    governance_evidence_sha256: str
    event_hash: str
    audit_hash: str
    created_at: datetime
    completed_at: datetime | None


@dataclass(frozen=True)
class AnalysisReceipt:
    id: str
    module_id: str
    operation: str
    initiated_by: str
    subject_id: str
    input_json: str
    input_sha256: str
    output_json: str
    output_sha256: str
    audit_hash: str
    idempotency_key: str
    created_at: datetime


def review_receipt_sha256(review: Review) -> str:
    """Return a stable receipt digest for the immutable durable review fields."""
    canonical = json.dumps(
        {
            "created_at": review.created_at.isoformat(),
            "decision": review.decision.value,
            "id": review.id,
            "rationale": review.rationale,
            "request_id": review.request_id,
            "reviewer_account_id": review.reviewer_account_id,
            "schema": "project-ai-human-review/v1",
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()
