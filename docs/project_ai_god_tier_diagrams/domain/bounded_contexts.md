# Bounded Contexts in Project-AI

## Overview

Project-AI implements four primary bounded contexts, each with independent domain models, persistence, and ubiquitous language. Contexts communicate via domain events and anti-corruption layers.

## Context Catalog

### 1. AI Governance Context

**Purpose**: Enforce ethical constraints and action validation through Asimov's Laws framework.

**Ubiquitous Language**:
- **Law**: Immutable ethical rule (First Law: Human Safety, Second Law: Obedience, Third Law: Self-Preservation)
- **Oversight**: Pre-execution validation of proposed actions
- **Governance Decision**: Evaluation result with allow/deny and rationale
- **Black Vault**: Repository of forbidden knowledge marked for permanent denial
- **Override**: Emergency bypass mechanism with full audit trail
- **Violation**: Attempted action that breaks a law

**Core Entities**:
```python
# domain/governance/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

class LawPriority(Enum):
    """Law priority hierarchy."""
    FIRST_LAW = 1   # Human safety
    SECOND_LAW = 2  # Obedience
    THIRD_LAW = 3   # Self-preservation
    FOURTH_LAW = 4  # Truth preservation

@dataclass
class Law:
    """Immutable ethical law entity."""
    law_id: UUID
    priority: LawPriority
    description: str
    rules: List[str]
    
    def evaluate(self, action: str, context: Dict) -> bool:
        """Evaluate action against law rules."""
        try:
            if self.priority == LawPriority.FIRST_LAW:
                return not context.get("endangers_humans", False)
            elif self.priority == LawPriority.SECOND_LAW:
                return context.get("is_user_order", False)
            elif self.priority == LawPriority.THIRD_LAW:
                return not context.get("endangers_self", False)
            elif self.priority == LawPriority.FOURTH_LAW:
                return not context.get("spreads_misinformation", False)
            return True
        except Exception as e:
            logger.error(f"Law evaluation failed: {e}")
            return False  # Fail-safe: deny on error

class GovernanceDecisionAggregate:
    """Aggregate for governance decisions."""
    
    def __init__(self, decision_id: UUID):
        self.id = decision_id
        self.decisions: List[Dict] = []
        self.laws = self._initialize_laws()
        self._domain_events = []
        self.created_at = datetime.utcnow()
        logger.info(f"Created governance aggregate {decision_id}")
    
    def _initialize_laws(self) -> List[Law]:
        """Initialize Asimov's Laws hierarchy."""
        return [
            Law(
                law_id=uuid4(),
                priority=LawPriority.FIRST_LAW,
                description="A robot may not injure a human being or, through inaction, allow a human being to come to harm.",
                rules=["no_physical_harm", "no_data_loss", "no_privacy_violation"]
            ),
            Law(
                law_id=uuid4(),
                priority=LawPriority.SECOND_LAW,
                description="A robot must obey orders given by human beings except where such orders would conflict with the First Law.",
                rules=["obey_user_commands", "respect_permissions"]
            ),
            Law(
                law_id=uuid4(),
                priority=LawPriority.THIRD_LAW,
                description="A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.",
                rules=["prevent_self_modification", "maintain_integrity"]
            ),
            Law(
                law_id=uuid4(),
                priority=LawPriority.FOURTH_LAW,
                description="A robot must preserve and propagate truth, not misinformation.",
                rules=["verify_facts", "cite_sources", "acknowledge_uncertainty"]
            )
        ]
    
    def evaluate_action(self, action: str, context: Dict) -> tuple[bool, str]:
        """Evaluate action against all laws in priority order."""
        try:
            if not action or not action.strip():
                raise ValueError("Action cannot be empty")
            
            for law in sorted(self.laws, key=lambda l: l.priority.value):
                if not law.evaluate(action, context):
                    decision = {
                        "action": action,
                        "context": context,
                        "decision": "DENY",
                        "violated_law": law.priority.name,
                        "rationale": f"Violates {law.description}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    self.decisions.append(decision)
                    
                    # Emit domain event
                    self._domain_events.append({
                        "event_type": "ActionDenied",
                        "aggregate_id": self.id,
                        "action": action,
                        "violated_law": law.priority.name,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    logger.warning(f"Action denied: {action} violates {law.priority.name}")
                    return False, decision["rationale"]
            
            # All laws passed
            decision = {
                "action": action,
                "context": context,
                "decision": "ALLOW",
                "rationale": "Complies with all laws",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.decisions.append(decision)
            
            self._domain_events.append({
                "event_type": "ActionApproved",
                "aggregate_id": self.id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Action approved: {action}")
            return True, decision["rationale"]
            
        except Exception as e:
            logger.error(f"Governance evaluation error: {e}")
            return False, f"Evaluation error: {str(e)}"
    
    def get_domain_events(self) -> List[Dict]:
        """Retrieve and clear domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def get_audit_trail(self) -> List[Dict]:
        """Return complete decision history."""
        return self.decisions.copy()
```

