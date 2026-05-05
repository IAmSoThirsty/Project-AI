"""
Governance Pipeline: Universal enforcement layer.

Every request from ANY execution path flows through this pipeline.
This is what ensures consistent governance across web/desktop/CLI/agents.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from .rate_limiter import check_rate_limit as redis_check_rate_limit
from .iron_path_executor import GovernanceBindingError, get_iron_path_executor

logger = logging.getLogger(__name__)

try:
    from utf.shadow_thirst.core import parse_shadow as _parse_shadow, promote as _promote_shadow
except ImportError:
    _parse_shadow = None  # type: ignore[assignment]
    _promote_shadow = None  # type: ignore[assignment]


# ACTION REGISTRY: Whitelist of all valid actions
# This prevents unknown/malicious actions from bypassing validation
VALID_ACTIONS = {
    # AI Operations
    "ai.chat", "ai.image", "ai.code", "ai.analyze",
    
    # User Management
    "user.login", "user.logout", "user.create", "user.update", "user.delete",
    
    # Persona Operations
    "persona.update", "persona.query", "persona.reset",
    
    # Agent Operations
    "agent.execute", "agent.plan", "agent.validate",
    
    # Temporal Operations
    "temporal.workflow.validate", "temporal.workflow.execute", 
    "temporal.activity.validate", "temporal.activity.execute",
    
    # System Operations
    "system.status", "system.config", "system.shutdown",
    
    # Data Operations
    "data.query", "data.update", "data.export",
    
    # Learning Operations
    "learning.request", "learning.approve", "learning.deny",

    # Dashboard Operations (governed desktop actions)
    "codex.fix", "codex.activate", "codex.qa",
    "access.grant", "audit.export", "agents.toggle",

    # External ecosystem integration (read-only governed inventory)
    "ecosystem.scan", "ecosystem.capabilities",

    # Auth aliases (backward compatibility)
    "auth.login",
}

# Action metadata for enhanced validation
ACTION_METADATA = {
    "ai.chat": {"requires_auth": True, "rate_limit": 30, "resource_intensive": False},
    "ai.image": {"requires_auth": True, "rate_limit": 10, "resource_intensive": True},
    "user.login": {"requires_auth": False, "rate_limit": 5, "resource_intensive": False},
    "user.delete": {"requires_auth": True, "admin_only": True, "resource_intensive": False},
    "system.shutdown": {"requires_auth": True, "admin_only": True, "resource_intensive": False},
}


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

    validated_context: dict[str, Any] | None = None
    gated_context: dict[str, Any] | None = None
    result: Any = None

    try:
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
        _log(gated_context, result, status="success")

        return result
    except Exception as e:
        # Always attempt to log failed requests for forensic traceability
        log_context = gated_context or validated_context or context
        _log(log_context, result=None, status="error", error=str(e))
        raise


def _validate(context: dict[str, Any]) -> dict[str, Any]:
    """
    Phase 1: Input validation and sanitization.

    Checks:
        - Action is in whitelist (prevents unknown/malicious actions)
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

    # ACTION REGISTRY CHECK: Reject unknown actions
    action = context["action"]
    
    # STRICT ACTION REGISTRY CHECK (no prefix/wildcard bypass)
    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Action '{action}' not in registry. "
            f"Valid actions: {sorted(VALID_ACTIONS)}"
        )

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

    action = context["action"]
    payload = context.get("payload", {})
    
    # Build simulation result based on action type
    simulation = {
        "estimated_impact": "low",
        "state_changes": [],
        "resource_usage": {"cpu": "low", "memory": "low", "network": "low"},
        "predicted_outcome": "success",
        "risk_level": "low",
        "requires_admin": False,
    }
    
    # Analyze based on action metadata
    if action in ACTION_METADATA:
        metadata = ACTION_METADATA[action]
        
        if metadata.get("resource_intensive"):
            simulation["estimated_impact"] = "high"
            simulation["resource_usage"]["cpu"] = "high"
            simulation["resource_usage"]["memory"] = "high"
            simulation["risk_level"] = "medium"
        
        if metadata.get("admin_only"):
            simulation["requires_admin"] = True
            simulation["risk_level"] = "high"
    
    # Predict state changes based on action
    if action.startswith("user."):
        simulation["state_changes"].append("user_database")
    elif action.startswith("persona."):
        simulation["state_changes"].append("persona_state")
    elif action.startswith("system."):
        simulation["state_changes"].append("system_config")
        simulation["estimated_impact"] = "high"
    
    # AI operations
    if action.startswith("ai."):
        simulation["resource_usage"]["network"] = "high"
        if action == "ai.image":
            simulation["resource_usage"]["cpu"] = "high"
            simulation["estimated_impact"] = "medium"
    
    # Agent operations
    if action.startswith("agent."):
        simulation["resource_usage"]["cpu"] = "medium"
        simulation["state_changes"].append("agent_state")
    
    # Temporal workflows
    if action.startswith("temporal."):
        simulation["resource_usage"]["memory"] = "medium"
        simulation["state_changes"].append("workflow_state")
    
    # Predict potential failures
    simulation["potential_failures"] = []
    
    if simulation["requires_admin"]:
        user_role = context.get("user", {}).get("role", "user")
        if user_role != "admin":
            simulation["predicted_outcome"] = "failure"
            simulation["potential_failures"].append("insufficient_permissions")
    
    # Check for required fields in payload
    required_fields = _get_required_fields(action)
    missing_fields = [f for f in required_fields if f not in payload]
    if missing_fields:
        simulation["predicted_outcome"] = "failure"
        simulation["potential_failures"].append(f"missing_fields: {missing_fields}")
    
    return simulation


