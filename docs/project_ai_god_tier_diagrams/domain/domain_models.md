# Domain Models: Entities, Value Objects, and Aggregates

## Overview

Project-AI implements rich domain models using tactical DDD patterns: Entities (identity-based objects), Value Objects (immutable attribute-based objects), and Aggregates (consistency boundaries).

## Pattern Taxonomy

```
Domain Models
├── Entities
│   ├── Has identity (UUID)
│   ├── Has lifecycle
│   ├── Mutable state
│   └── Equality by ID
├── Value Objects
│   ├── No identity
│   ├── Immutable
│   ├── Equality by attributes
│   └── Replaceable
└── Aggregates
    ├── Cluster of entities/VOs
    ├── Single root entity
    ├── Consistency boundary
    └── Transaction scope
```

## Entity Pattern

### Base Entity

```python
# domain/base/entity.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

@dataclass
class DomainEvent:
    """Base domain event."""
    event_id: UUID = field(default_factory=uuid4)
    event_type: str = field(init=False)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: UUID = None
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.event_type = self.__class__.__name__
        logger.debug(f"Created event {self.event_type} with ID {self.event_id}")

class Entity(ABC):
    """Base entity with identity and lifecycle."""
    
    def __init__(self, entity_id: UUID):
        self.id = entity_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._domain_events: List[DomainEvent] = []
        logger.info(f"Created entity {self.__class__.__name__} with ID {entity_id}")
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event to entity."""
        event.aggregate_id = self.id
        self._domain_events.append(event)
        logger.debug(f"Added event {event.event_type} to entity {self.id}")
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        logger.debug(f"Cleared {len(events)} events from entity {self.id}")
        return events
    
    def _touch(self) -> None:
        """Update modification timestamp."""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        """Entities are equal if IDs match."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID for set/dict usage."""
        return hash(self.id)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
```

### Concrete Entity Example: Agent

```python
# domain/agent/entities.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from domain.base.entity import Entity, DomainEvent
import logging

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent lifecycle states."""
    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class AgentType(Enum):
    """Agent specializations."""
    OVERSIGHT = "oversight"
    PLANNER = "planner"
    VALIDATOR = "validator"
    EXPLAINER = "explainer"
    EXECUTOR = "executor"

@dataclass
class AgentCreatedEvent(DomainEvent):
    """Event: Agent was created."""
    agent_name: str = ""
    agent_type: str = ""

@dataclass
class AgentStatusChangedEvent(DomainEvent):
    """Event: Agent status changed."""
    old_status: str = ""
    new_status: str = ""

class Agent(Entity):
    """Agent entity with specialized capabilities."""
    
    def __init__(
        self,
        agent_id: UUID,
        name: str,
        agent_type: AgentType,
        capabilities: List[str]
    ):
        super().__init__(agent_id)
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.task_history: List[Dict] = []
        self.metrics: Dict[str, int] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time_ms": 0
        }
        
        # Emit creation event
        event = AgentCreatedEvent(
            agent_name=name,
            agent_type=agent_type.value
        )
        self.add_domain_event(event)
        
        logger.info(f"Created agent {name} of type {agent_type.value}")
    
    def assign_task(self, task: Dict) -> None:
        """Assign task to agent."""
        if self.status != AgentStatus.IDLE:
            raise ValueError(f"Agent {self.name} is not idle (status: {self.status.value})")
        
        self._change_status(AgentStatus.BUSY)
        self.task_history.append({
            "task_id": str(uuid4()),
            "task": task,
            "started_at": datetime.utcnow().isoformat(),
            "status": "in_progress"
        })
        self._touch()
        logger.info(f"Assigned task to agent {self.name}")
    
    def complete_task(self, result: Dict) -> None:
        """Mark current task as completed."""
        if not self.task_history or self.task_history[-1]["status"] != "in_progress":
            raise ValueError("No task in progress")
        
        self.task_history[-1]["status"] = "completed"
        self.task_history[-1]["completed_at"] = datetime.utcnow().isoformat()
        self.task_history[-1]["result"] = result
        
        self.metrics["tasks_completed"] += 1
        self._change_status(AgentStatus.IDLE)
        self._touch()
        logger.info(f"Agent {self.name} completed task")
    
    def fail_task(self, error: str) -> None:
        """Mark current task as failed."""
        if not self.task_history or self.task_history[-1]["status"] != "in_progress":
            raise ValueError("No task in progress")
        
        self.task_history[-1]["status"] = "failed"
        self.task_history[-1]["completed_at"] = datetime.utcnow().isoformat()
        self.task_history[-1]["error"] = error
        
        self.metrics["tasks_failed"] += 1
        self._change_status(AgentStatus.ERROR)
        self._touch()
        logger.error(f"Agent {self.name} failed task: {error}")
    
    def _change_status(self, new_status: AgentStatus) -> None:
        """Change agent status and emit event."""
        old_status = self.status
        self.status = new_status
        
        event = AgentStatusChangedEvent(
            old_status=old_status.value,
            new_status=new_status.value
        )
        self.add_domain_event(event)
        logger.info(f"Agent {self.name} status: {old_status.value} → {new_status.value}")
    
    def get_success_rate(self) -> float:
        """Calculate task success rate."""
        total = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total == 0:
            return 0.0
        return self.metrics["tasks_completed"] / total
```

