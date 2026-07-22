"""Fail-closed Project-AI HTTP gateway."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal, cast

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    Security,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from kernel.version import PROJECT_AI_VERSION
from project_ai_waterfall.transport import WaterfallRuntime
from taar.errors import TaarError
from waterfall_adapter import WaterfallAdapter

from accounts import (
    Account,
    AccountRepository,
    AccountService,
    AccountServiceError,
    InterfacePermission,
    InvalidCsrf,
    InvalidMachineCredential,
    InvalidSession,
    PermissionDenied,
    PostgresAccountRepository,
    RateLimited,
    has_permission,
)
from atlas import SUBORDINATION_NOTICE, NarrativeArchetype, SludgeSandboxError, get_sludge_sandbox
from project_ai_api.atlas_workflows import install_atlas_workflow_routes
from project_ai_api.auth import (
    SESSION_COOKIE_SCHEME,
    install_auth_routes,
    request_source,
    require_same_origin,
)
from project_ai_api.metrics import install_metrics
from project_ai_api.models import (
    AtlasSludgeEventDetailResponse,
    AtlasSludgeEventRecord,
    AtlasSludgeInspectionResponse,
    AtlasSludgeNarrative,
    AtlasSludgeRequest,
    AtlasSludgeResponse,
    AtlasStatus,
    AuditDetailRequest,
    AuditDetailResponse,
    AuditExportFilters,
    AuditExportRecord,
    AuditExportRequest,
    AuditExportResponse,
    AuditResponse,
    AuditSearchRequest,
    AuditWriteResponse,
    CanaryRequest,
    DashboardResponse,
    DashboardSurface,
    DoiRecord,
    DoiResponse,
    HealthResponse,
    HumanAuditRecordSummary,
    HumanAuditResponse,
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

AUDIT_EXPORT_SAFE_FIELDS = frozenset(
    {
        "attack_type",
        "classification",
        "configured",
        "confidence",
        "exported_count",
        "filtered_count",
        "limit",
        "offset",
        "outcome",
        "severity",
        "status",
        "verdict",
    }
)
AUDIT_EXPORT_IDENTIFIER_FIELDS = frozenset(
    {
        "action_id",
        "account_id",
        "agent_id",
        "actor_id",
        "attempt_id",
        "bundle_id",
        "claim_id",
        "created_by",
        "initiated_by",
        "machine_credential_id",
        "narrative_id",
        "request_id",
        "reviewer_account_id",
        "run_id",
        "scenario_id",
    }
)
AUDIT_EXPORT_HASH_SUFFIXES = ("_hash", "_sha256")
AUDIT_DETAIL_SECRET_FIELD_FRAGMENTS = (
    "authorization",
    "cookie",
    "csrf",
    "password",
    "private_key",
    "recovery_code",
    "secret",
    "token",
    "totp",
)
AUDIT_FILTER_FIELDS: dict[str, tuple[str, ...]] = {
    "actor": ("actor_id", "agent_id"),
    "account": ("account_id", "initiated_by", "created_by", "reviewer_account_id"),
    "operation": ("operation",),
    "resource": ("resource",),
    "verdict": ("verdict", "outcome"),
    "severity": ("severity",),
}

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


def _audit_filters(
    *,
    query: str | None = None,
    event: str | None = None,
    actor: str | None = None,
    account: str | None = None,
    operation: str | None = None,
    resource: str | None = None,
    verdict: Literal["ALLOW", "DENY", "ESCALATE"] | None = None,
    severity: str | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> AuditExportFilters:
    def cleaned(value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None

    return AuditExportFilters(
        query=cleaned(query),
        event=cleaned(event),
        actor=cleaned(actor),
        account=cleaned(account),
        operation=cleaned(operation),
        resource=cleaned(resource),
        verdict=verdict,
        severity=cleaned(severity),
        from_time=from_time,
        to_time=to_time,
    )


def _audit_records(
    relay: AppendOnlyAuditRelay,
    limit: int,
    offset: int = 0,
    cursor: str | None = None,
    filters: AuditExportFilters | None = None,
    *,
    sensitive_query: bool = True,
) -> AuditResponse:
    active_filters = filters or AuditExportFilters()
    if cursor and offset:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Audit cursor and offset cannot be combined",
        )
    for boundary in (active_filters.from_time, active_filters.to_time):
        if boundary is not None and boundary.utcoffset() is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Audit time filters must include a timezone offset",
            )
    if (
        active_filters.from_time is not None
        and active_filters.to_time is not None
        and active_filters.from_time > active_filters.to_time
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Audit from_time must not be later than to_time",
        )
    count, records = _verified_audit_snapshot(relay)
    normalized_query = active_filters.query.strip().casefold() if active_filters.query else ""
    normalized_event = active_filters.event.strip().casefold() if active_filters.event else ""

    def exact_field_match(record: AuditRecord, filter_name: str, expected: str | None) -> bool:
        if not expected:
            return True
        normalized = expected.strip().casefold()
        return any(
            str(record.get(field, "")).casefold() == normalized
            for field in AUDIT_FILTER_FIELDS[filter_name]
        )

    def time_match(record: AuditRecord) -> bool:
        if active_filters.from_time is None and active_filters.to_time is None:
            return True
        try:
            timestamp = datetime.fromisoformat(
                str(record.get("timestamp", "")).replace("Z", "+00:00")
            )
        except ValueError:
            return False
        if timestamp.utcoffset() is None:
            return False
        return not (
            (active_filters.from_time is not None and timestamp < active_filters.from_time)
            or (active_filters.to_time is not None and timestamp > active_filters.to_time)
        )

    filtered: list[AuditRecord] = []
    for record in records:
        query_record = (
            record if sensitive_query else _human_audit_summary(record).model_dump(mode="json")
        )
        if (
            (not normalized_event or str(record.get("event", "")).casefold() == normalized_event)
            and exact_field_match(record, "actor", active_filters.actor)
            and exact_field_match(record, "account", active_filters.account)
            and exact_field_match(record, "operation", active_filters.operation)
            and exact_field_match(record, "resource", active_filters.resource)
            and exact_field_match(record, "verdict", active_filters.verdict)
            and exact_field_match(record, "severity", active_filters.severity)
            and time_match(record)
            and (
                not normalized_query
                or normalized_query in json.dumps(query_record, sort_keys=True).casefold()
            )
        ):
            filtered.append(record)
    newest_first = tuple(reversed(filtered))
    start = offset
    if cursor:
        try:
            start = next(
                index + 1
                for index, record in enumerate(newest_first)
                if record.get("hash") == cursor
            )
        except StopIteration as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Audit cursor does not match the current filter set",
            ) from error
    page = newest_first[start : start + limit]
    has_more = start + len(page) < len(newest_first)
    next_cursor = str(page[-1]["hash"]) if page and has_more else None
    return AuditResponse(
        count=count,
        filtered_count=len(filtered),
        offset=start,
        limit=limit,
        cursor=cursor,
        next_cursor=next_cursor,
        has_more=has_more,
        records=page,
    )


def _verified_audit_snapshot(
    relay: AppendOnlyAuditRelay,
) -> tuple[int, tuple[AuditRecord, ...]]:
    try:
        valid, count, records = relay.verified_snapshot()
    except (OSError, ValueError):
        valid, count, records = False, 0, ()
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Audit hash chain verification failed",
        )
    return count, records


def _human_audit_summary(record: AuditRecord) -> HumanAuditRecordSummary:
    raw_verdict = record.get("verdict")
    verdict = cast(
        Literal["ALLOW", "DENY", "ESCALATE"] | None,
        raw_verdict if raw_verdict in {"ALLOW", "DENY", "ESCALATE"} else None,
    )
    raw_severity = record.get("severity")
    return HumanAuditRecordSummary(
        event=str(record.get("event", "audit.record")),
        timestamp=str(record.get("timestamp", "")),
        source_hash=str(record.get("hash", "")),
        previous_hash=str(record.get("previous_hash", "")),
        verdict=verdict,
        severity=raw_severity if isinstance(raw_severity, str) else None,
    )


def _human_audit_response(source: AuditResponse) -> HumanAuditResponse:
    return HumanAuditResponse(
        count=source.count,
        filtered_count=source.filtered_count,
        offset=source.offset,
        limit=source.limit,
        cursor=source.cursor,
        next_cursor=source.next_cursor,
        has_more=source.has_more,
        records=tuple(_human_audit_summary(record) for record in source.records),
    )


def _audit_sensitive_filter_permission(
    account: Account,
    filters: AuditExportFilters,
) -> bool:
    privileged = has_permission(account.role, InterfacePermission.AUDIT_RAW_VIEW)
    if not privileged and any(
        (filters.actor, filters.account, filters.operation, filters.resource)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Raw audit filters require permission: audit.raw_view",
        )
    return privileged


def _audit_export_record(record: AuditRecord) -> AuditExportRecord:
    structural = {"event", "hash", "previous_hash", "timestamp"}
    fields: dict[str, JsonScalar] = {}
    redacted_fields: list[str] = []
    for key, value in sorted(record.items()):
        if key in structural:
            continue
        if key in AUDIT_EXPORT_IDENTIFIER_FIELDS:
            fields[f"{key}_sha256"] = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
            redacted_fields.append(key)
        elif key in AUDIT_EXPORT_SAFE_FIELDS or key.endswith(AUDIT_EXPORT_HASH_SUFFIXES):
            fields[key] = value
        else:
            redacted_fields.append(key)
    return AuditExportRecord(
        event=str(record.get("event", "audit.record")),
        timestamp=str(record.get("timestamp", "")),
        source_hash=str(record.get("hash", "")),
        previous_hash=str(record.get("previous_hash", "")),
        fields=fields,
        redacted_fields=tuple(redacted_fields),
    )


def _audit_export_digest(records: tuple[AuditExportRecord, ...]) -> str:
    payload = json.dumps(
        [record.model_dump(mode="json") for record in records],
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _audit_detail_secret_field(field: str) -> bool:
    normalized = field.casefold().replace("-", "_")
    return any(fragment in normalized for fragment in AUDIT_DETAIL_SECRET_FIELD_FRAGMENTS)


def _audit_record_detail(
    relay: AppendOnlyAuditRelay,
    source_hash: str,
    *,
    privileged: bool,
) -> AuditDetailResponse:
    count, records = _verified_audit_snapshot(relay)
    match = next(
        (
            (position, record)
            for position, record in enumerate(records, start=1)
            if record.get("hash") == source_hash
        ),
        None,
    )
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit record not found in the verified chain",
        )
    position, record = match
    if privileged:
        redacted_fields = tuple(
            sorted(field for field in record if _audit_detail_secret_field(field))
        )
        safe_raw = {
            field: "[REDACTED]" if field in redacted_fields else value
            for field, value in record.items()
        }
        fields = {
            field: value
            for field, value in safe_raw.items()
            if field not in {"event", "hash", "previous_hash", "timestamp"}
        }
        raw_record: dict[str, JsonScalar] | None = safe_raw
        visibility: Literal["privileged", "redacted"] = "privileged"
    else:
        redacted = _audit_export_record(record)
        fields = redacted.fields
        redacted_fields = redacted.redacted_fields
        raw_record = None
        visibility = "redacted"
    return AuditDetailResponse(
        chain_position=position,
        chain_records=count,
        visibility=visibility,
        event=str(record.get("event", "audit.record")),
        timestamp=str(record.get("timestamp", "")),
        source_hash=str(record.get("hash", "")),
        previous_hash=str(record.get("previous_hash", "")),
        fields=fields,
        redacted_fields=redacted_fields,
        raw_record=raw_record,
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

    def authorize_human_audit_read(request: Request, session_token: str | None) -> Account:
        require_same_origin(request)
        if configured_accounts is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Human session required for audit search",
            )
        try:
            account, _ = configured_accounts.authenticate(session_token)
            configured_accounts.require_permission(account, InterfacePermission.EVIDENCE_VIEW)
            return account
        except InvalidSession as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            ) from error
        except PermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except AccountServiceError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage unavailable",
            ) from error

    def authorize_audit_export(
        request: Request,
        session_token: str | None,
        csrf_token: str | None,
    ) -> Account:
        require_same_origin(request)
        if configured_accounts is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Human session required for audit export",
            )
        try:
            return configured_accounts.authorize_rate_limited_action(
                session_token,
                csrf_token,
                permission=InterfacePermission.AUDIT_EXPORT,
                operation="audit_export",
                source=request_source(request),
                limit=10,
            )
        except InvalidSession as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            ) from error
        except (InvalidCsrf, PermissionDenied) as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except RateLimited as error:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(error),
                headers={"Retry-After": "900"},
            ) from error
        except AccountServiceError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage unavailable",
            ) from error

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
        cursor: Annotated[str | None, Query(pattern=r"^[a-f0-9]{64}$")] = None,
        query: Annotated[str | None, Query(max_length=200)] = None,
        event: Annotated[str | None, Query(max_length=120)] = None,
        actor: Annotated[str | None, Query(max_length=200)] = None,
        account: Annotated[str | None, Query(max_length=200)] = None,
        operation: Annotated[str | None, Query(max_length=200)] = None,
        resource: Annotated[str | None, Query(max_length=300)] = None,
        verdict: Literal["ALLOW", "DENY", "ESCALATE"] | None = None,
        severity: Annotated[str | None, Query(max_length=40)] = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> AuditResponse:
        return _audit_records(
            active_relay(),
            limit,
            offset,
            cursor,
            _audit_filters(
                query=query,
                event=event,
                actor=actor,
                account=account,
                operation=operation,
                resource=resource,
                verdict=verdict,
                severity=severity,
                from_time=from_time,
                to_time=to_time,
            ),
        )

    @application.post("/audit/search", response_model=HumanAuditResponse)
    def audit_search(
        payload: AuditSearchRequest,
        request: Request,
        session_token: Annotated[str | None, Security(SESSION_COOKIE_SCHEME)] = None,
    ) -> HumanAuditResponse:
        account = authorize_human_audit_read(request, session_token)
        filters = _audit_filters(
            query=payload.query,
            event=payload.event,
            actor=payload.actor,
            account=payload.account,
            operation=payload.operation,
            resource=payload.resource,
            verdict=payload.verdict,
            severity=payload.severity,
            from_time=payload.from_time,
            to_time=payload.to_time,
        )
        privileged = _audit_sensitive_filter_permission(account, filters)
        return _human_audit_response(
            _audit_records(
                active_relay(),
                payload.limit,
                cursor=payload.cursor,
                filters=filters,
                sensitive_query=privileged,
            )
        )

    @application.post("/audit/detail", response_model=AuditDetailResponse)
    def audit_detail(
        payload: AuditDetailRequest,
        request: Request,
        session_token: Annotated[str | None, Security(SESSION_COOKIE_SCHEME)] = None,
    ) -> AuditDetailResponse:
        account = authorize_human_audit_read(request, session_token)
        return _audit_record_detail(
            active_relay(),
            payload.source_hash,
            privileged=has_permission(account.role, InterfacePermission.AUDIT_RAW_VIEW),
        )

    @application.post(
        "/audit/export",
        response_model=AuditExportResponse,
        status_code=status.HTTP_200_OK,
    )
    def audit_export(
        payload: AuditExportRequest,
        request: Request,
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
        session_token: Annotated[str | None, Security(SESSION_COOKIE_SCHEME)] = None,
    ) -> AuditExportResponse:
        relay = active_relay()
        account = authorize_audit_export(request, session_token, csrf_token)
        filters = _audit_filters(
            query=payload.query,
            event=payload.event,
            actor=payload.actor,
            account=payload.account,
            operation=payload.operation,
            resource=payload.resource,
            verdict=payload.verdict,
            severity=payload.severity,
            from_time=payload.from_time,
            to_time=payload.to_time,
        )
        privileged = _audit_sensitive_filter_permission(account, filters)
        source = _audit_records(
            relay,
            payload.limit,
            payload.offset,
            filters=filters,
            sensitive_query=privileged,
        )
        records = tuple(_audit_export_record(record) for record in source.records)
        records_sha256 = _audit_export_digest(records)
        filters_sha256 = hashlib.sha256(
            json.dumps(
                filters.model_dump(mode="json"),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        receipt = relay.append(
            "control_center.audit_export",
            {
                "exported_count": len(records),
                "filtered_count": source.filtered_count,
                "filters_sha256": filters_sha256,
                "initiated_by": account.id,
                "limit": payload.limit,
                "offset": payload.offset,
                "records_sha256": records_sha256,
            },
        )
        return AuditExportResponse(
            generated_at=datetime.now(UTC).isoformat(),
            source_chain_records=source.count,
            matched_records=source.filtered_count,
            exported_records=len(records),
            offset=payload.offset,
            limit=payload.limit,
            filters=filters,
            records_sha256=records_sha256,
            export_audit_hash=str(receipt["hash"]),
            records=records,
        )

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
