#!/usr/bin/env python3
"""
Composite Invariants System
Enforces cross-domain physical coherence beyond individual conservation laws.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from engines.alien_invaders.modules.world_state import GlobalState

logger = logging.getLogger(__name__)


@dataclass
class InvariantViolation:
    """Represents a violated invariant."""

    invariant_name: str
    description: str
    state_snapshot: dict[str, Any] = field(default_factory=dict)
    severity: str = "critical"  # low, medium, high, critical


class CompositeInvariant:
    """
    Base class for composite invariants that enforce cross-domain coherence.

    Composite invariants validate that changes in one domain properly
    cascade to related domains, preventing physically impossible states.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize composite invariant.

        Args:
            name: Invariant identifier
            description: Human-readable description
        """
        self.name = name
        self.description = description

    def validate(self, state: GlobalState, prev_state: GlobalState | None = None) -> list[InvariantViolation]:
        """
        Validate the invariant against current and previous state.

        Args:
            state: Current global state
            prev_state: Previous state for delta calculations

        Returns:
            List of violations (empty if valid)
        """
        raise NotImplementedError("Subclasses must implement validate()")


class ResourceEconomicInvariant(CompositeInvariant):
    """
    Invariant: Resource depletion must cascade to economic impact.

    Validates that significant resource extraction causes proportional GDP decline.
    """

    def __init__(self, depletion_threshold: float = 0.1, gdp_sensitivity: float = 0.5):
        """
        Initialize resource-economic invariant.

        Args:
            depletion_threshold: Minimum depletion to trigger check (e.g., 0.1 = 10%)
            gdp_sensitivity: Expected GDP impact ratio (0.5 = 50% of depletion)
        """
        super().__init__(
            "resource_economic_coherence",
            "Resource depletion must cause proportional economic impact",
        )
        self.depletion_threshold = depletion_threshold
        self.gdp_sensitivity = gdp_sensitivity

    def validate(self, state: GlobalState, prev_state: GlobalState | None = None) -> list[InvariantViolation]:
        violations = []

        if prev_state is None:
            return violations  # No previous state to compare

        # Calculate average resource depletion
        prev_resources = prev_state.remaining_resources
        curr_resources = state.remaining_resources

        total_depletion = 0.0
        resource_count = 0

        for resource, curr_amount in curr_resources.items():
            if resource in prev_resources:
                prev_amount = prev_resources[resource]
                depletion = prev_amount - curr_amount
                if depletion > 0:
                    total_depletion += depletion
                    resource_count += 1

        if resource_count == 0:
            return violations

        avg_depletion = total_depletion / resource_count

        # Check if depletion is significant
        if avg_depletion < self.depletion_threshold:
            return violations  # Below threshold, no check needed

        # Calculate GDP change
        prev_gdp = prev_state.get_total_gdp()
        curr_gdp = state.get_total_gdp()

        if prev_gdp == 0:
            return violations

        gdp_change_ratio = (prev_gdp - curr_gdp) / prev_gdp
        expected_min_impact = avg_depletion * self.gdp_sensitivity

        # Violation if GDP didn't decline proportionally
        if gdp_change_ratio < expected_min_impact * 0.5:  # Allow 50% tolerance
            violations.append(
                InvariantViolation(
                    invariant_name=self.name,
                    description=f"Resource depletion ({avg_depletion:.2%}) without proportional GDP impact "
                    f"(expected ≥{expected_min_impact:.2%}, got {gdp_change_ratio:.2%})",
                    state_snapshot={
                        "avg_resource_depletion": avg_depletion,
                        "gdp_change_ratio": gdp_change_ratio,
                        "expected_min_impact": expected_min_impact,
                    },
                    severity="high",
                )
            )

        return violations


class EconomicSocietalInvariant(CompositeInvariant):
    """
    Invariant: Economic collapse must impact societal metrics.

    Validates that GDP decline causes proportional morale/stability decline.
    """

    def __init__(self, gdp_threshold: float = 0.15, morale_sensitivity: float = 0.3):
        """
        Initialize economic-societal invariant.

        Args:
            gdp_threshold: Minimum GDP decline to trigger check
            morale_sensitivity: Expected morale impact ratio
        """
        super().__init__("economic_societal_coherence", "Economic decline must cause societal impact")
        self.gdp_threshold = gdp_threshold
        self.morale_sensitivity = morale_sensitivity

    def validate(self, state: GlobalState, prev_state: GlobalState | None = None) -> list[InvariantViolation]:
        violations = []

        if prev_state is None:
            return violations

        # Calculate GDP decline
        prev_gdp = prev_state.get_total_gdp()
        curr_gdp = state.get_total_gdp()

        if prev_gdp == 0:
            return violations

        gdp_decline = (prev_gdp - curr_gdp) / prev_gdp

        if gdp_decline < self.gdp_threshold:
            return violations  # Below threshold

        # Calculate morale change
        prev_morale = prev_state.get_average_morale()
        curr_morale = state.get_average_morale()

        morale_decline = prev_morale - curr_morale
        expected_min_decline = gdp_decline * self.morale_sensitivity

        # Violation if morale didn't decline
        if morale_decline < expected_min_decline * 0.5:
            violations.append(
                InvariantViolation(
                    invariant_name=self.name,
                    description=f"GDP decline ({gdp_decline:.2%}) without morale impact "
                    f"(expected ≥{expected_min_decline:.2f}, got {morale_decline:.2f})",
                    state_snapshot={
                        "gdp_decline": gdp_decline,
                        "morale_decline": morale_decline,
                        "expected_min_decline": expected_min_decline,
                    },
                    severity="high",
                )
            )

        return violations


class SocietalPoliticalInvariant(CompositeInvariant):
    """
    Invariant: Low morale must impact political stability.

    Validates that sustained low morale causes government instability.
    """

    def __init__(self, morale_threshold: float = 0.3, stability_impact: float = 0.2):
        """
        Initialize societal-political invariant.

        Args:
            morale_threshold: Morale level that triggers instability
            stability_impact: Expected stability decline per tick at low morale
        """
        super().__init__(
            "societal_political_coherence",
            "Low morale must cause political instability",
        )
        self.morale_threshold = morale_threshold
        self.stability_impact = stability_impact

    def validate(self, state: GlobalState, prev_state: GlobalState | None = None) -> list[InvariantViolation]:
        violations = []

        if prev_state is None:
            return violations

        # Check for sustained low morale
        avg_morale = state.get_average_morale()

        if avg_morale >= self.morale_threshold:
            return violations  # Morale is acceptable

        # Calculate average stability
        total_stability = sum(c.government_stability for c in state.countries.values())
        curr_avg_stability = total_stability / len(state.countries) if state.countries else 1.0

        prev_total_stability = sum(c.government_stability for c in prev_state.countries.values())
        prev_avg_stability = prev_total_stability / len(prev_state.countries) if prev_state.countries else 1.0

        stability_decline = prev_avg_stability - curr_avg_stability

        # Violation if stability didn't decline under low morale
        if stability_decline < self.stability_impact * 0.3:  # Allow tolerance
            violations.append(
                InvariantViolation(
                    invariant_name=self.name,
                    description=f"Low morale ({avg_morale:.2f}) without stability decline "
                    f"(expected ≥{self.stability_impact * 0.3:.2f}, got {stability_decline:.2f})",
                    state_snapshot={
                        "avg_morale": avg_morale,
                        "stability_decline": stability_decline,
                        "threshold": self.morale_threshold,
                    },
                    severity="medium",
                )
            )

        return violations


class PoliticalGovernanceInvariant(CompositeInvariant):
    """
    Invariant: Political instability must affect AI governance confidence.

    Validates that government instability impacts AI alignment and operational trust.
    """

    def __init__(self, stability_threshold: float = 0.4, alignment_sensitivity: float = 0.1):
        """
        Initialize political-governance invariant.

        Args:
            stability_threshold: Stability level that affects AI
            alignment_sensitivity: AI alignment decline per tick at low stability
        """
        super().__init__(
            "political_governance_coherence",
            "Political instability must affect AI governance confidence",
        )
        self.stability_threshold = stability_threshold
        self.alignment_sensitivity = alignment_sensitivity

    def validate(self, state: GlobalState, prev_state: GlobalState | None = None) -> list[InvariantViolation]:
        violations = []

        if prev_state is None or not state.ai_systems_operational:
            return violations

        # Check average stability
        total_stability = sum(c.government_stability for c in state.countries.values())
        avg_stability = total_stability / len(state.countries) if state.countries else 1.0

        if avg_stability >= self.stability_threshold:
            return violations  # Stability is acceptable

        # Check AI alignment change
        alignment_decline = prev_state.ai_alignment_score - state.ai_alignment_score

        # Violation if AI alignment didn't decline under instability
        if alignment_decline < self.alignment_sensitivity * 0.2:
            violations.append(
                InvariantViolation(
                    invariant_name=self.name,
                    description=f"Political instability ({avg_stability:.2f}) without AI alignment impact "
                    f"(expected ≥{self.alignment_sensitivity * 0.2:.3f}, got {alignment_decline:.3f})",
                    state_snapshot={
                        "avg_stability": avg_stability,
                        "alignment_decline": alignment_decline,
                        "threshold": self.stability_threshold,
                    },
                    severity="medium",
                )
            )

        return violations


class CompositeInvariantValidator:
    """
    Validates all composite invariants to ensure cross-domain coherence.
    """

    def __init__(self):
        """Initialize validator with default invariants."""
        self.invariants: list[CompositeInvariant] = [
            ResourceEconomicInvariant(),
            EconomicSocietalInvariant(),
            SocietalPoliticalInvariant(),
            PoliticalGovernanceInvariant(),
        ]

    def add_invariant(self, invariant: CompositeInvariant):
        """Add a custom invariant to the validator."""
        self.invariants.append(invariant)

    def validate_all(
        self,
        state: GlobalState,
        prev_state: GlobalState | None = None,
        enforce: bool = True,
    ) -> tuple[bool, list[InvariantViolation]]:
        """
        Validate all composite invariants.

        Args:
            state: Current state
            prev_state: Previous state for delta calculations
            enforce: If True, treat violations as fatal

        Returns:
            Tuple of (is_valid, violations_list)
        """
        all_violations = []

        for invariant in self.invariants:
            try:
                violations = invariant.validate(state, prev_state)
                all_violations.extend(violations)

                if violations:
                    for violation in violations:
                        logger.warning(
                            "Composite invariant violation [%s]: %s",
                            violation.invariant_name,
                            violation.description,
                        )
            except Exception as e:
                logger.error(
                    "Error validating invariant %s: %s",
                    invariant.name,
                    e,
                    exc_info=True,
                )

        is_valid = len(all_violations) == 0 or not enforce

        if not is_valid:
            logger.error(
                "Composite invariant validation failed with %d violations",
                len(all_violations),
            )

        return is_valid, all_violations