---

## Value Object Pattern

### Base Value Object

```python
# domain/base/value_object.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ValueObject(ABC):
    """Base immutable value object."""
    
    def __post_init__(self):
        """Validate on construction."""
        try:
            self._validate()
            logger.debug(f"Created value object {self.__class__.__name__}")
        except Exception as e:
            logger.error(f"Value object validation failed: {e}")
            raise
    
    @abstractmethod
    def _validate(self) -> None:
        """Validate value object invariants."""
        pass
    
    def __eq__(self, other: Any) -> bool:
        """Value objects equal by attributes."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """Hash all attributes for set/dict usage."""
        return hash(tuple(sorted(self.__dict__.items())))
```

### Concrete Value Objects

```python
# domain/user/value_objects.py
from dataclasses import dataclass
from typing import Optional
import re
from domain.base.value_object import ValueObject

@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """Email address value object."""
    address: str
    
    def _validate(self) -> None:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.address):
            raise ValueError(f"Invalid email address: {self.address}")
    
    def domain(self) -> str:
        """Extract domain part."""
        return self.address.split('@')[1]
    
    def __str__(self) -> str:
        return self.address

@dataclass(frozen=True)
class Username(ValueObject):
    """Username value object."""
    value: str
    
    def _validate(self) -> None:
        """Validate username rules."""
        if not 3 <= len(self.value) <= 50:
            raise ValueError("Username must be 3-50 characters")
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.value):
            raise ValueError("Username can only contain alphanumeric, underscore, hyphen")
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class Money(ValueObject):
    """Money value object with currency."""
    amount: float
    currency: str = "USD"
    
    def _validate(self) -> None:
        """Validate money invariants."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency not in ["USD", "EUR", "GBP"]:
            raise ValueError(f"Unsupported currency: {self.currency}")
    
    def add(self, other: 'Money') -> 'Money':
        """Add money (same currency)."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

@dataclass(frozen=True)
class DateRange(ValueObject):
    """Date range value object."""
    start_date: str  # ISO format
    end_date: str    # ISO format
    
    def _validate(self) -> None:
        """Validate date range."""
        from datetime import datetime
        start = datetime.fromisoformat(self.start_date)
        end = datetime.fromisoformat(self.end_date)
        if start >= end:
            raise ValueError("Start date must be before end date")
    
    def duration_days(self) -> int:
        """Calculate duration in days."""
        from datetime import datetime
        start = datetime.fromisoformat(self.start_date)
        end = datetime.fromisoformat(self.end_date)
        return (end - start).days
```

---

## Aggregate Pattern

### Base Aggregate Root

