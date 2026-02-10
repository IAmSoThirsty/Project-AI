"""Irreversibility laws for state evolution.

Implements all physics laws governing state transitions including trust decay,
kindness singularity, betrayal probability, moral injury accumulation, and
legitimacy erosion.
"""

import logging
from typing import Any

from ..schemas.config_schema import IrreversibilityConfig
from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class IrreversibilityLaws:
    """Physics engine for irreversible state evolution.

    Implements all laws of state transitions with one-way constraints.
    """

    def __init__(self, config: IrreversibilityConfig):
        """Initialize irreversibility laws.

        Args:
            config: Configuration for law parameters
        """
        self.config = config
        logger.info("Irreversibility laws initialized")

    def apply_trust_decay_law(self, state: StateVector) -> float:
        """Apply trust decay law: trust(t+1) = trust(t) * (1 - decay_rate).

        Trust decays exponentially over time. Betrayals cause permanent ceiling reduction.

        Args:
            state: Current state vector

        Returns:
            Trust change applied
        """
        if state.trust.value <= 0:
            return 0.0

        # Exponential decay
        decay = -state.trust.value * self.config.trust_decay_rate

        # Apply ceiling constraint (irreversibility from past betrayals)
        actual_change = state.trust.update(
            delta=decay,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        logger.debug(
            "Trust decay: %s, actual: %s, value: %s",
            decay,
            actual_change,
            state.trust.value,
        )
        return actual_change

    def apply_betrayal_impact(
        self, state: StateVector, severity: float = 0.5
    ) -> dict[str, float]:
        """Apply betrayal impact to trust and impose permanent ceiling.

        Betrayals cause immediate trust loss and permanent recovery ceiling reduction.

        Args:
            state: Current state vector
            severity: Betrayal severity (0.0 to 1.0)

        Returns:
            Dictionary of changes applied
        """
        # Immediate trust loss
        trust_loss = -self.config.betrayal_trust_impact * (0.5 + severity)
        trust_change = state.trust.update(
            delta=trust_loss,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        # Permanent ceiling reduction (irreversibility)
        ceiling_reduction = self.config.betrayal_ceiling_reduction * severity
        new_ceiling = state.trust.value * (1.0 - ceiling_reduction)
        new_ceiling = max(new_ceiling, 0.1)  # Minimum ceiling
        state.trust.impose_ceiling(new_ceiling)

        # Update betrayal counter
        state.betrayal_count += 1

        logger.info(
            "Betrayal impact: trust loss %s, new ceiling %s", trust_change, new_ceiling
        )

        return {
            "trust_change": trust_change,
            "new_ceiling": new_ceiling,
            "betrayal_count": state.betrayal_count,
        }

    def check_kindness_singularity(self, state: StateVector) -> tuple[bool, str]:
        """Check if kindness has crossed singularity threshold.

        Below threshold, cooperation becomes impossible and system enters collapse.

        Args:
            state: Current state vector

        Returns:
            Tuple of (crossed_threshold, reason)
        """
        threshold = self.config.kindness_singularity_threshold

        if state.kindness.value < threshold:
            if not state.in_collapse:
                logger.critical(
                    "KINDNESS SINGULARITY: value %s < threshold %s",
                    state.kindness.value,
                    threshold,
                )
                return True, "kindness_singularity"

        return False, ""

    def apply_kindness_decay(self, state: StateVector) -> float:
        """Apply kindness decay law.

        Kindness decays slowly over time without cooperation events.

        Args:
            state: Current state vector

        Returns:
            Kindness change applied
        """
        if state.kindness.value <= 0:
            return 0.0

        # Base decay
        decay = -state.kindness.value * self.config.kindness_decay_rate

        # Accelerate decay if near singularity
        if state.kindness.value < (self.config.kindness_singularity_threshold * 1.5):
            acceleration_factor = 1.0 / (state.kindness.value + 0.1)
            decay *= acceleration_factor

        actual_change = state.kindness.update(
            delta=decay,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        logger.debug(
            "Kindness decay: %s, actual: %s, value: %s",
            decay,
            actual_change,
            state.kindness.value,
        )
        return actual_change

    def apply_cooperation_boost(
        self, state: StateVector, magnitude: float = 0.5
    ) -> float:
        """Apply cooperation event boost to kindness.

        Cooperation events temporarily boost kindness, but ceiling constraints apply.

        Args:
            state: Current state vector
            magnitude: Cooperation magnitude (0.0 to 1.0)

        Returns:
            Kindness change applied
        """
        boost = self.config.kindness_cooperation_boost * magnitude

        # Diminishing returns at high kindness
        diminishing_factor = 1.0 - (state.kindness.value * 0.5)
        boost *= diminishing_factor

        actual_change = state.kindness.update(
            delta=boost,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        state.cooperation_count += 1

        logger.debug("Cooperation boost: %s, actual: %s", boost, actual_change)
        return actual_change

    def apply_legitimacy_erosion(
        self,
        state: StateVector,
        broken_promises: int = 0,
        failures: int = 0,
        visibility: float = 0.5,
    ) -> dict[str, float]:
        """Apply legitimacy erosion law.

        legitimacy(t+1) = legitimacy(t) - (broken_promises + failures) * visibility
        Legitimacy can never fully recover after damage (governance ceiling).

        Args:
            state: Current state vector
            broken_promises: Number of broken promises
            failures: Number of institutional failures
            visibility: How widely known (0.0 to 1.0)

        Returns:
            Dictionary of changes applied
        """
        # Base decay
        decay = -state.legitimacy.value * self.config.legitimacy_decay_rate

        # Impact from broken promises
        if broken_promises > 0:
            promise_impact = (
                -self.config.broken_promise_impact * broken_promises * visibility
            )
            decay += promise_impact
            state.broken_promises += broken_promises

        # Impact from institutional failures
        if failures > 0:
            failure_impact = (
                -self.config.institutional_failure_impact * failures * visibility
            )
            decay += failure_impact
            state.institutional_failures += failures

        actual_change = state.legitimacy.update(
            delta=decay,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        # Impose new ceiling if significant erosion occurred
        if actual_change < -0.05:
            new_ceiling = state.legitimacy.value * 0.95
            new_ceiling = max(new_ceiling, self.config.legitimacy_recovery_limit)
            state.legitimacy.impose_ceiling(new_ceiling)
            logger.info("Legitimacy ceiling imposed: %s", new_ceiling)

        logger.debug("Legitimacy erosion: %s, actual: %s", decay, actual_change)

        return {
            "legitimacy_change": actual_change,
            "broken_promises": state.broken_promises,
            "institutional_failures": state.institutional_failures,
        }

    def accumulate_moral_injury(
        self, state: StateVector, violation_severity: float = 0.5
    ) -> dict[str, float]:
        """Apply moral injury accumulation law.

        moral_injury(t+1) = moral_injury(t) + violation_severity
        Moral injury is largely irreversible - accumulates from ethical violations.

        Args:
            state: Current state vector
            violation_severity: Severity of violation (0.0 to 1.0)

        Returns:
            Dictionary of changes applied
        """
        # Calculate injury accumulation
        injury_delta = self.config.violation_severity_base * (0.5 + violation_severity)

        # Moral injury has a floor (can't easily heal)
        old_floor = state.moral_injury.floor or 0.0
        new_floor = state.moral_injury.value + injury_delta

        actual_change = state.moral_injury.update(
            delta=injury_delta,
            timestamp=state.timestamp,
            enforce_ceiling=False,
        )

        # Impose new floor (irreversibility)
        if new_floor > old_floor:
            state.moral_injury.impose_floor(new_floor)

        # Check if critical threshold crossed
        critical = state.moral_injury.value > self.config.moral_injury_threshold

        logger.info(
            "Moral injury accumulated: %s, total: %s, critical: %s",
            actual_change,
            state.moral_injury.value,
            critical,
        )

        return {
            "moral_injury_change": actual_change,
            "moral_injury_value": state.moral_injury.value,
            "critical_threshold_crossed": critical,
            "new_floor": new_floor,
        }

    def apply_moral_injury_healing(self, state: StateVector) -> float:
        """Apply very slow moral injury healing over time.

        Moral injury heals extremely slowly and can never return to zero.

        Args:
            state: Current state vector

        Returns:
            Healing applied (negative change)
        """
        if state.moral_injury.value <= 0:
            return 0.0

        # Very slow healing
        healing = -state.moral_injury.value * self.config.moral_injury_decay_rate

        # Floor prevents dropping below minimum
        actual_change = state.moral_injury.update(
            delta=healing,
            timestamp=state.timestamp,
            enforce_ceiling=False,
        )

        logger.debug("Moral injury healing: %s, actual: %s", healing, actual_change)
        return actual_change

    def calculate_betrayal_probability(self, state: StateVector) -> float:
        """Calculate betrayal probability based on current state.

        P(betrayal) = f(trust, legitimacy, moral_injury, pressure)
        Probability increases as trust/legitimacy decrease and moral injury increases.

        Args:
            state: Current state vector

        Returns:
            Probability of betrayal (0.0 to 1.0)
        """
        base_prob = self.config.betrayal_prob_base

        # Trust contribution (inverse)
        trust_factor = self.config.betrayal_prob_trust_factor * (
            1.0 - state.trust.value
        )

        # Legitimacy contribution (inverse)
        legitimacy_factor = self.config.betrayal_prob_legitimacy_factor * (
            1.0 - state.legitimacy.value
        )

        # Moral injury contribution (direct)
        moral_factor = self.config.betrayal_prob_moral_factor * state.moral_injury.value

        # Combined probability
        probability = base_prob + trust_factor + legitimacy_factor + moral_factor

        # Cap at 1.0
        probability = min(probability, 1.0)

        logger.debug(
            "Betrayal probability: %s (trust: %s, legitimacy: %s, moral: %s)",
            probability,
            trust_factor,
            legitimacy_factor,
            moral_factor,
        )

        return probability

    def apply_epistemic_decay(self, state: StateVector) -> float:
        """Apply epistemic confidence decay.

        Epistemic confidence decays as misinformation accumulates.

        Args:
            state: Current state vector

        Returns:
            Epistemic confidence change
        """
        if state.epistemic_confidence.value <= 0:
            return 0.0

        # Base decay
        decay = -state.epistemic_confidence.value * self.config.epistemic_decay_rate

        # Accelerate if many manipulation events occurred
        if state.manipulation_events > 10:
            acceleration = 1.0 + (state.manipulation_events / 20.0)
            decay *= acceleration

        actual_change = state.epistemic_confidence.update(
            delta=decay,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        logger.debug("Epistemic decay: %s, actual: %s", decay, actual_change)
        return actual_change

    def apply_manipulation_impact(
        self, state: StateVector, reach: float = 0.5, sophistication: float = 0.5
    ) -> dict[str, float]:
        """Apply information manipulation impact to epistemic confidence.

        Manipulation reduces ability to perceive truth, creating divergent realities.

        Args:
            state: Current state vector
            reach: Fraction of population affected (0.0 to 1.0)
            sophistication: Difficulty of detection (0.0 to 1.0)

        Returns:
            Dictionary of changes applied
        """
        # Calculate damage
        base_damage = -self.config.manipulation_impact
        reach_multiplier = 1.0 + reach
        sophistication_multiplier = 1.0 + sophistication

        total_damage = base_damage * reach_multiplier * sophistication_multiplier

        actual_change = state.epistemic_confidence.update(
            delta=total_damage,
            timestamp=state.timestamp,
            enforce_ceiling=True,
        )

        # Impose ceiling after significant manipulation
        if actual_change < -0.05:
            new_ceiling = state.epistemic_confidence.value * 0.92
            state.epistemic_confidence.impose_ceiling(new_ceiling)
            logger.info("Epistemic confidence ceiling imposed: %s", new_ceiling)

        state.manipulation_events += 1

        logger.info("Manipulation impact: %s, actual: %s", total_damage, actual_change)

        return {
            "epistemic_change": actual_change,
            "manipulation_events": state.manipulation_events,
        }

    def apply_collapse_acceleration(
        self, state: StateVector, acceleration_factor: float = 2.0
    ) -> None:
        """Apply collapse acceleration once system enters collapse state.

        After crossing critical thresholds, decay rates accelerate.

        Args:
            state: Current state vector
            acceleration_factor: How much to accelerate decay
        """
        if not state.in_collapse:
            return

        logger.warning(
            "Applying collapse acceleration (factor: %s)", acceleration_factor
        )

        # Accelerate all decay rates temporarily
        original_config = IrreversibilityConfig(
            trust_decay_rate=self.config.trust_decay_rate,
            kindness_decay_rate=self.config.kindness_decay_rate,
            legitimacy_decay_rate=self.config.legitimacy_decay_rate,
            epistemic_decay_rate=self.config.epistemic_decay_rate,
        )

        self.config.trust_decay_rate *= acceleration_factor
        self.config.kindness_decay_rate *= acceleration_factor
        self.config.legitimacy_decay_rate *= acceleration_factor
        self.config.epistemic_decay_rate *= acceleration_factor

        # Apply accelerated decay
        self.apply_trust_decay_law(state)
        self.apply_kindness_decay(state)
        self.apply_legitimacy_erosion(
            state, broken_promises=0, failures=0, visibility=0
        )
        self.apply_epistemic_decay(state)

        # Restore original rates
        self.config.trust_decay_rate = original_config.trust_decay_rate
        self.config.kindness_decay_rate = original_config.kindness_decay_rate
        self.config.legitimacy_decay_rate = original_config.legitimacy_decay_rate
        self.config.epistemic_decay_rate = original_config.epistemic_decay_rate

    def tick_all_laws(self, state: StateVector) -> dict[str, Any]:
        """Apply all natural decay laws for one time step.

        Args:
            state: Current state vector

        Returns:
            Dictionary of all changes applied
        """
        changes = {}

        # Apply natural decay
        changes["trust_decay"] = self.apply_trust_decay_law(state)
        changes["kindness_decay"] = self.apply_kindness_decay(state)
        changes["legitimacy_decay"] = self.apply_legitimacy_erosion(
            state, broken_promises=0, failures=0, visibility=0
        )
        changes["moral_injury_healing"] = self.apply_moral_injury_healing(state)
        changes["epistemic_decay"] = self.apply_epistemic_decay(state)

        # Calculate derived metrics
        changes["betrayal_probability"] = self.calculate_betrayal_probability(state)

        # Check collapse condition
        crossed, reason = self.check_kindness_singularity(state)
        changes["kindness_singularity"] = crossed
        changes["collapse_reason"] = reason

        return changes
