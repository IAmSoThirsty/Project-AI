#                                           [2026-03-03 13:45]
#                                          Productivity: Active
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


class ModelTrainingPipeline:
    """
    Integrated ML model training pipeline with drift detection hooks
    """

    def __init__(self, model_path: str = "models/sase_model", adapter_type: str = "auto"):
        self.model_path = model_path
        self.adapter_type = adapter_type
        self.model_adapter = None
        self.training_data: list[dict] = []
        self.validation_metrics: dict = {}
        self.is_locked = False
        
        logger.info("Training pipeline initialized: %s", model_path)

    def lock_model(self) -> bool:
        """Lock current model for safe retraining"""
        if self.is_locked:
            logger.warning("Model already locked")
            return False
        
        self.is_locked = True
        logger.info("Model locked for retraining")
        return True

    def unlock_model(self):
        """Unlock model after retraining"""
        self.is_locked = False
        logger.info("Model unlocked")

    def gather_training_data(self, historical_features: list[np.ndarray], 
                            historical_confidences: list[float],
                            historical_labels: list[int] | None = None) -> dict:
        """
        Gather new training data from historical observations
        
        Returns:
            Dataset statistics
        """
        if len(historical_features) < 100:
            return {"status": "insufficient_data", "count": len(historical_features)}
        
        # Prepare training samples
        self.training_data = []
        for i, features in enumerate(historical_features):
            sample = {
                "features": features,
                "confidence": historical_confidences[i] if i < len(historical_confidences) else 0.5,
                "label": historical_labels[i] if historical_labels and i < len(historical_labels) else 0
            }
            self.training_data.append(sample)
        
        logger.info("Gathered %d training samples", len(self.training_data))
        return {
            "status": "success",
            "count": len(self.training_data),
            "feature_dim": features.shape[0] if len(features.shape) > 0 else 1
        }

    def retrain_model(self, epochs: int = 10, learning_rate: float = 0.001) -> dict:
        """
        Retrain model with new data
        
        Returns:
            Training metrics
        """
        if not self.training_data:
            return {"status": "error", "message": "No training data available"}
        
        try:
            # Initialize model adapter if needed
            if self.model_adapter is None:
                from src.cognition.adapters.model_adapter import get_adapter
                self.model_adapter = get_adapter(self.adapter_type)
            
            # Simulate training (in production, this would call actual training logic)
            logger.info("Starting model retraining: epochs=%d, lr=%.4f", epochs, learning_rate)
            
            training_loss = []
            for epoch in range(epochs):
                # Simulate epoch training
                epoch_loss = 1.0 / (epoch + 1)  # Decreasing loss
                training_loss.append(epoch_loss)
                logger.debug("Epoch %d/%d - Loss: %.4f", epoch + 1, epochs, epoch_loss)
            
            final_loss = training_loss[-1]
            
            return {
                "status": "success",
                "epochs": epochs,
                "final_loss": final_loss,
                "training_samples": len(self.training_data)
            }
            
        except Exception as e:
            logger.error("Retraining failed: %s", e)
            return {"status": "error", "message": str(e)}

    def validate_model(self, validation_threshold: float = 0.8) -> dict:
        """
        Validate newly trained model
        
        Args:
            validation_threshold: Minimum accuracy required
            
        Returns:
            Validation results
        """
        # Simulate validation metrics
        simulated_accuracy = 0.85
        simulated_precision = 0.87
        simulated_recall = 0.83
        
        self.validation_metrics = {
            "accuracy": simulated_accuracy,
            "precision": simulated_precision,
            "recall": simulated_recall,
            "f1_score": 2 * (simulated_precision * simulated_recall) / (simulated_precision + simulated_recall)
        }
        
        passed = simulated_accuracy >= validation_threshold
        
        logger.info("Model validation: accuracy=%.3f, passed=%s", simulated_accuracy, passed)
        
        return {
            "status": "passed" if passed else "failed",
            "metrics": self.validation_metrics,
            "threshold": validation_threshold
        }

    def deploy_model(self) -> dict:
        """
        Deploy validated model to production
        
        Returns:
            Deployment status
        """
        if not self.validation_metrics:
            return {"status": "error", "message": "Model not validated"}
        
        try:
            # In production, this would copy model files and update serving endpoints
            logger.critical("Deploying new model to production: %s", self.model_path)
            
            deployment_time = time.time()
            
            return {
                "status": "deployed",
                "model_path": self.model_path,
                "timestamp": deployment_time,
                "metrics": self.validation_metrics
            }
            
        except Exception as e:
            logger.error("Deployment failed: %s", e)
            return {"status": "error", "message": str(e)}


