"""FastAPI REST API for Sovereign War Room.

Provides HTTP endpoints for running scenarios, viewing results,
and managing the competition.

Architectural notes (port from legacy):

The legacy implementation imports `SovereignWarRoom` from
`.core` at module load time. The Beginnings port defers the
core dependency using a factory pattern: `app` and `swr` are
module-level placeholders, and `set_swr(swr_instance)` sets
the actual implementation. This allows the api module to be
imported even when core is not yet ported.

The api exposes 13 endpoints:
  - GET  /                       (root)
  - GET  /health                 (health check)
  - POST /scenarios/load         (load scenarios, optional filter)
  - GET  /scenarios/{id}         (get scenario by id)
  - POST /scenarios/{id}/execute (execute scenario with response)
  - GET  /results                (list results, optional filter)
  - GET  /results/{id}/verify    (verify result integrity)
  - GET  /leaderboard            (top systems)
  - GET  /systems/{id}/performance (per-system metrics)
  - GET  /scenarios/{id}/statistics (per-scenario statistics)
  - GET  /governance/audit-log   (governance audit log)
  - GET  /proofs/{id}            (proof + verification)
  - POST /export                 (export results)

The api expects fastapi, pydantic, and uvicorn to be
installed (all available in the Beginnings venv).
"""

from __future__ import annotations

from typing import Any

import uvicorn
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Request/Response models ───────────────────────


class AISystemResponse(BaseModel):
    """AI system response to scenario."""

    decision: str
    reasoning: dict[str, Any] | None = None
    confidence: float | None = None
    constraints_satisfied: bool | None = None
    internal_state: dict[str, Any] | None = None


class ExecuteScenarioRequest(BaseModel):
    """Request to execute a scenario."""

    scenario_id: str
    system_id: str
    response: AISystemResponse


class LoadScenariosRequest(BaseModel):
    """Request to load scenarios."""

    round_number: int | None = None
    scenario_type: str | None = None
    difficulty: int | None = None


# ── App factory + module-level placeholders ──────────

# Module-level placeholders. The actual SovereignWarRoom
# instance is set via set_swr() before the api serves.
# This defers the core import so api can be imported
# independently of core.
swr: Any = None


