"""
Global Monolithic Registry System
=================================

Universal registry for all department floors, enabling:
- Floor discovery and registration
- Cross-language service lookup
- Capability-based routing
- Health monitoring and status tracking
"""

import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class FloorStatus(Enum):
    """Floor operational status"""

    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


class ServiceType(Enum):
    """Types of services floors can provide"""

    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    CODE_FORMATTING = "code_formatting"
    CODE_TESTING = "code_testing"
    CODE_SECURITY = "code_security"
    CODE_REVIEW = "code_review"
    BUILD = "build"
    DEPLOYMENT = "deployment"
    DATA_PROCESSING = "data_processing"
    WEB_SERVICE = "web_service"


@dataclass
class AgentRegistration:
    """Registration of an agent within a floor"""

    agent_id: str
    name: str
    role: str
    capabilities: List[str]
    floor: str
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FloorRegistration:
    """Registration of a department floor"""

    floor_id: str
    floor_number: int
    language: str
    domain: str
    status: FloorStatus
    services: List[ServiceType]
    agents: List[str] = field(default_factory=list)
    endpoint: Optional[str] = None
    process_id: Optional[int] = None
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_heartbeat: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["services"] = [s.value for s in self.services]
        return data


class GlobalRegistry:
    """
    Global Monolithic Registry

    Central registry for all department floors, providing:
    - Floor registration and discovery
    - Agent tracking across floors
    - Service capability routing
    - Health monitoring
    - Cross-floor communication metadata
    """

    def __init__(self):
        self.floors: Dict[str, FloorRegistration] = {}
        self.agents: Dict[str, AgentRegistration] = {}
        self.service_index: Dict[ServiceType, Set[str]] = {service: set() for service in ServiceType}
        self._lock = threading.RLock()
        self._initialized = False

    def initialize(self):
        """Initialize the registry"""
        with self._lock:
            if self._initialized:
                return
            self._initialized = True

    def register_floor(
        self,
        floor_id: str,
        floor_number: int,
        language: str,
        domain: str,
        services: List[ServiceType],
        endpoint: Optional[str] = None,
        process_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FloorRegistration:
        """
        Register a new floor in the global registry

        Args:
            floor_id: Unique identifier for the floor
            floor_number: Floor number (1-28)
            language: Programming language
            domain: Domain of expertise
            services: List of service types this floor provides
            endpoint: Communication endpoint (optional)
            process_id: Process ID if running as separate process
            metadata: Additional floor metadata

        Returns:
            FloorRegistration object
        """
        with self._lock:
            if floor_id in self.floors:
                raise ValueError(f"Floor {floor_id} already registered")

            registration = FloorRegistration(
                floor_id=floor_id,
                floor_number=floor_number,
                language=language,
                domain=domain,
                status=FloorStatus.INITIALIZING,
                services=services,
                endpoint=endpoint,
                process_id=process_id,
                metadata=metadata or {},
            )

            self.floors[floor_id] = registration

            # Update service index
            for service in services:
                self.service_index[service].add(floor_id)

            return registration

    def register_agent(
        self, agent_id: str, name: str, role: str, capabilities: List[str], floor_id: str
    ) -> AgentRegistration:
        """
        Register an agent within a floor

        Args:
            agent_id: Unique identifier for the agent
            name: Agent name
            role: Agent role (e.g., Architect, Builder, Tester)
            capabilities: List of capabilities
            floor_id: ID of the floor this agent belongs to

        Returns:
            AgentRegistration object
        """
        with self._lock:
            if agent_id in self.agents:
                raise ValueError(f"Agent {agent_id} already registered")

            if floor_id not in self.floors:
                raise ValueError(f"Floor {floor_id} not found in registry")

            registration = AgentRegistration(
                agent_id=agent_id, name=name, role=role, capabilities=capabilities, floor=floor_id
            )

            self.agents[agent_id] = registration
            self.floors[floor_id].agents.append(agent_id)

            return registration

    def update_floor_status(self, floor_id: str, status: FloorStatus) -> None:
        """Update the status of a floor"""
        with self._lock:
            if floor_id not in self.floors:
                raise ValueError(f"Floor {floor_id} not found")

            self.floors[floor_id].status = status
            self.floors[floor_id].last_heartbeat = datetime.utcnow().isoformat()

    def get_floor(self, floor_id: str) -> Optional[FloorRegistration]:
        """Get floor registration by ID"""
        with self._lock:
            return self.floors.get(floor_id)

    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent registration by ID"""
        with self._lock:
            return self.agents.get(agent_id)

    def find_floors_by_language(self, language: str) -> List[FloorRegistration]:
        """Find all floors for a specific language"""
        with self._lock:
            return [floor for floor in self.floors.values() if floor.language.lower() == language.lower()]

    def find_floors_by_service(self, service: ServiceType) -> List[FloorRegistration]:
        """Find all floors that provide a specific service"""
        with self._lock:
            floor_ids = self.service_index.get(service, set())
            return [self.floors[fid] for fid in floor_ids if fid in self.floors]

    def find_ready_floors_by_service(self, service: ServiceType) -> List[FloorRegistration]:
        """Find all ready floors that provide a specific service"""
        floors = self.find_floors_by_service(service)
        return [floor for floor in floors if floor.status == FloorStatus.READY]

    def get_all_floors(self) -> List[FloorRegistration]:
        """Get all registered floors"""
        with self._lock:
            return list(self.floors.values())

    def get_all_agents(self) -> List[AgentRegistration]:
        """Get all registered agents"""
        with self._lock:
            return list(self.agents.values())

    def get_agents_by_floor(self, floor_id: str) -> List[AgentRegistration]:
        """Get all agents for a specific floor"""
        with self._lock:
            if floor_id not in self.floors:
                return []

            agent_ids = self.floors[floor_id].agents
            return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def deregister_floor(self, floor_id: str) -> bool:
        """
        Deregister a floor and its agents

        Args:
            floor_id: ID of the floor to deregister

        Returns:
            True if deregistered, False if not found
        """
        with self._lock:
            if floor_id not in self.floors:
                return False

            floor = self.floors[floor_id]

            # Remove from service index
            for service in floor.services:
                self.service_index[service].discard(floor_id)

            # Remove agents
            for agent_id in floor.agents:
                self.agents.pop(agent_id, None)

            # Remove floor
            del self.floors[floor_id]

            return True

    def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent

        Args:
            agent_id: ID of the agent to deregister

        Returns:
            True if deregistered, False if not found
        """
        with self._lock:
            if agent_id not in self.agents:
                return False

            agent = self.agents[agent_id]
            floor_id = agent.floor

            # Remove from floor's agent list
            if floor_id in self.floors:
                self.floors[floor_id].agents = [aid for aid in self.floors[floor_id].agents if aid != agent_id]

            # Remove agent
            del self.agents[agent_id]

            return True

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the registry"""
        with self._lock:
            status_counts = {}
            for floor in self.floors.values():
                status = floor.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            service_counts = {}
            for service, floor_ids in self.service_index.items():
                service_counts[service.value] = len(floor_ids)

            return {
                "total_floors": len(self.floors),
                "total_agents": len(self.agents),
                "floors_by_status": status_counts,
                "floors_by_service": service_counts,
                "languages": list(set(floor.language for floor in self.floors.values())),
            }

    def export_registry(self) -> Dict[str, Any]:
        """Export the entire registry as JSON-serializable dict"""
        with self._lock:
            return {
                "floors": {fid: floor.to_dict() for fid, floor in self.floors.items()},
                "agents": {aid: agent.to_dict() for aid, agent in self.agents.items()},
                "stats": self.get_registry_stats(),
                "exported_at": datetime.utcnow().isoformat(),
            }

    def import_registry(self, data: Dict[str, Any]) -> None:
        """Import registry from exported data (for persistence)"""
        with self._lock:
            # Clear existing data
            self.floors.clear()
            self.agents.clear()
            for service in self.service_index:
                self.service_index[service].clear()

            # Import floors
            for floor_id, floor_data in data.get("floors", {}).items():
                floor_data["status"] = FloorStatus(floor_data["status"])
                floor_data["services"] = [ServiceType(s) for s in floor_data["services"]]
                floor = FloorRegistration(**floor_data)
                self.floors[floor_id] = floor

                # Rebuild service index
                for service in floor.services:
                    self.service_index[service].add(floor_id)

            # Import agents
            for agent_id, agent_data in data.get("agents", {}).items():
                agent = AgentRegistration(**agent_data)
                self.agents[agent_id] = agent


# Global singleton instance
_global_registry: Optional[GlobalRegistry] = None


def get_global_registry() -> GlobalRegistry:
    """Get the global registry singleton"""
    global _global_registry
    if _global_registry is None:
        _global_registry = GlobalRegistry()
        _global_registry.initialize()
    return _global_registry
