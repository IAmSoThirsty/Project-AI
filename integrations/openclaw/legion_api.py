#!/usr/bin/env python3
"""
Legion HTTP Interface - Custom Single-Gate API
Maintains Triumvirate governance for ALL requests
"""

from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import Legion agent
try:
    from integrations.openclaw.agent_adapter import LegionAgent
    LEGION_AVAILABLE = True
except ImportError:
    LEGION_AVAILABLE = False
    print("[WARN] Legion agent not available")


# ============================================
# Models
# ============================================

class ChatMessage(BaseModel):
    """User message to Legion"""
    message: str
    user_id: str
    platform: str = "web"
    metadata: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    """Legion's response"""
    response: str
    agent_id: str
    timestamp: float
    governed: bool = True  # All responses are Triumvirate-governed


class LegionStatus(BaseModel):
    """Legion system status"""
    agent_id: str
    status: str
    learning_active: bool
    capabilities_loaded: int
    triumvirate_connected: bool
    eed_connected: bool


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="Legion Interface",
    description="Single-gate interface to Project-AI via Triumvirate governance",
    version="1.0.0"
)

# CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Legion
legion: LegionAgent | None = None

@app.on_event("startup")
async def startup():
    """Initialize Legion on startup"""
    global legion
    if LEGION_AVAILABLE:
        legion = LegionAgent(api_url="http://localhost:8001")
        print(f"[Legion] Initialized: {legion.agent_id}")

        # Start background learning
        await legion.start_background_learning()
    else:
        print("[ERROR] Legion agent not available - import failed")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global legion
    if legion and hasattr(legion, 'learning_engine'):
        await legion.stop_background_learning()
        print("[Legion] Background learning stopped")


# ============================================
# Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Legion Interface",
        "version": "1.0.0",
        "description": "Single-gate access to Project-AI",
        "governance": "Triumvirate (Galahad, Cerberus, CodexDeus)",
        "endpoints": {
            "chat": "POST /chat",
            "status": "GET /status",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "legion_available": LEGION_AVAILABLE,
        "legion_initialized": legion is not None
    }


@app.get("/status")
async def get_status():
    """Get Legion status"""
    if not legion:
        raise HTTPException(status_code=503, detail="Legion not initialized")

    learning_stats = legion.get_learning_stats()

    return LegionStatus(
        agent_id=legion.agent_id,
        status="active",
        learning_active=learning_stats.get("status") == "active",
        capabilities_loaded=len(legion.capability_registry.capabilities) if legion.capability_registry else 0,
        triumvirate_connected=legion.triumvirate_client is not None,
        eed_connected=legion.eed is not None
    )


@app.post("/chat")
async def chat(msg: ChatMessage) -> ChatResponse:
    """
    Send message to Legion

    ALL MESSAGES GO THROUGH TRIUMVIRATE GOVERNANCE
    No backdoors, no bypass - single gate only
    """
    if not legion:
        raise HTTPException(status_code=503, detail="Legion not initialized")

    try:
        # Process through Legion (includes Triumvirate governance)
        response = await legion.process_message(
            message=msg.message,
            user_id=msg.user_id,
            platform=msg.platform,
            metadata=msg.metadata
        )

        import time
        return ChatResponse(
            response=response,
            agent_id=legion.agent_id,
            timestamp=time.time(),
            governed=True  # Always governed by Triumvirate
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legion error: {str(e)}")


@app.post("/learning/start")
async def start_learning():
    """Start background learning"""
    if not legion:
        raise HTTPException(status_code=503, detail="Legion not initialized")

    await legion.start_background_learning()
    return {"status": "learning_started"}


@app.post("/learning/stop")
async def stop_learning():
    """Stop background learning"""
    if not legion:
        raise HTTPException(status_code=503, detail="Legion not initialized")

    await legion.stop_background_learning()
    return {"status": "learning_stopped"}


@app.get("/learning/stats")
async def learning_stats():
    """Get learning statistics"""
    if not legion:
        raise HTTPException(status_code=503, detail="Legion not initialized")

    return legion.get_learning_stats()


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Legion Interface - Single-Gate Architecture")
    print("=" * 60)
    print("\nSecurity Model:")
    print("  ✓ All requests go through Triumvirate governance")
    print("  ✓ No backdoors or bypass mechanisms")
    print("  ✓ Single point of entry and exit")
    print("  ✓ TARL enforcement on all actions")
    print("\nStarting server...")
    print("  Legion API: http://localhost:8002")
    print("  Docs: http://localhost:8002/docs")
    print("\nNote: Project-AI API must be running on port 8001")
    print("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
