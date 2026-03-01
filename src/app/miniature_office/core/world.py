"""
World, Floor, and Office Structure
Implements Formal Codex Schema (World, Floor, Office entities)
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.miniature_office.agents.agent import Agent, Manager
from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import get_registry
from app.miniature_office.departments.department import Department
from app.miniature_office.tools.supply_store import get_supply_store


@dataclass
class OfficeSchema:
    """
    Office schema matching codex/office.json
    """

    officeId: str
    roles: List[str]  # Agent IDs
    manager: str  # Manager ID

    def to_dict(self) -> Dict:
        return {"officeId": self.officeId, "roles": self.roles, "manager": self.manager}

    @staticmethod
    def from_dict(data: Dict) -> "OfficeSchema":
        return OfficeSchema(
            officeId=data["officeId"],
            roles=data.get("roles", []),
            manager=data.get("manager", ""),
        )


class Office:
    """
    Office represents a team within a department.
    Contains agents and a manager.
    Codex Schema: codex/office.json
    """

    def __init__(self, office_id: str, department: Department):
        self.office_id = office_id
        self.department = department
        self.agents: List[str] = []  # Agent IDs
        self.manager: Optional[Manager] = None

    def add_agent(self, agent: Agent):
        """Add an agent to this office"""
        if agent.entity_id not in self.agents:
            self.agents.append(agent.entity_id)

    def set_manager(self, manager: Manager):
        """Set the manager for this office"""
        self.manager = manager

    def get_agents(self) -> List[Agent]:
        """Get all agents in this office"""
        result = []
        for agent_id in self.agents:
            agent = get_registry().get(agent_id)
            if agent and isinstance(agent, Agent):
                result.append(agent)
        return result

    def to_schema(self) -> OfficeSchema:
        """Convert to schema format"""
        return OfficeSchema(
            officeId=self.office_id,
            roles=self.agents,
            manager=self.manager.entity_id if self.manager else "",
        )

    def to_dict(self) -> Dict:
        return self.to_schema().to_dict()


@dataclass
class FloorSchema:
    """
    Floor schema matching codex/floor.json
    """

    floorId: str
    language: str
    offices: List[Dict]

    def to_dict(self) -> Dict:
        return {
            "floorId": self.floorId,
            "language": self.language,
            "offices": self.offices,
        }

    @staticmethod
    def from_dict(data: Dict) -> "FloorSchema":
        return FloorSchema(
            floorId=data["floorId"],
            language=data["language"],
            offices=data.get("offices", []),
        )


class Floor:
    """
    Floor represents a department domain (e.g., Python, Rust, JavaScript).
    Each floor contains offices (teams).
    Codex Schema: codex/floor.json
    """

    def __init__(self, floor_id: str, language: str):
        self.floor_id = floor_id
        self.language = language
        self.offices: Dict[str, Office] = {}
        self.department: Optional[Department] = None

    def add_office(self, office: Office):
        """Add an office to this floor"""
        self.offices[office.office_id] = office

    def get_office(self, office_id: str) -> Optional[Office]:
        """Get an office by ID"""
        return self.offices.get(office_id)

    def get_all_agents(self) -> List[Agent]:
        """Get all agents across all offices on this floor"""
        agents = []
        for office in self.offices.values():
            agents.extend(office.get_agents())
        return agents

    def to_schema(self) -> FloorSchema:
        """Convert to schema format"""
        return FloorSchema(
            floorId=self.floor_id,
            language=self.language,
            offices=[office.to_dict() for office in self.offices.values()],
        )

    def to_dict(self) -> Dict:
        return self.to_schema().to_dict()


@dataclass
class WorldSchema:
    """
    World schema matching codex/world.json
    """

    worldId: str
    name: str
    floors: List[Dict]
    supplyStore: Dict
    time: int

    def to_dict(self) -> Dict:
        return {
            "worldId": self.worldId,
            "name": self.name,
            "floors": self.floors,
            "supplyStore": self.supplyStore,
            "time": self.time,
        }

    @staticmethod
    def from_dict(data: Dict) -> "WorldSchema":
        return WorldSchema(
            worldId=data["worldId"],
            name=data["name"],
            floors=data.get("floors", []),
            supplyStore=data.get("supplyStore", {}),
            time=data.get("time", 0),
        )


class World:
    """
    Top-level World entity containing everything.
    Implements tick-based simulation.
    Codex Schema: codex/world.json
    """

    def __init__(self, world_id: str, name: str):
        self.world_id = world_id
        self.name = name
        self.floors: Dict[str, Floor] = {}
        self.supply_store = get_supply_store()
        self.time = 0  # Simulation time (ticks)
        self.is_active = True

        # Log world creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.world_id,
            data={"entity_type": "world", "name": name},
        )

    def add_floor(self, floor: Floor):
        """Add a floor to the world"""
        self.floors[floor.floor_id] = floor

        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=floor.floor_id,
            data={
                "entity_type": "floor",
                "language": floor.language,
                "world_id": self.world_id,
            },
        )

    def get_floor(self, floor_id: str) -> Optional[Floor]:
        """Get a floor by ID"""
        return self.floors.get(floor_id)

    def get_floor_by_language(self, language: str) -> Optional[Floor]:
        """Get a floor by language"""
        for floor in self.floors.values():
            if floor.language.lower() == language.lower():
                return floor
        return None

    def tick(self):
        """
        Advance simulation by one tick.
        Part of simulation engine loop.
        """
        self.time += 1

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            target_id=self.world_id,
            data={"action": "world_tick", "time": self.time},
        )

    def to_schema(self) -> WorldSchema:
        """Convert to schema format"""
        return WorldSchema(
            worldId=self.world_id,
            name=self.name,
            floors=[floor.to_dict() for floor in self.floors.values()],
            supplyStore={
                "items": [t.to_dict() for t in self.supply_store.tools.values()]
            },
            time=self.time,
        )

    def to_dict(self) -> Dict:
        """Serialize world to dictionary"""
        return self.to_schema().to_dict()

    def to_json(self) -> str:
        """Serialize world to JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_schema(schema: WorldSchema) -> "World":
        """Create world from schema"""
        world = World(schema.worldId, schema.name)
        world.time = schema.time

        # Reconstruct floors (simplified - full reconstruction would need more context)
        for floor_data in schema.floors:
            floor_schema = FloorSchema.from_dict(floor_data)
            floor = Floor(floor_schema.floorId, floor_schema.language)
            world.add_floor(floor)

        return world

    @staticmethod
    def from_json(json_str: str) -> "World":
        """Deserialize world from JSON"""
        data = json.loads(json_str)
        schema = WorldSchema.from_dict(data)
        return World.from_schema(schema)


# Global world instance
_world: Optional[World] = None


def create_world(world_id: str, name: str) -> World:
    """Create and set the global world instance"""
    global _world
    _world = World(world_id, name)
    return _world


def get_world() -> Optional[World]:
    """Get the global world instance"""
    return _world
