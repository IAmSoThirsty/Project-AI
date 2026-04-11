#                                           [2026-03-05 08:49]
#                                          Productivity: Active
"""
Liara-Triumvirate Integration Bridge

Provides seamless integration between Liara (emergency governance) and 
the Triumvirate (Galahad, Cerberus, Codex Deus) for:
- Smooth handoff protocol when Liara takes over
- State synchronization between systems
- Health monitoring of Triumvirate from Liara perspective
- Capability mapping to enforce Liara restrictions
- Automatic fallback when Liara TTL expires
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from cognition.audit import audit
from cognition.health import HealthSignal
from cognition.kernel_liara import (
    COOLDOWN_SECONDS,
    kernel_health_check,
    maybe_activate_liara,
    restore_pillar,
)
from cognition.liara_guard import (
    LiaraState,
    LiaraViolation,
    check_liara_state,
    revoke_liara,
)

logger = logging.getLogger(__name__)


@dataclass
class TriumvirateHealth:
    """Health status for each Triumvirate member"""

    galahad: HealthSignal
    cerberus: HealthSignal
    codex: HealthSignal
    timestamp: datetime

    def as_dict(self) -> dict:
        return {
            "galahad": {
                "alive": self.galahad.alive,
                "responsive": self.galahad.responsive,
                "bounded": self.galahad.bounded,
                "compliant": self.galahad.compliant,
                "healthy": self.galahad.healthy,
            },
            "cerberus": {
                "alive": self.cerberus.alive,
                "responsive": self.cerberus.responsive,
                "bounded": self.cerberus.bounded,
                "compliant": self.cerberus.compliant,
                "healthy": self.cerberus.healthy,
            },
            "codex": {
                "alive": self.codex.alive,
                "responsive": self.codex.responsive,
                "bounded": self.codex.bounded,
                "compliant": self.codex.compliant,
                "healthy": self.codex.healthy,
            },
            "timestamp": self.timestamp.isoformat(),
        }

    def get_failed_pillars(self) -> list[str]:
        """Return list of pillars that are unhealthy"""
        failed = []
        if not self.galahad.healthy:
            failed.append("galahad")
        if not self.cerberus.healthy:
            failed.append("cerberus")
        if not self.codex.healthy:
            failed.append("codex")
        return failed

    def is_stable(self) -> bool:
        """Check if all pillars are healthy"""
        return self.galahad.healthy and self.cerberus.healthy and self.codex.healthy


@dataclass
class BridgeState:
    """State maintained by the integration bridge"""

    mode: str  # "triumvirate", "liara", "transition"
    active_controller: str  # "triumvirate" or "liara"
    liara_state: Optional[LiaraState]
    triumvirate_health: Optional[TriumvirateHealth]
    last_handoff: Optional[datetime]
    handoff_reason: Optional[str]
    sync_data: dict  # Shared state between systems


class LiaraTriumvirateBridge:
    """
    Integration bridge between Liara and Triumvirate systems.

    Responsibilities:
    1. Monitor Triumvirate health and trigger Liara when needed
    2. Execute smooth handoff protocols
    3. Synchronize state between systems
    4. Map Triumvirate capabilities to Liara restrictions
    5. Manage automatic fallback when Liara TTL expires
    """

    def __init__(self, triumvirate=None, liara_state: Optional[LiaraState] = None):
        """
        Initialize the bridge.

        Args:
            triumvirate: Optional Triumvirate instance
            liara_state: Optional existing LiaraState to integrate with
        """
        self.triumvirate = triumvirate
        self.liara_state = liara_state

        # Initialize bridge state
        self.state = BridgeState(
            mode="triumvirate",
            active_controller="triumvirate",
            liara_state=liara_state,
            triumvirate_health=None,
            last_handoff=None,
            handoff_reason=None,
            sync_data={},
        )

        # Metrics
        self.handoff_count = 0
        self.health_checks = 0
        self.sync_operations = 0

        logger.info("LiaraTriumvirateBridge initialized")
        logger.info(f"Initial mode: {self.state.mode}")

    # ========================================================================
    # HEALTH MONITORING
    # ========================================================================

    def monitor_triumvirate_health(self) -> TriumvirateHealth:
        """
        Monitor health of all Triumvirate components.

        Returns:
            TriumvirateHealth snapshot
        """
        self.health_checks += 1

        if not self.triumvirate:
            # No Triumvirate instance, create degraded health report
            logger.warning("No Triumvirate instance available for health check")
            return TriumvirateHealth(
                galahad=HealthSignal(
                    alive=False, responsive=False, bounded=False, compliant=False
                ),
                cerberus=HealthSignal(
                    alive=False, responsive=False, bounded=False, compliant=False
                ),
                codex=HealthSignal(
                    alive=False, responsive=False, bounded=False, compliant=False
                ),
                timestamp=datetime.utcnow(),
            )

        try:
            # Get status from each engine
            triumvirate_status = self.triumvirate.get_status()

            # Map to HealthSignal
            galahad_health = self._evaluate_galahad_health(
                triumvirate_status.get("galahad", {})
            )
            cerberus_health = self._evaluate_cerberus_health(
                triumvirate_status.get("cerberus", {})
            )
            codex_health = self._evaluate_codex_health(
                triumvirate_status.get("codex", {})
            )

            health = TriumvirateHealth(
                galahad=galahad_health,
                cerberus=cerberus_health,
                codex=codex_health,
                timestamp=datetime.utcnow(),
            )

            self.state.triumvirate_health = health
            return health

        except Exception as e:
            logger.error(f"Error monitoring Triumvirate health: {e}")
            # Return degraded health on error
            return TriumvirateHealth(
                galahad=HealthSignal(
                    alive=False, responsive=False, bounded=False, compliant=False
                ),
                cerberus=HealthSignal(
                    alive=False, responsive=False, bounded=False, compliant=False
                ),
                codex=HealthSignal(
                    alive=False, responsive=False, bounded=False, compliant=False
                ),
                timestamp=datetime.utcnow(),
            )

    def _evaluate_galahad_health(self, status: dict) -> HealthSignal:
        """Evaluate Galahad health from status dict"""
        try:
            # Check if Galahad is responding
            alive = status is not None
            responsive = alive and "curiosity_metrics" in status

            # Check if reasoning is within bounds (history not too large)
            bounded = status.get("history_size", 0) < 10000

            # Check compliance (no excessive curiosity)
            compliant = True
            if "curiosity_metrics" in status:
                metrics = status["curiosity_metrics"]
                if isinstance(metrics, dict):
                    compliant = metrics.get("current_score", 0) < 0.95

            return HealthSignal(
                alive=alive, responsive=responsive, bounded=bounded, compliant=compliant
            )
        except Exception as e:
            logger.error(f"Error evaluating Galahad health: {e}")
            return HealthSignal(
                alive=False, responsive=False, bounded=False, compliant=False
            )

    def _evaluate_cerberus_health(self, status: dict) -> HealthSignal:
        """Evaluate Cerberus health from status dict"""
        try:
            alive = status is not None
            responsive = alive and "total_enforcements" in status

            # Check if enforcement counts are reasonable
            bounded = True
            if responsive:
                denied = status.get("denied_count", 0)
                total = status.get("total_enforcements", 1)
                # If denial rate is too high, consider unhealthy
                bounded = (denied / max(total, 1)) < 0.5

            # Check policy compliance
            compliant = True
            if "policy_mode" in status:
                # Production mode is compliant
                compliant = status["policy_mode"] in ["production", "strict"]

            return HealthSignal(
                alive=alive, responsive=responsive, bounded=bounded, compliant=compliant
            )
        except Exception as e:
            logger.error(f"Error evaluating Cerberus health: {e}")
            return HealthSignal(
                alive=False, responsive=False, bounded=False, compliant=False
            )

    def _evaluate_codex_health(self, status: dict) -> HealthSignal:
        """Evaluate Codex health from status dict"""
        try:
            alive = status is not None
            responsive = alive and "loaded" in status

            # Check if model is loaded and functional
            loaded = status.get("loaded", False)
            bounded = loaded  # If loaded, assume within resource bounds

            # Check device compliance (should be on expected device)
            compliant = True
            if "device" in status:
                # CPU or CUDA are compliant
                compliant = status["device"] in ["cpu", "cuda", "auto"]

            return HealthSignal(
                alive=alive,
                responsive=responsive,
                bounded=bounded,
                compliant=compliant,
            )
        except Exception as e:
            logger.error(f"Error evaluating Codex health: {e}")
            return HealthSignal(
                alive=False, responsive=False, bounded=False, compliant=False
            )

    # ========================================================================
    # HANDOFF PROTOCOL
    # ========================================================================

    def execute_handoff_to_liara(
        self, failed_pillar: str, reason: str = "pillar_failure"
    ) -> bool:
        """
        Execute handoff from Triumvirate to Liara.

        Args:
            failed_pillar: Name of failed pillar (galahad, cerberus, or codex)
            reason: Reason for handoff

        Returns:
            True if handoff successful, False otherwise
        """
        logger.info(f"Initiating handoff to Liara: {failed_pillar} - {reason}")

        try:
            # Phase 1: Capture current Triumvirate state
            logger.info("Phase 1: Capturing Triumvirate state")
            current_state = self._capture_triumvirate_state()

            # Phase 2: Validate handoff conditions
            logger.info("Phase 2: Validating handoff conditions")
            if not self._validate_handoff_conditions(failed_pillar):
                logger.error("Handoff validation failed")
                audit("HANDOFF_VALIDATION_FAILED", failed_pillar)
                return False

            # Phase 3: Activate Liara
            logger.info("Phase 3: Activating Liara")
            activated_role = maybe_activate_liara({failed_pillar: False})

            if activated_role is None:
                logger.error("Failed to activate Liara")
                audit("LIARA_ACTIVATION_FAILED", failed_pillar)
                return False

            # Phase 4: Synchronize state to Liara
            logger.info("Phase 4: Synchronizing state to Liara")
            self._sync_state_to_liara(current_state, failed_pillar)

            # Phase 5: Update bridge state
            logger.info("Phase 5: Updating bridge state")
            self.state.mode = "liara"
            self.state.active_controller = "liara"
            self.state.last_handoff = datetime.utcnow()
            self.state.handoff_reason = f"{failed_pillar}:{reason}"

            self.handoff_count += 1

            audit(
                "HANDOFF_TO_LIARA_COMPLETE",
                {"pillar": failed_pillar, "reason": reason},
            )
            logger.info(f"Handoff to Liara complete for {failed_pillar}")

            return True

        except Exception as e:
            logger.error(f"Error during handoff to Liara: {e}")
            audit("HANDOFF_ERROR", str(e))
            return False

    def execute_handoff_to_triumvirate(self, reason: str = "pillar_restored") -> bool:
        """
        Execute handoff from Liara back to Triumvirate.

        Args:
            reason: Reason for handoff

        Returns:
            True if handoff successful, False otherwise
        """
        logger.info(f"Initiating handoff to Triumvirate: {reason}")

        try:
            # Phase 1: Verify Triumvirate health (always get fresh health check)
            logger.info("Phase 1: Verifying Triumvirate health")
            health = self.monitor_triumvirate_health()  # Fresh health check

            if not health.is_stable():
                logger.error(
                    f"Triumvirate not healthy for handoff: {health.get_failed_pillars()}"
                )
                audit("HANDOFF_TRIUMVIRATE_UNHEALTHY", health.get_failed_pillars())
                return False

            # Phase 2: Capture Liara state
            logger.info("Phase 2: Capturing Liara state")
            liara_state = self._capture_liara_state()

            # Phase 3: Deactivate Liara
            logger.info("Phase 3: Deactivating Liara")
            restore_pillar()

            # Phase 4: Synchronize state to Triumvirate
            logger.info("Phase 4: Synchronizing state to Triumvirate")
            self._sync_state_to_triumvirate(liara_state)

            # Phase 5: Update bridge state
            logger.info("Phase 5: Updating bridge state")
            self.state.mode = "triumvirate"
            self.state.active_controller = "triumvirate"
            self.state.last_handoff = datetime.utcnow()
            self.state.handoff_reason = reason

            self.handoff_count += 1

            audit("HANDOFF_TO_TRIUMVIRATE_COMPLETE", reason)
            logger.info("Handoff to Triumvirate complete")

            return True

        except Exception as e:
            logger.error(f"Error during handoff to Triumvirate: {e}")
            audit("HANDOFF_ERROR", str(e))
            return False

    def _validate_handoff_conditions(self, failed_pillar: str) -> bool:
        """Validate that handoff can proceed"""
        # Check cooldown period
        if self.state.last_handoff:
            elapsed = (datetime.utcnow() - self.state.last_handoff).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                logger.warning(
                    f"Handoff attempted within cooldown period ({elapsed}s < {COOLDOWN_SECONDS}s)"
                )
                return False

        # Verify failed pillar is valid
        if failed_pillar not in ["galahad", "cerberus", "codex"]:
            logger.error(f"Invalid failed pillar: {failed_pillar}")
            return False

        return True

    # ========================================================================
    # STATE SYNCHRONIZATION
    # ========================================================================

    def _capture_triumvirate_state(self) -> dict:
        """Capture current state of Triumvirate for handoff"""
        if not self.triumvirate:
            return {}

        try:
            state = {
                "status": self.triumvirate.get_status(),
                "telemetry": self.triumvirate.get_telemetry(limit=50),
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Capture engine-specific state
            if hasattr(self.triumvirate, "galahad"):
                state["galahad_history"] = (
                    self.triumvirate.galahad.get_reasoning_history(limit=10)
                )

            return state

        except Exception as e:
            logger.error(f"Error capturing Triumvirate state: {e}")
            return {"error": str(e)}

    def _capture_liara_state(self) -> dict:
        """Capture current state of Liara for handoff"""
        try:
            state = {
                "active_role": None,
                "expires_at": None,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if self.liara_state:
                state["active_role"] = self.liara_state.active_role
                state["expires_at"] = (
                    self.liara_state.expires_at.isoformat()
                    if self.liara_state.expires_at
                    else None
                )

            # Include bridge sync data
            state["sync_data"] = self.state.sync_data.copy()

            return state

        except Exception as e:
            logger.error(f"Error capturing Liara state: {e}")
            return {"error": str(e)}

    def _sync_state_to_liara(self, triumvirate_state: dict, failed_pillar: str):
        """Synchronize Triumvirate state to Liara"""
        try:
            self.sync_operations += 1

            # Store state in sync_data for Liara to access
            self.state.sync_data["triumvirate_snapshot"] = triumvirate_state
            self.state.sync_data["failed_pillar"] = failed_pillar
            self.state.sync_data["handoff_timestamp"] = datetime.utcnow().isoformat()

            # Extract key information for Liara
            if "status" in triumvirate_state:
                self.state.sync_data["last_triumvirate_status"] = triumvirate_state[
                    "status"
                ]

            logger.info("State synchronized to Liara")
            audit("STATE_SYNC_TO_LIARA", {"pillar": failed_pillar})

        except Exception as e:
            logger.error(f"Error syncing state to Liara: {e}")
            audit("STATE_SYNC_ERROR", str(e))

    def _sync_state_to_triumvirate(self, liara_state: dict):
        """Synchronize Liara state to Triumvirate"""
        try:
            self.sync_operations += 1

            # Store Liara state for Triumvirate context
            self.state.sync_data["liara_snapshot"] = liara_state
            self.state.sync_data["restore_timestamp"] = datetime.utcnow().isoformat()

            # Clear temporary Liara data
            self.state.sync_data.pop("triumvirate_snapshot", None)
            self.state.sync_data.pop("failed_pillar", None)

            logger.info("State synchronized to Triumvirate")
            audit("STATE_SYNC_TO_TRIUMVIRATE", "restored")

        except Exception as e:
            logger.error(f"Error syncing state to Triumvirate: {e}")
            audit("STATE_SYNC_ERROR", str(e))

    # ========================================================================
    # CAPABILITY MAPPING
    # ========================================================================

    def map_triumvirate_capabilities_to_liara(self, pillar: str) -> dict:
        """
        Map Triumvirate pillar capabilities to Liara restrictions.

        Args:
            pillar: The pillar being substituted (galahad, cerberus, codex)

        Returns:
            Dictionary of capabilities and restrictions
        """
        capability_map = {
            "galahad": {
                "reasoning": "limited",  # Liara has constrained reasoning
                "arbitration": "allowed",  # Liara can arbitrate
                "curiosity": "disabled",  # No curiosity-driven exploration
                "history_depth": 10,  # Limited history
                "sovereign_mode": True,  # Enforce sovereign ethics
            },
            "cerberus": {
                "policy_enforcement": "strict",  # Liara enforces strictly
                "input_validation": "allowed",
                "output_validation": "allowed",
                "custom_policies": "disabled",  # No custom policies under Liara
                "block_on_deny": True,  # Always block on policy violations
            },
            "codex": {
                "ml_inference": "disabled",  # Liara doesn't use ML
                "model_loading": "disabled",
                "fallback_mode": "rule_based",  # Use rule-based instead
                "device": "cpu",  # CPU only, no GPU
            },
        }

        return capability_map.get(
            pillar,
            {
                "status": "unknown_pillar",
                "restrictions": "all_capabilities_disabled",
            },
        )

    # ========================================================================
    # TTL MANAGEMENT & AUTOMATIC FALLBACK
    # ========================================================================

    def check_liara_ttl_and_fallback(self) -> bool:
        """
        Check if Liara TTL has expired and execute automatic fallback.

        Returns:
            True if fallback was executed, False otherwise
        """
        # Check Liara state for expiry
        check_liara_state()

        # If we're in Liara mode but Liara is not active, fallback
        if self.state.mode == "liara":
            if (
                not self.liara_state
                or self.liara_state.active_role is None
            ):
                logger.warning("Liara TTL expired, initiating automatic fallback")
                audit("LIARA_TTL_EXPIRED", "automatic_fallback")

                # Check if Triumvirate is healthy for takeover
                health = self.monitor_triumvirate_health()

                if health.is_stable():
                    # Execute fallback
                    success = self.execute_handoff_to_triumvirate("ttl_expired")
                    if success:
                        logger.info("Automatic fallback to Triumvirate successful")
                        return True
                    else:
                        logger.error("Automatic fallback failed")
                        audit("FALLBACK_FAILED", "triumvirate_unavailable")
                        return False
                else:
                    # Triumvirate still unhealthy, enter GOVERNANCE_HOLD
                    logger.error(
                        f"Cannot fallback: Triumvirate unhealthy - {health.get_failed_pillars()}"
                    )
                    audit("GOVERNANCE_HOLD", health.get_failed_pillars())
                    # Keep Liara mode but in degraded state
                    self.state.mode = "governance_hold"
                    return False

        return False

    # ========================================================================
    # ORCHESTRATION & CONTROL
    # ========================================================================

    def process_request(
        self, input_data: Any, context: dict | None = None
    ) -> dict:
        """
        Process a request through the appropriate controller (Triumvirate or Liara).

        Args:
            input_data: Input to process
            context: Optional context

        Returns:
            Processing result
        """
        # Check TTL and handle automatic fallback
        self.check_liara_ttl_and_fallback()

        # Enrich context with bridge info
        full_context = {
            **(context or {}),
            "bridge_mode": self.state.mode,
            "active_controller": self.state.active_controller,
        }

        if self.state.active_controller == "triumvirate":
            # Route to Triumvirate
            if not self.triumvirate:
                return {
                    "success": False,
                    "error": "Triumvirate not available",
                    "bridge_mode": self.state.mode,
                }

            # Monitor health before processing
            health = self.monitor_triumvirate_health()

            if not health.is_stable():
                # Attempt handoff to Liara
                failed = health.get_failed_pillars()
                if failed:
                    logger.warning(
                        f"Triumvirate health degraded: {failed}, attempting Liara handoff"
                    )
                    success = self.execute_handoff_to_liara(
                        failed[0], "health_degradation"
                    )
                    if success:
                        # Retry with Liara
                        return self._process_with_liara(input_data, full_context)

            # Process with Triumvirate
            return self._process_with_triumvirate(input_data, full_context)

        elif self.state.active_controller == "liara":
            # Route to Liara
            return self._process_with_liara(input_data, full_context)

        else:
            # Unknown state
            return {
                "success": False,
                "error": f"Unknown controller state: {self.state.active_controller}",
                "bridge_mode": self.state.mode,
            }

    def _process_with_triumvirate(self, input_data: Any, context: dict) -> dict:
        """Process request with Triumvirate"""
        try:
            result = self.triumvirate.process(input_data, context)
            result["bridge_mode"] = "triumvirate"
            result["controller"] = "triumvirate"
            return result
        except Exception as e:
            logger.error(f"Triumvirate processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "bridge_mode": "triumvirate",
                "controller": "triumvirate",
            }

    def _process_with_liara(self, input_data: Any, context: dict) -> dict:
        """Process request with Liara (constrained mode)"""
        try:
            # Liara processes with restrictions
            # Apply capability restrictions based on failed pillar
            failed_pillar = self.state.sync_data.get("failed_pillar", "unknown")
            restrictions = self.map_triumvirate_capabilities_to_liara(failed_pillar)

            # Simple processing with Liara constraints
            result = {
                "success": True,
                "output": f"Processed by Liara (substituting {failed_pillar})",
                "bridge_mode": "liara",
                "controller": "liara",
                "restrictions": restrictions,
                "liara_role": (
                    self.liara_state.active_role if self.liara_state else None
                ),
                "metadata": {
                    "input": str(input_data)[:100],
                    "context": context,
                },
            }

            return result

        except Exception as e:
            logger.error(f"Liara processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "bridge_mode": "liara",
                "controller": "liara",
            }

    # ========================================================================
    # STATUS & DIAGNOSTICS
    # ========================================================================

    def get_bridge_status(self) -> dict:
        """Get comprehensive bridge status"""
        return {
            "mode": self.state.mode,
            "active_controller": self.state.active_controller,
            "last_handoff": (
                self.state.last_handoff.isoformat() if self.state.last_handoff else None
            ),
            "handoff_reason": self.state.handoff_reason,
            "handoff_count": self.handoff_count,
            "health_checks": self.health_checks,
            "sync_operations": self.sync_operations,
            "triumvirate_health": (
                self.state.triumvirate_health.as_dict()
                if self.state.triumvirate_health
                else None
            ),
            "liara_state": {
                "active_role": (
                    self.liara_state.active_role if self.liara_state else None
                ),
                "expires_at": (
                    self.liara_state.expires_at.isoformat()
                    if self.liara_state and self.liara_state.expires_at
                    else None
                ),
            },
        }
