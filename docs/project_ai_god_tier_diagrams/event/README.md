# Event Sourcing in Project-AI

## Overview

Event Sourcing persists aggregate state as a sequence of domain events rather than current state snapshots. This enables complete audit trails, time-travel debugging, and event replay for state reconstruction.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│              Event Sourcing Architecture                    │
└────────────────────────────────────────────────────────────┘

Command → Aggregate → Events → Event Store (Append-Only)
                                      │
                                      ├──► Event Bus → Handlers
                                      │
                                      └──► Event Replay → Rebuild State
```

## Event Store Implementation

```python
# infrastructure/event_store/event_store.py
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID
from domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

class EventStore:
    """Append-only event store for domain events."""
    
    def __init__(self, storage_dir: str = "data/events"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._initialize_index()
        logger.info(f"Initialized event store at {storage_dir}")
    
    def _initialize_index(self) -> None:
        """Initialize event index if not exists."""
        if not self.index_file.exists():
            with open(self.index_file, 'w') as f:
                json.dump({"aggregates": {}, "total_events": 0}, f)
    
    def append_event(self, event: DomainEvent) -> None:
        """Append event to store (immutable)."""
        try:
            # Get aggregate stream file
            stream_file = self._get_stream_file(event.aggregate_id)
            
            # Append event
            with open(stream_file, 'a') as f:
                f.write(event.to_json() + '\n')
            
            # Update index
            self._update_index(event)
            
            logger.info(
                f"Appended event {event.event_type} for aggregate {event.aggregate_id}"
            )
        except Exception as e:
            logger.error(f"Failed to append event: {e}")
            raise
    
    def load_events(
        self,
        aggregate_id: UUID,
        from_version: int = 0
    ) -> List[DomainEvent]:
        """Load event stream for aggregate."""
        try:
            stream_file = self._get_stream_file(aggregate_id)
            
            if not stream_file.exists():
                return []
            
            events = []
            with open(stream_file, 'r') as f:
                for line in f:
                    event_data = json.loads(line)
                    event = self._deserialize_event(event_data)
                    events.append(event)
            
            # Filter by version
            if from_version > 0:
                events = events[from_version:]
            
            logger.info(f"Loaded {len(events)} events for aggregate {aggregate_id}")
            return events
        except Exception as e:
            logger.error(f"Failed to load events: {e}")
            return []
    
    def get_event_count(self, aggregate_id: UUID) -> int:
        """Get total events for aggregate."""
        events = self.load_events(aggregate_id)
        return len(events)
    
    def _get_stream_file(self, aggregate_id: UUID) -> Path:
        """Get event stream file path for aggregate."""
        return self.storage_dir / f"{aggregate_id}.events.jsonl"
    
    def _update_index(self, event: DomainEvent) -> None:
        """Update event index."""
        with open(self.index_file, 'r') as f:
            index = json.load(f)
        
        agg_id = str(event.aggregate_id)
        if agg_id not in index["aggregates"]:
            index["aggregates"][agg_id] = {
                "event_count": 0,
                "last_event_at": None
            }
        
        index["aggregates"][agg_id]["event_count"] += 1
        index["aggregates"][agg_id]["last_event_at"] = event.occurred_at.isoformat()
        index["total_events"] += 1
        
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _deserialize_event(self, data: dict) -> DomainEvent:
        """Deserialize event from JSON (basic implementation)."""
        # In production, use event type registry
        from domain.events.base import DomainEvent
        event = DomainEvent()
        event.__dict__.update(data)
        return event
```

## Event Replay

```python
# infrastructure/event_store/event_replay.py
import logging
from typing import List, Type, TypeVar
from uuid import UUID
from domain.base.aggregate import AggregateRoot
from domain.events.base import DomainEvent
from infrastructure.event_store.event_store import EventStore

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=AggregateRoot)

class EventReplay:
    """Event replay for aggregate reconstruction."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        logger.info("Initialized event replay")
    
    def rebuild_aggregate(
        self,
        aggregate_type: Type[T],
        aggregate_id: UUID
    ) -> T:
        """Rebuild aggregate from event history."""
        try:
            # Load events
            events = self.event_store.load_events(aggregate_id)
            
            if not events:
                raise ValueError(f"No events found for aggregate {aggregate_id}")
            
            # Create aggregate
            aggregate = aggregate_type(aggregate_id)
            
            # Apply events
            for event in events:
                aggregate.apply_event(event)
            
            logger.info(
                f"Rebuilt {aggregate_type.__name__} {aggregate_id} "
                f"from {len(events)} events (version {aggregate.version})"
            )
            
            return aggregate
            
        except Exception as e:
            logger.error(f"Failed to rebuild aggregate: {e}")
            raise
    
    def replay_events(
        self,
        aggregate_id: UUID,
        to_version: int
    ) -> List[DomainEvent]:
        """Replay events up to specific version."""
        events = self.event_store.load_events(aggregate_id)
        return events[:to_version]
```

## Event Projections

```python
# infrastructure/projections/read_model_projector.py
import logging
from typing import Callable, Dict
from domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

class ReadModelProjector:
    """Projects events into read models."""
    
    def __init__(self):
        self._projections: Dict[str, Callable] = {}
        logger.info("Initialized read model projector")
    
    def register(self, event_type: str, projection: Callable[[DomainEvent], None]) -> None:
        """Register projection for event type."""
        self._projections[event_type] = projection
        logger.info(f"Registered projection for {event_type}")
    
    def project(self, event: DomainEvent) -> None:
        """Project event to read model."""
        try:
            projection = self._projections.get(event.event_type)
            if projection:
                projection(event)
                logger.debug(f"Projected {event.event_type} to read model")
            else:
                logger.debug(f"No projection for {event.event_type}")
        except Exception as e:
            logger.error(f"Projection failed: {e}")
```

## Testing

```python
# tests/infrastructure/test_event_store.py
import pytest
from uuid import uuid4
from infrastructure.event_store.event_store import EventStore
from domain.events.user_events import UserRegisteredEvent

class TestEventStore:
    """Test event store."""
    
    def test_append_and_load_events(self, tmp_path):
        """Verify event persistence."""
        store = EventStore(storage_dir=str(tmp_path))
        
        agg_id = uuid4()
        event = UserRegisteredEvent(
            username="testuser",
            email="test@example.com",
            role="user"
        )
        event.aggregate_id = agg_id
        
        store.append_event(event)
        
        events = store.load_events(agg_id)
        assert len(events) == 1
        assert events[0].event_type == "UserRegisteredEvent"
```

## Related Documentation

- **[Domain Events](../domain/domain_events.md)** - Event definitions
- **[Aggregates](../aggregate/README.md)** - Event-sourced aggregates
- **[Event Projections](event_projections.md)** - Read model updates