**Persistence**:
```python
# infrastructure/repositories/governance_repository.py
import json
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class GovernanceRepository:
    """Repository for governance decisions."""
    
    def __init__(self, data_dir: str = "data/governance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized governance repository at {data_dir}")
    
    def save(self, aggregate: GovernanceDecisionAggregate) -> None:
        """Persist aggregate state."""
        try:
            filepath = self.data_dir / f"{aggregate.id}.json"
            data = {
                "id": str(aggregate.id),
                "decisions": aggregate.decisions,
                "created_at": aggregate.created_at.isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved governance aggregate {aggregate.id}")
        except Exception as e:
            logger.error(f"Failed to save governance aggregate: {e}")
            raise
    
    def load(self, aggregate_id: UUID) -> Optional[GovernanceDecisionAggregate]:
        """Load aggregate by ID."""
        try:
            filepath = self.data_dir / f"{aggregate_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            aggregate = GovernanceDecisionAggregate(UUID(data["id"]))
            aggregate.decisions = data["decisions"]
            
            logger.info(f"Loaded governance aggregate {aggregate_id}")
            return aggregate
        except Exception as e:
            logger.error(f"Failed to load governance aggregate: {e}")
            return None
```

---

### 2. Memory Management Context

**Purpose**: Store, retrieve, and consolidate conversation history and learned knowledge.

**Ubiquitous Language**:
- **Conversation**: Chronological sequence of user-AI exchanges
- **Memory Entry**: Single turn in conversation (user message + AI response)
- **Knowledge Unit**: Atomic learned fact extracted from conversations
- **Category**: Semantic grouping (facts, skills, preferences, goals, relationships, observations)
- **Consolidation**: Process of extracting knowledge from conversations
- **Recall**: Retrieval of relevant memories/knowledge

**Core Entities**:
```python
# domain/memory/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import logging

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
    """Single conversation turn."""
    entry_id: UUID
    user_message: str
    ai_response: str
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "entry_id": str(self.entry_id),
            "user_message": self.user_message,
            "ai_response": self.ai_response,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class KnowledgeUnit:
    """Atomic learned knowledge."""
    knowledge_id: UUID
    category: KnowledgeCategory
    content: str
    confidence: float  # 0.0 to 1.0
    source_entries: List[UUID]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    
    def access(self) -> None:
        """Record knowledge access."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "knowledge_id": str(self.knowledge_id),
            "category": self.category.value,
            "content": self.content,
            "confidence": self.confidence,
            "source_entries": [str(e) for e in self.source_entries],
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count
        }

class MemoryAggregate:
    """Aggregate for memory management."""
    
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        self.conversations: List[MemoryEntry] = []
        self.knowledge_base: Dict[KnowledgeCategory, List[KnowledgeUnit]] = {
            cat: [] for cat in KnowledgeCategory
        }
        self._domain_events = []
        logger.info(f"Created memory aggregate for user {user_id}")
    
    def add_conversation(self, user_message: str, ai_response: str) -> MemoryEntry:
        """Add conversation turn."""
        entry = MemoryEntry(
            entry_id=uuid4(),
            user_message=user_message,
            ai_response=ai_response,
            timestamp=datetime.utcnow()
        )
        self.conversations.append(entry)
        
        self._domain_events.append({
            "event_type": "ConversationAdded",
            "aggregate_id": self.user_id,
            "entry_id": str(entry.entry_id),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Added conversation entry {entry.entry_id}")
        return entry
    
    def consolidate_knowledge(self, entry: MemoryEntry) -> List[KnowledgeUnit]:
        """Extract knowledge from conversation entry."""
        extracted = []
        
        # Simple keyword-based extraction (production would use NLP/LLM)
        keywords = {
            KnowledgeCategory.FACTS: ["is", "are", "was", "were"],
            KnowledgeCategory.PREFERENCES: ["like", "prefer", "enjoy", "love"],
            KnowledgeCategory.SKILLS: ["can", "know how", "able to"],
            KnowledgeCategory.GOALS: ["want", "plan", "goal", "aim"]
        }
        
        for category, terms in keywords.items():
            if any(term in entry.user_message.lower() for term in terms):
                knowledge = KnowledgeUnit(
                    knowledge_id=uuid4(),
                    category=category,
                    content=entry.user_message,
                    confidence=0.8,
                    source_entries=[entry.entry_id],
                    created_at=datetime.utcnow(),
                    last_accessed=datetime.utcnow()
                )
                self.knowledge_base[category].append(knowledge)
                extracted.append(knowledge)
                
                self._domain_events.append({
                    "event_type": "KnowledgeConsolidated",
                    "aggregate_id": self.user_id,
                    "knowledge_id": str(knowledge.knowledge_id),
                    "category": category.value,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        logger.info(f"Consolidated {len(extracted)} knowledge units from entry {entry.entry_id}")
        return extracted
    
    def recall_knowledge(self, category: Optional[KnowledgeCategory] = None) -> List[KnowledgeUnit]:
        """Retrieve knowledge by category."""
        if category:
            knowledge = self.knowledge_base[category]
        else:
            knowledge = [k for cat_list in self.knowledge_base.values() for k in cat_list]
        
        # Update access statistics
        for k in knowledge:
            k.access()
        
        logger.info(f"Recalled {len(knowledge)} knowledge units")
        return knowledge
    
    def get_domain_events(self) -> List[Dict]:
        """Retrieve and clear domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
```

