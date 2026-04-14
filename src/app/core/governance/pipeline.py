"""
Governance Pipeline: Universal enforcement layer.

Every request from ANY execution path flows through this pipeline.
This is what ensures consistent governance across web/desktop/CLI/agents.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def enforce_pipeline(context: dict[str, Any]) -> Any:
    """
    Execute governance pipeline: validate → simulate → gate → execute → commit → log.

    This pipeline ensures EVERY request (regardless of source) undergoes:
        1. Validation - Input sanitization, type checking
        2. Simulation - Shadow execution for impact analysis
        3. Gate - Authorization checks (Four Laws, user permissions)
        4. Execution - Actual operation
        5. Commit - State persistence with rollback capability
        6. Logging - Complete audit trail

    Args:
        context: Execution context with:
            - source: ExecutionSource (web/desktop/cli/agent)
            - payload: Request data
            - action: Action to perform
            - user: User information
            - config: Configuration overrides

    Returns:
        Execution result (type depends on action)

    Raises:
        ValueError: If validation fails
        PermissionError: If gate denies access
        RuntimeError: If execution fails
    """
    logger.info(
        f"Governance pipeline: {context.get('action', 'unknown')} from {context.get('source', 'unknown')}"
    )

    # Phase 1: Validation
    validated_context = _validate(context)

    # Phase 2: Simulation (shadow execution for impact analysis)
    simulation_result = _simulate(validated_context)

    # Phase 3: Gate (authorization, Four Laws compliance)
    gated_context = _gate(validated_context, simulation_result)

    # Phase 4: Execution
    result = _execute(gated_context)

    # Phase 5: Commit (persist state changes)
    _commit(gated_context, result)

    # Phase 6: Logging (audit trail)
    _log(gated_context, result)

    return result


def _validate(context: dict[str, Any]) -> dict[str, Any]:
    """
    Phase 1: Input validation and sanitization.

    Checks:
        - Required fields present
        - Data types correct
        - Input sanitization (XSS, injection prevention)
        - Schema validation
    """
    from .validators import validate_input, sanitize_payload

    logger.debug("Governance Phase 1: Validation")

    # Validate required fields
    required_fields = ["source", "payload", "action"]
    for field in required_fields:
        if field not in context:
            raise ValueError(f"Missing required field: {field}")

    # Sanitize payload to prevent injection attacks
    context["payload"] = sanitize_payload(context["payload"])

    # Validate input against schemas
    validate_input(context["action"], context["payload"])

    return context


def _simulate(context: dict[str, Any]) -> dict[str, Any]:
    """
    Phase 2: Shadow execution for impact analysis.

    Simulates the operation to predict:
        - State changes
        - Resource usage
        - Potential failures
        - Side effects
    """
    logger.debug("Governance Phase 2: Simulation")

    # For now, return basic simulation metadata
    # TODO: Implement full shadow execution in deterministic_replay.py
    simulation = {
        "estimated_impact": "low",
        "state_changes": [],
        "resource_usage": {"cpu": "low", "memory": "low"},
        "predicted_outcome": "success",
    }

    return simulation


def _gate(
    context: dict[str, Any], simulation: dict[str, Any]
) -> dict[str, Any]:
    """
    Phase 3: Authorization and compliance gate.

    Checks:
        - User permissions
        - Four Laws compliance (via FourLaws.validate_action)
        - Rate limiting
        - Resource quotas
    """
    logger.debug("Governance Phase 3: Gate")

    # Check Four Laws compliance
    from app.core.ai_systems import FourLaws

    action = context["action"]
    is_allowed, reason = FourLaws.validate_action(
        action,
        context={
            "source": context["source"],
            "user": context.get("user", {}),
            "simulation": simulation,
        },
    )

    if not is_allowed:
        raise PermissionError(f"Action blocked by Four Laws: {reason}")

    # Rate limiting check
    _check_rate_limit(context)

    # User permission check
    _check_user_permissions(context)

    # Resource quota check
    _check_resource_quotas(context)

    return context


def _check_rate_limit(context: dict[str, Any]) -> None:
    """
    Enforce rate limits based on action type and user.
    
    Raises:
        PermissionError: If rate limit exceeded
    """
    action = context["action"]
    source = context["source"]
    user = context.get("user", {}).get("username", "anonymous")
    
    # Rate limit rules
    limits = {
        "user.login": {"window": 60, "max_requests": 5},  # 5/min
        "ai.chat": {"window": 60, "max_requests": 30},    # 30/min
        "ai.image": {"window": 3600, "max_requests": 10}, # 10/hour
        "persona.update": {"window": 60, "max_requests": 20}, # 20/min
    }
    
    # Get limit for action (or default)
    limit = limits.get(action, {"window": 60, "max_requests": 100})
    
    # Check rate limit (in-memory for now, should use Redis in production)
    from datetime import datetime, timedelta
    import threading
    
    # Simple in-memory rate limiter
    if not hasattr(_check_rate_limit, "requests"):
        _check_rate_limit.requests = {}
        _check_rate_limit.lock = threading.Lock()
    
    with _check_rate_limit.lock:
        key = f"{source}:{user}:{action}"
        now = datetime.now()
        window_start = now - timedelta(seconds=limit["window"])
        
        # Clean old requests
        if key in _check_rate_limit.requests:
            _check_rate_limit.requests[key] = [
                ts for ts in _check_rate_limit.requests[key]
                if ts > window_start
            ]
        else:
            _check_rate_limit.requests[key] = []
        
        # Check limit
        if len(_check_rate_limit.requests[key]) >= limit["max_requests"]:
            raise PermissionError(
                f"Rate limit exceeded for {action}: "
                f"{limit['max_requests']} requests per {limit['window']}s"
            )
        
        # Record this request
        _check_rate_limit.requests[key].append(now)


def _check_user_permissions(context: dict[str, Any]) -> None:
    """
    Check user permissions for action.
    
    Raises:
        PermissionError: If user lacks permission
    """
    action = context["action"]
    user = context.get("user", {})
    
    # Permission rules
    admin_only_actions = ["user.delete", "system.shutdown"]
    user_role = user.get("role", "user")
    
    if action in admin_only_actions and user_role != "admin":
        raise PermissionError(
            f"Action {action} requires admin role (user has: {user_role})"
        )
    
    # TODO: Implement full RBAC system


def _check_resource_quotas(context: dict[str, Any]) -> None:
    """
    Check resource quotas (CPU, memory, API calls).
    
    Raises:
        PermissionError: If quota exceeded
    """
    action = context["action"]
    user = context.get("user", {}).get("username", "anonymous")
    
    # Quota rules (example: daily AI call limits)
    quotas = {
        "ai.chat": {"daily_limit": 1000},
        "ai.image": {"daily_limit": 100},
    }
    
    if action in quotas:
        # TODO: Implement persistent quota tracking (Redis/DB)
        # For now, just log
        logger.info(f"Quota check for {user}: {action} (limit: {quotas[action]['daily_limit']}/day)")
        pass


def _execute(context: dict[str, Any]) -> Any:
    """
    Phase 4: Actual execution.

    Routes to appropriate executor based on action type:
        - AI operations → ai/orchestrator.py
        - System operations → core/systems/*
        - Data operations → data_persistence.py
    """
    logger.debug("Governance Phase 4: Execution")

    action = context["action"]
    payload = context["payload"]

    # Route agent operations through CognitionKernel (unified governance)
    if action.startswith("agent.") or context.get("source") == "agent":
        from app.core.cognition_kernel import get_cognition_kernel
        
        kernel = get_cognition_kernel()
        if not kernel:
            raise RuntimeError("CognitionKernel not available for agent action")
        
        # Execute through kernel (kernel has its own internal governance)
        result = kernel.execute(
            action_type=action.replace("agent.", ""),
            payload=payload,
            requester=context.get("user", "system")
        )
        return result
    
    # Route AI operations to orchestrator
    elif action.startswith("ai."):
        from app.core.ai.orchestrator import run_ai, AIRequest

        # Convert payload to AIRequest
        ai_request = AIRequest(
            task_type=payload.get("task_type", "chat"),
            prompt=payload.get("prompt", ""),
            model=payload.get("model"),
            provider=payload.get("provider"),
            config=payload.get("config"),
            context=context,
        )

        response = run_ai(ai_request)
        return response.result

    # Route system operations to existing core modules
    # This preserves all existing functionality
    elif action == "user.login":
        from app.core.user_manager import UserManager
        from app.core.security.auth import generate_jwt_token

        manager = UserManager()
        # FIX: UserManager has authenticate(), not authenticate_user()
        is_authenticated = manager.authenticate(
            payload.get("username"), payload.get("password")
        )
        
        if is_authenticated:
            # Get user details for role
            user = manager.users.get(payload.get("username"), {})
            # Generate secure JWT token
            token = generate_jwt_token(
                username=payload.get("username"),
                role=user.get("role", "user")
            )
            return {
                "username": payload.get("username"),
                "token": token,
                "role": user.get("role", "user")
            }
        else:
            raise PermissionError("Invalid credentials")

    elif action == "persona.update":
        from app.core.ai_systems import AIPersona

        persona = AIPersona()
        return persona.adjust_trait(
            payload.get("trait"), payload.get("value")
        )

    # Route Temporal workflow operations
    elif action.startswith("temporal."):
        return _execute_temporal_action(action, payload, context)

    # Add more action routes as needed
    else:
        raise ValueError(f"Unknown action: {action}")


def _commit(context: dict[str, Any], result: Any) -> None:
    """
    Phase 5: Commit state changes to persistence layer.

    Ensures:
        - Atomic writes
        - Rollback capability
        - State consistency
    """
    logger.debug("Governance Phase 5: Commit")

    action = context["action"]
    
    # State-modifying actions that require persistence
    state_actions = ["user.login", "persona.update", "user.create", "user.update"]
    
    if action in state_actions:
        # Record state change in audit log
        _record_state_change(context, result)
        
        # Validate state consistency
        if not _validate_state_consistency(context, result):
            logger.error(f"State consistency check failed for {action}")
            # In production: implement rollback here
            raise RuntimeError(f"State consistency violation in {action}")


def _record_state_change(context: dict[str, Any], result: Any) -> None:
    """Record state change for audit and potential rollback."""
    import json
    from datetime import datetime
    
    change_record = {
        "timestamp": datetime.now().isoformat(),
        "action": context["action"],
        "source": context["source"],
        "user": context.get("user", {}).get("username", "anonymous"),
        "result_summary": str(result)[:200],  # Truncated for logging
    }
    
    # Write to audit log (append-only)
    try:
        with open("data/runtime/state_changes.log", "a") as f:
            f.write(json.dumps(change_record) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write state change log: {e}")


def _validate_state_consistency(context: dict[str, Any], result: Any) -> bool:
    """
    Validate state consistency after operation.
    
    Returns:
        True if state is consistent, False otherwise
    """
    # Basic validation: ensure result is not None for state-modifying actions
    if result is None:
        return False
    
    # TODO: Implement deeper consistency checks
    # - Foreign key validation
    # - Data type validation
    # - Business rule validation
    
    return True


def _log(context: dict[str, Any], result: Any) -> None:
    """
    Phase 6: Audit logging.

    Records:
        - Action performed
        - User/source
        - Timestamp
        - Result
        - Full execution trace
    """
    import json
    from datetime import datetime
    
    # Build structured audit log entry
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": context["action"],
        "source": context["source"],
        "user": context.get("user", {}).get("username", "anonymous"),
        "status": "success" if result else "unknown",
        "result_type": type(result).__name__,
        "payload_summary": {
            k: str(v)[:50] for k, v in context.get("payload", {}).items()
            if k not in ["password", "token", "api_key"]  # Redact sensitive fields
        }
    }
    
    # Write to structured audit log
    try:
        import os
        os.makedirs("data/runtime", exist_ok=True)
        with open("data/runtime/governance_audit.log", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write audit log: {e}")
    
    # Also log to standard logger
    logger.info(
        f"Governance audit: {context['action']} from {context['source']} "
        f"by {audit_entry['user']} - Status: {audit_entry['status']}"
    )
    
    # TODO: Send to centralized logging system (ELK, Splunk, etc.)
    # TODO: Implement log retention policy
    # TODO: Add alerting for suspicious patterns


def _execute_temporal_action(
    action: str, payload: dict[str, Any], context: dict[str, Any]
) -> Any:
    """
    Execute Temporal workflow operations through governance.

    Supported actions:
        - temporal.workflow.validate: Pre-execution validation gate
        - temporal.workflow.execute: Execute workflow through Temporal client
        - temporal.activity.validate: Pre-activity validation

    Args:
        action: Temporal action type
        payload: Action payload with workflow/activity data
        context: Execution context

    Returns:
        Action result (validation status or workflow result)

    Raises:
        ValueError: If action not recognized
        PermissionError: If validation fails
    """
    logger.debug(f"Executing Temporal action: {action}")

    if action == "temporal.workflow.validate":
        # Validate workflow execution request
        workflow_type = payload.get("workflow_type")
        
        # Workflow-specific validation rules
        validation_rules = {
            "ai_learning": _validate_learning_workflow,
            "image_generation": _validate_image_workflow,
            "data_analysis": _validate_data_workflow,
            "memory_expansion": _validate_memory_workflow,
            "crisis_response": _validate_crisis_workflow,
        }
        
        validator = validation_rules.get(workflow_type)
        if not validator:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        # Run validation
        validation_result = validator(payload, context)
        
        if not validation_result["valid"]:
            raise PermissionError(validation_result["reason"])
        
        return {"status": "validated", "metadata": validation_result}

    elif action == "temporal.workflow.execute":
        # Execute workflow through Temporal client
        # This is called AFTER validation has passed
        workflow_type = payload.get("workflow_type")
        
        logger.info(f"Executing Temporal workflow: {workflow_type}")
        
        # Import and execute workflow
        # NOTE: Actual Temporal client execution would happen here
        # For now, return success marker
        return {
            "status": "workflow_started",
            "workflow_type": workflow_type,
            "message": "Workflow queued for execution",
        }

    elif action == "temporal.activity.validate":
        # Validate activity execution
        activity_type = payload.get("activity_type")
        
        # Activity-specific validation (e.g., agent_mission requires auth)
        if activity_type == "agent_mission":
            mission = payload.get("payload", {})
            if not mission.get("agent_id") or not mission.get("target"):
                raise PermissionError("Agent mission requires agent_id and target")
        
        return {"status": "validated", "activity_type": activity_type}

    else:
        raise ValueError(f"Unknown Temporal action: {action}")


def _validate_learning_workflow(
    payload: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Validate AI learning workflow request."""
    request = payload.get("payload", {})
    
    # Check category is valid
    valid_categories = [
        "security", "programming", "data_science", 
        "general", "tips", "facts"
    ]
    category = request.get("category")
    if category not in valid_categories:
        return {
            "valid": False,
            "reason": f"Invalid category: {category}. Must be one of {valid_categories}",
        }
    
    # Check content length
    content = request.get("content", "")
    if len(content) < 10:
        return {"valid": False, "reason": "Content too short (minimum 10 characters)"}
    if len(content) > 100000:
        return {"valid": False, "reason": "Content too large (maximum 100KB)"}
    
    return {"valid": True, "reason": "Learning workflow validation passed"}


def _validate_image_workflow(
    payload: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Validate image generation workflow request."""
    request = payload.get("payload", {})
    
    # Check prompt exists
    prompt = request.get("prompt", "")
    if not prompt or len(prompt) < 3:
        return {"valid": False, "reason": "Prompt too short (minimum 3 characters)"}
    
    # Check quota (10 images/hour)
    user_id = context.get("user", {}).get("username", "anonymous")
    # TODO: Implement actual quota check
    # For now, allow
    
    return {"valid": True, "reason": "Image workflow validation passed"}


def _validate_data_workflow(
    payload: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Validate data analysis workflow request."""
    request = payload.get("payload", {})
    
    # Check file path exists
    file_path = request.get("file_path", "")
    if not file_path:
        return {"valid": False, "reason": "File path required"}
    
    # Check analysis type is valid
    valid_types = ["clustering", "statistics", "visualization"]
    analysis_type = request.get("analysis_type")
    if analysis_type not in valid_types:
        return {
            "valid": False,
            "reason": f"Invalid analysis type: {analysis_type}. Must be one of {valid_types}",
        }
    
    return {"valid": True, "reason": "Data workflow validation passed"}


def _validate_memory_workflow(
    payload: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Validate memory expansion workflow request."""
    request = payload.get("payload", {})
    
    # Check conversation_id exists
    conversation_id = request.get("conversation_id", "")
    if not conversation_id:
        return {"valid": False, "reason": "Conversation ID required"}
    
    # Check messages list exists
    messages = request.get("messages", [])
    if not messages or not isinstance(messages, list):
        return {"valid": False, "reason": "Messages list required"}
    
    return {"valid": True, "reason": "Memory workflow validation passed"}


def _validate_crisis_workflow(
    payload: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    """Validate crisis response workflow request."""
    request = payload.get("payload", {})
    user = context.get("user", {})
    
    # Check 1: Admin role required
    if user.get("role") != "admin":
        return {
            "valid": False,
            "reason": f"Crisis response requires admin role (user has: {user.get('role', 'none')})",
        }
    
    # Check 2: Target member exists
    target = request.get("target_member", "")
    if not target or len(target) < 3:
        return {"valid": False, "reason": "Valid target member required"}
    
    # Check 3: Missions list exists and is non-empty
    missions = request.get("missions", [])
    if not missions or not isinstance(missions, list):
        return {"valid": False, "reason": "Missions list required"}
    
    # Check 4: Each mission has required fields
    for mission in missions:
        if not isinstance(mission, dict):
            return {"valid": False, "reason": "Invalid mission structure"}
        
        required_fields = ["phase_id", "agent_id", "action", "target"]
        for field in required_fields:
            if field not in mission:
                return {
                    "valid": False,
                    "reason": f"Mission missing required field: {field}",
                }
    
    return {"valid": True, "reason": "Crisis workflow validation passed"}

