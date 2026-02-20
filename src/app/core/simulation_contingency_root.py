#!/usr/bin/env python3
"""
Simulation Contingency Root - Contract Interface for Simulation Systems
Project-AI God-Tier Global Scenario Engine

This module defines the contract interface that all simulation and contingency
systems must implement. It provides a unified API for:
- Scenario generation and simulation
- Risk detection and threshold monitoring
- Crisis alert generation
- Causal analysis and explainability

All simulation systems must register with this root contract to ensure
consistent behavior and integration with the broader Project-AI ecosystem.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RiskDomain(Enum):
    """Enumeration of risk domains tracked by simulation systems."""

    ECONOMIC = "economic"
    INFLATION = "inflation"
    UNEMPLOYMENT = "unemployment"
    CIVIL_UNREST = "civil_unrest"
    CLIMATE = "climate"
    PANDEMIC = "pandemic"
    BIOSECURITY = "biosecurity"
    MIGRATION = "migration"
    TRADE = "trade"
    MILITARY = "military"
    CYBERSECURITY = "cybersecurity"
    POLITICAL = "political"
    TERRORISM = "terrorism"
    SUPPLY_CHAIN = "supply_chain"
    FOOD = "food"
    WATER = "water"
    ENERGY = "energy"
    NUCLEAR = "nuclear"
    SPACE = "space"
    FINANCIAL = "financial"


class AlertLevel(Enum):
    """Alert severity levels for crisis scenarios."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


@dataclass
class ThresholdEvent:
    """Represents a detected threshold exceedance event."""

    event_id: str
    timestamp: datetime
    country: str
    domain: RiskDomain
    metric_name: str
    value: float
    threshold: float
    severity: float  # 0-1 scale
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalLink:
    """Represents a causal relationship between events or domains."""

    source: str  # Source event/domain
    target: str  # Target event/domain
    strength: float  # 0-1 correlation/causation strength
    lag_years: float  # Time lag in years
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0  # Statistical confidence


@dataclass
class ScenarioProjection:
    """Represents a future scenario projection."""

    scenario_id: str
    year: int
    likelihood: float  # 0-1 probability
    title: str
    description: str
    trigger_events: list[ThresholdEvent]
    causal_chain: list[CausalLink]
    affected_countries: set[str] = field(default_factory=set)
    impact_domains: set[RiskDomain] = field(default_factory=set)
    severity: AlertLevel = AlertLevel.MEDIUM
    mitigation_strategies: list[str] = field(default_factory=list)


@dataclass
class CrisisAlert:
    """Represents a high-probability crisis alert."""

    alert_id: str
    timestamp: datetime
    scenario: ScenarioProjection
    evidence: list[ThresholdEvent]
    causal_activation: list[CausalLink]
    risk_score: float  # 0-100
    explainability: str  # Human-readable explanation
    recommended_actions: list[str] = field(default_factory=list)


