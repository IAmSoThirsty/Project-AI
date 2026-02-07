"""
Tier Interfaces - Formal interface definitions for three-tier platform communication.

This module defines the formal interfaces that govern communication between tiers:
- Tier 1 (Governance) → Tier 2 (Infrastructure) → Tier 3 (Application)

CRITICAL BOUNDARIES:
- Tier 1 can command Tier 2/3 (authority flows downward)
- Tier 2/3 can request from Tier 1 (capability flows upward)
- Tier 2 can block Tier 3 based on governance policies
- All cross-tier communication goes through these interfaces

=== FORMAL SPECIFICATION ===

## Tier Interface Hierarchy

### Tier 1 (Governance) Interface
- evaluate_action(action, context) → Decision
- enforce_policy(policy, target_tier) → Enforcement
- audit_operation(operation) → AuditRecord
- rollback_tier(tier, reason) → RollbackResult

### Tier 2 (Infrastructure) Interface
- orchestrate_resources(request) → ResourceAllocation
- isolate_workload(workload) → IsolationDomain
- scale_capacity(metric) → ScalingDecision
- block_application(app_id, reason) → BlockResult

### Tier 3 (Application) Interface
- request_capability(capability) → CapabilityGrant
- submit_task(task) → TaskResult
- query_status() → Status
- register_service(service) → Registration

=== END FORMAL SPECIFICATION ===
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class InterfaceType(Enum):
    """Type of tier interface."""

    GOVERNANCE_INTERFACE = "governance"  # Tier 1 interface
    INFRASTRUCTURE_INTERFACE = "infrastructure"  # Tier 2 interface
    APPLICATION_INTERFACE = "application"  # Tier 3 interface


class RequestType(Enum):
    """Type of cross-tier request."""

    AUTHORITY_COMMAND = "authority_command"  # Downward authority
    CAPABILITY_REQUEST = "capability_request"  # Upward capability
    RESOURCE_ALLOCATION = "resource_allocation"  # Infrastructure operation
    ENFORCEMENT_ACTION = "enforcement_action"  # Governance enforcement


class EnforcementAction(Enum):
    """Actions that can be enforced cross-tier."""

    PAUSE_COMPONENT = "pause"
    RESUME_COMPONENT = "resume"
    BLOCK_OPERATION = "block"
    ALLOW_OPERATION = "allow"
    ROLLBACK_STATE = "rollback"
    TERMINATE_PROCESS = "terminate"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class TierRequest:
    """
    Represents a request between tiers.

    Validates authority flow (downward) and capability flow (upward).
    """

    request_id: str
    request_type: RequestType
    source_tier: int  # 1, 2, or 3
    target_tier: int  # 1, 2, or 3
    source_component: str
    target_component: str
    operation: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TierResponse:
    """Response to a tier request."""

    request_id: str
    success: bool
    result: Any
    error_message: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class GovernanceDecisionRequest:
    """Request for governance decision from Tier 1."""

    action: str
    context: dict[str, Any]
    requesting_tier: int
    requesting_component: str
    risk_level: str = "medium"
    requires_consensus: bool = False


@dataclass
class GovernanceDecisionResponse:
    """Response to governance decision request."""

    approved: bool
    reason: str
    council_votes: dict[str, Any] | None = None
    enforcement_actions: list[EnforcementAction] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocationRequest:
    """Request for resource allocation from Tier 2."""

    resource_type: str  # "memory", "compute", "storage", "network"
    amount: int
    priority: str  # "low", "medium", "high", "critical"
    requesting_component: str
    justification: str


@dataclass
class ResourceAllocationResponse:
    """Response to resource allocation request."""

    allocated: bool
    amount_granted: int
    allocation_id: str
    constraints: dict[str, Any] = field(default_factory=dict)
    expires_at: str | None = None


@dataclass
class BlockRequest:
    """Request to block a Tier 3 component (from Tier 2)."""

    component_id: str
    reason: str
    duration: str | None = None  # "permanent" or ISO duration
    requires_governance_approval: bool = True


@dataclass
class BlockResponse:
    """Response to block request."""

    blocked: bool
    block_id: str
    reason: str
    can_be_appealed: bool = True


# ============================================================================
# Abstract Tier Interfaces
# ============================================================================


class ITier1Governance(ABC):
    """
    Interface for Tier 1 (Governance) operations.

    This is the sovereign authority interface - all governance operations
    flow through this interface.

    AUTHORITY: Can command any tier
    CAPABILITY: Provides policy enforcement, audit, rollback
    """

    @abstractmethod
    def evaluate_action(
        self, request: GovernanceDecisionRequest
    ) -> GovernanceDecisionResponse:
        """
        Evaluate an action against governance policies.

        This is the primary authority mechanism - all significant actions
        must pass through governance evaluation.

        Args:
            request: Governance decision request

        Returns:
            GovernanceDecisionResponse with approval/denial
        """
        pass

    @abstractmethod
    def enforce_policy(
        self, policy_id: str, target_tier: int, target_component: str
    ) -> bool:
        """
        Enforce a policy on a lower tier.

        Args:
            policy_id: Policy to enforce
            target_tier: Target tier (2 or 3)
            target_component: Component to enforce on

        Returns:
            bool: True if enforcement succeeded
        """
        pass

    @abstractmethod
    def audit_operation(
        self, operation: str, tier: int, component: str, details: dict[str, Any]
    ) -> str:
        """
        Record an audit entry for an operation.

        Args:
            operation: Operation name
            tier: Tier that performed operation
            component: Component that performed operation
            details: Operation details

        Returns:
            str: Audit record ID
        """
        pass

    @abstractmethod
    def rollback_tier(self, tier: int, reason: str) -> bool:
        """
        Rollback a tier to previous state.

        Args:
            tier: Tier to rollback (2 or 3)
            reason: Reason for rollback

        Returns:
            bool: True if rollback succeeded
        """
        pass


class ITier2Infrastructure(ABC):
    """
    Interface for Tier 2 (Infrastructure) operations.

    This is the constrained control interface - infrastructure operations
    are subordinate to governance and can be paused/rolled back.

    AUTHORITY: Can block/control Tier 3 (with governance approval)
    CAPABILITY: Provides resource orchestration, isolation, scaling
    """

    @abstractmethod
    def allocate_resources(
        self, request: ResourceAllocationRequest
    ) -> ResourceAllocationResponse:
        """
        Allocate resources for a component.

        Args:
            request: Resource allocation request

        Returns:
            ResourceAllocationResponse with allocation details
        """
        pass

    @abstractmethod
    def isolate_workload(self, workload_id: str, isolation_level: str) -> str:
        """
        Create isolation domain for workload.

        Args:
            workload_id: Workload to isolate
            isolation_level: "low", "medium", "high"

        Returns:
            str: Isolation domain ID
        """
        pass

    @abstractmethod
    def scale_capacity(self, component_id: str, target_capacity: int) -> bool:
        """
        Scale capacity for a component.

        Args:
            component_id: Component to scale
            target_capacity: Target capacity level

        Returns:
            bool: True if scaling succeeded
        """
        pass

    @abstractmethod
    def block_application(self, request: BlockRequest) -> BlockResponse:
        """
        Block a Tier 3 application component.

        This requires governance approval for permanent blocks.

        Args:
            request: Block request

        Returns:
            BlockResponse with block details
        """
        pass


class ITier3Application(ABC):
    """
    Interface for Tier 3 (Application) operations.

    This is the sandboxed interface - applications have no enforcement
    authority and must request capabilities from higher tiers.

    AUTHORITY: None (sandboxed)
    CAPABILITY: Can request resources, submit tasks, query status
    """

    @abstractmethod
    def request_capability(self, capability: str, justification: str) -> bool:
        """
        Request a capability from higher tier.

        Args:
            capability: Capability to request
            justification: Reason for request

        Returns:
            bool: True if granted
        """
        pass

    @abstractmethod
    def submit_task(self, task: dict[str, Any]) -> str:
        """
        Submit a task for execution (routed through kernel).

        Args:
            task: Task definition

        Returns:
            str: Task ID
        """
        pass

    @abstractmethod
    def query_status(self) -> dict[str, Any]:
        """
        Query component status.

        Returns:
            dict: Status information
        """
        pass

    @abstractmethod
    def register_service(self, service_id: str, service_spec: dict[str, Any]) -> bool:
        """
        Register a service with the platform.

        Args:
            service_id: Service identifier
            service_spec: Service specification

        Returns:
            bool: True if registration succeeded
        """
        pass


# ============================================================================
# Interface Router
# ============================================================================


class TierInterfaceRouter:
    """
    Routes requests between tiers, enforcing authority and capability flow.

    CRITICAL RULES:
    - Authority flows downward: Tier 1 → Tier 2 → Tier 3
    - Capability flows upward: Tier 3 → Tier 2 → Tier 1
    - Cross-tier communication validated
    """

    def __init__(self):
        """Initialize the tier interface router."""
        self._tier1_interface: ITier1Governance | None = None
        self._tier2_interface: ITier2Infrastructure | None = None
        self._tier3_interfaces: dict[str, ITier3Application] = {}

        # Request tracking
        self._request_log: list[TierRequest] = []
        self._response_log: list[TierResponse] = []
        self._blocked_requests: list[TierRequest] = []

        logger.info("TierInterfaceRouter initialized")

    def register_tier1_interface(self, interface: ITier1Governance) -> None:
        """Register Tier 1 governance interface."""
        self._tier1_interface = interface
        logger.info("Registered Tier 1 Governance interface")

    def register_tier2_interface(self, interface: ITier2Infrastructure) -> None:
        """Register Tier 2 infrastructure interface."""
        self._tier2_interface = interface
        logger.info("Registered Tier 2 Infrastructure interface")

    def register_tier3_interface(
        self, component_id: str, interface: ITier3Application
    ) -> None:
        """Register Tier 3 application interface."""
        self._tier3_interfaces[component_id] = interface
        logger.info("Registered Tier 3 Application interface: %s", component_id)

    def route_request(self, request: TierRequest) -> TierResponse:
        """
        Route a request between tiers.

        Validates authority flow and capability flow.

        Args:
            request: Tier request

        Returns:
            TierResponse with result
        """
        logger.info(
            "Routing request %s: Tier %d → Tier %d",
            request.request_id,
            request.source_tier,
            request.target_tier,
        )

        # Validate request
        is_valid, reason = self._validate_request(request)
        if not is_valid:
            response = TierResponse(
                request_id=request.request_id,
                success=False,
                result=None,
                error_message=f"Request validation failed: {reason}",
            )
            self._blocked_requests.append(request)
            self._response_log.append(response)
            return response

        # Log request
        self._request_log.append(request)

        # Route based on request type and target tier
        try:
            result = self._execute_request(request)
            response = TierResponse(
                request_id=request.request_id,
                success=True,
                result=result,
            )
        except Exception as e:
            logger.error("Request execution failed: %s", e)
            response = TierResponse(
                request_id=request.request_id,
                success=False,
                result=None,
                error_message=str(e),
            )

        self._response_log.append(response)
        return response

    def _validate_request(self, request: TierRequest) -> tuple[bool, str]:
        """
        Validate request follows authority/capability flow rules.

        Rules:
        - Authority commands: Must flow downward (lower tier number → higher)
        - Capability requests: Must flow upward (higher tier number → lower)
        - Same-tier communication: Always allowed

        Returns:
            Tuple of (is_valid, reason)
        """
        # Same-tier communication is always valid
        if request.source_tier == request.target_tier:
            return True, "Same-tier communication"

        # Authority commands must flow downward
        if request.request_type == RequestType.AUTHORITY_COMMAND:
            if request.source_tier > request.target_tier:
                return False, "Authority cannot flow upward"
            return True, "Authority flows downward"

        # Capability requests must flow upward
        if request.request_type == RequestType.CAPABILITY_REQUEST:
            if request.source_tier < request.target_tier:
                return False, "Capability requests cannot flow downward"
            return True, "Capability flows upward"

        # Resource allocation: Tier 3 → Tier 2 or Tier 2 → Tier 1
        if request.request_type == RequestType.RESOURCE_ALLOCATION:
            if request.source_tier < request.target_tier:
                return False, "Resource requests cannot flow downward"
            return True, "Resource request flows upward"

        # Enforcement: Tier 1 → Tier 2/3 or Tier 2 → Tier 3
        if request.request_type == RequestType.ENFORCEMENT_ACTION:
            if request.source_tier > request.target_tier:
                return False, "Enforcement cannot flow upward"
            return True, "Enforcement flows downward"

        return True, "Request type validated"

    def _execute_request(self, request: TierRequest) -> Any:
        """Execute a validated request."""
        # Implementation would route to appropriate tier interface
        # For now, return acknowledgment
        return {
            "status": "acknowledged",
            "request_id": request.request_id,
            "message": f"Request routed: Tier {request.source_tier} → Tier {request.target_tier}",
        }

    def get_request_log(self) -> list[TierRequest]:
        """Get all logged requests."""
        return self._request_log.copy()

    def get_blocked_requests(self) -> list[TierRequest]:
        """Get all blocked requests."""
        return self._blocked_requests.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get routing statistics."""
        return {
            "total_requests": len(self._request_log),
            "successful_requests": sum(1 for r in self._response_log if r.success),
            "failed_requests": sum(1 for r in self._response_log if not r.success),
            "blocked_requests": len(self._blocked_requests),
        }


# ============================================================================
# Global Router Access
# ============================================================================


_global_router: TierInterfaceRouter | None = None


def get_tier_router() -> TierInterfaceRouter:
    """
    Get the global tier interface router.

    Returns:
        TierInterfaceRouter: Global router singleton
    """
    global _global_router
    if _global_router is None:
        _global_router = TierInterfaceRouter()
    return _global_router
