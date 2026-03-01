"""
SASE - Sovereign Adversarial Signal Engine
L13: Model Training & Drift Governance

Detects distribution drift and triggers retraining.

DRIFT DETECTION:
- KL divergence between historical and current distributions
- Change in confidence distribution variance
- ASN entropy change

Trigger retraining when drift exceeds threshold.
"""

import logging
import time

import numpy as np

logger = logging.getLogger("SASE.L13.ModelDrift")


class KLDivergenceCalculator:
    """
    Kullback-Leibler divergence calculator

    Measures distribution drift
    """

    @staticmethod
    def calculate(p: np.ndarray, q: np.ndarray) -> float:
        """
        Calculate KL(P || Q)

        Args:
            p: Historical distribution
            q: Current distribution

        Returns:
            KL divergence (bits)
        """
        # Normalize to probabilities
        p = p / np.sum(p)
        q = q / np.sum(q)

        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        p = p + epsilon
        q = q + epsilon

        # KL divergence
        kl = np.sum(p * np.log2(p / q))

        return float(kl)


class DriftDetector:
    """
    Detects model drift across multiple dimensions

    Monitors:
    - Feature distribution drift (KL divergence)
    - Confidence variance changes
    - ASN entropy changes
    """

    DRIFT_THRESHOLD_KL = 0.5  # bits
    DRIFT_THRESHOLD_VARIANCE = 0.1
    DRIFT_THRESHOLD_ENTROPY = 0.15

    def __init__(self):
        # Historical baselines
        self.historical_features: list[np.ndarray] = []
        self.historical_confidences: list[float] = []
        self.historical_asn_entropy: list[float] = []

        self.kl_calc = KLDivergenceCalculator()

        logger.info("Drift detector initialized")

    def update_baseline(
        self, features: np.ndarray, confidence: float, asn_entropy: float
    ):
        """Update historical baseline"""
        self.historical_features.append(features)
        self.historical_confidences.append(confidence)
        self.historical_asn_entropy.append(asn_entropy)

        # Keep last 1000 samples
        if len(self.historical_features) > 1000:
            self.historical_features = self.historical_features[-1000:]
            self.historical_confidences = self.historical_confidences[-1000:]
            self.historical_asn_entropy = self.historical_asn_entropy[-1000:]

    def detect_drift(
        self,
        current_features: list[np.ndarray],
        current_confidences: list[float],
        current_asn_entropy: list[float],
    ) -> dict:
        """
        Detect drift in current distribution

        Returns drift metrics and whether retraining is needed
        """
        if len(self.historical_features) < 100:
            return {"drift_detected": False, "reason": "Insufficient baseline data"}

        # 1. Feature distribution drift (KL divergence)
        historical_dist = self._compute_feature_distribution(self.historical_features)
        current_dist = self._compute_feature_distribution(current_features)

        kl_divergence = self.kl_calc.calculate(historical_dist, current_dist)

        # 2. Confidence variance change
        hist_var = np.var(self.historical_confidences)
        curr_var = np.var(current_confidences)
        variance_change = abs(curr_var - hist_var)

        # 3. ASN entropy change
        hist_entropy = np.mean(self.historical_asn_entropy)
        curr_entropy = np.mean(current_asn_entropy)
        entropy_change = abs(curr_entropy - hist_entropy)

        # Determine if drift detected
        drift_detected = (
            kl_divergence > self.DRIFT_THRESHOLD_KL
            or variance_change > self.DRIFT_THRESHOLD_VARIANCE
            or entropy_change > self.DRIFT_THRESHOLD_ENTROPY
        )

        result = {
            "drift_detected": drift_detected,
            "kl_divergence": kl_divergence,
            "variance_change": variance_change,
            "entropy_change": entropy_change,
            "thresholds": {
                "kl": self.DRIFT_THRESHOLD_KL,
                "variance": self.DRIFT_THRESHOLD_VARIANCE,
                "entropy": self.DRIFT_THRESHOLD_ENTROPY,
            },
        }

        if drift_detected:
            logger.warning(
                f"DRIFT DETECTED: KL={kl_divergence:.3f}, Var={variance_change:.3f}, Ent={entropy_change:.3f}"
            )

        return result

    def _compute_feature_distribution(self, features: list[np.ndarray]) -> np.ndarray:
        """Compute feature distribution histogram"""
        if not features:
            return np.array([1.0])  # Uniform

        # Stack features
        stacked = np.vstack(features)

        # Compute histogram (discretize into 10 bins)
        mean_features = np.mean(stacked, axis=1)
        hist, _ = np.histogram(mean_features, bins=10, density=True)

        return hist + 1e-10  # Add epsilon


class RetrainingTrigger:
    """
    Triggers model retraining when drift detected
    """

    def __init__(self):
        self.retrain_count = 0
        self.last_retrain = 0

    def should_retrain(self, drift: dict) -> bool:
        """Check if retraining should be triggered"""
        return drift.get("drift_detected", False)

    def trigger_retrain(self):
        """Trigger retraining process"""
        logger.critical("RETRAINING TRIGGERED")

        # TODO: Integrate with model training pipeline
        # 1. Lock current model
        # 2. Gather new training data
        # 3. Retrain model
        # 4. Validate new model
        # 5. Deploy if performance improved

        self.retrain_count += 1
        self.last_retrain = time.time()

        return {"retrain_initiated": True, "count": self.retrain_count}


__all__ = ["KLDivergenceCalculator", "DriftDetector", "RetrainingTrigger"]
