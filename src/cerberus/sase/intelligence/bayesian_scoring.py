#                                           [2026-04-09 11:30]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L6: Bayesian Confidence Aggregation

Probabilistic threat scoring using Bayesian inference.
Hardened against adversarial memory exhaustion and temporal drift.
"""

import logging
from collections import deque
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("SASE.L6.BayesianScoring")


@dataclass
class PriorDistribution:
    """
    Prior probability distribution
    Base rates for malicious vs benign behavior.
    """

    malicious_base_rate: float = 0.01

    def get_prior(self, feature_vector: Any = None) -> float:
        """Get prior probability P(M) with indicator adjustments."""
        from .attribution import FeatureVector

        if feature_vector is None:
            return self.malicious_base_rate

        adjusted_prior = self.malicious_base_rate
        if isinstance(feature_vector, FeatureVector):
            if feature_vector.Tor_flag:
                adjusted_prior += 0.2
            if feature_vector.ASN_risk > 0.7:
                adjusted_prior += 0.15
            if feature_vector.Historical_reuse_count > 10:
                adjusted_prior += 0.1
            adjusted_prior = min(0.95, adjusted_prior)

        return adjusted_prior


@dataclass
class LikelihoodEstimator:
    """
    Likelihood estimation for observations.
    P(E|M) = Likelihood given malicious
    P(E|¬M) = Likelihood given benign
    """

    def estimate_malicious_likelihood(
        self, feature_vector: Any, behavior_state: Any = None
    ) -> float:
        """Estimate P(E|M) - likelihood given malicious actor."""
        from .attribution import FeatureVector
        from .behavioral_model import BehaviorState

        if not isinstance(feature_vector, FeatureVector):
            return 0.5

        likelihood = 0.5
        likelihood += feature_vector.ASN_risk * 0.15
        likelihood += feature_vector.Geo_anomaly_score * 0.1
        likelihood += feature_vector.Token_sensitivity * 0.15
        likelihood += feature_vector.Time_of_day_deviation * 0.05
        likelihood += feature_vector.Infrastructure_entropy * 0.1

        if feature_vector.Tor_flag:
            likelihood += 0.2
        if feature_vector.VPS_flag:
            likelihood += 0.1

        if behavior_state:
            escalation_states = {
                BehaviorState.ESCALATION_ATTEMPT,
                BehaviorState.API_ENUMERATION,
                BehaviorState.CREDENTIAL_USE,
            }
            if behavior_state in escalation_states:
                likelihood += 0.15

        return min(0.99, likelihood)

    def estimate_benign_likelihood(
        self, feature_vector: Any, behavior_state: Any = None
    ) -> float:
        """Estimate P(E|¬M) - likelihood given benign actor."""
        from .attribution import FeatureVector
        from .behavioral_model import BehaviorState

        if not isinstance(feature_vector, FeatureVector):
            return 0.5

        likelihood = 0.5
        likelihood += (1.0 - feature_vector.ASN_risk) * 0.1
        likelihood += (1.0 - feature_vector.Geo_anomaly_score) * 0.05
        likelihood += (1.0 - feature_vector.Time_of_day_deviation) * 0.05
        likelihood += (1.0 - feature_vector.Infrastructure_entropy) * 0.05

        if not feature_vector.Tor_flag:
            likelihood += 0.1
        if not feature_vector.VPS_flag:
            likelihood += 0.05

        if behavior_state:
            benign_states = {BehaviorState.DORMANCY, BehaviorState.PASSIVE_RECON}
            if behavior_state in benign_states:
                likelihood += 0.1

        return min(0.99, likelihood)


class BayesianScorer:
    """
    Bayesian confidence scoring engine.
    Applies Bayes' theorem to compute posterior malicious probability.
    """

    def __init__(self):
        self.prior_dist = PriorDistribution()
        self.likelihood_est = LikelihoodEstimator()
        logger.info("L6 Bayesian Scorer initialized")

    def score(
        self,
        feature_vector: Any,
        behavior_state: Any = None,
        _evidence: dict[str, Any] | None = None,
    ) -> float:
        """Compute Bayesian confidence score (0.0-1.0)."""
        prior_malicious = self.prior_dist.get_prior(feature_vector)
        p_e_given_m = self.likelihood_est.estimate_malicious_likelihood(feature_vector, behavior_state)
        p_e_given_not_m = self.likelihood_est.estimate_benign_likelihood(feature_vector, behavior_state)

        numerator = p_e_given_m * prior_malicious
        denominator = (p_e_given_m * prior_malicious) + (p_e_given_not_m * (1 - prior_malicious))

        if denominator < 1e-10:
            posterior = 0.5
        else:
            posterior = numerator / denominator

        posterior = max(0.0, min(1.0, posterior))

        logger.info("Bayesian score computed: %.4f (Prior: %.4f)", posterior, prior_malicious)
        return posterior

    def score_to_percentage(self, score: float) -> int:
        """Convert 0-1 score to 0-100 percentage."""
        return int(score * 100)


class ConfidenceAggregator:
    """
    L6: Bayesian Confidence Aggregation
    Hardened against memory exhaustion.
    """

    def __init__(self, max_score_history: int = 100):
        self.scorer = BayesianScorer()
        # Memory-hardened score history using deque
        self.score_history: dict[str, deque[float]] = {}
        self.max_score_history = max_score_history

        logger.info("L6 Confidence Aggregator initialized (history_depth=%d)", max_score_history)

    def aggregate(
        self, event: Any, feature_vector: Any, behavior_state: Any = None
    ) -> dict[str, Any]:
        """Aggregate confidence score for event with trend analysis."""
        confidence_score = self.scorer.score(feature_vector, behavior_state)
        confidence_pct = self.scorer.score_to_percentage(confidence_score)

        ip = getattr(event, "source_ip", "UNKNOWN")
        if ip not in self.score_history:
            if len(self.score_history) >= 1000:
                self.score_history.clear()  # Evict oldest entries
            self.score_history[ip] = deque(maxlen=self.max_score_history)

        self.score_history[ip].append(confidence_score)

        trend = self._calculate_trend(ip)
        threat_class = self._classify_threat(confidence_pct)

        result = {
            "confidence_score": confidence_score,
            "confidence_percentage": confidence_pct,
            "threat_classification": threat_class,
            "trend": trend,
            "event_id": getattr(event, "event_id", "UNKNOWN"),
            "source_ip": ip,
        }

        logger.info("Confidence aggregated: %d%% (%s) for %s", confidence_pct, threat_class, ip)
        return result

    def _calculate_trend(self, ip: str) -> str:
        """Calculate score trend for IP."""
        history = self.score_history.get(ip)
        if not history or len(history) < 3:
            return "INSUFFICIENT_DATA"

        recent = list(history)[-3:]
        older = list(history)[:-3]
        if not older:
            return "STABLE"

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)

        if recent_avg > older_avg + 0.1:
            return "ESCALATING"
        elif recent_avg < older_avg - 0.1:
            return "DECLINING"
        else:
            return "STABLE"

    def _classify_threat(self, confidence_pct: int) -> str:
        """Classify threat level."""
        if confidence_pct < 30: return "LOW"
        if confidence_pct < 50: return "MEDIUM"
        if confidence_pct < 70: return "HIGH"
        if confidence_pct < 85: return "CRITICAL"
        return "SEVERE"


__all__ = ["PriorDistribution", "LikelihoodEstimator", "BayesianScorer", "ConfidenceAggregator"]
