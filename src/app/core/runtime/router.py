"""
Runtime Router: Multi-path coordination layer.

Ensures all execution paths (web/desktop/CLI/agents) flow through
the same governance pipeline and AI orchestrator.

NOT a single entrypoint - preserves all sovereign paths.
IS a shared coordination layer for governance alignment.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)

ExecutionSource = Literal["web", "desktop", "cli", "agent", "test"]


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
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
