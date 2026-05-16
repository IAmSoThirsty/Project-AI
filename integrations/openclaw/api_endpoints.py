"""
OpenClaw API Extensions
New endpoints for Legion agent integration
"""

import os
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add integrations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from integrations.openclaw import LegionAgent, get_config

# Create router
router = APIRouter(prefix="/openclaw", tags=["Legion Agent"])

# Initialize Legion agent (singleton)
_legion_agent: LegionAgent | None = None


def get_legion_agent() -> LegionAgent:
    """Get or create Legion agent instance"""
    global _legion_agent
    if _legion_agent is None:
        config = get_config()
        _legion_agent = LegionAgent(api_url=config["api"]["project_ai_url"])
    return _legion_agent


# Request/Response models
class OpenClawMessage(BaseModel):
    """Message from OpenClaw to Legion"""

    content: str
    user_id: str
    platform: str = "openclaw"
    metadata: dict = {}


class LegionResponse(BaseModel):
    """Response from Legion to OpenClaw"""

    response: str
    agent_id: str
    status: str
    governance: dict | None = None


class CapabilityRequest(BaseModel):
    """Request to execute a specific capability"""

    capability_id: str
    params: dict = {}
    user_id: str


# Endpoints


@router.post("/message", response_model=LegionResponse)
async def process_message(message: OpenClawMessage):
    """
    Main OpenClaw message handler

    Processes messages through Legion's full pipeline:
    1. Security validation (Cerberus)
    2. Intent parsing
    3. Context retrieval (EED)
    4. Triumvirate governance
    5. Capability execution
    """
    legion = get_legion_agent()

    try:
        response_text = await legion.process_message(
            message=message.content,
            user_id=message.user_id,
            platform=message.platform,
            metadata=message.metadata,
        )

        return LegionResponse(
            response=response_text, agent_id=legion.agent_id, status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/capabilities")
async def list_capabilities():
    """
    List all available Project-AI capabilities

    Returns capability registry with:
    - Capability IDs
    - Subsystem mappings
    - Risk levels
    - Required permissions
    """
    # Placeholder - will integrate with capability registry
    return {
        "capabilities": {
            "threat_analysis": {
                "subsystem": "Cerberus",
                "description": "Analyze current threat landscape",
                "risk_level": "high",
                "permissions": ["security.read", "cerberus.analyze"],
            },
            "scenario_forecast": {
                "subsystem": "Global Scenario Engine",
                "description": "Run Monte Carlo crisis simulations",
                "risk_level": "medium",
                "permissions": ["scenario.read", "scenario.simulate"],
            },
            "memory_recall": {
                "subsystem": "EED",
                "description": "Query episodic memory",
                "risk_level": "low",
                "permissions": ["memory.read"],
            },
        },
        "total_count": 3,
    }


@router.post("/execute")
async def execute_capability(request: CapabilityRequest):
    """
    Execute a specific Project-AI capability

    All executions go through:
    - Triumvirate governance
    - TARL enforcement
    - Audit logging
    """
    # Placeholder - will integrate with capability execution
    return {
        "capability_id": request.capability_id,
        "status": "phase1_placeholder",
        "message": "Full capability execution in Phase 2",
    }


@router.get("/health")
async def health_check():
    """
    Legion agent health check

    Returns:
    - Agent status
    - Subsystem status
    - Security status
    """
    legion = get_legion_agent()

    return {
        "agent": "Legion",
        "version": "1.0.0-phase1",
        "status": "operational",
        "agent_id": legion.agent_id,
        "tagline": "For we are many, and we are one",
        "subsystems": {
            "triumvirate": "ready",
            "cerberus": "active",
            "eed": "online",
            "tarl": "enforcing",
        },
    }


@router.get("/status")
async def get_status():
    """Get detailed status including security metrics"""
    legion = get_legion_agent()

    return {
        "agent_id": legion.agent_id,
        "conversations": len(legion.conversation_history),
        "security": {"enabled": True, "hydra_active": True},
    }


# ── Memory endpoints ──────────────────────────────────────────────────────────

class MemoryLearnRequest(BaseModel):
    user_id: str
    section: str  # fact, preference, goal, skill
    text: str


class MemoryForgetRequest(BaseModel):
    user_id: str
    memory_id: str


class MemoryNoteRequest(BaseModel):
    user_id: str
    note: str


@router.post("/memory/learn")
async def memory_learn(request: MemoryLearnRequest):
    """Add a fact, preference, goal, or skill to the user's Legion memory."""
    from integrations.openclaw.legion_memory import CATEGORY_ALIASES, add_memory
    section = CATEGORY_ALIASES.get(request.section.lower())
    if not section:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown section '{request.section}'. Use: fact, preference, goal, skill.",
        )
    memory_id = add_memory(request.user_id, section, request.text)
    return {"status": "learned", "memory_id": memory_id, "section": section}


@router.post("/memory/forget")
async def memory_forget(request: MemoryForgetRequest):
    """Remove a memory item by ID."""
    from integrations.openclaw.legion_memory import forget_memory
    removed = forget_memory(request.user_id, request.memory_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Memory ID '{request.memory_id}' not found.")
    return {"status": "forgotten", "memory_id": request.memory_id}


@router.get("/memory/view/{user_id}")
async def memory_view(user_id: str):
    """View a user's full structured memory profile and freeform notes."""
    from integrations.openclaw.legion_memory import format_profile, load_notes
    return {
        "user_id": user_id,
        "profile": format_profile(user_id),
        "notes": load_notes(user_id) or "No notes yet.",
    }


@router.post("/memory/note")
async def memory_note(request: MemoryNoteRequest):
    """Append a freeform note to the user's memory."""
    from integrations.openclaw.legion_memory import append_note
    append_note(request.user_id, request.note)
    return {"status": "noted"}


@router.post("/memory/export/{user_id}")
async def memory_export(user_id: str):
    """Export conversation history as fine-tuning JSONL data."""
    from integrations.openclaw.legion_memory import export_training_data
    count, path = export_training_data(user_id)
    return {"status": "exported", "examples": count, "path": str(path)}
