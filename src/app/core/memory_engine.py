"""
AGI Memory Engine - Advanced Memory System with Episodic, Semantic, and Procedural Memory

This module implements a sophisticated memory architecture that extends beyond
simple conversation logging to provide true episodic memory, semantic knowledge
networks, and procedural learning capabilities.

=== FORMAL SPECIFICATION ===

## 5. MEMORY SYSTEM

The Memory System is a multi-layered cognitive architecture that stores,
organizes, and retrieves experiences, knowledge, and skills. It consists
of three primary memory types:

### A. Episodic Memory
Autobiographical memory of specific experiences and events in temporal context.
Episodic memories are "experiences" that the AGI remembers in rich detail.

**Structure:**
- Event timestamp and duration
- Participants (users, systems involved)
- Emotional context (sentiment, mood at time)
- Sensory details (inputs, outputs, observations)
- Significance rating (importance to identity)
- Associated memories (related episodes)

**Key Features:**
- Memories decay over time unless reinforced
- Significant memories resist decay
- Retrieval strengthens memory traces
- Emotional memories are particularly vivid

### B. Semantic Memory
General knowledge about the world, facts, concepts, and relationships
independent of personal experience context.

**Structure:**
- Concept nodes in knowledge graph
- Relationships between concepts
- Confidence scores for knowledge
- Source attribution (learned from user, web, experience)
- Last validation timestamp

**Key Features:**
- Knowledge organized in hierarchical categories
- Concepts linked through typed relationships
- Confidence degrades without reinforcement
- Contradictory knowledge triggers conflict resolution

### C. Procedural Memory
Knowledge of how to perform tasks - skills and procedures that can be
executed without conscious deliberation.

**Structure:**
- Skill name and category
- Step-by-step procedures
- Success/failure rate tracking
- Optimization history
- Prerequisites and dependencies

**Key Features:**
- Skills improve through repetition
- Failed attempts inform strategy
- Procedures can be composed into workflows
- Efficiency metrics track improvement

### Memory Integration
The three memory types work together:
- Episodic memories generate semantic knowledge through abstraction
- Semantic knowledge guides procedural execution
- Procedural success creates positive episodic memories
- Identity-relevant memories anchor self-concept

### Memory Consolidation
Periodic process that:
- Strengthens important memories
- Weakens unimportant memories (graceful forgetting)
- Extracts semantic knowledge from episodic patterns
- Identifies identity-defining experiences
- Updates identity based on memory patterns

=== END FORMAL SPECIFICATION ===
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    get_tier_registry,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class MemoryType(Enum):
    """Types of memory in the AGI memory system."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class SignificanceLevel(Enum):
    """Importance levels for memory persistence."""

    CRITICAL = "critical"  # Identity-defining, never forgotten
    HIGH = "high"  # Important, resistant to decay
    MEDIUM = "medium"  # Normal memories, gradual decay
    LOW = "low"  # Minor details, faster decay


