#!/usr/bin/env python3
#                                           [2026-03-04 21:13]
#                                          Productivity: Active
"""
Liara Kernel Test Suite

Comprehensive unit and integration tests for the Liara failover controller.

Tests:
- Hot-swap activation/deactivation
- TTL enforcement and cryptographic proof
- Role-stacking prohibition
- Health monitoring integration
- Capability restrictions
- Pillar handoff protocol
- Edge cases and error handling
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from kernel.health import HealthMonitor, HealthStatus
from kernel.liara_kernel import LiaraCapability, LiaraKernel, TriumviratePillar


class TestLiaraKernelBasics(unittest.TestCase):
    """Test basic Liara kernel functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.liara = LiaraKernel(ttl_seconds=60)

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def test_initialization(self):
        """Test Liara kernel initialization."""
        self.assertIsNotNone(self.liara)
        self.assertIsNone(self.liara.active_role)
        self.assertEqual(self.liara.ttl_seconds, 60)
        self.assertFalse(self.liara.ttl_active)

    def test_activate_failover(self):
        """Test failover activation."""
        success = self.liara.activate_failover(
            TriumviratePillar.GALAHAD, reason="test"
        )

        self.assertTrue(success)
        self.assertIsNotNone(self.liara.active_role)
        self.assertEqual(self.liara.active_role.pillar, TriumviratePillar.GALAHAD)
        self.assertIsNotNone(self.liara.active_role.activation_proof)
        self.assertTrue(self.liara.ttl_active)

    def test_deactivate_failover(self):
        """Test failover deactivation."""
        self.liara.activate_failover(TriumviratePillar.CERBERUS, reason="test")
        success = self.liara.deactivate_failover(reason="test_complete")

        self.assertTrue(success)
        self.assertIsNone(self.liara.active_role)
        self.assertFalse(self.liara.ttl_active)

    def test_get_active_role(self):
        """Test getting active role."""
        # Initially no role
        role = self.liara.get_active_role()
        self.assertIsNone(role)

        # After activation
        self.liara.activate_failover(TriumviratePillar.CODEX_DEUS, reason="test")
        role = self.liara.get_active_role()
        self.assertEqual(role, TriumviratePillar.CODEX_DEUS)

    def test_get_status(self):
        """Test status reporting."""
        status = self.liara.get_status()

        self.assertIn("active", status)
        self.assertIn("active_role", status)
        self.assertIn("ttl_remaining", status)
        self.assertIn("pillar_health", status)
        self.assertIn("statistics", status)

        self.assertFalse(status["active"])
        self.assertIsNone(status["active_role"])


