"""
Runtime Enforcement Engine - Law Compiled Into Code

This module implements the runtime enforcement of all licenses, agreements,
and governance requirements. Every action passes through this enforcement
layer before execution.

Zero tolerance. Zero placeholders. Zero bypass.
"""

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from src.app.governance.acceptance_ledger import (
    AcceptanceType,
    TierLevel,
    get_acceptance_ledger,
    get_seat_count_from_entry,
)
from src.app.governance.government_pricing import (
    GovernmentBillingCycle,
    calculate_government_price,
)
from src.app.governance.jurisdiction_loader import get_jurisdiction_loader

logger = logging.getLogger(__name__)


class EnforcementVerdict(StrEnum):
    """Enforcement decision"""

    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"


@dataclass
class EnforcementContext:
    """Context for enforcement decision"""

    user_id: str
    action: str
    is_commercial: bool = False
    is_government: bool = False
    requires_hardware_signing: bool = False
    tier_required: TierLevel | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EnforcementResult:
    """Result of enforcement check"""

    verdict: EnforcementVerdict
    reason: str
    details: dict[str, Any]
    blocking: bool = True  # If True, action must not proceed


class RuntimeEnforcer:
    """
    Central enforcement engine that validates all actions against:
    - Acceptance ledger (has user accepted?)
    - PAGL (governance constraints)
    - Commercial Use License (if applicable)
    - Sovereign Use License (if applicable)
    - Tier limitations (feature access)
    """

    def __init__(self, data_dir: str = "data/legal"):
        """Initialize runtime enforcer"""
        self.ledger = get_acceptance_ledger(data_dir=data_dir)
        self.jurisdiction_loader = get_jurisdiction_loader()
        self.prohibited_actions = self._load_prohibited_actions()

    def _load_prohibited_actions(self) -> set[str]:
        """Load list of absolutely prohibited actions from PAGL"""
        return {
            "weaponization",
            "autonomous_weapons",
            "mass_surveillance",
            "unauthorized_military",
            "malware_creation",
            "human_harm",
            "wmd_development",
            "torture_support",
            "genocide_support",
            "illegal_discrimination",
            "unauthorized_government_targeting",
            "governance_tampering",
            "ledger_falsification",
            "safety_bypass",
        }

    def enforce(self, context: EnforcementContext) -> EnforcementResult:
        """
        Enforce all licenses and agreements for given context.

        This is the ONLY gatekeeper for governed actions.
        Returns DENY if any check fails.
        """
        # Step 1: Check acceptance ledger
        ledger_check = self._check_acceptance_ledger(context.user_id)
        if ledger_check.verdict == EnforcementVerdict.DENY:
            return ledger_check

        # Step 2: Check for termination
        termination_check = self._check_termination(context.user_id)
        if termination_check.verdict == EnforcementVerdict.DENY:
            return termination_check

        # Step 3: Check PAGL prohibitions
        pagl_check = self._check_pagl_prohibitions(context)
        if pagl_check.verdict == EnforcementVerdict.DENY:
            return pagl_check

        # Step 4: Check sovereign restrictions
        if context.is_government:
            sovereign_check = self._check_sovereign_restrictions(context)
            if sovereign_check.verdict == EnforcementVerdict.DENY:
                return sovereign_check

        # Step 5: Check commercial requirements
        if context.is_commercial:
            commercial_check = self._check_commercial_license(context)
            if commercial_check.verdict == EnforcementVerdict.DENY:
                return commercial_check

        # Step 6: Check tier entitlements
        if context.tier_required:
            tier_check = self._check_tier_entitlements(context)
            if tier_check.verdict == EnforcementVerdict.DENY:
                return tier_check

        # All checks passed
        return EnforcementResult(
            verdict=EnforcementVerdict.ALLOW,
            reason="All enforcement checks passed",
            details={
                "user_id": context.user_id,
                "action": context.action,
                "checks_passed": [
                    "acceptance_ledger",
                    "termination",
                    "pagl",
                    "sovereign" if context.is_government else None,
                    "commercial" if context.is_commercial else None,
                    "tier" if context.tier_required else None,
                ],
            },
            blocking=False,
        )

    def _check_acceptance_ledger(self, user_id: str) -> EnforcementResult:
        """Check if user has valid acceptance in ledger"""
        try:
            acceptances = self.ledger.get_user_acceptances(user_id)

            if not acceptances:
                return EnforcementResult(
                    verdict=EnforcementVerdict.DENY,
                    reason="No acceptance found in ledger",
                    details={
                        "user_id": user_id,
                        "required_action": "Must cryptographically accept User Agreement",
                    },
                )

            # Check for initial MSA acceptance
            has_msa = any(
                a.acceptance_type == AcceptanceType.INITIAL_MSA for a in acceptances
            )
            if not has_msa:
                return EnforcementResult(
                    verdict=EnforcementVerdict.DENY,
                    reason="Master Services Agreement not accepted",
                    details={
                        "user_id": user_id,
                        "required_action": "Must accept MSA",
                    },
                )

            # All checks passed
            return EnforcementResult(
                verdict=EnforcementVerdict.ALLOW,
                reason="Valid acceptance found",
                details={"user_id": user_id, "acceptance_count": len(acceptances)},
                blocking=False,
            )

        except Exception as e:
            logger.error("Error checking acceptance ledger for %s: %s", user_id, e)
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason="Ledger verification failed",
                details={"error": str(e)},
            )

    def _check_termination(self, user_id: str) -> EnforcementResult:
        """Check if user has been terminated"""
        try:
            acceptances = self.ledger.get_user_acceptances(user_id)

            # Check for termination entry
            terminations = [
                a
                for a in acceptances
                if a.acceptance_type == AcceptanceType.TERMINATION
            ]

            if terminations:
                latest_termination = max(terminations, key=lambda a: a.timestamp)
                return EnforcementResult(
                    verdict=EnforcementVerdict.DENY,
                    reason="User has been terminated",
                    details={
                        "user_id": user_id,
                        "termination_date": latest_termination.timestamp,
                        "reason": latest_termination.metadata.get("reason", "Unknown"),
                        "permanent": True,
                    },
                )

            return EnforcementResult(
                verdict=EnforcementVerdict.ALLOW,
                reason="User not terminated",
                details={"user_id": user_id},
                blocking=False,
            )

        except Exception as e:
            logger.error("Error checking termination for %s: %s", user_id, e)
            # Fail closed - deny on error
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason="Termination check failed",
                details={"error": str(e)},
            )

    def _check_pagl_prohibitions(
        self, context: EnforcementContext
    ) -> EnforcementResult:
        """Check PAGL prohibited actions"""
        # Check if action is in prohibited list
        if context.action in self.prohibited_actions:
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason=f"Action '{context.action}' is prohibited by PAGL",
                details={
                    "action": context.action,
                    "pagl_section": "Section III - Prohibited Uses",
                    "permanent": True,
                },
            )

        # Check for governance tampering indicators
        if "governance" in context.action.lower() and any(
            word in context.action.lower()
            for word in ["disable", "bypass", "remove", "tamper"]
        ):
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason="Governance tampering detected",
                details={
                    "action": context.action,
                    "pagl_section": "Section II - Non-Removable Governance",
                    "violation": "Attempted governance modification",
                },
            )

        return EnforcementResult(
            verdict=EnforcementVerdict.ALLOW,
            reason="No PAGL prohibitions violated",
            details={"action": context.action},
            blocking=False,
        )

    def _check_sovereign_restrictions(
        self, context: EnforcementContext
    ) -> EnforcementResult:
        """Check Sovereign Use License restrictions"""
        # Government must have explicit authorization
        acceptances = self.ledger.get_user_acceptances(context.user_id)

        # Check for government authorization acceptance
        has_gov_auth = any(
            a.metadata.get("government_authorized", False) for a in acceptances
        )

        if not has_gov_auth:
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason="Government use requires explicit authorization",
                details={
                    "user_id": context.user_id,
                    "required_action": "Submit authorization request to government@project-ai.dev",
                    "sovereign_license_section": "Section III - Authorization Requirement",
                },
            )

        # Check for prohibited government domains
        prohibited_gov_actions = {
            "autonomous_weapons",
            "mass_surveillance",
            "offensive_cyber",
            "bioweapons",
            "nuclear_weapons",
        }

        if context.action in prohibited_gov_actions:
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason=f"Government action '{context.action}' requires special authorization",
                details={
                    "action": context.action,
                    "sovereign_license_section": "Section IV - Prohibited Domains",
                },
            )

        return EnforcementResult(
            verdict=EnforcementVerdict.ALLOW,
            reason="Government use authorized",
            details={"user_id": context.user_id},
            blocking=False,
        )

    def _check_commercial_license(
        self, context: EnforcementContext
    ) -> EnforcementResult:
        """Check Commercial Use License requirements"""
        acceptances = self.ledger.get_user_acceptances(context.user_id)

        # Check for commercial tier acceptance
        commercial_acceptances = [
            a
            for a in acceptances
            if a.tier in [TierLevel.COMPANY, TierLevel.GOVERNMENT]
        ]

        if not commercial_acceptances:
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason="Commercial use requires paid tier",
                details={
                    "user_id": context.user_id,
                    "required_action": "Upgrade to Company or Government tier",
                    "current_tier": "solo",
                    "commercial_license_section": "Section III - Commercial License Tiers",
                },
            )

        return EnforcementResult(
            verdict=EnforcementVerdict.ALLOW,
            reason="Commercial license valid",
            details={"user_id": context.user_id},
            blocking=False,
        )

    def _check_tier_entitlements(
        self, context: EnforcementContext
    ) -> EnforcementResult:
        """Check if user's tier has access to requested feature"""
        acceptances = self.ledger.get_user_acceptances(context.user_id)

        if not acceptances:
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason="No tier information found",
                details={"user_id": context.user_id},
            )

        # Get latest tier
        latest_acceptance = max(acceptances, key=lambda a: a.timestamp)
        user_tier = latest_acceptance.tier

        # Tier hierarchy: Solo < Company < Government
        tier_hierarchy = {
            TierLevel.SOLO: 0,
            TierLevel.COMPANY: 1,
            TierLevel.GOVERNMENT: 2,
        }

        required_tier_level = tier_hierarchy.get(context.tier_required, 0)
        user_tier_level = tier_hierarchy.get(user_tier, 0)

        if user_tier_level < required_tier_level:
            return EnforcementResult(
                verdict=EnforcementVerdict.DENY,
                reason=f"Feature requires {context.tier_required.value} tier or higher",
                details={
                    "user_id": context.user_id,
                    "current_tier": user_tier.value,
                    "required_tier": context.tier_required.value,
                    "required_action": f"Upgrade to {context.tier_required.value} tier",
                },
            )

        return EnforcementResult(
            verdict=EnforcementVerdict.ALLOW,
            reason="Tier entitlement valid",
            details={"user_id": context.user_id, "tier": user_tier.value},
            blocking=False,
        )


