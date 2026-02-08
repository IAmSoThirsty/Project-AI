"""Validators for state consistency, irreversibility, and path-dependence.

Production-grade validation for engine correctness.
"""

import logging

from ..kernel.irreversibility_laws import IrreversibilityLaws
from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class StateValidator:
    """Validates state vector consistency and constraints."""

    @staticmethod
    def validate_state(state: StateVector) -> tuple[bool, list[str]]:
        """Validate state vector for consistency.

        Args:
            state: State to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check dimension bounds
        if not (0.0 <= state.trust.value <= 1.0):
            errors.append(f"Trust out of bounds: {state.trust.value}")

        if not (0.0 <= state.legitimacy.value <= 1.0):
            errors.append(f"Legitimacy out of bounds: {state.legitimacy.value}")

        if not (0.0 <= state.kindness.value <= 1.0):
            errors.append(f"Kindness out of bounds: {state.kindness.value}")

        if not (0.0 <= state.moral_injury.value <= 1.0):
            errors.append(f"Moral injury out of bounds: {state.moral_injury.value}")

        if not (0.0 <= state.epistemic_confidence.value <= 1.0):
            errors.append(
                f"Epistemic confidence out of bounds: {state.epistemic_confidence.value}"
            )

        # Check derived metrics
        if not (0.0 <= state.social_cohesion <= 1.0):
            errors.append(f"Social cohesion out of bounds: {state.social_cohesion}")

        if not (0.0 <= state.governance_capacity <= 1.0):
            errors.append(
                f"Governance capacity out of bounds: {state.governance_capacity}"
            )

        if not (0.0 <= state.reality_consensus <= 1.0):
            errors.append(f"Reality consensus out of bounds: {state.reality_consensus}")

        # Check ceiling constraints
        if state.trust.ceiling is not None and state.trust.value > state.trust.ceiling:
            errors.append(
                f"Trust exceeds ceiling: {state.trust.value} > {state.trust.ceiling}"
            )

        if (
            state.legitimacy.ceiling is not None
            and state.legitimacy.value > state.legitimacy.ceiling
        ):
            errors.append(
                f"Legitimacy exceeds ceiling: {state.legitimacy.value} > {state.legitimacy.ceiling}"
            )

        # Check floor constraints
        if (
            state.moral_injury.floor is not None
            and state.moral_injury.value < state.moral_injury.floor
        ):
            errors.append(
                f"Moral injury below floor: {state.moral_injury.value} < {state.moral_injury.floor}"
            )

        # Check counters are non-negative
        if state.betrayal_count < 0:
            errors.append(f"Negative betrayal count: {state.betrayal_count}")

        if state.cooperation_count < 0:
            errors.append(f"Negative cooperation count: {state.cooperation_count}")

        return len(errors) == 0, errors


class IrreversibilityValidator:
    """Validates irreversibility constraints are enforced."""

    @staticmethod
    def validate_trust_ceiling(
        state_before: StateVector, state_after: StateVector
    ) -> tuple[bool, str]:
        """Validate trust ceiling was not violated.

        Args:
            state_before: State before transition
            state_after: State after transition

        Returns:
            Tuple of (is_valid, error_message)
        """
        # If ceiling was imposed or exists, value should not exceed it
        if state_after.trust.ceiling is not None:
            if state_after.trust.value > state_after.trust.ceiling:
                return (
                    False,
                    f"Trust ceiling violated: {state_after.trust.value} > {state_after.trust.ceiling}",
                )

        # Ceiling should never increase (can only decrease or stay same)
        if (
            state_before.trust.ceiling is not None
            and state_after.trust.ceiling is not None
        ):
            if state_after.trust.ceiling > state_before.trust.ceiling:
                return (
                    False,
                    f"Trust ceiling increased: {state_before.trust.ceiling} -> {state_after.trust.ceiling}",
                )

        return True, ""

    @staticmethod
    def validate_moral_injury_floor(
        state_before: StateVector, state_after: StateVector
    ) -> tuple[bool, str]:
        """Validate moral injury floor was not violated.

        Args:
            state_before: State before transition
            state_after: State after transition

        Returns:
            Tuple of (is_valid, error_message)
        """
        # If floor was imposed or exists, value should not go below it
        if state_after.moral_injury.floor is not None:
            if state_after.moral_injury.value < state_after.moral_injury.floor:
                return (
                    False,
                    f"Moral injury floor violated: {state_after.moral_injury.value} < {state_after.moral_injury.floor}",
                )

        # Floor should never decrease (can only increase or stay same)
        if (
            state_before.moral_injury.floor is not None
            and state_after.moral_injury.floor is not None
        ):
            if state_after.moral_injury.floor < state_before.moral_injury.floor:
                return (
                    False,
                    f"Moral injury floor decreased: {state_before.moral_injury.floor} -> {state_after.moral_injury.floor}",
                )

        return True, ""

    @staticmethod
    def validate_all_irreversibility(
        state_before: StateVector, state_after: StateVector
    ) -> tuple[bool, list[str]]:
        """Validate all irreversibility constraints.

        Args:
            state_before: State before transition
            state_after: State after transition

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Trust ceiling
        valid, error = IrreversibilityValidator.validate_trust_ceiling(
            state_before, state_after
        )
        if not valid:
            errors.append(error)

        # Legitimacy ceiling
        if state_after.legitimacy.ceiling is not None:
            if state_after.legitimacy.value > state_after.legitimacy.ceiling:
                errors.append(
                    f"Legitimacy ceiling violated: {state_after.legitimacy.value} > {state_after.legitimacy.ceiling}"
                )

        # Moral injury floor
        valid, error = IrreversibilityValidator.validate_moral_injury_floor(
            state_before, state_after
        )
        if not valid:
            errors.append(error)

        # Epistemic confidence ceiling
        if state_after.epistemic_confidence.ceiling is not None:
            if (
                state_after.epistemic_confidence.value
                > state_after.epistemic_confidence.ceiling
            ):
                errors.append(
                    f"Epistemic ceiling violated: {state_after.epistemic_confidence.value} > {state_after.epistemic_confidence.ceiling}"
                )

        return len(errors) == 0, errors


