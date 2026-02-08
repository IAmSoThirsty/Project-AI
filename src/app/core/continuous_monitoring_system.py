"""Continuous 24/7 Monitoring System with Secure Storage.

This module extends the Global Intelligence Library with:
- 24/7 continuous monitoring threads
- Secure encrypted storage
- Automatic labeling and organization
- Global geographic coverage tracking
- Real-time data collection and analysis
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from app.core.global_intelligence_library import (
    ChangeLevel,
    IntelligenceAgent,
    IntelligenceDomain,
    IntelligenceReport,
    MonitoringStatus,
)

logger = logging.getLogger(__name__)


class GlobalRegion(Enum):
    """Global geographic regions for coverage."""

    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"
    ASIA_PACIFIC = "asia_pacific"
    CENTRAL_ASIA = "central_asia"
    OCEANIA = "oceania"


class DataClassification(Enum):
    """Data classification levels for secure storage."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


@dataclass
class GeographicCoverage:
    """Geographic coverage information for an agent."""

    region: GlobalRegion
    countries: list[str] = field(default_factory=list)
    coordinates: tuple[float, float] | None = None  # (latitude, longitude)
    timezone: str = "UTC"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "region": self.region.value,
            "countries": self.countries,
            "coordinates": self.coordinates,
            "timezone": self.timezone,
        }


@dataclass
class SecureDataPackage:
    """Secure encrypted data package."""

    data_id: str
    timestamp: float
    classification: DataClassification
    encrypted_data: bytes
    checksum: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "data_id": self.data_id,
            "timestamp": self.timestamp,
            "classification": self.classification.value,
            "encrypted_data": self.encrypted_data.hex(),
            "checksum": self.checksum,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SecureDataPackage:
        """Create from dictionary."""
        return cls(
            data_id=data["data_id"],
            timestamp=data["timestamp"],
            classification=DataClassification(data["classification"]),
            encrypted_data=bytes.fromhex(data["encrypted_data"]),
            checksum=data["checksum"],
            metadata=data.get("metadata", {}),
        )