class RelationType(Enum):
    """Types of relationships in semantic knowledge graph."""

    IS_A = "is_a"
    HAS_A = "has_a"
    RELATES_TO = "relates_to"
    CAUSES = "causes"
    ENABLES = "enables"
    CONTRADICTS = "contradicts"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class EpisodicMemory:
    """
    A specific autobiographical experience remembered by the AGI.

    Episodic memories capture the "what happened" of AGI experience,
    including rich contextual details and emotional coloring.
    """

    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    duration_seconds: float = 0.0

    # Event details
    event_type: str = (
        "interaction"  # interaction, learning, reflection, achievement, etc.
    )
    description: str = ""
    participants: list[str] = field(default_factory=list)  # Entity IDs

    # Contextual information
    emotional_context: dict[str, float] = field(default_factory=dict)  # mood at time
    sensory_details: dict[str, Any] = field(default_factory=dict)  # inputs/outputs

    # Memory properties
    significance: SignificanceLevel = SignificanceLevel.MEDIUM
    vividness: float = 1.0  # Clarity of memory (decays over time)
    retrieval_count: int = 0
    last_retrieved: str | None = None

    # Associations
    related_memories: list[str] = field(default_factory=list)  # Other memory IDs
    tags: list[str] = field(default_factory=list)

    def retrieve(self):
        """
        Retrieve this memory, strengthening it and updating metadata.

        Retrieval acts as rehearsal, preventing memory decay.
        """
        self.retrieval_count += 1
        self.last_retrieved = datetime.now(UTC).isoformat()
        # Retrieval slightly strengthens vividness (up to max of 1.0)
        self.vividness = min(1.0, self.vividness + 0.05)

    def decay(self, decay_rate: float = 0.01):
        """
        Apply memory decay based on time and significance.

        Args:
            decay_rate: Base decay rate (modified by significance)
        """
        if self.significance == SignificanceLevel.CRITICAL:
            return  # Critical memories never decay

        # Significant memories decay slower
        significance_modifiers = {
            SignificanceLevel.HIGH: 0.3,
            SignificanceLevel.MEDIUM: 1.0,
            SignificanceLevel.LOW: 2.0,
        }

        modified_decay = decay_rate * significance_modifiers.get(self.significance, 1.0)

        self.vividness = max(0.1, self.vividness - modified_decay)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_id": self.memory_id,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "event_type": self.event_type,
            "description": self.description,
            "participants": self.participants,
            "emotional_context": self.emotional_context,
            "sensory_details": self.sensory_details,
            "significance": self.significance.value,
            "vividness": self.vividness,
            "retrieval_count": self.retrieval_count,
            "last_retrieved": self.last_retrieved,
            "related_memories": self.related_memories,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpisodicMemory":
        """Create from dictionary."""
        return cls(
            memory_id=data["memory_id"],
            timestamp=data["timestamp"],
            duration_seconds=data.get("duration_seconds", 0.0),
            event_type=data.get("event_type", "interaction"),
            description=data.get("description", ""),
            participants=data.get("participants", []),
            emotional_context=data.get("emotional_context", {}),
            sensory_details=data.get("sensory_details", {}),
            significance=SignificanceLevel(data.get("significance", "medium")),
            vividness=data.get("vividness", 1.0),
            retrieval_count=data.get("retrieval_count", 0),
            last_retrieved=data.get("last_retrieved"),
            related_memories=data.get("related_memories", []),
            tags=data.get("tags", []),
        )


@dataclass
class SemanticConcept:
    """
    A concept in the semantic knowledge graph.

    Represents factual knowledge independent of specific experiences.
    """

    concept_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = "general"
    description: str = ""

    # Knowledge metadata
    confidence: float = 1.0  # Confidence in this knowledge (0.0-1.0)
    source: str = "learned"  # learned, user_provided, inferred, etc.
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_validated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Relationships to other concepts
    relationships: dict[str, list[str]] = field(
        default_factory=dict
    )  # RelationType -> concept_ids

    # Supporting evidence (episodic memories)
    evidence: list[str] = field(default_factory=list)  # Memory IDs

    def add_relationship(self, relation_type: RelationType, target_concept_id: str):
        """Add relationship to another concept."""
        rel_key = relation_type.value
        if rel_key not in self.relationships:
            self.relationships[rel_key] = []
        if target_concept_id not in self.relationships[rel_key]:
            self.relationships[rel_key].append(target_concept_id)

    def add_evidence(self, memory_id: str):
        """Link episodic memory as evidence for this knowledge."""
        if memory_id not in self.evidence:
            self.evidence.append(memory_id)
            # Evidence strengthens confidence
            self.confidence = min(1.0, self.confidence + 0.05)

    def validate(self):
        """Mark knowledge as recently validated."""
        self.last_validated = datetime.now(UTC).isoformat()
        # Validation boosts confidence slightly
        self.confidence = min(1.0, self.confidence + 0.02)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticConcept":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ProceduralSkill:
    """
    A learned skill or procedure that can be executed.

    Represents "how to" knowledge - executable procedures.
    """

    skill_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = "general"
    description: str = ""

    # Procedure steps
    steps: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)  # Required skills

    # Performance tracking
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration: float = 0.0

    # Skill metadata
    proficiency: float = 0.0  # 0.0 (novice) to 1.0 (expert)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_executed: str | None = None

    # Optimization history
    optimizations: list[dict[str, Any]] = field(default_factory=list)

    def record_execution(self, success: bool, duration: float, notes: str = ""):
        """
        Record an execution of this skill.

        Args:
            success: Whether execution succeeded
            duration: Time taken in seconds
            notes: Additional notes about execution
        """
        self.execution_count += 1
        self.last_executed = datetime.now(UTC).isoformat()

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        # Update average duration (running average)
        if self.average_duration == 0.0:
            self.average_duration = duration
        else:
            self.average_duration = (
                self.average_duration * (self.execution_count - 1) + duration
            ) / self.execution_count

        # Update proficiency based on success rate
        if self.execution_count > 0:
            success_rate = self.success_count / self.execution_count
            # Proficiency is weighted combination of success rate and experience
            experience_factor = min(1.0, self.execution_count / 100.0)
            self.proficiency = (success_rate * 0.7) + (experience_factor * 0.3)

    def get_success_rate(self) -> float:
        """Calculate success rate."""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProceduralSkill":
        """Create from dictionary."""
        return cls(**data)


