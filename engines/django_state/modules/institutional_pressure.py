"""Institutional pressure module.

Models bureaucratic inertia, legitimacy erosion, and institutional dynamics.
"""

import logging
import random
from typing import Any

from ..kernel.irreversibility_laws import IrreversibilityLaws
from ..schemas.event_schema import InstitutionalFailureEvent
from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class InstitutionalPressureModule:
    """Models institutional dynamics and governance capacity.

    Tracks bureaucratic inertia, legitimacy erosion, broken promises,
    and institutional failure cascades.
    """

    def __init__(self, laws: IrreversibilityLaws):
        """Initialize institutional pressure module.

        Args:
            laws: Irreversibility laws instance
        """
        self.laws = laws

        # Institutional capacity tracking
        self.base_capacity = 1.0
        self.current_capacity = 1.0
        self.capacity_history: list[float] = []

        # Promise tracking
        self.promises_made = 0
        self.promises_kept = 0
        self.promises_broken = 0

        # Failure tracking
        self.failure_history: list[dict[str, Any]] = []
        self.cascading_failures = 0

        # Bureaucratic parameters
        self.inertia_factor = 0.2  # Resistance to change
        self.efficiency = 0.75  # How well institutions function

        logger.info("Institutional pressure module initialized")

    def calculate_governance_capacity(self, state: StateVector) -> float:
        """Calculate current governance capacity from state.

        Args:
            state: Current state vector

        Returns:
            Governance capacity (0.0 to 1.0)
        """
        # Base capacity affected by legitimacy and epistemic confidence
        capacity = state.legitimacy.value * 0.6 + state.epistemic_confidence.value * 0.4

        # Reduce by bureaucratic inertia
        capacity *= 1.0 - self.inertia_factor

        # Adjust by efficiency
        capacity *= self.efficiency

        # Recent failures reduce capacity
        recent_failures = len(
            [f for f in self.failure_history[-10:] if f.get("severity", 0) > 0.5]
        )
        failure_penalty = min(recent_failures * 0.05, 0.3)
        capacity -= failure_penalty

        self.current_capacity = max(0.0, min(1.0, capacity))
        self.capacity_history.append(self.current_capacity)

        logger.debug("Governance capacity: %s", self.current_capacity)

        return self.current_capacity

    def make_promise(self, difficulty: float = 0.5) -> str:
        """Institutional promise made.

        Args:
            difficulty: How difficult to keep (0.0 to 1.0)

        Returns:
            Promise ID
        """
        self.promises_made += 1
        promise_id = f"promise_{self.promises_made}"

        logger.debug("Promise made: %s, difficulty=%s", promise_id, difficulty)

        return promise_id

    def evaluate_promise_keeping(
        self, state: StateVector, promise_difficulty: float = 0.5
    ) -> bool:
        """Evaluate whether a promise can be kept.

        Args:
            state: Current state vector
            promise_difficulty: Difficulty of keeping promise (0.0 to 1.0)

        Returns:
            True if promise kept, False if broken
        """
        # Capacity to keep promise
        keep_probability = self.current_capacity * (1.0 - promise_difficulty)

        # Trust affects follow-through
        keep_probability += state.trust.value * 0.2

        # Moral injury makes promise-keeping harder
        keep_probability -= state.moral_injury.value * 0.3

        kept = random.random() < keep_probability

        if kept:
            self.promises_kept += 1
            logger.debug("Promise kept (prob=%s)", keep_probability)
        else:
            self.promises_broken += 1
            logger.info("Promise broken (prob=%s)", keep_probability)

        return kept

    def generate_failure_event(
        self,
        state: StateVector,
        failure_type: str = "system_failure",
        impact_scope: str = "local",
        severity: float = 0.5,
    ) -> InstitutionalFailureEvent:
        """Generate institutional failure event.

        Args:
            state: Current state vector
            failure_type: Type of failure
            impact_scope: Scope of impact
            severity: Failure severity

        Returns:
            InstitutionalFailureEvent instance
        """
        from ..schemas.event_schema import EventType

        event = InstitutionalFailureEvent(
            event_type=EventType.INSTITUTIONAL_FAILURE,
            timestamp=state.timestamp,
            source="institutional_pressure",
            description=f"Institutional failure: {failure_type}, scope={impact_scope}",
            failure_type=failure_type,
            impact_scope=impact_scope,
            severity=severity,
        )

        # Record in history
        self.failure_history.append(
            {
                "timestamp": state.timestamp,
                "failure_type": failure_type,
                "impact_scope": impact_scope,
                "severity": severity,
                "event_id": event.event_id,
            }
        )

        logger.info(
            "Generated failure event: %s, scope=%s, severity=%s",
            failure_type,
            impact_scope,
            severity,
        )

        return event

    def check_cascading_failure(self, state: StateVector) -> bool:
        """Check if conditions exist for cascading failure.

        Cascading failures occur when legitimacy is very low and capacity is impaired.

        Args:
            state: Current state vector

        Returns:
            True if cascading failure should occur
        """
        # High risk if legitimacy very low
        if state.legitimacy.value < 0.25:
            cascade_prob = 0.3 * (1.0 - state.legitimacy.value / 0.25)

            # Recent failures increase cascade probability
            recent_failures = len(list(self.failure_history[-5:]))
            cascade_prob += recent_failures * 0.1

            if random.random() < cascade_prob:
                self.cascading_failures += 1
                logger.warning(
                    "CASCADING FAILURE DETECTED (total: %s)", self.cascading_failures
                )
                return True

        return False

    def apply_institutional_dynamics(self, state: StateVector) -> dict[str, Any]:
        """Apply institutional dynamics for this tick.

        Args:
            state: Current state vector

        Returns:
            Dictionary with dynamics results
        """
        # Calculate current capacity
        capacity = self.calculate_governance_capacity(state)

        # Simulate promise-keeping
        promises_this_tick = 0
        broken_this_tick = 0

        if random.random() < 0.3:  # 30% chance of promise each tick
            promise_difficulty = random.uniform(0.3, 0.8)
            self.make_promise(promise_difficulty)
            promises_this_tick += 1

            if not self.evaluate_promise_keeping(state, promise_difficulty):
                broken_this_tick += 1
                # Apply legitimacy erosion
                self.laws.apply_legitimacy_erosion(
                    state,
                    broken_promises=1,
                    failures=0,
                    visibility=random.uniform(0.4, 0.9),
                )

        # Check for institutional failures
        failure_occurred = False
        failure_event = None

        # Failure more likely with low capacity
        failure_prob = 0.05 * (1.0 - capacity)

        # Increased by low legitimacy
        if state.legitimacy.value < 0.4:
            failure_prob += (0.4 - state.legitimacy.value) * 0.2

        if random.random() < failure_prob:
            failure_occurred = True
            failure_type = random.choice(
                ["system_failure", "corruption", "promise_broken"]
            )
            impact_scope = random.choice(["local", "regional", "national"])
            severity = random.uniform(0.4, 0.8)

            failure_event = self.generate_failure_event(
                state, failure_type, impact_scope, severity
            )

            # Apply legitimacy erosion
            self.laws.apply_legitimacy_erosion(
                state,
                broken_promises=0,
                failures=1,
                visibility=random.uniform(0.5, 1.0),
            )

        # Check for cascading failures
        cascading = self.check_cascading_failure(state)

        if cascading:
            # Generate multiple failures
            for _ in range(random.randint(2, 4)):
                self.generate_failure_event(
                    state,
                    failure_type="cascading_failure",
                    impact_scope=random.choice(["regional", "national", "global"]),
                    severity=random.uniform(0.6, 1.0),
                )
                self.laws.apply_legitimacy_erosion(
                    state,
                    broken_promises=0,
                    failures=1,
                    visibility=1.0,
                )

        # Bureaucratic inertia increases over time
        if state.tick_count % 100 == 0:
            self.inertia_factor = min(0.5, self.inertia_factor * 1.05)
            logger.debug("Bureaucratic inertia increased to %s", self.inertia_factor)

        return {
            "governance_capacity": capacity,
            "promises_this_tick": promises_this_tick,
            "promises_broken_this_tick": broken_this_tick,
            "failure_occurred": failure_occurred,
            "failure_event": failure_event,
            "cascading_failure": cascading,
            "inertia_factor": self.inertia_factor,
        }

    def get_promise_keeping_rate(self) -> float:
        """Calculate promise-keeping rate.

        Returns:
            Rate of promises kept (0.0 to 1.0)
        """
        if self.promises_made == 0:
            return 1.0
        return self.promises_kept / self.promises_made

    def get_capacity_trend(self, window: int = 10) -> str:
        """Get capacity trend over recent history.

        Args:
            window: Number of recent ticks to analyze

        Returns:
            Trend description
        """
        if len(self.capacity_history) < window:
            return "insufficient_data"

        recent = self.capacity_history[-window:]
        first_half = sum(recent[: window // 2]) / (window // 2)
        second_half = sum(recent[window // 2 :]) / (window - window // 2)

        diff = second_half - first_half

        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "degrading"
        else:
            return "stable"

    def get_summary(self) -> dict[str, Any]:
        """Get module summary.

        Returns:
            Dictionary with module state
        """
        return {
            "current_capacity": self.current_capacity,
            "promises_made": self.promises_made,
            "promises_kept": self.promises_kept,
            "promises_broken": self.promises_broken,
            "promise_keeping_rate": self.get_promise_keeping_rate(),
            "total_failures": len(self.failure_history),
            "cascading_failures": self.cascading_failures,
            "inertia_factor": self.inertia_factor,
            "efficiency": self.efficiency,
            "capacity_trend": self.get_capacity_trend(),
        }

    def reset(self) -> None:
        """Reset module to initial state."""
        self.__init__(self.laws)
        logger.info("Institutional pressure module reset")
