# Observer Pattern in Project-AI

## Overview

Observer Pattern defines one-to-many dependency where observers are notified of state changes. Project-AI uses observers for event listening, metrics collection, and monitoring.

## Event Listeners

```python

# infrastructure/observers/event_listener.py

import logging
from abc import ABC, abstractmethod
from domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

class EventListener(ABC):
    """Base event listener/observer."""

    @abstractmethod
    def on_event(self, event: DomainEvent) -> None:
        """Handle event notification."""
        pass

class MetricsObserver(EventListener):
    """Observer for metrics collection."""

    def __init__(self):
        self.event_counts = {}
        logger.info("Initialized metrics observer")

    def on_event(self, event: DomainEvent) -> None:
        """Record event metrics."""
        event_type = event.event_type
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
        logger.debug(f"Recorded metric for {event_type}")

    def get_metrics(self) -> dict:
        """Get collected metrics."""
        return self.event_counts.copy()
```

## Related Documentation

- **[Domain Events](../domain/domain_events.md)** - Event definitions
- **[Monitoring](../../monitoring/README.md)** - System monitoring
