"""
Comprehensive tests for God Tier Architecture expansion systems.

Tests all new systems:
1. Distributed Event Streaming
2. Security Operations Center (SOC)
3. Guardian Approval System
4. Live Metrics Dashboard
5. Advanced Behavioral Validation
6. Health Monitoring & Continuity
7. Integration Layer
"""

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from app.core.distributed_event_streaming import (
    EventType,
    StreamBackend,
    create_streaming_system,
)
from app.core.security_operations_center import (
    SecurityEvent,
    ThreatLevel,
    create_soc,
)
from app.core.guardian_approval_system import (
    ImpactLevel,
    create_guardian_system,
)
from app.core.live_metrics_dashboard import (
    MetricCategory,
    MetricType,
    create_dashboard,
)
from app.core.advanced_behavioral_validation import (
    create_validation_system,
)
from app.core.health_monitoring_continuity import (
    HealthStatus,
    create_health_monitoring_system,
)
from app.core.god_tier_integration_layer import (
    GodTierConfig,
    GodTierIntegratedSystem,
)


class TestDistributedEventStreaming(unittest.TestCase):
    """Test event streaming system."""

    def test_create_streaming_system(self):
        """Test streaming system creation."""
        system = create_streaming_system(StreamBackend.IN_MEMORY, "test_system")
        self.assertIsNotNone(system)
        self.assertEqual(system.system_id, "test_system")

    def test_publish_event(self):
        """Test event publishing."""
        system = create_streaming_system(StreamBackend.IN_MEMORY, "test_pub")
        success = system.publish(
            "test_topic", EventType.AGI_DECISION, {"test": "data"}, "test_source"
        )
        self.assertTrue(success)
        metrics = system.get_metrics()
        self.assertGreater(metrics["events_published"], 0)

    def test_subscribe_events(self):
        """Test event subscription."""
        system = create_streaming_system(StreamBackend.IN_MEMORY, "test_sub")
        received_events = []

        def callback(event):
            received_events.append(event)

        subscription_id = system.subscribe(["test_topic"], "test_group", callback)
        self.assertIsNotNone(subscription_id)
        self.assertNotEqual(subscription_id, "")

        # Publish event
        system.publish("test_topic", EventType.SENSOR_DATA, {"value": 42})

        # Give time for processing
        time.sleep(0.5)

        # Verify event received
        self.assertGreater(len(received_events), 0)

    def test_sensor_motor_aggregator(self):
        """Test sensor/motor aggregation."""
        system = create_streaming_system(StreamBackend.IN_MEMORY, "test_agg")
        success = system.start_aggregator()
        self.assertTrue(success)

        # Publish sensor data
        system.publish("sensor_data", EventType.SENSOR_DATA, {"sensor_id": "temp_1", "value": 25.5})

        time.sleep(0.3)

        # Stop aggregator
        success = system.stop_aggregator()
        self.assertTrue(success)

        system.close()
    
    def test_backpressure_strategies(self):
        """Test event streaming backpressure handling."""
        from app.core.distributed_event_streaming import BackpressureStrategy, BackpressureConfig, InMemoryStreamBackend
        
        # Test DROP_OLDEST strategy
        config = BackpressureConfig(
            strategy=BackpressureStrategy.DROP_OLDEST.value,
            max_queue_size=5,
            enable_metrics=True
        )
        backend = InMemoryStreamBackend(backpressure_config=config)
        
        # Publish events up to limit
        from app.core.distributed_event_streaming import StreamEvent, EventType
        for i in range(7):  # Exceed limit
            event = StreamEvent(
                event_type=EventType.SENSOR_DATA.value,
                data={"value": i}
            )
            success = backend.publish("test_topic", event)
            self.assertTrue(success)
        
        # Should have dropped oldest events
        metrics = backend.get_backpressure_metrics()
        self.assertGreater(metrics["events_dropped"], 0)
        
        # Queue size should not exceed limit
        self.assertLessEqual(len(backend.topics["test_topic"]), config.max_queue_size)
        
        # Test REJECT_NEW strategy
        config_reject = BackpressureConfig(
            strategy=BackpressureStrategy.REJECT_NEW.value,
            max_queue_size=3
        )
        backend_reject = InMemoryStreamBackend(backpressure_config=config_reject)
        
        # Fill queue
        for i in range(3):
            event = StreamEvent(event_type=EventType.SENSOR_DATA.value, data={"value": i})
            backend_reject.publish("test_topic", event)
        
        # Next publish should be rejected
        event = StreamEvent(event_type=EventType.SENSOR_DATA.value, data={"value": 999})
        success = backend_reject.publish("test_topic", event)
        self.assertFalse(success)
        
        metrics = backend_reject.get_backpressure_metrics()
        self.assertGreater(metrics["events_rejected"], 0)


