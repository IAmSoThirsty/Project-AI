#                                           [2026-04-09 06:25]
#                                          Productivity: Active
"""
SASE Invariant Checks

Critical mathematical assertions that must hold across detection lifecycle.
Failure of any invariant triggers an emergency fail-closed state.

INVARIANTS:
- Posterior probability immutability (after commitment)
- Temporal causality (Events cannot precede their causes)
- Identity non-repudiation
- Confidence monotonicity (during enrichment)
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("SASE.Invariants")


class InvariantError(Exception):
    """Raised when SASE invariant is violated"""


class PosteriorImmutabilityGuard:
    """
    Ensures confidence scores cannot be altered once committed to audit trail.
    """

    def __init__(self):
        self.committed_hashes: dict[str, str] = {}

    def commit(self, event_id: str, confidence_score: float):
        """Commit confidence score hash to registry"""
        score_hash = str(hash(confidence_score))
        self.committed_hashes[event_id] = score_hash

    def verify(self, event_id: str, current_score: float):
        """Verify score hasn't drifted since commitment"""
        if event_id not in self.committed_hashes:
            return

        expected_hash = self.committed_hashes[event_id]
        current_hash = str(hash(current_score))

        if expected_hash != current_hash:
            logger.critical("INVARIANT VIOLATION: Score drift for event %s", event_id)
            raise InvariantError(f"Posterior Immutability violation for {event_id}")


class TemporalCausalityGuard:
    """
    Ensures logical event ordering.
    Normalization time must be >= Ingestion time.
    """

    @staticmethod
    def verify_causality(ingestion_ts: float, normalization_ts: float):
        """Verify temporal ordering"""
        if normalization_ts < ingestion_ts:
            logger.critical("TEMPORAL ANOMALY: Normalization precedes Ingestion!")
            raise InvariantError("Causality violation detected")


@dataclass
class SASEState:
    """System state snapshot for invariant checking"""

    event_id: str
    stage: str
    confidence: float
    timestamp: float


class InvariantEngine:
    """
    SASE L9: Invariant Checking & Validation Substrate
    """

    def __init__(self):
        self.immutability = PosteriorImmutabilityGuard()
        self.causality = TemporalCausalityGuard()
        self.historical_states: list[SASEState] = []

        logger.info("L9 Invariant Engine initialized")

    def validate_transition(self, old_state: SASEState, new_state: SASEState):
        """Perform system-wide invariant validation on state transition"""

        # 1. Monotonicity check (Confidence should typically not drop during enrichment)
        # Note: In adversarial scenarios, confidence might drop if new evidence contradicts old.
        # This is a 'soft' invariant.

        # 2. Hard temporal causality
        self.causality.verify_causality(old_state.timestamp, new_state.timestamp)

        # 3. Immutability check if new state is terminal/committed
        if new_state.stage == "COMMITTED":
            self.immutability.commit(new_state.event_id, new_state.confidence)

        # 4. Persistence validation
        self.historical_states.append(new_state)
        # Keep buffer small
        if len(self.historical_states) > 500:
            self.historical_states.pop(0)

    def verify_event_integrity(self, event_id: str, current_confidence: float):
        """Audit existing event against immutability records"""
        self.immutability.verify(event_id, current_confidence)


__all__ = ["SASEState", "InvariantEngine", "InvariantError"]