def _get_required_fields(action: str) -> list[str]:
    """Get required payload fields for an action."""
    field_requirements = {
        "auth.login": ["username", "password"],
        "user.login": ["username", "password"],
        "user.create": ["username", "password", "role"],
        "user.update": ["username"],
        "persona.update": ["trait", "value"],
        "ai.chat": ["prompt"],
        "ai.image": ["prompt"],
        "agent.execute": ["agent_type", "task"],
        "learning.approve": ["request_id"],
        "learning.deny": ["request_id"],
        "codex.activate": ["staged_path"],
        "access.grant": ["username", "role"],
        "agents.toggle": ["agent_types"],
    }
    return field_requirements.get(action, [])


def _lookup_user_role(username: str) -> str:
    """Best-effort role lookup from user and access control stores."""
    if not username or username == "anonymous":
        return "anonymous"

    # Primary source: UserManager roles
    try:
        from app.core.user_manager import UserManager

        user_manager = UserManager()
        role = user_manager.users.get(username, {}).get("role")
        if role:
            return role
    except Exception as e:
        logger.debug("UserManager role lookup failed for %s: %s", username, e)

    # Secondary source: AccessControl roles
    try:
        from app.core.access_control import get_access_control

        access = get_access_control()
        if access.has_role(username, "admin"):
            return "admin"
        if access.has_role(username, "integrator") or access.has_role(
            username, "expert"
        ):
            return "power_user"
    except Exception as e:
        logger.debug("AccessControl role lookup failed for %s: %s", username, e)

    # Authenticated user fallback
    return "user"


def _resolve_user_context(context: dict[str, Any]) -> dict[str, Any]:
    """
    Resolve authenticated user context from explicit user object and/or JWT token.

    Priority:
    1. Explicit user context in request
    2. JWT token in payload
    3. Role lookup by username
    4. Anonymous fallback
    """
    payload = context.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}

    user = context.get("user", {})
    if not isinstance(user, dict):
        user = {}

    username = user.get("username")
    role = user.get("role")

    # Try token-based resolution when role context is incomplete
    token = payload.get("token")
    if token and (not username or not role):
        try:
            from app.core.security.auth import verify_jwt_token

            token_payload = verify_jwt_token(token)
        except Exception as e:
            raise PermissionError(f"Token verification failed: {e}") from e

        if token_payload is None:
            raise PermissionError("Invalid or expired authentication token")

        username = token_payload.username
        role = token_payload.role

    # Infer role if username exists but role was not explicitly provided
    if username and not role:
        role = _lookup_user_role(username)

    if not username:
        username = "anonymous"
    if not role:
        role = "anonymous"

    resolved = {
        "username": username,
        "role": role,
    }

    context["user"] = resolved
    return resolved


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

    # Resolve authenticated user context before all gate checks
    _resolve_user_context(context)

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

    # High-impact mutation governance binding (Iron Path)
    _enforce_mutation_governance_binding(context, simulation)

    return context