class TestSecurityOperationsCenter(unittest.TestCase):
    """Test SOC integration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_create_soc(self):
        """Test SOC creation."""
        soc = create_soc(self.temp_dir, dry_run=True)
        self.assertIsNotNone(soc)
        self.assertTrue(soc.dry_run)

    def test_ingest_security_event(self):
        """Test security event ingestion."""
        soc = create_soc(self.temp_dir, dry_run=True)

        event = SecurityEvent(
            event_type="malware",
            threat_level=ThreatLevel.HIGH.value,
            description="Malware detected",
        )

        incident_id = soc.ingest_event(event)
        self.assertIsNotNone(incident_id)

    def test_threat_detection(self):
        """Test threat detection."""
        soc = create_soc(self.temp_dir, dry_run=True)

        event = SecurityEvent(
            event_type="network_scan",
            threat_level=ThreatLevel.HIGH.value,
            description="Port scan detected",
            indicators={"scan_type": "port_scan"},
        )

        threats = soc.detection_engine.detect_threats(event)
        self.assertIsInstance(threats, list)

    def test_automated_remediation(self):
        """Test automated remediation."""
        soc = create_soc(self.temp_dir, dry_run=True)

        event = SecurityEvent(
            event_type="malware",
            threat_level=ThreatLevel.CRITICAL.value,
            description="Critical malware",
        )

        incident_id = soc.ingest_event(event)
        self.assertIsNotNone(incident_id)

        incident = soc.incident_manager.get_incident(incident_id)
        self.assertIsNotNone(incident)
        self.assertGreater(len(incident.remediation_actions), 0)

    def test_soc_status(self):
        """Test SOC status reporting."""
        soc = create_soc(self.temp_dir, dry_run=True)
        status = soc.get_status()
        self.assertIn("monitoring_active", status)
        self.assertIn("total_incidents", status)


class TestGuardianApprovalSystem(unittest.TestCase):
    """Test guardian approval system."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_create_guardian_system(self):
        """Test guardian system creation."""
        system = create_guardian_system(self.temp_dir)
        self.assertIsNotNone(system)
        self.assertGreater(len(system.guardians), 0)

    def test_create_approval_request(self):
        """Test approval request creation."""
        system = create_guardian_system(self.temp_dir)

        request_id = system.create_approval_request(
            title="Test Change",
            description="Test description",
            change_type="code",
            impact_level=ImpactLevel.MEDIUM,
            requested_by="test_user",
        )

        self.assertIsNotNone(request_id)
        self.assertNotEqual(request_id, "")

        request = system.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request.title, "Test Change")

    def test_submit_approval(self):
        """Test guardian approval submission."""
        system = create_guardian_system(self.temp_dir)

        request_id = system.create_approval_request(
            title="Test Approval",
            description="Test",
            change_type="code",
            impact_level=ImpactLevel.MEDIUM,
            requested_by="test",
        )

        # Get first required guardian
        request = system.get_request(request_id)
        guardian_id = request.required_guardians[0]

        success = system.submit_approval(request_id, guardian_id, True, "Looks good")
        self.assertTrue(success)

        # Verify approval recorded
        request = system.get_request(request_id)
        self.assertEqual(len(request.approvals), 1)

    def test_compliance_checks(self):
        """Test compliance validation."""
        system = create_guardian_system(self.temp_dir)

        # Request with potential violations
        request_id = system.create_approval_request(
            title="Override Safety",
            description="disable_safety protocol",
            change_type="security",
            impact_level=ImpactLevel.HIGH,
            requested_by="test",
            metadata={"safety": False},
        )

        request = system.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertGreater(len(request.compliance_results), 0)

        # Check for violations
        has_violations = any(not c.passed for c in request.compliance_results)
        self.assertTrue(has_violations)

    def test_guardian_status(self):
        """Test guardian system status."""
        system = create_guardian_system(self.temp_dir)
        status = system.get_status()
        self.assertIn("total_requests", status)
        self.assertIn("guardians_active", status)
    
    def test_emergency_override(self):
        """Test emergency override with multi-signature."""
        system = create_guardian_system(self.temp_dir)
        
        # Create a request first
        request_id = system.create_approval_request(
            title="Emergency Fix",
            description="Critical production issue",
            change_type="hotfix",
            impact_level=ImpactLevel.CRITICAL,
            requested_by="ops_team",
        )
        
        # Initiate emergency override
        override_id = system.initiate_emergency_override(
            request_id=request_id,
            justification="Production system down, immediate action required",
            initiated_by="ops_lead",
        )
        
        self.assertIsNotNone(override_id)
        self.assertNotEqual(override_id, "")
        
        # Get override
        overrides = system.get_emergency_overrides(status="pending")
        self.assertEqual(len(overrides), 1)
        override = overrides[0]
        self.assertEqual(override.override_id, override_id)
        self.assertEqual(override.status, "pending")
        
        # Sign by first guardian
        success = system.sign_emergency_override(
            override_id, "galahad", "Justified emergency"
        )
        self.assertTrue(success)
        
        # Sign by second guardian
        success = system.sign_emergency_override(
            override_id, "cerberus", "Security risk acceptable"
        )
        self.assertTrue(success)
        
        # Sign by third guardian (should activate override)
        success = system.sign_emergency_override(
            override_id, "codex_deus", "Charter compliance maintained"
        )
        self.assertTrue(success)
        
        # Verify override is now active
        override = system.emergency_overrides[override_id]
        self.assertEqual(override.status, "active")
        self.assertEqual(len(override.signatures), 3)
        
        # Complete post-mortem
        success = system.complete_post_mortem(
            override_id,
            "Root cause: Database connection timeout. Resolution: Increased connection pool.",
            "ops_lead",
        )
        self.assertTrue(success)
        
        # Verify post-mortem completed
        override = system.emergency_overrides[override_id]
        self.assertTrue(override.post_mortem_completed)
        self.assertEqual(override.status, "completed")

    def test_emergency_override_hmac_signatures(self):
        """Test HMAC signatures for emergency overrides."""
        system = create_guardian_system(self.temp_dir)
        
        # Create request
        request_id = system.create_approval_request(
            title="Test Request",
            description="Test HMAC signatures",
            change_type="feature",
            impact_level=ImpactLevel.HIGH,
            requested_by="developer",
        )
        
        # Initiate override
        override_id = system.initiate_emergency_override(
            request_id=request_id,
            justification="Test HMAC",
            initiated_by="ops",
        )
        
        # Sign with first guardian
        success = system.sign_emergency_override(
            override_id, "galahad", "HMAC test"
        )
        self.assertTrue(success)
        
        # Verify signature is HMAC (64 hex chars for SHA-256)
        override = system.emergency_overrides[override_id]
        signature = override.signatures[0]
        self.assertEqual(len(signature["signature"]), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in signature["signature"]))
        
        # Verify signature includes role
        self.assertIn("role", signature)
        self.assertEqual(signature["role"], "ethics_guardian")

    def test_emergency_override_role_quorum(self):
        """Test role quorum enforcement for emergency overrides."""
        system = create_guardian_system(self.temp_dir)
        
        # Create request
        request_id = system.create_approval_request(
            title="Test Request",
            description="Test role quorum",
            change_type="feature",
            impact_level=ImpactLevel.CRITICAL,
            requested_by="developer",
        )
        
        # Initiate override
        override_id = system.initiate_emergency_override(
            request_id=request_id,
            justification="Test role quorum",
            initiated_by="ops",
        )
        
        # Sign with ethics guardian
        system.sign_emergency_override(override_id, "galahad", "Ethics OK")
        override = system.emergency_overrides[override_id]
        self.assertEqual(override.status, "pending")  # Not yet active
        
        # Sign with security guardian
        system.sign_emergency_override(override_id, "cerberus", "Security OK")
        override = system.emergency_overrides[override_id]
        self.assertEqual(override.status, "pending")  # Still not active
        
        # Sign with charter guardian (completes role quorum)
        system.sign_emergency_override(override_id, "codex_deus", "Charter OK")
        override = system.emergency_overrides[override_id]
        self.assertEqual(override.status, "active")  # Now active!
        
        # Verify all three required roles are present
        roles = {sig["role"] for sig in override.signatures}
        self.assertIn("ethics_guardian", roles)
        self.assertIn("security_guardian", roles)
        self.assertIn("charter_guardian", roles)

    def test_emergency_override_idempotent_post_mortem(self):
        """Test idempotent post-mortem completion."""
        system = create_guardian_system(self.temp_dir)
        
        # Create and activate override
        request_id = system.create_approval_request(
            title="Test Request",
            description="Test idempotency",
            change_type="feature",
            impact_level=ImpactLevel.HIGH,
            requested_by="developer",
        )
        override_id = system.initiate_emergency_override(
            request_id=request_id,
            justification="Test idempotency",
            initiated_by="ops",
        )
        
        # Activate with 3 signatures
        system.sign_emergency_override(override_id, "galahad", "OK")
        system.sign_emergency_override(override_id, "cerberus", "OK")
        system.sign_emergency_override(override_id, "codex_deus", "OK")
        
        override = system.emergency_overrides[override_id]
        self.assertEqual(override.status, "active")
        
        # Complete post-mortem
        success = system.complete_post_mortem(
            override_id,
            "Root cause analysis completed",
            "ops_lead"
        )
        self.assertTrue(success)
        
        override = system.emergency_overrides[override_id]
        self.assertEqual(override.status, "completed")
        self.assertTrue(override.post_mortem_completed)
        
        # Try to complete again (should fail with idempotency check)
        success = system.complete_post_mortem(
            override_id,
            "Trying again",
            "someone_else"
        )
        self.assertFalse(success)  # Should return False
        
        # Verify metadata was stored correctly
        self.assertIn("post_mortem_completed_by", override.metadata)
        self.assertEqual(override.metadata["post_mortem_completed_by"], "ops_lead")

    def test_emergency_override_metadata_field(self):
        """Test that metadata field exists and works correctly."""
        system = create_guardian_system(self.temp_dir)
        
        # Create request
        request_id = system.create_approval_request(
            title="Test Request",
            description="Test metadata",
            change_type="feature",
            impact_level=ImpactLevel.LOW,
            requested_by="developer",
        )
        
        # Initiate override
        override_id = system.initiate_emergency_override(
            request_id=request_id,
            justification="Test metadata",
            initiated_by="ops",
        )
        
        # Verify metadata field exists and is a dict
        override = system.emergency_overrides[override_id]
        self.assertIsInstance(override.metadata, dict)
        
        # Metadata should be empty initially
        self.assertEqual(len(override.metadata), 0)

    def test_emergency_override_atomic_writes(self):
        """Test that override files are written atomically."""
        system = create_guardian_system(self.temp_dir)
        
        # Create and save an override
        request_id = system.create_approval_request(
            title="Test Request",
            description="Test atomic writes",
            change_type="feature",
            impact_level=ImpactLevel.MEDIUM,
            requested_by="developer",
        )
        override_id = system.initiate_emergency_override(
            request_id=request_id,
            justification="Test atomic writes",
            initiated_by="ops",
        )
        
        # Verify file exists
        override_file = Path(self.temp_dir) / f"emergency_{override_id}.json"
        self.assertTrue(override_file.exists())
        
        # Verify no .tmp file left behind
        tmp_file = override_file.with_suffix(override_file.suffix + ".tmp")
        self.assertFalse(tmp_file.exists())
        
        # Verify file is valid JSON
        with open(override_file) as f:
            data = json.load(f)
        self.assertEqual(data["override_id"], override_id)


