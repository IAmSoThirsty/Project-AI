"""
Cross-Tier Governance Policies - Rules for inter-tier enforcement and blocking.

This module defines formal governance policies that govern cross-tier interactions:
- When Tier 1 can pause/rollback Tier 2/3
- When Tier 2 can block Tier 3 applications
- Resource allocation quotas and constraints
- Escalation paths for policy violations

CRITICAL PRINCIPLES:
1. Authority flows downward (Tier 1 → Tier 2 → Tier 3)
2. Tier 2 blocks require governance approval for permanent actions
3. Temporary blocks (< 5 minutes) can be autonomous
4. All permanent blocks must be audited
5. Tier 3 has appeal mechanism for blocks

=== FORMAL SPECIFICATION ===

## Policy Hierarchy

### Level 1: Tier 1 Sovereign Policies (Absolute)
- Can pause any component in Tier 2/3
- Can rollback any tier to previous state
- Can override any Tier 2 block
- Requires Triumvirate consensus for core mutations

### Level 2: Tier 2 Infrastructure Policies (Constrained)
- Can temporarily block Tier 3 (<5 min) autonomously
- Permanent blocks require Tier 1 approval
- Can throttle resource allocation
- Must report all blocks to Tier 1

### Level 3: Tier 3 Application Policies (Sandboxed)
- No enforcement authority
- Can request capability grants
- Can appeal blocks to Tier 1
- Must operate within resource quotas

## Cross-Tier Rules

### Tier 1 → Tier 2 Rules
- Governance can pause infrastructure components
- Governance can impose resource constraints
- Infrastructure decisions are suggestions until validated
- Governance owns rollback authority

### Tier 1 → Tier 3 Rules
- Governance can terminate any application
- Governance can revoke capability grants
- Applications have no appeal against Tier 1 decisions

### Tier 2 → Tier 3 Rules
- Infrastructure can block applications
- Temporary blocks (<5 min): Autonomous
- Permanent blocks: Require Tier 1 approval
- Resource throttling: Autonomous with audit
- Applications can appeal to Tier 1

=== END FORMAL SPECIFICATION ===
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class PolicyLevel(Enum):
    """Level of policy in hierarchy."""

    SOVEREIGN = "sovereign"  # Tier 1 policies - absolute authority
    CONSTRAINED = "constrained"  # Tier 2 policies - require approval
    SANDBOXED = "sandboxed"  # Tier 3 policies - no enforcement


class BlockType(Enum):
    """Type of block that can be imposed."""

    TEMPORARY = "temporary"  # <5 minutes, autonomous
    EXTENDED = "extended"  # 5min-1hour, requires approval
    PERMANENT = "permanent"  # >1 hour or indefinite, requires consensus


class BlockReason(Enum):
    """Reason for blocking a component."""

    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_VIOLATION = "security_violation"
    POLICY_BREACH = "policy_breach"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    GOVERNANCE_ORDER = "governance_order"
    MAINTENANCE = "maintenance"


class AppealStatus(Enum):
    """Status of block appeal."""

    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"  # Block lifted
    DENIED = "denied"  # Block upheld
    ESCALATED = "escalated"  # Sent to Tier 1


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class BlockPolicy:
    """
    Policy governing when and how components can be blocked.
    
    Defines the rules for cross-tier blocking with different levels
    of authority and approval requirements.
    """

    policy_id: str
    policy_name: str
    level: PolicyLevel
    blocking_tier: int  # Which tier can apply this block
    target_tier: int  # Which tier is being blocked
    block_type: BlockType
    requires_approval: bool
    requires_audit: bool
    max_duration_seconds: int | None = None
    auto_lift: bool = False  # Auto-lift when duration expires
    can_be_appealed: bool = True


@dataclass
class BlockRecord:
    """Record of a component block."""

    block_id: str
    component_id: str
    component_name: str
    tier: int
    blocked_by: str  # Component that imposed block
    blocking_tier: int
    reason: BlockReason
    block_type: BlockType
    policy_id: str
    started_at: str
    expires_at: str | None = None
    lifted_at: str | None = None
    is_active: bool = True
    governance_approved: bool = False
    audit_recorded: bool = False


@dataclass
class BlockAppeal:
    """Appeal against a component block."""

    appeal_id: str
    block_id: str
    component_id: str
    appellant: str
    justification: str
    status: AppealStatus
    filed_at: str
    reviewed_at: str | None = None
    decision: str | None = None
    decided_by: str | None = None


@dataclass
class ResourceQuota:
    """Resource allocation quota for a tier or component."""

    quota_id: str
    tier: int
    component_id: str | None  # None = tier-wide quota
    resource_type: str  # "memory", "compute", "storage", "network"
    allocated_amount: int
    current_usage: int
    max_burst: int  # Temporary burst allowance
    enforcement_level: str  # "soft", "hard"
    throttle_when_exceeded: bool = True


@dataclass
class EscalationPath:
    """Escalation path for policy violations."""

    escalation_id: str
    trigger_condition: str
    from_tier: int
    to_tier: int
    action: str  # "notify", "block", "pause", "escalate"
    requires_review: bool
    timeout_seconds: int = 300  # 5 minutes default


# ============================================================================
# Policy Definitions
# ============================================================================


# Tier 1 → Tier 2/3 Policies (Sovereign Authority)
TIER1_PAUSE_POLICY = BlockPolicy(
    policy_id="tier1_pause_any",
    policy_name="Tier 1 Pause Authority",
    level=PolicyLevel.SOVEREIGN,
    blocking_tier=1,
    target_tier=2,  # Can target 2 or 3
    block_type=BlockType.PERMANENT,
    requires_approval=False,  # Tier 1 has sovereign authority
    requires_audit=True,
    can_be_appealed=False,  # Cannot appeal Tier 1 decisions
)

TIER1_ROLLBACK_POLICY = BlockPolicy(
    policy_id="tier1_rollback_any",
    policy_name="Tier 1 Rollback Authority",
    level=PolicyLevel.SOVEREIGN,
    blocking_tier=1,
    target_tier=2,
    block_type=BlockType.PERMANENT,
    requires_approval=False,
    requires_audit=True,
    can_be_appealed=False,
)

# Tier 2 → Tier 3 Policies (Constrained Authority)
TIER2_TEMPORARY_BLOCK_POLICY = BlockPolicy(
    policy_id="tier2_temp_block",
    policy_name="Tier 2 Temporary Block",
    level=PolicyLevel.CONSTRAINED,
    blocking_tier=2,
    target_tier=3,
    block_type=BlockType.TEMPORARY,
    requires_approval=False,  # <5 min blocks are autonomous
    requires_audit=True,
    max_duration_seconds=300,  # 5 minutes
    auto_lift=True,
    can_be_appealed=True,
)

TIER2_EXTENDED_BLOCK_POLICY = BlockPolicy(
    policy_id="tier2_extended_block",
    policy_name="Tier 2 Extended Block",
    level=PolicyLevel.CONSTRAINED,
    blocking_tier=2,
    target_tier=3,
    block_type=BlockType.EXTENDED,
    requires_approval=True,  # Requires Tier 1 approval
    requires_audit=True,
    max_duration_seconds=3600,  # 1 hour
    auto_lift=True,
    can_be_appealed=True,
)

TIER2_PERMANENT_BLOCK_POLICY = BlockPolicy(
    policy_id="tier2_permanent_block",
    policy_name="Tier 2 Permanent Block",
    level=PolicyLevel.CONSTRAINED,
    blocking_tier=2,
    target_tier=3,
    block_type=BlockType.PERMANENT,
    requires_approval=True,  # ALWAYS requires Tier 1 approval
    requires_audit=True,
    can_be_appealed=True,
)


# ============================================================================
# Policy Engine
# ============================================================================


class CrossTierPolicyEngine:
    """
    Engine for enforcing cross-tier governance policies.
    
    Responsibilities:
    - Validate block requests against policies
    - Enforce approval requirements
    - Track active blocks and appeals
    - Manage resource quotas
    - Handle escalations
    """

    def __init__(self):
        """Initialize the policy engine."""
        self._policies: dict[str, BlockPolicy] = {
            TIER1_PAUSE_POLICY.policy_id: TIER1_PAUSE_POLICY,
            TIER1_ROLLBACK_POLICY.policy_id: TIER1_ROLLBACK_POLICY,
            TIER2_TEMPORARY_BLOCK_POLICY.policy_id: TIER2_TEMPORARY_BLOCK_POLICY,
            TIER2_EXTENDED_BLOCK_POLICY.policy_id: TIER2_EXTENDED_BLOCK_POLICY,
            TIER2_PERMANENT_BLOCK_POLICY.policy_id: TIER2_PERMANENT_BLOCK_POLICY,
        }
        
        self._blocks: dict[str, BlockRecord] = {}
        self._appeals: dict[str, BlockAppeal] = {}
        self._quotas: dict[str, ResourceQuota] = {}
        self._escalations: list[EscalationPath] = []
        
        self._block_counter = 0
        self._appeal_counter = 0
        
        logger.info("CrossTierPolicyEngine initialized")
        logger.info("  Loaded %d policies", len(self._policies))

    def validate_block_request(
        self,
        blocking_tier: int,
        target_tier: int,
        block_type: BlockType,
    ) -> tuple[bool, str, BlockPolicy | None]:
        """
        Validate a block request against policies.
        
        Args:
            blocking_tier: Tier requesting the block
            target_tier: Tier being blocked
            block_type: Type of block
            
        Returns:
            Tuple of (is_valid, reason, policy)
        """
        # Authority must flow downward
        if blocking_tier > target_tier:
            return False, "Authority cannot flow upward", None
        
        # Find matching policy
        for policy in self._policies.values():
            if (
                policy.blocking_tier == blocking_tier
                and policy.target_tier == target_tier
                and policy.block_type == block_type
            ):
                return True, "Policy matched", policy
        
        return False, "No matching policy found", None

    def request_block(
        self,
        component_id: str,
        component_name: str,
        tier: int,
        blocked_by: str,
        blocking_tier: int,
        reason: BlockReason,
        block_type: BlockType,
        duration_seconds: int | None = None,
    ) -> tuple[bool, str, BlockRecord | None]:
        """
        Request to block a component.
        
        Args:
            component_id: Component to block
            component_name: Component name
            tier: Component tier
            blocked_by: Component requesting block
            blocking_tier: Tier requesting block
            reason: Reason for block
            block_type: Type of block
            duration_seconds: Duration (for temporary/extended blocks)
            
        Returns:
            Tuple of (success, reason, block_record)
        """
        # Validate request
        is_valid, validation_reason, policy = self.validate_block_request(
            blocking_tier, tier, block_type
        )
        
        if not is_valid:
            logger.warning("Block request denied: %s", validation_reason)
            return False, validation_reason, None
        
        # Check approval requirement
        if policy.requires_approval:
            # For now, automatic approval - in production, would route to Tier 1
            logger.info(
                "Block requires approval: %s → %s", blocked_by, component_id
            )
        
        # Calculate expiration
        started_at = datetime.now(UTC)
        expires_at = None
        
        if duration_seconds:
            expires_at = started_at + timedelta(seconds=duration_seconds)
        elif policy.max_duration_seconds:
            expires_at = started_at + timedelta(seconds=policy.max_duration_seconds)
        
        # Create block record
        block_id = f"block_{self._block_counter}"
        self._block_counter += 1
        
        block_record = BlockRecord(
            block_id=block_id,
            component_id=component_id,
            component_name=component_name,
            tier=tier,
            blocked_by=blocked_by,
            blocking_tier=blocking_tier,
            reason=reason,
            block_type=block_type,
            policy_id=policy.policy_id,
            started_at=started_at.isoformat(),
            expires_at=expires_at.isoformat() if expires_at else None,
            governance_approved=not policy.requires_approval,  # Auto-approved if no approval required
            audit_recorded=False,  # Will be recorded by audit system
        )
        
        self._blocks[block_id] = block_record
        
        logger.info(
            "Block imposed: %s [%s] on %s by %s - Reason: %s",
            block_id,
            block_type.value,
            component_id,
            blocked_by,
            reason.value,
        )
        
        return True, "Block imposed", block_record

    def lift_block(self, block_id: str, lifted_by: str) -> bool:
        """
        Lift an active block.
        
        Args:
            block_id: Block to lift
            lifted_by: Component lifting the block
            
        Returns:
            bool: True if block lifted
        """
        if block_id not in self._blocks:
            logger.warning("Block %s not found", block_id)
            return False
        
        block = self._blocks[block_id]
        
        if not block.is_active:
            logger.warning("Block %s already lifted", block_id)
            return False
        
        block.is_active = False
        block.lifted_at = datetime.now(UTC).isoformat()
        
        logger.info("Block lifted: %s by %s", block_id, lifted_by)
        return True

    def file_appeal(
        self,
        block_id: str,
        appellant: str,
        justification: str,
    ) -> tuple[bool, str, BlockAppeal | None]:
        """
        File an appeal against a block.
        
        Args:
            block_id: Block being appealed
            appellant: Component filing appeal
            justification: Reason for appeal
            
        Returns:
            Tuple of (success, reason, appeal)
        """
        if block_id not in self._blocks:
            return False, "Block not found", None
        
        block = self._blocks[block_id]
        
        # Check if block can be appealed
        policy = self._policies.get(block.policy_id)
        if policy and not policy.can_be_appealed:
            return False, "Block cannot be appealed (Tier 1 decision)", None
        
        # Create appeal
        appeal_id = f"appeal_{self._appeal_counter}"
        self._appeal_counter += 1
        
        appeal = BlockAppeal(
            appeal_id=appeal_id,
            block_id=block_id,
            component_id=block.component_id,
            appellant=appellant,
            justification=justification,
            status=AppealStatus.PENDING,
            filed_at=datetime.now(UTC).isoformat(),
        )
        
        self._appeals[appeal_id] = appeal
        
        logger.info(
            "Appeal filed: %s for block %s by %s",
            appeal_id,
            block_id,
            appellant,
        )
        
        return True, "Appeal filed", appeal

    def process_appeal(
        self,
        appeal_id: str,
        approved: bool,
        decided_by: str,
        decision: str,
    ) -> bool:
        """
        Process an appeal decision.
        
        Args:
            appeal_id: Appeal to process
            approved: Whether appeal is approved
            decided_by: Who made the decision
            decision: Decision rationale
            
        Returns:
            bool: True if processed
        """
        if appeal_id not in self._appeals:
            logger.warning("Appeal %s not found", appeal_id)
            return False
        
        appeal = self._appeals[appeal_id]
        appeal.status = AppealStatus.APPROVED if approved else AppealStatus.DENIED
        appeal.reviewed_at = datetime.now(UTC).isoformat()
        appeal.decided_by = decided_by
        appeal.decision = decision
        
        # If approved, lift the block
        if approved:
            self.lift_block(appeal.block_id, decided_by)
        
        logger.info(
            "Appeal %s %s by %s",
            appeal_id,
            "approved" if approved else "denied",
            decided_by,
        )
        
        return True

    def get_active_blocks(self, tier: int | None = None) -> list[BlockRecord]:
        """
        Get active blocks, optionally filtered by tier.
        
        Args:
            tier: Filter by tier (None = all)
            
        Returns:
            List of active blocks
        """
        blocks = [b for b in self._blocks.values() if b.is_active]
        
        if tier is not None:
            blocks = [b for b in blocks if b.tier == tier]
        
        return blocks

    def get_pending_appeals(self) -> list[BlockAppeal]:
        """Get all pending appeals."""
        return [
            a
            for a in self._appeals.values()
            if a.status == AppealStatus.PENDING
        ]

    def check_auto_lift_blocks(self) -> list[str]:
        """
        Check for expired blocks that should be auto-lifted.
        
        Returns:
            List of block IDs that were auto-lifted
        """
        now = datetime.now(UTC)
        lifted_blocks = []
        
        for block in self._blocks.values():
            if not block.is_active:
                continue
            
            if block.expires_at:
                expires = datetime.fromisoformat(block.expires_at)
                if now >= expires:
                    # Auto-lift expired block
                    policy = self._policies.get(block.policy_id)
                    if policy and policy.auto_lift:
                        self.lift_block(block.block_id, "auto_lift_system")
                        lifted_blocks.append(block.block_id)
        
        return lifted_blocks

    def get_statistics(self) -> dict[str, Any]:
        """Get policy engine statistics."""
        return {
            "total_policies": len(self._policies),
            "total_blocks": len(self._blocks),
            "active_blocks": len([b for b in self._blocks.values() if b.is_active]),
            "total_appeals": len(self._appeals),
            "pending_appeals": len(self.get_pending_appeals()),
            "approved_appeals": len(
                [a for a in self._appeals.values() if a.status == AppealStatus.APPROVED]
            ),
            "denied_appeals": len(
                [a for a in self._appeals.values() if a.status == AppealStatus.DENIED]
            ),
        }


# ============================================================================
# Global Policy Engine Access
# ============================================================================


_global_policy_engine: CrossTierPolicyEngine | None = None


def get_policy_engine() -> CrossTierPolicyEngine:
    """
    Get the global cross-tier policy engine.
    
    Returns:
        CrossTierPolicyEngine: Global engine singleton
    """
    global _global_policy_engine
    if _global_policy_engine is None:
        _global_policy_engine = CrossTierPolicyEngine()
    return _global_policy_engine
