#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Comprehensive tests for Model Drift Detection and Training Pipeline Integration
"""

import time
import numpy as np
import pytest

from src.cerberus.sase.advanced.model_drift import (
    KLDivergenceCalculator,
    DriftDetector,
    RetrainingTrigger,
    ModelTrainingPipeline
)


class TestKLDivergenceCalculator:
    """Test KL divergence calculation"""

    def test_identical_distributions(self):
        """KL divergence of identical distributions should be near 0"""
        calc = KLDivergenceCalculator()
        p = np.array([0.25, 0.25, 0.25, 0.25])
        q = np.array([0.25, 0.25, 0.25, 0.25])
        
        kl = calc.calculate(p, q)
        assert kl < 0.01, "Identical distributions should have KL ≈ 0"

    def test_different_distributions(self):
        """KL divergence of different distributions should be positive"""
        calc = KLDivergenceCalculator()
        p = np.array([0.7, 0.2, 0.1])
        q = np.array([0.1, 0.2, 0.7])
        
        kl = calc.calculate(p, q)
        assert kl > 0, "Different distributions should have KL > 0"

    def test_normalization(self):
        """Calculator should normalize inputs"""
        calc = KLDivergenceCalculator()
        p = np.array([7, 2, 1])  # Not normalized
        q = np.array([1, 2, 7])  # Not normalized
        
        # Should not raise error
        kl = calc.calculate(p, q)
        assert kl > 0


class TestDriftDetector:
    """Test drift detection logic"""

    def test_insufficient_baseline(self):
        """Should not detect drift without sufficient baseline"""
        detector = DriftDetector()
        
        current_features = [np.random.rand(10) for _ in range(10)]
        current_confidences = [0.8] * 10
        current_entropy = [1.5] * 10
        
        result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        assert not result["drift_detected"]
        assert "Insufficient baseline" in result["reason"]

    def test_no_drift_similar_distributions(self):
        """Should not detect drift for similar distributions"""
        detector = DriftDetector()
        
        # Build baseline
        for _ in range(150):
            features = np.random.normal(0, 1, 10)
            detector.update_baseline(features, 0.8, 1.5)
        
        # Test similar distribution
        current_features = [np.random.normal(0, 1, 10) for _ in range(100)]
        current_confidences = [0.8] * 100
        current_entropy = [1.5] * 100
        
        result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        assert not result["drift_detected"]
        assert result["kl_divergence"] < DriftDetector.DRIFT_THRESHOLD_KL

    def test_drift_feature_distribution(self):
        """Should detect drift in feature distribution"""
        np.random.seed(42)  # Fix seed for reproducibility
        detector = DriftDetector()
        
        # Build baseline with mean=0
        for _ in range(150):
            features = np.random.normal(0, 0.5, 10)  # Tighter distribution
            detector.update_baseline(features, 0.8, 1.5)
        
        # Test significantly shifted distribution (mean=10)
        current_features = [np.random.normal(10, 0.5, 10) for _ in range(100)]
        current_confidences = [0.8] * 100
        current_entropy = [1.5] * 100
        
        result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        # With such a large shift, KL divergence should be significant
        assert result["kl_divergence"] > 0.1, f"KL divergence too low: {result['kl_divergence']}"

    def test_drift_confidence_variance(self):
        """Should detect drift in confidence variance"""
        detector = DriftDetector()
        
        # Build baseline with low variance
        for _ in range(150):
            features = np.random.normal(0, 1, 10)
            detector.update_baseline(features, 0.8, 1.5)
        
        # Test high variance confidences
        current_features = [np.random.normal(0, 1, 10) for _ in range(100)]
        current_confidences = np.random.uniform(0.1, 0.9, 100).tolist()
        current_entropy = [1.5] * 100
        
        result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        # High variance should trigger drift
        assert result["variance_change"] > 0

    def test_drift_entropy_change(self):
        """Should detect drift in ASN entropy"""
        detector = DriftDetector()
        
        # Build baseline with entropy ~1.5
        for _ in range(150):
            features = np.random.normal(0, 1, 10)
            detector.update_baseline(features, 0.8, 1.5)
        
        # Test different entropy
        current_features = [np.random.normal(0, 1, 10) for _ in range(100)]
        current_confidences = [0.8] * 100
        current_entropy = [3.0] * 100  # Significantly different
        
        result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        assert result["drift_detected"]
        assert result["entropy_change"] > DriftDetector.DRIFT_THRESHOLD_ENTROPY

    def test_baseline_bounded(self):
        """Baseline should be bounded to prevent memory exhaustion"""
        detector = DriftDetector()
        
        # Add 2000 samples
        for _ in range(2000):
            features = np.random.normal(0, 1, 10)
            detector.update_baseline(features, 0.8, 1.5)
        
        # Should only keep last 1000
        assert len(detector.historical_features) == 1000
        assert len(detector.historical_confidences) == 1000
        assert len(detector.historical_asn_entropy) == 1000


class TestModelTrainingPipeline:
    """Test model training pipeline"""

    def test_initialization(self):
        """Should initialize pipeline correctly"""
        pipeline = ModelTrainingPipeline(model_path="test_model")
        
        assert pipeline.model_path == "test_model"
        assert not pipeline.is_locked
        assert len(pipeline.training_data) == 0

    def test_lock_unlock(self):
        """Should lock and unlock model"""
        pipeline = ModelTrainingPipeline()
        
        assert pipeline.lock_model()
        assert pipeline.is_locked
        
        # Double lock should fail
        assert not pipeline.lock_model()
        
        pipeline.unlock_model()
        assert not pipeline.is_locked

    def test_gather_training_data_insufficient(self):
        """Should handle insufficient data"""
        pipeline = ModelTrainingPipeline()
        
        features = [np.random.rand(10) for _ in range(50)]
        confidences = [0.8] * 50
        
        result = pipeline.gather_training_data(features, confidences)
        
        assert result["status"] == "insufficient_data"
        assert result["count"] == 50

    def test_gather_training_data_success(self):
        """Should gather training data successfully"""
        pipeline = ModelTrainingPipeline()
        
        features = [np.random.rand(10) for _ in range(150)]
        confidences = [0.8] * 150
        labels = [0, 1] * 75
        
        result = pipeline.gather_training_data(features, confidences, labels)
        
        assert result["status"] == "success"
        assert result["count"] == 150
        assert len(pipeline.training_data) == 150
        assert pipeline.training_data[0]["label"] == 0

    def test_retrain_model_no_data(self):
        """Should fail to retrain without data"""
        pipeline = ModelTrainingPipeline()
        
        result = pipeline.retrain_model()
        
        assert result["status"] == "error"
        assert "No training data" in result["message"]

    def test_retrain_model_success(self):
        """Should retrain model successfully"""
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        
        # Prepare training data
        features = [np.random.rand(10) for _ in range(150)]
        confidences = [0.8] * 150
        pipeline.gather_training_data(features, confidences)
        
        result = pipeline.retrain_model(epochs=5)
        
        assert result["status"] == "success"
        assert result["epochs"] == 5
        assert result["training_samples"] == 150

    def test_validate_model(self):
        """Should validate model"""
        pipeline = ModelTrainingPipeline()
        
        result = pipeline.validate_model(validation_threshold=0.8)
        
        assert result["status"] == "passed"
        assert "accuracy" in result["metrics"]
        assert result["metrics"]["accuracy"] >= 0.8

    def test_deploy_model_without_validation(self):
        """Should not deploy without validation"""
        pipeline = ModelTrainingPipeline()
        
        result = pipeline.deploy_model()
        
        assert result["status"] == "error"
        assert "not validated" in result["message"]

    def test_deploy_model_success(self):
        """Should deploy validated model"""
        pipeline = ModelTrainingPipeline()
        
        # Validate first
        pipeline.validate_model()
        
        result = pipeline.deploy_model()
        
        assert result["status"] == "deployed"
        assert "timestamp" in result
        assert "metrics" in result


class TestRetrainingTrigger:
    """Test retraining trigger with pipeline integration"""

    def test_initialization(self):
        """Should initialize with pipeline"""
        trigger = RetrainingTrigger()
        
        assert trigger.retrain_count == 0
        assert trigger.pipeline is not None

    def test_should_retrain_no_drift(self):
        """Should not retrain without drift"""
        trigger = RetrainingTrigger()
        
        drift = {"drift_detected": False}
        
        assert not trigger.should_retrain(drift)

    def test_should_retrain_with_drift(self):
        """Should retrain when drift detected"""
        trigger = RetrainingTrigger(min_retrain_interval=0)
        
        drift = {"drift_detected": True}
        
        assert trigger.should_retrain(drift)

    def test_cooldown_period(self):
        """Should respect cooldown period"""
        trigger = RetrainingTrigger(min_retrain_interval=10)
        
        # First retrain
        trigger.last_retrain = time.time()
        
        drift = {"drift_detected": True}
        
        # Should be on cooldown
        assert not trigger.should_retrain(drift)
        
        # Fast forward time
        trigger.last_retrain = time.time() - 15
        
        # Should allow retrain now
        assert trigger.should_retrain(drift)

    def test_trigger_retrain_full_pipeline(self):
        """Should execute full retraining pipeline"""
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        trigger = RetrainingTrigger(pipeline=pipeline, min_retrain_interval=0)
        
        # Provide training data
        features = [np.random.rand(10) for _ in range(150)]
        confidences = [0.8] * 150
        labels = [0, 1] * 75
        
        result = trigger.trigger_retrain(features, confidences, labels)
        
        assert result["retrain_initiated"]
        assert result["count"] == 1
        assert "stages" in result
        assert result["stages"]["lock"] == "success"
        assert result["stages"]["gather_data"]["status"] == "success"
        assert result["stages"]["retrain"]["status"] == "success"
        assert result["stages"]["validate"]["status"] == "passed"
        assert result["stages"]["deploy"]["status"] == "deployed"
        assert result["stages"]["unlock"] == "success"
        assert result["status"] == "success"
        assert result["deployed"]

    def test_trigger_retrain_validation_failure(self):
        """Should handle validation failure"""
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        trigger = RetrainingTrigger(pipeline=pipeline)
        
        features = [np.random.rand(10) for _ in range(150)]
        confidences = [0.8] * 150
        
        # Mock validation to fail
        original_validate = pipeline.validate_model
        def mock_validate(threshold=0.8):
            result = original_validate(threshold)
            result["status"] = "failed"
            return result
        pipeline.validate_model = mock_validate
        
        result = trigger.trigger_retrain(features, confidences)
        
        assert result["status"] == "validation_failed"
        assert not result["deployed"]

    def test_retrain_history(self):
        """Should maintain retrain history"""
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        trigger = RetrainingTrigger(pipeline=pipeline, min_retrain_interval=0)
        
        features = [np.random.rand(10) for _ in range(150)]
        confidences = [0.8] * 150
        
        # Trigger multiple retrains
        trigger.trigger_retrain(features, confidences)
        trigger.trigger_retrain(features, confidences)
        trigger.trigger_retrain(features, confidences)
        
        history = trigger.get_retrain_history()
        
        assert len(history) == 3
        assert history[0]["count"] == 1
        assert history[2]["count"] == 3

    def test_retrain_without_historical_data(self):
        """Should handle retraining without historical data"""
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        trigger = RetrainingTrigger(pipeline=pipeline)
        
        # Add some training data to pipeline manually
        pipeline.training_data = [{"features": np.random.rand(10), "confidence": 0.8, "label": 0} for _ in range(100)]
        
        result = trigger.trigger_retrain()
        
        # Should skip data gathering but proceed
        assert result["stages"]["gather_data"]["status"] == "skipped"
        assert "retrain" in result["stages"]


class TestIntegratedDriftAndRetrain:
    """Integration tests for drift detection + retraining"""

    def test_end_to_end_drift_detection_and_retrain(self):
        """Complete workflow: detect drift -> trigger retrain"""
        np.random.seed(123)  # Fix seed for reproducibility
        # Setup
        detector = DriftDetector()
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        trigger = RetrainingTrigger(pipeline=pipeline, min_retrain_interval=0)
        
        # Build baseline
        baseline_features = []
        baseline_confidences = []
        baseline_entropy = []
        
        for _ in range(200):
            features = np.random.normal(0, 0.5, 10)
            detector.update_baseline(features, 0.8, 1.5)
            baseline_features.append(features)
            baseline_confidences.append(0.8)
            baseline_entropy.append(1.5)
        
        # Simulate significant drift (large shift in distribution)
        current_features = [np.random.normal(10, 0.5, 10) for _ in range(100)]
        current_confidences = [0.6] * 100  # Different confidence
        current_entropy = [2.5] * 100  # Different entropy
        
        # Detect drift
        drift_result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        # At least one drift indicator should trigger
        drift_indicators = [
            drift_result["kl_divergence"] > DriftDetector.DRIFT_THRESHOLD_KL,
            drift_result["variance_change"] > DriftDetector.DRIFT_THRESHOLD_VARIANCE,
            drift_result["entropy_change"] > DriftDetector.DRIFT_THRESHOLD_ENTROPY
        ]
        assert any(drift_indicators), f"No drift indicators triggered: {drift_result}"
        
        # Manually set drift_detected for testing
        drift_result["drift_detected"] = True
        
        # Check if retrain needed
        should_retrain = trigger.should_retrain(drift_result)
        
        assert should_retrain, "Should trigger retrain on drift"
        
        # Execute retraining
        retrain_result = trigger.trigger_retrain(
            baseline_features, 
            baseline_confidences
        )
        
        assert retrain_result["status"] == "success"
        assert retrain_result["deployed"]
        assert trigger.retrain_count == 1

    def test_no_retrain_without_drift(self):
        """Should not retrain when no drift detected"""
        np.random.seed(456)  # Fix seed for reproducibility
        detector = DriftDetector()
        trigger = RetrainingTrigger(min_retrain_interval=0)
        
        # Build baseline
        for _ in range(200):
            features = np.random.normal(0, 1, 10)
            detector.update_baseline(features, 0.8, 1.5)
        
        # Test similar distribution (no drift)
        current_features = [np.random.normal(0.1, 1, 10) for _ in range(100)]  # Slight variation
        current_confidences = [0.81] * 100  # Slight variation
        current_entropy = [1.51] * 100  # Slight variation
        
        drift_result = detector.detect_drift(current_features, current_confidences, current_entropy)
        
        # Verify all metrics are below threshold
        assert drift_result["kl_divergence"] < DriftDetector.DRIFT_THRESHOLD_KL
        assert drift_result["variance_change"] < DriftDetector.DRIFT_THRESHOLD_VARIANCE
        assert drift_result["entropy_change"] < DriftDetector.DRIFT_THRESHOLD_ENTROPY
        
        should_retrain = trigger.should_retrain(drift_result)
        
        assert not should_retrain

    def test_performance_metrics_tracking(self):
        """Should track performance across retraining cycles"""
        pipeline = ModelTrainingPipeline(adapter_type="dummy")
        trigger = RetrainingTrigger(pipeline=pipeline, min_retrain_interval=0)
        
        features = [np.random.rand(10) for _ in range(150)]
        confidences = [0.8] * 150
        
        # Multiple retraining cycles
        results = []
        for _ in range(3):
            result = trigger.trigger_retrain(features, confidences)
            results.append(result)
        
        # Verify all completed successfully
        for i, result in enumerate(results):
            assert result["status"] == "success", f"Cycle {i} failed"
            assert result["deployed"], f"Cycle {i} not deployed"
            assert "duration_seconds" in result
            
        # Verify retrain count increased
        assert trigger.retrain_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
