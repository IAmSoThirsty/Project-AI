"""Fail-closed Project-AI HTTP gateway."""

from __future__ import annotations

import hmac
import json
import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Annotated, Literal, cast

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from kernel.version import PROJECT_AI_VERSION
from project_ai_waterfall.transport import WaterfallRuntime
from taar.errors import TaarError
from waterfall_adapter import WaterfallAdapter

from accounts import (
    AccountRepository,
    AccountService,
    AccountServiceError,
    InterfacePermission,
    InvalidMachineCredential,
    PermissionDenied,
    PostgresAccountRepository,
)
from atlas import SUBORDINATION_NOTICE, NarrativeArchetype, SludgeSandboxError, get_sludge_sandbox
from project_ai_api.atlas_workflows import install_atlas_workflow_routes
from project_ai_api.auth import SESSION_COOKIE_SCHEME, install_auth_routes
from project_ai_api.metrics import install_metrics
from project_ai_api.models import (
    AtlasSludgeEventDetailResponse,
    AtlasSludgeEventRecord,
    AtlasSludgeInspectionResponse,
    AtlasSludgeNarrative,
    AtlasSludgeRequest,
    AtlasSludgeResponse,
    AtlasStatus,
    AuditResponse,
    AuditWriteResponse,
    CanaryRequest,
    DashboardResponse,
    DashboardSurface,
    DoiRecord,
    DoiResponse,
    HealthResponse,
    InstanceIdentityResponse,
    JsonScalar,
    ModulesResponse,
    ModuleSurface,
    ReplayStatus,
    VerdictRequest,
)
from project_ai_api.registry import load_doi_registry
from project_ai_api.screening import (
    DEFAULT_QUARANTINE_DIR,
    CerberusScreen,
    ScreeningBlockResponse,
)
from project_ai_api.swr_workflows import build_swr_runtime, install_swr_workflow_routes
from project_ai_api.taar_workflows import TaarInspectionService, install_taar_workflow_routes
from project_ai_api.waterfall_workflows import (
    build_waterfall_integration,
    install_waterfall_routes,
)
from project_ai_api.workflows import install_workflow_routes
from security import AppendOnlyAuditRelay, receive_canary_hit, receive_verdict
from swr import WarRoomCore
from workflows import PostgresWorkflowRepository, WorkflowRepository, WorkflowService

type AuditRecord = dict[str, JsonScalar]

# Declared at module scope so deferred annotations resolve and every
# machine-token route advertises the same OpenAPI security scheme;
# auto_error=False keeps the guards' own 503/401 semantics.
MACHINE_BEARER_SCHEME = HTTPBearer(
    scheme_name="machineBearer",
    description=(
        "Per-program machine credential; development may use the bootstrap "
        "PROJECT_AI_API_TOKEN until credentials are provisioned."
    ),
    auto_error=False,
)


def _optional_path(value: str | None) -> Path | None:
    return Path(value).expanduser() if value and value.strip() else None


def _secret_value(explicit: str | None, environment: str) -> str | None:
    """Resolve a secret from an argument, environment value, or mounted file."""
    if explicit is not None:
        return explicit
    direct_value = os.getenv(environment)
    file_path = os.getenv(f"{environment}_FILE")
    if direct_value is not None and file_path is not None:
        raise ValueError(f"{environment} and {environment}_FILE must not both be set")
    if file_path is None:
        return direct_value
    try:
        file_value = Path(file_path).read_text(encoding="utf-8").strip()
    except OSError as error:
        raise ValueError(f"Unable to read {environment}_FILE") from error
    if not file_value:
        raise ValueError(f"{environment}_FILE must not be empty")
    return file_value


def _default_registry_path() -> Path | None:
    configured = _optional_path(os.getenv("PROJECT_AI_DOI_REGISTRY"))
    if configured is not None:
        return configured
    candidate = Path.cwd() / "docs" / "reference" / "DOI_REGISTRY.md"
    return candidate if candidate.is_file() else None


