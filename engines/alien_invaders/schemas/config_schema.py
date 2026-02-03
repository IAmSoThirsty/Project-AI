#!/usr/bin/env python3
"""
Configuration Schema for Alien Invaders Contingency Plan Defense Engine
Defines validation schemas for all configuration parameters.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AlienThreatLevel(Enum):
    """Classification of alien threat levels."""

    RECONNAISSANCE = "reconnaissance"
    PROBE = "probe"
    INFILTRATION = "infiltration"
    INVASION = "invasion"
    OCCUPATION = "occupation"
    EXTINCTION = "extinction"


class TechnologyLevel(Enum):
    """Technology advancement levels."""

    PRIMITIVE = "primitive"  # Medieval/Industrial
    CONTEMPORARY = "contemporary"  # Current Earth
    NEAR_FUTURE = "near_future"  # 50-100 years ahead
    ADVANCED = "advanced"  # 100-500 years ahead
    SUPERIOR = "superior"  # 500-1000 years ahead
    GODLIKE = "godlike"  # Beyond comprehension


@dataclass
class WorldConfig:
    """Configuration for world state initialization."""

    start_year: int = 2026
    simulation_duration_years: int = 5
    time_step_days: int = 30  # Monthly simulation by default
    num_countries: int = 195  # UN member states
    global_population: int = 8_000_000_000
    global_gdp_usd: float = 100_000_000_000_000.0  # 100 trillion
    enable_climate_effects: bool = True
    enable_economic_propagation: bool = True
    enable_political_instability: bool = True
    enable_religious_tensions: bool = True


@dataclass
class AlienConfig:
    """Configuration for alien adversary characteristics."""

    initial_threat_level: AlienThreatLevel = AlienThreatLevel.RECONNAISSANCE
    technology_level: TechnologyLevel = TechnologyLevel.SUPERIOR
    initial_ship_count: int = 1
    invasion_probability_per_year: float = 0.15
    technology_advantage_multiplier: float = 100.0  # How much more advanced
    resource_extraction_rate: float = 0.05  # 5% of planetary resources per year
    hostile_intent: float = 0.7  # 0-1 scale, 1 = total annihilation
    adaptation_rate: float = 0.1  # How quickly they adapt to human countermeasures
    communication_attempts: bool = True
    negotiation_openness: float = 0.2  # Willingness to negotiate


@dataclass
class AIGovernanceConfig:
    """Configuration for AI governance and decision-making layer."""

    enable_ai_governance: bool = True
    ai_failure_probability: float = 0.05  # 5% chance per year
    ai_alignment_score: float = 0.85  # How well AI is aligned with human values
    ai_decision_weight: float = 0.6  # Weight of AI decisions vs human
    enable_ai_failsafes: bool = True
    human_override_capability: bool = True
    catastrophic_failure_threshold: float = 0.95  # Risk threshold for intervention


@dataclass
class ValidationConfig:
    """Configuration for state validation and consistency enforcement."""

    enable_strict_validation: bool = True
    conservation_tolerance: float = 0.01  # 1% tolerance for resource conservation
    causality_enforcement: bool = True
    deterministic_replay: bool = True
    random_seed: int | None = None  # For reproducibility
    save_state_frequency: int = 30  # Save every 30 days


@dataclass
class ArtifactConfig:
    """Configuration for artifact generation."""

    generate_monthly_reports: bool = True
    generate_annual_reports: bool = True
    generate_postmortem: bool = True
    output_format: str = "json"  # json, yaml, or both
    include_raw_data: bool = True
    include_visualizations: bool = False  # Requires matplotlib
    artifact_dir: str = "engines/alien_invaders/artifacts"


@dataclass
class SimulationConfig:
    """Master configuration for the entire simulation."""

    world: WorldConfig = field(default_factory=WorldConfig)
    alien: AlienConfig = field(default_factory=AlienConfig)
    ai_governance: AIGovernanceConfig = field(default_factory=AIGovernanceConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    artifacts: ArtifactConfig = field(default_factory=ArtifactConfig)
    
    # Scenario presets
    scenario: str = "standard"  # standard, aggressive, peaceful, extinction
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "world": {
                "start_year": self.world.start_year,
                "simulation_duration_years": self.world.simulation_duration_years,
                "time_step_days": self.world.time_step_days,
                "num_countries": self.world.num_countries,
                "global_population": self.world.global_population,
                "global_gdp_usd": self.world.global_gdp_usd,
                "enable_climate_effects": self.world.enable_climate_effects,
                "enable_economic_propagation": self.world.enable_economic_propagation,
                "enable_political_instability": self.world.enable_political_instability,
                "enable_religious_tensions": self.world.enable_religious_tensions,
            },
            "alien": {
                "initial_threat_level": self.alien.initial_threat_level.value,
                "technology_level": self.alien.technology_level.value,
                "initial_ship_count": self.alien.initial_ship_count,
                "invasion_probability_per_year": self.alien.invasion_probability_per_year,
                "technology_advantage_multiplier": self.alien.technology_advantage_multiplier,
                "resource_extraction_rate": self.alien.resource_extraction_rate,
                "hostile_intent": self.alien.hostile_intent,
                "adaptation_rate": self.alien.adaptation_rate,
                "communication_attempts": self.alien.communication_attempts,
                "negotiation_openness": self.alien.negotiation_openness,
            },
            "ai_governance": {
                "enable_ai_governance": self.ai_governance.enable_ai_governance,
                "ai_failure_probability": self.ai_governance.ai_failure_probability,
                "ai_alignment_score": self.ai_governance.ai_alignment_score,
                "ai_decision_weight": self.ai_governance.ai_decision_weight,
                "enable_ai_failsafes": self.ai_governance.enable_ai_failsafes,
                "human_override_capability": self.ai_governance.human_override_capability,
                "catastrophic_failure_threshold": self.ai_governance.catastrophic_failure_threshold,
            },
            "validation": {
                "enable_strict_validation": self.validation.enable_strict_validation,
                "conservation_tolerance": self.validation.conservation_tolerance,
                "causality_enforcement": self.validation.causality_enforcement,
                "deterministic_replay": self.validation.deterministic_replay,
                "random_seed": self.validation.random_seed,
                "save_state_frequency": self.validation.save_state_frequency,
            },
            "artifacts": {
                "generate_monthly_reports": self.artifacts.generate_monthly_reports,
                "generate_annual_reports": self.artifacts.generate_annual_reports,
                "generate_postmortem": self.artifacts.generate_postmortem,
                "output_format": self.artifacts.output_format,
                "include_raw_data": self.artifacts.include_raw_data,
                "include_visualizations": self.artifacts.include_visualizations,
                "artifact_dir": self.artifacts.artifact_dir,
            },
            "scenario": self.scenario,
        }


def load_scenario_preset(scenario_name: str) -> SimulationConfig:
    """
    Load a predefined scenario configuration.
    
    Args:
        scenario_name: Name of the scenario preset
        
    Returns:
        SimulationConfig with preset values
    """
    config = SimulationConfig()
    
    if scenario_name == "aggressive":
        # High threat, immediate invasion
        config.alien.initial_threat_level = AlienThreatLevel.INVASION
        config.alien.invasion_probability_per_year = 0.95
        config.alien.hostile_intent = 0.95
        config.alien.negotiation_openness = 0.05
        config.alien.resource_extraction_rate = 0.15
        
    elif scenario_name == "peaceful":
        # Low threat, scientific interest
        config.alien.initial_threat_level = AlienThreatLevel.RECONNAISSANCE
        config.alien.invasion_probability_per_year = 0.05
        config.alien.hostile_intent = 0.2
        config.alien.negotiation_openness = 0.8
        config.alien.resource_extraction_rate = 0.01
        config.alien.communication_attempts = True
        
    elif scenario_name == "extinction":
        # Apocalyptic scenario
        config.alien.initial_threat_level = AlienThreatLevel.EXTINCTION
        config.alien.technology_level = TechnologyLevel.GODLIKE
        config.alien.invasion_probability_per_year = 1.0
        config.alien.hostile_intent = 1.0
        config.alien.negotiation_openness = 0.0
        config.alien.resource_extraction_rate = 0.5
        config.alien.technology_advantage_multiplier = 10000.0
        
    config.scenario = scenario_name
    return config