class TestRoleStackingPrevention(unittest.TestCase):
    """Test role-stacking prohibition."""

    def setUp(self):
        """Set up test fixtures."""
        self.liara = LiaraKernel(ttl_seconds=60)

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def test_prevent_role_stacking(self):
        """Test that role stacking is prevented."""
        # Activate for Galahad
        success1 = self.liara.activate_failover(
            TriumviratePillar.GALAHAD, reason="test1"
        )
        self.assertTrue(success1)

        # Try to activate for Cerberus (should fail)
        success2 = self.liara.activate_failover(
            TriumviratePillar.CERBERUS, reason="test2"
        )
        self.assertFalse(success2)

        # Verify still active as Galahad
        self.assertEqual(self.liara.get_active_role(), TriumviratePillar.GALAHAD)

        # Verify statistics
        self.assertEqual(self.liara.stats["role_stacking_prevented"], 1)

    def test_prevent_multiple_stacking_attempts(self):
        """Test multiple role stacking attempts are all prevented."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Try multiple times
        self.liara.activate_failover(TriumviratePillar.CERBERUS, reason="test")
        self.liara.activate_failover(TriumviratePillar.CODEX_DEUS, reason="test")

        self.assertEqual(self.liara.stats["role_stacking_prevented"], 2)

    def test_cannot_activate_none_pillar(self):
        """Test that NONE pillar cannot be activated."""
        success = self.liara.activate_failover(
            TriumviratePillar.NONE, reason="test"
        )
        self.assertFalse(success)
        self.assertIsNone(self.liara.active_role)


class TestTTLEnforcement(unittest.TestCase):
    """Test TTL enforcement and cryptographic proof."""

    def setUp(self):
        """Set up test fixtures."""
        self.liara = LiaraKernel(ttl_seconds=2)  # Short TTL for testing

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def test_get_remaining_ttl(self):
        """Test TTL remaining calculation."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Initially should be close to TTL
        remaining = self.liara.get_remaining_ttl()
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 1.0)
        self.assertLessEqual(remaining, 2.0)

        # After waiting
        time.sleep(1)
        remaining = self.liara.get_remaining_ttl()
        self.assertLess(remaining, 2.0)

    def test_ttl_automatic_shutdown(self):
        """Test automatic shutdown when TTL expires."""
        self.liara.activate_failover(TriumviratePillar.CERBERUS, reason="test")

        # Wait for TTL to expire
        time.sleep(3)

        # Should be automatically deactivated
        self.assertIsNone(self.liara.active_role)
        self.assertFalse(self.liara.ttl_active)

    def test_verify_ttl_proof(self):
        """Test cryptographic TTL proof verification."""
        self.liara.activate_failover(TriumviratePillar.CODEX_DEUS, reason="test")

        # Proof should be valid
        valid = self.liara.verify_ttl_proof()
        self.assertTrue(valid)

        # Proof should be non-empty
        self.assertIsNotNone(self.liara.active_role.activation_proof)
        self.assertGreater(len(self.liara.active_role.activation_proof), 0)

    def test_ttl_proof_after_expiry(self):
        """Test TTL proof verification fails after expiry."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Wait for expiry
        time.sleep(3)

        # Proof verification should fail (TTL exceeded)
        # Note: May be None if already auto-shutdown
        if self.liara.active_role:
            valid = self.liara.verify_ttl_proof()
            self.assertFalse(valid)


class TestHealthMonitoring(unittest.TestCase):
    """Test health monitoring integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.health_monitor = HealthMonitor()
        self.liara = LiaraKernel(
            health_monitor=self.health_monitor, ttl_seconds=60, failover_threshold=3
        )

        # Mock health check functions
        self.galahad_healthy = True
        self.cerberus_healthy = True
        self.codex_healthy = True

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()
        self.health_monitor.stop_monitoring()

    def galahad_check(self) -> bool:
        return self.galahad_healthy

    def cerberus_check(self) -> bool:
        return self.cerberus_healthy

    def codex_check(self) -> bool:
        return self.codex_healthy

    def test_register_pillar_health_check(self):
        """Test registering pillar health checks."""
        self.liara.register_pillar_health_check(
            TriumviratePillar.GALAHAD, self.galahad_check
        )

        # Check should be registered
        self.assertIn("triumvirate_galahad", self.health_monitor.health_checks)

    def test_check_pillar_health(self):
        """Test checking pillar health."""
        self.liara.register_pillar_health_check(
            TriumviratePillar.GALAHAD, self.galahad_check
        )

        # Healthy
        status = self.liara.check_pillar_health(TriumviratePillar.GALAHAD)
        self.assertEqual(status, HealthStatus.HEALTHY)

        # Make unhealthy and check multiple times to exceed threshold
        self.galahad_healthy = False
        for _ in range(4):  # Exceed threshold of 3
            status = self.liara.check_pillar_health(TriumviratePillar.GALAHAD)
        
        self.assertEqual(status, HealthStatus.UNHEALTHY)

    def test_auto_failover_on_degradation(self):
        """Test automatic failover when pillar degrades."""
        self.liara.register_pillar_health_check(
            TriumviratePillar.CERBERUS, self.cerberus_check
        )

        # First establish healthy baseline
        self.cerberus_healthy = True
        self.liara.check_pillar_health(TriumviratePillar.CERBERUS)
        
        # Make pillar unhealthy
        self.cerberus_healthy = False

        # Check multiple times to exceed threshold (3 failures triggers failover)
        for i in range(5):  # Use 5 to be sure we exceed threshold of 3
            status = self.liara.check_pillar_health(TriumviratePillar.CERBERUS)
            # Give a brief moment for processing
            time.sleep(0.05)

        # Should have triggered failover
        self.assertIsNotNone(self.liara.active_role)
        if self.liara.active_role:
            self.assertEqual(self.liara.active_role.pillar, TriumviratePillar.CERBERUS)


