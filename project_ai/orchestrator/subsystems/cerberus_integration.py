"""
Cerberus Security Framework Integration
Provides multi-agent security shield with 3+ guardians
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add Cerberus to path
cerberus_path = (
    Path(__file__).parent.parent.parent.parent / "external" / "Cerberus" / "src"
)
sys.path.insert(0, str(cerberus_path))

try:
    from cerberus.security import (
        AuditLogger,
        InputValidator,
        RateLimiter,
        SecurityMonitor,
        ThreatDetector,
    )

    from cerberus import CerberusHub

    CERBERUS_AVAILABLE = True
except ImportError as e:
    CERBERUS_AVAILABLE = False
    import_error = str(e)


class CerberusIntegration:
    """Integrates Cerberus multi-agent security framework"""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.active = False

        if not CERBERUS_AVAILABLE:
            self.logger.warning(f"Cerberus not available: {import_error}")
            self.hub = None
            return

        # Initialize Cerberus Hub (spawns 3 guardians automatically)
        self.hub = CerberusHub()

        # Initialize security modules
        self.validator = InputValidator()
        self.audit_logger = AuditLogger()
        self.rate_limiter = RateLimiter()
        self.threat_detector = ThreatDetector()
        self.security_monitor = SecurityMonitor()

        self.logger.info("Cerberus integration initialized")

    def start(self) -> None:
        """Start all Cerberus security components"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING CERBERUS SECURITY FRAMEWORK")
        self.logger.info("=" * 60)

        if not CERBERUS_AVAILABLE or not self.hub:
            self.logger.error("Cerberus not available - skipping")
            return

        # Hub auto-starts with 3 guardians
        status = self.hub.get_status()
        self.logger.info(f"Cerberus Hub: {status['active_guardians']} guardians ACTIVE")

        # Start security monitoring
        self.security_monitor.start_monitoring()
        self.logger.info("Security monitor: ACTIVE")

        # Log initial threat level
        threat_level = self.threat_detector.get_current_threat_level()
        self.logger.info(f"Threat level: {threat_level}")

        self.active = True
        self.logger.info("✓ Cerberus Security Framework OPERATIONAL")

    def stop(self) -> None:
        """Stop Cerberus"""
        self.logger.info("Stopping Cerberus Security Framework...")
        if CERBERUS_AVAILABLE and hasattr(self, "security_monitor"):
            self.security_monitor.stop_monitoring()
        self.active = False
        self.logger.info("Cerberus stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Cerberus status"""
        if not CERBERUS_AVAILABLE or not self.hub:
            return {"active": False, "available": False}

        return {
            "active": self.active,
            "available": True,
            "hub_status": self.hub.get_status(),
            "validator_stats": (
                self.validator.get_statistics()
                if hasattr(self.validator, "get_statistics")
                else {}
            ),
            "threat_level": (
                self.threat_detector.get_current_threat_level()
                if hasattr(self.threat_detector, "get_current_threat_level")
                else "UNKNOWN"
            ),
        }

    def analyze_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze input for threats (main API)"""
        if not CERBERUS_AVAILABLE or not self.hub:
            return {
                "should_block": False,
                "summary": "Cerberus not available",
                "active_guardians": 0,
            }

        decision = self.hub.analyze(user_input)
        return {
            "should_block": decision.should_block,
            "summary": decision.summary,
            "active_guardians": self.hub.get_status()["active_guardians"],
        }
