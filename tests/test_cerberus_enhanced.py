#                                           [2026-04-09 06:00]
#                                          Productivity: Ultimate
"""
Comprehensive Test Suite for Cerberus Enhanced
===============================================

Tests all components of the ultimate adaptive security system:
- Threat prediction (LSTM/Transformer)
- Zero-day detection
- Adaptive policy generation
- Threat intelligence integration
- OctoReflex coordination
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cognition.cerberus_enhanced import (
    AdaptivePolicyGenerator,
    AttackPhase,
    AttackPrediction,
    CerberusEnhanced,
    OctoReflexCoordinator,
    SecurityPolicy,
    ThreatEvent,
    ThreatIndicator,
    ThreatIntelligence,
    ThreatPredictor,
    ThreatSeverity,
    ZeroDayDetector,
    create_sample_threat_event,
)
from src.cognition.security_ml.anomaly_detector import AnomalyDetector
from src.cognition.security_ml.threat_lstm import ThreatLSTM
from src.cognition.security_ml.transformer_predictor import TransformerPredictor


class TestThreatIndicators:
    """Test threat indicator creation and management."""
    
    def test_threat_indicator_creation(self):
        """Test creating threat indicators."""
        indicator = ThreatIndicator(
            indicator_type="ip",
            value="192.168.1.100",
            severity=ThreatSeverity.HIGH,
            confidence=0.9,
            source="test_source",
            timestamp=datetime.now()
        )
        
        assert indicator.indicator_type == "ip"
        assert indicator.value == "192.168.1.100"
        assert indicator.severity == ThreatSeverity.HIGH
        assert indicator.confidence == 0.9
    
    def test_threat_indicator_with_mitre(self):
        """Test indicator with MITRE techniques."""
        indicator = ThreatIndicator(
            indicator_type="hash",
            value="abc123",
            severity=ThreatSeverity.CRITICAL,
            confidence=0.95,
            source="threat_feed",
            timestamp=datetime.now(),
            mitre_techniques=["T1190", "T1059"]
        )
        
        assert len(indicator.mitre_techniques) == 2
        assert "T1190" in indicator.mitre_techniques


class TestThreatEvents:
    """Test threat event creation and processing."""
    
    def test_threat_event_creation(self):
        """Test creating threat events."""
        event = ThreatEvent(
            event_id="test_001",
            timestamp=datetime.now(),
            event_type="suspicious_login",
            severity=ThreatSeverity.MEDIUM,
            source_ip="10.0.0.1"
        )
        
        assert event.event_id == "test_001"
        assert event.severity == ThreatSeverity.MEDIUM
        assert event.source_ip == "10.0.0.1"
    
    def test_threat_event_with_indicators(self):
        """Test event with multiple indicators."""
        indicators = [
            ThreatIndicator(
                indicator_type="ip",
                value="10.0.0.1",
                severity=ThreatSeverity.MEDIUM,
                confidence=0.7,
                source="internal",
                timestamp=datetime.now()
            ),
            ThreatIndicator(
                indicator_type="domain",
                value="malicious.example",
                severity=ThreatSeverity.HIGH,
                confidence=0.85,
                source="threat_feed",
                timestamp=datetime.now()
            )
        ]
        
        event = ThreatEvent(
            event_id="test_002",
            timestamp=datetime.now(),
            event_type="c2_communication",
            severity=ThreatSeverity.HIGH,
            indicators=indicators
        )
        
        assert len(event.indicators) == 2
        assert event.indicators[1].value == "malicious.example"


class TestThreatPredictor:
    """Test ML-based threat prediction."""
    
    def test_predictor_initialization(self):
        """Test predictor initialization."""
        predictor = ThreatPredictor()
        
        assert predictor.sequence_length == 50
        assert predictor.feature_dim == 32
        assert len(predictor.attack_patterns) == 0
    
    def test_feature_extraction(self):
        """Test extracting features from events."""
        predictor = ThreatPredictor()
        event = create_sample_threat_event()
        
        features = predictor.extract_features(event)
        
        assert features.shape == (32,)
        assert 0 <= features[0] <= 1  # Normalized severity
        assert features[1] == event.confidence
    
    def test_sequence_update(self):
        """Test updating event sequence."""
        predictor = ThreatPredictor()
        
        for i in range(10):
            event = ThreatEvent(
                event_id=f"event_{i}",
                timestamp=datetime.now(),
                event_type="test_event",
                severity=ThreatSeverity.MEDIUM
            )
            predictor.update_sequence(event)
        
        assert len(predictor.sequence_buffer) == 10
    
    def test_attack_prediction(self):
        """Test predicting next attack."""
        predictor = ThreatPredictor()
        
        # Add events to build pattern
        for i in range(15):
            event = ThreatEvent(
                event_id=f"event_{i}",
                timestamp=datetime.now(),
                event_type="escalating_attack",
                severity=ThreatSeverity(min(i % 5 + 2, 6)),
                attack_phase=AttackPhase.INITIAL_ACCESS
            )
            predictor.update_sequence(event)
        
        prediction = predictor.predict_next_attack()
        
        assert prediction is not None
        assert isinstance(prediction, AttackPrediction)
        assert 0 <= prediction.confidence <= 1
        assert 0 <= prediction.probability <= 1


class TestZeroDayDetector:
    """Test zero-day threat detection."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = ZeroDayDetector()
        
        assert detector.anomaly_threshold == 3.0
        assert len(detector.baseline_profiles) == 0
    
    def test_baseline_building(self):
        """Test building baseline profiles."""
        detector = ZeroDayDetector()
        
        # Create baseline events
        events = []
        for i in range(50):
            event = ThreatEvent(
                event_id=f"baseline_{i}",
                timestamp=datetime.now(),
                event_type="normal_login",
                severity=ThreatSeverity.LOW
            )
            events.append(event)
        
        detector.build_baseline(events)
        
        assert "normal_login" in detector.baseline_profiles
        assert detector.baseline_profiles["normal_login"]["count"] == 50
    
    def test_anomaly_detection(self):
        """Test detecting anomalous events."""
        detector = ZeroDayDetector()
        
        # Build baseline
        normal_events = [
            ThreatEvent(
                event_id=f"normal_{i}",
                timestamp=datetime.now(),
                event_type="normal_event",
                severity=ThreatSeverity.LOW
            )
            for i in range(100)
        ]
        detector.build_baseline(normal_events)
        
        # Test with anomalous event
        anomaly = ThreatEvent(
            event_id="anomaly_1",
            timestamp=datetime.now(),
            event_type="unknown_event",
            severity=ThreatSeverity.CRITICAL
        )
        
        is_anomaly, score, reason = detector.detect_anomaly(anomaly)
        
        assert is_anomaly
        assert score >= detector.anomaly_threshold
        assert "Unknown event type" in reason