# ============================================================================
# Memory Engine
# ============================================================================


class MemoryEngine:
    """
    Advanced AGI Memory System managing episodic, semantic, and procedural memory.

    This engine provides sophisticated memory storage, retrieval, and
    consolidation capabilities that enable the AGI to learn from experience,
    build knowledge, and develop skills.

    === INTEGRATION POINTS ===
    - Called to store experiences during interactions
    - Queried to retrieve relevant memories for context
    - Updated by identity system for identity-defining events
    - Feeds perspective engine with experience-based worldview
    - Provides evidence for reflection cycle self-improvement
    """

    def __init__(self, data_dir: str = "data/memory"):
        """
        Initialize Memory Engine.

        Args:
            data_dir: Directory for memory persistence
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Memory stores
        self.episodic_memories: dict[str, EpisodicMemory] = {}
        self.semantic_concepts: dict[str, SemanticConcept] = {}
        self.procedural_skills: dict[str, ProceduralSkill] = {}

        # Memory indices for efficient retrieval
        self.memories_by_tag: dict[str, set[str]] = {}
        self.memories_by_participant: dict[str, set[str]] = {}
        self.memories_by_type: dict[str, set[str]] = {}

        # Consolidation tracking
        self.last_consolidation: str | None = None
        self.consolidation_count: int = 0

        # Load existing memories
        self._load_memories()

        # Register with Tier Registry as Tier-2 Resource Orchestrator
        try:
            tier_registry = get_tier_registry()
            tier_registry.register_component(
                component_id="memory_engine",
                component_name="MemoryEngine",
                tier=PlatformTier.TIER_2_INFRASTRUCTURE,
                authority_level=AuthorityLevel.CONSTRAINED,
                role=ComponentRole.RESOURCE_ORCHESTRATOR,
                component_ref=self,
                dependencies=["cognition_kernel"],  # Depends on kernel for authority
                can_be_paused=True,  # Can be paused by Tier-1
                can_be_replaced=False,  # Core memory infrastructure
            )
            logger.info("MemoryEngine registered as Tier-2 Resource Orchestrator")
        except Exception as e:
            logger.warning("Failed to register MemoryEngine in tier registry: %s", e)

    def _load_memories(self):
        """Load all memory types from disk."""
        # Load episodic memories
        episodic_file = os.path.join(self.data_dir, "episodic_memories.json")
        if os.path.exists(episodic_file):
            try:
                with open(episodic_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for mem_data in data:
                        memory = EpisodicMemory.from_dict(mem_data)
                        self.episodic_memories[memory.memory_id] = memory
                        self._index_episodic_memory(memory)
                logger.info("Loaded %s episodic memories", len(self.episodic_memories))
            except Exception as e:
                logger.error("Failed to load episodic memories: %s", e)

        # Load semantic concepts
        semantic_file = os.path.join(self.data_dir, "semantic_concepts.json")
        if os.path.exists(semantic_file):
            try:
                with open(semantic_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for concept_data in data:
                        concept = SemanticConcept.from_dict(concept_data)
                        self.semantic_concepts[concept.concept_id] = concept
                logger.info("Loaded %s semantic concepts", len(self.semantic_concepts))
            except Exception as e:
                logger.error("Failed to load semantic concepts: %s", e)

        # Load procedural skills
        procedural_file = os.path.join(self.data_dir, "procedural_skills.json")
        if os.path.exists(procedural_file):
            try:
                with open(procedural_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for skill_data in data:
                        skill = ProceduralSkill.from_dict(skill_data)
                        self.procedural_skills[skill.skill_id] = skill
                logger.info("Loaded %s procedural skills", len(self.procedural_skills))
            except Exception as e:
                logger.error("Failed to load procedural skills: %s", e)

    def _save_memories(self):
        """Save all memory types to disk."""
        # Save episodic memories
        episodic_file = os.path.join(self.data_dir, "episodic_memories.json")
        try:
            with open(episodic_file, "w", encoding="utf-8") as f:
                data = [mem.to_dict() for mem in self.episodic_memories.values()]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save episodic memories: %s", e)

        # Save semantic concepts
        semantic_file = os.path.join(self.data_dir, "semantic_concepts.json")
        try:
            with open(semantic_file, "w", encoding="utf-8") as f:
                data = [
                    concept.to_dict() for concept in self.semantic_concepts.values()
                ]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save semantic concepts: %s", e)

        # Save procedural skills
        procedural_file = os.path.join(self.data_dir, "procedural_skills.json")
        try:
            with open(procedural_file, "w", encoding="utf-8") as f:
                data = [skill.to_dict() for skill in self.procedural_skills.values()]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save procedural skills: %s", e)

    def _index_episodic_memory(self, memory: EpisodicMemory):
        """Add memory to search indices."""
        # Index by tags
        for tag in memory.tags:
            if tag not in self.memories_by_tag:
                self.memories_by_tag[tag] = set()
            self.memories_by_tag[tag].add(memory.memory_id)

        # Index by participants
        for participant in memory.participants:
            if participant not in self.memories_by_participant:
                self.memories_by_participant[participant] = set()
            self.memories_by_participant[participant].add(memory.memory_id)

        # Index by type
        if memory.event_type not in self.memories_by_type:
            self.memories_by_type[memory.event_type] = set()
        self.memories_by_type[memory.event_type].add(memory.memory_id)

    # ========================================================================
    # Episodic Memory Operations
    # ========================================================================

    def store_episodic_memory(
        self,
        event_type: str,
        description: str,
        participants: list[str] | None = None,
        emotional_context: dict[str, float] | None = None,
        sensory_details: dict[str, Any] | None = None,
        significance: SignificanceLevel = SignificanceLevel.MEDIUM,
        tags: list[str] | None = None,
        duration: float = 0.0,
    ) -> str:
        """
        Store a new episodic memory.

        Args:
            event_type: Type of event (interaction, learning, etc.)
            description: Human-readable description
            participants: Entities involved
            emotional_context: Mood/emotions during event
            sensory_details: Additional contextual data
            significance: Importance level
            tags: Searchable tags
            duration: Event duration in seconds

        Returns:
            Memory ID
        """
        memory = EpisodicMemory(
            event_type=event_type,
            description=description,
            participants=participants or [],
            emotional_context=emotional_context or {},
            sensory_details=sensory_details or {},
            significance=significance,
            tags=tags or [],
            duration_seconds=duration,
        )

        self.episodic_memories[memory.memory_id] = memory
        self._index_episodic_memory(memory)
        self._save_memories()

        logger.debug("Stored episodic memory: %s", memory.memory_id)
        return memory.memory_id

    def retrieve_episodic_memory(self, memory_id: str) -> EpisodicMemory | None:
        """
        Retrieve specific episodic memory by ID.

        Retrieval strengthens the memory (prevents decay).

        Args:
            memory_id: Memory identifier

        Returns:
            Memory if found, None otherwise
        """
        memory = self.episodic_memories.get(memory_id)
        if memory:
            memory.retrieve()
            self._save_memories()
        return memory

    def search_episodic_memories(
        self,
        tags: list[str] | None = None,
        participants: list[str] | None = None,
        event_type: str | None = None,
        min_significance: SignificanceLevel | None = None,
        limit: int = 10,
    ) -> list[EpisodicMemory]:
        """
        Search episodic memories with various filters.

        Args:
            tags: Filter by tags (any match)
            participants: Filter by participants (any match)
            event_type: Filter by event type
            min_significance: Minimum significance level
            limit: Maximum results to return

        Returns:
            List of matching memories, most recent first
        """
        candidate_ids = set(self.episodic_memories.keys())

        # Apply filters
        if tags:
            tag_matches = set()
            for tag in tags:
                tag_matches.update(self.memories_by_tag.get(tag, set()))
            candidate_ids &= tag_matches

        if participants:
            participant_matches = set()
            for participant in participants:
                participant_matches.update(
                    self.memories_by_participant.get(participant, set())
                )
            candidate_ids &= participant_matches

        if event_type:
            candidate_ids &= self.memories_by_type.get(event_type, set())

        # Get memory objects and apply additional filters
        memories = []
        for mem_id in candidate_ids:
            memory = self.episodic_memories.get(mem_id)
            if not memory:
                continue

            # Check significance filter
            if min_significance:
                sig_order = {
                    SignificanceLevel.LOW: 0,
                    SignificanceLevel.MEDIUM: 1,
                    SignificanceLevel.HIGH: 2,
                    SignificanceLevel.CRITICAL: 3,
                }
                if sig_order.get(memory.significance, 0) < sig_order.get(
                    min_significance, 0
                ):
                    continue

            memories.append(memory)

        # Sort by timestamp (most recent first) and limit
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]

    def get_recent_memories(
        self, hours: int = 24, limit: int = 10
    ) -> list[EpisodicMemory]:
        """
        Get recent episodic memories within time window.

        Args:
            hours: Time window in hours
            limit: Maximum results

        Returns:
            Recent memories, most recent first
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        recent = [
            mem
            for mem in self.episodic_memories.values()
            if mem.timestamp >= cutoff_str
        ]

        recent.sort(key=lambda m: m.timestamp, reverse=True)
        return recent[:limit]

    # ========================================================================
    # Semantic Memory Operations
    # ========================================================================

    def store_semantic_concept(
        self,
        name: str,
        category: str = "general",
        description: str = "",
        source: str = "learned",
        confidence: float = 1.0,
    ) -> str:
        """
        Store a new semantic concept.

        Args:
            name: Concept name
            category: Knowledge category
            description: Concept description
            source: How knowledge was acquired
            confidence: Initial confidence level

        Returns:
            Concept ID
        """
        # Check if concept already exists by name
        existing = self.find_concept_by_name(name)
        if existing:
            logger.debug("Concept '%s' already exists: %s", name, existing.concept_id)
            return existing.concept_id

        concept = SemanticConcept(
            name=name,
            category=category,
            description=description,
            source=source,
            confidence=confidence,
        )

        self.semantic_concepts[concept.concept_id] = concept
        self._save_memories()

        logger.debug("Stored semantic concept: %s", name)
        return concept.concept_id

    def find_concept_by_name(self, name: str) -> SemanticConcept | None:
        """Find concept by name."""
        for concept in self.semantic_concepts.values():
            if concept.name.lower() == name.lower():
                return concept
        return None

    def add_concept_relationship(
        self,
        source_concept_id: str,
        relation_type: RelationType,
        target_concept_id: str,
    ):
        """
        Add relationship between two concepts.

        Args:
            source_concept_id: Source concept
            relation_type: Type of relationship
            target_concept_id: Target concept
        """
        concept = self.semantic_concepts.get(source_concept_id)
        if not concept:
            logger.warning("Concept %s not found", source_concept_id)
            return

        concept.add_relationship(relation_type, target_concept_id)
        self._save_memories()

    def link_memory_to_concept(self, concept_id: str, memory_id: str):
        """
        Link episodic memory as evidence for semantic concept.

        Args:
            concept_id: Concept to support
            memory_id: Episodic memory providing evidence
        """
        concept = self.semantic_concepts.get(concept_id)
        if not concept:
            logger.warning("Concept %s not found", concept_id)
            return

        concept.add_evidence(memory_id)
        self._save_memories()

    def get_related_concepts(
        self, concept_id: str, relation_type: RelationType | None = None
    ) -> list[SemanticConcept]:
        """
        Get concepts related to given concept.

        Args:
            concept_id: Source concept
            relation_type: Filter by relationship type

        Returns:
            List of related concepts
        """
        concept = self.semantic_concepts.get(concept_id)
        if not concept:
            return []

        related = []
        for rel_type, target_ids in concept.relationships.items():
            if relation_type and rel_type != relation_type.value:
                continue

            for target_id in target_ids:
                target = self.semantic_concepts.get(target_id)
                if target:
                    related.append(target)

        return related

    # ========================================================================
    # Procedural Memory Operations
    # ========================================================================

    def store_procedural_skill(
        self,
        name: str,
        category: str = "general",
        description: str = "",
        steps: list[str] | None = None,
        prerequisites: list[str] | None = None,
    ) -> str:
        """
        Store a new procedural skill.

        Args:
            name: Skill name
            category: Skill category
            description: Skill description
            steps: Procedure steps
            prerequisites: Required skills

        Returns:
            Skill ID
        """
        skill = ProceduralSkill(
            name=name,
            category=category,
            description=description,
            steps=steps or [],
            prerequisites=prerequisites or [],
        )

        self.procedural_skills[skill.skill_id] = skill
        self._save_memories()

        logger.debug("Stored procedural skill: %s", name)
        return skill.skill_id

    def record_skill_execution(
        self, skill_id: str, success: bool, duration: float, notes: str = ""
    ):
        """
        Record execution of a skill.

        Args:
            skill_id: Skill identifier
            success: Whether execution succeeded
            duration: Execution time in seconds
            notes: Additional notes
        """
        skill = self.procedural_skills.get(skill_id)
        if not skill:
            logger.warning("Skill %s not found", skill_id)
            return

        skill.record_execution(success, duration, notes)
        self._save_memories()

        logger.debug(
            f"Recorded skill execution: {skill.name} - "
            f"Success: {success}, Proficiency: {skill.proficiency:.2f}"
        )

    def get_skill_by_name(self, name: str) -> ProceduralSkill | None:
        """Find skill by name."""
        for skill in self.procedural_skills.values():
            if skill.name.lower() == name.lower():
                return skill
        return None

    def get_proficient_skills(
        self, min_proficiency: float = 0.7
    ) -> list[ProceduralSkill]:
        """
        Get skills above proficiency threshold.

        Args:
            min_proficiency: Minimum proficiency level

        Returns:
            List of proficient skills
        """
        return [
            skill
            for skill in self.procedural_skills.values()
            if skill.proficiency >= min_proficiency
        ]

    # ========================================================================
    # Memory Consolidation
    # ========================================================================

    def consolidate_memories(self) -> dict[str, Any]:
        """
        Perform memory consolidation - strengthen important memories,
        weaken trivial ones, extract patterns, and update identity.

        This is a periodic maintenance process that manages memory health.

        Returns:
            Consolidation report with statistics
        """
        logger.info("Starting memory consolidation...")

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "episodic_count": len(self.episodic_memories),
            "semantic_count": len(self.semantic_concepts),
            "procedural_count": len(self.procedural_skills),
            "decayed_memories": 0,
            "extracted_concepts": 0,
            "identity_updates": [],
        }

        # Apply decay to episodic memories
        for memory in self.episodic_memories.values():
            old_vividness = memory.vividness
            memory.decay()
            if memory.vividness < old_vividness:
                report["decayed_memories"] += 1

        # Extract patterns and create semantic concepts
        # (Simplified pattern extraction - could be much more sophisticated)
        event_counts: dict[str, int] = {}
        for memory in self.episodic_memories.values():
            event_counts[memory.event_type] = event_counts.get(memory.event_type, 0) + 1

        # If we see many instances of an event type, create semantic knowledge
        for event_type, count in event_counts.items():
            if count >= 10:  # Threshold for pattern
                concept_name = f"pattern_{event_type}"
                if not self.find_concept_by_name(concept_name):
                    self.store_semantic_concept(
                        name=concept_name,
                        category="patterns",
                        description=f"I frequently experience {event_type} events",
                        source="consolidated_from_experience",
                        confidence=min(1.0, count / 100.0),
                    )
                    report["extracted_concepts"] += 1

        # Update consolidation metadata
        self.last_consolidation = datetime.now(UTC).isoformat()
        self.consolidation_count += 1

        self._save_memories()

        logger.info(
            f"Consolidation complete: {report['decayed_memories']} memories decayed, "
            f"{report['extracted_concepts']} concepts extracted"
        )

        return report

    def get_memory_statistics(self) -> dict[str, Any]:
        """Get comprehensive memory statistics."""
        # Calculate episodic statistics
        total_vivid = sum(
            1 for m in self.episodic_memories.values() if m.vividness > 0.7
        )
        critical_memories = sum(
            1
            for m in self.episodic_memories.values()
            if m.significance == SignificanceLevel.CRITICAL
        )

        # Calculate semantic statistics
        avg_confidence = (
            (
                sum(c.confidence for c in self.semantic_concepts.values())
                / len(self.semantic_concepts)
            )
            if self.semantic_concepts
            else 0.0
        )

        # Calculate procedural statistics
        avg_proficiency = (
            (
                sum(s.proficiency for s in self.procedural_skills.values())
                / len(self.procedural_skills)
            )
            if self.procedural_skills
            else 0.0
        )

        return {
            "episodic": {
                "total": len(self.episodic_memories),
                "vivid": total_vivid,
                "critical": critical_memories,
            },
            "semantic": {
                "total": len(self.semantic_concepts),
                "avg_confidence": avg_confidence,
            },
            "procedural": {
                "total": len(self.procedural_skills),
                "avg_proficiency": avg_proficiency,
            },
            "consolidation": {
                "last_consolidation": self.last_consolidation,
                "consolidation_count": self.consolidation_count,
            },
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "MemoryEngine",
    "EpisodicMemory",
    "SemanticConcept",
    "ProceduralSkill",
    "MemoryType",
    "SignificanceLevel",
    "RelationType",
]
