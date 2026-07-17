"""Human-session TAAR inspection over server-configured, report-only readers."""

import hashlib
import json
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Security, status
from taar.audit import hash_audit_record, list_audit_records
from taar.config import TaarConfig, load_taar_config
from taar.errors import AdmissionDenied, EvidenceError, TaarError
from taar.evidence import read_evidence, validate_evidence_hash
from taar.executor import run_agent
from taar.models import (
    CLASSIFICATION_RANK,
    AgentClass,
    AuditRecord,
    ClassificationLevel,
    EvidenceBundle,
    RunStatus,
)

from accounts import (
    Account,
    AccountService,
    AccountServiceError,
    InterfacePermission,
    PermissionDenied,
    StoredSession,
)
from project_ai_api.auth import SESSION_COOKIE_SCHEME, _require_same_origin
from project_ai_api.models import (
    TaarCommandResponse,
    TaarEvidenceResponse,
    TaarFindingResponse,
    TaarReaderSurface,
    TaarRunCreateResponse,
    TaarRunRequest,
    TaarRunsResponse,
    TaarStatusResponse,
)
from security import AppendOnlyAuditRelay
from taar.registry import Registry, load_registry
from workflows import WorkflowConflict, WorkflowPermissionDenied, WorkflowService

MAX_TAAR_REQUEST_BYTES = 16 * 1024
MAX_EVIDENCE_BYTES = 512 * 1024
TAAR_READER_OPERATION = "taar.reader.inspect"
REDACTION_BOUNDARY = (
    "SECRET, PHANTOM, BLACK, or hash-invalid evidence retains metadata but withholds "
    "commands, findings, and uncertainty from this human interface."
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class TaarInspectionService:
    """Read and run only registered TAAR readers against one fixed repository."""

    def __init__(self, repo_root: Path) -> None:
        root = repo_root.expanduser().resolve()
        if not root.is_dir():
            raise ValueError("TAAR inspection target must be an existing directory")
        self.config: TaarConfig = load_taar_config(root)
        if self.config.repo_root != root:
            raise ValueError("TAAR inspection target resolved outside the configured repository")
        self.registry: Registry = load_registry(root)

    def readers(self) -> tuple[TaarReaderSurface, ...]:
        surfaces: list[TaarReaderSurface] = []
        for agent in sorted(self.registry.agents_by_id.values(), key=lambda item: item.id):
            if agent.class_ is not AgentClass.READER or not agent.enabled:
                continue
            task = self.registry.tasks_by_id.get(agent.task_id)
            if task is None or not task.enabled:
                continue
            surfaces.append(
                TaarReaderSurface(
                    id=agent.id,
                    task_id=task.id,
                    description=task.description,
                    classification_default=task.classification_default.value,
                    timeout_seconds=task.timeout_seconds,
                    evidence_scope=tuple(task.input_paths or agent.allowed_read_paths),
                )
            )
        return tuple(surfaces)

    def status(self) -> TaarStatusResponse:
        return TaarStatusResponse(
            target_repository=self.config.repo_root.name,
            target_path=str(self.config.repo_root),
            facility_mode=self.config.facility_mode,  # type: ignore[arg-type, unused-ignore]
            registry_valid=not self.registry.validation_errors,
            registry_validation_errors=len(self.registry.validation_errors),
            readers=self.readers(),
        )

    def _evidence_paths(self) -> list[Path]:
        root = self.config.evidence_root.resolve()
        paths: list[Path] = []
        for candidate in self.config.evidence_root.glob("*/*/evidence.yaml"):
            resolved = candidate.resolve()
            if candidate.is_symlink() or not resolved.is_relative_to(root):
                continue
            if resolved.is_file() and resolved.stat().st_size <= MAX_EVIDENCE_BYTES:
                paths.append(resolved)
        return sorted(paths, key=lambda path: path.parent.name, reverse=True)

    def _audit_by_run(self) -> dict[str, AuditRecord]:
        records = list_audit_records(self.config.audit_root, limit=5000)
        result: dict[str, AuditRecord] = {}
        for record in records:
            result.setdefault(record.run_id, record)
        return result

    @staticmethod
    def _response(bundle: EvidenceBundle, audit: AuditRecord | None) -> TaarEvidenceResponse:
        evidence_valid = validate_evidence_hash(bundle)
        audit_valid = audit is not None and hash_audit_record(audit) == audit.hash
        redacted = (
            not evidence_valid
            or CLASSIFICATION_RANK[bundle.classification]
            >= CLASSIFICATION_RANK[ClassificationLevel.SECRET]
        )
        findings: tuple[TaarFindingResponse, ...] = ()
        commands: tuple[TaarCommandResponse, ...] = ()
        uncertainty: tuple[str, ...] = ()
        if not redacted:
            findings = tuple(
                TaarFindingResponse(
                    finding_id=item.finding_id,
                    severity=item.severity,
                    path=item.path,
                    line=item.line,
                    message=item.message,
                )
                for item in bundle.findings
            )
            commands = tuple(
                TaarCommandResponse(
                    command=item.command,
                    exit_code=item.exit_code,
                    duration_ms=item.duration_ms,
                )
                for item in bundle.commands
            )
            uncertainty = tuple(bundle.uncertainty)
        return TaarEvidenceResponse(
            run_id=bundle.run_id,
            agent_id=bundle.agent_id,
            task_id=bundle.task_id,
            classification=bundle.classification.value,
            status=(audit.status.value if audit is not None else RunStatus.FAILED.value),
            branch=bundle.branch,
            commit=bundle.commit,
            dirty_state_before=bundle.dirty_state_before,
            start_time=bundle.start_time,
            end_time=bundle.end_time,
            duration_ms=bundle.duration_ms,
            command_count=len(bundle.commands),
            finding_count=len(bundle.findings),
            evidence_hash=bundle.evidence_hash,
            evidence_hash_valid=evidence_valid,
            audit_record_hash=audit.hash if audit is not None else None,
            audit_record_hash_valid=audit_valid,
            details_redacted=redacted,
            findings=findings,
            commands=commands,
            uncertainty=uncertainty,
            human_action_required=bundle.classification is not ClassificationLevel.OPEN,
        )

    def runs(self, limit: int = 50) -> tuple[TaarEvidenceResponse, ...]:
        audits = self._audit_by_run()
        bundles = (read_evidence(path) for path in self._evidence_paths()[:limit])
        return tuple(self._response(bundle, audits.get(bundle.run_id)) for bundle in bundles)

    def run(self, run_id: str) -> TaarEvidenceResponse:
        for response in self.runs(limit=100):
            if response.run_id == run_id:
                return response
        raise EvidenceError("TAAR evidence run does not exist")

    def run_reader(self, agent_id: str) -> TaarEvidenceResponse:
        agent = self.registry.agents_by_id.get(agent_id)
        if agent is None or agent.class_ is not AgentClass.READER or not agent.enabled:
            raise AdmissionDenied(["only enabled registered reader agents may be run"])
        record = run_agent(agent_id, self.config, self.registry)
        return self.run(record.run_id)


def install_taar_workflow_routes(
    application: FastAPI,
    accounts: AccountService | None,
    workflows: WorkflowService | None,
    audit_relay: AppendOnlyAuditRelay | None,
    inspection: TaarInspectionService | None,
    configuration_error: str | None = None,
) -> None:
    def current(
        session_token: Annotated[str | None, Security(SESSION_COOKIE_SCHEME)] = None,
    ) -> tuple[Account, StoredSession]:
        if accounts is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Human account storage is not configured",
            )
        if not session_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
        try:
            account, session = accounts.authenticate(session_token)
            accounts.require_permission(account, InterfacePermission.TAAR_VIEW)
            return account, session
        except PermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except AccountServiceError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            ) from error

    def require_inspection() -> TaarInspectionService:
        if inspection is None:
            detail = "TAAR inspection target is not configured"
            if configuration_error:
                detail = f"TAAR inspection target is unavailable: {configuration_error}"
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
        return inspection

    @application.get("/api/v1/modules/taar/status", response_model=TaarStatusResponse)
    def taar_status(
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> TaarStatusResponse:
        del session
        return require_inspection().status()

    @application.get("/api/v1/modules/taar/runs", response_model=TaarRunsResponse)
    def list_taar_runs(
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
    ) -> TaarRunsResponse:
        del session
        try:
            runs = require_inspection().runs(limit)
        except (OSError, ValueError, TaarError, json.JSONDecodeError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TAAR evidence storage could not be verified",
            ) from error
        return TaarRunsResponse(runs=runs, redaction_boundary=REDACTION_BOUNDARY)

    @application.get("/api/v1/modules/taar/runs/{run_id}", response_model=TaarEvidenceResponse)
    def get_taar_run(
        run_id: str,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
    ) -> TaarEvidenceResponse:
        del session
        try:
            return require_inspection().run(run_id)
        except EvidenceError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        except (OSError, ValueError, TaarError, json.JSONDecodeError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TAAR evidence storage could not be verified",
            ) from error

    @application.post(
        "/api/v1/modules/taar/runs",
        response_model=TaarRunCreateResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_taar_run(
        payload: TaarRunRequest,
        request: Request,
        session: Annotated[tuple[Account, StoredSession], Depends(current)],
        csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    ) -> TaarRunCreateResponse:
        _require_same_origin(request)
        account, stored_session = session
        service = require_inspection()
        if accounts is None or workflows is None or audit_relay is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Durable human workflow and audit storage is required for TAAR inspection",
            )
        if len(await request.body()) > MAX_TAAR_REQUEST_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="TAAR inspection request must not exceed 16 KB",
            )
        try:
            accounts.require_permission(account, InterfacePermission.TAAR_RUN_READER)
            accounts.require_csrf(stored_session, csrf_token)
        except (PermissionDenied, AccountServiceError) as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error

        input_json = _canonical_json(
            {"agent_id": payload.agent_id, "target_path": str(service.config.repo_root)}
        )
        input_sha256 = _sha256(input_json)
        try:
            existing = workflows.existing_analysis(account, payload.idempotency_key)
            if existing is not None:
                if existing.input_sha256 != input_sha256:
                    raise WorkflowConflict(
                        "Idempotency key conflicts with different TAAR inspection input"
                    )
                output = json.loads(existing.output_json)
                return TaarRunCreateResponse(
                    run=service.run(output["run_id"]), reused_existing_receipt=True
                )
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except (WorkflowConflict, KeyError, json.JSONDecodeError) as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

        try:
            chain_valid, _ = audit_relay.verify()
        except (OSError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            ) from error
        if not chain_valid:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit hash chain verification failed",
            )

        try:
            run = service.run_reader(payload.agent_id)
        except AdmissionDenied as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
        except (OSError, ValueError, TaarError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TAAR reader execution failed before verifiable evidence was available",
            ) from error

        audit = audit_relay.append(
            "control_center.taar_reader_run",
            {
                "agent_id": run.agent_id,
                "classification": run.classification,
                "evidence_hash": run.evidence_hash,
                "initiated_by": account.id,
                "run_id": run.run_id,
                "taar_audit_hash": run.audit_record_hash or "",
            },
        )
        output_json = _canonical_json(
            {
                "evidence_hash": run.evidence_hash,
                "run_id": run.run_id,
                "taar_audit_hash": run.audit_record_hash,
            }
        )
        try:
            workflows.record_analysis(
                account,
                module_id="taar",
                operation=TAAR_READER_OPERATION,
                subject_id=run.run_id,
                input_json=input_json,
                input_sha256=input_sha256,
                output_json=output_json,
                output_sha256=_sha256(output_json),
                audit_hash=str(audit["hash"]),
                idempotency_key=payload.idempotency_key,
            )
        except WorkflowPermissionDenied as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
        except WorkflowConflict as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
        return TaarRunCreateResponse(run=run, reused_existing_receipt=False)
