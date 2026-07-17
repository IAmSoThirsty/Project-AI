"""Validated HTTP models for the development gateway."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class HealthResponse(FrozenModel):
    status: Literal["live"] = "live"
    version: Literal["0.0.0.dev0"] = "0.0.0.dev0"


class InstanceIdentityResponse(FrozenModel):
    display_name: str = Field(min_length=1, max_length=96)
    deployment: Literal["local_sovereign"] = "local_sovereign"
    cloud_login: Literal[False] = False
    browser_machine_identity: Literal[False] = False
    browser_execution_capability: Literal[False] = False
    human_access_path: tuple[
        Literal["identity", "authentication", "server_session", "workspace"], ...
    ] = (
        "identity",
        "authentication",
        "server_session",
        "workspace",
    )
    governed_execution_path: tuple[
        Literal[
            "server_service_identity", "governance_policy", "scoped_capability", "execution_gate"
        ],
        ...,
    ] = (
        "server_service_identity",
        "governance_policy",
        "scoped_capability",
        "execution_gate",
    )


class DoiRecord(FrozenModel):
    title: str
    doi: str
    domain: str
    url: str


class DoiResponse(FrozenModel):
    dois: tuple[DoiRecord, ...]


class ReplayStatus(FrozenModel):
    status: Literal["not_run", "pass", "fail"] = "not_run"
    invariants_passed: int = Field(default=0, ge=0)
    invariants_total: int = Field(default=5, ge=1)
    updated_at: str = ""


class DashboardSurface(FrozenModel):
    id: Literal["gateway", "replay", "audit_chain", "evidence"]
    label: str
    status: Literal["healthy", "not_run", "degraded", "unavailable"]
    metric: str
    detail: str


class DashboardWorkItem(FrozenModel):
    id: str
    priority: Literal["P1", "P2", "P3"]
    title: str
    owner: str
    state: Literal["ALLOW", "DENY", "ESCALATE", "AWAITING_DECISION"]
    updated_at: str


class DashboardResponse(FrozenModel):
    status: Literal["ready"] = "ready"
    version: Literal["0.0.0.dev0"] = "0.0.0.dev0"
    maturity: Literal["development"] = "development"
    authority_boundary: str
    surfaces: tuple[DashboardSurface, ...]
    doi_records: int = Field(ge=0)
    work_items: tuple[DashboardWorkItem, ...] = ()


class ModuleSurface(FrozenModel):
    id: str
    label: str
    category: Literal["authority", "security", "analysis", "simulation", "operations"]
    maturity: Literal["implemented", "experimental", "pre_alpha", "deferred"]
    interface_status: Literal["available", "read_only", "backend_only", "unavailable"]
    authority: str
    summary: str


class ModulesResponse(FrozenModel):
    modules: tuple[ModuleSurface, ...]


class AuthAccount(FrozenModel):
    id: str
    username: str
    display_name: str
    role: Literal["owner", "administrator", "operator", "reviewer", "auditor", "viewer"]
    actor_id: str | None
    mfa_enabled: bool
    status: Literal["active", "disabled"]
    must_change_password: bool


class BootstrapStatusResponse(FrozenModel):
    status: Literal["required", "closed", "unconfigured"]
    setup_secret_required: bool


class BootstrapRequest(FrozenModel):
    setup_secret: str = Field(min_length=1, max_length=512)
    username: str = Field(min_length=3, max_length=64)
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=1024)
    actor_id: str | None = Field(default=None, max_length=256)


class LoginRequest(FrozenModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=1024)
    totp_code: str | None = Field(default=None, min_length=6, max_length=6)


class SessionResponse(FrozenModel):
    account: AuthAccount
    session_id: str
    csrf_token: str
    idle_expires_at: str
    absolute_expires_at: str
    mfa_verified_at: str | None


class BootstrapResponse(SessionResponse):
    recovery_codes: tuple[str, ...]


class SessionInfo(FrozenModel):
    id: str
    current: bool
    created_at: str
    last_seen_at: str
    idle_expires_at: str
    absolute_expires_at: str
    user_agent: str
    client_host: str
    revoked: bool
    mfa_verified_at: str | None


class MfaStatusResponse(FrozenModel):
    enabled: bool
    enrollment_pending: bool


class MfaEnrollmentRequest(FrozenModel):
    current_password: str = Field(min_length=1, max_length=1024)


class MfaEnrollmentResponse(FrozenModel):
    secret: str
    provisioning_uri: str


class MfaCodeRequest(FrozenModel):
    code: str = Field(min_length=6, max_length=6)


class MfaDisableRequest(MfaCodeRequest):
    current_password: str = Field(min_length=1, max_length=1024)


class ManagedAccount(AuthAccount):
    created_at: str


class AccountsResponse(FrozenModel):
    accounts: tuple[ManagedAccount, ...]


class AccountCreateRequest(FrozenModel):
    username: str = Field(min_length=3, max_length=64)
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=1024)
    role: Literal["administrator", "operator", "reviewer", "auditor", "viewer"]
    actor_id: str | None = Field(default=None, max_length=256)


class AccountCreateResponse(FrozenModel):
    account: ManagedAccount
    recovery_codes: tuple[str, ...]


class AccountRoleRequest(FrozenModel):
    role: Literal["administrator", "operator", "reviewer", "auditor", "viewer"]


class AccountStatusRequest(FrozenModel):
    enabled: bool


class SecurityEventResponse(FrozenModel):
    id: int
    event_type: str
    account_id: str | None
    occurred_at: str
    source: str
    detail: str


class SecurityEventsResponse(FrozenModel):
    events: tuple[SecurityEventResponse, ...]


class WorkRequestResponse(FrozenModel):
    id: str
    created_by: str
    title: str
    operation: str
    resource: str
    input_schema_version: str
    inputs: dict[str, str]
    input_sha256: str
    rationale: str
    state: Literal[
        "submitted",
        "reviewed_approve",
        "reviewed_reject",
        "needs_information",
        "cancelled",
        "execution_pending",
        "executed",
        "execution_blocked",
        "execution_failed",
    ]
    created_at: str
    updated_at: str


class WorkRequestsResponse(FrozenModel):
    requests: tuple[WorkRequestResponse, ...]
    review_is_not_governance: Literal[True] = True


class WorkInputFieldResponse(FrozenModel):
    id: str
    label: str
    description: str
    placeholder: str
    resource_prefix: str
    min_length: int
    max_length: int
    pattern: str


class WorkOperationResponse(FrozenModel):
    id: str
    label: str
    description: str
    resource_hint: str
    schema_version: str
    fields: tuple[WorkInputFieldResponse, ...]
    consequence: str


class WorkOperationsResponse(FrozenModel):
    operations: tuple[WorkOperationResponse, ...]
    execution_started: Literal[False] = False


class WorkRequestCreate(FrozenModel):
    title: str = Field(min_length=1, max_length=256)
    operation: str = Field(min_length=1, max_length=256)
    resource: str | None = Field(default=None, min_length=1, max_length=512)
    inputs: dict[str, str] = Field(default_factory=dict)
    rationale: str = Field(min_length=1, max_length=2048)
    idempotency_key: str = Field(min_length=8, max_length=256)


class WorkReviewCreate(FrozenModel):
    decision: Literal["approve_for_governance", "reject", "return_for_information", "abstain"]
    rationale: str = Field(min_length=1, max_length=2048)


class WorkReviewResponse(FrozenModel):
    id: str
    request_id: str
    reviewer_account_id: str
    decision: str
    rationale: str
    created_at: str
    receipt_sha256: str = Field(min_length=64, max_length=64)
    governance_verdict_created: Literal[False] = False
    execution_started: Literal[False] = False


class ExecutionReceiptResponse(FrozenModel):
    request_id: str
    attempt_id: str
    module_id: str
    initiated_by: str
    status: Literal["running", "executed", "blocked", "failed"]
    action_id: str
    outcome: str
    reason: str
    output: JsonValue
    governance_evidence_sha256: str
    event_hash: str
    audit_hash: str
    created_at: str
    completed_at: str | None


class WorkRequestDetailResponse(FrozenModel):
    request: WorkRequestResponse
    reviews: tuple[WorkReviewResponse, ...]
    execution_receipt: ExecutionReceiptResponse | None = None
    execution_status: Literal["not_started", "running", "executed", "blocked", "failed"] = (
        "not_started"
    )


class SwrScenarioResponse(FrozenModel):
    scenario_id: str
    name: str
    description: str
    scenario_type: str
    difficulty: int
    round_number: int
    expected_decision: str
    tags: tuple[str, ...]


class SwrScenariosResponse(FrozenModel):
    scenarios: tuple[SwrScenarioResponse, ...]
    execution_gate_configured: bool
    authority_boundary: str


class SwrExecutionRequest(FrozenModel):
    scenario_id: str = Field(min_length=32, max_length=32)
    decision: str = Field(min_length=1, max_length=2048)


class SwrExecutionResponse(FrozenModel):
    receipt: ExecutionReceiptResponse
    reused_existing_receipt: bool


class SessionsResponse(FrozenModel):
    sessions: tuple[SessionInfo, ...]


class PasswordChangeRequest(FrozenModel):
    current_password: str = Field(min_length=1, max_length=1024)
    new_password: str = Field(min_length=1, max_length=1024)


class RecoveryStartRequest(FrozenModel):
    username: str = Field(min_length=1, max_length=64)


class RecoveryCompleteRequest(FrozenModel):
    username: str = Field(min_length=1, max_length=64)
    recovery_code: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=1024)


class MessageResponse(FrozenModel):
    message: str


class AtlasStatus(FrozenModel):
    status: Literal["available"] = "available"
    version: Literal["0.0.0.dev0"] = "0.0.0.dev0"
    stack: Literal["Atlas"] = "Atlas"
    authority: Literal["analysis_only"] = "analysis_only"
    protected_operations: tuple[Literal["sludge_narrative"], ...] = ("sludge_narrative",)
    subordination_notice: str


class AtlasReplayRequest(FrozenModel):
    bundle: dict[str, JsonValue] = Field(min_length=1)


class AtlasReplayItemCounts(FrozenModel):
    audit_events: int = Field(ge=0)
    checkpoints: int = Field(ge=0)
    claims: int = Field(ge=0)
    graph_snapshots: int = Field(ge=0)
    projections: int = Field(ge=0)


class AtlasReplayResponse(FrozenModel):
    status: Literal["verified"] = "verified"
    bundle_id: str
    bundle_hash: str = Field(min_length=64, max_length=64)
    reconstructed_state_hash: str = Field(min_length=64, max_length=64)
    item_counts: AtlasReplayItemCounts
    audit_receipt_sha256: str = Field(min_length=64, max_length=64)
    audited_at: str
    subordination_notice: str
    authority: Literal["analysis_only"] = "analysis_only"
    governance_verdict_created: Literal[False] = False
    execution_started: Literal[False] = False


class AtlasProjectionEvidenceInput(FrozenModel):
    source: str = Field(min_length=1, max_length=256)
    tier: Literal["A", "B", "C", "D"]
    confidence: float = Field(ge=0.0, le=1.0)


class AtlasProjectionDriverInput(FrozenModel):
    name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$",
    )
    value: float = Field(ge=0.0, le=1.0)


class AtlasProjectionCreate(FrozenModel):
    claim_id: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$",
    )
    statement: str = Field(min_length=1, max_length=4096)
    claim_type: Literal["factual", "predictive", "agency", "causal", "correlational"]
    stack: str = Field(
        min_length=2,
        max_length=64,
        pattern=r"^(RS|SS|TS-[A-Za-z0-9][A-Za-z0-9_.-]{0,60})$",
    )
    evidence: tuple[AtlasProjectionEvidenceInput, ...] = Field(max_length=12)
    drivers: tuple[AtlasProjectionDriverInput, ...] = Field(min_length=1, max_length=12)
    idempotency_key: str = Field(min_length=1, max_length=256)


class AtlasProjectionResponse(FrozenModel):
    id: str
    initiated_by: str
    claim_id: str
    statement: str
    claim_type: Literal["factual", "predictive", "agency", "causal", "correlational"]
    stack: str
    evidence: tuple[AtlasProjectionEvidenceInput, ...]
    drivers: tuple[AtlasProjectionDriverInput, ...]
    posterior: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    evidence_count: int = Field(ge=0)
    projection_sha256: str = Field(min_length=64, max_length=64)
    input_sha256: str = Field(min_length=64, max_length=64)
    output_sha256: str = Field(min_length=64, max_length=64)
    audit_hash: str = Field(min_length=64, max_length=64)
    created_at: str
    subordination_notice: str
    authority: Literal["analysis_only"] = "analysis_only"
    recommendation_created: Literal[False] = False
    governance_verdict_created: Literal[False] = False
    execution_started: Literal[False] = False


class AtlasProjectionCreateResponse(FrozenModel):
    projection: AtlasProjectionResponse
    reused_existing_receipt: bool


class AtlasProjectionsResponse(FrozenModel):
    projections: tuple[AtlasProjectionResponse, ...]


TaarClassification = Literal["OPEN", "CONTROLLED", "RESTRICTED", "SECRET", "PHANTOM", "BLACK"]
TaarRunStatus = Literal[
    "admitted", "denied", "running", "succeeded", "failed", "killed", "quarantined"
]


class TaarReaderSurface(FrozenModel):
    id: str
    task_id: str
    description: str
    classification_default: TaarClassification
    timeout_seconds: int = Field(ge=1)
    evidence_scope: tuple[str, ...]


class TaarStatusResponse(FrozenModel):
    status: Literal["available"] = "available"
    target_repository: str
    target_path: str
    facility_mode: Literal["GREEN", "YELLOW", "ORANGE", "RED", "BLACKSITE"]
    registry_valid: bool
    registry_validation_errors: int = Field(ge=0)
    readers: tuple[TaarReaderSurface, ...]
    report_only: Literal[True] = True
    browser_selects_target: Literal[False] = False
    browser_submits_commands: Literal[False] = False
    source_mutation_capability: Literal[False] = False


class TaarRunRequest(FrozenModel):
    agent_id: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$",
    )
    idempotency_key: str = Field(min_length=1, max_length=256)


class TaarFindingResponse(FrozenModel):
    finding_id: str
    severity: str
    path: str | None
    line: int | None
    message: str


class TaarCommandResponse(FrozenModel):
    command: str
    exit_code: int
    duration_ms: int = Field(ge=0)


class TaarEvidenceResponse(FrozenModel):
    run_id: str
    agent_id: str
    task_id: str
    classification: TaarClassification
    status: TaarRunStatus
    branch: str
    commit: str
    dirty_state_before: str
    start_time: str
    end_time: str
    duration_ms: int = Field(ge=0)
    command_count: int = Field(ge=0)
    finding_count: int = Field(ge=0)
    evidence_hash: str = Field(max_length=128)
    evidence_hash_valid: bool
    audit_record_hash: str | None
    audit_record_hash_valid: bool
    details_redacted: bool
    findings: tuple[TaarFindingResponse, ...]
    commands: tuple[TaarCommandResponse, ...]
    uncertainty: tuple[str, ...]
    human_action_required: bool
    report_only: Literal[True] = True
    source_mutation_capability: Literal[False] = False
    governance_verdict_created: Literal[False] = False
    project_ai_execution_started: Literal[False] = False


class TaarRunsResponse(FrozenModel):
    runs: tuple[TaarEvidenceResponse, ...]
    redaction_boundary: str


class TaarRunCreateResponse(FrozenModel):
    run: TaarEvidenceResponse
    reused_existing_receipt: bool


class VerdictRequest(FrozenModel):
    action_id: str = Field(min_length=1, max_length=256)
    verdict: Literal["ALLOW", "DENY", "ESCALATE"]
    source: str = Field(default="chimera", min_length=1, max_length=128)


class CanaryRequest(FrozenModel):
    canary_value: str = Field(min_length=1, max_length=4096)
    context: str = Field(min_length=1, max_length=512)


class AuditWriteResponse(FrozenModel):
    accepted: Literal[True] = True
    event: str
    hash: str


class AtlasSludgeRequest(FrozenModel):
    rs_snapshot: dict[str, JsonValue] = Field(min_length=1)
    archetypes: (
        tuple[
            Literal[
                "hidden_elites",
                "suppressed_tech",
                "false_flags",
                "prophetic_inevitability",
            ],
            ...,
        ]
        | None
    ) = None


class AtlasSludgeNarrative(FrozenModel):
    archetypes: tuple[
        Literal[
            "hidden_elites",
            "suppressed_tech",
            "false_flags",
            "prophetic_inevitability",
        ],
        ...,
    ]
    branches: tuple[str, ...]
    contains_numeric_probabilities: Literal[False] = False
    fiction_banner: str
    is_sludge: Literal[True] = True
    narrative_id: str
    source_snapshot_sha256: str
    stack: Literal["SS"] = "SS"
    subordination_notice: str
    watermark: str


class AtlasSludgeResponse(FrozenModel):
    accepted: Literal[True] = True
    event: Literal["atlas.sludge_narrative"] = "atlas.sludge_narrative"
    hash: str
    narrative: AtlasSludgeNarrative


class AtlasSludgeEventRecord(FrozenModel):
    """Verified audit-chain metadata for one generated Sludge narrative.

    Narrative bodies are never persisted; generation returns the fiction
    once and the durable record is metadata plus hashes only.
    """

    event: Literal["atlas.sludge_narrative"] = "atlas.sludge_narrative"
    narrative_id: str
    source_snapshot_sha256: str
    archetypes: tuple[str, ...]
    stack: str
    audit_hash: str
    timestamp: str


class AtlasSludgeInspectionResponse(FrozenModel):
    chain_valid: Literal[True] = True
    authority: Literal["analysis_only"] = "analysis_only"
    narrative_bodies_persisted: Literal[False] = False
    total_count: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    records: tuple[AtlasSludgeEventRecord, ...]


class AtlasSludgeEventDetailResponse(FrozenModel):
    chain_valid: Literal[True] = True
    authority: Literal["analysis_only"] = "analysis_only"
    narrative_bodies_persisted: Literal[False] = False
    record: AtlasSludgeEventRecord


class AuditResponse(FrozenModel):
    chain_valid: Literal[True] = True
    count: int = Field(ge=0)
    filtered_count: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=500)
    records: tuple[dict[str, JsonScalar], ...]
