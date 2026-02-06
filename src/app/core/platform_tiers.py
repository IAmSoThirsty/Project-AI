"""
Platform Tiers - Three-Tier Platform Strategy Implementation

This module implements the formal three-tier platform architecture:
- Tier 1: Governance / Enforcement Platform (Non-Negotiable Core)
- Tier 2: Infrastructure Control Platform (Constrained, Subordinate)
- Tier 3: Application / Runtime Platform (Optional, Replaceable)

CRITICAL CONSTRAINTS:
- Authority only flows downward (Tier 1 → Tier 2 → Tier 3)
- Capability flows upward (Tier 3 → Tier 2 → Tier 1)
- Tier 1 never depends on Tier 2 or 3
- Infrastructure decisions are suggestions until validated by governance
- Tier 3 is swappable without threatening Tier 1/2

=== FORMAL SPECIFICATION ===

## Tier 1 — Governance / Enforcement Platform (Non-Negotiable Core)

Role:
- Defines invariants
- Enforces policy
- Owns rollback
- Terminates ambiguity

Characteristics:
- Kernel-bound
- Deterministic
- Auditable
- Sovereign

Components:
- CognitionKernel (trust root)
- GovernanceService (policy enforcement)
- Triumvirate (three-council governance)
- Four Laws (ethical constraints)
- Identity System (immutable snapshots)

Rule:
This tier must never depend on Tiers 2 or 3 to function.
If everything else dies, this still holds the line.

## Tier 2 — Infrastructure Control Platform (Constrained, Subordinate)

Role:
- Resource orchestration
- Placement decisions
- Isolation domains
- Elasticity coordination

Characteristics:
- Responds to Tier-1 decisions
- Cannot override enforcement
- Can be paused, rolled back, or constrained by Tier 1

Components:
- GlobalWatchTower (security infrastructure)
- MemoryEngine (storage orchestration)
- ExecutionService (execution infrastructure)
- SecurityEnforcer (ASL-3 controls)
- TARL enforcement (code integrity)

Rule:
Infrastructure decisions are suggestions until validated by governance.

## Tier 3 — Application / Runtime Platform (Optional, Replaceable)

Role:
- Runtime services
- APIs
- SDKs
- Developer surfaces
- Product experiences

Characteristics:
- Fully sandboxed
- No enforcement authority
- No sovereignty
- Disposable

Components:
- CouncilHub (agent registry)
- All agents (defense, expert, planner, etc.)
- GUI Dashboard (user interface)
- Plugin system
- API endpoints

Rule:
Tier-3 must be swappable without threatening Tier-1 or Tier-2.

=== END FORMAL SPECIFICATION ===
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class PlatformTier(Enum):
    """
    Platform tier classification.

    Authority flows downward: TIER_1 > TIER_2 > TIER_3
    Capability flows upward: TIER_3 → TIER_2 → TIER_1
    """

    TIER_1_GOVERNANCE = 1  # Sovereign, non-negotiable core
    TIER_2_INFRASTRUCTURE = 2  # Subordinate, constrained control
    TIER_3_APPLICATION = 3  # Replaceable, sandboxed runtime


class AuthorityLevel(Enum):
    """Authority level for tier components."""

    SOVEREIGN = "sovereign"  # Tier 1 only - absolute authority
    CONSTRAINED = "constrained"  # Tier 2 only - validated authority
    SANDBOXED = "sandboxed"  # Tier 3 only - no authority


class ComponentRole(Enum):
    """Role classification for platform components."""

    # Tier 1 roles
    GOVERNANCE_CORE = "governance_core"
    POLICY_ENFORCER = "policy_enforcer"
    INVARIANT_GUARDIAN = "invariant_guardian"

    # Tier 2 roles
    RESOURCE_ORCHESTRATOR = "resource_orchestrator"
    INFRASTRUCTURE_CONTROLLER = "infrastructure_controller"
    ISOLATION_MANAGER = "isolation_manager"

    # Tier 3 roles
    RUNTIME_SERVICE = "runtime_service"
    API_SURFACE = "api_surface"
    USER_INTERFACE = "user_interface"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class TierComponent:
    """
    Represents a component registered in the platform tier system.

    Immutable after registration to ensure tier integrity.
    """

    component_id: str
    component_name: str
    tier: PlatformTier
    authority_level: AuthorityLevel
    role: ComponentRole
    component_ref: Any  # Reference to actual component
    dependencies: list[str] = field(default_factory=list)
    can_be_paused: bool = True
    can_be_replaced: bool = False
    registered_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TierBoundaryViolation:
    """Records a violation of tier boundary rules."""

    violation_id: str
    violation_type: (
        str  # "upward_authority", "tier_1_dependency", "unauthorized_enforcement"
    )
    source_component: str
    target_component: str
    source_tier: PlatformTier
    target_tier: PlatformTier
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TierHealthStatus:
    """Health status for a platform tier."""

    tier: PlatformTier
    is_operational: bool
    component_count: int
    active_components: int
    paused_components: int
    failed_components: int
    last_check: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ============================================================================
# Tier Registry
# ============================================================================


class TierRegistry:
    """
    Central registry for platform tier components.

    Enforces tier boundaries and authority flow constraints:
    - Authority only flows downward (Tier 1 → Tier 2 → Tier 3)
    - Capability flows upward (Tier 3 → Tier 2 → Tier 1)
    - Tier 1 never depends on Tier 2/3
    - Infrastructure decisions validated by governance
    - Tier 3 is swappable

    Thread-safe singleton pattern.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the tier registry (singleton pattern)."""
        if self._initialized:
            return

        self._components: dict[str, TierComponent] = {}
        self._tier_1_components: list[str] = []
        self._tier_2_components: list[str] = []
        self._tier_3_components: list[str] = []
        self._violations: list[TierBoundaryViolation] = []
        self._paused_components: set[str] = set()

        self._initialized = True
        logger.info("TierRegistry initialized")

    def register_component(
        self,
        component_id: str,
        component_name: str,
        tier: PlatformTier,
        authority_level: AuthorityLevel,
        role: ComponentRole,
        component_ref: Any,
        dependencies: list[str] | None = None,
        can_be_paused: bool = True,
        can_be_replaced: bool = False,
    ) -> TierComponent:
        """
        Register a component in the tier system.

        Args:
            component_id: Unique identifier
            component_name: Human-readable name
            tier: Platform tier classification
            authority_level: Authority level for the component
            role: Component role classification
            component_ref: Reference to actual component
            dependencies: List of component IDs this depends on
            can_be_paused: Whether Tier-1 can pause this component
            can_be_replaced: Whether component is replaceable

        Returns:
            TierComponent: Registered component

        Raises:
            ValueError: If tier boundaries are violated
        """
        if component_id in self._components:
            logger.warning("Component %s already registered, updating", component_id)

        # Validate tier/authority alignment
        self._validate_tier_authority_alignment(tier, authority_level)

        # Validate dependencies (Tier 1 cannot depend on Tier 2/3)
        if dependencies:
            self._validate_dependencies(tier, dependencies)

        component = TierComponent(
            component_id=component_id,
            component_name=component_name,
            tier=tier,
            authority_level=authority_level,
            role=role,
            component_ref=component_ref,
            dependencies=dependencies or [],
            can_be_paused=can_be_paused,
            can_be_replaced=can_be_replaced,
        )

        self._components[component_id] = component

        # Add to tier-specific tracking
        if tier == PlatformTier.TIER_1_GOVERNANCE:
            self._tier_1_components.append(component_id)
        elif tier == PlatformTier.TIER_2_INFRASTRUCTURE:
            self._tier_2_components.append(component_id)
        else:
            self._tier_3_components.append(component_id)

        logger.info(
            "Registered component: %s [%s] - Tier %s, Authority: %s",
            component_name,
            component_id,
            tier.value,
            authority_level.value,
        )

        return component

    def _validate_tier_authority_alignment(
        self, tier: PlatformTier, authority: AuthorityLevel
    ) -> None:
        """Validate that tier and authority level are aligned."""
        if tier == PlatformTier.TIER_1_GOVERNANCE:
            if authority != AuthorityLevel.SOVEREIGN:
                raise ValueError(
                    f"Tier 1 components must have SOVEREIGN authority, got {authority}"
                )
        elif tier == PlatformTier.TIER_2_INFRASTRUCTURE:
            if authority != AuthorityLevel.CONSTRAINED:
                raise ValueError(
                    f"Tier 2 components must have CONSTRAINED authority, got {authority}"
                )
        elif tier == PlatformTier.TIER_3_APPLICATION:
            if authority != AuthorityLevel.SANDBOXED:
                raise ValueError(
                    f"Tier 3 components must have SANDBOXED authority, got {authority}"
                )

    def _validate_dependencies(
        self, tier: PlatformTier, dependencies: list[str]
    ) -> None:
        """
        Validate dependencies don't violate tier boundaries.

        CRITICAL: Tier 1 must never depend on Tier 2 or 3.
        """
        for dep_id in dependencies:
            if dep_id not in self._components:
                logger.warning("Dependency %s not yet registered", dep_id)
                continue

            dep_component = self._components[dep_id]

            # Tier 1 cannot depend on Tier 2/3
            if tier == PlatformTier.TIER_1_GOVERNANCE:
                if dep_component.tier != PlatformTier.TIER_1_GOVERNANCE:
                    violation = TierBoundaryViolation(
                        violation_id=f"dep_{len(self._violations)}",
                        violation_type="tier_1_dependency",
                        source_component="<new_component>",
                        target_component=dep_id,
                        source_tier=tier,
                        target_tier=dep_component.tier,
                        description=f"Tier 1 component cannot depend on {dep_component.tier.name}",
                    )
                    self._violations.append(violation)
                    raise ValueError(
                        f"Tier 1 cannot depend on Tier 2/3: {dep_id} is {dep_component.tier.name}"
                    )

    def validate_authority_flow(
        self,
        source_component_id: str,
        target_component_id: str,
        action: str,
    ) -> tuple[bool, str]:
        """
        Validate that authority flow is downward only.

        Authority flows: Tier 1 → Tier 2 → Tier 3

        Args:
            source_component_id: Component initiating action
            target_component_id: Component receiving action
            action: Description of action

        Returns:
            Tuple of (is_valid, reason)
        """
        if source_component_id not in self._components:
            return False, f"Source component {source_component_id} not registered"

        if target_component_id not in self._components:
            return False, f"Target component {target_component_id} not registered"

        source = self._components[source_component_id]
        target = self._components[target_component_id]

        # Authority can only flow downward
        if source.tier.value > target.tier.value:
            # Upward authority flow - violation
            violation = TierBoundaryViolation(
                violation_id=f"auth_{len(self._violations)}",
                violation_type="upward_authority",
                source_component=source_component_id,
                target_component=target_component_id,
                source_tier=source.tier,
                target_tier=target.tier,
                description=f"Authority cannot flow upward: {source.tier.name} → {target.tier.name}",
            )
            self._violations.append(violation)
            return (
                False,
                f"Authority flow violation: {source.tier.name} cannot command {target.tier.name}",
            )

        # Authority flows downward - valid
        return True, "Authority flow valid"

    def pause_component(self, component_id: str) -> bool:
        """
        Pause a component (Tier-1 authority only).

        Args:
            component_id: Component to pause

        Returns:
            bool: True if paused successfully
        """
        if component_id not in self._components:
            logger.error("Cannot pause unknown component: %s", component_id)
            return False

        component = self._components[component_id]

        if not component.can_be_paused:
            logger.error("Component %s cannot be paused", component_id)
            return False

        self._paused_components.add(component_id)
        logger.info("Paused component: %s [%s]", component.component_name, component_id)
        return True

    def resume_component(self, component_id: str) -> bool:
        """
        Resume a paused component.

        Args:
            component_id: Component to resume

        Returns:
            bool: True if resumed successfully
        """
        if component_id in self._paused_components:
            self._paused_components.remove(component_id)
            logger.info("Resumed component: %s", component_id)
            return True
        return False

    def is_component_paused(self, component_id: str) -> bool:
        """Check if a component is paused."""
        return component_id in self._paused_components

    def get_tier_health(self, tier: PlatformTier) -> TierHealthStatus:
        """
        Get health status for a tier.

        Args:
            tier: Tier to check

        Returns:
            TierHealthStatus: Health status
        """
        if tier == PlatformTier.TIER_1_GOVERNANCE:
            component_ids = self._tier_1_components
        elif tier == PlatformTier.TIER_2_INFRASTRUCTURE:
            component_ids = self._tier_2_components
        else:
            component_ids = self._tier_3_components

        active = sum(1 for cid in component_ids if cid not in self._paused_components)
        paused = len(self._paused_components.intersection(component_ids))

        return TierHealthStatus(
            tier=tier,
            is_operational=len(component_ids) > 0 and active > 0,
            component_count=len(component_ids),
            active_components=active,
            paused_components=paused,
            failed_components=0,  # TODO: Track failures
        )

    def get_all_violations(self) -> list[TierBoundaryViolation]:
        """Get all tier boundary violations."""
        return self._violations.copy()

    def get_component(self, component_id: str) -> TierComponent | None:
        """Get a registered component by ID."""
        return self._components.get(component_id)

    def get_tier_components(self, tier: PlatformTier) -> list[TierComponent]:
        """Get all components in a specific tier."""
        return [c for c in self._components.values() if c.tier == tier]

    def get_all_components(self) -> dict[str, TierComponent]:
        """Get all registered components."""
        return self._components.copy()


# ============================================================================
# Global Registry Access
# ============================================================================


def get_tier_registry() -> TierRegistry:
    """
    Get the global tier registry instance.

    Returns:
        TierRegistry: Global registry singleton
    """
    return TierRegistry()