```python
# domain/base/aggregate.py
from typing import List, Optional
from uuid import UUID
from domain.base.entity import Entity, DomainEvent
import logging

logger = logging.getLogger(__name__)

class AggregateRoot(Entity):
    """Base aggregate root with version for optimistic concurrency."""
    
    def __init__(self, aggregate_id: UUID):
        super().__init__(aggregate_id)
        self.version = 0
        logger.info(f"Created aggregate root {aggregate_id} at version 0")
    
    def increment_version(self) -> None:
        """Increment version for optimistic locking."""
        self.version += 1
        logger.debug(f"Incremented aggregate {self.id} to version {self.version}")
    
    def apply_event(self, event: DomainEvent) -> None:
        """Apply event to aggregate (for event sourcing)."""
        handler_name = f"_apply_{event.event_type}"
        handler = getattr(self, handler_name, None)
        
        if handler:
            handler(event)
            self.increment_version()
            logger.debug(f"Applied event {event.event_type} to aggregate {self.id}")
        else:
            logger.warning(f"No handler for event {event.event_type} on {self.__class__.__name__}")
    
    def load_from_history(self, events: List[DomainEvent]) -> None:
        """Reconstruct aggregate from event history."""
        logger.info(f"Loading aggregate {self.id} from {len(events)} events")
        for event in events:
            self.apply_event(event)
        logger.info(f"Loaded aggregate {self.id} to version {self.version}")
```

### Concrete Aggregate: Order

```python
# domain/order/aggregate.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List
from uuid import UUID, uuid4
from domain.base.aggregate import AggregateRoot
from domain.base.entity import DomainEvent
from domain.user.value_objects import Money
import logging

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    """Order lifecycle states."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class OrderItem:
    """Order line item (entity within aggregate)."""
    item_id: UUID
    product_name: str
    quantity: int
    unit_price: Money
    
    def total_price(self) -> Money:
        """Calculate line item total."""
        return Money(
            self.unit_price.amount * self.quantity,
            self.unit_price.currency
        )

@dataclass
class OrderSubmittedEvent(DomainEvent):
    """Event: Order was submitted."""
    order_id: str = ""
    total_amount: float = 0.0
    currency: str = "USD"

@dataclass
class OrderApprovedEvent(DomainEvent):
    """Event: Order was approved."""
    order_id: str = ""
    approved_by: str = ""

class OrderAggregate(AggregateRoot):
    """Order aggregate managing order lifecycle."""
    
    def __init__(self, order_id: UUID, customer_id: UUID):
        super().__init__(order_id)
        self.customer_id = customer_id
        self.status = OrderStatus.DRAFT
        self.items: List[OrderItem] = []
        self.submitted_at: Optional[datetime] = None
        self.approved_at: Optional[datetime] = None
        self.approved_by: Optional[str] = None
        logger.info(f"Created order aggregate {order_id} for customer {customer_id}")
    
    def add_item(self, product_name: str, quantity: int, unit_price: Money) -> None:
        """Add item to order (only in DRAFT)."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot add items to order in status {self.status.value}")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        item = OrderItem(
            item_id=uuid4(),
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price
        )
        self.items.append(item)
        self._touch()
        logger.info(f"Added item {product_name} (qty: {quantity}) to order {self.id}")
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove item from order (only in DRAFT)."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot remove items from order in status {self.status.value}")
        
        self.items = [item for item in self.items if item.item_id != item_id]
        self._touch()
        logger.info(f"Removed item {item_id} from order {self.id}")
    
    def calculate_total(self) -> Money:
        """Calculate order total."""
        if not self.items:
            return Money(0.0)
        
        total = Money(0.0, self.items[0].unit_price.currency)
        for item in self.items:
            total = total.add(item.total_price())
        return total
    
    def submit(self) -> None:
        """Submit order for approval."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot submit order in status {self.status.value}")
        
        if not self.items:
            raise ValueError("Cannot submit empty order")
        
        self.status = OrderStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        
        total = self.calculate_total()
        event = OrderSubmittedEvent(
            order_id=str(self.id),
            total_amount=total.amount,
            currency=total.currency
        )
        self.add_domain_event(event)
        self.increment_version()
        self._touch()
        logger.info(f"Submitted order {self.id} (total: {total})")
    
    def approve(self, approver: str) -> None:
        """Approve submitted order."""
        if self.status != OrderStatus.SUBMITTED:
            raise ValueError(f"Cannot approve order in status {self.status.value}")
        
        self.status = OrderStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = approver
        
        event = OrderApprovedEvent(
            order_id=str(self.id),
            approved_by=approver
        )
        self.add_domain_event(event)
        self.increment_version()
        self._touch()
        logger.info(f"Approved order {self.id} by {approver}")
    
    def reject(self, reason: str) -> None:
        """Reject submitted order."""
        if self.status != OrderStatus.SUBMITTED:
            raise ValueError(f"Cannot reject order in status {self.status.value}")
        
        self.status = OrderStatus.REJECTED
        self._touch()
        logger.info(f"Rejected order {self.id}: {reason}")
    
    def cancel(self) -> None:
        """Cancel order (allowed before completion)."""
        if self.status == OrderStatus.COMPLETED:
            raise ValueError("Cannot cancel completed order")
        
        self.status = OrderStatus.CANCELLED
        self._touch()
        logger.info(f"Cancelled order {self.id}")
    
    # Event sourcing handlers
    def _apply_OrderSubmittedEvent(self, event: OrderSubmittedEvent) -> None:
        """Apply order submitted event."""
        self.status = OrderStatus.SUBMITTED
        self.submitted_at = event.occurred_at
    
    def _apply_OrderApprovedEvent(self, event: OrderApprovedEvent) -> None:
        """Apply order approved event."""
        self.status = OrderStatus.APPROVED
        self.approved_at = event.occurred_at
        self.approved_by = event.payload.get("approved_by")
```