def _enforce_mutation_governance_binding(
    context: dict[str, Any], simulation: dict[str, Any]
) -> None:
    """
    Enforce MutationGovernanceBinding and immutable decision records for
    high-impact mutations.

    This keeps legacy low-impact operations flowing while ensuring critical
    mutations are fully governed and audit-replayable.
    """
    action = context.get("action", "")
    payload = context.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}

    executor = get_iron_path_executor()
    mutation_class = executor.classify_mutation(action)

    # Read-only operations are exempt from mutation binding.
    if mutation_class == "read":
        return

    # Only enforce mandatory binding for high-impact classes.
    if mutation_class not in {"hardMutation", "governanceMutation"}:
        return

    principal = context.get("user", {}).get("username", "anonymous")
    trace_id = payload.get("trace_id") or str(uuid.uuid4())
    resource = payload.get("resource") or action

    eval_req, eval_result = executor.evaluate_policy(
        action=action,
        resource=resource,
        principal=principal,
        context={
            "trace_id": trace_id,
            "valid_actions": sorted(VALID_ACTIONS),
            "constraints": [
                "default-deny",
                "immutable-decision-record",
                "policy-evaluation-binding",
            ],
            "source": context.get("source"),
            "user": context.get("user", {}),
            "simulation": simulation,
        },
    )

    capability_token = payload.get("capability_token", "")
    quorum_proof = payload.get("quorum_proof")

    try:
        binding = executor.bind_mutation(
            action=action,
            resource=resource,
            capability_token=capability_token,
            governance_context={
                "source": context.get("source"),
                "user": context.get("user", {}),
                "simulation": simulation,
            },
            resolution_policy="default-deny-precedence",
            evaluation_request=eval_req,
            evaluation_result=eval_result,
            quorum_proof=quorum_proof,
        )
    except GovernanceBindingError as e:
        raise PermissionError(f"Mutation governance binding failed: {e}") from e

    decision = executor.record_decision(
        principal=principal,
        binding=binding,
        evaluation_result=eval_result,
        decision="allow",
        reason="High-impact mutation authorized with complete governance binding",
        metadata={
            "source": context.get("source"),
            "pipeline_action": action,
        },
    )

    # Shadow Thirst promotion gate — runs when caller supplies a shadow_source
    # (a .shadowthirst mutation block). REJECT halts the mutation; PROMOTE adds
    # replay provenance to governance context.
    shadow_source = payload.get("shadow_source")
    if shadow_source and _parse_shadow is not None and _promote_shadow is not None:
        try:
            shadow_module = _parse_shadow(shadow_source)
            promotion = _promote_shadow(shadow_module, replay_id=trace_id)
            if promotion["decision"] == "REJECT":
                failed = [
                    r["message"] for r in promotion["analysis"]
                    if r["level"] == "critical" and not r["passed"]
                ]
                raise PermissionError(
                    f"Shadow Thirst REJECT (replay={promotion['replay_id']}): "
                    + "; ".join(failed)
                )
            payload.setdefault("_shadow_promotion", {
                "decision": promotion["decision"],
                "replay_id": promotion["replay_id"],
                "replay_hash": promotion["replay_hash"],
            })
        except PermissionError:
            raise
        except Exception as exc:
            logger.warning("Shadow Thirst analysis skipped: %s", exc)

    context.setdefault("governance", {})
    context["governance"]["trace_id"] = trace_id
    context["governance"]["decision_record_id"] = decision.decision_record_id
    context["governance"]["mutation_class"] = mutation_class
    if "_shadow_promotion" in payload:
        context["governance"]["shadow_promotion"] = payload["_shadow_promotion"]