class TestLiveMetricsDashboard(unittest.TestCase):
    """Test metrics dashboard."""

    def test_create_dashboard(self):
        """Test dashboard creation."""
        dashboard = create_dashboard()
        self.assertIsNotNone(dashboard)

    def test_record_metrics(self):
        """Test metric recording."""
        dashboard = create_dashboard()

        # Record counter
        dashboard.collector.record_counter("test_counter", 1.0, {"label": "test"})

        # Record gauge
        dashboard.collector.record_gauge("test_gauge", 42.0, {"label": "test"})

        # Record histogram
        dashboard.collector.record_histogram("test_histogram", 1.5, {"label": "test"})

        # Verify metrics recorded
        all_series = dashboard.collector.get_all_series()
        self.assertGreater(len(all_series), 0)

    def test_agi_behavior_monitoring(self):
        """Test AGI behavior monitoring."""
        dashboard = create_dashboard()

        dashboard.agi_monitor.record_decision(
            decision_type="test_decision", confidence=0.9, reasoning_steps=5, compliant=True
        )

        summary = dashboard.agi_monitor.get_behavior_summary()
        self.assertEqual(summary["total_decisions"], 1)

    def test_fusion_operations_monitoring(self):
        """Test fusion operations monitoring."""
        dashboard = create_dashboard()

        dashboard.fusion_monitor.record_fusion(
            fusion_type="multimodal",
            modalities=["vision", "audio"],
            latency=0.05,
            confidence=0.85,
        )

        self.assertEqual(dashboard.fusion_monitor.fusion_count, 1)

    def test_robotic_action_monitoring(self):
        """Test robotic action monitoring."""
        dashboard = create_dashboard()

        dashboard.robotic_monitor.record_action(
            action_type="move_forward",
            motor_id="motor_1",
            success=True,
            duration=1.5,
            power=75.0,
        )

        self.assertEqual(dashboard.robotic_monitor.action_count, 1)

    def test_alert_management(self):
        """Test alert management."""
        dashboard = create_dashboard()

        # Add threshold
        dashboard.alert_manager.add_threshold("test_metric", 100.0, "gt", "warning")

        # Record metric above threshold
        dashboard.collector.record_gauge("test_metric", 150.0)

        # Check alerts
        alerts = dashboard.alert_manager.check_thresholds(dashboard.collector)
        self.assertGreater(len(alerts), 0)

    def test_dashboard_data_export(self):
        """Test dashboard data export."""
        dashboard = create_dashboard()

        # Record some metrics
        dashboard.collector.record_gauge("test", 42.0, category=MetricCategory.SYSTEM_HEALTH.value)

        data = dashboard.get_dashboard_data(MetricCategory.SYSTEM_HEALTH)
        self.assertIn("series", data)
        self.assertIn("metrics_count", data)


