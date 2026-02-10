"""
Temporal Activities for Triumvirate System

Deterministic activity wrappers for the Triumvirate AI pipeline.
All activities follow Temporal best practices for determinism.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def run_triumvirate_pipeline(request: dict) -> dict:
    """
    Run the complete Triumvirate pipeline as a Temporal activity.

    This is the main activity that executes the Triumvirate processing.
    It's deterministic and suitable for Temporal workflows.

    Args:
        request: Dictionary with:
            - input_data: Input to process
            - context: Optional context dict
            - skip_validation: Optional boolean

    Returns:
        Processing result dictionary
    """
    activity.logger.info("Starting Triumvirate pipeline activity")

    try:
        # Import here to avoid top-level imports in activities
        from src.cognition.triumvirate import Triumvirate

        # Extract request parameters
        input_data = request.get("input_data")
        context = request.get("context", {})
        skip_validation = request.get("skip_validation", False)

        # Add activity metadata to context
        context["activity_id"] = activity.info().activity_id
        context["workflow_id"] = activity.info().workflow_id
        context["attempt"] = activity.info().attempt

        # Initialize Triumvirate (cached in workflow worker)
        triumvirate = Triumvirate()

        # Process through pipeline
        result = triumvirate.process(
            input_data=input_data, context=context, skip_validation=skip_validation
        )

        activity.logger.info(
            "Triumvirate pipeline complete: %s", result.get("correlation_id")
        )
        return result

    except Exception as e:
        activity.logger.error("Triumvirate pipeline activity failed: %s", e)
        return {
            "success": False,
            "error": str(e),
            "correlation_id": str(uuid.uuid4()),
        }


@activity.defn
async def validate_input_activity(input_data: Any, context: dict | None = None) -> dict:
    """
    Validate input data through Cerberus engine.

    Args:
        input_data: Data to validate
        context: Optional context

    Returns:
        Validation result
    """
    activity.logger.info("Input validation activity")

    try:
        from src.cognition.cerberus.engine import CerberusEngine

        cerberus = CerberusEngine()
        result = cerberus.validate_input(input_data, context)
        return result

    except Exception as e:
        activity.logger.error("Validation activity failed: %s", e)
        return {"valid": False, "reason": str(e)}


@activity.defn
async def run_codex_inference(input_data: Any, context: dict | None = None) -> dict:
    """
    Run ML inference through Codex engine.

    Args:
        input_data: Input for inference
        context: Optional context

    Returns:
        Inference result
    """
    activity.logger.info("Codex inference activity")

    try:
        from src.cognition.codex.engine import CodexEngine

        codex = CodexEngine()
        result = codex.process(input_data, context)
        return result

    except Exception as e:
        activity.logger.error("Codex activity failed: %s", e)
        return {"success": False, "error": str(e)}


@activity.defn
async def run_galahad_reasoning(inputs: list, context: dict | None = None) -> dict:
    """
    Run reasoning through Galahad engine.

    Args:
        inputs: List of inputs to reason over
        context: Optional context

    Returns:
        Reasoning result
    """
    activity.logger.info("Galahad reasoning activity with %s inputs", len(inputs))

    try:
        from src.cognition.galahad.engine import GalahadEngine

        galahad = GalahadEngine()
        result = galahad.reason(inputs, context)
        return result

    except Exception as e:
        activity.logger.error("Galahad activity failed: %s", e)
        return {"success": False, "error": str(e)}


@activity.defn
async def enforce_output_policy(output_data: Any, context: dict | None = None) -> dict:
    """
    Enforce output policies through Cerberus engine.

    Args:
        output_data: Output to enforce policies on
        context: Optional context

    Returns:
        Enforcement result
    """
    activity.logger.info("Output enforcement activity")

    try:
        from src.cognition.cerberus.engine import CerberusEngine

        cerberus = CerberusEngine()
        result = cerberus.enforce_output(output_data, context)
        return result

    except Exception as e:
        activity.logger.error("Enforcement activity failed: %s", e)
        return {"allowed": False, "reason": str(e)}


@activity.defn
async def record_telemetry(event_type: str, payload: dict) -> bool:
    """
    Record telemetry event for monitoring.

    Args:
        event_type: Type of event
        payload: Event data

    Returns:
        True if recorded successfully
    """
    activity.logger.info("Recording telemetry: %s", event_type)

    try:
        # In production, this would send to monitoring system
        # For now, just log it
        telemetry_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
            "workflow_id": activity.info().workflow_id,
            "activity_id": activity.info().activity_id,
        }

        activity.logger.debug("Telemetry: %s", json.dumps(telemetry_data))
        return True

    except Exception as e:
        activity.logger.error("Telemetry recording failed: %s", e)
        return False


# Export all activities
__all__ = [
    "run_triumvirate_pipeline",
    "validate_input_activity",
    "run_codex_inference",
    "run_galahad_reasoning",
    "enforce_output_policy",
    "record_telemetry",
]