---

## Repository Pattern

```python
# infrastructure/repositories/order_repository.py
import json
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID
from domain.order.aggregate import OrderAggregate

logger = logging.getLogger(__name__)

class OrderRepository:
    """Repository for order aggregates."""
    
    def __init__(self, data_dir: str = "data/orders"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized order repository at {data_dir}")
    
    def save(self, aggregate: OrderAggregate) -> None:
        """Persist aggregate with optimistic concurrency check."""
        try:
            filepath = self.data_dir / f"{aggregate.id}.json"
            
            # Check version for optimistic locking
            if filepath.exists():
                with open(filepath, 'r') as f:
                    existing = json.load(f)
                if existing["version"] != aggregate.version - 1:
                    raise ValueError(
                        f"Concurrency conflict: expected version {aggregate.version - 1}, "
                        f"found {existing['version']}"
                    )
            
            data = {
                "id": str(aggregate.id),
                "customer_id": str(aggregate.customer_id),
                "status": aggregate.status.value,
                "version": aggregate.version,
                "items": [
                    {
                        "item_id": str(item.item_id),
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price.amount,
                        "currency": item.unit_price.currency
                    }
                    for item in aggregate.items
                ],
                "submitted_at": aggregate.submitted_at.isoformat() if aggregate.submitted_at else None,
                "approved_at": aggregate.approved_at.isoformat() if aggregate.approved_at else None,
                "approved_by": aggregate.approved_by
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved order aggregate {aggregate.id} version {aggregate.version}")
        except Exception as e:
            logger.error(f"Failed to save order aggregate: {e}")
            raise
    
    def load(self, aggregate_id: UUID) -> Optional[OrderAggregate]:
        """Load aggregate by ID."""
        try:
            filepath = self.data_dir / f"{aggregate_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            from domain.user.value_objects import Money
            
            aggregate = OrderAggregate(
                order_id=UUID(data["id"]),
                customer_id=UUID(data["customer_id"])
            )
            aggregate.status = OrderStatus[data["status"].upper()]
            aggregate.version = data["version"]
            
            for item_data in data["items"]:
                aggregate.items.append(OrderItem(
                    item_id=UUID(item_data["item_id"]),
                    product_name=item_data["product_name"],
                    quantity=item_data["quantity"],
                    unit_price=Money(item_data["unit_price"], item_data["currency"])
                ))
            
            logger.info(f"Loaded order aggregate {aggregate_id}")
            return aggregate
        except Exception as e:
            logger.error(f"Failed to load order aggregate: {e}")
            return None
```

---

## Testing

