"""
Temporal Workflow Governance Integration.

Provides governance wrappers and validation helpers for Temporal workflows
to ensure all workflows route through the unified governance pipeline.
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


async def validate_workflow_execution(
    workflow_type: str,
    request: dict | Any,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Validate workflow execution through governance pipeline.

    This function provides a pre-execution gate for Temporal workflows,
    ensuring all workflows comply with:
        - Four Laws ethics framework
        - Rate limiting policies
        - User authorization
        - Content safety checks
        - Resource quotas

    Args:
        workflow_type: Type identifier (e.g., 'ai_learning', 'crisis_response')
        request: Workflow request data (dataclass or dict)
        context: Additional execution context (user_id, source, etc.)

    Returns:
        dict with:
            - allowed: bool - Whether workflow can proceed
            - reason: str - Explanation if blocked
            - metadata: dict - Governance metadata (rate limits, quotas, etc.)

    Example:
        gate_result = await validate_workflow_execution(
            workflow_type="ai_learning",
            request=learning_request,
            context={"user_id": "user123", "category": "security"}
        )

        if not gate_result["allowed"]:
            return LearningResult(success=False, error=gate_result["reason"])
    """
    logger.info(f"Governance validation for workflow: {workflow_type}")

    context = context or {}

    # Convert dataclass request to dict if needed
    if hasattr(request, "__dict__"):
        request_dict = request.__dict__
    else:
        request_dict = request if isinstance(request, dict) else {}

    # Build governance payload
    from app.core.runtime.router import route_request

    try:
        # Route through governance pipeline (validation + gate phases only)
        result = route_request(
            "temporal",
            {
                "action": f"temporal.workflow.validate",
                "workflow_type": workflow_type,
                "payload": request_dict,
                "user": context.get("user", {}),
                "context": context,
            },
        )

        if result["status"] == "success":
            return {
                "allowed": True,
                "reason": "Governance checks passed",
                "metadata": result.get("metadata", {}),
            }
        else:
            return {
                "allowed": False,
                "reason": result.get("error", "Governance gate blocked request"),
                "metadata": result.get("metadata", {}),
            }

    except PermissionError as e:
        logger.warning(f"Workflow {workflow_type} blocked by governance: {e}")
        return {"allowed": False, "reason": str(e), "metadata": {}}

    except Exception as e:
        logger.error(f"Governance validation failed for {workflow_type}: {e}")
        # Fail closed: deny if governance check fails
        return {
            "allowed": False,
            "reason": f"Governance system error: {str(e)}",
            "metadata": {},
        }


