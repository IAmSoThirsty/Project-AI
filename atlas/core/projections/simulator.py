"""
Projections Module for PROJECT ATLAS

Implements timeline projection engine with deterministic seeds, applies drivers
for state evolution, generates multiple scenarios with full replayability.

Production-grade with full error handling, logging, and audit trail integration.
"""

import hashlib
import logging
import random
from datetime import datetime, timedelta
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, AuditTrail, get_audit_trail
from atlas.config.loader import ConfigLoader, get_config_loader
from atlas.schemas.validator import SchemaValidator, get_schema_validator

logger = logging.getLogger(__name__)


class ProjectionError(Exception):
    """Raised when projection operations fail."""
    pass


class SimulationError(Exception):
    """Raised when simulation fails."""
    pass


class ProjectionSimulator:
    """
    Production-grade timeline projection simulator for PROJECT ATLAS.
    
    Implements deterministic timeline generation using seeded RNG, applies
    drivers for state evolution, generates multiple scenarios with audit trail.
    """

    def __init__(self,
                 config_loader: ConfigLoader | None = None,
                 schema_validator: SchemaValidator | None = None,
                 audit_trail: AuditTrail | None = None):
        """
        Initialize projection simulator.
        
        Args:
            config_loader: Configuration loader (uses global if None)
            schema_validator: Schema validator (uses global if None)
            audit_trail: Audit trail (uses global if None)
        """
        self.config = config_loader or get_config_loader()
        self.validator = schema_validator or get_schema_validator()
        self.audit = audit_trail or get_audit_trail()

        # Load configurations
        self.seeds_config = self.config.get("seeds")
        self.drivers_config = self.config.get("drivers")
        self.thresholds = self.config.get("thresholds")

        # Extract timeline seeds
        self.timeline_seeds = self.seeds_config.get("timeline_seeds", {})
        self.scenario_seeds = self.seeds_config.get("scenario_seeds", {})
        self.seed_usage_rules = self.seeds_config.get("usage_rules", {})

        # Extract driver configurations
        self.projection_drivers = self.drivers_config.get("projection_drivers", {})
        self.scenario_drivers = self.drivers_config.get("scenario_drivers", {})
        self.temporal_drivers = self.drivers_config.get("temporal_drivers", {})

        # Track statistics
        self._stats = {
            "projections_generated": 0,
            "timelines_created": 0,
            "scenarios_generated": 0,
            "determinism_verified": 0
        }

        logger.info("ProjectionSimulator initialized successfully")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="projection_simulator_initialized",
            actor="PROJECTIONS_MODULE",
            details={
                "seeds_loaded": len(self.timeline_seeds),
                "config_hashes": self.config.get_all_hashes()
            }
        )

    def generate_projection(self,
                           world_state: dict[str, Any],
                           stack: str,
                           horizon_days: int,
                           seed_variant: str = "default",
                           scenarios: list[str] | None = None) -> dict[str, Any]:
        """
        Generate timeline projection from current world state.
        
        Args:
            world_state: Current world state object
            stack: Timeline stack (TS-0, TS-1, TS-2, TS-3)
            horizon_days: Projection horizon in days
            seed_variant: Seed variant to use (default, optimistic, pessimistic, etc.)
            scenarios: List of scenario types to generate (if None, generates expected only)
            
        Returns:
            ProjectionPack object with multiple scenarios
            
        Raises:
            ProjectionError: If projection generation fails
        """
        try:
            self._stats["projections_generated"] += 1

            # Get appropriate seed
            seed_string = self._get_seed(stack, seed_variant)

            # Initialize deterministic RNG
            rng = self._initialize_rng(seed_string)

            # Log projection start
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="generate_projection_start",
                actor="PROJECTIONS_MODULE",
                details={
                    "stack": stack,
                    "horizon_days": horizon_days,
                    "seed_variant": seed_variant,
                    "seed_hash": hashlib.sha256(seed_string.encode()).hexdigest()[:16]
                },
                stack=stack
            )

            # Generate scenarios
            scenario_types = scenarios or ["expected"]
            projection_scenarios = []

            for scenario_type in scenario_types:
                scenario = self._generate_scenario(
                    world_state,
                    stack,
                    horizon_days,
                    scenario_type,
                    rng
                )
                projection_scenarios.append(scenario)
                self._stats["scenarios_generated"] += 1

            # Create projection pack
            projection_pack = {
                "id": f"PROJ-{stack}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                "stack": stack,
                "base_world_state_id": world_state.get("id", "unknown"),
                "projection_start": datetime.utcnow().isoformat(),
                "horizon_days": horizon_days,
                "seed_variant": seed_variant,
                "seed_used": seed_string,
                "scenarios": projection_scenarios,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "projection_version": "1.0.0",
                    "deterministic": True,
                    "replayable": True,
                    "config_hashes": self.config.get_all_hashes()
                }
            }

            # Validate against schema
            self.validator.validate_projection_pack(projection_pack, strict=True)

            # Log success
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="generate_projection_success",
                actor="PROJECTIONS_MODULE",
                details={
                    "projection_id": projection_pack["id"],
                    "scenarios_count": len(projection_scenarios),
                    "stack": stack
                },
                stack=stack
            )

            return projection_pack

        except Exception as e:
            logger.error("Failed to generate projection: %s", e)

            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.HIGH_PRIORITY,
                operation="generate_projection_failed",
                actor="PROJECTIONS_MODULE",
                details={"error": str(e), "stack": stack},
                stack=stack
            )

            raise ProjectionError(f"Failed to generate projection: {e}") from e

    def replay_projection(self,
                         world_state: dict[str, Any],
                         projection_pack: dict[str, Any]) -> dict[str, Any]:
        """
        Replay a projection using its recorded seed for verification.
        
        Args:
            world_state: World state used for original projection
            projection_pack: Original projection pack
            
        Returns:
            Replayed projection pack
            
        Raises:
            ProjectionError: If replay fails or results don't match
        """
        try:
            stack = projection_pack["stack"]
            horizon_days = projection_pack["horizon_days"]
            seed_variant = projection_pack["seed_variant"]

            # Generate new projection with same parameters
            replayed = self.generate_projection(
                world_state,
                stack,
                horizon_days,
                seed_variant,
                scenarios=[s["type"] for s in projection_pack["scenarios"]]
            )

            # Verify determinism - results should be identical
            self._verify_determinism(projection_pack, replayed)

            self._stats["determinism_verified"] += 1

            self.audit.log_event(
                category=AuditCategory.VALIDATION,
                level=AuditLevel.STANDARD,
                operation="projection_replay_verified",
                actor="PROJECTIONS_MODULE",
                details={
                    "original_id": projection_pack["id"],
                    "replayed_id": replayed["id"],
                    "determinism_verified": True
                },
                stack=stack
            )

            return replayed

        except Exception as e:
            logger.error("Failed to replay projection: %s", e)
            raise ProjectionError(f"Failed to replay projection: {e}") from e

    def _generate_scenario(self,
                          world_state: dict[str, Any],
                          stack: str,
                          horizon_days: int,
                          scenario_type: str,
                          rng: random.Random) -> dict[str, Any]:
        """
        Generate a single scenario timeline.
        
        Args:
            world_state: Current world state
            stack: Timeline stack
            horizon_days: Projection horizon
            scenario_type: Scenario type (expected, best_case, worst_case)
            rng: Seeded random number generator
            
        Returns:
            Scenario object with timeline
        """
        self._stats["timelines_created"] += 1

        # Get scenario driver configuration
        scenario_config = self.scenario_drivers.get(scenario_type, self.scenario_drivers.get("expected", {}))
        multipliers = scenario_config.get("multipliers", {})

        # Generate timeline states
        timeline = []
        current_state = self._copy_world_state(world_state)

        # Number of time steps (one per day for simplicity)
        time_steps = horizon_days

        for day in range(time_steps):
            # Calculate projection date
            projection_date = datetime.fromisoformat(current_state.get("timestamp", datetime.utcnow().isoformat()))
            projection_date = projection_date + timedelta(days=day + 1)

            # Evolve state using drivers
            next_state = self._evolve_state(
                current_state,
                timeline,
                multipliers,
                rng
            )

            next_state["timestamp"] = projection_date.isoformat()
            next_state["day"] = day + 1

            timeline.append(next_state)
            current_state = next_state

        # Create scenario object
        scenario = {
            "type": scenario_type,
            "probability": scenario_config.get("probability_weight", 0.0),
            "timeline": timeline,
            "summary": {
                "start_date": world_state.get("timestamp"),
                "end_date": timeline[-1]["timestamp"] if timeline else None,
                "time_steps": len(timeline),
                "final_state": timeline[-1] if timeline else None
            }
        }

        return scenario

    def _evolve_state(self,
                     current_state: dict[str, Any],
                     history: list[dict[str, Any]],
                     scenario_multipliers: dict[str, float],
                     rng: random.Random) -> dict[str, Any]:
        """
        Evolve world state by one time step using drivers.
        
        Args:
            current_state: Current world state
            history: Historical states
            scenario_multipliers: Scenario-specific multipliers
            rng: Seeded RNG
            
        Returns:
            Next world state
        """
        next_state = self._copy_world_state(current_state)

        # Apply temporal drivers
        self._apply_temporal_drivers(next_state, current_state, history)

        # Apply projection drivers
        self._apply_projection_drivers(next_state, current_state, history, rng)

        # Apply scenario multipliers
        self._apply_scenario_multipliers(next_state, scenario_multipliers)

        # Apply constraints and normalization
        self._normalize_state(next_state)

        return next_state

    def _apply_temporal_drivers(self,
                               next_state: dict[str, Any],
                               current_state: dict[str, Any],
                               history: list[dict[str, Any]]) -> None:
        """Apply temporal dynamics (decay, growth, oscillation)."""
        for entity in next_state.get("entities", []):
            current_influence = entity.get("influence", 0.5)

            # Apply decay
            decay_config = self.temporal_drivers.get("decay", {})
            decay_rate = decay_config.get("decay_rate", 0.001)
            influence_after_decay = current_influence * (1 - decay_rate)

            # Apply growth
            growth_config = self.temporal_drivers.get("growth", {})
            growth_rate = growth_config.get("growth_rate", 0.002)
            growth_factor = entity.get("growth_factor", 1.0)
            saturation = growth_config.get("saturation_limit", 0.95)

            influence_after_growth = influence_after_decay * (1 + growth_rate * growth_factor)
            influence_after_growth = min(influence_after_growth, saturation)

            entity["influence"] = influence_after_growth

    def _apply_projection_drivers(self,
                                 next_state: dict[str, Any],
                                 current_state: dict[str, Any],
                                 history: list[dict[str, Any]],
                                 rng: random.Random) -> None:
        """Apply projection drivers (momentum, volatility, network effects)."""
        for entity in next_state.get("entities", []):
            current_influence = entity.get("influence", 0.5)

            # Get previous influence
            prev_influence = current_influence
            if history:
                prev_entity = next((e for e in history[-1].get("entities", []) if e["id"] == entity["id"]), None)
                if prev_entity:
                    prev_influence = prev_entity.get("influence", 0.5)

            # Apply momentum
            momentum_config = self.projection_drivers.get("momentum", {})
            velocity_factor = momentum_config.get("velocity_factor", 0.1)
            momentum = (current_influence - prev_influence) * velocity_factor

            # Apply volatility (add randomness)
            volatility_config = self.projection_drivers.get("volatility", {})
            volatility_multiplier = volatility_config.get("volatility_multiplier", 1.5)

            # Calculate historical volatility
            if len(history) >= 2:
                recent_influences = [current_influence]
                for state in history[-10:]:  # Look back 10 steps
                    hist_entity = next((e for e in state.get("entities", []) if e["id"] == entity["id"]), None)
                    if hist_entity:
                        recent_influences.append(hist_entity.get("influence", 0.5))

                if len(recent_influences) > 1:
                    mean = sum(recent_influences) / len(recent_influences)
                    variance = sum((x - mean) ** 2 for x in recent_influences) / len(recent_influences)
                    stddev = variance ** 0.5
                    volatility = stddev * volatility_multiplier * rng.gauss(0, 1)
                else:
                    volatility = 0.0
            else:
                volatility = 0.0

            # Apply changes
            new_influence = current_influence + momentum + volatility

            entity["influence"] = new_influence

    def _apply_scenario_multipliers(self,
                                   state: dict[str, Any],
                                   multipliers: dict[str, float]) -> None:
        """Apply scenario-specific multipliers to state."""
        for entity in state.get("entities", []):
            # Apply multipliers to relevant attributes
            for driver_name, multiplier in multipliers.items():
                # Map driver names to entity attributes
                if driver_name == "economic_power" or driver_name == "political_influence" or driver_name == "social_cohesion":
                    entity["influence"] *= multiplier

    def _normalize_state(self, state: dict[str, Any]) -> None:
        """Normalize state values to valid ranges."""
        for entity in state.get("entities", []):
            # Clamp influence to [0, 1]
            entity["influence"] = max(0.0, min(1.0, entity.get("influence", 0.5)))

    def _copy_world_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create a deep copy of world state."""
        import copy
        return copy.deepcopy(state)

    def _get_seed(self, stack: str, variant: str) -> str:
        """
        Get deterministic seed for timeline stack and variant.
        
        Args:
            stack: Timeline stack identifier
            variant: Seed variant
            
        Returns:
            Seed string
            
        Raises:
            ProjectionError: If seed not found
        """
        # Map stack to timeline seed key
        stack_key = stack.replace("-", "")  # TS-0 -> TS0

        if stack_key not in self.timeline_seeds:
            raise ProjectionError(f"No seeds configured for stack: {stack}")

        seeds = self.timeline_seeds[stack_key].get("seeds", {})

        if variant not in seeds:
            logger.warning("Seed variant %s not found for %s, using default", variant, stack)
            variant = "default"

        seed_string = seeds.get(variant)

        if not seed_string:
            raise ProjectionError(f"Seed not found for {stack}/{variant}")

        return seed_string

    def _initialize_rng(self, seed_string: str) -> random.Random:
        """
        Initialize deterministic random number generator from seed.
        
        Args:
            seed_string: Seed string
            
        Returns:
            Seeded Random instance
        """
        # Convert seed string to integer for RNG
        seed_hash = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()
        seed_int = int(seed_hash[:16], 16)  # Use first 64 bits

        rng = random.Random(seed_int)

        # Log seed usage
        self.audit.log_event(
            category=AuditCategory.OPERATION,
            level=AuditLevel.INFORMATIONAL,
            operation="rng_initialized",
            actor="PROJECTIONS_MODULE",
            details={
                "seed_string": seed_string,
                "seed_hash": seed_hash[:16]
            }
        )

        return rng

    def _verify_determinism(self,
                           original: dict[str, Any],
                           replayed: dict[str, Any]) -> None:
        """
        Verify that replayed projection matches original.
        
        Args:
            original: Original projection pack
            replayed: Replayed projection pack
            
        Raises:
            SimulationError: If results don't match
        """
        # Compare key fields
        if original["stack"] != replayed["stack"]:
            raise SimulationError("Stack mismatch in replay")

        if original["horizon_days"] != replayed["horizon_days"]:
            raise SimulationError("Horizon mismatch in replay")

        if len(original["scenarios"]) != len(replayed["scenarios"]):
            raise SimulationError("Scenario count mismatch in replay")

        # Compare scenario timelines
        for i, (orig_scenario, replay_scenario) in enumerate(zip(original["scenarios"], replayed["scenarios"])):
            if len(orig_scenario["timeline"]) != len(replay_scenario["timeline"]):
                raise SimulationError(f"Timeline length mismatch in scenario {i}")

            # Compare state values (with tolerance for floating point)
            tolerance = 1e-10
            for j, (orig_state, replay_state) in enumerate(zip(orig_scenario["timeline"], replay_scenario["timeline"])):
                for entity_orig, entity_replay in zip(orig_state.get("entities", []), replay_state.get("entities", [])):
                    orig_influence = entity_orig.get("influence", 0)
                    replay_influence = entity_replay.get("influence", 0)

                    if abs(orig_influence - replay_influence) > tolerance:
                        raise SimulationError(
                            f"Determinism violation: influence mismatch at scenario {i}, step {j}, "
                            f"entity {entity_orig.get('id')}: {orig_influence} != {replay_influence}"
                        )

        logger.info("Determinism verification passed")

    def get_statistics(self) -> dict[str, Any]:
        """Get projection statistics."""
        return dict(self._stats)

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            "projections_generated": 0,
            "timelines_created": 0,
            "scenarios_generated": 0,
            "determinism_verified": 0
        }


if __name__ == "__main__":
    # Test projection simulator
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        simulator = ProjectionSimulator()

        # Test world state
        world_state = {
            "id": "WS-TEST-001",
            "timestamp": datetime.utcnow().isoformat(),
            "entities": [
                {
                    "id": "ORG-001",
                    "name": "Organization Alpha",
                    "influence": 0.75,
                    "growth_factor": 1.2
                },
                {
                    "id": "ORG-002",
                    "name": "Organization Beta",
                    "influence": 0.65,
                    "growth_factor": 0.9
                }
            ]
        }

        # Generate projection
        projection = simulator.generate_projection(
            world_state=world_state,
            stack="TS-1",
            horizon_days=30,
            seed_variant="default",
            scenarios=["expected", "optimistic", "pessimistic"]
        )

        print("Projection Generated Successfully:")
        print(f"  ID: {projection['id']}")
        print(f"  Stack: {projection['stack']}")
        print(f"  Horizon: {projection['horizon_days']} days")
        print(f"  Scenarios: {len(projection['scenarios'])}")

        for scenario in projection['scenarios']:
            print(f"\n  Scenario: {scenario['type']}")
            print(f"    Timeline Steps: {len(scenario['timeline'])}")
            print(f"    Probability: {scenario['probability']:.2f}")

            if scenario['timeline']:
                final_state = scenario['timeline'][-1]
                print(f"    Final State (day {final_state.get('day', 0)}):")
                for entity in final_state.get('entities', []):
                    print(f"      {entity['id']}: influence = {entity['influence']:.4f}")

        # Test replay for determinism
        print("\nTesting Determinism (replay)...")
        replayed = simulator.replay_projection(world_state, projection)
        print("✓ Determinism verified - replay matches original")

        # Print statistics
        print("\nStatistics:")
        import json
        print(json.dumps(simulator.get_statistics(), indent=2))

    except Exception as e:
        logger.error("Test failed: %s", e, exc_info=True)
        raise
