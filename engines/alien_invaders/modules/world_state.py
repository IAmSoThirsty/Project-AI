#!/usr/bin/env python3
"""
World State Data Structures
Defines the complete state of the world at any point in the simulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Country:
    """Represents a sovereign nation."""

    name: str
    code: str  # ISO 3166-1 alpha-3
    population: int
    gdp_usd: float
    military_strength: float  # 0-1 normalized
    technology_level: float  # 0-1 normalized
    government_stability: float  # 0-1, 1 = stable
    public_morale: float  # 0-1, 1 = high morale
    resource_stockpiles: dict[str, float] = field(default_factory=dict)
    infrastructure_integrity: float = 1.0  # 0-1, 1 = fully intact
    alien_influence: float = 0.0  # 0-1, alien control level
    casualties: int = 0
    refugees: int = 0
    
    # Political alignments
    alliances: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    
    # Economic
    unemployment_rate: float = 0.05
    inflation_rate: float = 0.02
    trade_balance: float = 0.0
    
    # Social
    civil_unrest_level: float = 0.0  # 0-1
    religious_tension: float = 0.0  # 0-1
    cultural_cohesion: float = 0.8  # 0-1


@dataclass
class GlobalState:
    """Complete state of the world."""

    current_date: datetime
    day_number: int  # Days since simulation start
    
    # Countries
    countries: dict[str, Country] = field(default_factory=dict)
    
    # Global metrics
    global_population: int = 0
    global_gdp_usd: float = 0.0
    global_casualties: int = 0
    global_refugees: int = 0
    
    # Alien presence
    alien_ships_in_system: int = 0
    alien_ground_forces: int = 0
    planets_colonized: int = 0
    alien_resource_extraction: float = 0.0
    
    # Technology
    human_tech_level: float = 0.5  # 0-1 normalized
    alien_tech_level: float = 0.95  # 0-1 normalized
    
    # Communication
    alien_contact_established: bool = False
    negotiations_active: bool = False
    ceasefire_active: bool = False
    
    # AI governance
    ai_systems_operational: bool = True
    ai_alignment_score: float = 0.85
    ai_failure_count: int = 0
    
    # Environment
    global_temperature_change: float = 0.0  # Celsius
    atmospheric_composition: dict[str, float] = field(default_factory=dict)
    
    # Resources (planetary scale)
    remaining_resources: dict[str, float] = field(default_factory=dict)
    
    # Events log
    events_history: list[dict[str, Any]] = field(default_factory=list)
    
    def get_total_population(self) -> int:
        """Calculate total global population."""
        return sum(c.population for c in self.countries.values())
    
    def get_total_gdp(self) -> float:
        """Calculate total global GDP."""
        return sum(c.gdp_usd for c in self.countries.values())
    
    def get_average_morale(self) -> float:
        """Calculate weighted average global morale."""
        if not self.countries:
            return 0.0
        
        total_pop = self.get_total_population()
        if total_pop == 0:
            return 0.0
        
        weighted_morale = sum(
            c.public_morale * c.population for c in self.countries.values()
        )
        return weighted_morale / total_pop
    
    def get_alien_control_percentage(self) -> float:
        """Calculate percentage of world under alien control."""
        if not self.countries:
            return 0.0
        
        total_pop = self.get_total_population()
        if total_pop == 0:
            return 0.0
        
        controlled_pop = sum(
            c.population * c.alien_influence for c in self.countries.values()
        )
        return (controlled_pop / total_pop) * 100.0


@dataclass
class SimulationEvent:
    """Represents a discrete event in the simulation."""

    event_id: str
    timestamp: datetime
    day_number: int
    event_type: str
    severity: str  # low, medium, high, critical, catastrophic
    affected_countries: list[str]
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    consequences: list[str] = field(default_factory=list)
    causal_chain: list[str] = field(default_factory=list)  # Event IDs that led to this


@dataclass
class CausalLink:
    """Represents a cause-and-effect relationship between events."""

    source_event_id: str
    target_event_id: str
    source_domain: str  # political, economic, military, etc.
    target_domain: str
    strength: float  # 0-1, how strong the causal link is
    lag_days: int  # Time delay between cause and effect
    confidence: float  # 0-1, confidence in this causal relationship
    explanation: str


@dataclass
class ValidationState:
    """Tracks validation and consistency metrics."""

    timestamp: datetime
    is_valid: bool = True
    violations: list[str] = field(default_factory=list)
    
    # Conservation checks
    population_conserved: bool = True
    resources_conserved: bool = True
    energy_conserved: bool = True
    
    # Consistency checks
    causality_maintained: bool = True
    state_coherent: bool = True
    
    # Metrics
    population_delta: int = 0
    resource_delta: dict[str, float] = field(default_factory=dict)