class TestCapabilities(unittest.TestCase):
    """Test capability restrictions."""

    def setUp(self):
        """Set up test fixtures."""
        self.liara = LiaraKernel(ttl_seconds=60)

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def test_capabilities_when_inactive(self):
        """Test capabilities when Liara is inactive."""
        # Only health monitoring available
        self.assertTrue(
            self.liara.has_capability(LiaraCapability.HEALTH_MONITORING)
        )
        self.assertFalse(
            self.liara.has_capability(LiaraCapability.BASIC_REASONING)
        )
        self.assertFalse(self.liara.has_capability(LiaraCapability.POLICY_CHECK))
        self.assertFalse(
            self.liara.has_capability(LiaraCapability.SIMPLE_INFERENCE)
        )

    def test_capabilities_as_galahad(self):
        """Test capabilities when active as Galahad."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Should have reasoning capability
        self.assertTrue(
            self.liara.has_capability(LiaraCapability.BASIC_REASONING)
        )
        self.assertTrue(
            self.liara.has_capability(LiaraCapability.HEALTH_MONITORING)
        )
        self.assertTrue(
            self.liara.has_capability(LiaraCapability.EMERGENCY_SHUTDOWN)
        )

        # Should NOT have other capabilities
        self.assertFalse(self.liara.has_capability(LiaraCapability.POLICY_CHECK))
        self.assertFalse(
            self.liara.has_capability(LiaraCapability.SIMPLE_INFERENCE)
        )

    def test_capabilities_as_cerberus(self):
        """Test capabilities when active as Cerberus."""
        self.liara.activate_failover(TriumviratePillar.CERBERUS, reason="test")

        # Should have policy capability
        self.assertTrue(self.liara.has_capability(LiaraCapability.POLICY_CHECK))
        self.assertTrue(
            self.liara.has_capability(LiaraCapability.HEALTH_MONITORING)
        )
        self.assertTrue(
            self.liara.has_capability(LiaraCapability.EMERGENCY_SHUTDOWN)
        )

        # Should NOT have other capabilities
        self.assertFalse(
            self.liara.has_capability(LiaraCapability.BASIC_REASONING)
        )
        self.assertFalse(
            self.liara.has_capability(LiaraCapability.SIMPLE_INFERENCE)
        )

    def test_execute_operation_without_capability(self):
        """Test executing operation without required capability."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Try to execute policy check (not available for Galahad)
        result = self.liara.execute_limited_operation(
            LiaraCapability.POLICY_CHECK, {}
        )

        self.assertFalse(result["success"])
        self.assertIn("not available", result["error"])

    def test_execute_operation_with_capability(self):
        """Test executing operation with required capability."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Execute basic reasoning (available for Galahad)
        result = self.liara.execute_limited_operation(
            LiaraCapability.BASIC_REASONING, {}
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["capability"], "basic_reasoning")


class TestHandoffProtocol(unittest.TestCase):
    """Test pillar handoff protocol."""

    def setUp(self):
        """Set up test fixtures."""
        self.health_monitor = HealthMonitor()
        self.liara = LiaraKernel(health_monitor=self.health_monitor, ttl_seconds=60)

        # Mock health checks
        self.galahad_healthy = True

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def galahad_check(self) -> bool:
        return self.galahad_healthy

    def test_handoff_to_healthy_pillar(self):
        """Test handoff to recovered pillar."""
        self.liara.register_pillar_health_check(
            TriumviratePillar.GALAHAD, self.galahad_check
        )

        # Activate failover
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Mark pillar as healthy
        self.galahad_healthy = True
        self.liara.check_pillar_health(TriumviratePillar.GALAHAD)

        # Perform handoff
        success = self.liara.handoff_to_pillar(TriumviratePillar.GALAHAD)

        self.assertTrue(success)
        self.assertIsNone(self.liara.active_role)
        self.assertEqual(self.liara.stats["total_handoffs"], 1)

    def test_handoff_to_unhealthy_pillar_fails(self):
        """Test handoff fails for unhealthy pillar."""
        self.liara.register_pillar_health_check(
            TriumviratePillar.GALAHAD, self.galahad_check
        )

        # Activate failover
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Mark pillar as unhealthy
        self.galahad_healthy = False
        self.liara.check_pillar_health(TriumviratePillar.GALAHAD)

        # Try handoff
        success = self.liara.handoff_to_pillar(TriumviratePillar.GALAHAD)

        self.assertFalse(success)
        self.assertIsNotNone(self.liara.active_role)

    def test_handoff_wrong_pillar_fails(self):
        """Test handoff fails for wrong pillar."""
        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        # Try to hand off to different pillar
        success = self.liara.handoff_to_pillar(TriumviratePillar.CERBERUS)

        self.assertFalse(success)
        self.assertIsNotNone(self.liara.active_role)


class TestCallbacks(unittest.TestCase):
    """Test callback functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.liara = LiaraKernel(ttl_seconds=60)
        self.activation_called = False
        self.shutdown_called = False

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def activation_callback(self, pillar, reason):
        """Activation callback."""
        self.activation_called = True
        self.activation_pillar = pillar
        self.activation_reason = reason

    def shutdown_callback(self, pillar, reason, duration):
        """Shutdown callback."""
        self.shutdown_called = True
        self.shutdown_pillar = pillar
        self.shutdown_reason = reason
        self.shutdown_duration = duration

    def test_activation_callback(self):
        """Test activation callback is called."""
        self.liara.register_activation_callback(self.activation_callback)

        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        self.assertTrue(self.activation_called)
        self.assertEqual(self.activation_pillar, TriumviratePillar.GALAHAD)
        self.assertEqual(self.activation_reason, "test")

    def test_shutdown_callback(self):
        """Test shutdown callback is called."""
        self.liara.register_shutdown_callback(self.shutdown_callback)

        self.liara.activate_failover(TriumviratePillar.CERBERUS, reason="test")
        time.sleep(0.1)  # Brief delay
        self.liara.deactivate_failover(reason="test_complete")

        self.assertTrue(self.shutdown_called)
        self.assertEqual(self.shutdown_pillar, TriumviratePillar.CERBERUS)
        self.assertEqual(self.shutdown_reason, "test_complete")
        self.assertGreater(self.shutdown_duration, 0)