class SimulationSystem(ABC):
    """
    Abstract base class for all simulation and contingency systems.

    This contract ensures that all simulation systems provide consistent APIs
    for data loading, event detection, scenario simulation, and alert generation.

    All implementations must be production-ready with:
    - Full error handling and logging
    - Data persistence and state management
    - Extensibility for new data sources
    - Complete documentation
    """

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the simulation system.

        Returns:
            bool: True if initialization successful, False otherwise
        """

    @abstractmethod
    def load_historical_data(
        self,
        start_year: int,
        end_year: int,
        domains: list[RiskDomain] | None = None,
        countries: list[str] | None = None,
    ) -> bool:
        """
        Load historical data for specified time range and domains.

        Args:
            start_year: Start year for data loading
            end_year: End year for data loading
            domains: List of risk domains to load (None = all)
            countries: List of countries to load (None = all)

        Returns:
            bool: True if data loaded successfully
        """

    @abstractmethod
    def detect_threshold_events(self, year: int, domains: list[RiskDomain] | None = None) -> list[ThresholdEvent]:
        """
        Detect threshold exceedance events for a given year.

        Args:
            year: Year to analyze
            domains: Domains to analyze (None = all)

        Returns:
            List of detected threshold events
        """

    @abstractmethod
    def build_causal_model(self, historical_events: list[ThresholdEvent]) -> list[CausalLink]:
        """
        Build causal relationships from historical event data.

        Args:
            historical_events: Historical threshold events

        Returns:
            List of causal links between domains/events
        """

    @abstractmethod
    def simulate_scenarios(self, projection_years: int = 10, num_simulations: int = 1000) -> list[ScenarioProjection]:
        """
        Run probabilistic scenario simulations for future years.

        Args:
            projection_years: Number of years to project forward
            num_simulations: Number of Monte Carlo simulations

        Returns:
            List of scenario projections with likelihoods
        """

    @abstractmethod
    def generate_alerts(self, scenarios: list[ScenarioProjection], threshold: float = 0.7) -> list[CrisisAlert]:
        """
        Generate crisis alerts for high-probability scenarios.

        Args:
            scenarios: List of scenario projections
            threshold: Minimum likelihood threshold for alerts

        Returns:
            List of crisis alerts
        """

    @abstractmethod
    def get_explainability(self, scenario: ScenarioProjection) -> str:
        """
        Generate human-readable explanation for a scenario.

        Args:
            scenario: Scenario to explain

        Returns:
            Detailed explanation of causal chain and evidence
        """

    @abstractmethod
    def persist_state(self) -> bool:
        """
        Persist current simulation state to storage.

        Returns:
            bool: True if state saved successfully
        """

    @abstractmethod
    def validate_data_quality(self) -> dict[str, Any]:
        """
        Validate quality of loaded data.

        Returns:
            Dictionary with validation metrics and issues
        """


class SimulationRegistry:
    """
    Registry for managing simulation system implementations.

    This class maintains a registry of all simulation systems and provides
    a unified interface for accessing them.

    INTEGRATION POINT C: Read-Only Projection → Mandatory
    - Registry enforces projection-only access by default
    - Any engine requesting mutable access must:
      1. Be inside the Monolith
      2. Pass law evaluation
      3. Generate an accountability record
    """

    _systems: dict[str, SimulationSystem] = {}
    _projection_mode: bool = True  # Enforce read-only by default
    _monolith_authority: Any = None  # Reference to PlanetaryDefenseMonolith

    @classmethod
    def set_monolith_authority(cls, monolith: Any) -> None:
        """
        Set the monolith authority for access control.

        Args:
            monolith: PlanetaryDefenseMonolith instance
        """
        cls._monolith_authority = monolith
        logger.info("SimulationRegistry: Monolith authority established")

    @classmethod
    def enable_projection_mode(cls, enabled: bool = True) -> None:
        """
        Enable or disable projection mode enforcement.

        Args:
            enabled: If True, enforce read-only access
        """
        cls._projection_mode = enabled
        logger.info(
            "SimulationRegistry: Projection mode %s",
            "ENABLED" if enabled else "DISABLED",
        )

    @classmethod
    def register(cls, name: str, system: SimulationSystem, from_monolith: bool = False) -> None:
        """
        Register a simulation system.

        Args:
            name: Unique name for the system
            system: SimulationSystem implementation
            from_monolith: If True, bypass projection mode check
        """
        # Check if mutable access is allowed
        if cls._projection_mode and not from_monolith:
            if cls._monolith_authority is not None:
                # Request authorization from monolith
                from engines.alien_invaders.modules.planetary_defense_monolith import (
                    RegistryAccessRequest,
                )

                access_request = RegistryAccessRequest(
                    requestor="SimulationRegistry",
                    access_type="write",
                    target=f"register_{name}",
                    context={"from_monolith": from_monolith},
                )

                allowed, reason = cls._monolith_authority.authorize_registry_access(access_request)

                if not allowed:
                    logger.error("Registration of %s DENIED: %s", name, reason)
                    raise PermissionError(f"Registry registration denied: {reason}")

        if name in cls._systems:
            logger.warning("Overwriting existing system: %s", name)
        cls._systems[name] = system
        logger.info("Registered simulation system: %s", name)

    @classmethod
    def get(cls, name: str, mutable: bool = False, from_monolith: bool = False) -> SimulationSystem | None:
        """
        Retrieve a registered simulation system.

        In projection mode, returns a read-only view by default.
        Mutable access requires monolith authorization.

        Args:
            name: Name of the system
            mutable: If True, request mutable access (requires authorization)
            from_monolith: If True, bypass projection mode check

        Returns:
            SimulationSystem or None if not found
        """
        system = cls._systems.get(name)

        if system is None:
            return None

        # Check if mutable access is requested
        if mutable and cls._projection_mode and not from_monolith:
            if cls._monolith_authority is not None:
                # Request authorization from monolith
                from engines.alien_invaders.modules.planetary_defense_monolith import (
                    RegistryAccessRequest,
                )

                access_request = RegistryAccessRequest(
                    requestor="SimulationRegistry.get",
                    access_type="write",
                    target=f"get_{name}_mutable",
                    context={"from_monolith": from_monolith},
                )

                allowed, reason = cls._monolith_authority.authorize_registry_access(access_request)

                if not allowed:
                    logger.warning("Mutable access to %s DENIED: %s", name, reason)
                    # Return None to prevent mutable access
                    return None

        # Return the system (read-only or mutable based on authorization)
        return system

    @classmethod
    def list_systems(cls) -> list[str]:
        """
        List all registered simulation systems.

        Returns:
            List of system names
        """
        return list(cls._systems.keys())

    @classmethod
    def unregister(cls, name: str, from_monolith: bool = False) -> bool:
        """
        Unregister a simulation system.

        Args:
            name: Name of the system to remove
            from_monolith: If True, bypass projection mode check

        Returns:
            bool: True if system was removed
        """
        # Check if mutable access is allowed
        if cls._projection_mode and not from_monolith:
            if cls._monolith_authority is not None:
                # Request authorization from monolith
                from engines.alien_invaders.modules.planetary_defense_monolith import (
                    RegistryAccessRequest,
                )

                access_request = RegistryAccessRequest(
                    requestor="SimulationRegistry.unregister",
                    access_type="write",
                    target=f"unregister_{name}",
                    context={"from_monolith": from_monolith},
                )

                allowed, reason = cls._monolith_authority.authorize_registry_access(access_request)

                if not allowed:
                    logger.error("Unregistration of %s DENIED: %s", name, reason)
                    return False

        if name in cls._systems:
            del cls._systems[name]
            logger.info("Unregistered simulation system: %s", name)
            return True
        return False