class TestAdaptivePolicyGenerator:
    """Test adaptive policy generation."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = AdaptivePolicyGenerator()
        
        assert len(generator.policies) == 0
    
    def test_policy_generation_from_threat(self):
        """Test generating policy from threat."""
        generator = AdaptivePolicyGenerator()
        
        threat = ThreatEvent(
            event_id="threat_001",
            timestamp=datetime.now(),
            event_type="malware_detected",
            severity=ThreatSeverity.HIGH,
            source_ip="192.168.1.100",
            indicators=[
                ThreatIndicator(
                    indicator_type="ip",
                    value="192.168.1.100",
                    severity=ThreatSeverity.HIGH,
                    confidence=0.9,
                    source="detector",
                    timestamp=datetime.now()
                )
            ]
        )
        
        policy = generator.generate_policy_from_threat(threat)
        
        assert isinstance(policy, SecurityPolicy)
        assert policy.enabled
        assert len(policy.conditions) > 0
        assert len(policy.actions) > 0
    
    def test_policy_priority_calculation(self):
        """Test policy priority based on threat severity."""
        generator = AdaptivePolicyGenerator()
        
        low_threat = ThreatEvent(
            event_id="low_001",
            timestamp=datetime.now(),
            event_type="test",
            severity=ThreatSeverity.LOW,
            confidence=0.5
        )
        
        high_threat = ThreatEvent(
            event_id="high_001",
            timestamp=datetime.now(),
            event_type="test",
            severity=ThreatSeverity.CRITICAL,
            confidence=0.95
        )
        
        low_policy = generator.generate_policy_from_threat(low_threat)
        high_policy = generator.generate_policy_from_threat(high_threat)
        
        assert high_policy.priority > low_policy.priority


class TestThreatIntelligence:
    """Test threat intelligence integration."""
    
    def test_intel_initialization(self):
        """Test intelligence system initialization."""
        intel = ThreatIntelligence()
        
        assert intel.cache_dir.exists()
    
    def test_indicator_management(self):
        """Test adding and checking indicators."""
        intel = ThreatIntelligence()
        
        indicator = ThreatIndicator(
            indicator_type="ip",
            value="198.51.100.42",
            severity=ThreatSeverity.HIGH,
            confidence=0.9,
            source="test_feed",
            timestamp=datetime.now()
        )
        
        intel.add_indicator(indicator)
        
        result = intel.check_indicator("ip", "198.51.100.42")
        assert result is not None
        assert result.value == "198.51.100.42"
    
    def test_event_enrichment(self):
        """Test enriching events with threat intel."""
        intel = ThreatIntelligence()
        
        # Add indicator
        indicator = ThreatIndicator(
            indicator_type="ip",
            value="10.0.0.50",
            severity=ThreatSeverity.CRITICAL,
            confidence=0.95,
            source="threat_feed",
            timestamp=datetime.now()
        )
        intel.add_indicator(indicator)
        
        # Create event
        event = ThreatEvent(
            event_id="test_001",
            timestamp=datetime.now(),
            event_type="connection",
            severity=ThreatSeverity.MEDIUM,
            source_ip="10.0.0.50"
        )
        
        # Enrich
        enriched = intel.enrich_event(event)
        
        assert len(enriched.indicators) > 0
        assert enriched.severity == ThreatSeverity.CRITICAL


class TestOctoReflexCoordinator:
    """Test OctoReflex coordination."""
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        coordinator = OctoReflexCoordinator()
        
        assert len(coordinator.pending_actions) == 0
    
    @pytest.mark.asyncio
    async def test_containment_request(self):
        """Test requesting containment action."""
        coordinator = OctoReflexCoordinator()
        
        threat = ThreatEvent(
            event_id="threat_001",
            timestamp=datetime.now(),
            event_type="breach_attempt",
            severity=ThreatSeverity.CRITICAL,
            source_ip="192.168.1.200"
        )
        
        action = await coordinator.request_containment(threat, "isolate")
        
        assert action.action_type == "isolate"
        assert action.target == "192.168.1.200"
        assert action.severity == ThreatSeverity.CRITICAL


class TestThreatLSTM:
    """Test LSTM threat prediction model."""
    
    def test_lstm_initialization(self):
        """Test LSTM model initialization."""
        model = ThreatLSTM(input_dim=32, hidden_dim=64, num_layers=2)
        
        assert model.input_dim == 32
        assert model.hidden_dim == 64
        assert model.num_layers == 2
    
    def test_lstm_forward_pass(self):
        """Test LSTM forward pass."""
        model = ThreatLSTM(input_dim=32, hidden_dim=64)
        
        sequence = np.random.randn(10, 32)
        output = model.forward(sequence)
        
        assert output.shape == (10, 64)
    
    def test_lstm_prediction(self):
        """Test threat prediction."""
        model = ThreatLSTM(input_dim=32, hidden_dim=64)
        
        sequence = np.random.randn(20, 32)
        probability, importance = model.predict_threat(sequence)
        
        assert 0 <= probability <= 1
        assert importance.shape == (64,)


class TestTransformerPredictor:
    """Test Transformer threat prediction model."""
    
    def test_transformer_initialization(self):
        """Test Transformer initialization."""
        model = TransformerPredictor(
            input_dim=32,
            d_model=128,
            num_heads=8,
            num_layers=2
        )
        
        assert model.input_dim == 32
        assert model.d_model == 128
        assert model.num_heads == 8
    
    def test_transformer_forward_pass(self):
        """Test forward pass."""
        model = TransformerPredictor(input_dim=32, d_model=64, num_layers=2)
        
        sequence = np.random.randn(15, 32)
        output = model.forward(sequence)
        
        assert output.shape == (15, 64)
    
    def test_transformer_prediction(self):
        """Test threat sequence prediction."""
        model = TransformerPredictor(input_dim=32, d_model=64)
        
        sequence = np.random.randn(20, 32)
        probabilities, attention = model.predict_threat_sequence(sequence)
        
        assert len(probabilities) == 20
        assert all(0 <= p <= 1 for p in probabilities)


class TestAnomalyDetector:
    """Test advanced anomaly detector."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = AnomalyDetector(feature_dim=32)
        
        assert detector.feature_dim == 32
    
    def test_detector_training(self):
        """Test training anomaly detector."""
        detector = AnomalyDetector(feature_dim=32)
        
        # Generate normal data
        normal_data = np.random.randn(100, 32) * 0.5
        
        detector.fit(normal_data)
        
        assert detector.mean is not None
        assert detector.isolation_forest is not None
    
    def test_anomaly_detection(self):
        """Test detecting anomalies."""
        detector = AnomalyDetector(feature_dim=32)
        
        # Train on normal data
        normal_data = np.random.randn(100, 32) * 0.5
        detector.fit(normal_data, train_autoencoder=False)
        
        # Test normal sample
        normal_sample = np.random.randn(32) * 0.5
        is_normal, score_normal, _ = detector.detect(normal_sample)
        
        # Test anomalous sample
        anomaly_sample = np.random.randn(32) * 5.0  # Much larger variance
        is_anomaly, score_anomaly, _ = detector.detect(anomaly_sample)
        
        assert score_anomaly > score_normal


