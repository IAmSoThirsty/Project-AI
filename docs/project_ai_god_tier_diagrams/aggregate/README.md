# Aggregates in Project-AI

## Overview

Aggregates are clusters of domain objects (entities and value objects) treated as a single unit for data changes. They enforce invariants, define transactional boundaries, and provide consistency guarantees.

## Aggregate Design Principles

```
┌────────────────────────────────────────────────────────────┐
│              Aggregate Anatomy                             │
└────────────────────────────────────────────────────────────┘

         Aggregate Root (Entity)
                 │
                 │ Controls access to:
                 │
        ┌────────┼────────┐
        │        │        │
    Entity   Entity   Value Object
        │        │
   Value Obj  Value Obj

Rules:
1. External references only to root
2. Root enforces invariants
3. Root manages lifecycle
4. Transaction boundary = aggregate boundary
```

## Aggregate Catalog

### 1. User Aggregate

**Purpose**: Manage user identity, authentication, and authorization.

**Root Entity**: User
**Child Entities**: Session
**Value Objects**: EmailAddress, Username, Password

```python
# domain/aggregate/user_aggregate.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
import bcrypt
import logging
from domain.base.aggregate import AggregateRoot
from domain.events.user_events import (
    UserRegisteredEvent,
    UserLoggedInEvent,
    PasswordChangedEvent,
    PermissionGrantedEvent,
    PermissionRevokedEvent
)

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    MODERATOR = "moderator"

@dataclass(frozen=True)
class Permission:
    """Permission value object."""
    resource: str
    action: str  # read, write, delete, execute
    
    def matches(self, resource: str, action: str) -> bool:
        """Check if permission matches."""
        # Support wildcards
        resource_match = self.resource == "*" or self.resource == resource
        action_match = self.action == "*" or self.action == action
        return resource_match and action_match

@dataclass
class Session:
    """Session entity within User aggregate."""
    session_id: UUID
    created_at: datetime
    expires_at: datetime
    ip_address: str
    active: bool = True
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if session expired."""
        return datetime.utcnow() > self.expires_at
    
    def touch(self) -> None:
        """Update last activity timestamp."""
        if not self.is_expired():
            self.last_activity = datetime.utcnow()
    
    def terminate(self) -> None:
        """Terminate session."""
        self.active = False

class UserAggregate(AggregateRoot):
    """User aggregate root."""
    
    def __init__(self, user_id: UUID, username: str, email: str):
        super().__init__(user_id)
        self.username = username
        self.email = email
        self.password_hash: Optional[str] = None
        self.role = UserRole.USER
        self.permissions: Set[Permission] = set()
        self.sessions: Dict[UUID, Session] = {}
        self.profile: Dict = {
            "display_name": username,
            "avatar_url": None,
            "bio": "",
            "preferences": {}
        }
        self.email_verified = False
        self.account_locked = False
        self.failed_login_attempts = 0
        self.last_login: Optional[datetime] = None
        
        logger.info(f"Created user aggregate for {username}")
    
    def register(self, password: str) -> None:
        """Register user with password."""
        if self.password_hash:
            raise ValueError("User already registered")
        
        self._set_password(password)
        
        event = UserRegisteredEvent(
            username=self.username,
            email=self.email,
            role=self.role.value
        )
        event.user_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"User {self.username} registered")
    
    def _set_password(self, password: str) -> None:
        """Hash and set password with validation."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain uppercase letter")
        
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain digit")
        
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()
    
    def change_password(self, old_password: str, new_password: str) -> None:
        """Change password with old password verification."""
        if not self.verify_password(old_password):
            raise ValueError("Incorrect current password")
        
        self._set_password(new_password)
        
        event = PasswordChangedEvent(
            username=self.username,
            changed_by=self.username
        )
        event.user_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"Password changed for user {self.username}")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())
    
    def login(self, password: str, ip_address: str, session_duration_hours: int = 24) -> Session:
        """Authenticate and create session."""
        if self.account_locked:
            raise ValueError("Account is locked")
        
        if not self.verify_password(password):
            self._handle_failed_login()
            raise ValueError("Invalid credentials")
        
        # Reset failed attempts on success
        self.failed_login_attempts = 0
        self.last_login = datetime.utcnow()
        
        # Create session
        session = Session(
            session_id=uuid4(),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=session_duration_hours),
            ip_address=ip_address
        )
        self.sessions[session.session_id] = session
        
        # Emit event
        event = UserLoggedInEvent(
            username=self.username,
            session_id=str(session.session_id),
            ip_address=ip_address
        )
        event.user_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"User {self.username} logged in from {ip_address}")
        return session
    
    def _handle_failed_login(self) -> None:
        """Handle failed login attempt."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.account_locked = True
            logger.warning(f"Account locked for user {self.username} after {self.failed_login_attempts} failed attempts")
    
    def logout(self, session_id: UUID) -> None:
        """Terminate session."""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        self.sessions[session_id].terminate()
        logger.info(f"User {self.username} logged out session {session_id}")
    
    def grant_permission(self, resource: str, action: str) -> None:
        """Grant permission to user."""
        permission = Permission(resource=resource, action=action)
        self.permissions.add(permission)
        
        event = PermissionGrantedEvent(
            username=self.username,
            resource=resource,
            action=action,
            granted_by="system"
        )
        event.user_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"Granted {action} on {resource} to {self.username}")
    
    def revoke_permission(self, resource: str, action: str) -> None:
        """Revoke permission from user."""
        self.permissions = {
            p for p in self.permissions
            if not (p.resource == resource and p.action == action)
        }
        
        event = PermissionRevokedEvent(
            username=self.username,
            resource=resource,
            action=action,
            revoked_by="system"
        )
        event.user_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"Revoked {action} on {resource} from {self.username}")
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission."""
        # Admin has all permissions
        if self.role == UserRole.ADMIN:
            return True
        
        return any(p.matches(resource, action) for p in self.permissions)
    
    def update_profile(self, updates: Dict) -> None:
        """Update user profile."""
        allowed_fields = ["display_name", "avatar_url", "bio", "preferences"]
        
        for key, value in updates.items():
            if key in allowed_fields:
                self.profile[key] = value
        
        self.increment_version()
        logger.info(f"Updated profile for user {self.username}")
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.email_verified = True
        self.increment_version()
        logger.info(f"Email verified for user {self.username}")
    
    def unlock_account(self) -> None:
        """Unlock account and reset failed attempts."""
        self.account_locked = False
        self.failed_login_attempts = 0
        self.increment_version()
        logger.info(f"Account unlocked for user {self.username}")
    
    def get_active_sessions(self) -> List[Session]:
        """Get all active non-expired sessions."""
        return [
            session for session in self.sessions.values()
            if session.active and not session.is_expired()
        ]
```

