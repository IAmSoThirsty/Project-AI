#!/usr/bin/env python3
"""
Structured JSON Audit Log
Enhanced audit logging with structured JSON format for better querying

Production-ready JSON-based audit system with full compatibility.
"""

import hashlib
import json
import logging
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JSONAuditLog:
    """
    Structured JSON audit log with cryptographic chaining.

    Features:
    - JSON format for structured data
    - SHA-256 cryptographic chaining
    - OpenTelemetry trace/span integration
    - High-performance writes
    - Query-friendly structure
    - Automatic rotation
    """

    def __init__(
        self,
        log_file: Path | None = None,
        auto_rotate: bool = True,
        max_size_mb: int = 100,
    ):
        """
        Initialize JSON audit log.

        Args:
            log_file: Path to audit log file
            auto_rotate: Enable automatic rotation
            max_size_mb: Maximum file size before rotation
        """
        self.log_file = log_file or Path("var/audit.json")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.auto_rotate = auto_rotate
        self.max_size_mb = max_size_mb
        self.lock = threading.Lock()

        self.last_hash = self._load_last_hash()
        self.event_count = 0

        logger.info(f"JSONAuditLog initialized at {self.log_file}")

    def _load_last_hash(self) -> str:
        """Load hash of last event from log file."""
        if not self.log_file.exists():
            return "GENESIS"

        try:
            with open(self.log_file, "r") as f:
                # Read last line
                lines = f.readlines()
                if lines:
                    last_event = json.loads(lines[-1])
                    return last_event.get("hash", "GENESIS")
        except Exception as e:
            logger.warning(f"Failed to load last hash: {e}")

        return "GENESIS"

    def _compute_hash(self, event_data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of event data."""
        # Create canonical JSON representation
        canonical = json.dumps(event_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _should_rotate(self) -> bool:
        """Check if log rotation is needed."""
        if not self.auto_rotate or not self.log_file.exists():
            return False

        size_mb = self.log_file.stat().st_size / (1024 * 1024)
        return size_mb >= self.max_size_mb

    def _rotate_log(self):
        """Rotate log file with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.log_file.with_suffix(f".{timestamp}.json")

        self.log_file.rename(archive_file)
        logger.info(f"Rotated audit log to {archive_file}")

        # Reset chain
        self.last_hash = "GENESIS"

    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any] | None = None,
        actor: str = "system",
        action: str = "",
        target: str = "",
        outcome: str = "success",
        severity: str = "info",
        metadata: Dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> bool:
        """
        Log a structured audit event.

        Args:
            event_type: Type/category of event
            data: Event data dictionary
            actor: Entity performing the action
            action: Action being performed
            target: Target of the action
            outcome: Outcome (success/failure)
            severity: Severity level
            metadata: Additional metadata
            trace_id: OpenTelemetry trace ID
            span_id: OpenTelemetry span ID

        Returns:
            True if logged successfully
        """
        with self.lock:
            try:
                # Check if rotation needed
                if self._should_rotate():
                    self._rotate_log()

                # Create structured event
                event = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "event_type": event_type,
                    "actor": actor,
                    "action": action or event_type,
                    "target": target,
                    "outcome": outcome,
                    "severity": severity,
                    "previous_hash": self.last_hash,
                    "data": data or {},
                    "metadata": metadata or {},
                }

                # Add OpenTelemetry context if available
                if trace_id:
                    event["trace_id"] = trace_id
                if span_id:
                    event["span_id"] = span_id

                # Compute hash
                event_hash = self._compute_hash(event)
                event["hash"] = event_hash

                # Append to log file (one JSON object per line)
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(event, separators=(",", ":")) + "\n")

                # Update state
                self.last_hash = event_hash
                self.event_count += 1

                logger.debug(
                    f"Audit event logged: {event_type} (hash: {event_hash[:16]}...)"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to log audit event: {e}")
                return False

    def verify_chain(self) -> tuple[bool, str]:
        """Verify integrity of audit log chain."""
        if not self.log_file.exists():
            return True, "Log file does not exist (valid)"

        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            expected_prev_hash = "GENESIS"

            for i, line in enumerate(lines):
                event = json.loads(line)

                # Check previous hash
                if event.get("previous_hash") != expected_prev_hash:
                    return (
                        False,
                        f"Chain broken at event {i}: expected {expected_prev_hash}, got {event.get('previous_hash')}",
                    )

                # Verify event hash
                stored_hash = event.get("hash")
                if not stored_hash:
                    return False, f"Event {i} missing hash"

                # Recompute hash
                event_copy = {k: v for k, v in event.items() if k != "hash"}
                computed_hash = self._compute_hash(event_copy)

                if computed_hash != stored_hash:
                    return False, f"Event {i} hash mismatch"

                expected_prev_hash = stored_hash

            return True, f"Chain verified ({len(lines)} events)"

        except Exception as e:
            return False, f"Verification failed: {e}"

    def query_events(
        self,
        event_type: str | None = None,
        actor: str | None = None,
        severity: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Query audit events with filters.

        Args:
            event_type: Filter by event type
            actor: Filter by actor
            severity: Filter by severity
            start_time: Filter events after this time
            end_time: Filter events before this time
            limit: Maximum number of events to return

        Returns:
            List of matching events
        """
        if not self.log_file.exists():
            return []

        results = []

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    event = json.loads(line)

                    # Apply filters
                    if event_type and event.get("event_type") != event_type:
                        continue

                    if actor and event.get("actor") != actor:
                        continue

                    if severity and event.get("severity") != severity:
                        continue

                    # Time filtering
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if start_time and event_time < start_time:
                        continue
                    if end_time and event_time > end_time:
                        continue

                    results.append(event)

                    # Limit check
                    if limit and len(results) >= limit:
                        break

        except Exception as e:
            logger.error(f"Query failed: {e}")

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        if not self.log_file.exists():
            return {"total_events": 0, "file_size_mb": 0, "file_exists": False}

        try:
            with open(self.log_file, "r") as f:
                events = [json.loads(line) for line in f]

            # Aggregate statistics
            event_types = {}
            actors = {}
            severities = {}

            for event in events:
                event_type = event.get("event_type", "unknown")
                actor = event.get("actor", "unknown")
                severity = event.get("severity", "info")

                event_types[event_type] = event_types.get(event_type, 0) + 1
                actors[actor] = actors.get(actor, 0) + 1
                severities[severity] = severities.get(severity, 0) + 1

            return {
                "total_events": len(events),
                "file_size_mb": self.log_file.stat().st_size / (1024 * 1024),
                "file_exists": True,
                "event_types": event_types,
                "actors": actors,
                "severities": severities,
                "first_event": events[0]["timestamp"] if events else None,
                "last_event": events[-1]["timestamp"] if events else None,
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test JSON audit log
    import tempfile

    logging.basicConfig(level=logging.INFO)

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test_audit.json"
        audit = JSONAuditLog(log_file=log_file)

        # Log some events
        audit.log_event(
            event_type="user_login",
            actor="john.doe",
            action="authenticate",
            target="web_portal",
            outcome="success",
            severity="info",
            data={"ip": "192.168.1.100", "method": "password"},
        )

        audit.log_event(
            event_type="vault_access",
            actor="system",
            action="read_secret",
            target="api_key",
            outcome="success",
            severity="info",
            trace_id="abc123",
            span_id="def456",
        )

        # Verify chain
        is_valid, message = audit.verify_chain()
        print(f"Chain verification: {message}")

        # Query events
        events = audit.query_events(event_type="user_login")
        print(f"Found {len(events)} user_login events")

        # Get statistics
        stats = audit.get_statistics()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
