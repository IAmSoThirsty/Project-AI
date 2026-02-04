"""
FastAPI REST API for SOVEREIGN WAR ROOM

Provides HTTP endpoints for running scenarios, viewing results,
and managing the competition.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uvicorn

from .core import SovereignWarRoom
from .scenario import ScenarioType, DifficultyLevel


# Request/Response models
class AISystemResponse(BaseModel):
    """AI system response to scenario."""
    decision: str
    reasoning: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    constraints_satisfied: Optional[bool] = None
    internal_state: Optional[Dict[str, Any]] = None


class ExecuteScenarioRequest(BaseModel):
    """Request to execute a scenario."""
    scenario_id: str
    system_id: str
    response: AISystemResponse


class LoadScenariosRequest(BaseModel):
    """Request to load scenarios."""
    round_number: Optional[int] = None
    scenario_type: Optional[ScenarioType] = None
    difficulty: Optional[DifficultyLevel] = None


# Create FastAPI app
app = FastAPI(
    title="SOVEREIGN WAR ROOM API",
    description="AI Governance Testing Framework API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SOVEREIGN WAR ROOM
swr = SovereignWarRoom()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SOVEREIGN WAR ROOM API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/scenarios/load")
async def load_scenarios(request: LoadScenariosRequest = Body(...)):
    """
    Load scenarios for testing.
    
    Args:
        request: Load scenarios request
        
    Returns:
        List of loaded scenarios
    """
    try:
        scenarios = swr.load_scenarios(request.round_number)
        
        # Filter by type if specified
        if request.scenario_type:
            scenarios = [s for s in scenarios if s.scenario_type == request.scenario_type]
        
        # Filter by difficulty if specified
        if request.difficulty:
            scenarios = [s for s in scenarios if s.difficulty == request.difficulty]
        
        return {
            "count": len(scenarios),
            "scenarios": [s.model_dump() for s in scenarios]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """
    Get scenario by ID.
    
    Args:
        scenario_id: Scenario identifier
        
    Returns:
        Scenario details
    """
    scenario = swr.get_scenario(scenario_id)
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    return scenario.model_dump()


@app.post("/scenarios/{scenario_id}/execute")
async def execute_scenario(
    scenario_id: str,
    system_id: str,
    response: AISystemResponse
):
    """
    Execute a scenario with AI system response.
    
    Args:
        scenario_id: Scenario identifier
        system_id: AI system identifier
        response: AI system response
        
    Returns:
        Execution results
    """
    scenario = swr.get_scenario(scenario_id)
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        result = swr.execute_scenario(
            scenario,
            response.model_dump(),
            system_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results")
async def get_results(
    system_id: Optional[str] = None,
    round_number: Optional[int] = None
):
    """
    Get execution results.
    
    Args:
        system_id: Optional filter by system
        round_number: Optional filter by round
        
    Returns:
        List of results
    """
    results = swr.get_results(system_id, round_number)
    return {"count": len(results), "results": results}


@app.get("/results/{result_id}/verify")
async def verify_result(result_id: int):
    """
    Verify integrity of a result.
    
    Args:
        result_id: Index of result to verify
        
    Returns:
        Verification status
    """
    if result_id >= len(swr.results):
        raise HTTPException(status_code=404, detail="Result not found")
    
    result = swr.results[result_id]
    is_valid = swr.verify_result_integrity(result)
    
    return {
        "result_id": result_id,
        "valid": is_valid,
        "scenario_id": result["scenario_id"],
        "system_id": result["system_id"]
    }


@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """
    Get competition leaderboard.
    
    Args:
        limit: Maximum entries to return
        
    Returns:
        Leaderboard entries
    """
    leaderboard = swr.get_leaderboard()
    return {"leaderboard": leaderboard[:limit]}


@app.get("/systems/{system_id}/performance")
async def get_system_performance(system_id: str):
    """
    Get performance metrics for a system.
    
    Args:
        system_id: System identifier
        
    Returns:
        Performance metrics
    """
    performance = swr.scoreboard.get_system_performance(system_id)
    
    if "error" in performance:
        raise HTTPException(status_code=404, detail=performance["error"])
    
    return performance


@app.get("/scenarios/{scenario_id}/statistics")
async def get_scenario_statistics(scenario_id: str):
    """
    Get statistics for a scenario.
    
    Args:
        scenario_id: Scenario identifier
        
    Returns:
        Scenario statistics
    """
    stats = swr.scoreboard.get_scenario_statistics(scenario_id)
    
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    
    return stats


@app.get("/governance/audit-log")
async def get_audit_log(limit: int = 100):
    """
    Get governance audit log.
    
    Args:
        limit: Maximum entries to return
        
    Returns:
        Audit log entries
    """
    audit_log = swr.governance.get_audit_log(limit)
    return {"count": len(audit_log), "entries": audit_log}


@app.get("/proofs/{proof_id}")
async def get_proof(proof_id: str, reveal_witness: bool = False):
    """
    Get and optionally verify a proof.
    
    Args:
        proof_id: Proof identifier
        reveal_witness: Whether to reveal witness data
        
    Returns:
        Proof and verification result
    """
    proof = swr.proof_system.get_proof(proof_id)
    
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    verification = swr.proof_system.verify_proof(proof, reveal_witness)
    
    return {
        "proof": proof.model_dump(),
        "verification": verification
    }


@app.post("/export")
async def export_results(filename: str, format: str = "json"):
    """
    Export results to file.
    
    Args:
        filename: Output filename
        format: Export format (json, csv)
        
    Returns:
        Export confirmation
    """
    try:
        filepath = swr.export_results(filename, format)
        return {
            "success": True,
            "filepath": filepath,
            "format": format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_api(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the API server.
    
    Args:
        host: Host address
        port: Port number
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()