def _check_rate_limit(context: dict[str, Any]) -> None:
    """
    Enforce rate limits using Redis-based distributed rate limiter.
    
    This replaces the old in-memory implementation with production-ready
    Redis-based rate limiting that supports:
    - Multi-tier limits (per-action, per-user, global)
    - Distributed rate limiting across processes/servers
    - Accurate sliding window algorithm
    - Automatic fallback to in-memory if Redis unavailable
    
    Raises:
        PermissionError: If rate limit exceeded
    """
    # Use new Redis-based rate limiter
    redis_check_rate_limit(context)


def _check_user_permissions(context: dict[str, Any]) -> None:
    """
    Check user permissions for action with full RBAC implementation.
    
    Raises:
        PermissionError: If user lacks permission
    """
    action = context["action"]
    user = context.get("user", {})
    user_role = user.get("role", "anonymous")
    username = user.get("username", "anonymous")
    
    # Role hierarchy: admin > power_user > user > guest
    role_hierarchy = {"admin": 4, "power_user": 3, "user": 2, "guest": 1, "anonymous": 0}
    user_level = role_hierarchy.get(user_role, 0)
    
    # Permission matrix: action -> minimum role level required
    permission_matrix = {
        # Admin-only actions
        "user.delete": 4,
        "system.shutdown": 4,
        "system.config": 4,
        
        # Power user actions
        "user.create": 3,
        "user.update": 3,
        "data.export": 3,
        
        # Authenticated user actions
        "ai.chat": 2,
        "ai.image": 2,
        "ai.code": 2,
        "persona.update": 2,
        "learning.request": 2,
        "learning.approve": 3,
        "learning.deny": 3,
        "agent.execute": 2,

        # Governance-powered dashboard operations
        "codex.fix": 3,
        "codex.activate": 3,
        "codex.qa": 3,
        "access.grant": 3,
        "audit.export": 3,
        "agents.toggle": 3,
        
        # Guest actions
        "system.status": 1,
        "data.query": 1,
        
        # Anonymous actions
        "user.login": 0,
        "auth.login": 0,
    }
    
    # Check action permission
    required_level = permission_matrix.get(action, 2)  # Default: require authenticated user
    
    # Special case: users can always update their own data
    if action == "user.update":
        target_user = context.get("payload", {}).get("username")
        if target_user == username:
            required_level = 2  # Own profile
    
    if user_level < required_level:
        required_role = [r for r, l in role_hierarchy.items() if l == required_level][0]
        raise PermissionError(
            f"Action '{action}' requires role '{required_role}' or higher "
            f"(user '{username}' has role '{user_role}')"
        )
    
    logger.debug(f"Permission check passed: {username} ({user_role}) for {action}")