def _audit_records(
    relay: AppendOnlyAuditRelay,
    limit: int,
    offset: int = 0,
    query: str | None = None,
    event: str | None = None,
) -> AuditResponse:
    try:
        valid, count = relay.verify()
    except (OSError, ValueError):
        valid, count = False, 0
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit hash chain verification failed",
        )
    if not relay.path.exists():
        return AuditResponse(count=0, filtered_count=0, offset=offset, limit=limit, records=())
    lines = [line for line in relay.path.read_text(encoding="utf-8").splitlines() if line]
    records = [cast(AuditRecord, json.loads(line)) for line in lines]
    normalized_query = query.strip().casefold() if query else ""
    normalized_event = event.strip().casefold() if event else ""
    filtered = [
        record
        for record in records
        if (not normalized_event or str(record.get("event", "")).casefold() == normalized_event)
        and (
            not normalized_query
            or normalized_query in json.dumps(record, sort_keys=True).casefold()
        )
    ]
    page = tuple(reversed(filtered))[offset : offset + limit]
    return AuditResponse(
        count=count,
        filtered_count=len(filtered),
        offset=offset,
        limit=limit,
        records=page,
    )


def _sludge_event_records(relay: AppendOnlyAuditRelay) -> tuple[AtlasSludgeEventRecord, ...]:
    """Load verified Sludge generation metadata from the audit chain (fail-closed)."""
    try:
        valid, _count = relay.verify()
    except (OSError, ValueError):
        valid = False
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit hash chain verification failed",
        )
    if not relay.path.exists():
        return ()
    records: list[AtlasSludgeEventRecord] = []
    for line in relay.path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        raw = cast(AuditRecord, json.loads(line))
        if raw.get("event") != "atlas.sludge_narrative":
            continue
        archetypes_field = str(raw.get("archetypes", ""))
        records.append(
            AtlasSludgeEventRecord(
                narrative_id=str(raw.get("narrative_id", "")),
                source_snapshot_sha256=str(raw.get("source_snapshot_sha256", "")),
                archetypes=tuple(part for part in archetypes_field.split(",") if part),
                stack=str(raw.get("stack", "")),
                audit_hash=str(raw.get("hash", "")),
                timestamp=str(raw.get("timestamp", "")),
            )
        )
    return tuple(records)