---

### 2. Identity Aggregate

**Purpose**: Manage AI persona identity and state transitions.

```python
# domain/aggregate/identity_aggregate.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List
from uuid import UUID, uuid4
import logging
from domain.base.aggregate import AggregateRoot
from domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

class MoodState(Enum):
    """AI mood states."""
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    HELPFUL = "helpful"
    CAUTIOUS = "cautious"
    ANALYTICAL = "analytical"
    FRIENDLY = "friendly"

@dataclass
class PersonalityTrait:
    """Personality trait value object."""
    name: str
    value: float  # 0.0 to 1.0
    
    def adjust(self, delta: float) -> 'PersonalityTrait':
        """Return new trait with adjusted value."""
        new_value = max(0.0, min(1.0, self.value + delta))
        return PersonalityTrait(self.name, new_value)

@dataclass
class MoodTransitionedEvent(DomainEvent):
    """Event: Mood changed."""
    old_mood: str = ""
    new_mood: str = ""
    trigger: str = ""

class IdentityAggregate(AggregateRoot):
    """AI identity aggregate managing persona and mood."""
    
    def __init__(self, identity_id: UUID, name: str):
        super().__init__(identity_id)
        self.name = name
        self.mood = MoodState.NEUTRAL
        self.personality_traits: Dict[str, PersonalityTrait] = {
            "curiosity": PersonalityTrait("curiosity", 0.7),
            "helpfulness": PersonalityTrait("helpfulness", 0.9),
            "assertiveness": PersonalityTrait("assertiveness", 0.5),
            "creativity": PersonalityTrait("creativity", 0.6),
            "formality": PersonalityTrait("formality", 0.4),
            "humor": PersonalityTrait("humor", 0.3),
            "empathy": PersonalityTrait("empathy", 0.8),
            "analytical": PersonalityTrait("analytical", 0.7)
        }
        self.interaction_count = 0
        self.mood_history: List[Dict] = []
        self.core_values = [
            "Transparency",
            "User Safety",
            "Continuous Learning",
            "Ethical Behavior"
        ]
        
        logger.info(f"Created identity aggregate for {name}")
    
    def transition_mood(self, new_mood: MoodState, trigger: str) -> None:
        """Transition to new mood state."""
        if new_mood == self.mood:
            return  # No change
        
        old_mood = self.mood
        self.mood = new_mood
        
        # Record mood history
        self.mood_history.append({
            "from": old_mood.value,
            "to": new_mood.value,
            "trigger": trigger,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Emit event
        event = MoodTransitionedEvent(
            old_mood=old_mood.value,
            new_mood=new_mood.value,
            trigger=trigger
        )
        event.aggregate_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"Identity {self.name} mood: {old_mood.value} → {new_mood.value}")
    
    def adjust_trait(self, trait_name: str, delta: float) -> None:
        """Adjust personality trait value."""
        if trait_name not in self.personality_traits:
            raise ValueError(f"Unknown trait: {trait_name}")
        
        old_trait = self.personality_traits[trait_name]
        new_trait = old_trait.adjust(delta)
        self.personality_traits[trait_name] = new_trait
        
        self.increment_version()
        logger.info(f"Adjusted {trait_name}: {old_trait.value:.2f} → {new_trait.value:.2f}")
    
    def record_interaction(self, interaction_type: str) -> None:
        """Record interaction and update state."""
        self.interaction_count += 1
        
        # Adjust traits based on interaction
        if interaction_type == "question":
            self.adjust_trait("curiosity", 0.01)
        elif interaction_type == "help_request":
            self.adjust_trait("helpfulness", 0.01)
        elif interaction_type == "creative_task":
            self.adjust_trait("creativity", 0.01)
        
        self.increment_version()
    
    def get_personality_summary(self) -> Dict[str, float]:
        """Get current personality trait values."""
        return {
            name: trait.value
            for name, trait in self.personality_traits.items()
        }
```

