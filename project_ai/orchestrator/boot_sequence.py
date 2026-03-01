"""
Master Boot Sequence for Sovereign Stack
Orchestrates startup of all subsystems in correct order
"""

import logging
from typing import Any, Dict

from .subsystems import (
    CerberusIntegration,
    MonolithIntegration,
    ThirstyLangIntegration,
    TriumvirateIntegration,
    WaterfallIntegration,
)


class BootSequence:
    """Manages startup of all Sovereign Stack subsystems"""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.subsystems = {}
        self.boot_order = [
            "cerberus",  # Security FIRST
            "monolith",  # Governance SECOND
            "thirsty_lang",  # Execution THIRD
            "waterfall",  # Privacy FOURTH
            "triumvirate",  # Unknown LAST
        ]

    def initialize_all(self) -> None:
        """Initialize and start all subsystems in order"""
        self.logger.info("=" * 70)
        self.logger.info("SOVEREIGN STACK BOOT SEQUENCE - STARTING")
        self.logger.info("=" * 70)

        # Phase 1: Security Layer (CRITICAL - Must be first)
        self.logger.info("\n[Phase 1/5] Initializing Security Layer...")
        try:
            self.subsystems["cerberus"] = CerberusIntegration(
                self.config.get("cerberus", {})
            )
            self.subsystems["cerberus"].start()
        except Exception as e:
            self.logger.warning(f"Security layer warning: {e}")
            # Non-critical if not available

        # Phase 2: Governance Layer
        self.logger.info("\n[Phase 2/5] Initializing Governance Layer...")
        try:
            self.subsystems["monolith"] = MonolithIntegration(
                self.config.get("monolith", {})
            )
            self.subsystems["monolith"].start()
        except Exception as e:
            self.logger.warning(f"Governance layer warning: {e}")
            # Non-critical, continue

        # Phase 3: Execution Layer
        self.logger.info("\n[Phase 3/5] Initializing Execution Layer...")
        try:
            self.subsystems["thirsty_lang"] = ThirstyLangIntegration(
                self.config.get("thirsty_lang", {})
            )
            self.subsystems["thirsty_lang"].start()
        except Exception as e:
            self.logger.warning(f"Execution layer warning: {e}")
            # Non-critical, continue

        # Phase 4: Privacy Layer
        self.logger.info("\n[Phase 4/5] Initializing Privacy Layer...")
        try:
            self.subsystems["waterfall"] = WaterfallIntegration(
                self.config.get("waterfall", {})
            )
            self.subsystems["waterfall"].start()
        except Exception as e:
            self.logger.warning(f"Privacy layer warning: {e}")
            # Non-critical, continue

        # Phase 5: Triumvirate (Unknown)
        self.logger.info("\n[Phase 5/5] Initializing Triumvirate Layer...")
        try:
            self.subsystems["triumvirate"] = TriumvirateIntegration(
                self.config.get("triumvirate", {})
            )
            self.subsystems["triumvirate"].start()
        except Exception as e:
            self.logger.warning(f"Triumvirate layer warning: {e}")
            # Non-critical, continue

        self.logger.info("\n" + "=" * 70)
        self.logger.info("BOOT SEQUENCE COMPLETE")
        self._print_status_summary()
        self.logger.info("=" * 70)

    def shutdown_all(self) -> None:
        """Shutdown all subsystems in reverse order"""
        self.logger.info("Shutting down all subsystems...")

        for subsystem_name in reversed(self.boot_order):
            if subsystem_name in self.subsystems:
                try:
                    self.subsystems[subsystem_name].stop()
                    self.logger.info(f"✓ {subsystem_name} stopped")
                except Exception as e:
                    self.logger.error(f"Error stopping {subsystem_name}: {e}")

        self.logger.info("All subsystems shut down")

    def _print_status_summary(self) -> None:
        """Print status summary of all subsystems"""
        self.logger.info("\n📊 Subsystem Status Summary:")
        for name, subsystem in self.subsystems.items():
            status = subsystem.get_status()
            active = status.get("active", False)
            symbol = "✅" if active else "❌"
            self.logger.info(
                f"  {symbol} {name.upper()}: {'ACTIVE' if active else 'INACTIVE'}"
            )

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all subsystems"""
        return {
            name: subsystem.get_status() for name, subsystem in self.subsystems.items()
        }