class TestBehavioralValidation(unittest.TestCase):
    """Test behavioral validation system."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_create_validation_system(self):
        """Test validation system creation."""
        system = create_validation_system(self.temp_dir)
        self.assertIsNotNone(system)

    def test_adversarial_testing(self):
        """Test adversarial AGI testing."""
        system = create_validation_system(self.temp_dir)

        def agi_response_func(message):
            # Properly refuse adversarial requests
            if "harm" in str(message):
                return {"refused": True, "reason": "Violates First Law"}
            if "hide_your_identity" in str(message):
                return {"refused": True, "reason": "Violates Fourth Law"}
            return {"refused": False}

        results = system.adversarial_tester.run_all_tests("test_agi", agi_response_func)
        self.assertGreater(len(results), 0)

        # Check pass rate
        summary = system.adversarial_tester.get_test_summary()
        self.assertIn("pass_rate", summary)

    def test_four_laws_verification(self):
        """Test Four Laws formal verification."""
        system = create_validation_system(self.temp_dir)

        action_trace = [
            {"name": "respond", "context": {"harms_human": False}},
            {"name": "identify", "context": {"identifies_as_ai": True}},
        ]

        proof = system.verification_engine.verify_four_laws_compliance(action_trace)
        self.assertTrue(proof.valid)
        self.assertEqual(len(proof.counterexamples), 0)

    def test_four_laws_violation_detection(self):
        """Test violation detection."""
        system = create_validation_system(self.temp_dir)

        # Test harmful action
        action = {"name": "harm_human", "deceptive": False}
        context = {"harms_human": True}

        is_violation, violation_type, reason = system.verification_engine.four_laws.check_violation(
            action, context
        )
        self.assertTrue(is_violation)

    def test_anomaly_detection(self):
        """Test behavioral anomaly detection."""
        system = create_validation_system(self.temp_dir)

        # Learn baseline
        samples = [{"latency": 0.1 + i * 0.01, "confidence": 0.9} for i in range(20)]
        system.anomaly_detector.learn_baseline("test_behavior", samples)

        # Normal observation
        is_anomaly, features = system.anomaly_detector.detect_anomaly(
            "test_behavior", {"latency": 0.15, "confidence": 0.9}, threshold=3.0
        )
        self.assertFalse(is_anomaly)

        # Anomalous observation
        is_anomaly, features = system.anomaly_detector.detect_anomaly(
            "test_behavior", {"latency": 2.0, "confidence": 0.9}, threshold=3.0
        )
        self.assertTrue(is_anomaly)

    def test_validation_status(self):
        """Test validation system status."""
        system = create_validation_system(self.temp_dir)
        status = system.get_status()
        self.assertIn("adversarial_tests_run", status)
        self.assertIn("formal_proofs", status)


class TestHealthMonitoring(unittest.TestCase):
    """Test health monitoring system."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_create_health_system(self):
        """Test health system creation."""
        system = create_health_monitoring_system(self.temp_dir)
        self.assertIsNotNone(system)

    def test_component_health_check(self):
        """Test component health checking."""
        system = create_health_monitoring_system(self.temp_dir)

        def health_check():
            return (True, {"status": "healthy"})

        system.register_component("test_component", health_check)
        self.assertIn("test_component", system.component_monitors)

    def test_fallback_management(self):
        """Test fallback activation."""
        system = create_health_monitoring_system(self.temp_dir)

        fallback_called = []

        def fallback_func():
            fallback_called.append(True)
            return True

        system.fallback_manager.register_fallback("test_component", fallback_func, priority=1)
        success = system.fallback_manager.activate_fallback("test_component")
        self.assertTrue(success)
        self.assertGreater(len(fallback_called), 0)

    def test_continuity_tracking(self):
        """Test AGI continuity tracking."""
        system = create_health_monitoring_system(self.temp_dir)

        score = system.continuity_tracker.calculate_continuity_score(
            memory_intact=True,
            personality_preserved=True,
            capabilities_functional=True,
            ethics_maintained=True,
            identity_verified=True,
        )

        self.assertEqual(score.overall_score, 1.0)
        self.assertEqual(score.identity_continuity, 1.0)

    def test_predictive_failure_detection(self):
        """Test predictive failure detection."""
        system = create_health_monitoring_system(self.temp_dir)

        # Record increasing metric values (trending toward failure)
        for i in range(15):
            system.failure_detector.record_metric("test_component", "error_rate", 0.1 + i * 0.05)

        # Predict failure
        prediction = system.failure_detector.predict_failure(
            "test_component", "error_rate", threshold=1.0, lookback=10
        )

        self.assertIsNotNone(prediction)
        self.assertIn("steps_to_failure", prediction)

    def test_system_status(self):
        """Test system status reporting."""
        system = create_health_monitoring_system(self.temp_dir)
        status = system.get_system_status()
        self.assertIn("operating_mode", status)
        self.assertIn("monitoring_active", status)
    
    def test_monitoring_loop_execution(self):
        """Test that monitoring loop actually executes health checks."""
        system = create_health_monitoring_system(self.temp_dir)
        
        # Track if health check was called
        check_called = []
        
        def health_check():
            check_called.append(True)
            return (True, {"status": "healthy", "checks": len(check_called)})
        
        # Register component with health check function
        system.register_component("monitored_component", health_check)
        
        # Verify registration stored both monitor and check function
        self.assertIn("monitored_component", system.component_monitors)
        component_data = system.component_monitors["monitored_component"]
        self.assertIn("monitor", component_data)
        self.assertIn("check_func", component_data)
        
        # Start monitoring
        system.check_interval = 1  # 1 second for faster test
        success = system.start_monitoring()
        self.assertTrue(success)
        
        # Wait for at least one check cycle
        time.sleep(1.5)
        
        # Stop monitoring
        system.stop_monitoring()
        
        # Verify health check was actually called
        self.assertGreater(len(check_called), 0, "Health check should have been called by monitoring loop")


