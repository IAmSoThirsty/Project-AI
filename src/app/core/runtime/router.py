"""
Runtime Router: Multi-path coordination layer.

Ensures all execution paths (web/desktop/CLI/agents) flow through
the same governance pipeline and AI orchestrator.

NOT a single entrypoint - preserves all sovereign paths.
IS a shared coordination layer for governance alignment.
"""

from __future__ import annotations

import logging
from datetime import UTC
from typing import Any, Literal

logger = logging.getLogger(__name__)

ExecutionSource = Literal["web", "desktop", "cli", "agent", "temporal", "test"]


def route_request(source: ExecutionSource, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Route requests from any execution path through governance pipeline.

    Architecture:
        Interface → Router → Governance → AI Orchestrator → Systems → State

    Args:
        source: Execution path identifier (web/desktop/cli/agent/test)
        payload: Request data with:
            - action: str - Action to perform
            - context: dict - Execution context
            - user: dict - User information (optional)
            - config: dict - Configuration overrides (optional)

    Returns:
        dict: Response with:
            - status: str - success/error/blocked
            - result: Any - Action result
            - metadata: dict - Execution metadata (logs, timing, etc.)

    Raises:
        RuntimeError: If governance pipeline rejects the request
    """
    logger.info(f"Routing request from {source}: {payload.get('action', 'unknown')}")

    # Build execution context with source metadata
    context = {
        "source": source,
        "payload": payload,
        "action": payload.get("action", ""),
        "user": payload.get("user", {}),
        "config": payload.get("config", {}),
        "timestamp": _get_timestamp(),
    }

    try:
        # Import governance pipeline (lazy to avoid circular imports)
        from app.core.governance.pipeline import enforce_pipeline

        # IRON_PATH_2_PHASE_1_ANNOTATION_ONLY
        # IRON_PATH_2_STOP_CONDITION: runtime router pipeline authority fragment
        # Current behavior: runtime router sends requests to governance.pipeline.enforce_pipeline(), which is a parallel path from execution_router.py.
        # Required before Phase 2+: Use a caller-map-driven consolidation so router traffic reaches the canonical ExecutionGate lifecycle or is explicitly classified as non-authoritative.
        # Do not change behavior in Phase 1.
        # Route through governance → AI orchestrator → systems
        result = enforce_pipeline(context)

        return {
            "status": "success",
            "result": result,
            "metadata": {
                "source": source,
                "action": context["action"],
                "timestamp": context["timestamp"],
            },
        }

    except Exception as e:
        logger.error(f"Request routing failed for {source}: {e}")
        return {
            "status": "error",
            "result": None,
            "error": str(e),
            "metadata": {
                "source": source,
                "action": context.get("action", "unknown"),
                "timestamp": context["timestamp"],
            },
        }


def _get_timestamp() -> str:
    """Get ISO 8601 timestamp for request tracking."""
    from datetime import datetime

    return datetime.now(UTC).isoformat()