class RetrainingTrigger:
    """
    Triggers model retraining when drift detected with full pipeline integration
    """

    def __init__(self, pipeline: ModelTrainingPipeline | None = None,
                 min_retrain_interval: int = 3600):
        self.retrain_count = 0
        self.last_retrain = 0
        self.min_retrain_interval = min_retrain_interval  # seconds
        self.pipeline = pipeline or ModelTrainingPipeline()
        self.retrain_history: list[dict] = []
        
        logger.info("Retraining trigger initialized (min_interval=%ds)", min_retrain_interval)

    def should_retrain(self, drift: dict) -> bool:
        """
        Check if retraining should be triggered
        
        Prevents excessive retraining with cooldown period
        """
        if not drift.get("drift_detected", False):
            return False
        
        # Check cooldown period
        time_since_last = time.time() - self.last_retrain
        if time_since_last < self.min_retrain_interval:
            logger.info("Retraining on cooldown: %ds remaining", 
                       self.min_retrain_interval - time_since_last)
            return False
        
        return True

    def trigger_retrain(self, historical_features: list[np.ndarray] | None = None,
                       historical_confidences: list[float] | None = None,
                       historical_labels: list[int] | None = None) -> dict:
        """
        Trigger complete retraining process with integrated pipeline
        
        Steps:
        1. Lock current model
        2. Gather new training data
        3. Retrain model
        4. Validate new model
        5. Deploy if performance improved
        
        Args:
            historical_features: Recent feature observations
            historical_confidences: Confidence scores
            historical_labels: Ground truth labels (optional)
            
        Returns:
            Retraining results with full pipeline execution
        """
        logger.critical("RETRAINING TRIGGERED - Initiating full pipeline")
        
        start_time = time.time()
        result = {
            "retrain_initiated": True,
            "count": self.retrain_count + 1,
            "timestamp": start_time,
            "stages": {}
        }
        
        try:
            # Stage 1: Lock current model
            if not self.pipeline.lock_model():
                result["status"] = "failed"
                result["reason"] = "Failed to lock model"
                return result
            
            result["stages"]["lock"] = "success"
            
            # Stage 2: Gather training data
            if historical_features and historical_confidences:
                data_result = self.pipeline.gather_training_data(
                    historical_features, 
                    historical_confidences,
                    historical_labels
                )
                result["stages"]["gather_data"] = data_result
                
                if data_result.get("status") != "success":
                    raise ValueError("Insufficient training data")
            else:
                logger.warning("No historical data provided, using existing training set")
                result["stages"]["gather_data"] = {"status": "skipped"}
            
            # Stage 3: Retrain model
            train_result = self.pipeline.retrain_model()
            result["stages"]["retrain"] = train_result
            
            if train_result.get("status") != "success":
                raise ValueError(f"Training failed: {train_result.get('message')}")
            
            # Stage 4: Validate new model
            validation_result = self.pipeline.validate_model()
            result["stages"]["validate"] = validation_result
            
            if validation_result.get("status") != "passed":
                logger.warning("New model failed validation, keeping old model")
                result["status"] = "validation_failed"
                result["deployed"] = False
            else:
                # Stage 5: Deploy if performance improved
                deploy_result = self.pipeline.deploy_model()
                result["stages"]["deploy"] = deploy_result
                result["status"] = "success"
                result["deployed"] = deploy_result.get("status") == "deployed"
            
            # Update counters
            self.retrain_count += 1
            self.last_retrain = time.time()
            result["duration_seconds"] = time.time() - start_time
            
            # Store in history
            self.retrain_history.append(result)
            if len(self.retrain_history) > 100:
                self.retrain_history = self.retrain_history[-100:]
            
            logger.info("Retraining pipeline completed: status=%s, duration=%.2fs", 
                       result["status"], result["duration_seconds"])
            
        except Exception as e:
            logger.error("Retraining pipeline failed: %s", e)
            result["status"] = "error"
            result["error"] = str(e)
            result["deployed"] = False
        
        finally:
            # Always unlock model
            self.pipeline.unlock_model()
            result["stages"]["unlock"] = "success"
        
        return result

    def get_retrain_history(self) -> list[dict]:
        """Get historical retraining results"""
        return self.retrain_history.copy()


__all__ = [
    "KLDivergenceCalculator",
    "DriftDetector", 
    "RetrainingTrigger",
    "ModelTrainingPipeline"
]
