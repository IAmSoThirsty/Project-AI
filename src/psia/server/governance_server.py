"""
Governance API Server — FastAPI application serving the desktop frontend.

Endpoints:
    GET  /health  — System health status (PSIA + Triumvirate)
    POST /intent  — Submit intent for governance evaluation
    GET  /audit   — Query DurableLedger records
    GET  /tarl    — Current TARL protection rules

The server runs on port 8001 (matching desktop/src/api/governance.ts).
CORS is configured for Electron localhost origins.

Usage:
    uvicorn psia.server.governance_server:app --host 0.0.0.0 --port 8001
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from psia.server.runtime import PSIARuntime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response Models (matching desktop/src/api/governance.ts)
# ---------------------------------------------------------------------------


class IntentRequest(BaseModel):
    """Matches the Intent interface in governance.ts."""
    actor: str = Field(..., description="human | agent | system")
    action: str = Field(..., description="read | write | execute | mutate")
    target: str = Field(..., description="Target resource")
    context: dict[str, Any] = Field(default_factory=dict)
    origin: str = Field("desktop", description="Request origin")


class PillarVote(BaseModel):
    """Single Triumvirate pillar vote."""
    pillar: str
    verdict: str  # allow | deny | degrade
    reason: str


class GovernanceResult(BaseModel):
    """Full governance evaluation result."""
    intent_hash: str
    tarl_version: str
    votes: list[PillarVote]
    final_verdict: str  # allow | deny | degrade
    timestamp: float


class IntentResponse(BaseModel):
    """Response wrapper for intent submission."""
    message: str
    governance: GovernanceResult


class AuditRecord(BaseModel):
    """Single audit record from the ledger."""
    intent_hash: str
    tarl_version: str
    votes: list[dict[str, Any]]
    final_verdict: str
    timestamp: float


class AuditResponse(BaseModel):
    """Full audit log response."""
    tarl_version: str
    tarl_signature: str
    records: list[AuditRecord]


class TarlRule(BaseModel):
    """Single TARL protection rule."""
    action: str
    allowed_actors: list[str]
    risk: str
    default: str


class TarlResponse(BaseModel):
    """TARL rules response."""
    version: str
    rules: list[TarlRule]


class HealthResponse(BaseModel):
    """System health response."""
    status: str
    tarl: str
    node_id: str | None = None
    boot_time: str | None = None
    intents_processed: int = 0
    ledger_records: int = 0
    sealed_blocks: int = 0
    halted: bool = False


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

_runtime: PSIARuntime | None = None


def _get_runtime() -> PSIARuntime:
    """Get the booted runtime singleton."""
    global _runtime
    if _runtime is None:
        _runtime = PSIARuntime.get_instance()
        boot_result = _runtime.boot()
        logger.info("Runtime boot result: %s", boot_result)
    return _runtime


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Startup: boot PSIA runtime. Shutdown: log."""
    logger.info("Governance API Server starting on port 8001...")
    _get_runtime()
    logger.info("PSIA Runtime booted — desktop API ready")
    yield
    logger.info("Governance API Server shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="Project-AI Governance API",
        description="REST API bridging PSIA, Triumvirate governance, and TARL to the desktop app",
        version="1.0.0",
        lifespan=_lifespan,
    )

    # CORS — allow Electron (localhost), Vite dev server, and file:// origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # Vite dev server
            "http://localhost:8001",   # Self
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8001",
            "file://",                 # Electron file:// origin
            "*",                       # Permissive for desktop use
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------
    # Routes
    # -------------------------------------------------------------------

    @application.get("/health", response_model=HealthResponse)
    async def health():
        """System health check — consumed by Dashboard page."""
        runtime = _get_runtime()
        data = runtime.get_health()
        return HealthResponse(**data)

    @application.post("/intent", response_model=IntentResponse)
    async def submit_intent(intent: IntentRequest):
        """Submit an intent for Triumvirate governance evaluation.

        The intent is evaluated by all three pillars (Galahad, Cerberus,
        Codex Deus), run through Four Laws checks, and the verdict is
        recorded in the PSIA DurableLedger.
        """
        runtime = _get_runtime()
        result = runtime.process_intent(intent.model_dump())

        governance = GovernanceResult(
            intent_hash=result["intent_hash"],
            tarl_version=result["tarl_version"],
            votes=[PillarVote(**v) for v in result["votes"]],
            final_verdict=result["final_verdict"],
            timestamp=result["timestamp"],
        )

        return IntentResponse(
            message=f"Intent evaluated: {governance.final_verdict}",
            governance=governance,
        )

    @application.get("/audit", response_model=AuditResponse)
    async def get_audit(limit: int = Query(default=50, ge=1, le=500)):
        """Query audit records from the PSIA DurableLedger."""
        runtime = _get_runtime()
        data = runtime.get_audit_records(limit=limit)

        return AuditResponse(
            tarl_version=data["tarl_version"],
            tarl_signature=data["tarl_signature"],
            records=[AuditRecord(**r) for r in data["records"]],
        )

    @application.get("/tarl", response_model=TarlResponse)
    async def get_tarl():
        """Get current TARL protection rules — consumed by TARL page."""
        runtime = _get_runtime()
        data = runtime.get_tarl_rules()

        return TarlResponse(
            version=data["version"],
            rules=[TarlRule(**r) for r in data["rules"]],
        )

    return application


# Module-level app instance for uvicorn
app = create_app()


__all__ = ["app", "create_app"]