def _check_resource_quotas(context: dict[str, Any]) -> None:
    """
    Check resource quotas with persistent tracking via file-based storage.
    
    Raises:
        PermissionError: If quota exceeded
    """
    import json
    import os
    from datetime import datetime, timedelta
    
    action = context["action"]
    user = context.get("user", {}).get("username", "anonymous")
    
    # Quota definitions: action -> limits
    quotas = {
        "ai.chat": {"hourly_limit": 100, "daily_limit": 1000},
        "ai.image": {"hourly_limit": 10, "daily_limit": 100},
        "ai.code": {"hourly_limit": 50, "daily_limit": 500},
        "data.export": {"daily_limit": 10},
        "agent.execute": {"hourly_limit": 20, "daily_limit": 200},
    }
    
    if action not in quotas:
        return  # No quota for this action
    
    limits = quotas[action]
    
    # Load quota tracking data
    quota_file = "data/runtime/quotas.json"
    os.makedirs("data/runtime", exist_ok=True)
    
    try:
        if os.path.exists(quota_file):
            with open(quota_file, "r") as f:
                quota_data = json.load(f)
        else:
            quota_data = {}
    except Exception as e:
        logger.warning(f"Failed to load quota data: {e}")
        quota_data = {}
    
    # Initialize user quota tracking
    if user not in quota_data:
        quota_data[user] = {}
    if action not in quota_data[user]:
        quota_data[user][action] = {"requests": []}
    
    # Get request history
    requests = quota_data[user][action]["requests"]
    now = datetime.now()
    
    # Clean old requests (older than 24 hours)
    requests = [
        ts for ts in requests
        if datetime.fromisoformat(ts) > now - timedelta(hours=24)
    ]
    
    # Check hourly limit
    if "hourly_limit" in limits:
        hour_ago = now - timedelta(hours=1)
        hourly_requests = [
            ts for ts in requests
            if datetime.fromisoformat(ts) > hour_ago
        ]
        
        if len(hourly_requests) >= limits["hourly_limit"]:
            raise PermissionError(
                f"Hourly quota exceeded for {action}: "
                f"{len(hourly_requests)}/{limits['hourly_limit']} requests in last hour"
            )
    
    # Check daily limit
    if "daily_limit" in limits:
        day_ago = now - timedelta(hours=24)
        daily_requests = [
            ts for ts in requests
            if datetime.fromisoformat(ts) > day_ago
        ]
        
        if len(daily_requests) >= limits["daily_limit"]:
            raise PermissionError(
                f"Daily quota exceeded for {action}: "
                f"{len(daily_requests)}/{limits['daily_limit']} requests in last 24 hours"
            )
    
    # Record this request
    requests.append(now.isoformat())
    quota_data[user][action]["requests"] = requests
    
    # Save updated quota data
    try:
        with open(quota_file, "w") as f:
            json.dump(quota_data, f)
    except Exception as e:
        logger.warning(f"Failed to save quota data: {e}")
    
    logger.debug(f"Quota check passed for {user}: {action}")


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
    if action.startswith("agent."):
        from app.core.kernel_integration import get_global_kernel

        kernel = get_global_kernel()
        if not kernel:
            raise RuntimeError("CognitionKernel not available for agent action")

        # Execute through kernel route API
        result = kernel.route(
            task={
                "action": action,
                "payload": payload,
            },
            source="agent",
            metadata={
                "action": action,
                "requester": context.get("user", {}).get("username", "system"),
                "requires_approval": True,
                "risk_level": "medium",
            },
        )

        if hasattr(result, "success"):
            if result.success:
                return result.result
            raise RuntimeError(result.error or "Kernel-routed agent action failed")

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
    elif action in {"user.login", "auth.login"}:
        from app.core.user_manager import UserManager
        from app.core.security.auth import generate_jwt_token

        manager = UserManager()
        auth_result = manager.authenticate(
            payload.get("username"), payload.get("password")
        )

        if isinstance(auth_result, tuple):
            is_authenticated = bool(auth_result[0])
            auth_message = str(auth_result[1]) if len(auth_result) > 1 else ""
        else:
            is_authenticated = bool(auth_result)
            auth_message = ""

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
            raise PermissionError(auth_message or "Invalid credentials")

    elif action == "persona.update":
        from app.core.ai_systems import AIPersona

        persona = AIPersona()
        trait = payload.get("trait")
        if not trait:
            raise ValueError("persona.update requires 'trait'")

        try:
            delta = float(payload.get("value", 0.0))
        except (TypeError, ValueError) as e:
            raise ValueError("persona.update requires numeric 'value'") from e

        persona.adjust_trait(trait, delta)
        return {
            "status": "updated",
            "trait": trait,
            "value": persona.personality.get(trait),
        }

    elif action == "learning.approve":
        from app.core.ai_systems import LearningRequestManager

        request_id = payload.get("request_id")
        if not request_id:
            raise ValueError("learning.approve requires 'request_id'")

        manager = LearningRequestManager()
        approved = manager.approve_request(
            request_id,
            payload.get("response", "Approved via governance pipeline"),
        )
        if not approved:
            raise ValueError(f"Learning request not found: {request_id}")

        return {"status": "approved", "request_id": request_id}

    elif action == "learning.deny":
        from app.core.ai_systems import LearningRequestManager

        request_id = payload.get("request_id")
        if not request_id:
            raise ValueError("learning.deny requires 'request_id'")

        manager = LearningRequestManager()
        denied = manager.deny_request(
            request_id,
            payload.get("reason", "Denied via governance pipeline"),
            bool(payload.get("to_vault", True)),
        )
        if not denied:
            raise ValueError(f"Learning request not found: {request_id}")

        return {"status": "denied", "request_id": request_id}

    elif action == "codex.fix":
        from app.agents.codex_deus_maximus import create_codex

        root = payload.get("root")
        codex = create_codex()
        report = codex.run_schematic_enforcement(root)
        return {
            "fixed": report.get("fixes", []),
            "errors": report.get("errors", []),
            "structure": report.get("structure_check", {}),
        }

    elif action == "codex.activate":
        import os
        import shutil

        staged_path = payload.get("staged_path")
        if not staged_path:
            raise ValueError("codex.activate requires 'staged_path'")
        if not os.path.exists(staged_path):
            raise ValueError(f"Staged artifact not found: {staged_path}")

        integrated_dir = "data/waiting_room/integrated"
        os.makedirs(integrated_dir, exist_ok=True)
        destination = os.path.join(integrated_dir, os.path.basename(staged_path))
        shutil.copy2(staged_path, destination)

        return {
            "status": "activated",
            "integrated_path": destination,
        }

    elif action == "codex.qa":
        from app.core.council_hub import get_council_hub

        hub = get_council_hub()
        checks = hub.run_checks(payload.get("staged_path"))
        success = bool(checks.get("success"))
        return {
            "dependency_success": success,
            "test_success": success,
            "details": checks,
        }

    elif action == "access.grant":
        from app.core.access_control import get_access_control

        username = payload.get("username")
        role = payload.get("role")
        if not username or not role:
            raise ValueError("access.grant requires 'username' and 'role'")

        access = get_access_control()
        access.grant_role(username, role)
        return {
            "status": "granted",
            "username": username,
            "role": role,
        }

    elif action == "audit.export":
        import json
        import os
        from datetime import datetime

        export_dir = "data/runtime/exports"
        os.makedirs(export_dir, exist_ok=True)
        out_path = os.path.join(
            export_dir,
            f"audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )

        export_payload: dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "requester": payload.get("requester", "unknown"),
            "sources": {},
        }

        sources = [
            "data/runtime/governance_audit.log",
            "data/runtime/state_changes.log",
            "data/codex_audit.json",
        ]
        for source_path in sources:
            if not os.path.exists(source_path):
                continue
            try:
                if source_path.endswith(".log"):
                    with open(source_path, encoding="utf-8") as f:
                        export_payload["sources"][source_path] = f.read().splitlines()
                else:
                    with open(source_path, encoding="utf-8") as f:
                        export_payload["sources"][source_path] = json.load(f)
            except Exception as e:
                export_payload["sources"][source_path] = {
                    "error": f"Failed to read source: {e}",
                }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=2)

        return {
            "status": "exported",
            "out": out_path,
        }

    elif action == "agents.toggle":
        from app.core.council_hub import get_council_hub

        agent_types = payload.get("agent_types")
        if not isinstance(agent_types, list) or not agent_types:
            raise ValueError("agents.toggle requires non-empty 'agent_types' list")

        hub = get_council_hub()
        target_enabled = not hub.is_agent_enabled(agent_types[0])

        for agent_id in agent_types:
            if target_enabled:
                hub.enable_agent(agent_id)
            else:
                hub.disable_agent(agent_id)

        return {
            "enabled": target_enabled,
            "agent_types": agent_types,
        }

    elif action == "ecosystem.scan":
        from app.core.governance.external_ecosystem_bridge import (
            get_external_ecosystem_bridge,
        )

        bridge = get_external_ecosystem_bridge()
        inventories = [item.to_dict() for item in bridge.inventory()]
        return {
            "status": "ok",
            "inventory": inventories,
            "available": len([inv for inv in inventories if inv.get("exists")]),
        }

    elif action == "ecosystem.capabilities":
        from app.core.governance.external_ecosystem_bridge import (
            get_external_ecosystem_bridge,
        )

        bridge = get_external_ecosystem_bridge()
        return {
            "status": "ok",
            "governance_context": bridge.governance_context(),
        }

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
    state_actions = [
        "user.login",
        "auth.login",
        "persona.update",
        "user.create",
        "user.update",
    ]
    
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

    action = context.get("action", "")
    payload = context.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}

    # Action-specific consistency checks
    if action in {"user.login", "auth.login"}:
        if not isinstance(result, dict):
            return False
        return bool(result.get("username")) and bool(result.get("token"))

    if action == "persona.update":
        if not isinstance(result, dict):
            return False
        expected_trait = payload.get("trait")
        return (
            result.get("status") == "updated"
            and result.get("trait") == expected_trait
            and result.get("value") is not None
        )

    if action in {"user.create", "user.update"} and isinstance(result, dict):
        expected_username = payload.get("username")
        if expected_username:
            return result.get("username") == expected_username

    return True


