# Domain-Driven Design (DDD) in Project-AI

## Overview

Project-AI implements tactical and strategic DDD patterns to model complex AI governance, memory management, and agent orchestration domains with explicit bounded contexts, ubiquitous language, and rich domain models.

## Bounded Contexts

```
┌─────────────────────────────────────────────────────────────┐
│                    Project-AI System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────┐      ┌────────────────────┐         │
│  │  AI Governance     │      │  Memory Management │         │
│  │  Context           │◄────►│  Context           │         │
│  │                    │      │                    │         │
│  │ - FourLaws         │      │ - Conversations    │         │
│  │ - Oversight        │      │ - Knowledge Base   │         │
│  │ - Validation       │      │ - Consolidation    │         │
│  └────────────────────┘      └────────────────────┘         │
│           ▲                           ▲                      │
│           │                           │                      │
│           ▼                           ▼                      │
│  ┌────────────────────┐      ┌────────────────────┐         │
│  │  User Management   │      │  Agent Execution   │         │
│  │  Context           │      │  Context           │         │
│  │                    │      │                    │         │
│  │ - Authentication   │      │ - Workflows        │         │
│  │ - Authorization    │      │ - Task Execution   │         │
│  │ - Profiles         │      │ - Council Mgmt     │         │
│  └────────────────────┘      └────────────────────┘         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Ubiquitous Language

### AI Governance Context
- **Law**: Immutable ethical rule (Asimov's Laws hierarchy)
- **Oversight**: Pre-execution action validation against laws
- **Governance Decision**: Result of law evaluation with rationale
- **Black Vault**: Repository of forbidden knowledge/actions
- **Override**: Emergency mechanism to bypass governance (audited)

### Memory Management Context
- **Conversation**: Chronological sequence of user-AI interactions
- **Memory Entry**: Single conversation turn with metadata
- **Knowledge Unit**: Atomic piece of learned information
- **Consolidation**: Process of converting conversations to knowledge
- **Category**: Semantic grouping of knowledge (facts, skills, preferences, etc.)

### User Management Context
- **User**: Authenticated human actor with credentials
- **Profile**: User preferences and configuration
- **Session**: Time-bound authenticated interaction
- **Credential**: Authentication material (password hash, API key)
- **Permission**: Authorization rule for resource access

### Agent Execution Context
- **Agent**: Autonomous AI entity with specialized capability
- **Workflow**: Temporal-orchestrated multi-step process
- **Task**: Unit of work assigned to agent
- **Council**: Collective of agents for collaborative decision-making
- **Execution Context**: Environment snapshot for agent execution

## Domain Model Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Application Layer                                           │
│  - Command Handlers                                          │
│  - Query Handlers                                            │
│  - Application Services                                      │
├─────────────────────────────────────────────────────────────┤
│  Domain Layer                                                │
│  - Entities                                                  │
│  - Value Objects                                             │
│  - Aggregates                                                │
│  - Domain Services                                           │
│  - Domain Events                                             │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                        │
│  - Repositories                                              │
│  - Event Store                                               │
│  - External Services                                         │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

### 1. **Bounded Context Isolation**
Each context has:
- Independent domain model
- Dedicated persistence
- Context-specific ubiquitous language
- Anti-corruption layers at boundaries

### 2. **Aggregate Design**
Aggregates enforce:
- Transactional consistency boundaries
- Invariant protection
- Single root entity
- Internal change management

### 3. **Domain Event Propagation**
Events enable:
- Cross-context communication
- Event sourcing for audit trail
- Asynchronous processing
- Eventual consistency

### 4. **Rich Domain Models**
Models contain:
- Business logic in entities
- Validation rules
- State transitions
- Domain-specific operations

## Implementation Strategy

### Tactical Patterns
1. **Entities**: Objects with identity and lifecycle
2. **Value Objects**: Immutable objects defined by attributes
3. **Aggregates**: Consistency boundaries with single root
4. **Domain Services**: Operations that don't belong to entities
5. **Domain Events**: State change notifications
6. **Repositories**: Persistence abstraction

### Strategic Patterns
1. **Bounded Contexts**: Explicit model boundaries
2. **Context Mapping**: Inter-context relationships
3. **Anti-Corruption Layers**: Translation between contexts
4. **Shared Kernel**: Common domain model elements
5. **Customer-Supplier**: Upstream/downstream relationships

## Context Map

```
┌─────────────────────────────────────────────────────────────┐
│                     Context Relationships                    │
└─────────────────────────────────────────────────────────────┘

User Management (U) ──[Customer-Supplier]──► AI Governance (P)
        │
        │ [Shared Kernel: UserIdentity]
        │
        └──────────────────────────────► Memory Management (C)
        
