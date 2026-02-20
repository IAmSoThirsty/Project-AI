#!/usr/bin/env python3
"""
Simulation Runner for AICPD Engine
Executes a complete 5+ year simulation and generates all artifacts.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engines.alien_invaders import AlienInvadersEngine, load_scenario_preset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("engines/alien_invaders/artifacts/simulation.log"),
    ],
)
logger = logging.getLogger(__name__)


def run_simulation(
    scenario: str = "standard",
    duration_years: int = 5,
    output_dir: str = "engines/alien_invaders/artifacts",
) -> bool:
    """
    Run a complete AICPD simulation.

    Args:
        scenario: Scenario preset name
        duration_years: Simulation duration in years
        output_dir: Output directory for artifacts

    Returns:
        bool: True if simulation completed successfully
    """
    logger.info("=" * 80)
    logger.info("ALIEN INVADERS CONTINGENCY PLAN DEFENSE ENGINE")
    logger.info("=" * 80)
    logger.info("Scenario: %s", scenario)
    logger.info("Duration: %d years", duration_years)
    logger.info("Output: %s", output_dir)
    logger.info("=" * 80)

    try:
        # Load configuration
        config = load_scenario_preset(scenario)
        config.world.simulation_duration_years = duration_years
        config.artifacts.artifact_dir = output_dir

        # Create engine
        engine = AlienInvadersEngine(config)

        # Initialize
        if not engine.init():
            logger.error("Failed to initialize simulation")
            return False

        # Calculate total ticks
        total_days = duration_years * 365
        total_ticks = total_days // config.world.time_step_days

        logger.info("Starting simulation: %d ticks over %d years", total_ticks, duration_years)

        # Run simulation
        for tick_num in range(total_ticks):
            if not engine.tick():
                logger.error("Simulation failed at tick %d", tick_num)
                return False

            # Progress logging
            if (tick_num + 1) % 12 == 0:  # Every year (12 months)
                year = (tick_num + 1) // 12
                state = engine.observe("global")
                logger.info(
                    "Year %d: Population=%d, Casualties=%d, Morale=%.2f",
                    year,
                    state["population"],
                    state["casualties"],
                    state["average_morale"],
                )

                alien_state = engine.observe("aliens")
                logger.info(
                    "  Aliens: Ships=%d, Control=%.1f%%",
                    alien_state["alien_ships"],
                    alien_state["control_percentage"],
                )

            # Inject random events occasionally
            if tick_num % 24 == 0 and tick_num > 0:  # Every 2 years
                engine.inject_event(
                    "random_crisis",
                    {
                        "severity": "medium",
                        "description": "Random crisis event for realism",
                    },
                )

        # Export artifacts
        logger.info("Simulation complete. Exporting artifacts...")
        if not engine.export_artifacts(output_dir):
            logger.error("Failed to export artifacts")
            return False

        # Final summary
        final_state = engine.observe()
        logger.info("=" * 80)
        logger.info("SIMULATION COMPLETE")
        logger.info("=" * 80)
        logger.info("Final Population: %d", final_state["global"]["population"])
        logger.info("Total Casualties: %d", final_state["global"]["casualties"])
        logger.info("Average Morale: %.2f", final_state["global"]["average_morale"])
        logger.info("Alien Control: %.1f%%", final_state["aliens"]["control_percentage"])
        logger.info("AI Operational: %s", final_state["ai"]["operational"])
        logger.info("Total Events: %d", final_state["num_events"])
        logger.info("=" * 80)
        logger.info("Artifacts saved to: %s", output_dir)
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error("Simulation failed with exception: %s", e, exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Alien Invaders Contingency Plan Defense Engine - Simulation Runner")

    parser.add_argument(
        "--scenario",
        type=str,
        default="standard",
        choices=["standard", "aggressive", "peaceful", "extinction"],
        help="Scenario preset to run",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Simulation duration in years (default: 5)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="engines/alien_invaders/artifacts",
        help="Output directory for artifacts",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Run simulation
    success = run_simulation(
        scenario=args.scenario,
        duration_years=args.duration,
        output_dir=args.output,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
