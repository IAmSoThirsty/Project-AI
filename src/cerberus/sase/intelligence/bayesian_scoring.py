"""
SASE - Sovereign Adversarial Signal Engine
L6: Bayesian Confidence Aggregation

Probabilistic threat scoring using Bayesian inference.

FORMULA:
P(M|E) = (P(E|M) * P(M)) / 
         [(P(E|M) * P(M)) + (P(E|¬M) * (1 - P(M)))]

Where:
- P(M) = Prior malicious probability
- P(E|M) = Likelihood of event given malicious actor
- P(E|¬M) = Likelihood of event given benign actor
- P(M|E) = Posterior probability (confidence score)

Output: 0-100 confidence score
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("SASE.L6.BayesianScoring")


@dataclass
class PriorDistribution:
    """
    Prior probability distribution

    Base rates for malicious vs benign behavior
    """

    malicious_base_rate: float = 0.01  # 1% of traffic is malicious (adjustable)

    def get_prior(self, feature_vector: Any = None) -> float:
        """
        Get prior probability P(M)

        Can be adjusted based on feature vector context
        """
        from .attribution import FeatureVector

        if feature_vector is None:
            return self.malicious_base_rate

        # Adjust prior based on strong indicators
        adjusted_prior = self.malicious_base_rate

        if isinstance(feature_vector, FeatureVector):
            # Tor usage increases prior
            if feature_vector.Tor_flag:
                adjusted_prior += 0.2

            # High ASN risk increases prior
            if feature_vector.ASN_risk > 0.7:
                adjusted_prior += 0.15

            # High reuse count increases prior
            if feature_vector.Historical_reuse_count > 10:
                adjusted_prior += 0.1

            # Cap at reasonable maximum
            adjusted_prior = min(0.95, adjusted_prior)

        return adjusted_prior


@dataclass
class LikelihoodEstimator:
    """
    Likelihood estimation for observations

    P(E|M) = Likelihood of evidence given malicious
    P(E|¬M) = Likelihood of evidence given benign
    """

    def estimate_malicious_likelihood(
        self, feature_vector: Any, behavior_state: Any = None
    ) -> float:
        """
        Estimate P(E|M) - likelihood given malicious actor

        Higher = more consistent with malicious behavior
        """
        from .attribution import FeatureVector
        from .behavioral_model import BehaviorState

        if not isinstance(feature_vector, FeatureVector):
            return 0.5

        # Start with base likelihood
        likelihood = 0.5

        # Feature-based adjustments

        # ASN risk
        likelihood += feature_vector.ASN_risk * 0.15

        # Geo anomaly
        likelihood += feature_vector.Geo_anomaly_score * 0.1

        # Token sensitivity (high-value targets)
        likelihood += feature_vector.Token_sensitivity * 0.15

        # Time deviation (off-hours access)
        likelihood += feature_vector.Time_of_day_deviation * 0.05

        # Infrastructure entropy
        likelihood += feature_vector.Infrastructure_entropy * 0.1

        # Tor/VPS flags
        if feature_vector.Tor_flag:
            likelihood += 0.2
        if feature_vector.VPS_flag:
            likelihood += 0.1

        # Behavioral state context
        if behavior_state:
            escalation_states = {
                BehaviorState.ESCALATION_ATTEMPT,
                BehaviorState.API_ENUMERATION,
                BehaviorState.CREDENTIAL_USE,
            }

            if behavior_state in escalation_states:
                likelihood += 0.15

        # Cap at maximum
        likelihood = min(0.99, likelihood)

        return likelihood

    def estimate_benign_likelihood(
        self, feature_vector: Any, behavior_state: Any = None
    ) -> float:
        """
        Estimate P(E|¬M) - likelihood given benign actor

        Higher = more consistent with benign behavior
        """
        from .attribution import FeatureVector
        from .behavioral_model import BehaviorState

        if not isinstance(feature_vector, FeatureVector):
            return 0.5

        # Benign likelihood is generally inverse of malicious indicators
        likelihood = 0.5

        # Low ASN risk
        likelihood += (1.0 - feature_vector.ASN_risk) * 0.1

        # Normal geography
        likelihood += (1.0 - feature_vector.Geo_anomaly_score) * 0.05

        # Normal timing
        likelihood += (1.0 - feature_vector.Time_of_day_deviation) * 0.05

        # Low infrastructure entropy
        likelihood += (1.0 - feature_vector.Infrastructure_entropy) * 0.05

        # No Tor/VPS
        if not feature_vector.Tor_flag:
            likelihood += 0.1
        if not feature_vector.VPS_flag:
            likelihood += 0.05

        # Benign behavioral states
        if behavior_state:
            benign_states = {BehaviorState.DORMANCY, BehaviorState.PASSIVE_RECON}

            if behavior_state in benign_states:
                likelihood += 0.1

        # Cap
        likelihood = min(0.99, likelihood)

        return likelihood


class BayesianScorer:
    """
    Bayesian confidence scoring engine

    Applies Bayes' theorem to compute posterior malicious probability
    """

    def __init__(self):
        self.prior_dist = PriorDistribution()
        self.likelihood_est = LikelihoodEstimator()

        logger.info("Bayesian scorer initialized")

    def score(
        self,
        feature_vector: Any,
        behavior_state: Any = None,
        evidence: dict[str, Any] = None,
    ) -> float:
        """
        Compute Bayesian confidence score

        Args:
            feature_vector: L4 feature vector
            behavior_state: L5 inferred state (optional)
            evidence: Additional evidence dict (optional)

        Returns:
            Confidence score 0.0-1.0
        """
        # Get prior P(M)
        prior_malicious = self.prior_dist.get_prior(feature_vector)

        # Get likelihoods
        p_e_given_m = self.likelihood_est.estimate_malicious_likelihood(
            feature_vector, behavior_state
        )

        p_e_given_not_m = self.likelihood_est.estimate_benign_likelihood(
            feature_vector, behavior_state
        )

        # Apply Bayes' theorem
        # P(M|E) = P(E|M) * P(M) / [P(E|M)*P(M) + P(E|¬M)*(1-P(M))]

        numerator = p_e_given_m * prior_malicious
        denominator = (p_e_given_m * prior_malicious) + (
            p_e_given_not_m * (1 - prior_malicious)
        )

        if denominator < 1e-10:
            posterior = 0.5  # Undefined, default to neutral
        else:
            posterior = numerator / denominator

        # Clamp to valid range
        posterior = max(0.0, min(1.0, posterior))

        logger.info(f"Bayesian score computed: {posterior:.4f}")
        logger.debug(f"  Prior P(M): {prior_malicious:.4f}")
        logger.debug(f"  P(E|M): {p_e_given_m:.4f}")
        logger.debug(f"  P(E|¬M): {p_e_given_not_m:.4f}")

        return posterior

    def score_to_percentage(self, score: float) -> int:
        """Convert 0-1 score to 0-100 percentage"""
        return int(score * 100)


class ConfidenceAggregator:
    """
    L6: Bayesian Confidence Aggregation

    Orchestrates Bayesian scoring across event pipeline
    """

    def __init__(self):
        self.scorer = BayesianScorer()
        self.score_history: dict[str, list] = {}  # ip -> [scores]

        logger.info("L6 Confidence Aggregator initialized")

    def aggregate(
        self, event: Any, feature_vector: Any, behavior_state: Any = None
    ) -> dict[str, Any]:
        """
        Aggregate confidence score for event

        Args:
            event: AdversarialEvent
            feature_vector: L4 attribution features
            behavior_state: L5 behavioral state

        Returns:
            Confidence assessment dict
        """
        from ..core.ingestion_gateway import AdversarialEvent

        if not isinstance(event, AdversarialEvent):
            raise TypeError("Event must be AdversarialEvent")

        # Compute Bayesian score
        confidence_score = self.scorer.score(feature_vector, behavior_state)
        confidence_pct = self.scorer.score_to_percentage(confidence_score)

        # Track history for trend analysis
        ip = event.source_ip
        if ip not in self.score_history:
            self.score_history[ip] = []

        self.score_history[ip].append(confidence_score)

        # Calculate trend (increasing=escalating threat)
        trend = self._calculate_trend(ip)

        # Determine threat classification
        threat_class = self._classify_threat(confidence_pct)

        result = {
            "confidence_score": confidence_score,
            "confidence_percentage": confidence_pct,
            "threat_classification": threat_class,
            "trend": trend,
            "event_id": event.event_id,
            "source_ip": ip,
        }

        logger.info(f"Confidence aggregated: {confidence_pct}% ({threat_class})")

        return result

    def _calculate_trend(self, ip: str) -> str:
        """Calculate score trend for IP"""
        if ip not in self.score_history or len(self.score_history[ip]) < 3:
            return "INSUFFICIENT_DATA"

        history = self.score_history[ip][-10:]  # Last 10

        # Simple linear trend
        if len(history) < 2:
            return "STABLE"

        recent_avg = sum(history[-3:]) / 3
        older_avg = sum(history[:-3]) / len(history[:-3])

        if recent_avg > older_avg + 0.1:
            return "ESCALATING"
        elif recent_avg < older_avg - 0.1:
            return "DECLINING"
        else:
            return "STABLE"

    def _classify_threat(self, confidence_pct: int) -> str:
        """Classify threat level from confidence score"""
        if confidence_pct < 30:
            return "LOW"
        elif confidence_pct < 50:
            return "MEDIUM"
        elif confidence_pct < 70:
            return "HIGH"
        elif confidence_pct < 85:
            return "CRITICAL"
        else:
            return "SEVERE"


__all__ = [
    "PriorDistribution",
    "LikelihoodEstimator",
    "BayesianScorer",
    "ConfidenceAggregator",
]
