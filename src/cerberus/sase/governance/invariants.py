"""
SASE Invariant Checks

Hard invariants to prevent feedback loops and ensure mathematical correctness.

CRITICAL INVARIANTS:
1. Bayesian posterior must be immutable after L6
2. L15 classification CANNOT modify confidence
3. Actor class influences response type, NOT severity
4. No recursive feedback into prior distribution
"""

import hashlib
import json
import logging
from typing import Any, Dict

logger = logging.getLogger("SASE.Invariants")


class InvariantViolation(Exception):
    """Raised when SASE invariant is violated"""

    pass


class PosteriorImmutabilityGuard:
    """
    Ensures Bayesian posterior cannot be mutated after L6

    CRITICAL: Prevents feedback loop where L15 classification
    influences confidence scores, creating double-weighting bias.
    """

    def __init__(self):
        self.posterior_hashes: Dict[str, str] = {}

    def lock_posterior(self, event_id: str, confidence_assessment: Dict[str, Any]) -> str:
        """
        Lock posterior confidence for event

        Returns hash of locked posterior
        """
        # Create deterministic hash of confidence assessment
        confidence_str = json.dumps(
            {
                "confidence_score": confidence_assessment["confidence_score"],
                "confidence_percentage": confidence_assessment["confidence_percentage"],
                "prior": confidence_assessment.get("prior", 0.01),
                "likelihood_malicious": confidence_assessment.get("likelihood_malicious", 0),
                "likelihood_benign": confidence_assessment.get("likelihood_benign", 0),
            },
            sort_keys=True,
        )

        posterior_hash = hashlib.sha256(confidence_str.encode()).hexdigest()

        self.posterior_hashes[event_id] = posterior_hash

        logger.debug(f"Locked posterior for {event_id}: hash={posterior_hash[:8]}")

        return posterior_hash

    def verify_immutability(self, event_id: str, current_confidence: Dict[str, Any]):
        """
        Verify posterior has not been mutated

        Raises InvariantViolation if mutation detected
        """
        if event_id not in self.posterior_hashes:
            raise InvariantViolation(f"No locked posterior for event {event_id}")

        # Recompute hash
        confidence_str = json.dumps(
            {
                "confidence_score": current_confidence["confidence_score"],
                "confidence_percentage": current_confidence["confidence_percentage"],
                "prior": current_confidence.get("prior", 0.01),
                "likelihood_malicious": current_confidence.get("likelihood_malicious", 0),
                "likelihood_benign": current_confidence.get("likelihood_benign", 0),
            },
            sort_keys=True,
        )

        current_hash = hashlib.sha256(confidence_str.encode()).hexdigest()

        if current_hash != self.posterior_hashes[event_id]:
            logger.critical(f"INVARIANT VIOLATION: Posterior mutated for {event_id}")
            logger.critical(f"Expected hash: {self.posterior_hashes[event_id][:16]}")
            logger.critical(f"Current hash:  {current_hash[:16]}")
            raise InvariantViolation(
                f"Posterior mutation detected for event {event_id}. "
                "L15 or downstream layer illegally modified confidence score."
            )

        logger.debug(f"Posterior immutability verified for {event_id}")


class ClassificationDecouplingGuard:
    """
    Ensures L15 classification does NOT influence L6 posterior

    Actor class should only determine response strategy,
    not modify threat probability.
    """

    @staticmethod
    def validate_classification_output(threat_class: Dict[str, Any]):
        """
        Validate L15 output does not contain posterior mutations

        Raises InvariantViolation if illegal fields present
        """
        illegal_fields = [
            "confidence_override",
            "adjusted_confidence",
            "confidence_multiplier",
            "risk_boost",
            "prior_adjustment",
        ]

        for field in illegal_fields:
            if field in threat_class:
                raise InvariantViolation(
                    f"L15 classification contains illegal field '{field}'. "
                    "Classification must NOT modify confidence scores."
                )

        logger.debug("L15 classification output validated - no illegal mutations")


class FeatureDoubleWeightingDetector:
    """
    Detects feature double-weighting where same signal influences
    posterior multiple times

    Example violation:
    - L4 extracts Tor flag → feeds into L6
    - L15 classifies as "Tor Relay" → feeds back into prior
    = Tor signal used twice  = structural bias
    """

    @staticmethod
    def check_for_double_weighting(
        feature_vector: Any,
        confidence_assessment: Dict[str, Any],
        threat_class: Dict[str, Any],
    ):
        """
        Check if actor class risk score is derived from same
        features already encoded in posterior

        This is a heuristic check - full validation requires
        mathematical audit of probability flows
        """
        # Extract feature flags
        from ..intelligence.attribution import FeatureVector

        if not isinstance(feature_vector, FeatureVector):
            return  # Cannot validate

        features = feature_vector.to_dict()

        # Check if Tor flag is being double-weighted
        if features.get("tor_flag") and threat_class.get("actor_class") == "tor_relay":
            logger.warning(
                "Potential double-weighting: Tor flag in features AND "
                "Tor Relay classification. Ensure prior is not being adjusted."
            )

        # Check if VPS flag is being double-weighted
        if features.get("vps_flag") and threat_class.get("actor_class") == "cloud_vps_actor":
            logger.warning(
                "Potential double-weighting: VPS flag in features AND "
                "Cloud VPS classification. Ensure prior is not being adjusted."
            )


__all__ = [
    "InvariantViolation",
    "PosteriorImmutabilityGuard",
    "ClassificationDecouplingGuard",
    "FeatureDoubleWeightingDetector",
]
