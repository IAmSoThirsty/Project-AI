# Domain Events in Project-AI

## Overview

Domain events are immutable facts representing state changes in the domain model. They enable loose coupling between bounded contexts, provide audit trails, and support event sourcing architecture.

## Event Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Event Flow                              │
└────────────────────────────────────────────────────────────┘

Domain Model                Event Bus              Event Handlers
     │                          │                        │
     │ 1. State Change         │                        │
     ├─────────────────►       │                        │
     │ 2. Emit Event           │                        │
     │                          │ 3. Publish Event       │
     │                          ├──────────────────────► │
     │                          │                        │ 4. Handle Event
     │                          │                        │ (Update Read Model,
     │                          │                        │  Trigger Workflow,
     │                          │                        │  Send Notification)
     │                          │                        │
     │                          │ 5. Persist to Store    │
     │                          ├──────────────────────► │
                                │                        │
                         [Event Store]           [Event Handlers]
                      (Append-only log)        (Async processing)
```

## Event Base Classes

```python
# domain/events/base.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    
    # Metadata fields
    event_id: UUID = field(default_factory=uuid4)
    event_type: str = field(init=False)
    event_version: int = 1
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: Optional[UUID] = None
    aggregate_type: Optional[str] = None
    correlation_id: Optional[UUID] = None  # For tracing related events
    causation_id: Optional[UUID] = None    # Event that caused this event
    user_id: Optional[UUID] = None         # User who triggered event
    
    # Event payload (override in subclasses)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.event_type = self.__class__.__name__
        logger.debug(f"Created event {self.event_type} with ID {self.event_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "event_version": self.event_version,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": str(self.aggregate_id) if self.aggregate_id else None,
            "aggregate_type": self.aggregate_type,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "payload": self.payload
        }
    
    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Deserialize event from dictionary."""
        return cls(
            event_id=UUID(data["event_id"]),
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            aggregate_id=UUID(data["aggregate_id"]) if data.get("aggregate_id") else None,
            correlation_id=UUID(data["correlation_id"]) if data.get("correlation_id") else None,
            causation_id=UUID(data["causation_id"]) if data.get("causation_id") else None,
            user_id=UUID(data["user_id"]) if data.get("user_id") else None,
            **data.get("payload", {})
        )
```

## Event Catalog

### AI Governance Events

```python
# domain/events/governance_events.py
from dataclasses import dataclass
from typing import Dict, List
from domain.events.base import DomainEvent

@dataclass
class ActionEvaluatedEvent(DomainEvent):
    """Event: Action was evaluated against governance laws."""
    action: str = ""
    decision: str = ""  # ALLOW, DENY
    violated_law: str = ""
    rationale: str = ""
    context: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "action": self.action,
            "decision": self.decision,
            "violated_law": self.violated_law,
            "rationale": self.rationale,
            "context": self.context
        }

@dataclass
class OverrideActivatedEvent(DomainEvent):
    """Event: Emergency override was activated."""
    override_type: str = ""
    justification: str = ""
    activated_by: str = ""
    expires_at: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "override_type": self.override_type,
            "justification": self.justification,
            "activated_by": self.activated_by,
            "expires_at": self.expires_at
        }

@dataclass
class BlackVaultEntryAddedEvent(DomainEvent):
    """Event: Entry added to Black Vault (forbidden knowledge)."""
    content_hash: str = ""
    reason: str = ""
    added_by: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "content_hash": self.content_hash,
            "reason": self.reason,
            "added_by": self.added_by
        }
```

### Memory Management Events

```python
# domain/events/memory_events.py
from dataclasses import dataclass
from typing import List
from domain.events.base import DomainEvent

@dataclass
class ConversationStartedEvent(DomainEvent):
    """Event: New conversation initiated."""
    user_id: str = ""
    initial_message: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "user_id": self.user_id,
            "initial_message": self.initial_message
        }

@dataclass
class MemoryEntryCreatedEvent(DomainEvent):
    """Event: Memory entry (conversation turn) created."""
    entry_id: str = ""
    user_message: str = ""
    ai_response: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "entry_id": self.entry_id,
            "user_message": self.user_message,
            "ai_response": self.ai_response
        }

@dataclass
class KnowledgeConsolidatedEvent(DomainEvent):
    """Event: Knowledge extracted from conversation."""
    knowledge_id: str = ""
    category: str = ""
    content: str = ""
    confidence: float = 0.0
    source_entries: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "knowledge_id": self.knowledge_id,
            "category": self.category,
            "content": self.content,
            "confidence": self.confidence,
            "source_entries": self.source_entries
        }

@dataclass
class MemoryPurgedEvent(DomainEvent):
    """Event: Old memories purged per retention policy."""
    purged_count: int = 0
    before_date: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "purged_count": self.purged_count,
            "before_date": self.before_date
        }
```

### User Management Events

```python
# domain/events/user_events.py
from dataclasses import dataclass
from domain.events.base import DomainEvent

@dataclass
class UserRegisteredEvent(DomainEvent):
    """Event: New user registered."""
    username: str = ""
    email: str = ""
    role: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "username": self.username,
            "email": self.email,
            "role": self.role
        }

@dataclass
class UserLoggedInEvent(DomainEvent):
    """Event: User authenticated successfully."""
    username: str = ""
    session_id: str = ""
    ip_address: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "username": self.username,
            "session_id": self.session_id,
            "ip_address": self.ip_address
        }

@dataclass
class PasswordChangedEvent(DomainEvent):
    """Event: User password changed."""
    username: str = ""
    changed_by: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "username": self.username,
            "changed_by": self.changed_by
        }

@dataclass
class PermissionGrantedEvent(DomainEvent):
    """Event: Permission granted to user."""
    username: str = ""
    resource: str = ""
    action: str = ""
    granted_by: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "username": self.username,
            "resource": self.resource,
            "action": self.action,
            "granted_by": self.granted_by
        }
```

### Agent Execution Events

```python
# domain/events/agent_events.py
from dataclasses import dataclass
from typing import Dict
from domain.events.base import DomainEvent

@dataclass
class AgentCreatedEvent(DomainEvent):
    """Event: Agent created."""
    agent_name: str = ""
    agent_type: str = ""
    capabilities: list = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities
        }

@dataclass
class TaskAssignedEvent(DomainEvent):
    """Event: Task assigned to agent."""
    agent_id: str = ""
    task_id: str = ""
    task_description: str = ""
    priority: str = "normal"
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "task_description": self.task_description,
            "priority": self.priority
        }

@dataclass
class TaskCompletedEvent(DomainEvent):
    """Event: Agent completed task."""
    agent_id: str = ""
    task_id: str = ""
    result: Dict = field(default_factory=dict)
    execution_time_ms: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "result": self.result,
            "execution_time_ms": self.execution_time_ms
        }

@dataclass
class WorkflowStartedEvent(DomainEvent):
    """Event: Temporal workflow started."""
    workflow_id: str = ""
    workflow_type: str = ""
    input_params: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "input_params": self.input_params
        }

@dataclass
class CouncilDecisionMadeEvent(DomainEvent):
    """Event: Agent council reached decision."""
    council_id: str = ""
    decision: str = ""
    votes: Dict[str, str] = field(default_factory=dict)
    consensus_reached: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        self.payload = {
            "council_id": self.council_id,
            "decision": self.decision,
            "votes": self.votes,
            "consensus_reached": self.consensus_reached
        }
```

---

## Event Bus

```python
# infrastructure/event_bus/in_memory_event_bus.py
from typing import Callable, Dict, List
import asyncio
import logging
from domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

class InMemoryEventBus:
    """Simple in-memory event bus for event distribution."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._async_handlers: Dict[str, List[Callable]] = {}
        logger.info("Initialized in-memory event bus")
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe synchronous handler to event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")
    
    def subscribe_async(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe asynchronous handler to event type."""
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        self._async_handlers[event_type].append(handler)
        logger.info(f"Subscribed async handler to {event_type}")
    
    def publish(self, event: DomainEvent) -> None:
        """Publish event to all subscribers (sync)."""
        try:
            logger.info(f"Publishing event {event.event_type} (ID: {event.event_id})")
            
            # Execute synchronous handlers
            handlers = self._handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    handler(event)
                    logger.debug(f"Handler {handler.__name__} processed {event.event_type}")
                except Exception as e:
                    logger.error(f"Handler {handler.__name__} failed: {e}")
            
            # Execute async handlers
            async_handlers = self._async_handlers.get(event.event_type, [])
            if async_handlers:
                asyncio.create_task(self._run_async_handlers(event, async_handlers))
        
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            raise
    
    async def _run_async_handlers(self, event: DomainEvent, handlers: List[Callable]) -> None:
        """Execute async handlers."""
        for handler in handlers:
            try:
                await handler(event)
                logger.debug(f"Async handler {handler.__name__} processed {event.event_type}")
            except Exception as e:
                logger.error(f"Async handler {handler.__name__} failed: {e}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe handler from event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]
        if event_type in self._async_handlers:
            self._async_handlers[event_type] = [h for h in self._async_handlers[event_type] if h != handler]
        logger.info(f"Unsubscribed handler from {event_type}")
```

---

## Event Handlers

```python
# application/event_handlers/governance_handlers.py
import logging
from domain.events.governance_events import ActionEvaluatedEvent, OverrideActivatedEvent
from domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

class GovernanceEventHandlers:
    """Handlers for governance domain events."""
    
    @staticmethod
    def handle_action_evaluated(event: ActionEvaluatedEvent) -> None:
        """Handle action evaluation event."""
        logger.info(f"Action '{event.action}' evaluated: {event.decision}")
        
        # Audit logging
        if event.decision == "DENY":
            logger.warning(
                f"Action denied - Law: {event.violated_law}, "
                f"Reason: {event.rationale}"
            )
            # Could trigger alert, notification, etc.
    
    @staticmethod
    def handle_override_activated(event: OverrideActivatedEvent) -> None:
        """Handle override activation event."""
        logger.warning(
            f"OVERRIDE ACTIVATED - Type: {event.override_type}, "
            f"By: {event.activated_by}, "
            f"Justification: {event.justification}"
        )
        
        # Send alert to administrators
        # Log to security audit system
        # Schedule automatic deactivation at expiry


# application/event_handlers/memory_handlers.py
class MemoryEventHandlers:
    """Handlers for memory domain events."""
    
    @staticmethod
    def handle_knowledge_consolidated(event: DomainEvent) -> None:
        """Handle knowledge consolidation event."""
        logger.info(
            f"Knowledge consolidated - Category: {event.payload['category']}, "
            f"Confidence: {event.payload['confidence']}"
        )
        
        # Update search index
        # Trigger ML model retraining
        # Update knowledge graph
    
    @staticmethod
    async def handle_conversation_started(event: DomainEvent) -> None:
        """Handle conversation start event (async)."""
        logger.info(f"Conversation started for user {event.payload['user_id']}")
        
        # Load user context
        # Prepare relevant memories
        # Initialize conversation state


# application/event_handlers/user_handlers.py
class UserEventHandlers:
    """Handlers for user domain events."""
    
    @staticmethod
    def handle_user_logged_in(event: DomainEvent) -> None:
        """Handle user login event."""
        logger.info(
            f"User {event.payload['username']} logged in from "
            f"{event.payload['ip_address']}"
        )
        
        # Update last login timestamp
        # Check for suspicious login patterns
        # Initialize user session context
    
    @staticmethod
    def handle_permission_granted(event: DomainEvent) -> None:
        """Handle permission grant event."""
        logger.info(
            f"Permission granted - User: {event.payload['username']}, "
            f"Resource: {event.payload['resource']}, "
            f"Action: {event.payload['action']}"
        )
        
        # Invalidate authorization cache
        # Audit log security change
```

---

## Event Handler Registration

```python
# infrastructure/event_bus/setup.py
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from application.event_handlers.governance_handlers import GovernanceEventHandlers
from application.event_handlers.memory_handlers import MemoryEventHandlers
from application.event_handlers.user_handlers import UserEventHandlers
import logging

logger = logging.getLogger(__name__)

def setup_event_handlers(event_bus: InMemoryEventBus) -> None:
    """Register all event handlers with event bus."""
    
    # Governance events
    event_bus.subscribe(
        "ActionEvaluatedEvent",
        GovernanceEventHandlers.handle_action_evaluated
    )
    event_bus.subscribe(
        "OverrideActivatedEvent",
        GovernanceEventHandlers.handle_override_activated
    )
    
    # Memory events
    event_bus.subscribe(
        "KnowledgeConsolidatedEvent",
        MemoryEventHandlers.handle_knowledge_consolidated
    )
    event_bus.subscribe_async(
        "ConversationStartedEvent",
        MemoryEventHandlers.handle_conversation_started
    )
    
    # User events
    event_bus.subscribe(
        "UserLoggedInEvent",
        UserEventHandlers.handle_user_logged_in
    )
    event_bus.subscribe(
        "PermissionGrantedEvent",
        UserEventHandlers.handle_permission_granted
    )
    
    logger.info("Registered all event handlers")
```

---

## Event Sourcing Integration

```python
# infrastructure/event_store/event_sourced_aggregate.py
from typing import List
from uuid import UUID
from domain.base.aggregate import AggregateRoot
from domain.events.base import DomainEvent
import logging

logger = logging.getLogger(__name__)

class EventSourcedAggregate(AggregateRoot):
    """Aggregate that rebuilds state from events."""
    
    def __init__(self, aggregate_id: UUID):
        super().__init__(aggregate_id)
        self._uncommitted_events: List[DomainEvent] = []
    
    def load_from_history(self, events: List[DomainEvent]) -> None:
        """Reconstruct aggregate from event stream."""
        logger.info(f"Loading aggregate {self.id} from {len(events)} events")
        
        for event in events:
            self._apply_event(event)
            self.increment_version()
        
        logger.info(f"Loaded aggregate {self.id} at version {self.version}")
    
    def _apply_event(self, event: DomainEvent) -> None:
        """Apply event to aggregate state."""
        handler_name = f"_apply_{event.event_type}"
        handler = getattr(self, handler_name, None)
        
        if handler:
            handler(event)
        else:
            logger.warning(f"No handler for {event.event_type} on {self.__class__.__name__}")
    
    def raise_event(self, event: DomainEvent) -> None:
        """Raise new domain event and apply to state."""
        event.aggregate_id = self.id
        event.aggregate_type = self.__class__.__name__
        
        # Apply to current state
        self._apply_event(event)
        
        # Track for persistence
        self._uncommitted_events.append(event)
        self.increment_version()
        
        logger.debug(f"Raised event {event.event_type} on aggregate {self.id}")
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get events not yet persisted."""
        events = self._uncommitted_events.copy()
        self._uncommitted_events.clear()
        return events
```

---

## Testing

```python
# tests/domain/test_domain_events.py
import pytest
from uuid import uuid4
from domain.events.governance_events import ActionEvaluatedEvent
from domain.events.memory_events import KnowledgeConsolidatedEvent
from infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus

class TestDomainEvents:
    """Test domain event functionality."""
    
    def test_event_creation(self):
        """Verify event creation and metadata."""
        event = ActionEvaluatedEvent(
            action="test_action",
            decision="ALLOW",
            rationale="All laws satisfied"
        )
        
        assert event.event_id is not None
        assert event.event_type == "ActionEvaluatedEvent"
        assert event.occurred_at is not None
        assert event.action == "test_action"
    
    def test_event_serialization(self):
        """Verify event serialization."""
        event = KnowledgeConsolidatedEvent(
            knowledge_id=str(uuid4()),
            category="facts",
            content="The sky is blue",
            confidence=0.95
        )
        
        event_dict = event.to_dict()
        assert event_dict["event_type"] == "KnowledgeConsolidatedEvent"
        assert event_dict["payload"]["category"] == "facts"
        
        json_str = event.to_json()
        assert "KnowledgeConsolidatedEvent" in json_str
    
    def test_event_bus_publish_subscribe(self):
        """Verify event bus functionality."""
        bus = InMemoryEventBus()
        handled_events = []
        
        def handler(event):
            handled_events.append(event)
        
        bus.subscribe("ActionEvaluatedEvent", handler)
        
        event = ActionEvaluatedEvent(
            action="test",
            decision="DENY",
            violated_law="FIRST_LAW",
            rationale="Endangers user"
        )
        
        bus.publish(event)
        
        assert len(handled_events) == 1
        assert handled_events[0].action == "test"
```

## Performance Considerations

### Event Storage
- Use append-only event store for performance
- Implement event snapshots for large aggregates
- Archive old events to cold storage

### Event Distribution
- Use message queue for reliable delivery
- Implement retry logic for failed handlers
- Consider event batching for high throughput

### Event Processing
- Process events asynchronously when possible
- Use dead letter queue for failed events
- Monitor handler execution times

## Related Documentation

- **[Event Sourcing](../event/README.md)** - Event store implementation
- **[Aggregates](../aggregate/README.md)** - Event-sourced aggregates
- **[Command Handlers](../command/command_handlers.md)** - Command to event flow
