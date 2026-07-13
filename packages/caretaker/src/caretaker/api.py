"""
caretaker.api — FastAPI server exposing the full governance pipeline.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/api.py``. Unlike upstream, importing this module
does NOT construct a default app (no import-time side effects); call
:func:`create_app` explicitly (or use ``caretaker serve``).

POST /chat/ runs the pipeline; GET /health/, /ledger/{id},
/continuity/{id}, /session/{id} expose runtime state.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from caretaker.providers.base import InferenceProvider
from caretaker.providers.mock import MockProvider
from caretaker.runtime import GovernanceRequest, GovernanceRuntime
from caretaker.system_prompt import SystemPromptBuilder


class ChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1)
    session_id: str = "default"
    context: list[dict[str, str]] | None = None


class ChatResponse(BaseModel):
    text: str
    decision: str
    theta: float
    caki: float
    c_r: float
    reweighted: bool
    triumvirate_votes: list[str]
    faults: list[str]
    policy_reasons: list[str]
    session_id: str
    ledger_index: int


class HealthResponse(BaseModel):
    provider: str
    healthy: bool
    exposes_logits: bool


class LedgerResponse(BaseModel):
    session_id: str
    length: int
    chain_valid: bool
    entries: list[dict[str, Any]]


class ContinuityResponse(BaseModel):
    session_id: str
    length: int
    chain_valid: bool
    lineage: list[str]


class SessionResponse(BaseModel):
    session_id: str
    created_at: float
    message_count: int
    last_decision: str
    last_theta: float
    continuity_length: int
    ledger_length: int
    integrity_valid: bool


def create_app(provider: InferenceProvider | None = None) -> FastAPI:
    """Create a FastAPI app with the given (or default Mock) provider."""
    app = FastAPI(title="Caretaker", version="0.2.0")

    if provider is None:
        provider = MockProvider()

    runtime = GovernanceRuntime(provider=provider)
    prompt_builder = SystemPromptBuilder()

    app.state.runtime = runtime
    app.state.provider = provider
    app.state.prompt_builder = prompt_builder

    @app.post("/chat/", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        system_prompt = prompt_builder.build_prompt(runtime.policy.get_context())
        request = GovernanceRequest(
            user_message=req.user_message,
            system_prompt=system_prompt,
            session_id=req.session_id,
            context=req.context,
        )
        response = runtime.govern(request)
        return ChatResponse(
            text=response.text,
            decision=response.decision,
            theta=response.theta,
            caki=response.caki,
            c_r=response.c_r,
            reweighted=response.reweighted,
            triumvirate_votes=response.triumvirate_votes,
            faults=response.faults,
            policy_reasons=response.policy_reasons,
            session_id=response.session_id,
            ledger_index=response.ledger_index,
        )

    @app.get("/health/", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            provider=provider.name,
            healthy=provider.health_check(),
            exposes_logits=provider.exposes_logits,
        )

    @app.get("/ledger/{session_id}", response_model=LedgerResponse)
    async def get_ledger(session_id: str) -> LedgerResponse:
        session = runtime.get_session(session_id)
        return LedgerResponse(
            session_id=session_id,
            length=session.ledger.length,
            chain_valid=session.ledger.verify_chain(),
            entries=session.ledger.to_dict_list(),
        )

    @app.get("/continuity/{session_id}", response_model=ContinuityResponse)
    async def get_continuity(session_id: str) -> ContinuityResponse:
        session = runtime.get_session(session_id)
        return ContinuityResponse(
            session_id=session_id,
            length=session.continuity.length,
            chain_valid=session.continuity.verify_chain(),
            lineage=session.continuity.lineage(),
        )

    @app.get("/session/{session_id}", response_model=SessionResponse)
    async def get_session_info(session_id: str) -> SessionResponse:
        session = runtime.get_session(session_id)
        return SessionResponse(**session.state_dict())

    return app


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ContinuityResponse",
    "HealthResponse",
    "LedgerResponse",
    "SessionResponse",
    "create_app",
]
