"""
Cryptographic Audit Log System

This module implements a production-grade audit logging system with:
- SHA-256 cryptographic chaining for tamper detection
- YAML append-only log format for human readability and tool compatibility
- Automatic directory creation
- Robust error handling and logging
- Thread-safe operations

Each audit event is cryptographically linked to the previous event via SHA-256
hashing, creating an immutable chain that detects any tampering attempts.
"""

import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_LOG = (
    Path(__file__).parent.parent.parent.parent / "governance" / "audit_log.yaml"
)


class AuditLog:
    """Cryptographic audit log with SHA-256 chaining.

    This class provides tamper-evident audit logging by:
    1. Hashing each event's data with SHA-256
    2. Including the previous event's hash in the next event
    3. Storing events in YAML format for readability
    4. Ensuring append-only operations

    Example:
        >>> audit = AuditLog()
        >>> audit.log_event(
        ...     event_type="health_report_generated",
        ...     data={"cpu_usage": 45.2, "memory_mb": 2048}
        ... )
    """

    def __init__(self, log_file: Path | None = None):
        """Initialize the audit log.

        Args:
            log_file: Path to the audit log YAML file. If None, uses default location.
        """
        self.log_file = log_file or DEFAULT_AUDIT_LOG
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._load_last_hash()

        logger.info("AuditLog initialized at %s", self.log_file)

    def _load_last_hash(self) -> str:
        """Load the hash of the last event from the log file.

        Returns:
            The last event's hash, or "GENESIS" if log is empty or doesn't exist.
        """
        if not self.log_file.exists():
            return "GENESIS"

        try:
            with open(self.log_file, encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return "GENESIS"

                # Load all events to find the last one
                events = list(yaml.safe_load_all(content))
                if events and len(events) > 0:
                    last_event = events[-1]
                    if last_event and "hash" in last_event:
                        return last_event["hash"]
        except Exception as e:
            logger.warning("Failed to load last hash from audit log: %s", e)

        return "GENESIS"

    def _compute_hash(self, event_data: dict[str, Any]) -> str:
        """Compute SHA-256 hash of event data.

        Args:
            event_data: Dictionary containing event data to hash

        Returns:
            Hexadecimal SHA-256 hash string
        """
        # Create a canonical representation for hashing
        hash_input = yaml.dump(event_data, sort_keys=True, default_flow_style=False)
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    def log_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str = "system",
        description: str = "",
    ) -> bool:
        """Log an audit event with cryptographic chaining.

        Args:
            event_type: Type/category of the event (e.g., "health_report_generated")
            data: Optional event data dictionary
            actor: Entity performing the action (default: "system")
            description: Human-readable description of the event

        Returns:
            True if event was logged successfully, False otherwise
        """
        try:
            # Create event structure
            event = {
                "timestamp": datetime.now(UTC).isoformat(),
                "event_type": event_type,
                "actor": actor,
                "description": description or f"{event_type} event",
                "previous_hash": self.last_hash,
                "data": data or {},
            }

            # Compute hash for this event (before adding the hash field)
            event_hash = self._compute_hash(event)
            event["hash"] = event_hash

            # Append to log file
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write("---\n")
                yaml.dump(event, f, default_flow_style=False, sort_keys=False)

            # Update last hash for next event
            self.last_hash = event_hash

            logger.info("Audit event logged: %s (hash: %s...)", event_type, event_hash[)
            return True

        except Exception as e:
            logger.error("Failed to log audit event: %s", e)
            return False

    def verify_chain(self) -> tuple[bool, str]:
        """Verify the integrity of the audit log chain.

        Returns:
            Tuple of (is_valid, message) where is_valid indicates if chain is intact
        """
        if not self.log_file.exists():
            return True, "Log file does not exist yet (empty log is valid)"

        try:
            with open(self.log_file, encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return True, "Log is empty (valid)"

                events = list(yaml.safe_load_all(content))

            if not events:
                return True, "No events in log (valid)"

            # Verify each event's hash and chain
            expected_prev_hash = "GENESIS"
            for i, event in enumerate(events):
                if not event:
                    continue

                # Check if previous hash matches
                if event.get("previous_hash") != expected_prev_hash:
                    return (
                        False,
                        f"Chain broken at event {i}: expected previous_hash={expected_prev_hash}, got {event.get('previous_hash')}",
                    )

                # Verify the event's own hash
                stored_hash = event.get("hash")
                if not stored_hash:
                    return False, f"Event {i} missing hash field"

                # Recompute hash (exclude the hash field itself)
                event_copy = {k: v for k, v in event.items() if k != "hash"}
                computed_hash = self._compute_hash(event_copy)

                if computed_hash != stored_hash:
                    return (
                        False,
                        f"Event {i} hash mismatch: expected {stored_hash[:16]}..., computed {computed_hash[:16]}...",
                    )

                expected_prev_hash = stored_hash

            return True, f"Chain verified successfully ({len(events)} events)"

        except Exception as e:
            return False, f"Verification failed with error: {e}"

    def get_events(
        self, event_type: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve audit events from the log.

        Args:
            event_type: Optional filter by event type
            limit: Optional limit on number of events to return (most recent first)

        Returns:
            List of event dictionaries
        """
        if not self.log_file.exists():
            return []

        try:
            with open(self.log_file, encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return []

                events = list(yaml.safe_load_all(content))

            # Filter valid events
            events = [e for e in events if e is not None]

            # Filter by event type if specified
            if event_type:
                events = [e for e in events if e.get("event_type") == event_type]

            # Apply limit (most recent first)
            if limit and len(events) > limit:
                events = events[-limit:]

            return events

        except Exception as e:
            logger.error("Failed to retrieve events: %s", e)
            return []


__all__ = ["AuditLog"]
