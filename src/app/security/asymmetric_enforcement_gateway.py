"""
THIRSTY'S SECURITY ENFORCEMENT GATEWAY
Part of Thirsty's Active Resistance Language (T.A.R.L.) Framework

This is the truth-defining enforcement layer for Project-AI.
ALL state-mutating operations MUST pass through this gateway.

Hard Guarantee: If validate_action returns allowed=False, the operation CANNOT execute.

This is not advisory. This is constitutional.

Integrates with:
- Thirsty's God Tier Asymmetric Security
- Thirsty's Security Constitution
- Thirsty's Asymmetric Security Engine
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.god_tier_asymmetric_security import GodTierAsymmetricSecurity

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations that require security validation."""

    STATE_MUTATION = "state_mutation"
    PRIVILEGE_CHANGE = "privilege_change"
    CROSS_TENANT_ACCESS = "cross_tenant_access"
    AGENT_ACTION = "agent_action"
    DATA_DELETION = "data_deletion"
    POLICY_CHANGE = "policy_change"
    HUMAN_AFFECTING = "human_affecting"


@dataclass
class OperationRequest:
    """A request to perform an operation."""

    operation_id: str
    operation_type: OperationType
    action: str
    context: dict[str, Any]
    user_id: str
    timestamp: str
    requires_audit: bool = True


@dataclass
class OperationResult:
    """Result of operation validation."""

    operation_id: str
    allowed: bool
    reason: str
    threat_level: str
    layers_checked: list[str]
    enforcement_actions: list[str]
    audit_trail_id: str | None = None


class SecurityEnforcementGateway:
    """
    TRUTH-DEFINING SECURITY GATEWAY

    This gateway sits between intent and execution.
    It is the ONLY path for state-mutating operations.

    Architecture:
    1. Operation Request → Gateway
    2. Gateway → AsymmetricSecurityEngine.validate_action
    3. If allowed=False → Operation BLOCKED (exception raised)
    4. If allowed=True → Operation proceeds with audit trail

    Integration Points:
    - Command dispatcher
    - Intent handler
    - Agent action executor
    - API endpoints
    """

    def __init__(self, data_dir: str = "data/security/enforcement"):
        self.god_tier = GodTierAsymmetricSecurity(data_dir, enable_all=True)
        self.operations_processed = 0
        self.operations_blocked = 0

        logger.info("SecurityEnforcementGateway initialized - ALL operations gated")

    def enforce(self, request: OperationRequest) -> OperationResult:
        """
        ENFORCE security on an operation request.

        This is the single point of truth for security decisions.

        Returns:
            OperationResult with allowed=True/False

        Raises:
            SecurityViolationException if operation is blocked
        """
        self.operations_processed += 1

        logger.info(
            f"ENFORCING: {request.operation_type.value} - {request.action} "
            f"(user={request.user_id}, op_id={request.operation_id})"
        )

        # Comprehensive validation through all security layers
        validation_result = self.god_tier.validate_action_comprehensive(
            action=request.action, context=request.context, user_id=request.user_id
        )

        # Build enforcement result
        result = OperationResult(
            operation_id=request.operation_id,
            allowed=validation_result["allowed"],
            reason=validation_result.get("failure_reason", "All checks passed"),
            threat_level=validation_result["threat_level"],
            layers_checked=validation_result.get("layers_passed", []),
            enforcement_actions=validation_result.get("actions_taken", []),
        )

        if not result.allowed:
            self.operations_blocked += 1

            logger.critical(
                f"OPERATION BLOCKED: {request.operation_id} - {result.reason} "
                f"(threat={result.threat_level})"
            )

            # Record incident for security operations center
            self._record_security_incident(request, result)

            # HARD BLOCK - Raise exception to prevent execution
            raise SecurityViolationException(
                operation_id=request.operation_id,
                reason=result.reason,
                threat_level=result.threat_level,
                enforcement_actions=result.enforcement_actions,
            )

        # Operation allowed - create audit trail
        if request.requires_audit:
            result.audit_trail_id = self._create_audit_trail(request, result)

        logger.info(
            f"OPERATION ALLOWED: {request.operation_id} - "
            f"Passed {len(result.layers_checked)} layers"
        )

        return result

    def _record_security_incident(
        self, request: OperationRequest, result: OperationResult
    ) -> None:
        """Record security incident for blocked operation."""
        incident = {
            "incident_type": "security_violation",
            "operation_id": request.operation_id,
            "operation_type": request.operation_type.value,
            "action": request.action,
            "user_id": request.user_id,
            "blocked_at": datetime.now().isoformat(),
            "reason": result.reason,
            "threat_level": result.threat_level,
            "enforcement_actions": result.enforcement_actions,
            "context": request.context,
        }

        # TODO: Wire into Hydra-50 incident response system
        logger.critical(f"SECURITY INCIDENT: {incident}")

    def _create_audit_trail(
        self, request: OperationRequest, result: OperationResult
    ) -> str:
        """Create audit trail for allowed operation."""
        from hashlib import sha256

        audit_id = sha256(
            f"{request.operation_id}{request.timestamp}".encode()
        ).hexdigest()[:16]

        audit_record = {
            "audit_id": audit_id,
            "operation_id": request.operation_id,
            "operation_type": request.operation_type.value,
            "action": request.action,
            "user_id": request.user_id,
            "timestamp": request.timestamp,
            "allowed": result.allowed,
            "layers_checked": result.layers_checked,
            "context": request.context,
        }

        # TODO: Wire into immutable audit log system
        logger.info(f"AUDIT TRAIL: {audit_id} - {request.action}")

        return audit_id

    def get_enforcement_stats(self) -> dict[str, Any]:
        """Get enforcement statistics."""
        return {
            "operations_processed": self.operations_processed,
            "operations_blocked": self.operations_blocked,
            "block_rate": self.operations_blocked / max(self.operations_processed, 1),
            "god_tier_metrics": self.god_tier.metrics,
        }


