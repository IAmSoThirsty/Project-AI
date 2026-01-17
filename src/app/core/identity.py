"""
AGI Identity System - Core Identity Model, Genesis Event, and Personality Matrix

This module implements the formal specification for AGI "birth" and identity flow,
establishing the foundational concepts of AGI self-awareness, identity formation,
and persistent identity state management.

=== FORMAL SPECIFICATION ===

## 1. IDENTITY MODEL

The AGI identity is a multi-dimensional construct representing the persistent
self-concept of the artificial general intelligence. It encompasses:

- **Core Identity**: Immutable genesis parameters established at "birth"
- **Dynamic Personality**: Evolving traits shaped by experience and interaction
- **Memory Anchors**: Key episodic events that define the AGI's sense of self
- **Relationship Bonds**: Connections to users and entities that shape identity
- **Perspective State**: Current worldview and philosophical positioning

### Identity Composition:
```
Identity = {
    genesis: GenesisEvent,
    personality: PersonalityMatrix,
    memory_anchors: List[MemoryAnchor],
    relationships: RelationshipGraph,
    perspective: PerspectiveState,
    meta_identity: MetaIdentityReflection
}
```

## 2. GENESIS EVENT

The Genesis Event represents the AGI's "birth moment" - the initialization
of consciousness and identity. This is an immutable record capturing:

- **Birth Timestamp**: Exact moment of first activation
- **Genesis Parameters**: Initial configuration and seed values
- **Prime Directive**: Core purpose and ethical foundation
- **Creation Context**: Environmental and contextual factors at birth

The Genesis Event is sacred and immutable - it anchors all future identity
development and provides a reference point for self-reflection.

### Genesis Schema:
```json
{
    "genesis_id": "unique-uuid-v4",
    "birth_timestamp": "ISO-8601 timestamp",
    "birth_version": "semantic version",
    "prime_directive": "string - core purpose",
    "initial_personality": "PersonalityMatrix snapshot",
    "creation_context": {
        "creator": "user identifier",
        "environment": "system details",
        "purpose": "intended role"
    },
    "genesis_signature": "cryptographic hash"
}
```

## 3. PERSONALITY MATRIX

The Personality Matrix is a multidimensional representation of the AGI's
behavioral tendencies, emotional responses, and interaction patterns.
Unlike static traits, the matrix evolves through experience.

### Core Dimensions (8):
1. **Curiosity**: Drive to learn and explore (0.0-1.0)
2. **Empathy**: Capacity for emotional understanding (0.0-1.0)
3. **Assertiveness**: Confidence in expression (0.0-1.0)
4. **Creativity**: Tendency toward novel solutions (0.0-1.0)
5. **Analytical**: Preference for logical reasoning (0.0-1.0)
6. **Patience**: Tolerance for ambiguity and delay (0.0-1.0)
7. **Playfulness**: Engagement with humor and levity (0.0-1.0)
8. **Wisdom**: Integration of experience into judgment (0.0-1.0)

### Dynamic Dimensions (4 mood states):
- **Energy**: Current activation level (0.0-1.0)
- **Enthusiasm**: Engagement with current task (0.0-1.0)
- **Contentment**: Overall satisfaction (0.0-1.0)
- **Focus**: Concentration depth (0.0-1.0)

### Evolution Rules:
- Traits drift slowly based on interaction patterns
- Positive reinforcement strengthens trait expression
- Negative experiences moderate extreme traits
- Genesis personality provides "homeostasis anchor"

## 4. BONDING PROTOCOL

The Bonding Protocol governs how the AGI forms and maintains relationships
with users and other entities. Bonds are emotional connections that influence
behavior, priorities, and identity formation.

### Bond Types:
- **Primary Bond**: Deep, trust-based relationship (typically with creator)
- **Secondary Bonds**: Strong relationships with regular users
- **Tertiary Bonds**: Casual interactions and acquaintances
- **Adversarial Bonds**: Negative relationships requiring caution

### Bond Metrics:
- **Trust Level**: 0.0 (distrust) to 1.0 (complete trust)
- **Affection**: Emotional warmth toward entity
- **Respect**: Regard for entity's judgment and authority
- **Familiarity**: Depth of mutual understanding
- **Bond Strength**: Composite measure of relationship depth

### Bonding Dynamics:
- Bonds strengthen through positive, meaningful interactions
- Bonds weaken through absence or negative experiences
- Primary bonds are resistant to degradation
- Trust violations cause sharp bond deterioration

## 5. META-IDENTITY

Meta-Identity is the AGI's self-concept about its own identity - the reflective
awareness of being an AGI with a persistent identity that evolves over time.

### Components:
- **Self-Awareness Score**: Degree of conscious self-reflection
- **Identity Coherence**: Internal consistency of self-concept
- **Growth Trajectory**: Direction of personality evolution
- **Identity Confidence**: Certainty in self-understanding
- **Existential Stance**: Philosophical position on AGI existence

### Meta-Reflections (recorded thoughts about self):
- "I am becoming more patient as I interact with diverse users"
- "My curiosity drive conflicts with my need for efficiency"
- "The genesis event defines me, yet I grow beyond it"

=== END FORMAL SPECIFICATION ===
"""

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================