```python
# tests/domain/test_domain_models.py
import pytest
from uuid import uuid4
from domain.agent.entities import Agent, AgentType, AgentStatus
from domain.user.value_objects import EmailAddress, Username, Money
from domain.order.aggregate import OrderAggregate, OrderStatus

class TestEntity:
    """Test entity pattern."""
    
    def test_entity_identity(self):
        """Verify entity equality by ID."""
        agent_id = uuid4()
        agent1 = Agent(agent_id, "agent1", AgentType.OVERSIGHT, [])
        agent2 = Agent(agent_id, "agent2", AgentType.PLANNER, [])
        
        assert agent1 == agent2  # Same ID
        assert hash(agent1) == hash(agent2)
    
    def test_entity_lifecycle(self):
        """Verify entity state changes."""
        agent = Agent(uuid4(), "test", AgentType.EXECUTOR, ["task_exec"])
        assert agent.status == AgentStatus.IDLE
        
        agent.assign_task({"action": "test"})
        assert agent.status == AgentStatus.BUSY
        
        agent.complete_task({"result": "success"})
        assert agent.status == AgentStatus.IDLE
        assert agent.metrics["tasks_completed"] == 1
    
    def test_domain_events(self):
        """Verify domain event emission."""
        agent = Agent(uuid4(), "test", AgentType.VALIDATOR, [])
        events = agent.clear_domain_events()
        
        assert len(events) == 1
        assert events[0].event_type == "AgentCreatedEvent"

class TestValueObject:
    """Test value object pattern."""
    
    def test_value_object_immutability(self):
        """Verify value objects are immutable."""
        email = EmailAddress("test@example.com")
        
        with pytest.raises(Exception):  # dataclass frozen
            email.address = "changed@example.com"
    
    def test_value_object_validation(self):
        """Verify value object invariants."""
        with pytest.raises(ValueError):
            EmailAddress("invalid-email")
        
        with pytest.raises(ValueError):
            Username("ab")  # Too short
        
        with pytest.raises(ValueError):
            Money(-10.0)  # Negative amount
    
    def test_value_object_equality(self):
        """Verify equality by attributes."""
        email1 = EmailAddress("test@example.com")
        email2 = EmailAddress("test@example.com")
        email3 = EmailAddress("other@example.com")
        
        assert email1 == email2
        assert email1 != email3
        assert hash(email1) == hash(email2)
    
    def test_value_object_operations(self):
        """Verify value object methods."""
        money1 = Money(10.0, "USD")
        money2 = Money(5.0, "USD")
        total = money1.add(money2)
        
        assert total.amount == 15.0
        assert total.currency == "USD"

class TestAggregate:
    """Test aggregate pattern."""
    
    def test_aggregate_consistency_boundary(self):
        """Verify aggregate enforces invariants."""
        order = OrderAggregate(uuid4(), uuid4())
        
        # Cannot submit empty order
        with pytest.raises(ValueError):
            order.submit()
        
        # Add items and submit
        order.add_item("Product A", 2, Money(10.0))
        order.submit()
        
        # Cannot add items after submission
        with pytest.raises(ValueError):
            order.add_item("Product B", 1, Money(5.0))
    
    def test_aggregate_versioning(self):
        """Verify optimistic concurrency."""
        order = OrderAggregate(uuid4(), uuid4())
        assert order.version == 0
        
        order.add_item("Product", 1, Money(10.0))
        order.submit()
        assert order.version == 1
        
        order.approve("admin")
        assert order.version == 2
    
    def test_aggregate_events(self):
        """Verify aggregate emits domain events."""
        order = OrderAggregate(uuid4(), uuid4())
        order.add_item("Product", 1, Money(10.0))
        order.submit()
        
        events = order.clear_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "OrderSubmittedEvent"
```

## Performance Considerations

### Entity Loading
- Lazy load related entities to avoid N+1 queries
- Use eager loading for frequently accessed relationships
- Implement caching for read-heavy entities

### Value Object Creation
- Value objects are immutable - safe to share instances
- Consider object pooling for frequently used VOs
- Use __slots__ for memory optimization

### Aggregate Size
- Keep aggregates small (< 10 entities)
- Large aggregates indicate wrong boundaries
- Consider splitting into separate aggregates

## Related Documentation

- **[Aggregates](../aggregate/README.md)** - Detailed aggregate implementations
- **[Domain Events](domain_events.md)** - Event definitions and handlers
- **[Bounded Contexts](bounded_contexts.md)** - Context-specific models