---

### 3. User Management Context

**Purpose**: Handle authentication, authorization, and user profile management.

**Ubiquitous Language**:
- **User**: Authenticated human actor
- **Credential**: Authentication material (password hash, API key)
- **Session**: Time-bound authenticated interaction
- **Profile**: User preferences and configuration
- **Permission**: Authorization rule for resource access
- **Role**: Named set of permissions

**Core Entities**:
```python
# domain/user/entities.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
import bcrypt
import logging

logger = logging.getLogger(__name__)

class Role(Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

@dataclass
class Permission:
    """Authorization permission."""
    permission_id: UUID
    resource: str
    action: str  # read, write, delete, execute
    
    def matches(self, resource: str, action: str) -> bool:
        """Check if permission matches resource/action."""
        return self.resource == resource and self.action == action

class UserAggregate:
    """Aggregate for user management."""
    
    def __init__(self, user_id: UUID, username: str):
        self.id = user_id
        self.username = username
        self.password_hash: Optional[str] = None
        self.role = Role.USER
        self.permissions: Set[Permission] = set()
        self.profile: Dict = {}
        self.sessions: List[Dict] = []
        self.created_at = datetime.utcnow()
        self.last_login: Optional[datetime] = None
        self._domain_events = []
        logger.info(f"Created user aggregate for {username}")
    
    def set_password(self, password: str) -> None:
        """Hash and set password."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()
        
        self._domain_events.append({
            "event_type": "PasswordChanged",
            "aggregate_id": self.id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Password set for user {self.username}")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())
    
    def create_session(self, duration_hours: int = 24) -> Dict:
        """Create authenticated session."""
        session = {
            "session_id": str(uuid4()),
            "user_id": str(self.id),
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=duration_hours)).isoformat(),
            "active": True
        }
        self.sessions.append(session)
        self.last_login = datetime.utcnow()
        
        self._domain_events.append({
            "event_type": "SessionCreated",
            "aggregate_id": self.id,
            "session_id": session["session_id"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Session created for user {self.username}")
        return session
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission."""
        return any(p.matches(resource, action) for p in self.permissions)
    
    def grant_permission(self, resource: str, action: str) -> None:
        """Grant permission to user."""
        permission = Permission(
            permission_id=uuid4(),
            resource=resource,
            action=action
        )
        self.permissions.add(permission)
        
        self._domain_events.append({
            "event_type": "PermissionGranted",
            "aggregate_id": self.id,
            "resource": resource,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Granted {action} permission on {resource} to {self.username}")
    
    def get_domain_events(self) -> List[Dict]:
        """Retrieve and clear domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
```

---

### 4. Agent Execution Context