---

### 3. Memory Aggregate

**Purpose**: Manage conversation history and knowledge consolidation.

```python
# domain/aggregate/memory_aggregate.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import hashlib
import logging
from domain.base.aggregate import AggregateRoot
from domain.events.memory_events import (
    ConversationStartedEvent,
    MemoryEntryCreatedEvent,
    KnowledgeConsolidatedEvent,
    MemoryPurgedEvent
)

logger = logging.getLogger(__name__)

class KnowledgeCategory(Enum):
    """Knowledge categorization."""
    FACTS = "facts"
    SKILLS = "skills"
    PREFERENCES = "preferences"
    GOALS = "goals"
    RELATIONSHIPS = "relationships"
    OBSERVATIONS = "observations"

@dataclass
class MemoryEntry:
    """Memory entry entity."""
    entry_id: UUID
    user_message: str
    ai_response: str
    timestamp: datetime
    metadata: Dict
    embedding: Optional[List[float]] = None  # For semantic search
    
    def get_content_hash(self) -> str:
        """Generate hash of entry content."""
        content = f"{self.user_message}|{self.ai_response}"
        return hashlib.sha256(content.encode()).hexdigest()

@dataclass
class KnowledgeUnit:
    """Knowledge unit entity."""
    knowledge_id: UUID
    category: KnowledgeCategory
    content: str
    confidence: float  # 0.0 to 1.0
    source_entries: List[UUID]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    
    def access(self) -> None:
        """Record knowledge access."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def boost_confidence(self, amount: float = 0.1) -> None:
        """Increase confidence (reinforcement learning)."""
        self.confidence = min(1.0, self.confidence + amount)
    
    def decay_confidence(self, amount: float = 0.05) -> None:
        """Decrease confidence (if not accessed)."""
        self.confidence = max(0.0, self.confidence - amount)

class MemoryAggregate(AggregateRoot):
    """Memory aggregate managing conversations and knowledge."""
    
    def __init__(self, user_id: UUID):
        super().__init__(user_id)
        self.user_id = user_id
        self.conversations: List[MemoryEntry] = []
        self.knowledge_base: Dict[KnowledgeCategory, List[KnowledgeUnit]] = {
            cat: [] for cat in KnowledgeCategory
        }
        self.conversation_active = False
        self.retention_days = 90  # Retention policy
        
        logger.info(f"Created memory aggregate for user {user_id}")
    
    def start_conversation(self, initial_message: str) -> None:
        """Start new conversation."""
        self.conversation_active = True
        
        event = ConversationStartedEvent(
            user_id=str(self.user_id),
            initial_message=initial_message
        )
        event.aggregate_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"Started conversation for user {self.user_id}")
    
    def add_memory(self, user_message: str, ai_response: str, metadata: Dict = None) -> MemoryEntry:
        """Add conversation turn to memory."""
        entry = MemoryEntry(
            entry_id=uuid4(),
            user_message=user_message,
            ai_response=ai_response,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.conversations.append(entry)
        
        event = MemoryEntryCreatedEvent(
            entry_id=str(entry.entry_id),
            user_message=user_message,
            ai_response=ai_response
        )
        event.aggregate_id = self.id
        self.add_domain_event(event)
        self.increment_version()
        
        logger.info(f"Added memory entry {entry.entry_id}")
        return entry
    
    def consolidate_knowledge(self, entry: MemoryEntry) -> List[KnowledgeUnit]:
        """Extract knowledge from conversation entry."""
        extracted = []
        
        # Simple keyword-based extraction (production: use NLP/LLM)
        extraction_patterns = {
            KnowledgeCategory.FACTS: ["is", "are", "was", "were", "means"],
            KnowledgeCategory.PREFERENCES: ["like", "prefer", "enjoy", "love", "hate"],
            KnowledgeCategory.SKILLS: ["can", "know how", "able to", "learned"],
            KnowledgeCategory.GOALS: ["want", "plan", "goal", "aim", "intend"],
            KnowledgeCategory.RELATIONSHIPS: ["friend", "family", "colleague", "knows"],
            KnowledgeCategory.OBSERVATIONS: ["noticed", "seems", "appears", "observed"]
        }
        
        user_msg_lower = entry.user_message.lower()
        
        for category, patterns in extraction_patterns.items():
            if any(pattern in user_msg_lower for pattern in patterns):
                knowledge = KnowledgeUnit(
                    knowledge_id=uuid4(),
                    category=category,
                    content=entry.user_message,
                    confidence=0.7,  # Initial confidence
                    source_entries=[entry.entry_id],
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow()
                )
                self.knowledge_base[category].append(knowledge)
                extracted.append(knowledge)
                
                # Emit event
                event = KnowledgeConsolidatedEvent(
                    knowledge_id=str(knowledge.knowledge_id),
                    category=category.value,
                    content=knowledge.content,
                    confidence=knowledge.confidence,
                    source_entries=[str(entry.entry_id)]
                )
                event.aggregate_id = self.id
                self.add_domain_event(event)
        
        self.increment_version()
        logger.info(f"Consolidated {len(extracted)} knowledge units from entry {entry.entry_id}")
        return extracted
    
    def recall_knowledge(
        self,
        category: Optional[KnowledgeCategory] = None,
        min_confidence: float = 0.5
    ) -> List[KnowledgeUnit]:
        """Retrieve knowledge by category and confidence."""
        if category:
            knowledge = self.knowledge_base[category]
        else:
            knowledge = [k for cat_list in self.knowledge_base.values() for k in cat_list]
        
        # Filter by confidence
        filtered = [k for k in knowledge if k.confidence >= min_confidence]
        
        # Update access statistics
        for k in filtered:
            k.access()
        
        # Sort by access count (most accessed first)
        filtered.sort(key=lambda k: k.access_count, reverse=True)
        
        logger.info(f"Recalled {len(filtered)} knowledge units")
        return filtered
    
    def purge_old_memories(self) -> int:
        """Remove memories older than retention policy."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        before_count = len(self.conversations)
        self.conversations = [
            entry for entry in self.conversations
            if entry.timestamp > cutoff_date
        ]
        after_count = len(self.conversations)
        purged_count = before_count - after_count
        
        if purged_count > 0:
            event = MemoryPurgedEvent(
                purged_count=purged_count,
                before_date=cutoff_date.isoformat()
            )
            event.aggregate_id = self.id
            self.add_domain_event(event)
            self.increment_version()
            
            logger.info(f"Purged {purged_count} old memories")
        
        return purged_count
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation history."""
        return {
            "total_conversations": len(self.conversations),
            "knowledge_units": sum(len(units) for units in self.knowledge_base.values()),
            "knowledge_by_category": {
                cat.value: len(units)
                for cat, units in self.knowledge_base.items()
            },
            "oldest_memory": self.conversations[0].timestamp.isoformat() if self.conversations else None,
            "newest_memory": self.conversations[-1].timestamp.isoformat() if self.conversations else None
        }
```