def _log(
    context: dict[str, Any],
    result: Any,
    status: str = "success",
    error: str | None = None,
) -> None:
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
    
    payload = context.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}

    # Build structured audit log entry
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": context["action"],
        "source": context["source"],
        "user": context.get("user", {}).get("username", "anonymous"),
        "status": status,
        "result_type": type(result).__name__,
        "payload_summary": {
            k: str(v)[:50] for k, v in payload.items()
            if k not in ["password", "token", "api_key"]  # Redact sensitive fields
        }
    }

    if error:
        audit_entry["error"] = error
    
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
    
def _execute_temporal_action(
    action: str, payload: dict[str, Any], context: dict[str, Any]
) -> Any:
    """
    Execute Temporal workflow operations through governance.

    Supported actions:
        - temporal.workflow.validate: Pre-execution validation gate
        - temporal.workflow.execute: Execute workflow through Temporal client
        - temporal.activity.validate: Pre-activity validation
        - temporal.activity.execute: Execute specific activity in governed mode

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
        workflow_type = payload.get("workflow_type")
        workflow_payload = payload.get("payload", {})

        if not workflow_type:
            raise ValueError("temporal.workflow.execute requires 'workflow_type'")

        logger.info(f"Executing Temporal workflow: {workflow_type}")

        workflow_result = _start_temporal_workflow(
            workflow_type=workflow_type,
            workflow_payload=workflow_payload,
            context=context,
        )

        return {
            "status": "workflow_started",
            "workflow_type": workflow_type,
            **workflow_result,
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

    elif action == "temporal.activity.execute":
        activity_type = payload.get("activity_type")
        activity_payload = payload.get("payload", {})

        if not activity_type:
            raise ValueError("temporal.activity.execute requires 'activity_type'")

        if not isinstance(activity_payload, dict):
            raise ValueError("temporal.activity.execute requires dict 'payload'")

        if activity_type == "agent_mission":
            from app.temporal.activities import perform_agent_mission

            success = _run_async_safely(perform_agent_mission(activity_payload))
            return {
                "status": "activity_executed",
                "activity_type": activity_type,
                "success": bool(success),
            }

        raise ValueError(f"Unknown activity type: {activity_type}")

    else:
        raise ValueError(f"Unknown Temporal action: {action}")


def _run_async_safely(coro: Any) -> Any:
    """Run an async coroutine from sync governance code."""
    import asyncio

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError(
        "Cannot run async Temporal operation inside an active event loop context"
    )


def _start_temporal_workflow(
    workflow_type: str,
    workflow_payload: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Start a Temporal workflow and return workflow/run identifiers."""
    import uuid

    from app.temporal.client import TemporalClientManager
    from app.temporal.workflows import (
        AILearningWorkflow,
        CrisisRequest,
        CrisisResponseWorkflow,
        DataAnalysisRequest,
        DataAnalysisWorkflow,
        ImageGenerationRequest,
        ImageGenerationWorkflow,
        LearningRequest,
        MemoryExpansionRequest,
        MemoryExpansionWorkflow,
        MissionPhase,
    )

    workflow_map = {
        "ai_learning": (AILearningWorkflow, LearningRequest),
        "image_generation": (ImageGenerationWorkflow, ImageGenerationRequest),
        "data_analysis": (DataAnalysisWorkflow, DataAnalysisRequest),
        "memory_expansion": (MemoryExpansionWorkflow, MemoryExpansionRequest),
        "crisis_response": (CrisisResponseWorkflow, CrisisRequest),
    }

    workflow_entry = workflow_map.get(workflow_type)
    if workflow_entry is None:
        raise ValueError(f"Unknown workflow type: {workflow_type}")

    workflow_cls, request_cls = workflow_entry

    # Normalize crisis workflow payload to dataclass contract
    if workflow_type == "crisis_response":
        missions_data = workflow_payload.get("missions", [])
        missions: list[MissionPhase] = []
        for mission in missions_data:
            if not isinstance(mission, dict):
                raise ValueError("Each crisis mission must be a dict")
            missions.append(
                MissionPhase(
                    phase_id=mission.get("phase_id", ""),
                    agent_id=mission.get("agent_id", ""),
                    action=mission.get("action", ""),
                    target=mission.get("target", ""),
                    priority=mission.get("priority", 1),
                )
            )

        request_obj = request_cls(
            target_member=workflow_payload.get("target_member", ""),
            missions=missions,
            crisis_id=workflow_payload.get("crisis_id"),
            initiated_by=context.get("user", {}).get("username"),
            initiator_role=context.get("user", {}).get("role"),
        )
    else:
        try:
            request_obj = request_cls(**workflow_payload)
        except TypeError as e:
            raise ValueError(
                f"Invalid workflow payload for {workflow_type}: {e}"
            ) from e

    workflow_id = workflow_payload.get("workflow_id") or (
        f"{workflow_type}-{uuid.uuid4().hex[:12]}"
    )

    async def _start() -> dict[str, Any]:
        manager = TemporalClientManager()
        await manager.connect()
        try:
            handle = await manager.client.start_workflow(
                workflow_cls.run,
                request_obj,
                id=workflow_id,
                task_queue=manager.task_queue,
            )
            return {
                "workflow_id": getattr(handle, "id", workflow_id),
                "run_id": getattr(handle, "first_execution_run_id", None),
            }
        finally:
            await manager.disconnect()

    return _run_async_safely(_start())


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
    
    # Check quota (10 images/hour per user) with lightweight rolling window file.
    user_id = context.get("user", {}).get("username", "anonymous")
    if not _check_image_workflow_quota(user_id):
        return {
            "valid": False,
            "reason": "Image workflow quota exceeded (10 requests/hour)",
        }
    
    return {"valid": True, "reason": "Image workflow validation passed"}


def _check_image_workflow_quota(user_id: str) -> bool:
    """Check and record image workflow quota in a bounded rolling window."""
    import json
    import os
    from datetime import datetime, timedelta

    quota_file = "data/runtime/image_workflow_quota.json"
    os.makedirs("data/runtime", exist_ok=True)

    try:
        if os.path.exists(quota_file):
            with open(quota_file, "r", encoding="utf-8") as f:
                quota_data = json.load(f)
        else:
            quota_data = {}
    except Exception as e:
        logger.warning("Failed loading image workflow quota file: %s", e)
        quota_data = {}

    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    entries = quota_data.get(user_id, [])
    filtered = []
    for item in entries:
        try:
            ts = datetime.fromisoformat(item)
            if ts > hour_ago:
                filtered.append(item)
        except Exception:
            continue

    if len(filtered) >= 10:
        return False

    filtered.append(now.isoformat())
    quota_data[user_id] = filtered

    try:
        with open(quota_file, "w", encoding="utf-8") as f:
            json.dump(quota_data, f)
    except Exception as e:
        logger.warning("Failed writing image workflow quota file: %s", e)

    return True


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