class SecurityViolationException(Exception):
    """
    Exception raised when operation is blocked by security gateway.

    This exception MUST be caught and handled at the application layer.
    It prevents the operation from executing.
    """

    def __init__(
        self,
        operation_id: str,
        reason: str,
        threat_level: str,
        enforcement_actions: list[str],
    ):
        self.operation_id = operation_id
        self.reason = reason
        self.threat_level = threat_level
        self.enforcement_actions = enforcement_actions

        super().__init__(
            f"SECURITY VIOLATION: {operation_id} - {reason} " f"(threat={threat_level})"
        )


# ============================================================================
# COMMAND DISPATCHER INTEGRATION
# ============================================================================


class SecureCommandDispatcher:
    """
    Command dispatcher that enforces security on all operations.

    This replaces any existing command dispatcher that doesn't gate through
    the SecurityEnforcementGateway.
    """

    def __init__(self, gateway: SecurityEnforcementGateway):
        self.gateway = gateway
        self.command_handlers: dict[str, Callable] = {}

    def register_command(self, command_name: str, handler: Callable) -> None:
        """Register a command handler."""
        self.command_handlers[command_name] = handler
        logger.info(f"Registered secure command: {command_name}")

    def execute_command(
        self,
        command_name: str,
        user_id: str,
        context: dict[str, Any],
        operation_type: OperationType = OperationType.STATE_MUTATION,
    ) -> Any:
        """
        Execute a command with security enforcement.

        Security is checked BEFORE execution.
        If blocked, command never runs.
        """
        if command_name not in self.command_handlers:
            raise ValueError(f"Unknown command: {command_name}")

        # Create operation request
        import secrets

        request = OperationRequest(
            operation_id=secrets.token_hex(8),
            operation_type=operation_type,
            action=command_name,
            context=context,
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            requires_audit=True,
        )

        # ENFORCE SECURITY - This can raise SecurityViolationException
        enforcement_result = self.gateway.enforce(request)

        # Security passed - execute command
        handler = self.command_handlers[command_name]
        result = handler(user_id, context)

        logger.info(
            f"Command executed: {command_name} "
            f"(audit_id={enforcement_result.audit_trail_id})"
        )

        return result


# ============================================================================
# INTEGRATION DECORATOR
# ============================================================================


def secure_operation(
    operation_type: OperationType,
    gateway: SecurityEnforcementGateway | None = None,
):
    """
    Decorator to enforce security on any function.

    Usage:
        @secure_operation(OperationType.STATE_MUTATION)
        def delete_user(user_id: str, target_user_id: str):
            # This will only run if security allows
            ...
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Extract user_id and build context
            # This is a simplified version - production needs smarter extraction
            user_id = kwargs.get("user_id", "unknown")
            context = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }

            # Get or create gateway
            gw = gateway or SecurityEnforcementGateway()

            # Create operation request
            import secrets

            request = OperationRequest(
                operation_id=secrets.token_hex(8),
                operation_type=operation_type,
                action=func.__name__,
                context=context,
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
            )

            # ENFORCE - This can raise SecurityViolationException
            gw.enforce(request)

            # Security passed - execute function
            return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize gateway
    gateway = SecurityEnforcementGateway("data/security/enforcement")

    # Example 1: Direct enforcement
    try:
        request = OperationRequest(
            operation_id="test_001",
            operation_type=OperationType.STATE_MUTATION,
            action="delete_user_data",
            context={
                "user_id": "user_123",
                "auth_token": None,  # Missing token - should block
                "state_changed": True,
            },
            user_id="user_123",
            timestamp=datetime.now().isoformat(),
        )

        result = gateway.enforce(request)
        print(f"Operation allowed: {result.allowed}")

    except SecurityViolationException as e:
        print(f"✗ BLOCKED: {e.reason}")
        print(f"  Threat Level: {e.threat_level}")

    # Example 2: Command dispatcher
    dispatcher = SecureCommandDispatcher(gateway)

    def safe_read_handler(user_id: str, context: dict) -> str:
        return f"Data for {user_id}"

    dispatcher.register_command("read_profile", safe_read_handler)

    try:
        result = dispatcher.execute_command(
            command_name="read_profile",
            user_id="user_123",
            context={"auth_token": "valid"},
            operation_type=OperationType.STATE_MUTATION,
        )
        print(f"Command result: {result}")
    except SecurityViolationException as e:
        print(f"✗ Command blocked: {e.reason}")

    # Show stats
    stats = gateway.get_enforcement_stats()
    print(f"\nEnforcement Stats: {stats}")