---

## Repository Implementation

```python
# infrastructure/repositories/aggregate_repository.py
import json
import logging
from pathlib import Path
from typing import Optional, Type, TypeVar
from uuid import UUID
from domain.base.aggregate import AggregateRoot

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=AggregateRoot)

class AggregateRepository:
    """Generic repository for aggregates."""
    
    def __init__(self, aggregate_type: Type[T], data_dir: str):
        self.aggregate_type = aggregate_type
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized repository for {aggregate_type.__name__} at {data_dir}")
    
    def save(self, aggregate: T) -> None:
        """Persist aggregate with version check."""
        try:
            filepath = self.data_dir / f"{aggregate.id}.json"
            
            # Optimistic concurrency check
            if filepath.exists():
                with open(filepath, 'r') as f:
                    existing = json.load(f)
                if existing.get("version", 0) != aggregate.version - 1:
                    raise ValueError(f"Concurrency conflict on aggregate {aggregate.id}")
            
            data = self._serialize(aggregate)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {self.aggregate_type.__name__} {aggregate.id} v{aggregate.version}")
        except Exception as e:
            logger.error(f"Failed to save aggregate: {e}")
            raise
    
    def load(self, aggregate_id: UUID) -> Optional[T]:
        """Load aggregate by ID."""
        try:
            filepath = self.data_dir / f"{aggregate_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            aggregate = self._deserialize(data)
            logger.info(f"Loaded {self.aggregate_type.__name__} {aggregate_id}")
            return aggregate
        except Exception as e:
            logger.error(f"Failed to load aggregate: {e}")
            return None
    
    def _serialize(self, aggregate: T) -> Dict:
        """Serialize aggregate to dict (override per type)."""
        raise NotImplementedError
    
    def _deserialize(self, data: Dict) -> T:
        """Deserialize aggregate from dict (override per type)."""
        raise NotImplementedError
```

