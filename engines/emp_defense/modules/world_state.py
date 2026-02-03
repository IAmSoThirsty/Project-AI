"""
Minimal world state for EMP Defense Engine.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class WorldState:
    """
    Minimal world state tracking 5 key metrics.
    
    Examples:
        >>> state = WorldState()
        >>> state.global_population
        8000000000
        >>> state.grid_operational_pct
        1.0
    """
    # Core metrics
    simulation_day: int = 0
    global_population: int = 8_000_000_000
    total_deaths: int = 0
    grid_operational_pct: float = 1.0  # 1.0 = 100% operational
    gdp_trillion: float = 100.0
    
    # Simple event tracking
    major_events: list[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.major_events is None:
            self.major_events = []
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
            
        Examples:
            >>> state = WorldState()
            >>> d = state.to_dict()
            >>> d['global_population']
            8000000000
        """
        return {
            "simulation_day": self.simulation_day,
            "global_population": self.global_population,
            "total_deaths": self.total_deaths,
            "grid_operational_pct": self.grid_operational_pct,
            "gdp_trillion": self.gdp_trillion,
            "major_events": self.major_events,
        }
