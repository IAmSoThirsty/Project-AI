"""Fail-closed Project-AI HTTP gateway."""

from __future__ import annotations

import hmac
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, cast

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status

from project_ai_api.models import (
    AuditResponse,
    AuditWriteResponse,
    CanaryRequest,
    DoiRecord,
    DoiResponse,
    HealthResponse,
    JsonScalar,
    ReplayStatus,
    VerdictRequest,
)
from project_ai_api.registry import load_doi_registry
from security import AppendOnlyAuditRelay, receive_canary_hit, receive_verdict

type AuditRecord = dict[str, JsonScalar]


def _optional_path(value: str | None) -> Path | None:
    return Path(value).expanduser() if value and value.strip() else None


def _default_registry_path() -> Path | None:
    configured = _optional_path(os.getenv("PROJECT_AI_DOI_REGISTRY"))
    if configured is not None:
        return configured
    candidate = Path.cwd() / "docs" / "reference" / "DOI_REGISTRY.md"
    return candidate if candidate.is_file() else None


def _audit_records(relay: AppendOnlyAuditRelay, limit: int) -> AuditResponse:
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
        return AuditResponse(count=0, records=())
    lines = [line for line in relay.path.read_text(encoding="utf-8").splitlines() if line]
    records = tuple(cast(AuditRecord, json.loads(line)) for line in lines[-limit:])
    return AuditResponse(count=count, records=records)


def create_app(
    *,
    api_token: str | None = None,
    audit_path: Path | None = None,
    doi_registry_path: Path | None = None,
    dois: Sequence[DoiRecord] | None = None,
    replay_status: ReplayStatus | None = None,
) -> FastAPI:
    """Create an app with explicit, injectable runtime state."""
    configured_token = api_token if api_token is not None else os.getenv("PROJECT_AI_API_TOKEN")
    configured_audit_path = audit_path or _optional_path(os.getenv("PROJECT_AI_AUDIT_PATH"))
    relay = AppendOnlyAuditRelay(configured_audit_path) if configured_audit_path else None

    registry_path = doi_registry_path or _default_registry_path()
    registry = (
        tuple(dois)
        if dois is not None
        else (load_doi_registry(registry_path) if registry_path is not None else ())
    )
    replay = replay_status or ReplayStatus()

    application = FastAPI(
        title="Project-AI Development Gateway",
        version="0.0.0.dev0",
        docs_url="/docs",
        redoc_url=None,
    )

    def require_auth(authorization: Annotated[str | None, Header()] = None) -> None:
        if not configured_token or relay is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Protected API surfaces are not configured",
            )
        scheme, separator, credential = (authorization or "").partition(" ")
        if (
            separator != " "
            or scheme.lower() != "bearer"
            or not hmac.compare_digest(credential.encode("utf-8"), configured_token.encode("utf-8"))
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    protected = [Depends(require_auth)]

    def active_relay() -> AppendOnlyAuditRelay:
        if relay is None:  # Protected dependencies reject this configuration first.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit relay is not configured",
            )
        return relay

    @application.get("/health/live", response_model=HealthResponse)
    def health_live() -> HealthResponse:
        return HealthResponse()

    @application.get("/dois", response_model=DoiResponse)
    def list_dois() -> DoiResponse:
        return DoiResponse(dois=registry)

    @application.get("/replay/status", response_model=ReplayStatus)
    def replay_state() -> ReplayStatus:
        return replay

    @application.get(
        "/audit",
        response_model=AuditResponse,
        dependencies=protected,
    )
    def audit_view(limit: Annotated[int, Query(ge=1, le=500)] = 100) -> AuditResponse:
        return _audit_records(active_relay(), limit)

    @application.post(
        "/chimera/verdict",
        response_model=AuditWriteResponse,
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=protected,
    )
    def chimera_verdict(request: VerdictRequest) -> AuditWriteResponse:
        record = receive_verdict(
            active_relay(),
            action_id=request.action_id,
            verdict=request.verdict,
            source=request.source,
        )
        return AuditWriteResponse(event=str(record["event"]), hash=str(record["hash"]))

    @application.post(
        "/chimera/canary",
        response_model=AuditWriteResponse,
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=protected,
    )
    def chimera_canary(request: CanaryRequest) -> AuditWriteResponse:
        record = receive_canary_hit(
            active_relay(), canary_value=request.canary_value, context=request.context
        )
        return AuditWriteResponse(event=str(record["event"]), hash=str(record["hash"]))

    return application


app = create_app()