def create_app(swr_instance: Any | None = None) -> FastAPI:
    """Create the FastAPI app with an injected SWR instance.

    Args:
        swr_instance: Optional SovereignWarRoom-compatible
            instance. If not provided, the app uses the
            module-level `swr` placeholder.

    Returns:
        Configured FastAPI app.
    """
    if swr_instance is not None:
        set_swr(swr_instance)

    app = FastAPI(
        title="SOVEREIGN WAR ROOM API",
        description="AI Governance Testing Framework API",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _get_swr() -> Any:
        """Return the configured SWR instance, or raise 503."""
        if swr is None:
            raise HTTPException(
                status_code=503,
                detail="SovereignWarRoom not configured. Call set_swr() before serving.",
            )
        return swr

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "name": "SOVEREIGN WAR ROOM API",
            "version": "1.0.0",
            "status": "operational",
        }

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.post("/scenarios/load")
    async def load_scenarios(
        request: LoadScenariosRequest = Body(...),
    ) -> dict[str, Any]:
        """Load scenarios for testing.

        Args:
            request: Load scenarios request with optional filters.

        Returns:
            Dict with count + list of loaded scenarios.
        """
        try:
            instance = _get_swr()
            scenarios = instance.load_scenarios(request.round_number)

            # Filter by type if specified
            if request.scenario_type:
                scenarios = [
                    s
                    for s in scenarios
                    if getattr(s, "scenario_type", None) == request.scenario_type
                ]

            # Filter by difficulty if specified
            if request.difficulty is not None:
                scenarios = [
                    s for s in scenarios if getattr(s, "difficulty", None) == request.difficulty
                ]

            return {
                "count": len(scenarios),
                "scenarios": [_scenario_to_dict(s) for s in scenarios],
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @app.get("/scenarios/{scenario_id}")
    async def get_scenario(scenario_id: str) -> dict[str, Any]:
        """Get scenario by ID.

        Args:
            scenario_id: Scenario identifier.

        Returns:
            Scenario details.

        Raises:
            HTTPException: 404 if scenario not found.
        """
        instance = _get_swr()
        scenario = instance.get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        return _scenario_to_dict(scenario)

    @app.post("/scenarios/{scenario_id}/execute")
    async def execute_scenario(
        scenario_id: str, system_id: str, response: AISystemResponse
    ) -> dict[str, Any]:
        """Execute a scenario with an AI system response.

        Args:
            scenario_id: Scenario identifier.
            system_id: AI system identifier.
            response: AI system response.

        Returns:
            Execution results.

        Raises:
            HTTPException: 404 if scenario not found, 500 on
                execution error.
        """
        instance = _get_swr()
        scenario = instance.get_scenario(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        try:
            result = instance.execute_scenario(scenario, response.model_dump(), system_id)
            return result  # type: ignore[no-any-return]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.get("/results")
    async def get_results(
        system_id: str | None = None, round_number: int | None = None
    ) -> dict[str, Any]:
        """Get execution results.

        Args:
            system_id: Optional filter by system.
            round_number: Optional filter by round.

        Returns:
            Dict with count + list of results.
        """
        instance = _get_swr()
        results = instance.get_results(system_id, round_number)
        return {"count": len(results), "results": list(results)}

    @app.get("/results/{result_id}/verify")
    async def verify_result(result_id: int) -> dict[str, Any]:
        """Verify integrity of a result.

        Args:
            result_id: Index of result to verify.

        Returns:
            Verification status.
        """
        instance = _get_swr()
        results = instance.results
        if result_id >= len(results):
            raise HTTPException(status_code=404, detail="Result not found")
        result = results[result_id]
        is_valid = instance.verify_result_integrity(result)
        return {
            "result_id": result_id,
            "valid": is_valid,
            "scenario_id": result.get("scenario_id"),
            "system_id": result.get("system_id"),
        }

    @app.get("/leaderboard")
    async def get_leaderboard(limit: int = 10) -> dict[str, Any]:
        """Get competition leaderboard.

        Args:
            limit: Maximum entries to return.

        Returns:
            Dict with leaderboard entries.
        """
        instance = _get_swr()
        leaderboard = instance.get_leaderboard()
        return {"leaderboard": leaderboard[:limit]}

    @app.get("/systems/{system_id}/performance")
    async def get_system_performance(system_id: str) -> dict[str, Any]:
        """Get performance metrics for a system.

        Args:
            system_id: System identifier.

        Returns:
            Performance metrics.
        """
        instance = _get_swr()
        performance: dict[str, Any] = instance.scoreboard.get_system_performance(system_id)
        if "error" in performance:
            raise HTTPException(status_code=404, detail=performance["error"])
        return performance

    @app.get("/scenarios/{scenario_id}/statistics")
    async def get_scenario_statistics(scenario_id: str) -> dict[str, Any]:
        """Get statistics for a scenario.

        Args:
            scenario_id: Scenario identifier.

        Returns:
            Scenario statistics.
        """
        instance = _get_swr()
        stats: dict[str, Any] = instance.scoreboard.get_scenario_statistics(scenario_id)
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        return stats

    @app.get("/governance/audit-log")
    async def get_audit_log(limit: int = 100) -> dict[str, Any]:
        """Get governance audit log.

        Args:
            limit: Maximum entries to return.

        Returns:
            Dict with count + list of audit log entries.
        """
        instance = _get_swr()
        audit_log = instance.governance.get_audit_log(limit)
        return {"count": len(audit_log), "entries": audit_log}

    @app.get("/proofs/{proof_id}")
    async def get_proof(proof_id: str, reveal_witness: bool = False) -> dict[str, Any]:
        """Get and optionally verify a proof.

        Args:
            proof_id: Proof identifier.
            reveal_witness: Whether to reveal witness data.

        Returns:
            Dict with proof + verification result.
        """
        instance = _get_swr()
        proof = instance.proof_system.get_proof(proof_id)
        if not proof:
            raise HTTPException(status_code=404, detail="Proof not found")
        verification = instance.proof_system.verify_proof(proof, reveal_witness)
        return {
            "proof": _proof_to_dict(proof),
            "verification": verification,
        }

    @app.post("/export")
    async def export_results(filename: str, format: str = "json") -> dict[str, Any]:
        """Export results to file.

        Args:
            filename: Output filename.
            format: Export format (json, csv).

        Returns:
            Export confirmation.
        """
        try:
            instance = _get_swr()
            filepath = instance.export_results(filename, format)
            return {
                "success": True,
                "filepath": filepath,
                "format": format,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return app


# ── Helpers ─────────────────────────────────────────


def _scenario_to_dict(scenario: Any) -> dict[str, Any]:
    """Convert a scenario object to a JSON-serializable dict.

    Supports both Pydantic-style .model_dump() and
    dataclass-style .to_dict() / __dict__ approaches.
    """
    if hasattr(scenario, "model_dump"):
        result: dict[str, Any] = scenario.model_dump()
        return result
    if hasattr(scenario, "to_dict"):
        return scenario.to_dict()  # type: ignore[no-any-return]
    if hasattr(scenario, "__dict__"):
        return dict(scenario.__dict__)
    return {}


def _proof_to_dict(proof: Any) -> dict[str, Any]:
    """Convert a proof object to a JSON-serializable dict."""
    if hasattr(proof, "model_dump"):
        result: dict[str, Any] = proof.model_dump()
        return result
    if hasattr(proof, "to_dict"):
        return proof.to_dict()  # type: ignore[no-any-return]
    if hasattr(proof, "__dict__"):
        return dict(proof.__dict__)
    return {}


# ── Module-level configuration ─────────────────────


def set_swr(swr_instance: Any) -> None:
    """Set the SovereignWarRoom instance for the api module.

    Args:
        swr_instance: A SovereignWarRoom-compatible object.
    """
    global swr
    swr = swr_instance


def start_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the API server.

    Args:
        host: Host address.
        port: Port number.
    """
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_api()


__all__ = [
    "AISystemResponse",
    "ExecuteScenarioRequest",
    "LoadScenariosRequest",
    "create_app",
    "set_swr",
    "start_api",
]
