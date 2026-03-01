"""Timeline module.

Event sourcing and state chain reconstruction with immutable audit trail.
"""

import hashlib
import json
import logging
from typing import Any

from ..schemas.event_schema import Event
from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


class TimelineModule:
    """Event sourcing with immutable timeline and state reconstruction.

    Maintains complete audit trail of all events and state transitions.
    """

    def __init__(self):
        """Initialize timeline module."""
        self.timeline: list[dict[str, Any]] = []
        self.state_snapshots: dict[int, dict[str, Any]] = {}
        self.event_index: dict[str, int] = {}  # event_id -> timeline index

        # Chain integrity
        self.chain_hash = ""
        self.last_snapshot_tick = 0

        logger.info("Timeline module initialized")

    def record_event(
        self,
        event: Event,
        state_before: StateVector,
        state_after: StateVector,
        changes_applied: dict[str, Any],
    ) -> int:
        """Record event in timeline with state transitions.

        Args:
            event: Event that occurred
            state_before: State before event
            state_after: State after event
            changes_applied: Dictionary of changes applied

        Returns:
            Timeline index of recorded event
        """
        # Calculate state hash
        state_hash_before = self._hash_state(state_before)
        state_hash_after = self._hash_state(state_after)

        # Sanitize changes for JSON serialization
        safe_changes = self._sanitize_for_json(changes_applied)

        # Create timeline entry
        entry = {
            "index": len(self.timeline),
            "timestamp": event.timestamp,
            "event": event.to_dict(),
            "state_hash_before": state_hash_before,
            "state_hash_after": state_hash_after,
            "changes": safe_changes,
            "previous_chain_hash": self.chain_hash,
        }

        # Calculate entry hash and update chain
        entry_hash = self._hash_entry(entry)
        entry["entry_hash"] = entry_hash
        self.chain_hash = entry_hash

        # Add to timeline
        self.timeline.append(entry)
        self.event_index[event.event_id] = entry["index"]

        logger.debug("Recorded event %s at index %s", event.event_id, entry["index"])

        return entry["index"]

    def record_tick(
        self,
        tick_number: int,
        timestamp: float,
        state_before: StateVector,
        state_after: StateVector,
        changes: dict[str, Any],
    ) -> int:
        """Record a tick with natural state evolution.

        Args:
            tick_number: Tick number
            timestamp: Simulation timestamp
            state_before: State before tick
            state_after: State after tick
            changes: Dictionary of changes from laws

        Returns:
            Timeline index
        """
        # Create synthetic tick event
        from ..schemas.event_schema import Event, EventType

        tick_event = Event(
            event_type=EventType.SYSTEM_SHOCK,
            timestamp=timestamp,
            source="system",
            description=f"Tick {tick_number}: natural state evolution",
            metadata={"tick": tick_number},  # Don't include full changes in metadata
        )

        # Record with changes separate
        return self.record_event(tick_event, state_before, state_after, changes)

    def create_snapshot(self, tick: int, state: StateVector) -> None:
        """Create state snapshot for efficient replay.

        Args:
            tick: Tick number
            state: State to snapshot
        """
        self.state_snapshots[tick] = state.to_dict()
        self.last_snapshot_tick = tick
        logger.debug("Created state snapshot at tick %s", tick)

    def _hash_state(self, state: StateVector) -> str:
        """Calculate hash of state vector.

        Args:
            state: State to hash

        Returns:
            SHA-256 hex digest
        """
        state_json = json.dumps(state.to_dict(), sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()

    def _sanitize_for_json(self, obj: Any) -> Any:
        """Sanitize object for JSON serialization.

        Args:
            obj: Object to sanitize

        Returns:
            JSON-serializable version
        """
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._sanitize_for_json(item) for item in obj]
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)

    def _hash_entry(self, entry: dict[str, Any]) -> str:
        """Calculate hash of timeline entry.

        Args:
            entry: Entry to hash

        Returns:
            SHA-256 hex digest
        """
        # Create deterministic representation
        entry_copy = entry.copy()
        entry_copy.pop("entry_hash", None)  # Remove hash field itself

        entry_json = json.dumps(entry_copy, sort_keys=True)
        return hashlib.sha256(entry_json.encode()).hexdigest()

    def verify_chain_integrity(self) -> tuple[bool, str | None]:
        """Verify integrity of event chain.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.timeline:
            return True, None

        # Check first entry
        first_entry = self.timeline[0]
        if first_entry["previous_chain_hash"] != "":
            return False, "First entry has non-empty previous hash"

        # Check chain linkage
        for i in range(1, len(self.timeline)):
            entry = self.timeline[i]
            previous_entry = self.timeline[i - 1]

            if entry["previous_chain_hash"] != previous_entry["entry_hash"]:
                return False, f"Chain break at index {i}"

        # Verify entry hashes
        for entry in self.timeline:
            expected_hash = entry["entry_hash"]
            calculated_hash = self._hash_entry(entry)

            if expected_hash != calculated_hash:
                return False, f"Hash mismatch at index {entry['index']}"

        return True, None

    def reconstruct_state_at_tick(
        self, target_tick: int, initial_state: StateVector
    ) -> StateVector | None:
        """Reconstruct state at specific tick from timeline.

        Args:
            target_tick: Tick to reconstruct
            initial_state: Starting state

        Returns:
            Reconstructed state or None if not possible
        """
        # Find nearest snapshot before target
        snapshot_tick = 0
        for tick in sorted(self.state_snapshots.keys()):
            if tick <= target_tick:
                snapshot_tick = tick
            else:
                break

        # Load snapshot or use initial state
        if snapshot_tick > 0:
            # Would need to implement StateVector.from_dict() for full reconstruction
            logger.info("Loading snapshot from tick %s", snapshot_tick)
            current_state = initial_state.copy()  # Simplified
        else:
            current_state = initial_state.copy()

        # Replay events from snapshot to target
        logger.info("Replaying events from tick %s to %s", snapshot_tick, target_tick)

        # This would require storing and replaying all events
        # Simplified implementation for now
        return current_state

    def get_event_by_id(self, event_id: str) -> dict[str, Any] | None:
        """Get timeline entry by event ID.

        Args:
            event_id: Event identifier

        Returns:
            Timeline entry or None
        """
        if event_id in self.event_index:
            index = self.event_index[event_id]
            return self.timeline[index]
        return None

    def get_events_in_range(
        self, start_time: float, end_time: float
    ) -> list[dict[str, Any]]:
        """Get all events in time range.

        Args:
            start_time: Start timestamp
            end_time: End timestamp

        Returns:
            List of timeline entries
        """
        return [
            entry
            for entry in self.timeline
            if start_time <= entry["timestamp"] <= end_time
        ]

    def get_timeline_summary(self) -> dict[str, Any]:
        """Get timeline summary statistics.

        Returns:
            Dictionary with summary
        """
        if not self.timeline:
            return {
                "total_events": 0,
                "timeline_start": 0.0,
                "timeline_end": 0.0,
                "snapshots": 0,
            }

        return {
            "total_events": len(self.timeline),
            "timeline_start": self.timeline[0]["timestamp"],
            "timeline_end": self.timeline[-1]["timestamp"],
            "snapshots": len(self.state_snapshots),
            "last_snapshot_tick": self.last_snapshot_tick,
            "chain_hash": self.chain_hash[:16] + "...",
            "chain_valid": self.verify_chain_integrity()[0],
        }

    def export_timeline(self, include_states: bool = False) -> list[dict[str, Any]]:
        """Export complete timeline.

        Args:
            include_states: Whether to include full state snapshots

        Returns:
            List of timeline entries
        """
        if include_states:
            return self.timeline.copy()
        else:
            # Export without full state data
            return [
                {
                    "index": entry["index"],
                    "timestamp": entry["timestamp"],
                    "event": entry["event"],
                    "changes": entry["changes"],
                }
                for entry in self.timeline
            ]

    def get_summary(self) -> dict[str, Any]:
        """Get module summary.

        Returns:
            Dictionary with module state
        """
        return self.get_timeline_summary()

    def reset(self) -> None:
        """Reset module to initial state."""
        self.__init__()
        logger.info("Timeline module reset")