async def audit_workflow_start(
    workflow_type: str,
    workflow_id: str,
    request: dict | Any,
    user_id: str | None = None,
) -> None:
    """
    Audit workflow start event.

    Records workflow initiation in governance audit log.

    Args:
        workflow_type: Workflow type identifier
        workflow_id: Temporal workflow ID
        request: Workflow request data
        user_id: User who initiated the workflow
    """
    import json
    import os

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "workflow_start",
        "workflow_type": workflow_type,
        "workflow_id": workflow_id,
        "user_id": user_id,
        "request_summary": _summarize_request(request),
    }

    try:
        os.makedirs("data/runtime", exist_ok=True)
        with open("data/runtime/workflow_audit.log", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write workflow audit log: {e}")


async def audit_workflow_completion(
    workflow_type: str,
    workflow_id: str,
    status: str,
    result: dict | Any,
    user_id: str | None = None,
    error: str | None = None,
) -> None:
    """
    Audit workflow completion event.

    Records workflow completion (success or failure) in governance audit log.

    Args:
        workflow_type: Workflow type identifier
        workflow_id: Temporal workflow ID
        status: 'completed' or 'failed'
        result: Workflow result data
        user_id: User who initiated the workflow
        error: Error message if failed
    """
    import json
    import os

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "workflow_completion",
        "workflow_type": workflow_type,
        "workflow_id": workflow_id,
        "status": status,
        "user_id": user_id,
        "result_summary": _summarize_request(result),
    }

    if error:
        audit_entry["error"] = error

    try:
        os.makedirs("data/runtime", exist_ok=True)
        with open("data/runtime/workflow_audit.log", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write workflow completion audit: {e}")


def _summarize_request(request: dict | Any, max_length: int = 200) -> dict:
    """
    Create summary of request for audit logging.

    Truncates large values and redacts sensitive fields.

    Args:
        request: Request data (dict or dataclass)
        max_length: Maximum string length per field

    Returns:
        Summarized dict with truncated/redacted values
    """
    # Convert dataclass to dict
    if hasattr(request, "__dict__"):
        request_dict = request.__dict__
    else:
        request_dict = request if isinstance(request, dict) else {}

    # Sensitive fields to redact
    sensitive_fields = [
        "password",
        "token",
        "api_key",
        "secret",
        "private_key",
        "credential",
    ]

    summary = {}
    for key, value in request_dict.items():
        # Redact sensitive fields
        if any(field in key.lower() for field in sensitive_fields):
            summary[key] = "***REDACTED***"
        # Truncate long strings
        elif isinstance(value, str) and len(value) > max_length:
            summary[key] = value[:max_length] + "..."
        # Include other values as-is (up to max_length)
        else:
            summary[key] = str(value)[:max_length] if value is not None else None

    return summary


async def check_workflow_quota(
    workflow_type: str, user_id: str | None = None
) -> dict[str, Any]:
    """
    Check if user has quota available for workflow execution.

    Quota rules (per user per day):
        - ai_learning: 100 workflows/day
        - image_generation: 10 workflows/day
        - data_analysis: 20 workflows/day
        - memory_expansion: 200 workflows/day
        - crisis_response: 5 workflows/day (admin only)

    Args:
        workflow_type: Workflow type identifier
        user_id: User ID (or None for anonymous)

    Returns:
        dict with:
            - allowed: bool - Whether quota available
            - remaining: int - Remaining quota
            - resets_at: str - ISO timestamp when quota resets
    """
    # Quota limits (per day)
    quotas = {
        "ai_learning": 100,
        "image_generation": 10,
        "data_analysis": 20,
        "memory_expansion": 200,
        "crisis_response": 5,
    }

    limit = quotas.get(workflow_type, 50)  # Default: 50/day

    # TODO: Implement persistent quota tracking with Redis
    # For now, return optimistic response
    logger.info(
        f"Quota check for {user_id or 'anonymous'}: "
        f"{workflow_type} (limit: {limit}/day)"
    )

    from datetime import timezone

    next_reset = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    from datetime import timedelta

    next_reset += timedelta(days=1)

    return {
        "allowed": True,  # Optimistic: assume quota available
        "remaining": limit,  # TODO: Calculate actual remaining quota
        "resets_at": next_reset.isoformat(),
        "limit": limit,
    }


async def validate_crisis_authorization(
    target_member: str, user_id: str | None = None, user_role: str | None = None
) -> dict[str, Any]:
    """
    Validate authorization for crisis response workflow.

    Crisis workflows require:
        - Admin role
        - Valid target member
        - No active crisis for same target

    Args:
        target_member: Target member ID for crisis response
        user_id: User initiating crisis
        user_role: User role (must be 'admin')

    Returns:
        dict with:
            - allowed: bool - Whether crisis can be initiated
            - reason: str - Explanation if blocked
    """
    logger.info(f"Crisis authorization check: target={target_member}, user={user_id}")

    # Check 1: Admin role required
    if user_role != "admin":
        return {
            "allowed": False,
            "reason": f"Crisis response requires admin role (user has: {user_role})",
        }

    # Check 2: Valid target member
    if not target_member or len(target_member) < 3:
        return {"allowed": False, "reason": "Invalid target member ID"}

    # Check 3: No duplicate active crisis for same target
    # TODO: Check for existing active crisis in Temporal
    # For now, allow (optimistic)

    return {"allowed": True, "reason": "Crisis authorization passed"}


# Export public API
__all__ = [
    "validate_workflow_execution",
    "audit_workflow_start",
    "audit_workflow_completion",
    "check_workflow_quota",
    "validate_crisis_authorization",
]
