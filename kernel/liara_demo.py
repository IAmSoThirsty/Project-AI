#!/usr/bin/env python3
#                                           [2026-03-04 21:13]
#                                          Productivity: Active
"""
Liara Kernel Demonstration and Integration Test

Demonstrates:
1. Hot-swap failover activation
2. TTL enforcement with cryptographic proof
3. Role-stacking prohibition
4. Health monitoring and degradation detection
5. Limited capability execution
6. Graceful handoff to recovered pillars
"""

import logging
import time
from typing import Dict

from kernel.health import HealthMonitor, HealthStatus
from kernel.liara_kernel import LiaraCapability, LiaraKernel, TriumviratePillar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class TriumvirateSimulator:
    """
    Simulates Triumvirate pillars for testing Liara failover.

    Allows controlled degradation and recovery of pillars.
    """

    def __init__(self):
        self.pillars = {
            TriumviratePillar.GALAHAD: {"healthy": True, "uptime": 0.0},
            TriumviratePillar.CERBERUS: {"healthy": True, "uptime": 0.0},
            TriumviratePillar.CODEX_DEUS: {"healthy": True, "uptime": 0.0},
        }

    def set_pillar_health(self, pillar: TriumviratePillar, healthy: bool):
        """Set health status of a pillar."""
        if pillar != TriumviratePillar.NONE:
            self.pillars[pillar]["healthy"] = healthy
            logger.info("Set %s health: %s", pillar.value, "HEALTHY" if healthy else "DEGRADED")

    def check_galahad(self) -> bool:
        """Health check for Galahad."""
        return self.pillars[TriumviratePillar.GALAHAD]["healthy"]

    def check_cerberus(self) -> bool:
        """Health check for Cerberus."""
        return self.pillars[TriumviratePillar.CERBERUS]["healthy"]

    def check_codex_deus(self) -> bool:
        """Health check for Codex Deus."""
        return self.pillars[TriumviratePillar.CODEX_DEUS]["healthy"]


def demo_basic_failover():
    """Demonstrate basic failover activation and deactivation."""
    logger.info("=" * 80)
    logger.info("DEMO 1: Basic Failover Activation")
    logger.info("=" * 80)

    # Create Liara kernel with short TTL for demo
    liara = LiaraKernel(ttl_seconds=30)

    # Activate failover for Galahad
    logger.info("Activating failover for Galahad...")
    success = liara.activate_failover(TriumviratePillar.GALAHAD, reason="demo_test")

    if success:
        logger.info("✅ Failover activated successfully")

        # Check status
        status = liara.get_status()
        logger.info("Active role: %s", status["active_role"])
        logger.info("TTL remaining: %.1fs", status["ttl_remaining"])
        logger.info("TTL proof valid: %s", status["ttl_proof_valid"])

        # Wait a bit
        time.sleep(2)

        # Check remaining TTL
        remaining = liara.get_remaining_ttl()
        logger.info("TTL remaining after 2s: %.1fs", remaining)

        # Deactivate
        logger.info("Deactivating failover...")
        liara.deactivate_failover(reason="demo_complete")
        logger.info("✅ Failover deactivated successfully")
    else:
        logger.error("❌ Failover activation failed")

    logger.info("")


def demo_role_stacking_prevention():
    """Demonstrate role-stacking prohibition."""
    logger.info("=" * 80)
    logger.info("DEMO 2: Role-Stacking Prevention")
    logger.info("=" * 80)

    liara = LiaraKernel(ttl_seconds=60)

    # Activate for Galahad
    logger.info("Activating failover for Galahad...")
    liara.activate_failover(TriumviratePillar.GALAHAD, reason="test1")

    # Try to activate for Cerberus (should fail)
    logger.info("Attempting to activate failover for Cerberus (should fail)...")
    success = liara.activate_failover(TriumviratePillar.CERBERUS, reason="test2")

    if not success:
        logger.info("✅ Role-stacking correctly prevented!")
        logger.info("Statistics: %s", liara.stats)
    else:
        logger.error("❌ Role-stacking was NOT prevented - BUG!")

    # Clean up
    liara.deactivate_failover()
    logger.info("")


def demo_ttl_enforcement():
    """Demonstrate TTL enforcement and automatic shutdown."""
    logger.info("=" * 80)
    logger.info("DEMO 3: TTL Enforcement (10s timeout)")
    logger.info("=" * 80)

    # Create with very short TTL for demo
    liara = LiaraKernel(ttl_seconds=10)

    # Activate failover
    logger.info("Activating failover with 10s TTL...")
    liara.activate_failover(TriumviratePillar.CODEX_DEUS, reason="ttl_test")

    # Monitor TTL countdown
    for i in range(12):
        remaining = liara.get_remaining_ttl()
        if remaining is not None:
            logger.info("TTL remaining: %.1fs", remaining)
        else:
            logger.info("Failover automatically shutdown (TTL expired)")
            break
        time.sleep(1)

    # Check final status
    status = liara.get_status()
    logger.info("Final status - Active: %s", status["active"])
    logger.info("Statistics: %s", status["statistics"])
    logger.info("")