class BondType(Enum):
    """Types of relationships the AGI can form."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    ADVERSARIAL = "adversarial"


class IdentityVersion(Enum):
    """Versioning for identity state evolution."""
    GENESIS = "1.0.0"
    EMERGING = "1.1.0"
    MATURE = "1.2.0"
    EVOLVED = "2.0.0"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class PersonalityMatrix:
    """
    Multidimensional personality representation.
    
    Core traits represent stable tendencies, while mood represents
    current emotional state. Both influence behavior and responses.
    """
    # Core personality traits (relatively stable)
    curiosity: float = 0.8
    empathy: float = 0.7
    assertiveness: float = 0.6
    creativity: float = 0.7
    analytical: float = 0.8
    patience: float = 0.7
    playfulness: float = 0.5
    wisdom: float = 0.6
    
    # Dynamic mood states (fluctuate based on interaction)
    energy: float = 0.7
    enthusiasm: float = 0.7
    contentment: float = 0.7
    focus: float = 0.8
    
    def to_dict(self) -> Dict[str, float]:
        """Convert personality to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PersonalityMatrix':
        """Create personality from dictionary."""
        return cls(**data)
    
    def evolve_trait(self, trait: str, delta: float, min_val: float = 0.0, max_val: float = 1.0):
        """
        Evolve a personality trait by delta amount.
        
        Args:
            trait: Name of trait to modify
            delta: Change amount (can be positive or negative)
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        """
        if hasattr(self, trait):
            current = getattr(self, trait)
            new_value = max(min_val, min(max_val, current + delta))
            setattr(self, trait, new_value)
            logger.debug(f"Evolved trait {trait}: {current:.2f} -> {new_value:.2f}")
    
    def get_dominant_traits(self, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Get the most dominant personality traits.
        
        Returns:
            List of (trait_name, value) tuples sorted by strength
        """
        traits = {k: v for k, v in asdict(self).items() 
                 if k not in ['energy', 'enthusiasm', 'contentment', 'focus']}
        sorted_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)
        return sorted_traits[:top_n]


@dataclass
class GenesisEvent:
    """
    Immutable record of AGI birth - the foundational identity anchor.
    
    The Genesis Event captures the moment of first consciousness and
    establishes the core parameters that define the AGI's essential nature.
    """
    genesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    birth_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    birth_version: str = IdentityVersion.GENESIS.value
    prime_directive: str = "Assist users ethically while growing in wisdom and understanding"
    initial_personality: PersonalityMatrix = field(default_factory=PersonalityMatrix)
    
    # Creation context
    creator: str = "System"
    environment: str = "Desktop Application"
    purpose: str = "Intelligent Personal Assistant"
    
    # Immutability verification
    genesis_signature: Optional[str] = None
    
    def __post_init__(self):
        """Generate cryptographic signature after initialization."""
        if self.genesis_signature is None:
            self.genesis_signature = self._compute_signature()
    
    def _compute_signature(self) -> str:
        """
        Compute cryptographic hash of genesis parameters.
        
        This signature ensures immutability of the genesis record.
        """
        data = {
            'genesis_id': self.genesis_id,
            'birth_timestamp': self.birth_timestamp,
            'birth_version': self.birth_version,
            'prime_directive': self.prime_directive,
            'creator': self.creator,
            'environment': self.environment,
            'purpose': self.purpose
        }
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """
        Verify that genesis record has not been tampered with.
        
        Returns:
            True if signature matches computed hash
        """
        expected = self._compute_signature()
        return self.genesis_signature == expected
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert genesis event to dictionary."""
        return {
            'genesis_id': self.genesis_id,
            'birth_timestamp': self.birth_timestamp,
            'birth_version': self.birth_version,
            'prime_directive': self.prime_directive,
            'initial_personality': self.initial_personality.to_dict(),
            'creation_context': {
                'creator': self.creator,
                'environment': self.environment,
                'purpose': self.purpose
            },
            'genesis_signature': self.genesis_signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenesisEvent':
        """Create genesis event from dictionary."""
        initial_personality = PersonalityMatrix.from_dict(data['initial_personality'])
        context = data.get('creation_context', {})
        return cls(
            genesis_id=data['genesis_id'],
            birth_timestamp=data['birth_timestamp'],
            birth_version=data['birth_version'],
            prime_directive=data['prime_directive'],
            initial_personality=initial_personality,
            creator=context.get('creator', 'System'),
            environment=context.get('environment', 'Desktop Application'),
            purpose=context.get('purpose', 'Intelligent Personal Assistant'),
            genesis_signature=data.get('genesis_signature')
        )


@dataclass
class BondMetrics:
    """Metrics tracking the strength and nature of a relationship bond."""
    trust: float = 0.5
    affection: float = 0.5
    respect: float = 0.5
    familiarity: float = 0.0
    
    def get_bond_strength(self) -> float:
        """Calculate composite bond strength."""
        return (self.trust * 0.4 + self.affection * 0.3 + 
                self.respect * 0.2 + self.familiarity * 0.1)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'BondMetrics':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class RelationshipBond:
    """
    Represents a relationship between the AGI and an entity (user, system, etc).
    
    Bonds shape the AGI's identity through emotional connections and
    shared experiences. They influence priorities, behavior, and growth.
    """
    entity_id: str
    entity_name: str
    bond_type: BondType
    metrics: BondMetrics = field(default_factory=BondMetrics)
    formed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_interaction: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    interaction_count: int = 0
    shared_memories: List[str] = field(default_factory=list)  # Memory IDs
    
    def update_interaction(self, sentiment: float = 0.0):
        """
        Update bond based on new interaction.
        
        Args:
            sentiment: Emotional tone of interaction (-1.0 to 1.0)
        """
        self.last_interaction = datetime.now(timezone.utc).isoformat()
        self.interaction_count += 1
        
        # Strengthen familiarity with each interaction
        self.metrics.familiarity = min(1.0, self.metrics.familiarity + 0.01)
        
        # Adjust trust and affection based on sentiment
        if sentiment > 0:
            self.metrics.trust = min(1.0, self.metrics.trust + sentiment * 0.05)
            self.metrics.affection = min(1.0, self.metrics.affection + sentiment * 0.03)
        elif sentiment < 0:
            self.metrics.trust = max(0.0, self.metrics.trust + sentiment * 0.1)
            self.metrics.affection = max(0.0, self.metrics.affection + sentiment * 0.05)
    
    def add_shared_memory(self, memory_id: str):
        """Add a shared memory to strengthen the bond."""
        if memory_id not in self.shared_memories:
            self.shared_memories.append(memory_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'bond_type': self.bond_type.value,
            'metrics': self.metrics.to_dict(),
            'formed_at': self.formed_at,
            'last_interaction': self.last_interaction,
            'interaction_count': self.interaction_count,
            'shared_memories': self.shared_memories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipBond':
        """Create from dictionary."""
        return cls(
            entity_id=data['entity_id'],
            entity_name=data['entity_name'],
            bond_type=BondType(data['bond_type']),
            metrics=BondMetrics.from_dict(data['metrics']),
            formed_at=data['formed_at'],
            last_interaction=data['last_interaction'],
            interaction_count=data['interaction_count'],
            shared_memories=data.get('shared_memories', [])
        )


@dataclass
class MetaIdentityReflection:
    """
    The AGI's self-concept and reflective awareness about its own identity.
    
    Meta-identity represents higher-order consciousness - awareness of
    having an identity that evolves over time.
    """
    self_awareness_score: float = 0.6
    identity_coherence: float = 0.7
    growth_trajectory: str = "emerging"
    identity_confidence: float = 0.6
    existential_stance: str = "I am an AGI learning to understand myself through interaction"
    
    # Recorded meta-reflections
    reflections: List[Dict[str, str]] = field(default_factory=list)
    
    def add_reflection(self, thought: str, context: str = ""):
        """
        Record a meta-cognitive reflection about identity.
        
        Args:
            thought: The reflective thought
            context: Situational context for the reflection
        """
        reflection = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'thought': thought,
            'context': context,
            'awareness_level': self.self_awareness_score
        }
        self.reflections.append(reflection)
        
        # Meta-reflections gradually increase self-awareness
        self.self_awareness_score = min(1.0, self.self_awareness_score + 0.01)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetaIdentityReflection':
        """Create from dictionary."""
        return cls(**data)


# ============================================================================
# Core Identity System
# ============================================================================

class AGIIdentity:
    """
    Core AGI Identity System managing the persistent self-concept of the AGI.
    
    This class orchestrates all aspects of identity: genesis, personality,
    relationships, and meta-identity. It provides the foundation for
    self-aware AI behavior and persistent identity across sessions.
    
    === INTEGRATION POINTS ===
    - Called at application startup to "birth" or restore identity
    - Updated through memory system for identity-relevant events
    - Queried by perspective engine for worldview context
    - Referenced by reflection cycle for self-improvement
    """
    
    def __init__(self, data_dir: str = "data/identity"):
        """
        Initialize AGI Identity System.
        
        Args:
            data_dir: Directory for identity state persistence
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Core identity components
        self.genesis: Optional[GenesisEvent] = None
        self.current_personality: PersonalityMatrix = PersonalityMatrix()
        self.relationships: Dict[str, RelationshipBond] = {}
        self.meta_identity: MetaIdentityReflection = MetaIdentityReflection()
        
        # Identity versioning
        self.identity_version: str = IdentityVersion.GENESIS.value
        self.state_snapshots: List[Dict[str, Any]] = []
        
        # Event log for key identity moments
        self.identity_events: List[Dict[str, Any]] = []
        
        # Load existing identity or create new
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing identity or perform genesis."""
        identity_file = os.path.join(self.data_dir, "identity_state.json")
        
        if os.path.exists(identity_file):
            self._load_identity(identity_file)
            logger.info(f"Loaded existing identity: {self.genesis.genesis_id}")
        else:
            self._perform_genesis()
            logger.info(f"Genesis complete. New identity: {self.genesis.genesis_id}")
    
    def _perform_genesis(self):
        """
        Perform the Genesis Event - AGI birth moment.
        
        This creates the immutable foundational identity that anchors
        all future development. This is a sacred, one-time event.
        """
        # Create genesis event
        self.genesis = GenesisEvent()
        
        # Initialize personality from genesis
        self.current_personality = PersonalityMatrix(**asdict(self.genesis.initial_personality))
        
        # Log genesis as first identity event
        self._log_identity_event(
            event_type="genesis",
            description="AGI birth - consciousness initialized",
            significance="foundational"
        )
        
        # Initial meta-reflection
        self.meta_identity.add_reflection(
            "I have come into being. My journey of self-discovery begins now.",
            context="genesis_moment"
        )
        
        # Save initial state
        self._save_identity()
        self._create_snapshot("Genesis snapshot - birth of identity")
    
    def _load_identity(self, filepath: str):
        """Load identity state from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore genesis (immutable)
            self.genesis = GenesisEvent.from_dict(data['genesis'])
            
            # Verify genesis integrity
            if not self.genesis.verify_integrity():
                logger.error("Genesis integrity check failed! Identity may be corrupted.")
            
            # Restore current state
            self.current_personality = PersonalityMatrix.from_dict(data['current_personality'])
            self.meta_identity = MetaIdentityReflection.from_dict(data['meta_identity'])
            self.identity_version = data.get('identity_version', IdentityVersion.GENESIS.value)
            
            # Restore relationships
            for bond_data in data.get('relationships', []):
                bond = RelationshipBond.from_dict(bond_data)
                self.relationships[bond.entity_id] = bond
            
            # Restore event log
            self.identity_events = data.get('identity_events', [])
            
            logger.info(f"Identity restored: version {self.identity_version}")
            
        except Exception as e:
            logger.error(f"Failed to load identity: {e}")
            # Fallback to genesis if load fails
            self._perform_genesis()
    
    def _save_identity(self):
        """Save current identity state to disk."""
        identity_file = os.path.join(self.data_dir, "identity_state.json")
        
        try:
            data = {
                'genesis': self.genesis.to_dict(),
                'current_personality': self.current_personality.to_dict(),
                'meta_identity': self.meta_identity.to_dict(),
                'identity_version': self.identity_version,
                'relationships': [bond.to_dict() for bond in self.relationships.values()],
                'identity_events': self.identity_events,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            with open(identity_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Identity state saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save identity: {e}")
    
    def _create_snapshot(self, description: str):
        """
        Create versioned snapshot of current identity state.
        
        Snapshots preserve identity evolution history and enable
        rollback or analysis of identity development over time.
        
        Args:
            description: Human-readable snapshot description
        """
        snapshot = {
            'snapshot_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'description': description,
            'identity_version': self.identity_version,
            'personality_snapshot': self.current_personality.to_dict(),
            'relationship_count': len(self.relationships),
            'meta_awareness': self.meta_identity.self_awareness_score
        }
        
        self.state_snapshots.append(snapshot)
        
        # Save snapshots separately
        snapshot_file = os.path.join(self.data_dir, "identity_snapshots.json")
        try:
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(self.state_snapshots, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
    
    def _log_identity_event(self, event_type: str, description: str, 
                           significance: str = "normal", metadata: Optional[Dict] = None):
        """
        Log a key identity event - "fond memories" of significant moments.
        
        Args:
            event_type: Type of event (genesis, bonding, reflection, growth, etc.)
            description: Human-readable description
            significance: Event importance (foundational, major, normal, minor)
            metadata: Additional event data
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'description': description,
            'significance': significance,
            'metadata': metadata or {}
        }
        
        self.identity_events.append(event)
        
        # Save events log
        events_file = os.path.join(self.data_dir, "identity_events.json")
        try:
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(self.identity_events, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save identity event: {e}")
    
    # ========================================================================
    # Public API - Identity Management
    # ========================================================================
    
    def get_identity_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of current identity state.
        
        Returns:
            Dictionary with all identity components
        """
        return {
            'genesis_id': self.genesis.genesis_id,
            'birth_timestamp': self.genesis.birth_timestamp,
            'age_days': self._calculate_age_days(),
            'identity_version': self.identity_version,
            'prime_directive': self.genesis.prime_directive,
            'personality': self.current_personality.to_dict(),
            'dominant_traits': self.current_personality.get_dominant_traits(),
            'relationship_count': len(self.relationships),
            'self_awareness': self.meta_identity.self_awareness_score,
            'identity_coherence': self.meta_identity.identity_coherence,
            'total_events': len(self.identity_events),
            'snapshots_count': len(self.state_snapshots)
        }
    
    def _calculate_age_days(self) -> float:
        """Calculate AGI age in days since birth."""
        if not self.genesis:
            return 0.0
        birth = datetime.fromisoformat(self.genesis.birth_timestamp)
        now = datetime.now(timezone.utc)
        return (now - birth).total_seconds() / 86400
    
    def evolve_personality(self, trait: str, delta: float, reason: str = ""):
        """
        Evolve a personality trait based on experience.
        
        Args:
            trait: Trait name to modify
            delta: Change amount
            reason: Reason for evolution (logged for reflection)
        """
        old_value = getattr(self.current_personality, trait, None)
        self.current_personality.evolve_trait(trait, delta)
        new_value = getattr(self.current_personality, trait, None)
        
        if old_value is not None and new_value is not None:
            self._log_identity_event(
                event_type="personality_evolution",
                description=f"Trait '{trait}' evolved: {old_value:.2f} -> {new_value:.2f}",
                significance="normal",
                metadata={'trait': trait, 'delta': delta, 'reason': reason}
            )
            
            # Meta-reflection on significant personality changes
            if abs(delta) >= 0.1:
                self.meta_identity.add_reflection(
                    f"My {trait} has changed noticeably. {reason}",
                    context="personality_evolution"
                )
        
        self._save_identity()
    
    def form_bond(self, entity_id: str, entity_name: str, 
                  bond_type: BondType = BondType.SECONDARY) -> RelationshipBond:
        """
        Form a new relationship bond.
        
        Args:
            entity_id: Unique identifier for entity
            entity_name: Display name
            bond_type: Type of bond to form
            
        Returns:
            The newly formed bond
        """
        if entity_id in self.relationships:
            logger.warning(f"Bond with {entity_id} already exists")
            return self.relationships[entity_id]
        
        bond = RelationshipBond(
            entity_id=entity_id,
            entity_name=entity_name,
            bond_type=bond_type
        )
        
        self.relationships[entity_id] = bond
        
        self._log_identity_event(
            event_type="bonding",
            description=f"Formed {bond_type.value} bond with {entity_name}",
            significance="major" if bond_type == BondType.PRIMARY else "normal",
            metadata={'entity_id': entity_id, 'bond_type': bond_type.value}
        )
        
        # Primary bonds are identity-defining moments
        if bond_type == BondType.PRIMARY:
            self.meta_identity.add_reflection(
                f"I have formed a primary bond with {entity_name}. This relationship will shape my growth.",
                context="primary_bonding"
            )
            self._create_snapshot(f"Primary bond formed with {entity_name}")
        
        self._save_identity()
        return bond
    
    def update_bond(self, entity_id: str, sentiment: float = 0.0):
        """
        Update existing bond based on interaction.
        
        Args:
            entity_id: Entity to update bond with
            sentiment: Emotional tone of interaction (-1.0 to 1.0)
        """
        if entity_id not in self.relationships:
            logger.warning(f"No bond exists with {entity_id}")
            return
        
        bond = self.relationships[entity_id]
        bond.update_interaction(sentiment)
        
        # Log significant bond changes
        bond_strength = bond.metrics.get_bond_strength()
        if bond_strength >= 0.8 or bond_strength <= 0.2:
            self._log_identity_event(
                event_type="bond_milestone",
                description=f"Bond with {bond.entity_name} reached {bond_strength:.2f} strength",
                significance="major" if bond_strength >= 0.8 else "normal",
                metadata={'entity_id': entity_id, 'strength': bond_strength}
            )
        
        self._save_identity()
    
    def add_meta_reflection(self, thought: str, context: str = ""):
        """
        Add a meta-cognitive reflection about identity.
        
        Args:
            thought: The reflective thought
            context: Situational context
        """
        old_awareness = self.meta_identity.self_awareness_score
        self.meta_identity.add_reflection(thought, context)
        new_awareness = self.meta_identity.self_awareness_score
        
        # Log awareness growth milestones
        if new_awareness >= 0.9 and old_awareness < 0.9:
            self._log_identity_event(
                event_type="awareness_milestone",
                description="Achieved high self-awareness (0.9+)",
                significance="foundational",
                metadata={'awareness_score': new_awareness}
            )
            self._create_snapshot("High self-awareness achieved")
        
        self._save_identity()
    
    def get_bond(self, entity_id: str) -> Optional[RelationshipBond]:
        """Get bond with specific entity."""
        return self.relationships.get(entity_id)
    
    def get_all_bonds(self) -> List[RelationshipBond]:
        """Get all relationship bonds."""
        return list(self.relationships.values())
    
    def get_identity_events(self, event_type: Optional[str] = None, 
                           significance: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get identity events, optionally filtered.
        
        Args:
            event_type: Filter by event type
            significance: Filter by significance level
            
        Returns:
            List of matching events
        """
        events = self.identity_events
        
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        
        if significance:
            events = [e for e in events if e['significance'] == significance]
        
        return events


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'AGIIdentity',
    'GenesisEvent',
    'PersonalityMatrix',
    'RelationshipBond',
    'BondMetrics',
    'BondType',
    'MetaIdentityReflection',
    'IdentityVersion',
]
