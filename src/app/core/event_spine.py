#!/usr/bin/env python3
"""
Inter-domain Event Spine - Lightweight Event Bus
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides a centralized event bus for cross-domain communication enabling:
- Ethics vetoing tactical decisions
- Supply reacting to situational alerts
- AGI Safeguards overriding command paths
- Self-aware system coordination

Features:
- Declarative subscription model
- Event priority and ordering
- Event filtering and transformation
- Cross-domain routing
- Authority-aware event processing
"""

import logging
import queue
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels"""

    CRITICAL = 0  # Safety-critical, immediate processing
    HIGH = 1  # Important operational events
    NORMAL = 2  # Standard events
    LOW = 3  # Background events
    DEBUG = 4  # Diagnostic events


class EventCategory(Enum):
    """Event categories for routing"""

    THREAT_DETECTED = "threat_detected"
    RESOURCE_CRITICAL = "resource_critical"
    MISSION_CREATED = "mission_created"
    ETHICAL_VIOLATION = "ethical_violation"
    AGI_ALERT = "agi_alert"
    TACTICAL_DECISION = "tactical_decision"
    SUPPLY_UPDATE = "supply_update"
    SURVIVOR_FOUND = "survivor_found"
    SYSTEM_HEALTH = "system_health"
    GOVERNANCE_DECISION = "governance_decision"


@dataclass
class Event:
    """
    Inter-domain event.

    Events flow through the spine, enabling cross-domain coordination
    and authority-based decision making.
    """

    event_id: str
    category: EventCategory
    source_domain: str
    timestamp: datetime
    priority: EventPriority
    payload: dict[str, Any]
    requires_approval: bool = False
    can_be_vetoed: bool = False
    approved_by: str | None = None
    vetoed_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "category": self.category.value,
            "source_domain": self.source_domain,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "payload": self.payload,
            "requires_approval": self.requires_approval,
            "can_be_vetoed": self.can_be_vetoed,
            "approved_by": self.approved_by,
            "vetoed_by": self.vetoed_by,
            "metadata": self.metadata,
        }


@dataclass
class Subscription:
    """Event subscription."""

    subscriber_id: str
    subscriber_domain: str
    categories: list[EventCategory]
    callback: Callable[[Event], None]
    priority_filter: list[EventPriority] | None = None
    source_filter: list[str] | None = None
    can_veto: bool = False
    can_approve: bool = False
    active: bool = True


class EventSpine:
    """
    Inter-domain Event Spine

    Lightweight event bus enabling declarative cross-domain communication
    with authority-aware processing.
    """

    def __init__(self, max_queue_size: int = 10000):
        """
        Initialize event spine.

        Args:
            max_queue_size: Maximum size of event queue
        """
        self.max_queue_size = max_queue_size

        # Event queue with priority
        self._event_queue: queue.PriorityQueue = queue.PriorityQueue(
            maxsize=max_queue_size
        )

        # Subscriptions
        self._subscriptions: dict[str, Subscription] = {}
        self._subscriptions_by_category: dict[EventCategory, list[str]] = {}

        # Event processing
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False

        # Event history (for debugging/audit)
        self._event_history: list[Event] = []
        self._max_history = 1000

        # Statistics
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_vetoed": 0,
            "events_approved": 0,
            "events_dropped": 0,
        }

        # Thread safety
        self._lock = threading.RLock()

        logger.info("Event Spine initialized")

    def start(self):
        """Start event processing."""
        if self._processing_active:
            logger.warning("Event processing already active")
            return

        self._processing_active = True
        self._processing_thread = threading.Thread(
            target=self._process_events_loop, daemon=True, name="EventSpine-Processor"
        )
        self._processing_thread.start()

        logger.info("Event Spine started")

    def stop(self):
        """Stop event processing."""
        self._processing_active = False

        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)

        logger.info("Event Spine stopped")

    def subscribe(
        self,
        subscriber_id: str,
        subscriber_domain: str,
        categories: list[EventCategory],
        callback: Callable[[Event], None],
        priority_filter: list[EventPriority] | None = None,
        source_filter: list[str] | None = None,
        can_veto: bool = False,
        can_approve: bool = False,
    ) -> str:
        """
        Subscribe to events.

        Args:
            subscriber_id: Unique subscriber identifier
            subscriber_domain: Domain subscribing
            categories: Event categories to subscribe to
            callback: Callback function for events
            priority_filter: Optional priority filter
            source_filter: Optional source domain filter
            can_veto: Whether subscriber can veto events
            can_approve: Whether subscriber can approve events

        Returns:
            Subscription ID
        """
        with self._lock:
            subscription = Subscription(
                subscriber_id=subscriber_id,
                subscriber_domain=subscriber_domain,
                categories=categories,
                callback=callback,
                priority_filter=priority_filter,
                source_filter=source_filter,
                can_veto=can_veto,
                can_approve=can_approve,
            )

            self._subscriptions[subscriber_id] = subscription

            # Update category index
            for category in categories:
                if category not in self._subscriptions_by_category:
                    self._subscriptions_by_category[category] = []

                if subscriber_id not in self._subscriptions_by_category[category]:
                    self._subscriptions_by_category[category].append(subscriber_id)

            logger.info(
                f"Subscription created: {subscriber_id} from {subscriber_domain} "
                f"for categories: {[c.value for c in categories]}"
            )

            return subscriber_id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscriber_id: Subscriber to remove

        Returns:
            True if unsubscribed successfully
        """
        with self._lock:
            if subscriber_id not in self._subscriptions:
                return False

            subscription = self._subscriptions.pop(subscriber_id)

            # Remove from category index
            for category in subscription.categories:
                if category in self._subscriptions_by_category:
                    if subscriber_id in self._subscriptions_by_category[category]:
                        self._subscriptions_by_category[category].remove(subscriber_id)

            logger.info("Unsubscribed: %s", subscriber_id)
            return True

    def publish(
        self,
        category: EventCategory,
        source_domain: str,
        payload: dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        requires_approval: bool = False,
        can_be_vetoed: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Publish an event to the spine.

        Args:
            category: Event category
            source_domain: Source domain
            payload: Event payload
            priority: Event priority
            requires_approval: Whether event requires approval
            can_be_vetoed: Whether event can be vetoed
            metadata: Optional metadata

        Returns:
            Event ID
        """
        event_id = f"{source_domain}_{category.value}_{int(time.time() * 1000)}"

        event = Event(
            event_id=event_id,
            category=category,
            source_domain=source_domain,
            timestamp=datetime.now(),
            priority=priority,
            payload=payload,
            requires_approval=requires_approval,
            can_be_vetoed=can_be_vetoed,
            metadata=metadata or {},
        )

        try:
            # Use priority as queue key (lower number = higher priority)
            self._event_queue.put((priority.value, event), block=False)

            with self._lock:
                self._stats["events_published"] += 1

            logger.debug("Event published: %s (%s) from %s", event_id, category.value, source_domain)

            return event_id

        except queue.Full:
            with self._lock:
                self._stats["events_dropped"] += 1

            logger.error("Event queue full, dropping event: %s", event_id)
            return event_id

    def _process_events_loop(self):
        """Background event processing loop."""
        while self._processing_active:
            try:
                # Get next event (blocks with timeout)
                try:
                    priority_value, event = self._event_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Process event
                self._process_event(event)

                # Update stats
                with self._lock:
                    self._stats["events_processed"] += 1

            except Exception as e:
                logger.error(f"Error in event processing loop: {e}", exc_info=True)

    def _process_event(self, event: Event):
        """
        Process a single event.

        Args:
            event: Event to process
        """
        logger.debug("Processing event: %s (%s)", event.event_id, event.category.value)

        # Add to history
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)

        # Find subscribers
        subscriber_ids = self._subscriptions_by_category.get(event.category, [])

        if not subscriber_ids:
            logger.debug("No subscribers for event category: %s", event.category.value)
            return

        # Phase 1: Check for veto (if event can be vetoed)
        if event.can_be_vetoed:
            for subscriber_id in subscriber_ids:
                subscription = self._subscriptions.get(subscriber_id)

                if not subscription or not subscription.active:
                    continue

                if not subscription.can_veto:
                    continue

                if not self._matches_filters(event, subscription):
                    continue

                # Call veto check
                try:
                    # Callback should return True to veto, False to allow
                    should_veto = subscription.callback(event)

                    if should_veto:
                        event.vetoed_by = subscriber_id

                        with self._lock:
                            self._stats["events_vetoed"] += 1

                        logger.info(
                            f"Event vetoed: {event.event_id} by {subscriber_id} "
                            f"({subscription.subscriber_domain})"
                        )
                        return  # Event is vetoed, don't process further

                except Exception as e:
                    logger.error("Error in veto check for %s: %s", subscriber_id, e)

        # Phase 2: Check for approval (if event requires approval)
        if event.requires_approval:
            approved = False

            for subscriber_id in subscriber_ids:
                subscription = self._subscriptions.get(subscriber_id)

                if not subscription or not subscription.active:
                    continue

                if not subscription.can_approve:
                    continue

                if not self._matches_filters(event, subscription):
                    continue

                # Call approval check
                try:
                    # Callback should return True to approve, False to deny
                    is_approved = subscription.callback(event)

                    if is_approved:
                        event.approved_by = subscriber_id
                        approved = True

                        with self._lock:
                            self._stats["events_approved"] += 1

                        logger.info(
                            f"Event approved: {event.event_id} by {subscriber_id} "
                            f"({subscription.subscriber_domain})"
                        )
                        break

                except Exception as e:
                    logger.error("Error in approval check for %s: %s", subscriber_id, e)

            if not approved:
                logger.warning("Event not approved: %s", event.event_id)
                return  # Event not approved, don't process further

        # Phase 3: Deliver to all subscribers
        for subscriber_id in subscriber_ids:
            subscription = self._subscriptions.get(subscriber_id)

            if not subscription or not subscription.active:
                continue

            # Skip veto/approval subscribers (already processed)
            if subscription.can_veto or subscription.can_approve:
                continue

            if not self._matches_filters(event, subscription):
                continue

            # Deliver event
            try:
                subscription.callback(event)

                logger.debug("Event delivered to %s (%s)", subscriber_id, subscription.subscriber_domain)

            except Exception as e:
                logger.error("Error delivering event to %s: %s", subscriber_id, e)

    def _matches_filters(self, event: Event, subscription: Subscription) -> bool:
        """
        Check if event matches subscription filters.

        Args:
            event: Event to check
            subscription: Subscription to match against

        Returns:
            True if event matches filters
        """
        # Check priority filter
        if subscription.priority_filter:
            if event.priority not in subscription.priority_filter:
                return False

        # Check source filter
        if subscription.source_filter:
            if event.source_domain not in subscription.source_filter:
                return False

        return True

    def get_stats(self) -> dict[str, Any]:
        """Get event spine statistics."""
        with self._lock:
            return {
                "stats": self._stats.copy(),
                "queue_size": self._event_queue.qsize(),
                "subscriptions": len(self._subscriptions),
                "categories": len(self._subscriptions_by_category),
                "processing_active": self._processing_active,
            }

    def get_subscriptions(self) -> list[dict[str, Any]]:
        """Get all active subscriptions."""
        with self._lock:
            return [
                {
                    "subscriber_id": sub.subscriber_id,
                    "subscriber_domain": sub.subscriber_domain,
                    "categories": [c.value for c in sub.categories],
                    "can_veto": sub.can_veto,
                    "can_approve": sub.can_approve,
                    "active": sub.active,
                }
                for sub in self._subscriptions.values()
            ]

    def get_event_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent event history."""
        with self._lock:
            history = self._event_history[-limit:]
            return [event.to_dict() for event in history]


# Singleton instance
_event_spine_instance: EventSpine | None = None
_event_spine_lock = threading.Lock()


def get_event_spine() -> EventSpine:
    """
    Get the singleton EventSpine instance.

    Returns:
        EventSpine instance
    """
    global _event_spine_instance

    with _event_spine_lock:
        if _event_spine_instance is None:
            _event_spine_instance = EventSpine()
            _event_spine_instance.start()

        return _event_spine_instance