def demo_health_monitoring():
    """Demonstrate health monitoring and automatic failover."""
    logger.info("=" * 80)
    logger.info("DEMO 4: Health Monitoring and Auto-Failover")
    logger.info("=" * 80)

    # Create simulator and Liara kernel
    simulator = TriumvirateSimulator()
    health_monitor = HealthMonitor()
    liara = LiaraKernel(
        health_monitor=health_monitor, ttl_seconds=60, failover_threshold=3
    )

    # Register health checks
    liara.register_pillar_health_check(
        TriumviratePillar.GALAHAD, simulator.check_galahad
    )
    liara.register_pillar_health_check(
        TriumviratePillar.CERBERUS, simulator.check_cerberus
    )
    liara.register_pillar_health_check(
        TriumviratePillar.CODEX_DEUS, simulator.check_codex_deus
    )

    # Start monitoring
    health_monitor.start_monitoring()

    # Simulate Galahad degradation
    logger.info("Simulating Galahad degradation...")
    simulator.set_pillar_health(TriumviratePillar.GALAHAD, healthy=False)

    # Check health multiple times to trigger failover
    for i in range(5):
        status = liara.check_pillar_health(TriumviratePillar.GALAHAD)
        logger.info("Health check %d: %s", i + 1, status.value)
        time.sleep(1)

    # Check if failover was triggered
    active_role = liara.get_active_role()
    if active_role == TriumviratePillar.GALAHAD:
        logger.info("✅ Auto-failover successfully triggered for degraded Galahad")
    else:
        logger.warning("❌ Auto-failover not triggered")

    # Simulate recovery
    logger.info("Simulating Galahad recovery...")
    simulator.set_pillar_health(TriumviratePillar.GALAHAD, healthy=True)
    time.sleep(2)

    # Perform handoff
    logger.info("Attempting handoff to recovered Galahad...")
    success = liara.handoff_to_pillar(TriumviratePillar.GALAHAD)

    if success:
        logger.info("✅ Handoff successful")
    else:
        logger.error("❌ Handoff failed")

    # Stop monitoring
    health_monitor.stop_monitoring()
    logger.info("")


def demo_limited_capabilities():
    """Demonstrate limited capability execution."""
    logger.info("=" * 80)
    logger.info("DEMO 5: Limited Capability Execution")
    logger.info("=" * 80)

    liara = LiaraKernel(ttl_seconds=60)

    # Test capabilities while inactive
    logger.info("Testing capabilities while inactive:")
    has_reasoning = liara.has_capability(LiaraCapability.BASIC_REASONING)
    has_monitoring = liara.has_capability(LiaraCapability.HEALTH_MONITORING)
    logger.info("  - Basic Reasoning: %s", has_reasoning)
    logger.info("  - Health Monitoring: %s", has_monitoring)

    # Activate as Galahad
    logger.info("\nActivating as Galahad...")
    liara.activate_failover(TriumviratePillar.GALAHAD, reason="capability_test")

    # Test capabilities while active
    logger.info("Testing capabilities while active as Galahad:")
    capabilities = [
        LiaraCapability.BASIC_REASONING,
        LiaraCapability.POLICY_CHECK,
        LiaraCapability.SIMPLE_INFERENCE,
        LiaraCapability.EMERGENCY_SHUTDOWN,
    ]

    for cap in capabilities:
        has_cap = liara.has_capability(cap)
        logger.info("  - %s: %s", cap.value, has_cap)

    # Execute basic reasoning
    logger.info("\nExecuting basic reasoning operation...")
    result = liara.execute_limited_operation(
        LiaraCapability.BASIC_REASONING, {"input": "test_data"}
    )
    logger.info("Result: %s", result)

    # Try executing policy check (should fail - not available for Galahad role)
    logger.info("\nAttempting policy check (should fail for Galahad role)...")
    result = liara.execute_limited_operation(
        LiaraCapability.POLICY_CHECK, {"input": "test_policy"}
    )
    logger.info("Result: %s", result)

    # Clean up
    liara.deactivate_failover()
    logger.info("")


def demo_cryptographic_proof():
    """Demonstrate cryptographic TTL proof verification."""
    logger.info("=" * 80)
    logger.info("DEMO 6: Cryptographic TTL Proof Verification")
    logger.info("=" * 80)

    liara = LiaraKernel(ttl_seconds=60)

    # Activate failover
    logger.info("Activating failover...")
    liara.activate_failover(TriumviratePillar.CERBERUS, reason="proof_test")

    # Verify proof
    logger.info("Verifying TTL proof...")
    valid = liara.verify_ttl_proof()
    logger.info("Proof valid: %s", valid)

    if valid:
        logger.info("✅ Cryptographic proof verified successfully")

        # Get proof details
        if liara.active_role:
            logger.info("Activation proof: %s", liara.active_role.activation_proof[:32] + "...")
            logger.info("Activated at: %s", liara.active_role.activated_at)
            logger.info("TTL: %ds", liara.active_role.ttl_seconds)

    # Clean up
    liara.deactivate_failover()
    logger.info("")


def run_all_demos():
    """Run all demonstration scenarios."""
    logger.info("\n")
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 20 + "LIARA KERNEL DEMONSTRATION" + " " * 32 + "║")
    logger.info("║" + " " * 15 + "Triumvirate Failover Controller" + " " * 32 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    logger.info("\n")

    demos = [
        ("Basic Failover", demo_basic_failover),
        ("Role-Stacking Prevention", demo_role_stacking_prevention),
        ("TTL Enforcement", demo_ttl_enforcement),
        ("Health Monitoring", demo_health_monitoring),
        ("Limited Capabilities", demo_limited_capabilities),
        ("Cryptographic Proof", demo_cryptographic_proof),
    ]

    for name, demo_func in demos:
        try:
            demo_func()
            time.sleep(1)  # Brief pause between demos
        except Exception as e:
            logger.error("Demo '%s' failed: %s", name, e, exc_info=True)

    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 25 + "ALL DEMOS COMPLETE" + " " * 35 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    logger.info("\n")


if __name__ == "__main__":
    run_all_demos()