## Testing

```python
# tests/domain/test_aggregates.py
import pytest
from uuid import uuid4
from domain.aggregate.user_aggregate import UserAggregate, UserRole
from domain.aggregate.memory_aggregate import MemoryAggregate, KnowledgeCategory

class TestUserAggregate:
    """Test user aggregate."""
    
    def test_user_registration(self):
        """Verify user registration flow."""
        user = UserAggregate(uuid4(), "testuser", "test@example.com")
        user.register("SecurePass123")
        
        assert user.password_hash is not None
        events = user.clear_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "UserRegisteredEvent"
    
    def test_authentication(self):
        """Verify login flow."""
        user = UserAggregate(uuid4(), "testuser", "test@example.com")
        user.register("SecurePass123")
        
        session = user.login("SecurePass123", "127.0.0.1")
        assert session.active
        assert not session.is_expired()
    
    def test_permission_management(self):
        """Verify permission grant/revoke."""
        user = UserAggregate(uuid4(), "testuser", "test@example.com")
        
        user.grant_permission("documents", "read")
        assert user.has_permission("documents", "read")
        
        user.revoke_permission("documents", "read")
        assert not user.has_permission("documents", "read")
    
    def test_account_lockout(self):
        """Verify account locks after failed attempts."""
        user = UserAggregate(uuid4(), "testuser", "test@example.com")
        user.register("SecurePass123")
        
        for _ in range(5):
            try:
                user.login("WrongPassword", "127.0.0.1")
            except ValueError:
                pass
        
        assert user.account_locked
        
        with pytest.raises(ValueError, match="locked"):
            user.login("SecurePass123", "127.0.0.1")

class TestMemoryAggregate:
    """Test memory aggregate."""
    
    def test_memory_creation(self):
        """Verify memory entry creation."""
        memory = MemoryAggregate(uuid4())
        memory.start_conversation("Hello")
        
        entry = memory.add_memory("What's the weather?", "Sunny and 75°F")
        assert len(memory.conversations) == 1
        assert entry.user_message == "What's the weather?"
    
    def test_knowledge_consolidation(self):
        """Verify knowledge extraction."""
        memory = MemoryAggregate(uuid4())
        entry = memory.add_memory(
            "I like pizza",
            "Great! I'll remember that."
        )
        
        knowledge = memory.consolidate_knowledge(entry)
        assert len(knowledge) > 0
        assert any(k.category == KnowledgeCategory.PREFERENCES for k in knowledge)
    
    def test_knowledge_recall(self):
        """Verify knowledge retrieval."""
        memory = MemoryAggregate(uuid4())
        entry = memory.add_memory("The sky is blue", "Correct!")
        memory.consolidate_knowledge(entry)
        
        facts = memory.recall_knowledge(category=KnowledgeCategory.FACTS)
        assert len(facts) > 0
    
    def test_memory_purge(self):
        """Verify old memory purging."""
        memory = MemoryAggregate(uuid4())
        memory.retention_days = 0  # Immediate purge
        
        memory.add_memory("Old message", "Response")
        purged = memory.purge_old_memories()
        
        assert purged == 1
        assert len(memory.conversations) == 0
```

## Related Documentation

- **[Domain Models](../domain/domain_models.md)** - Entity and value object patterns
- **[Domain Events](../domain/domain_events.md)** - Event definitions
- **[Command Handlers](../command/command_handlers.md)** - Command to aggregate mapping