class TestStatistics(unittest.TestCase):
    """Test statistics tracking."""

    def setUp(self):
        """Set up test fixtures."""
        self.liara = LiaraKernel(ttl_seconds=60)

    def tearDown(self):
        """Clean up after tests."""
        if self.liara.active_role:
            self.liara.deactivate_failover()

    def test_activation_statistics(self):
        """Test activation statistics are tracked."""
        initial = self.liara.stats["total_activations"]

        self.liara.activate_failover(TriumviratePillar.GALAHAD, reason="test")

        self.assertEqual(self.liara.stats["total_activations"], initial + 1)

    def test_shutdown_statistics(self):
        """Test shutdown statistics are tracked."""
        initial = self.liara.stats["total_shutdowns"]

        self.liara.activate_failover(TriumviratePillar.CERBERUS, reason="test")
        self.liara.deactivate_failover()

        self.assertEqual(self.liara.stats["total_shutdowns"], initial + 1)


def run_tests():
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLiaraKernelBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestRoleStackingPrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestTTLEnforcement))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMonitoring))
    suite.addTests(loader.loadTestsFromTestCase(TestCapabilities))
    suite.addTests(loader.loadTestsFromTestCase(TestHandoffProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestCallbacks))
    suite.addTests(loader.loadTestsFromTestCase(TestStatistics))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