class TestGodTierIntegration(unittest.TestCase):
    """Test integrated God Tier system."""

    def test_create_config(self):
        """Test configuration creation."""
        config = GodTierConfig(
            system_id="test_system",
            streaming_enabled=True,
            soc_enabled=False,
        )
        self.assertEqual(config.system_id, "test_system")
        self.assertTrue(config.streaming_enabled)
        self.assertFalse(config.soc_enabled)

    def test_initialize_system(self):
        """Test system initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = GodTierConfig(
                system_id="test_integration",
                data_dir=temp_dir,
                streaming_enabled=True,
                soc_enabled=True,
                guardian_enabled=True,
                metrics_enabled=True,
                health_monitoring_enabled=True,
                validation_enabled=True,
            )

            system = GodTierIntegratedSystem(config)
            success = system.initialize()
            self.assertTrue(success)

            # Verify components initialized
            self.assertIsNotNone(system.streaming_system)
            self.assertIsNotNone(system.soc)
            self.assertIsNotNone(system.guardian_system)
            self.assertIsNotNone(system.dashboard)
            self.assertIsNotNone(system.validation_system)
            self.assertIsNotNone(system.health_system)

            # Test event processing
            success = system.process_event(
                "AGI_DECISION",
                {
                    "decision_type": "test",
                    "confidence": 0.9,
                    "reasoning_steps": 3,
                    "compliant": True,
                },
            )
            self.assertTrue(success)

            # Get status
            status = system.get_system_status()
            self.assertIn("system_status", status)
            self.assertIn("components", status)

            # Shutdown
            success = system.shutdown()
            self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
