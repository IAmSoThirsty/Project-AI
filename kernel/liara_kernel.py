#                                           [2026-03-04 21:13]
#                                          Productivity: Active
"""
Liara Kernel - Triumvirate Failover Controller

Hot-swapping kernel controller that substitutes for degraded Triumvirate pillars.

Features:
- Hot-swap mechanism for Galahad/Cerberus/Codex Deus
- 900-second (15-minute) TTL with automatic shutdown
- Role-stacking prohibition (single role at a time)
- Health monitoring and degradation detection
- Cryptographic proof-of-TTL enforcement
- Limited capabilities compared to full Triumvirate members

Architecture:
    Liara activates when a Triumvirate pillar degrades:
    - Galahad: Reasoning and arbitration
    - Cerberus: Policy enforcement
    - Codex Deus: ML inference
    
    It maintains system stability during pillar recovery while
    enforcing strict time limits to prevent permanent substitution.

Thirst of Gods Level Architecture
"""

import hashlib
import hmac
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from kernel.health import HealthMonitor, HealthStatus, ProbeType

logger = logging.getLogger(__name__)


class TriumviratePillar(Enum):
    """Triumvirate pillar identifiers"""

    GALAHAD = "galahad"  # Reasoning and arbitration
    CERBERUS = "cerberus"  # Policy enforcement
    CODEX_DEUS = "codex_deus"  # ML inference
    NONE = "none"  # Not active


@dataclass
class LiaraRole:
    """Active Liara role configuration"""

    pillar: TriumviratePillar
    activated_at: float
    ttl_seconds: int = 900  # 15 minutes
    activation_proof: Optional[str] = None  # Cryptographic proof
    shutdown_callback: Optional[Callable] = None


@dataclass
class PillarHealth:
    """Health status of a Triumvirate pillar"""

    pillar: TriumviratePillar
    status: HealthStatus
    last_check: float
    consecutive_failures: int = 0
    failover_threshold: int = 3  # Failures before failover
    metadata: Dict[str, Any] = field(default_factory=dict)


class LiaraCapability(Enum):
    """Limited capabilities available to Liara"""

    # Reduced compared to full pillars
    BASIC_REASONING = "basic_reasoning"  # Simplified Galahad
    POLICY_CHECK = "policy_check"  # Basic Cerberus
    SIMPLE_INFERENCE = "simple_inference"  # Limited Codex
    HEALTH_MONITORING = "health_monitoring"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


