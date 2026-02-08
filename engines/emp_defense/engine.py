"""
EMP Defense Engine - Core simulation engine.

Implements the mandatory 5-method interface for defense engine simulations.
"""

import json
import logging
from pathlib import Path
from typing import Any

from engines.emp_defense.modules.world_state import WorldState
from engines.emp_defense.schemas.config_schema import SimulationConfig

logger = logging.getLogger(__name__)


class EMPDefenseEngine:
    """
    EMP Global Civilization Disruption Defense Engine.

    Simulates electromagnetic pulse events and their cascading effects
    on global civilization infrastructure.

    Examples:
        >>> engine = EMPDefenseEngine()
        >>> engine.init()
        True
        >>> engine.tick()
        True
        >>> state = engine.observe()
        >>> state['simulation_day']
        7
    """

    def __init__(self, config: SimulationConfig | None = None):
        """
        Initialize engine.

        Args:
            config: Simulation configuration (optional)
        """
        self.config = config or SimulationConfig()
        self.state: WorldState | None = None
        self.initialized = False
        self.events: list[dict[str, Any]] = []

        logger.info("EMPDefenseEngine created with scenario: %s", self.config.scenario)

    def init(self) -> bool:
        """
        Initialize simulation with starting conditions.

        Returns:
            True if initialization successful

        Examples:
            >>> engine = EMPDefenseEngine()
            >>> result = engine.init()
            >>> result
            True
            >>> engine.initialized
            True
        """
        try:
            logger.info("Initializing EMP Defense Engine...")

            # Create initial world state
            self.state = WorldState()
            self.state.major_events.append("T+0: Pre-EMP baseline established")

            # Apply initial EMP event
            self._apply_emp_event()

            self.initialized = True
            logger.info("✅ EMP Defense Engine initialized successfully")
            return True

        except Exception as e:
            logger.error("❌ Initialization failed: %s", e)
            return False

    def tick(self) -> bool:
        """
        Advance simulation by one time step (7 days).

        Returns:
            True if tick successful

        Examples:
            >>> engine = EMPDefenseEngine()
            >>> engine.init()
            True
            >>> engine.tick()
            True
            >>> engine.state.simulation_day
            7
        """
        if not self.initialized:
            logger.error("❌ Cannot tick: engine not initialized")
            return False

        try:
            # Advance time by 7 days (weekly time step)
            self.state.simulation_day += 7

            # Simple degradation model
            self._update_world_state()

            logger.debug("Tick complete: Day %s", self.state.simulation_day)
            return True

        except Exception as e:
            logger.error("❌ Tick failed: %s", e)
            return False

    def inject_event(self, event_type: str, parameters: dict) -> str:
        """
        Inject external event into simulation.

        Args:
            event_type: Type of event
            parameters: Event parameters

        Returns:
            Event ID

        Examples:
            >>> engine = EMPDefenseEngine()
            >>> engine.init()
            True
            >>> event_id = engine.inject_event("recovery_effort", {"region": "NA"})
            >>> event_id.startswith("evt_")
            True
        """
        if not self.initialized:
            logger.error("❌ Cannot inject event: engine not initialized")
            return ""

        try:
            event_id = f"evt_{len(self.events) + 1:04d}"
            event = {
                "id": event_id,
                "type": event_type,
                "parameters": parameters,
                "day": self.state.simulation_day,
            }
            self.events.append(event)

            logger.info("Event injected: %s (ID: %s)", event_type, event_id)
            self.state.major_events.append(
                f"Day {self.state.simulation_day}: {event_type}"
            )
            return event_id

        except Exception as e:
            logger.error("❌ Event injection failed: %s", e)
            return ""

    def observe(self, query: str | None = None) -> dict:
        """
        Query current simulation state.

        Args:
            query: Optional query filter (not implemented yet)

        Returns:
            Dictionary with state information

        Examples:
            >>> engine = EMPDefenseEngine()
            >>> engine.init()
            True
            >>> state = engine.observe()
            >>> 'simulation_day' in state
            True
            >>> 'global_population' in state
            True
        """
        if not self.initialized:
            logger.error("❌ Cannot observe: engine not initialized")
            return {}

        try:
            return self.state.to_dict()

        except Exception as e:
            logger.error("❌ Observation failed: %s", e)
            return {}

    def export_artifacts(self, output_dir: str | None = None) -> bool:
        """
        Generate and export simulation artifacts.

        Args:
            output_dir: Output directory (defaults to artifacts/)

        Returns:
            True if export successful

        Examples:
            >>> engine = EMPDefenseEngine()
            >>> engine.init()
            True
            >>> engine.tick()
            True
            >>> result = engine.export_artifacts()
            >>> result
            True
        """
        if not self.initialized:
            logger.error("❌ Cannot export: engine not initialized")
            return False

        try:
            # Determine output directory
            if output_dir is None:
                base_dir = Path(__file__).parent / "artifacts"
            else:
                base_dir = Path(output_dir)

            base_dir.mkdir(parents=True, exist_ok=True)

            # Export final state
            state_file = base_dir / "final_state.json"
            with open(state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)

            # Export events log
            events_file = base_dir / "events.json"
            with open(events_file, 'w') as f:
                json.dump(self.events, f, indent=2)

            # Create simple summary
            summary_file = base_dir / "summary.json"
            summary = {
                "scenario": self.config.scenario,
                "duration_days": self.state.simulation_day,
                "total_deaths": self.state.total_deaths,
                "grid_operational_pct": self.state.grid_operational_pct,
                "event_count": len(self.events),
            }
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            logger.info("✅ Artifacts exported to %s", base_dir)
            return True

        except Exception as e:
            logger.error("❌ Artifact export failed: %s", e)
            return False

    # Private helper methods

    def _apply_emp_event(self):
        """Apply initial EMP event effects."""
        # Grid failure based on configuration
        self.state.grid_operational_pct = 1.0 - self.config.grid_failure_pct

        # Record event
        self.state.major_events.append(
            f"Day 0: EMP event - {self.config.grid_failure_pct*100}% grid failure"
        )

        # Inject event
        self.inject_event("emp_strike", {
            "grid_failure_pct": self.config.grid_failure_pct,
            "population_affected_pct": self.config.population_affected_pct,
        })

    def _update_world_state(self):
        """Update world state for current tick."""
        # Simple degradation model
        days = self.state.simulation_day

        # Grid recovers slowly (0.1% per week)
        if self.state.grid_operational_pct < 1.0:
            self.state.grid_operational_pct = min(
                1.0,
                self.state.grid_operational_pct + 0.001
            )

        # Economic impact (GDP decreases with grid failure)
        grid_factor = self.state.grid_operational_pct
        self.state.gdp_trillion = 100.0 * grid_factor

        # Population impact (simple model: 1000 deaths per day per 10% grid loss)
        if days > 0:
            grid_loss = 1.0 - self.state.grid_operational_pct
            daily_deaths = int(grid_loss * 10000)  # Simple model
            self.state.total_deaths += daily_deaths * 7  # Weekly accumulation
            self.state.global_population = max(
                0,
                8_000_000_000 - self.state.total_deaths
            )
