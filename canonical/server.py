#!/usr/bin/env python3
"""
Canonical Scenario HTTP Server - External Validation Interface

This server exposes the canonical scenario as an HTTP API, allowing external
parties to verify Project-AI's claims and validate system behavior.

Endpoints:
- POST /run-canonical: Execute canonical scenario, return red/green status
- GET /health: Health check
- GET /metrics: System metrics

Usage:
    python canonical/server.py
    # or
    uvicorn canonical.server:app --host 0.0.0.0 --port 8000

External Access:
    curl -X POST https://project-ai.example.com/run-canonical
    # Returns: {"status": "pass", "trace_hash": "sha256:...", "artifacts": {...}}
"""

import hashlib
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CANONICAL_DIR = PROJECT_ROOT / "canonical"
REPLAY_SCRIPT = CANONICAL_DIR / "replay.py"
TRACE_FILE = CANONICAL_DIR / "execution_trace.json"

# Initialize FastAPI app
app = FastAPI(
    title="Project-AI Canonical Validator",
    description="External validation interface for Project-AI's canonical scenario",
    version="1.0.0",
)

# Global metrics
metrics = {
    "total_executions": 0,
    "passed_executions": 0,
    "failed_executions": 0,
    "last_execution_timestamp": None,
    "last_execution_status": None,
    "last_execution_duration_ms": None,
}


def compute_trace_hash(trace_data: dict[str, Any]) -> str:
    """Compute SHA-256 hash of execution trace."""
    # Normalize trace for consistent hashing
    trace_json = json.dumps(trace_data, sort_keys=True).encode()
    return hashlib.sha256(trace_json).hexdigest()


def execute_canonical_scenario() -> dict[str, Any]:
    """
    Execute the canonical scenario and return results.

    Returns:
        dict: Execution results including status, trace, and artifacts
    """
    start_time = time.time()

    try:
        # Execute replay.py
        result = subprocess.run(
            [sys.executable, str(REPLAY_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        duration_ms = (time.time() - start_time) * 1000

        # Check exit code
        passed = result.returncode == 0

        # Load execution trace
        trace_data = {}
        if TRACE_FILE.exists():
            with open(TRACE_FILE) as f:
                trace_data = json.load(f)

        # Compute trace hash
        trace_hash = compute_trace_hash(trace_data) if trace_data else None

        # Extract key metrics
        success_criteria_met = (
            trace_data.get("outcome", {}).get("all_criteria_met", False)
        )

        invariants_summary = trace_data.get("invariants", {}).get("summary", {})
        invariants_passed = invariants_summary.get("passed", 0)
        invariants_total = invariants_summary.get("total", 0)
        invariants_pass_rate = invariants_summary.get("pass_rate", 0.0)

        # Update global metrics
        metrics["total_executions"] += 1
        if passed:
            metrics["passed_executions"] += 1
        else:
            metrics["failed_executions"] += 1
        metrics["last_execution_timestamp"] = datetime.now(UTC).isoformat()
        metrics["last_execution_status"] = "pass" if passed else "fail"
        metrics["last_execution_duration_ms"] = duration_ms

        return {
            "status": "pass" if passed else "fail",
            "exit_code": result.returncode,
            "duration_ms": duration_ms,
            "trace_hash": trace_hash,
            "metrics": {
                "success_criteria": {
                    "all_met": success_criteria_met,
                },
                "invariants": {
                    "passed": invariants_passed,
                    "total": invariants_total,
                    "pass_rate": invariants_pass_rate,
                },
            },
            "artifacts": {
                "trace": trace_data,
                "stdout": result.stdout[-2000:] if result.stdout else "",  # Last 2KB
                "stderr": result.stderr[-2000:] if result.stderr else "",  # Last 2KB
            },
        }

    except subprocess.TimeoutExpired:
        metrics["total_executions"] += 1
        metrics["failed_executions"] += 1
        metrics["last_execution_timestamp"] = datetime.now(UTC).isoformat()
        metrics["last_execution_status"] = "timeout"
        metrics["last_execution_duration_ms"] = (time.time() - start_time) * 1000

        return {
            "status": "fail",
            "exit_code": -1,
            "duration_ms": (time.time() - start_time) * 1000,
            "error": "Execution timeout (30s)",
            "artifacts": {},
        }

    except Exception as e:
        metrics["total_executions"] += 1
        metrics["failed_executions"] += 1
        metrics["last_execution_timestamp"] = datetime.now(UTC).isoformat()
        metrics["last_execution_status"] = "error"
        metrics["last_execution_duration_ms"] = (time.time() - start_time) * 1000

        return {
            "status": "fail",
            "exit_code": -1,
            "duration_ms": (time.time() - start_time) * 1000,
            "error": str(e),
            "artifacts": {},
        }


@app.post("/run-canonical")
async def run_canonical(request: Request) -> JSONResponse:
    """
    Execute the canonical scenario and return results.

    Returns:
        JSONResponse: Execution results with status, trace hash, and artifacts

    Example:
        curl -X POST http://localhost:8000/run-canonical
        {
            "status": "pass",
            "trace_hash": "sha256:abc123...",
            "duration_ms": 42.5,
            "metrics": {...},
            "artifacts": {...}
        }
    """
    # Execute scenario
    result = execute_canonical_scenario()

    # Return results
    status_code = 200 if result["status"] == "pass" else 500

    return JSONResponse(content=result, status_code=status_code)


@app.get("/health")
async def health() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        dict: Health status and basic system info
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
        "replay_script": str(REPLAY_SCRIPT.exists()),
        "trace_file": str(TRACE_FILE.exists()),
    }


@app.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """
    System metrics endpoint.

    Returns:
        dict: Execution metrics and statistics
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "metrics": metrics,
        "derived": {
            "pass_rate": (
                metrics["passed_executions"] / metrics["total_executions"]
                if metrics["total_executions"] > 0
                else 0.0
            ),
            "fail_rate": (
                metrics["failed_executions"] / metrics["total_executions"]
                if metrics["total_executions"] > 0
                else 0.0
            ),
        },
    }


@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint with API documentation.

    Returns:
        dict: API information and available endpoints
    """
    return {
        "name": "Project-AI Canonical Validator",
        "version": "1.0.0",
        "description": "External validation interface for Project-AI's canonical scenario",
        "endpoints": {
            "POST /run-canonical": "Execute canonical scenario and return results",
            "GET /health": "Health check",
            "GET /metrics": "Execution metrics",
            "GET /": "This documentation",
        },
        "usage": {
            "curl": "curl -X POST http://localhost:8000/run-canonical",
            "python": 'requests.post("http://localhost:8000/run-canonical")',
        },
        "documentation": "/docs (Swagger UI) or /redoc (ReDoc)",
    }


def main():
    """Run the server using uvicorn."""
    import uvicorn

    print("=" * 80)
    print("🚀 PROJECT-AI CANONICAL VALIDATOR SERVER")
    print("=" * 80)
    print()
    print("Starting server on http://0.0.0.0:8000")
    print()
    print("Available endpoints:")
    print("  POST /run-canonical  - Execute canonical scenario")
    print("  GET  /health         - Health check")
    print("  GET  /metrics        - Execution metrics")
    print("  GET  /               - API documentation")
    print("  GET  /docs           - Swagger UI")
    print()
    print("Example usage:")
    print("  curl -X POST http://localhost:8000/run-canonical")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
