#!/usr/bin/env python3
"""
Defense Engine Main Entry Point
Project-AI God Tier Zombie Apocalypse Defense Engine

Main entry point for initializing and running the complete defense engine
with all 10 functional domain subsystems, core systems, and infrastructure.

Usage:
    python -m src.app.defense_engine

    # With custom config
    python -m src.app.defense_engine --config config/defense_engine.toml

    # Air-gapped mode
    python -m src.app.defense_engine --mode air_gapped
"""

import argparse
import logging
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.app.core.bootstrap_orchestrator import (
    BootstrapOrchestrator,
    bootstrap_defense_engine,
)
from src.app.core.interface_abstractions import OperationalMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/defense_engine.log"),
    ],
)
logger = logging.getLogger(__name__)


class DefenseEngine:
    """
    Main Defense Engine Coordinator

    Coordinates all subsystems and provides high-level control interface.
    """

    def __init__(
        self,
        config_path: str | None = None,
        data_dir: str = "data",
        operational_mode: OperationalMode = OperationalMode.NORMAL,
    ):
        """
        Initialize the defense engine.

        Args:
            config_path: Path to configuration file
            data_dir: Directory for persistent data
            operational_mode: Initial operational mode
        """
        self.config_path = config_path or "config/defense_engine.toml"
        self.data_dir = data_dir
        self.operational_mode = operational_mode

        self.orchestrator: BootstrapOrchestrator | None = None
        self.registry = None
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("=" * 80)
        logger.info("PROJECT-AI GOD TIER ZOMBIE APOCALYPSE DEFENSE ENGINE")
        logger.info("=" * 80)

    def initialize(self) -> bool:
        """
        Initialize the defense engine and all subsystems.

        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Defense Engine...")

            # Create data directory
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)

            # Bootstrap all subsystems
            self.orchestrator = bootstrap_defense_engine(
                config_path=self.config_path, data_dir=self.data_dir
            )

            self.registry = self.orchestrator.registry

            # Set operational mode on all subsystems
            if self.operational_mode != OperationalMode.NORMAL:
                self._set_operational_mode(self.operational_mode)

            # Verify critical subsystems
            critical_subsystems = [
                "situational_awareness",
                "command_control",
                "biomedical_defense",
                "ethics_governance",
                "agi_safeguards",
            ]

            for subsystem_id in critical_subsystems:
                subsystem = self.registry.get_subsystem(subsystem_id)
                if not subsystem:
                    logger.error("Critical subsystem not initialized: %s", subsystem_id)
                    return False

                if not subsystem.health_check():
                    logger.error("Critical subsystem unhealthy: %s", subsystem_id)
                    return False

            self.running = True
            logger.info("Defense Engine initialization complete!")
            logger.info("All systems operational. Ready for zombie apocalypse.")

            return True

        except Exception as e:
            logger.error("Failed to initialize Defense Engine: %s", e, exc_info=True)
            return False

    def run(self):
        """Run the defense engine main loop."""
        if not self.running:
            logger.error("Defense Engine not initialized")
            return

        logger.info("Defense Engine now running...")
        logger.info("Press Ctrl+C to shutdown gracefully")

        try:
            # Main loop - just keep the engine running
            # Individual subsystems have their own background threads
            while self.running:
                import time

                time.sleep(1)

                # Periodic status check
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self._log_status()

        except KeyboardInterrupt:
            logger.info("Shutdown signal received")

        finally:
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown the defense engine."""
        if not self.running:
            return

        logger.info("Shutting down Defense Engine...")
        self.running = False

        if self.orchestrator:
            self.orchestrator.shutdown()

        logger.info("Defense Engine shutdown complete")
        logger.info("Stay safe out there!")

    def _set_operational_mode(self, mode: OperationalMode):
        """Set operational mode on all subsystems."""
        logger.info("Setting operational mode to: %s", mode.value)

        if not self.registry:
            return

        status = self.registry.get_system_status()

        for subsystem_id in status.get("subsystems", {}):
            subsystem = self.registry.get_subsystem(subsystem_id)

            if subsystem and hasattr(subsystem, "set_operational_mode"):
                try:
                    subsystem.set_operational_mode(mode)
                except Exception as e:
                    logger.error("Failed to set mode on %s: %s", subsystem_id, e)

    def _log_status(self):
        """Log current system status."""
        if not self.registry:
            return

        status = self.registry.get_system_status()

        logger.info("=" * 60)
        logger.info("SYSTEM STATUS: %s", status["timestamp"])
        logger.info("Total Subsystems: %s", status["total_subsystems"])
        logger.info("State Distribution: %s", status["subsystems_by_state"])
        logger.info("=" * 60)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Received signal %s", signum)
        self.running = False

    def get_subsystem(self, subsystem_id: str):
        """Get a subsystem instance by ID."""
        if not self.registry:
            return None
        return self.registry.get_subsystem(subsystem_id)

    def get_status(self) -> dict:
        """Get comprehensive system status."""
        if not self.registry:
            return {"status": "not_initialized"}

        return self.registry.get_system_status()

    def execute_command(self, subsystem_id: str, command_type: str, parameters: dict):
        """
        Execute a command on a subsystem.

        Args:
            subsystem_id: Target subsystem ID
            command_type: Command type
            parameters: Command parameters

        Returns:
            Command response
        """
        subsystem = self.get_subsystem(subsystem_id)

        if not subsystem:
            return {"error": f"Subsystem not found: {subsystem_id}"}

        if not hasattr(subsystem, "execute_command"):
            return {"error": f"Subsystem {subsystem_id} does not support commands"}

        from datetime import datetime

        from src.app.core.interface_abstractions import SubsystemCommand

        command = SubsystemCommand(
            command_id=f"cmd_{datetime.now().timestamp()}",
            command_type=command_type,
            parameters=parameters,
            timestamp=datetime.now(),
        )

        try:
            response = subsystem.execute_command(command)
            return {
                "success": response.success,
                "result": response.result,
                "error": response.error,
                "execution_time_ms": response.execution_time_ms,
            }
        except Exception as e:
            logger.error("Command execution failed: %s", e)
            return {"error": str(e)}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Project-AI God Tier Zombie Apocalypse Defense Engine"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/defense_engine.toml",
        help="Path to configuration file",
    )

    parser.add_argument(
        "--data-dir", type=str, default="data", help="Directory for persistent data"
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=[
            "normal",
            "degraded",
            "air_gapped",
            "adversarial",
            "recovery",
            "maintenance",
            "emergency",
        ],
        default="normal",
        help="Operational mode",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Map mode string to enum
    mode_map = {
        "normal": OperationalMode.NORMAL,
        "degraded": OperationalMode.DEGRADED,
        "air_gapped": OperationalMode.AIR_GAPPED,
        "adversarial": OperationalMode.ADVERSARIAL,
        "recovery": OperationalMode.RECOVERY,
        "maintenance": OperationalMode.MAINTENANCE,
        "emergency": OperationalMode.EMERGENCY,
    }

    # Create and run defense engine
    engine = DefenseEngine(
        config_path=args.config,
        data_dir=args.data_dir,
        operational_mode=mode_map[args.mode],
    )

    if engine.initialize():
        engine.run()
        return 0
    else:
        logger.error("Failed to initialize Defense Engine")
        return 1


if __name__ == "__main__":
    sys.exit(main())