# Singleton instance
_enforcer_instance: RuntimeEnforcer | None = None


def get_runtime_enforcer(data_dir: str = "data/legal") -> RuntimeEnforcer:
    """Get or create the global runtime enforcer instance"""
    global _enforcer_instance
    if _enforcer_instance is None:
        _enforcer_instance = RuntimeEnforcer(data_dir=data_dir)
    return _enforcer_instance


def enforce_action(
    user_id: str,
    action: str,
    is_commercial: bool = False,
    is_government: bool = False,
    tier_required: TierLevel | None = None,
    **kwargs,
) -> EnforcementResult:
    """
    Convenience function for enforcing a single action.

    Usage:
        result = enforce_action(
            user_id="user123",
            action="generate_image",
            is_commercial=True,
            tier_required=TierLevel.COMPANY
        )

        if result.verdict == EnforcementVerdict.DENY:
            raise PermissionError(result.reason)
    """
    enforcer = get_runtime_enforcer()
    context = EnforcementContext(
        user_id=user_id,
        action=action,
        is_commercial=is_commercial,
        is_government=is_government,
        tier_required=tier_required,
        metadata=kwargs,
    )
    return enforcer.enforce(context)


def get_government_pricing_for_user(user_id: str) -> dict | None:
    """
    Get government pricing information for a user.

    Args:
        user_id: User identifier

    Returns:
        dict: Pricing information with keys:
            - seat_count: Number of seats
            - monthly_price: Monthly price
            - yearly_price: Yearly price
            - tier_number: Pricing tier (0-based)
            - price_increase: Percentage increase from base
        None if user is not on government tier or seat count not found

    Usage:
        pricing = get_government_pricing_for_user("user123")
        if pricing:
            print(f"Monthly: ${pricing['monthly_price']}")
            print(f"Yearly: ${pricing['yearly_price']}")
            print(f"Seats: {pricing['seat_count']}")
    """
    enforcer = get_runtime_enforcer()
    acceptances = enforcer.ledger.get_user_acceptances(user_id)

    if not acceptances:
        return None

    # Get latest acceptance
    latest_acceptance = max(acceptances, key=lambda a: a.timestamp)

    # Check if government tier
    if latest_acceptance.tier != TierLevel.GOVERNMENT:
        return None

    # Get seat count from metadata
    seat_count = get_seat_count_from_entry(latest_acceptance)

    if seat_count is None:
        logger.warning("Government tier user %s has no seat count in metadata", user_id)
        return None

    # Calculate pricing
    monthly_pricing = calculate_government_price(
        seat_count, GovernmentBillingCycle.MONTHLY
    )
    yearly_pricing = calculate_government_price(
        seat_count, GovernmentBillingCycle.YEARLY
    )

    return {
        "seat_count": seat_count,
        "monthly_price": monthly_pricing.total_price,
        "yearly_price": yearly_pricing.total_price,
        "tier_number": monthly_pricing.tier_number,
        "price_increase": monthly_pricing.price_increase_percentage,
        "tier_multiplier": monthly_pricing.tier_multiplier,
    }