AI Governance (U) ──[Partnership]──► Agent Execution (P)

Memory Management (U) ──[Anti-Corruption Layer]──► Agent Execution (D)

Legend:
  U = Upstream
  D = Downstream  
  P = Partnership
  C = Conformist
```

## Domain Events Flow

```
User Action
    │
    ▼
┌─────────────────┐
│ Command Handler │
│                 │
│ 1. Validate     │
│ 2. Load Agg     │
│ 3. Execute      │
│ 4. Emit Events  │
│ 5. Save         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Event Store    │◄────────── Append-only log
│                 │            Full audit trail
│  Event Bus      │
└────────┬────────┘
         │
         ├────────────────┬────────────────┬──────────────►
         ▼                ▼                ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │Handler 1│     │Handler 2│     │Handler 3│
    │(Context │     │(Context │     │(External│
    │  A)     │     │  B)     │     │ System) │
    └─────────┘     └─────────┘     └─────────┘
```

## Benefits Achieved

### 1. **Model Clarity**
- Clear separation between business domains
- Explicit vocabulary understood by developers and domain experts
- Self-documenting code structure

### 2. **Maintainability**
- Isolated changes within bounded contexts
- Protected invariants through aggregates
- Testable domain logic independent of infrastructure

### 3. **Scalability**
- Independent deployment of bounded contexts
- Async communication via events
- Loose coupling between contexts

### 4. **Auditability**
- Event sourcing provides complete history
- Reproducible state from event replay
- Compliance and debugging capabilities

## Python Implementation Example

```python
# domain/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

@dataclass
class DomainEvent:
    """Base class for all domain events."""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: Optional[UUID] = None
    event_type: str = field(init=False)
    
    def __post_init__(self):
        self.event_type = self.__class__.__name__

class Entity(ABC):
    """Base class for entities with identity."""
    
    def __init__(self, entity_id: UUID):
        self.id = entity_id
        self._domain_events: List[DomainEvent] = []
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to entity."""
        event.aggregate_id = self.id
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)

@dataclass(frozen=True)
class ValueObject:
    """Base class for immutable value objects."""
    
    def __post_init__(self):
        self._validate()
    
    @abstractmethod
    def _validate(self) -> None:
        """Validate value object invariants."""
        pass

class AggregateRoot(Entity):
    """Base class for aggregate roots."""
    
    def __init__(self, aggregate_id: UUID):
        super().__init__(aggregate_id)
        self.version = 0
    
    def increment_version(self) -> None:
        """Increment aggregate version for optimistic concurrency."""
        self.version += 1
```

## Integration Points

### With CQRS
- Commands modify aggregates
- Queries read denormalized views
- Events sync write/read models

### With Event Sourcing
- Aggregates reconstructed from events
- State derived from event stream
- Time-travel debugging possible

### With Microservices
- Bounded contexts map to services
- Events enable cross-service communication
- Each service owns its data

## Testing Strategy

```python
# tests/domain/test_aggregate.py
import pytest
from uuid import uuid4
from domain.governance import GovernanceDecision, Law

class TestGovernanceAggregate:
    """Test aggregate behavior and invariants."""
    
    def test_decision_creation_emits_event(self):
        """Verify domain event emission."""
        aggregate = GovernanceDecision(uuid4())
        aggregate.evaluate_action("delete_file", context={"user": "admin"})
        
        events = aggregate.clear_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "ActionEvaluated"
    
    def test_invariant_protection(self):
        """Verify invariants are enforced."""
        aggregate = GovernanceDecision(uuid4())
        
        with pytest.raises(ValueError):
            aggregate.evaluate_action("", context={})  # Empty action
    
    def test_aggregate_consistency(self):
        """Verify transactional consistency."""
        aggregate = GovernanceDecision(uuid4())
        
        # All changes succeed or fail together
        aggregate.evaluate_action("action1", {})
        aggregate.evaluate_action("action2", {})
        
        assert aggregate.decision_count == 2
```

## Related Documentation

- **[Bounded Contexts](bounded_contexts.md)** - Detailed context definitions
- **[Domain Models](domain_models.md)** - Entity and value object patterns
- **[Domain Events](domain_events.md)** - Event definitions and handlers
- **[Aggregates](../aggregate/README.md)** - Aggregate implementations
- **[Command Pattern](../command/README.md)** - CQRS command side
- **[Event Sourcing](../event/README.md)** - Event store architecture

## References

- Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software"
- Vaughn Vernon, "Implementing Domain-Driven Design"
- Vernon, "Domain-Driven Design Distilled"
- Martin Fowler, "Patterns of Enterprise Application Architecture"