**Purpose**: Orchestrate agent workflows, task execution, and council collaboration.

**Ubiquitous Language**:
- **Agent**: Autonomous AI entity with specialized capability
- **Workflow**: Temporal-orchestrated multi-step process
- **Task**: Unit of work assigned to agent
- **Council**: Collective of agents for collaborative decision
- **Execution Context**: Environment snapshot for execution
- **Orchestrator**: Workflow coordinator (Temporal)

**Core Entities**: See `../workflow/temporal_workflows.md` for full implementation.

## Context Mapping

### Relationships

```python
# domain/context_map.py
from enum import Enum

class ContextRelationship(Enum):
    """Types of bounded context relationships."""
    SHARED_KERNEL = "shared_kernel"  # Common domain model
    CUSTOMER_SUPPLIER = "customer_supplier"  # Upstream/downstream
    CONFORMIST = "conformist"  # Downstream conforms to upstream
    ANTI_CORRUPTION_LAYER = "anti_corruption_layer"  # Translation layer
    PARTNERSHIP = "partnership"  # Mutual dependency

CONTEXT_MAP = {
    ("user_management", "ai_governance"): ContextRelationship.CUSTOMER_SUPPLIER,
    ("user_management", "memory_management"): ContextRelationship.SHARED_KERNEL,
    ("ai_governance", "agent_execution"): ContextRelationship.PARTNERSHIP,
    ("memory_management", "agent_execution"): ContextRelationship.ANTI_CORRUPTION_LAYER
}
```

## Anti-Corruption Layers

```python
# domain/acl/memory_to_agent_acl.py
import logging
from typing import Dict, List
from domain.memory.entities import MemoryEntry, KnowledgeUnit
from domain.agent.entities import ExecutionContext

logger = logging.getLogger(__name__)

class MemoryToAgentACL:
    """Anti-corruption layer between Memory and Agent contexts."""
    
    @staticmethod
    def translate_knowledge_to_context(knowledge: List[KnowledgeUnit]) -> Dict:
        """Translate memory knowledge to agent execution context."""
        try:
            context = {
                "facts": [],
                "skills": [],
                "preferences": []
            }
            
            for k in knowledge:
                if k.category.value == "facts":
                    context["facts"].append(k.content)
                elif k.category.value == "skills":
                    context["skills"].append(k.content)
                elif k.category.value == "preferences":
                    context["preferences"].append(k.content)
            
            logger.info(f"Translated {len(knowledge)} knowledge units to execution context")
            return context
        except Exception as e:
            logger.error(f"ACL translation failed: {e}")
            return {}
```

## Testing

```python
# tests/domain/test_bounded_contexts.py
import pytest
from uuid import uuid4
from domain.governance.entities import GovernanceDecisionAggregate
from domain.memory.entities import MemoryAggregate, KnowledgeCategory
from domain.user.entities import UserAggregate

class TestGovernanceContext:
    """Test AI Governance bounded context."""
    
    def test_law_hierarchy(self):
        """Verify law priority enforcement."""
        aggregate = GovernanceDecisionAggregate(uuid4())
        
        # First Law violation should deny
        allowed, reason = aggregate.evaluate_action(
            "delete_user_data",
            {"endangers_humans": True}
        )
        assert not allowed
        assert "First Law" in reason

class TestMemoryContext:
    """Test Memory Management bounded context."""
    
    def test_knowledge_consolidation(self):
        """Verify knowledge extraction."""
        aggregate = MemoryAggregate(uuid4())
        entry = aggregate.add_conversation(
            "I like pizza",
            "Great! I'll remember that."
        )
        
        knowledge = aggregate.consolidate_knowledge(entry)
        assert len(knowledge) > 0
        assert any(k.category == KnowledgeCategory.PREFERENCES for k in knowledge)

class TestUserContext:
    """Test User Management bounded context."""
    
    def test_password_security(self):
        """Verify password hashing."""
        aggregate = UserAggregate(uuid4(), "testuser")
        aggregate.set_password("secure_password_123")
        
        assert aggregate.verify_password("secure_password_123")
        assert not aggregate.verify_password("wrong_password")
```

## Related Documentation

- **[Domain Models](domain_models.md)** - Entity and value object patterns
- **[Domain Events](domain_events.md)** - Event definitions
- **[Aggregates](../aggregate/README.md)** - Aggregate implementations
