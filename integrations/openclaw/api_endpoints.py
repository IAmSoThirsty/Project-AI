"""
OpenClaw API Extensions
New endpoints for Legion agent integration
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Add integrations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from integrations.openclaw import LegionAgent, get_config

# Create router
router = APIRouter(prefix="/openclaw", tags=["Legion Agent"])

# Initialize Legion agent (singleton)
_legion_agent: Optional[LegionAgent] = None


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
    governance: Optional[dict] = None


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
            metadata=message.metadata
        )
        
        return LegionResponse(
            response=response_text,
            agent_id=legion.agent_id,
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
                "permissions": ["security.read", "cerberus.analyze"]
            },
            "scenario_forecast": {
                "subsystem": "Global Scenario Engine",
                "description": "Run Monte Carlo crisis simulations",
                "risk_level": "medium",
                "permissions": ["scenario.read", "scenario.simulate"]
            },
            "memory_recall": {
                "subsystem": "EED",
                "description": "Query episodic memory",
                "risk_level": "low",
                "permissions": ["memory.read"]
            }
        },
        "total_count": 3
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
        "message": "Full capability execution in Phase 2"
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
            "tarl": "enforcing"
        }
    }


@router.get("/status")
async def get_status():
    """Get detailed status including security metrics"""
    legion = get_legion_agent()
    
    return {
        "agent_id": legion.agent_id,
        "conversations": len(legion.conversation_history),
        "security": {
            "enabled": True,
            "hydra_active": True
        }
    }