def create_app(
    *,
    api_token: str | None = None,
    audit_path: Path | None = None,
    doi_registry_path: Path | None = None,
    dois: Sequence[DoiRecord] | None = None,
    replay_status: ReplayStatus | None = None,
    account_service: AccountService | None = None,
    account_db_path: Path | None = None,
    account_setup_secret: str | None = None,
    session_cookie_secure: bool | None = None,
    workflow_service: WorkflowService | None = None,
    workflow_db_path: Path | None = None,
    database_url: str | None = None,
    bootstrap_trusted_proxy: bool | None = None,
    swr_runtime: WarRoomCore | None = None,
    execution_secret: str | None = None,
    instance_name: str | None = None,
    taar_repo_root: Path | None = None,
    screening_quarantine_dir: Path | None = None,
    waterfall_adapter: WaterfallAdapter | None = None,
    waterfall_runtime: WaterfallRuntime | None = None,
) -> FastAPI:
    """Create an app with explicit, injectable runtime state."""
    configured_token = _secret_value(api_token, "PROJECT_AI_API_TOKEN")
    configured_instance_name = (
        instance_name
        if instance_name is not None
        else os.getenv("PROJECT_AI_INSTANCE_NAME", "PROJECT-AI-LOCAL")
    ).strip()
    if not configured_instance_name:
        raise ValueError("PROJECT_AI_INSTANCE_NAME must not be blank")
    configured_audit_path = audit_path or _optional_path(os.getenv("PROJECT_AI_AUDIT_PATH"))
    relay = AppendOnlyAuditRelay(configured_audit_path) if configured_audit_path else None

    registry_path = doi_registry_path or _default_registry_path()
    registry = (
        tuple(dois)
        if dois is not None
        else (load_doi_registry(registry_path) if registry_path is not None else ())
    )
    replay = replay_status or ReplayStatus()
    secure_session_cookie = (
        session_cookie_secure
        if session_cookie_secure is not None
        else os.getenv("PROJECT_AI_SESSION_COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}
    )
    trust_private_bootstrap_proxy = (
        bootstrap_trusted_proxy
        if bootstrap_trusted_proxy is not None
        else os.getenv("PROJECT_AI_BOOTSTRAP_TRUST_PRIVATE_PROXY", "false").lower()
        in {"1", "true", "yes"}
    )
    configured_database_url = _secret_value(
        database_url if database_url else None,
        "PROJECT_AI_DATABASE_URL",
    )
    configured_setup_secret = _secret_value(account_setup_secret, "PROJECT_AI_SETUP_SECRET")
    configured_mfa_key = _secret_value(None, "PROJECT_AI_MFA_KEY")
    configured_account_path = account_db_path or _optional_path(os.getenv("PROJECT_AI_ACCOUNT_DB"))
    configured_accounts = account_service
    if configured_accounts is None and configured_database_url:
        configured_accounts = AccountService(
            PostgresAccountRepository(configured_database_url),
            setup_secret=configured_setup_secret,
            mfa_encryption_key=configured_mfa_key,
        )
    elif configured_accounts is None and configured_account_path is not None:
        configured_accounts = AccountService(
            AccountRepository(configured_account_path),
            setup_secret=configured_setup_secret,
            mfa_encryption_key=configured_mfa_key,
        )
    configured_workflow_path = workflow_db_path or _optional_path(
        os.getenv("PROJECT_AI_WORKFLOW_DB")
    )
    configured_workflows = workflow_service
    if configured_workflows is None and configured_database_url:
        configured_workflows = WorkflowService(PostgresWorkflowRepository(configured_database_url))
    elif configured_workflows is None and configured_workflow_path is not None:
        configured_workflows = WorkflowService(WorkflowRepository(configured_workflow_path))
    configured_execution_secret = _secret_value(
        execution_secret if execution_secret else None,
        "PROJECT_AI_EXECUTION_SECRET",
    )
    machine_credentials_required = os.getenv(
        "PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED", "false"
    ).lower() in {"1", "true", "yes", "on"}
    configured_waterfall_runtime = waterfall_runtime
    configured_waterfall_adapter = waterfall_adapter
    waterfall_enabled = os.getenv("PROJECT_AI_WATERFALL_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if configured_waterfall_runtime is None and configured_waterfall_adapter is None:
        configured_waterfall_runtime, configured_waterfall_adapter = build_waterfall_integration(
            enabled=waterfall_enabled,
            config_path=_optional_path(os.getenv("PROJECT_AI_WATERFALL_CONFIG")),
            execution_secret=configured_execution_secret,
            audit_relay=relay,
        )
    configured_swr = swr_runtime
    if configured_swr is None and configured_execution_secret:
        configured_bundle_dir = _optional_path(os.getenv("PROJECT_AI_SWR_BUNDLE_DIR"))
        if configured_bundle_dir is None and configured_audit_path is not None:
            configured_bundle_dir = configured_audit_path.parent / "swr-bundles"
        configured_swr = build_swr_runtime(
            configured_execution_secret,
            bundle_dir=configured_bundle_dir,
        )
    configured_quarantine_dir = (
        screening_quarantine_dir
        or _optional_path(os.getenv("PROJECT_AI_QUARANTINE_DIR"))
        or DEFAULT_QUARANTINE_DIR
    )
    input_screen = CerberusScreen(configured_quarantine_dir)
    configured_taar_root = taar_repo_root or _optional_path(os.getenv("PROJECT_AI_TAAR_REPO_ROOT"))
    configured_taar: TaarInspectionService | None = None
    taar_configuration_error: str | None = None
    if configured_taar_root is not None:
        try:
            configured_taar = TaarInspectionService(configured_taar_root)
        except (OSError, ValueError, TaarError) as error:
            taar_configuration_error = str(error)

    application = FastAPI(
        title="Project-AI Development Gateway",
        version=PROJECT_AI_VERSION,
        docs_url="/docs",
        redoc_url=None,
    )
    install_metrics(application)

    def _check_machine_credential(
        credential: HTTPAuthorizationCredentials | None,
        request: Request,
        required_scope: str | None = None,
    ) -> None:
        if relay is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Protected API surfaces are not configured",
            )
        if credential is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if configured_accounts is not None:
            stored_credentials = configured_accounts.repository.machine_credentials()
            if stored_credentials or machine_credentials_required:
                try:
                    principal = configured_accounts.authenticate_machine_credential(
                        credential.credentials, required_scope
                    )
                except PermissionDenied as error:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
                    ) from error
                except InvalidMachineCredential as error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid machine credential",
                        headers={"WWW-Authenticate": "Bearer"},
                    ) from error
                request.state.machine_credential = principal
                return
        if not configured_token:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Protected API surfaces are not configured",
            )
        if machine_credentials_required or not hmac.compare_digest(
            credential.credentials.encode("utf-8"), configured_token.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid machine credential",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _machine_auth_for_scope(required_scope: str | None) -> Callable[..., None]:
        def dependency(
            request: Request,
            credential: Annotated[
                HTTPAuthorizationCredentials | None, Security(MACHINE_BEARER_SCHEME)
            ] = None,
        ) -> None:
            _check_machine_credential(credential, request, required_scope)

        return dependency

    def require_machine_scope(scope: str) -> Callable[..., None]:
        return _machine_auth_for_scope(scope)

    def machine_identity(request: Request) -> dict[str, str]:
        principal = getattr(request.state, "machine_credential", None)
        if principal is None:
            return {}
        return {
            "machine_credential_id": principal.id,
            "machine_credential_label": principal.label,
        }

    machine_write_protected = [Depends(require_machine_scope("evidence.write"))]
    analysis_protected = [Depends(require_machine_scope("analysis.generate"))]

    def require_evidence_auth(
        request: Request,
        credential: Annotated[
            HTTPAuthorizationCredentials | None, Security(MACHINE_BEARER_SCHEME)
        ] = None,
        session_token: Annotated[str | None, Security(SESSION_COOKIE_SCHEME)] = None,
    ) -> None:
        if session_token and configured_accounts is not None:
            try:
                account, _ = configured_accounts.authenticate(session_token)
                configured_accounts.require_permission(account, InterfacePermission.EVIDENCE_VIEW)
                return
            except PermissionDenied as error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
                ) from error
            except AccountServiceError:
                pass
        _check_machine_credential(credential, request, "evidence.read")

    evidence_protected = [Depends(require_evidence_auth)]

    def active_relay() -> AppendOnlyAuditRelay:
        if relay is None:  # Protected dependencies reject this configuration first.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit relay is not configured",
            )
        return relay

    install_auth_routes(
        application,
        configured_accounts,
        secure_cookie=secure_session_cookie,
        trust_private_bootstrap_proxy=trust_private_bootstrap_proxy,
    )
    install_workflow_routes(application, configured_accounts, configured_workflows)
    install_atlas_workflow_routes(application, configured_accounts, configured_workflows, relay)
    install_swr_workflow_routes(
        application,
        configured_accounts,
        configured_workflows,
        configured_swr,
        relay,
    )
    install_taar_workflow_routes(
        application,
        configured_accounts,
        configured_workflows,
        relay,
        configured_taar,
        taar_configuration_error,
    )
    install_waterfall_routes(
        application,
        adapter=configured_waterfall_adapter,
        runtime=configured_waterfall_runtime,
        audit_relay=relay,
        require_machine_scope=require_machine_scope,
    )

    @application.get("/health/live", response_model=HealthResponse)
    def health_live() -> HealthResponse:
        return HealthResponse()

    @application.get("/api/v1/instance", response_model=InstanceIdentityResponse)
    def instance_identity() -> InstanceIdentityResponse:
        return InstanceIdentityResponse(display_name=configured_instance_name)

    @application.get("/dois", response_model=DoiResponse)
    def list_dois() -> DoiResponse:
        return DoiResponse(dois=registry)

    @application.get("/replay/status", response_model=ReplayStatus)
    def replay_state() -> ReplayStatus:
        return replay

    @application.get("/api/v1/dashboard", response_model=DashboardResponse)
    def dashboard_state() -> DashboardResponse:
        if relay is None:
            audit_surface = DashboardSurface(
                id="audit_chain",
                label="Audit chain",
                status="unavailable",
                metric="Not configured",
                detail="Protected audit storage is not configured for this gateway.",
            )
        else:
            try:
                chain_valid, audit_count = relay.verify()
            except (OSError, ValueError):
                chain_valid, audit_count = False, 0
            audit_surface = DashboardSurface(
                id="audit_chain",
                label="Audit chain",
                status="healthy" if chain_valid else "degraded",
                metric=f"{audit_count} entries" if chain_valid else "Verification failed",
                detail=(
                    "The append-only chain verifies."
                    if chain_valid
                    else "Evidence-dependent workflows must remain unavailable."
                ),
            )

        replay_surface_status: Literal["healthy", "degraded", "not_run"] = (
            "healthy"
            if replay.status == "pass"
            else "degraded"
            if replay.status == "fail"
            else "not_run"
        )
        return DashboardResponse(
            authority_boundary=(
                "The Control Center presents evidence and requests. It does not grant authority; "
                "canonical identity, capability, governance, audit, and execution gates remain decisive."
            ),
            surfaces=(
                DashboardSurface(
                    id="gateway",
                    label="Gateway",
                    status="healthy",
                    metric=PROJECT_AI_VERSION,
                    detail="Development gateway is live.",
                ),
                DashboardSurface(
                    id="replay",
                    label="Replay",
                    status=replay_surface_status,
                    metric=f"{replay.invariants_passed}/{replay.invariants_total} invariants",
                    detail=(
                        f"Replay state is {replay.status}."
                        + (f" Last update: {replay.updated_at}." if replay.updated_at else "")
                    ),
                ),
                audit_surface,
                DashboardSurface(
                    id="evidence",
                    label="Evidence registry",
                    status="healthy" if registry else "unavailable",
                    metric=f"{len(registry)} DOI records",
                    detail="Public DOI-backed evidence available to the console.",
                ),
            ),
            doi_records=len(registry),
        )

    @application.get("/api/v1/modules", response_model=ModulesResponse)
    def module_surfaces() -> ModulesResponse:
        """Describe real packages without claiming absent human workflows."""
        return ModulesResponse(
            modules=(
                ModuleSurface(
                    id="governance",
                    label="Governance",
                    category="authority",
                    maturity="implemented",
                    interface_status="read_only",
                    authority="Canonical verdict authority; execution remains separate",
                    summary="Fail-closed ALLOW, DENY, and ESCALATE evaluation.",
                ),
                ModuleSurface(
                    id="capability",
                    label="Capabilities",
                    category="authority",
                    maturity="implemented",
                    interface_status="backend_only",
                    authority="Scoped authorization input to the execution gate",
                    summary="Signed, scoped, expiring capability primitives.",
                ),
                ModuleSurface(
                    id="execution",
                    label="Execution gate",
                    category="authority",
                    maturity="implemented",
                    interface_status="backend_only",
                    authority="Sole governed actuation boundary",
                    summary="No human-interface actuation endpoint is exposed.",
                ),
                ModuleSurface(
                    id="chimera",
                    label="Chimera security",
                    category="security",
                    maturity="implemented",
                    interface_status="read_only",
                    authority="Security classification and append-only audit relay",
                    summary="Machine-authenticated writes; humans inspect verified evidence.",
                ),
                ModuleSurface(
                    id="swr",
                    label="Sovereign War Room",
                    category="simulation",
                    maturity="implemented",
                    interface_status=(
                        "available"
                        if configured_swr is not None and relay is not None
                        else "read_only"
                    ),
                    authority="Governed deterministic scenarios",
                    summary=(
                        "Reviewed scenario requests can produce execution-gate receipts."
                        if configured_swr is not None and relay is not None
                        else "Scenario catalog is readable; execution secrets or audit are unconfigured."
                    ),
                ),
                ModuleSurface(
                    id="atlas",
                    label="Atlas",
                    category="analysis",
                    maturity="experimental",
                    interface_status=(
                        "available"
                        if configured_accounts is not None and relay is not None
                        else "read_only"
                    ),
                    authority="Analysis only; never a verdict or authority grant",
                    summary=(
                        "Signed-in analysts can verify and reconstruct bounded replay bundles; "
                        "Sludge generation remains machine-authenticated."
                        if configured_accounts is not None and relay is not None
                        else "Status is readable; replay requires human accounts and durable audit."
                    ),
                ),
                ModuleSurface(
                    id="taar",
                    label="TAAR",
                    category="analysis",
                    maturity="experimental",
                    interface_status=(
                        "available"
                        if configured_taar is not None
                        and configured_accounts is not None
                        and configured_workflows is not None
                        and relay is not None
                        else "read_only"
                    ),
                    authority="Registered report-only readers; no source-mutation capability",
                    summary=(
                        "Signed-in operators can run registered readers against the fixed server target."
                        if configured_taar is not None
                        and configured_accounts is not None
                        and configured_workflows is not None
                        and relay is not None
                        else "Inspection requires a server-fixed target, accounts, workflows, and audit."
                    ),
                ),
                ModuleSurface(
                    id="caretaker",
                    label="Caretaker",
                    category="analysis",
                    maturity="pre_alpha",
                    interface_status="backend_only",
                    authority="Governs only its own hosted inference",
                    summary="Canonical Project-AI verdict authority remains separate.",
                ),
                ModuleSurface(
                    id="ai-takeover",
                    label="AI Takeover",
                    category="simulation",
                    maturity="experimental",
                    interface_status="backend_only",
                    authority="Simulation only",
                    summary="Registered package; no shared run contract is exposed.",
                ),
                ModuleSurface(
                    id="alien-invaders",
                    label="Alien Invaders",
                    category="simulation",
                    maturity="experimental",
                    interface_status="backend_only",
                    authority="Simulation only",
                    summary="Registered package; no shared run contract is exposed.",
                ),
                ModuleSurface(
                    id="cognitive-warfare",
                    label="Cognitive Warfare",
                    category="simulation",
                    maturity="experimental",
                    interface_status="backend_only",
                    authority="Simulation only",
                    summary="Registered package; no shared run contract is exposed.",
                ),
                ModuleSurface(
                    id="emp-defense",
                    label="EMP Defense",
                    category="simulation",
                    maturity="experimental",
                    interface_status="backend_only",
                    authority="Simulation only",
                    summary="Registered package; no shared run contract is exposed.",
                ),
                ModuleSurface(
                    id="waterfall",
                    label="Thirstys Waterfall",
                    category="operations",
                    maturity="implemented",
                    interface_status=(
                        "available"
                        if configured_waterfall_adapter is not None
                        and configured_waterfall_adapter.v3q_configured
                        and configured_waterfall_runtime is not None
                        and relay is not None
                        else "backend_only"
                    ),
                    authority="Shared Project-AI/V3Q authority contract through the execution gate",
                    summary=(
                        "Machine-authenticated status and allow-listed operations are available."
                        if configured_waterfall_adapter is not None
                        and configured_waterfall_adapter.v3q_configured
                        and configured_waterfall_runtime is not None
                        and relay is not None
                        else "Copied runtime is installed; V3Q gate, runtime, and audit must be configured."
                    ),
                ),
                ModuleSurface(
                    id="api",
                    label="Development gateway",
                    category="operations",
                    maturity="implemented",
                    interface_status="available",
                    authority="Transport only; no governance authority",
                    summary="Health, evidence, account, dashboard, and diagnostic APIs.",
                ),
            )
        )

    @application.get("/atlas/status", response_model=AtlasStatus)
    def atlas_status() -> AtlasStatus:
        return AtlasStatus(subordination_notice=SUBORDINATION_NOTICE)

    @application.get(
        "/audit",
        response_model=AuditResponse,
        dependencies=evidence_protected,
    )
    def audit_view(
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0,
        query: Annotated[str | None, Query(max_length=200)] = None,
        event: Annotated[str | None, Query(max_length=120)] = None,
    ) -> AuditResponse:
        return _audit_records(active_relay(), limit, offset, query, event)

    @application.post(
        "/chimera/verdict",
        response_model=AuditWriteResponse,
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=machine_write_protected,
    )
    def chimera_verdict(request: VerdictRequest, http_request: Request) -> AuditWriteResponse:
        identity = machine_identity(http_request)
        record = receive_verdict(
            active_relay(),
            action_id=request.action_id,
            verdict=request.verdict,
            source=request.source,
            **identity,
        )
        return AuditWriteResponse(event=str(record["event"]), hash=str(record["hash"]))

    @application.post(
        "/chimera/canary",
        response_model=AuditWriteResponse,
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=machine_write_protected,
    )
    def chimera_canary(request: CanaryRequest, http_request: Request) -> AuditWriteResponse:
        identity = machine_identity(http_request)
        record = receive_canary_hit(
            active_relay(),
            canary_value=request.canary_value,
            context=request.context,
            **identity,
        )
        return AuditWriteResponse(event=str(record["event"]), hash=str(record["hash"]))

    @application.post(
        "/atlas/sludge",
        response_model=AtlasSludgeResponse,
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=analysis_protected,
        responses={
            status.HTTP_403_FORBIDDEN: {
                "model": ScreeningBlockResponse,
                "description": (
                    "Input blocked by Cerberus screening "
                    "(transport-layer refusal, not a governance verdict)"
                ),
            }
        },
    )
    def atlas_sludge(
        request: AtlasSludgeRequest, response: Response, http_request: Request
    ) -> AtlasSludgeResponse:
        identity = machine_identity(http_request)
        screening_summary = input_screen.screen_payload(
            request.rs_snapshot, source="atlas.sludge", relay=active_relay()
        )
        try:
            archetypes = (
                None
                if request.archetypes is None
                else tuple(NarrativeArchetype(value) for value in request.archetypes)
            )
            narrative = get_sludge_sandbox().generate_narrative(
                request.rs_snapshot,
                archetypes=archetypes,
            )
        except SludgeSandboxError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        record = active_relay().append(
            "atlas.sludge_narrative",
            {
                "archetypes": ",".join(archetype.value for archetype in narrative.archetypes),
                "narrative_id": narrative.narrative_id,
                "source_snapshot_sha256": narrative.source_snapshot_sha256,
                "stack": narrative.stack,
                **identity,
            },
        )
        response.headers["X-Cerberus-Screening"] = screening_summary
        return AtlasSludgeResponse(
            hash=str(record["hash"]),
            narrative=AtlasSludgeNarrative.model_validate(narrative.to_canonical_dict()),
        )

    @application.get(
        "/api/v1/modules/atlas/sludge",
        response_model=AtlasSludgeInspectionResponse,
        dependencies=evidence_protected,
    )
    def atlas_sludge_inspection(
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> AtlasSludgeInspectionResponse:
        newest_first = tuple(reversed(_sludge_event_records(active_relay())))
        return AtlasSludgeInspectionResponse(
            total_count=len(newest_first),
            offset=offset,
            limit=limit,
            records=newest_first[offset : offset + limit],
        )

    @application.get(
        "/api/v1/modules/atlas/sludge/{narrative_id}",
        response_model=AtlasSludgeEventDetailResponse,
        dependencies=evidence_protected,
    )
    def atlas_sludge_event_detail(narrative_id: str) -> AtlasSludgeEventDetailResponse:
        for record in reversed(_sludge_event_records(active_relay())):
            if record.narrative_id == narrative_id:
                return AtlasSludgeEventDetailResponse(record=record)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sludge narrative event not found",
        )

    return application


app = create_app()