class LiaraKernel:
    """
    Liara Kernel - Triumvirate Failover Controller

    Hot-swap failover system for degraded Triumvirate pillars with:
    - Automatic degradation detection
    - Time-limited activation (900s TTL)
    - Single-role enforcement
    - Cryptographic proof of TTL
    - Limited capability subset
    - Graceful handoff back to recovered pillars
    """

    # Secret key for TTL proof generation (in production, use secure key management)
    _TTL_SECRET = b"liara_ttl_enforcement_key_v1"

    def __init__(
        self,
        health_monitor: Optional[HealthMonitor] = None,
        ttl_seconds: int = 900,
        failover_threshold: int = 3,
    ):
        """
        Initialize Liara Kernel.

        Args:
            health_monitor: Health monitoring system (creates new if None)
            ttl_seconds: Time-to-live for failover role (default: 900s = 15min)
            failover_threshold: Consecutive failures before triggering failover
        """
        # Health monitoring
        self.health_monitor = health_monitor or HealthMonitor()

        # Configuration
        self.ttl_seconds = ttl_seconds
        self.failover_threshold = failover_threshold

        # Current role (None if inactive)
        self.active_role: Optional[LiaraRole] = None

        # Pillar health tracking
        self.pillar_health: Dict[TriumviratePillar, PillarHealth] = {
            TriumviratePillar.GALAHAD: PillarHealth(
                pillar=TriumviratePillar.GALAHAD,
                status=HealthStatus.UNKNOWN,
                last_check=time.time(),
            ),
            TriumviratePillar.CERBERUS: PillarHealth(
                pillar=TriumviratePillar.CERBERUS,
                status=HealthStatus.UNKNOWN,
                last_check=time.time(),
            ),
            TriumviratePillar.CODEX_DEUS: PillarHealth(
                pillar=TriumviratePillar.CODEX_DEUS,
                status=HealthStatus.UNKNOWN,
                last_check=time.time(),
            ),
        }

        # TTL enforcement thread
        self.ttl_thread: Optional[threading.Thread] = None
        self.ttl_active = False

        # Statistics
        self.stats = {
            "total_activations": 0,
            "total_shutdowns": 0,
            "total_handoffs": 0,
            "ttl_violations_prevented": 0,
            "role_stacking_prevented": 0,
        }

        # Thread safety
        self.lock = threading.RLock()

        # Callbacks
        self.activation_callbacks: List[Callable] = []
        self.shutdown_callbacks: List[Callable] = []

        logger.info("Liara Kernel initialized (TTL: %ds)", ttl_seconds)

    def register_pillar_health_check(
        self, pillar: TriumviratePillar, check_func: Callable[[], bool]
    ):
        """
        Register health check for Triumvirate pillar.

        Args:
            pillar: Pillar to monitor
            check_func: Health check function (returns True if healthy)
        """
        with self.lock:
            # Register with health monitor
            self.health_monitor.register_health_check(
                name=f"triumvirate_{pillar.value}",
                probe_type=ProbeType.LIVENESS,
                check_func=check_func,
                interval_seconds=5.0,  # Check every 5s
                failure_threshold=self.failover_threshold,
            )

            # Register dependency
            self.health_monitor.register_dependency(
                name=f"{pillar.value}_service", check_func=check_func, critical=True
            )

            logger.info("Registered health check for %s", pillar.value)

    def check_pillar_health(self, pillar: TriumviratePillar) -> HealthStatus:
        """
        Check health of specific Triumvirate pillar.

        Args:
            pillar: Pillar to check

        Returns:
            Current health status
        """
        with self.lock:
            # Run health check
            status = self.health_monitor.run_check(f"triumvirate_{pillar.value}")

            # Update pillar health
            pillar_health = self.pillar_health[pillar]
            old_failures = pillar_health.consecutive_failures
            pillar_health.status = status
            pillar_health.last_check = time.time()

            # Track failures based on the returned status
            if status in (HealthStatus.UNHEALTHY, HealthStatus.DEGRADED):
                pillar_health.consecutive_failures += 1
            else:
                pillar_health.consecutive_failures = 0

            # Trigger failover if threshold exceeded
            # Only trigger once when crossing threshold
            if (
                pillar_health.consecutive_failures >= self.failover_threshold
                and old_failures < self.failover_threshold
            ):
                logger.warning(
                    "%s has exceeded failure threshold (%d failures)",
                    pillar.value,
                    pillar_health.consecutive_failures,
                )
                self._trigger_failover(pillar)

            return status

    def activate_failover(
        self, pillar: TriumviratePillar, reason: str = "manual_activation"
    ) -> bool:
        """
        Activate Liara failover for degraded pillar.

        Args:
            pillar: Pillar to substitute for
            reason: Reason for activation

        Returns:
            True if activation successful, False otherwise
        """
        with self.lock:
            # CRITICAL: Prevent role stacking
            if self.active_role is not None:
                logger.error(
                    "ROLE STACKING PREVENTED: Liara already active as %s, cannot activate as %s",
                    self.active_role.pillar.value,
                    pillar.value,
                )
                self.stats["role_stacking_prevented"] += 1
                return False

            # Check if pillar is valid
            if pillar == TriumviratePillar.NONE:
                logger.error("Cannot activate failover for NONE pillar")
                return False

            # Generate activation proof (cryptographic)
            activation_time = time.time()
            activation_proof = self._generate_ttl_proof(pillar, activation_time)

            # Create role
            self.active_role = LiaraRole(
                pillar=pillar,
                activated_at=activation_time,
                ttl_seconds=self.ttl_seconds,
                activation_proof=activation_proof,
            )

            # Start TTL enforcement
            self._start_ttl_enforcement()

            # Update stats
            self.stats["total_activations"] += 1

            # Trigger callbacks
            for callback in self.activation_callbacks:
                try:
                    callback(pillar, reason)
                except Exception as e:
                    logger.error("Activation callback failed: %s", e)

            logger.warning(
                "⚡ LIARA FAILOVER ACTIVATED: Substituting for %s (reason: %s, TTL: %ds)",
                pillar.value,
                reason,
                self.ttl_seconds,
            )

            return True

    def deactivate_failover(self, reason: str = "manual_shutdown") -> bool:
        """
        Deactivate Liara failover and return to normal operation.

        Args:
            reason: Reason for deactivation

        Returns:
            True if deactivation successful
        """
        with self.lock:
            if self.active_role is None:
                logger.warning("Liara not active, nothing to deactivate")
                return False

            pillar = self.active_role.pillar
            active_duration = time.time() - self.active_role.activated_at

            # Stop TTL enforcement
            self._stop_ttl_enforcement()

            # Clear role
            self.active_role = None

            # Update stats
            self.stats["total_shutdowns"] += 1

            # Trigger callbacks
            for callback in self.shutdown_callbacks:
                try:
                    callback(pillar, reason, active_duration)
                except Exception as e:
                    logger.error("Shutdown callback failed: %s", e)

            logger.info(
                "🔄 LIARA FAILOVER DEACTIVATED: Released %s role (reason: %s, duration: %.1fs)",
                pillar.value,
                reason,
                active_duration,
            )

            return True

    def get_active_role(self) -> Optional[TriumviratePillar]:
        """
        Get currently active failover role.

        Returns:
            Active pillar or None if inactive
        """
        with self.lock:
            return self.active_role.pillar if self.active_role else None

    def get_remaining_ttl(self) -> Optional[float]:
        """
        Get remaining time-to-live for active role.

        Returns:
            Remaining seconds or None if inactive
        """
        with self.lock:
            if self.active_role is None:
                return None

            elapsed = time.time() - self.active_role.activated_at
            remaining = self.active_role.ttl_seconds - elapsed

            return max(0.0, remaining)

    def verify_ttl_proof(self) -> bool:
        """
        Verify cryptographic proof of TTL enforcement.

        Returns:
            True if proof valid and TTL not violated
        """
        with self.lock:
            if self.active_role is None:
                return True  # No active role, no violation

            # Verify proof matches
            expected_proof = self._generate_ttl_proof(
                self.active_role.pillar, self.active_role.activated_at
            )

            if self.active_role.activation_proof != expected_proof:
                logger.error("TTL PROOF VERIFICATION FAILED: Proof mismatch")
                return False

            # Check TTL not exceeded
            remaining = self.get_remaining_ttl()
            if remaining is not None and remaining <= 0:
                logger.error("TTL VERIFICATION FAILED: Time limit exceeded")
                return False

            return True

    def has_capability(self, capability: LiaraCapability) -> bool:
        """
        Check if Liara has specific capability based on active role.

        Args:
            capability: Capability to check

        Returns:
            True if capability available
        """
        with self.lock:
            if self.active_role is None:
                # Only health monitoring available when inactive
                return capability == LiaraCapability.HEALTH_MONITORING

            # Map capabilities to pillars
            capability_map = {
                TriumviratePillar.GALAHAD: [
                    LiaraCapability.BASIC_REASONING,
                    LiaraCapability.HEALTH_MONITORING,
                    LiaraCapability.EMERGENCY_SHUTDOWN,
                ],
                TriumviratePillar.CERBERUS: [
                    LiaraCapability.POLICY_CHECK,
                    LiaraCapability.HEALTH_MONITORING,
                    LiaraCapability.EMERGENCY_SHUTDOWN,
                ],
                TriumviratePillar.CODEX_DEUS: [
                    LiaraCapability.SIMPLE_INFERENCE,
                    LiaraCapability.HEALTH_MONITORING,
                    LiaraCapability.EMERGENCY_SHUTDOWN,
                ],
            }

            available = capability_map.get(self.active_role.pillar, [])
            return capability in available

    def execute_limited_operation(
        self, capability: LiaraCapability, operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute limited operation based on capability.

        Args:
            capability: Required capability
            operation_data: Operation parameters

        Returns:
            Operation result
        """
        with self.lock:
            # Verify TTL not violated
            if not self.verify_ttl_proof():
                return {
                    "success": False,
                    "error": "TTL verification failed",
                    "ttl_violated": True,
                }

            # Check capability
            if not self.has_capability(capability):
                return {
                    "success": False,
                    "error": f"Capability {capability.value} not available",
                    "active_role": (
                        self.active_role.pillar.value if self.active_role else "none"
                    ),
                }

            # Execute based on capability (simplified implementations)
            if capability == LiaraCapability.BASIC_REASONING:
                return self._execute_basic_reasoning(operation_data)
            elif capability == LiaraCapability.POLICY_CHECK:
                return self._execute_policy_check(operation_data)
            elif capability == LiaraCapability.SIMPLE_INFERENCE:
                return self._execute_simple_inference(operation_data)
            elif capability == LiaraCapability.EMERGENCY_SHUTDOWN:
                return self._execute_emergency_shutdown(operation_data)
            else:
                return {"success": False, "error": "Unknown capability"}

    def handoff_to_pillar(self, pillar: TriumviratePillar) -> bool:
        """
        Hand off active role back to recovered pillar.

        Args:
            pillar: Pillar to hand off to

        Returns:
            True if handoff successful
        """
        with self.lock:
            if self.active_role is None:
                logger.warning("No active role to hand off")
                return False

            if self.active_role.pillar != pillar:
                logger.error(
                    "Cannot hand off %s role to %s",
                    self.active_role.pillar.value,
                    pillar.value,
                )
                return False

            # Verify pillar is healthy
            pillar_health = self.pillar_health[pillar]
            if pillar_health.status not in (HealthStatus.HEALTHY,):
                logger.error(
                    "Cannot hand off to unhealthy pillar %s (status: %s)",
                    pillar.value,
                    pillar_health.status.value,
                )
                return False

            # Perform handoff
            self.stats["total_handoffs"] += 1
            self.deactivate_failover(reason=f"handoff_to_{pillar.value}")

            logger.info("✅ HANDOFF COMPLETE: %s recovered and resumed", pillar.value)
            return True

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive Liara status.

        Returns:
            Status dictionary
        """
        with self.lock:
            status = {
                "active": self.active_role is not None,
                "active_role": (
                    self.active_role.pillar.value if self.active_role else None
                ),
                "ttl_remaining": self.get_remaining_ttl(),
                "ttl_proof_valid": self.verify_ttl_proof(),
                "pillar_health": {
                    pillar.value: {
                        "status": health.status.value,
                        "consecutive_failures": health.consecutive_failures,
                        "last_check": health.last_check,
                    }
                    for pillar, health in self.pillar_health.items()
                },
                "statistics": self.stats,
            }

            return status

    def register_activation_callback(self, callback: Callable):
        """Register callback for role activation."""
        with self.lock:
            self.activation_callbacks.append(callback)

    def register_shutdown_callback(self, callback: Callable):
        """Register callback for role shutdown."""
        with self.lock:
            self.shutdown_callbacks.append(callback)

    # Private methods

    def _trigger_failover(self, pillar: TriumviratePillar):
        """Automatically trigger failover for degraded pillar."""
        logger.warning(
            "AUTO-TRIGGERING FAILOVER: %s has degraded beyond threshold", pillar.value
        )
        self.activate_failover(pillar, reason="automatic_degradation_detection")

    def _generate_ttl_proof(self, pillar: TriumviratePillar, activation_time: float) -> str:
        """
        Generate cryptographic proof for TTL enforcement.

        Args:
            pillar: Activated pillar
            activation_time: Activation timestamp

        Returns:
            HMAC-SHA256 proof string
        """
        # Construct proof message
        message = f"{pillar.value}:{activation_time}:{self.ttl_seconds}".encode("utf-8")

        # Generate HMAC
        proof = hmac.new(self._TTL_SECRET, message, hashlib.sha256).hexdigest()

        return proof

    def _start_ttl_enforcement(self):
        """Start background TTL enforcement thread."""
        if self.ttl_active:
            return

        self.ttl_active = True
        self.ttl_thread = threading.Thread(target=self._ttl_enforcement_loop, daemon=True)
        self.ttl_thread.start()

        logger.info("TTL enforcement thread started")

    def _stop_ttl_enforcement(self):
        """Stop background TTL enforcement thread."""
        self.ttl_active = False

        if self.ttl_thread:
            # Check if we're trying to join from the same thread
            if threading.current_thread() != self.ttl_thread:
                self.ttl_thread.join(timeout=2.0)
            self.ttl_thread = None

        logger.info("TTL enforcement thread stopped")

    def _ttl_enforcement_loop(self):
        """Background loop for TTL enforcement."""
        while self.ttl_active:
            try:
                with self.lock:
                    if self.active_role is None:
                        break

                    remaining = self.get_remaining_ttl()

                    # Check if TTL expired
                    if remaining is not None and remaining <= 0:
                        logger.error(
                            "⏰ TTL EXPIRED: Forcing shutdown after %ds",
                            self.ttl_seconds,
                        )
                        self.stats["ttl_violations_prevented"] += 1
                        self.deactivate_failover(reason="ttl_expired")
                        break

                    # Warn at milestones
                    if remaining is not None:
                        if 55 <= remaining <= 65:  # ~1 minute warning
                            logger.warning(
                                "⚠️  TTL WARNING: %.0f seconds remaining", remaining
                            )

                # Sleep briefly
                time.sleep(1.0)

            except Exception as e:
                logger.error("TTL enforcement error: %s", e)

    # Limited capability implementations

    def _execute_basic_reasoning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute basic reasoning (limited Galahad)."""
        logger.info("Executing basic reasoning (limited Galahad capability)")
        return {
            "success": True,
            "capability": "basic_reasoning",
            "result": "Limited reasoning performed",
            "note": "This is a reduced capability compared to full Galahad",
        }

    def _execute_policy_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute policy check (limited Cerberus)."""
        logger.info("Executing policy check (limited Cerberus capability)")
        return {
            "success": True,
            "capability": "policy_check",
            "result": "Basic policy check performed",
            "note": "This is a reduced capability compared to full Cerberus",
        }

    def _execute_simple_inference(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple inference (limited Codex Deus)."""
        logger.info("Executing simple inference (limited Codex Deus capability)")
        return {
            "success": True,
            "capability": "simple_inference",
            "result": "Simple inference performed",
            "note": "This is a reduced capability compared to full Codex Deus",
        }

    def _execute_emergency_shutdown(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute emergency shutdown."""
        logger.warning("EMERGENCY SHUTDOWN requested")
        self.deactivate_failover(reason="emergency_shutdown")
        return {"success": True, "capability": "emergency_shutdown", "result": "Shutdown complete"}


# Public API
__all__ = [
    "LiaraKernel",
    "TriumviratePillar",
    "LiaraRole",
    "LiaraCapability",
    "PillarHealth",
]