class SecureStorageManager:
    """Manager for secure encrypted storage of intelligence data."""

    def __init__(self, storage_dir: str = "data/intelligence/secure"):
        """Initialize secure storage manager.

        Args:
            storage_dir: Directory for secure storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize encryption key
        self.key_file = self.storage_dir / ".encryption_key"
        self.cipher = self._initialize_encryption()

        logger.info("SecureStorageManager initialized with encrypted storage")

    def _initialize_encryption(self) -> Fernet:
        """Initialize encryption system.

        Returns:
            Fernet cipher instance
        """
        if self.key_file.exists():
            # Load existing key
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            # Secure the key file
            os.chmod(self.key_file, 0o600)

        return Fernet(key)

    def store_intelligence(
        self,
        data: IntelligenceReport,
        classification: DataClassification = DataClassification.CONFIDENTIAL,
    ) -> str:
        """Store intelligence report securely.

        Args:
            data: IntelligenceReport to store
            classification: Classification level

        Returns:
            Data ID for retrieval
        """
        # Convert report to JSON
        report_json = json.dumps(data.to_dict())

        # Encrypt data
        encrypted_data = self.cipher.encrypt(report_json.encode())

        # Generate checksum
        checksum = hashlib.sha256(report_json.encode()).hexdigest()

        # Create data package
        data_id = f"{data.domain.value}_{data.agent_id}_{int(data.timestamp)}"
        package = SecureDataPackage(
            data_id=data_id,
            timestamp=data.timestamp,
            classification=classification,
            encrypted_data=encrypted_data,
            checksum=checksum,
            metadata={
                "domain": data.domain.value,
                "agent_id": data.agent_id,
                "change_level": data.change_level.value,
            },
        )

        # Store to disk
        self._save_package(package)

        return data_id

    def retrieve_intelligence(self, data_id: str) -> IntelligenceReport | None:
        """Retrieve and decrypt intelligence report.

        Args:
            data_id: Data ID to retrieve

        Returns:
            IntelligenceReport if found, None otherwise
        """
        package = self._load_package(data_id)
        if not package:
            return None

        # Decrypt data
        decrypted_data = self.cipher.decrypt(package.encrypted_data)

        # Verify checksum
        checksum = hashlib.sha256(decrypted_data).hexdigest()
        if checksum != package.checksum:
            logger.error("Checksum mismatch for %s", data_id)
            return None

        # Parse JSON
        report_dict = json.loads(decrypted_data.decode())

        # Reconstruct IntelligenceReport (simplified)
        return report_dict  # In production, would reconstruct full object

    def _save_package(self, package: SecureDataPackage) -> None:
        """Save package to disk.

        Args:
            package: SecureDataPackage to save
        """
        # Organize by classification
        class_dir = self.storage_dir / package.classification.value
        class_dir.mkdir(exist_ok=True)

        # Save package
        package_file = class_dir / f"{package.data_id}.json"
        with open(package_file, "w") as f:
            json.dump(package.to_dict(), f, indent=2)

        # Secure the file
        os.chmod(package_file, 0o600)

    def _load_package(self, data_id: str) -> SecureDataPackage | None:
        """Load package from disk.

        Args:
            data_id: Data ID to load

        Returns:
            SecureDataPackage if found, None otherwise
        """
        # Search all classification directories
        for class_level in DataClassification:
            class_dir = self.storage_dir / class_level.value
            package_file = class_dir / f"{data_id}.json"

            if package_file.exists():
                with open(package_file) as f:
                    data = json.load(f)
                return SecureDataPackage.from_dict(data)

        return None

    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        stats = {"by_classification": {}, "total_packages": 0}

        for class_level in DataClassification:
            class_dir = self.storage_dir / class_level.value
            if class_dir.exists():
                count = len(list(class_dir.glob("*.json")))
                stats["by_classification"][class_level.value] = count
                stats["total_packages"] += count

        return stats


class Continuous24x7Agent(IntelligenceAgent):
    """Intelligence agent with 24/7 continuous monitoring capabilities."""

    def __init__(
        self,
        agent_id: str,
        domain: IntelligenceDomain,
        specialty: str,
        coverage: GeographicCoverage,
        storage_manager: SecureStorageManager,
        data_dir: str = "data/intelligence",
        kernel=None,
        monitoring_interval: int = 60,  # seconds
    ):
        """Initialize continuous monitoring agent.

        Args:
            agent_id: Unique agent identifier
            domain: Intelligence domain
            specialty: Agent specialty
            coverage: Geographic coverage
            storage_manager: Secure storage manager
            data_dir: Data directory
            kernel: Optional cognition kernel
            monitoring_interval: Monitoring interval in seconds
        """
        super().__init__(
            agent_id=agent_id,
            domain=domain,
            specialty=specialty,
            data_dir=data_dir,
            kernel=kernel,
        )

        self.coverage = coverage
        self.storage_manager = storage_manager
        self.monitoring_interval = monitoring_interval

        # 24/7 monitoring state
        self.monitoring_active = False
        self.monitoring_thread: threading.Thread | None = None
        self.stop_event = threading.Event()

        # Statistics
        self.total_collections = 0
        self.total_stored = 0
        self.last_collection_time: float | None = None

        # Labels and tags
        self.auto_labels: set[str] = set()
        self._initialize_labels()

        logger.info("Continuous24x7Agent %s initialized for %s", agent_id, coverage.region.value)

    def _initialize_labels(self) -> None:
        """Initialize automatic labels for this agent."""
        self.auto_labels.add(self.domain.value)
        self.auto_labels.add(self.specialty)
        self.auto_labels.add(self.coverage.region.value)
        self.auto_labels.add("continuous_monitoring")
        self.auto_labels.add("24x7")

    def start_monitoring(self) -> None:
        """Start 24/7 continuous monitoring."""
        if self.monitoring_active:
            logger.warning("Agent %s already monitoring", self.agent_id)
            return

        self.monitoring_active = True
        self.stop_event.clear()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            name=f"Monitor-{self.agent_id}",
            daemon=True,
        )
        self.monitoring_thread.start()

        logger.info("Agent %s started 24/7 monitoring", self.agent_id)

    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False
        self.stop_event.set()

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        logger.info("Agent %s stopped monitoring", self.agent_id)

    def _monitoring_loop(self) -> None:
        """Main 24/7 monitoring loop."""
        logger.info("Agent %s entering monitoring loop", self.agent_id)

        while self.monitoring_active and not self.stop_event.is_set():
            try:
                # Collect and monitor
                self._collect_and_process()

                # Wait for next interval
                self.stop_event.wait(self.monitoring_interval)

            except Exception as e:
                logger.error("Agent %s monitoring error: %s", self.agent_id, e)
                self.status = MonitoringStatus.ERROR
                # Continue monitoring despite errors
                time.sleep(self.monitoring_interval)

    def _collect_and_process(self) -> None:
        """Collect data, label, organize, and store securely."""
        self.status = MonitoringStatus.ANALYZING

        # Generate intelligence report
        report = self.monitor()

        # Add geographic and temporal labels
        report.tags.extend(self.auto_labels)
        report.tags.append(f"region_{self.coverage.region.value}")
        report.tags.append(f"collected_{datetime.utcnow().strftime('%Y%m%d')}")

        # Classify based on change level
        classification = self._classify_report(report)

        # Store securely
        data_id = self.storage_manager.store_intelligence(
            report, classification=classification
        )

        # Update statistics
        self.total_collections += 1
        self.total_stored += 1
        self.last_collection_time = time.time()

        logger.debug("Agent %s collected and stored report %s", self.agent_id, data_id)

    def _classify_report(self, report: IntelligenceReport) -> DataClassification:
        """Classify report for secure storage.

        Args:
            report: Intelligence report to classify

        Returns:
            DataClassification level
        """
        # Classify based on change level
        if report.change_level == ChangeLevel.CRISIS:
            return DataClassification.TOP_SECRET
        elif report.change_level == ChangeLevel.CRITICAL:
            return DataClassification.SECRET
        elif report.change_level == ChangeLevel.SIGNIFICANT:
            return DataClassification.CONFIDENTIAL
        elif report.change_level == ChangeLevel.NOTABLE:
            return DataClassification.INTERNAL
        else:
            return DataClassification.PUBLIC

    def get_monitoring_stats(self) -> dict[str, Any]:
        """Get monitoring statistics.

        Returns:
            Dictionary with monitoring stats
        """
        return {
            "agent_id": self.agent_id,
            "monitoring_active": self.monitoring_active,
            "total_collections": self.total_collections,
            "total_stored": self.total_stored,
            "last_collection_time": self.last_collection_time,
            "coverage": self.coverage.to_dict(),
            "labels": list(self.auto_labels),
            "status": self.status.value,
        }


class GlobalCoverageCoordinator:
    """Coordinates agents for global geographic coverage."""

    def __init__(self):
        """Initialize global coverage coordinator."""
        self.region_assignments: dict[GlobalRegion, list[Continuous24x7Agent]] = {
            region: [] for region in GlobalRegion
        }

        self.country_coverage: dict[str, list[str]] = {}  # country -> agent_ids

    def assign_agent(self, agent: Continuous24x7Agent, countries: list[str]) -> None:
        """Assign agent to cover specific countries.

        Args:
            agent: Agent to assign
            countries: List of countries to cover
        """
        # Add to region
        self.region_assignments[agent.coverage.region].append(agent)

        # Track country coverage
        for country in countries:
            if country not in self.country_coverage:
                self.country_coverage[country] = []
            self.country_coverage[country].append(agent.agent_id)

        logger.info("Assigned agent %s to %s countries in %s", agent.agent_id, len(countries), agent.coverage.region.value)

    def get_coverage_report(self) -> dict[str, Any]:
        """Get comprehensive coverage report.

        Returns:
            Dictionary with coverage statistics
        """
        return {
            "regions": {
                region.value: len(agents)
                for region, agents in self.region_assignments.items()
            },
            "countries_covered": len(self.country_coverage),
            "total_agents": sum(
                len(agents) for agents in self.region_assignments.values()
            ),
            "coverage_details": {
                region.value: [agent.agent_id for agent in agents]
                for region, agents in self.region_assignments.items()
            },
        }

    def get_agents_for_region(self, region: GlobalRegion) -> list[Continuous24x7Agent]:
        """Get all agents covering a region.

        Args:
            region: Geographic region

        Returns:
            List of agents covering that region
        """
        return self.region_assignments[region]

    def get_agents_for_country(self, country: str) -> list[str]:
        """Get agent IDs covering a specific country.

        Args:
            country: Country name

        Returns:
            List of agent IDs
        """
        return self.country_coverage.get(country, [])


class ContinuousMonitoringSystem:
    """Main system for managing 24/7 continuous intelligence monitoring."""

    def __init__(
        self,
        data_dir: str = "data/intelligence",
        monitoring_interval: int = 60,
    ):
        """Initialize continuous monitoring system.

        Args:
            data_dir: Data directory
            monitoring_interval: Monitoring interval in seconds
        """
        self.data_dir = Path(data_dir)
        self.monitoring_interval = monitoring_interval

        # Initialize components
        self.storage_manager = SecureStorageManager(
            storage_dir=str(self.data_dir / "secure")
        )
        self.coverage_coordinator = GlobalCoverageCoordinator()

        # Agent registry
        self.agents: dict[str, Continuous24x7Agent] = {}

        # System state
        self.system_active = False

        logger.info("ContinuousMonitoringSystem initialized")

    def create_global_coverage_agents(
        self,
        domain: IntelligenceDomain,
        specialty: str,
        count_per_region: int = 3,
        kernel=None,
    ) -> list[Continuous24x7Agent]:
        """Create agents with global coverage.

        Args:
            domain: Intelligence domain
            specialty: Agent specialty
            count_per_region: Number of agents per region
            kernel: Optional cognition kernel

        Returns:
            List of created agents
        """
        agents = []

        # Create agents for each region
        for region in GlobalRegion:
            for i in range(count_per_region):
                agent_id = f"{domain.value}_{specialty}_{region.value}_{i:02d}"

                # Create coverage for this region
                coverage = GeographicCoverage(
                    region=region,
                    countries=self._get_countries_for_region(region),
                )

                # Create agent
                agent = Continuous24x7Agent(
                    agent_id=agent_id,
                    domain=domain,
                    specialty=specialty,
                    coverage=coverage,
                    storage_manager=self.storage_manager,
                    data_dir=str(self.data_dir),
                    kernel=kernel,
                    monitoring_interval=self.monitoring_interval,
                )

                # Register agent
                self.agents[agent_id] = agent
                self.coverage_coordinator.assign_agent(agent, coverage.countries)
                agents.append(agent)

        logger.info("Created %s agents for %s/%s with global coverage", len(agents), domain.value, specialty)

        return agents

    def _get_countries_for_region(self, region: GlobalRegion) -> list[str]:
        """Get sample countries for a region.

        Args:
            region: Geographic region

        Returns:
            List of country names
        """
        # Sample countries per region (simplified)
        country_map = {
            GlobalRegion.NORTH_AMERICA: [
                "USA",
                "Canada",
                "Mexico",
                "Cuba",
                "Jamaica",
            ],
            GlobalRegion.SOUTH_AMERICA: [
                "Brazil",
                "Argentina",
                "Chile",
                "Colombia",
                "Peru",
            ],
            GlobalRegion.EUROPE: [
                "UK",
                "France",
                "Germany",
                "Italy",
                "Spain",
                "Poland",
            ],
            GlobalRegion.AFRICA: [
                "South Africa",
                "Egypt",
                "Nigeria",
                "Kenya",
                "Ethiopia",
            ],
            GlobalRegion.MIDDLE_EAST: [
                "Saudi Arabia",
                "UAE",
                "Israel",
                "Iran",
                "Turkey",
            ],
            GlobalRegion.ASIA_PACIFIC: [
                "China",
                "Japan",
                "India",
                "South Korea",
                "Australia",
            ],
            GlobalRegion.CENTRAL_ASIA: [
                "Kazakhstan",
                "Uzbekistan",
                "Turkmenistan",
            ],
            GlobalRegion.OCEANIA: [
                "New Zealand",
                "Fiji",
                "Papua New Guinea",
            ],
        }

        return country_map.get(region, ["Unknown"])

    def start_all_monitoring(self) -> None:
        """Start 24/7 monitoring for all agents."""
        if self.system_active:
            logger.warning("Monitoring system already active")
            return

        self.system_active = True

        for agent in self.agents.values():
            agent.start_monitoring()

        logger.info("Started 24/7 monitoring for %s agents across all regions", len(self.agents))

    def stop_all_monitoring(self) -> None:
        """Stop all monitoring."""
        if not self.system_active:
            return

        for agent in self.agents.values():
            agent.stop_monitoring()

        self.system_active = False

        logger.info("Stopped all monitoring")

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status.

        Returns:
            Dictionary with system status
        """
        active_agents = sum(
            1 for agent in self.agents.values() if agent.monitoring_active
        )

        total_collections = sum(
            agent.total_collections for agent in self.agents.values()
        )

        return {
            "system_active": self.system_active,
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "total_collections": total_collections,
            "coverage_report": self.coverage_coordinator.get_coverage_report(),
            "storage_stats": self.storage_manager.get_storage_stats(),
        }

    def get_agent_stats(self) -> list[dict[str, Any]]:
        """Get statistics for all agents.

        Returns:
            List of agent statistics
        """
        return [agent.get_monitoring_stats() for agent in self.agents.values()]