class TestCerberusEnhanced:
    """Test complete Cerberus Enhanced system."""
    
    @pytest.mark.asyncio
    async def test_cerberus_initialization(self):
        """Test Cerberus initialization."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        assert cerberus.threat_predictor is not None
        assert cerberus.zero_day_detector is not None
        assert cerberus.policy_generator is not None
    
    @pytest.mark.asyncio
    async def test_event_processing(self):
        """Test processing security events."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        event = create_sample_threat_event()
        results = await cerberus.process_event(event)
        
        assert 'event_id' in results
        assert 'final_severity' in results
        assert 'actions_taken' in results
    
    @pytest.mark.asyncio
    async def test_zero_day_handling(self):
        """Test zero-day threat handling."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        # Build baseline with normal events
        for i in range(50):
            normal_event = ThreatEvent(
                event_id=f"normal_{i}",
                timestamp=datetime.now(),
                event_type="routine_check",
                severity=ThreatSeverity.LOW
            )
            await cerberus.process_event(normal_event)
        
        # Process anomalous event
        zero_day = ThreatEvent(
            event_id="zero_day_001",
            timestamp=datetime.now(),
            event_type="unknown_attack",
            severity=ThreatSeverity.CRITICAL,
            indicators=[
                ThreatIndicator(
                    indicator_type="pattern",
                    value="never_seen_before",
                    severity=ThreatSeverity.CRITICAL,
                    confidence=0.9,
                    source="detector",
                    timestamp=datetime.now()
                )
            ]
        )
        
        results = await cerberus.process_event(zero_day)
        
        assert cerberus.metrics['zero_days_detected'] > 0
    
    @pytest.mark.asyncio
    async def test_security_status(self):
        """Test getting security status."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        status = cerberus.get_security_status()
        
        assert 'threat_level' in status
        assert 'active_threats' in status
        assert 'metrics' in status
    
    @pytest.mark.asyncio
    async def test_high_severity_octoreflex_integration(self):
        """Test OctoReflex coordination for high severity threats."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        critical_event = ThreatEvent(
            event_id="critical_001",
            timestamp=datetime.now(),
            event_type="active_breach",
            severity=ThreatSeverity.CRITICAL,
            source_ip="192.168.1.250"
        )
        
        results = await cerberus.process_event(critical_event)
        
        assert 'octoreflex_action' in results
        assert cerberus.metrics['octoreflex_actions'] > 0


class TestIntegrationScenarios:
    """Test complete integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_attack_progression_scenario(self):
        """Test detecting and responding to attack progression."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        # Simulate attack progression
        phases = [
            (AttackPhase.RECONNAISSANCE, ThreatSeverity.LOW),
            (AttackPhase.INITIAL_ACCESS, ThreatSeverity.MEDIUM),
            (AttackPhase.EXECUTION, ThreatSeverity.HIGH),
            (AttackPhase.PRIVILEGE_ESCALATION, ThreatSeverity.CRITICAL)
        ]
        
        for i, (phase, severity) in enumerate(phases):
            event = ThreatEvent(
                event_id=f"attack_phase_{i}",
                timestamp=datetime.now(),
                event_type=f"attack_{phase.value}",
                severity=severity,
                attack_phase=phase,
                source_ip="192.168.1.100",
                confidence=0.8 + (i * 0.05)  # Increasing confidence
            )
            
            results = await cerberus.process_event(event)
            
            # Higher phases should trigger more actions
            if severity.value >= ThreatSeverity.HIGH.value:
                assert 'octoreflex_action' in results
        
        # Should have generated predictions (threshold is now 5 events)
        assert cerberus.metrics['events_processed'] >= 4
    
    @pytest.mark.asyncio
    async def test_multi_indicator_threat(self):
        """Test threat with multiple indicators."""
        cerberus = CerberusEnhanced()
        await cerberus.initialize()
        
        indicators = [
            ThreatIndicator(
                indicator_type="ip",
                value="198.51.100.50",
                severity=ThreatSeverity.HIGH,
                confidence=0.9,
                source="threat_feed",
                timestamp=datetime.now(),
                mitre_techniques=["T1190"]
            ),
            ThreatIndicator(
                indicator_type="domain",
                value="c2-server.malicious",
                severity=ThreatSeverity.CRITICAL,
                confidence=0.95,
                source="threat_feed",
                timestamp=datetime.now(),
                mitre_techniques=["T1071"]
            ),
            ThreatIndicator(
                indicator_type="hash",
                value="deadbeef",
                severity=ThreatSeverity.HIGH,
                confidence=0.88,
                source="malware_analysis",
                timestamp=datetime.now(),
                mitre_techniques=["T1059"]
            )
        ]
        
        event = ThreatEvent(
            event_id="multi_indicator_001",
            timestamp=datetime.now(),
            event_type="advanced_threat",
            severity=ThreatSeverity.CRITICAL,
            indicators=indicators,
            mitre_techniques=["T1190", "T1071", "T1059"]
        )
        
        results = await cerberus.process_event(event)
        
        assert results['indicators_found'] == 3
        assert 'policy_generated' in results


def run_tests():
    """Run all tests and display results."""
    print("=" * 70)
    print("CERBERUS ENHANCED - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Run tests with pytest
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_"
    ]
    
    result = pytest.main(pytest_args)
    
    print("\n" + "=" * 70)
    if result == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
