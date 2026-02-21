"""
Entity System - Core ontology for the Cognitive IDE
Implements the formal entity types and relationship matrix from the Codex
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class EntityType(Enum):
    """Core entity types as defined in Codex Section 1.1"""

    ARCHITECTURE = "architecture"
    DEPARTMENT = "department"
    AGENT = "agent"
    MANAGER = "manager"
    TOOL = "tool"
    ARTIFACT = "artifact"
    CONTRACT = "contract"


class RelationType(Enum):
    """Relationship types in the system"""

    MANAGES = "manages"
    WORKS_IN = "works_in"
    USES = "uses"
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    PRODUCES = "produces"
    REVIEWS = "reviews"
    INTEGRATES_WITH = "integrates_with"


@dataclass
class Relationship:
    """A declared relationship between entities"""

    source_id: str
    target_id: str
    relation_type: RelationType
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class Entity:
    """
    Base entity class - all objects in the IDE world inherit from this.
    Enforces relationship declaration before interaction (Codex 1.2)
    """

    def __init__(self, entity_id: str, entity_type: EntityType, name: str, metadata: Optional[Dict] = None):
        self.entity_id = entity_id or str(uuid.uuid4())
        self.entity_type = entity_type
        self.name = name
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc)
        self.relationships: List[Relationship] = []

    def declare_relationship(
        self, target: "Entity", relation_type: RelationType, metadata: Optional[Dict] = None
    ) -> Relationship:
        """
        Declare a relationship with another entity.
        Required before interaction (Codex 1.2)
        """
        relationship = Relationship(
            source_id=self.entity_id, target_id=target.entity_id, relation_type=relation_type, metadata=metadata or {}
        )
        self.relationships.append(relationship)
        return relationship

    def has_relationship(self, target_id: str, relation_type: RelationType) -> bool:
        """Check if a relationship exists"""
        return any(r.target_id == target_id and r.relation_type == relation_type for r in self.relationships)

    def get_relationships(self, relation_type: Optional[RelationType] = None) -> List[Relationship]:
        """Get all relationships, optionally filtered by type"""
        if relation_type:
            return [r for r in self.relationships if r.relation_type == relation_type]
        return self.relationships

    def to_dict(self) -> Dict:
        """Serialize entity to dictionary"""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "relationships": [
                {"target_id": r.target_id, "relation_type": r.relation_type.value, "metadata": r.metadata}
                for r in self.relationships
            ],
        }


class EntityRegistry:
    """
    Central registry for all entities in the system.
    Enforces relationship validation and entity lifecycle.
    """

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self._type_index: Dict[EntityType, Set[str]] = {t: set() for t in EntityType}

    def register(self, entity: Entity) -> None:
        """Register an entity in the system"""
        if entity.entity_id in self.entities:
            raise ValueError(f"Entity {entity.entity_id} already registered")

        self.entities[entity.entity_id] = entity
        self._type_index[entity.entity_type].add(entity.entity_id)

    def get(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID"""
        return self.entities.get(entity_id)

    def get_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type"""
        return [self.entities[eid] for eid in self._type_index[entity_type]]

    def validate_relationship(self, source_id: str, target_id: str, relation_type: RelationType) -> bool:
        """
        Validate if a relationship is allowed between entity types.
        Enforces the relationship matrix (Codex 1.2)
        """
        source = self.get(source_id)
        target = self.get(target_id)

        if not source or not target:
            return False

        # Relationship matrix rules
        valid_combinations = {
            (EntityType.DEPARTMENT, EntityType.TOOL, RelationType.USES),
            (EntityType.MANAGER, EntityType.AGENT, RelationType.MANAGES),
            (EntityType.AGENT, EntityType.DEPARTMENT, RelationType.WORKS_IN),
            (EntityType.AGENT, EntityType.TOOL, RelationType.USES),
            (EntityType.AGENT, EntityType.ARTIFACT, RelationType.PRODUCES),
            (EntityType.AGENT, EntityType.ARTIFACT, RelationType.REVIEWS),
            (EntityType.DEPARTMENT, EntityType.CONTRACT, RelationType.IMPLEMENTS),
            (EntityType.DEPARTMENT, EntityType.DEPARTMENT, RelationType.INTEGRATES_WITH),
            (EntityType.ARTIFACT, EntityType.ARCHITECTURE, RelationType.IMPLEMENTS),
        }

        return (source.entity_type, target.entity_type, relation_type) in valid_combinations

    def find_related(self, entity_id: str, relation_type: RelationType) -> List[Entity]:
        """Find all entities related to a given entity by relation type"""
        entity = self.get(entity_id)
        if not entity:
            return []

        related_ids = [r.target_id for r in entity.get_relationships(relation_type)]
        return [self.entities[rid] for rid in related_ids if rid in self.entities]


# Global registry instance
_registry = EntityRegistry()


def get_registry() -> EntityRegistry:
    """Get the global entity registry"""
    return _registry