class PathDependenceValidator:
    """Validates path-dependent behavior."""

    @staticmethod
    def validate_betrayal_impact_path_dependence(
        state1: StateVector,
        state2: StateVector,
        betrayal_severity: float,
        laws: IrreversibilityLaws,
    ) -> bool:
        """Validate that same betrayal has different impact based on current state.

        Args:
            state1: First state
            state2: Second state (different from state1)
            betrayal_severity: Betrayal severity
            laws: Laws instance

        Returns:
            True if path-dependent behavior observed
        """
        # Apply same betrayal to both states
        state1_copy = state1.copy()
        state2_copy = state2.copy()

        result1 = laws.apply_betrayal_impact(state1_copy, betrayal_severity)
        result2 = laws.apply_betrayal_impact(state2_copy, betrayal_severity)

        # Impact should differ based on starting state
        impact1 = result1.get("trust_change", 0)
        impact2 = result2.get("trust_change", 0)

        # If states were different, impacts should differ
        if state1.trust.value != state2.trust.value:
            return abs(impact1 - impact2) > 0.001

        return True

    @staticmethod
    def validate_cooperation_diminishing_returns(
        high_trust_state: StateVector,
        low_trust_state: StateVector,
        laws: IrreversibilityLaws,
    ) -> bool:
        """Validate that cooperation has diminishing returns at high trust.

        Args:
            high_trust_state: State with high trust
            low_trust_state: State with low trust
            laws: Laws instance

        Returns:
            True if diminishing returns observed
        """
        high_copy = high_trust_state.copy()
        low_copy = low_trust_state.copy()

        boost_high = laws.apply_cooperation_boost(high_copy, magnitude=0.5)
        boost_low = laws.apply_cooperation_boost(low_copy, magnitude=0.5)

        # Boost should be larger for low trust state (diminishing returns at high trust)
        return abs(boost_low) > abs(boost_high)
