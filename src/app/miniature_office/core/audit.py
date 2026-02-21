"""
Audit Log System - Immutable event tracking and causality graph
Implements Codex Section 8.2 for audit trails and change lineage
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class EventType(Enum):
    """Types of events tracked in the audit log"""

    ENTITY_CREATED = "entity_created"
    ENTITY_UPDATED = "entity_updated"
    RELATIONSHIP_DECLARED = "relationship_declared"
    TASK_STATE_CHANGED = "task_state_changed"
    DIRECTIVE_CREATED = "directive_created"
    CONSENSUS_REACHED = "consensus_reached"
    OVERRIDE_ISSUED = "override_issued"
    MEETING_HELD = "meeting_held"
    ARTIFACT_PRODUCED = "artifact_produced"
    TOOL_CHECKED_OUT = "tool_checked_out"
    CODEX_AMENDMENT = "codex_amendment"
    AGENT_ACTION = "agent_action"
    SECURITY_EVENT = "security_event"


@dataclass
class AuditEvent:
    """
    Immutable audit event with cryptographic integrity.
    Forms nodes in the causality graph.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.AGENT_ACTION
    timestamp: datetime = field(default_factory=datetime.utcnow)
    actor_id: Optional[str] = None  # Entity that caused the event
    target_id: Optional[str] = None  # Entity affected by the event
    data: Dict[str, Any] = field(default_factory=dict)
    parent_events: List[str] = field(default_factory=list)  # Causality links
    _hash: Optional[str] = None

    def __post_init__(self):
        """Calculate hash for immutability verification"""
        if not self._hash:
            self._hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of event content"""
        content = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "data": self.data,
            "parent_events": sorted(self.parent_events),
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify event hasn't been tampered with"""
        return self._hash == self._calculate_hash()

    def to_dict(self) -> Dict:
        """Serialize event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "data": self.data,
            "parent_events": self.parent_events,
            "hash": self._hash,
        }


class CausalityGraph:
    """
    Maintains the causality relationships between events.
    Implements known causality graph (Codex 8.2)
    """

    def __init__(self):
        self.events: Dict[str, AuditEvent] = {}
        self.children: Dict[str, Set[str]] = {}  # parent_id -> set of child_ids

    def add_event(self, event: AuditEvent) -> None:
        """Add event to the causality graph"""
        if event.event_id in self.events:
            raise ValueError(f"Event {event.event_id} already exists")

        if not event.verify_integrity():
            raise ValueError(f"Event {event.event_id} failed integrity check")

        self.events[event.event_id] = event

        # Build reverse index for efficient child lookup
        for parent_id in event.parent_events:
            if parent_id not in self.children:
                self.children[parent_id] = set()
            self.children[parent_id].add(event.event_id)

    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Retrieve an event by ID"""
        return self.events.get(event_id)

    def get_children(self, event_id: str) -> List[AuditEvent]:
        """Get all events caused by a given event"""
        child_ids = self.children.get(event_id, set())
        return [self.events[cid] for cid in child_ids if cid in self.events]

    def get_lineage(self, event_id: str) -> List[AuditEvent]:
        """
        Get complete lineage (ancestry chain) of an event.
        Returns events from root to the specified event.
        """
        lineage = []
        visited = set()

        def trace_back(eid: str):
            if eid in visited or eid not in self.events:
                return

            event = self.events[eid]
            visited.add(eid)

            # Recursively trace parents first
            for parent_id in event.parent_events:
                trace_back(parent_id)

            lineage.append(event)

        trace_back(event_id)
        return lineage

    def get_descendants(self, event_id: str) -> List[AuditEvent]:
        """Get all events descended from a given event"""
        descendants = []
        visited = set()

        def traverse(eid: str):
            if eid in visited:
                return
            visited.add(eid)

            for child in self.get_children(eid):
                descendants.append(child)
                traverse(child.event_id)

        traverse(event_id)
        return descendants


class AuditLog:
    """
    Main audit log system implementing immutable logging.
    Codex Section 8.2 - Every stage of work writes to immutable log.
    """

    def __init__(self):
        self.graph = CausalityGraph()
        self._type_index: Dict[EventType, List[str]] = {}
        self._actor_index: Dict[str, List[str]] = {}
        self._target_index: Dict[str, List[str]] = {}

    def log_event(
        self,
        event_type: EventType,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        data: Optional[Dict] = None,
        parent_events: Optional[List[str]] = None,
    ) -> AuditEvent:
        """
        Log a new event to the immutable audit log.
        Returns the created event.
        """
        event = AuditEvent(
            event_type=event_type,
            actor_id=actor_id,
            target_id=target_id,
            data=data or {},
            parent_events=parent_events or [],
        )

        self.graph.add_event(event)

        # Update indexes for efficient querying
        if event_type not in self._type_index:
            self._type_index[event_type] = []
        self._type_index[event_type].append(event.event_id)

        if actor_id:
            if actor_id not in self._actor_index:
                self._actor_index[actor_id] = []
            self._actor_index[actor_id].append(event.event_id)

        if target_id:
            if target_id not in self._target_index:
                self._target_index[target_id] = []
            self._target_index[target_id].append(event.event_id)

        return event

    def get_events_by_type(self, event_type: EventType) -> List[AuditEvent]:
        """Get all events of a specific type"""
        event_ids = self._type_index.get(event_type, [])
        return [self.graph.get_event(eid) for eid in event_ids if self.graph.get_event(eid)]

    def get_events_by_actor(self, actor_id: str) -> List[AuditEvent]:
        """Get all events performed by a specific actor"""
        event_ids = self._actor_index.get(actor_id, [])
        return [self.graph.get_event(eid) for eid in event_ids if self.graph.get_event(eid)]

    def get_events_by_target(self, target_id: str) -> List[AuditEvent]:
        """Get all events affecting a specific target"""
        event_ids = self._target_index.get(target_id, [])
        return [self.graph.get_event(eid) for eid in event_ids if self.graph.get_event(eid)]

    def get_change_lineage(self, target_id: str) -> List[AuditEvent]:
        """
        Get complete change lineage for a target entity.
        Implements change lineage tracking (Codex 8.2)
        """
        events = self.get_events_by_target(target_id)
        # Sort by timestamp to show evolution
        return sorted(events, key=lambda e: e.timestamp)

    def get_events(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent events as dictionaries.
        Returns events in reverse chronological order.
        """
        all_events = list(self.graph.events.values())
        # Sort by timestamp descending
        all_events.sort(key=lambda e: e.timestamp, reverse=True)

        if limit:
            all_events = all_events[:limit]

        # Convert to dict format
        return [e.to_dict() for e in all_events]

    def verify_integrity(self) -> bool:
        """Verify integrity of entire audit log"""
        return all(event.verify_integrity() for event in self.graph.events.values())


# Global audit log instance
_audit_log = AuditLog()


def get_audit_log() -> AuditLog:
    """Get the global audit log instance"""
    return _audit_log
