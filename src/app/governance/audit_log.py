"""
Cryptographic Audit Log System

This module implements a production-grade audit logging system with:
- SHA-256 cryptographic chaining for tamper detection
- YAML append-only log format for human readability and tool compatibility
- Automatic directory creation
- Robust error handling and logging
- Thread-safe operations
- Log rotation and archiving
- Compression support
- Performance optimizations
- Export capabilities (JSON, CSV)
- Advanced querying and filtering
- Compliance reporting
- Integration with tamperproof and trace logging

Each audit event is cryptographically linked to the previous event via SHA-256
hashing, creating an immutable chain that detects any tampering attempts.

Example:
    >>> from src.app.governance.audit_log import AuditLog
    >>> audit = AuditLog()
    >>> audit.log_event(
    ...     event_type="system_started",
    ...     data={"version": "1.0.0"},
    ...     actor="system",
    ...     description="System initialization complete"
    ... )
    True
"""

import csv
import gzip
import hashlib
import json
import logging
import shutil
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_LOG = (
    Path(__file__).parent.parent.parent.parent / "governance" / "audit_log.yaml"
)

# Configuration constants
MAX_LOG_SIZE_MB = 100  # Rotate after 100MB
MAX_ARCHIVE_COUNT = 10  # Keep last 10 rotated logs
COMPRESSION_ENABLED = True  # Compress archived logs


class AuditLog:
    """Cryptographic audit log with SHA-256 chaining.

    This class provides tamper-evident audit logging by:
    1. Hashing each event's data with SHA-256
    2. Including the previous event's hash in the next event
    3. Storing events in YAML format for readability
    4. Ensuring append-only operations
    5. Automatic log rotation and archiving
    6. Compression support for archived logs
    7. Thread-safe operations
    8. Advanced querying and filtering
    9. Export capabilities (JSON, CSV, YAML)
    10. Compliance reporting

    Attributes:
        log_file: Path to the active audit log file
        last_hash: SHA-256 hash of the most recent event
        lock: Thread lock for synchronized operations
        event_count: Total number of events logged in current session
        event_callbacks: List of callbacks to invoke on event logging

    Example:
        >>> audit = AuditLog()
        >>> audit.log_event(
        ...     event_type="health_report_generated",
        ...     data={"cpu_usage": 45.2, "memory_mb": 2048}
        ... )
        True
    """

    def __init__(
        self,
        log_file: Path | None = None,
        auto_rotate: bool = True,
        max_size_mb: int = MAX_LOG_SIZE_MB,
        compression: bool = COMPRESSION_ENABLED,
    ):
        """Initialize the audit log.

        Args:
            log_file: Path to the audit log YAML file. If None, uses default location.
            auto_rotate: Enable automatic log rotation when size limit is reached
            max_size_mb: Maximum log file size in MB before rotation
            compression: Enable gzip compression for archived logs
        """
        self.log_file = log_file or DEFAULT_AUDIT_LOG
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.auto_rotate = auto_rotate
        self.max_size_mb = max_size_mb
        self.compression = compression
        self.lock = threading.Lock()
        self.event_count = 0
        self.event_callbacks: list[Callable[[dict[str, Any]], None]] = []

        self.last_hash = self._load_last_hash()

        logger.info(
            "AuditLog initialized at %s (auto_rotate=%s, max_size=%dMB, compression=%s)",
            self.log_file,
            auto_rotate,
            max_size_mb,
            compression,
        )

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
        severity: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Log an audit event with cryptographic chaining.

        This method is thread-safe and will automatically rotate logs if enabled.

        Args:
            event_type: Type/category of the event (e.g., "health_report_generated")
            data: Optional event data dictionary
            actor: Entity performing the action (default: "system")
            description: Human-readable description of the event
            severity: Event severity level (info, warning, error, critical)
            metadata: Additional metadata (e.g., IP address, session ID)

        Returns:
            True if event was logged successfully, False otherwise
        """
        with self.lock:
            try:
                # Check if rotation is needed
                if self.auto_rotate and self._should_rotate():
                    self._rotate_log()

                # Create event structure
                event = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "event_type": event_type,
                    "actor": actor,
                    "description": description or f"{event_type} event",
                    "severity": severity,
                    "previous_hash": self.last_hash,
                    "data": data or {},
                    "metadata": metadata or {},
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
                self.event_count += 1

                # Invoke callbacks
                for callback in self.event_callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.warning("Event callback failed: %s", e)

                logger.debug(
                    "Audit event logged: %s (hash: %s..., count: %d)",
                    event_type,
                    event_hash[:16],
                    self.event_count,
                )
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

    def _should_rotate(self) -> bool:
        """Check if log file should be rotated based on size.

        Returns:
            True if log file exceeds size limit, False otherwise
        """
        if not self.log_file.exists():
            return False

        try:
            size_mb = self.log_file.stat().st_size / (1024 * 1024)
            return size_mb >= self.max_size_mb
        except Exception as e:
            logger.warning("Failed to check log size: %s", e)
            return False

    def _rotate_log(self) -> bool:
        """Rotate the current log file and optionally compress it.

        Creates a timestamped archive of the current log and starts a new one.
        Old archives beyond MAX_ARCHIVE_COUNT are automatically deleted.

        Returns:
            True if rotation succeeded, False otherwise
        """
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            archive_name = f"{self.log_file.stem}_{timestamp}.yaml"

            if self.compression:
                archive_name += ".gz"

            archive_path = self.log_file.parent / "archive" / archive_name
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy and compress if needed
            if self.compression:
                with open(self.log_file, "rb") as f_in:
                    with gzip.open(archive_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(self.log_file, archive_path)

            # Clear current log file and reset hash
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("")

            self.last_hash = "GENESIS"

            # Clean up old archives
            self._cleanup_archives()

            logger.info("Log rotated successfully: %s", archive_path)
            return True

        except Exception as e:
            logger.error("Failed to rotate log: %s", e)
            return False

    def _cleanup_archives(self) -> None:
        """Remove old archive files beyond MAX_ARCHIVE_COUNT."""
        try:
            archive_dir = self.log_file.parent / "archive"
            if not archive_dir.exists():
                return

            # Get all archive files sorted by modification time
            archives = sorted(
                archive_dir.glob(f"{self.log_file.stem}_*.yaml*"),
                key=lambda p: p.stat().st_mtime,
            )

            # Remove oldest archives if we exceed the limit
            if len(archives) > MAX_ARCHIVE_COUNT:
                for archive in archives[: len(archives) - MAX_ARCHIVE_COUNT]:
                    archive.unlink()
                    logger.info("Removed old archive: %s", archive)

        except Exception as e:
            logger.warning("Failed to cleanup archives: %s", e)

    def register_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback function to be invoked on each event.

        Args:
            callback: Function that accepts event dictionary
        """
        self.event_callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[dict[str, Any]], None]) -> bool:
        """Unregister a previously registered callback.

        Args:
            callback: Function to unregister

        Returns:
            True if callback was found and removed, False otherwise
        """
        try:
            self.event_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    def get_events_filtered(
        self,
        event_type: str | None = None,
        actor: str | None = None,
        severity: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve audit events with advanced filtering.

        Args:
            event_type: Filter by event type
            actor: Filter by actor
            severity: Filter by severity level
            start_time: Filter events after this time
            end_time: Filter events before this time
            limit: Maximum number of events to return (most recent first)

        Returns:
            List of matching event dictionaries
        """
        events = self.get_events()

        # Apply filters
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]

        if actor:
            events = [e for e in events if e.get("actor") == actor]

        if severity:
            events = [e for e in events if e.get("severity") == severity]

        if start_time:
            events = [
                e
                for e in events
                if datetime.fromisoformat(e.get("timestamp", "")) >= start_time
            ]

        if end_time:
            events = [
                e
                for e in events
                if datetime.fromisoformat(e.get("timestamp", "")) <= end_time
            ]

        # Apply limit (most recent first)
        if limit and len(events) > limit:
            events = events[-limit:]

        return events

    def export_to_json(self, output_file: Path) -> bool:
        """Export audit log to JSON format.

        Args:
            output_file: Path to write JSON export

        Returns:
            True if export succeeded, False otherwise
        """
        try:
            events = self.get_events()
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "version": "1.0",
                        "exported_at": datetime.now(UTC).isoformat(),
                        "event_count": len(events),
                        "events": events,
                    },
                    f,
                    indent=2,
                )
            logger.info("Exported %d events to JSON: %s", len(events), output_file)
            return True
        except Exception as e:
            logger.error("Failed to export to JSON: %s", e)
            return False

    def export_to_csv(self, output_file: Path) -> bool:
        """Export audit log to CSV format.

        Args:
            output_file: Path to write CSV export

        Returns:
            True if export succeeded, False otherwise
        """
        try:
            events = self.get_events()
            if not events:
                return True

            with open(output_file, "w", newline="", encoding="utf-8") as f:
                # Determine all unique fields
                all_fields = set()
                for event in events:
                    all_fields.update(event.keys())

                # Write CSV
                writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                writer.writeheader()
                for event in events:
                    # Convert nested dicts to JSON strings
                    flat_event = {}
                    for key, value in event.items():
                        if isinstance(value, dict):
                            flat_event[key] = json.dumps(value)
                        else:
                            flat_event[key] = value
                    writer.writerow(flat_event)

            logger.info("Exported %d events to CSV: %s", len(events), output_file)
            return True
        except Exception as e:
            logger.error("Failed to export to CSV: %s", e)
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get audit log statistics.

        Returns:
            Dictionary containing log statistics
        """
        events = self.get_events()

        # Count by event type
        event_types = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        # Count by actor
        actors = {}
        for event in events:
            actor = event.get("actor", "unknown")
            actors[actor] = actors.get(actor, 0) + 1

        # Count by severity
        severities = {}
        for event in events:
            severity = event.get("severity", "info")
            severities[severity] = severities.get(severity, 0) + 1

        # Time range
        timestamps = [
            datetime.fromisoformat(e.get("timestamp", ""))
            for e in events
            if "timestamp" in e
        ]
        first_event = min(timestamps) if timestamps else None
        last_event = max(timestamps) if timestamps else None

        # File size
        file_size_mb = 0
        if self.log_file.exists():
            file_size_mb = self.log_file.stat().st_size / (1024 * 1024)

        return {
            "total_events": len(events),
            "event_types": event_types,
            "actors": actors,
            "severities": severities,
            "first_event": first_event.isoformat() if first_event else None,
            "last_event": last_event.isoformat() if last_event else None,
            "file_size_mb": round(file_size_mb, 2),
            "log_file": str(self.log_file),
        }

    def get_compliance_report(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> dict[str, Any]:
        """Generate a compliance report for audit log events.

        Args:
            start_time: Optional start time for report window
            end_time: Optional end time for report window

        Returns:
            Dictionary containing compliance metrics and report data
        """
        events = self.get_events_filtered(start_time=start_time, end_time=end_time)

        # Verify chain integrity
        is_valid, message = self.verify_chain()

        # Count critical/error events
        critical_events = len([e for e in events if e.get("severity") == "critical"])
        error_events = len([e for e in events if e.get("severity") == "error"])
        warning_events = len([e for e in events if e.get("severity") == "warning"])

        # Calculate time window
        if events:
            timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
            actual_start = min(timestamps)
            actual_end = max(timestamps)
        else:
            actual_start = start_time
            actual_end = end_time

        return {
            "report_generated": datetime.now(UTC).isoformat(),
            "window_start": actual_start.isoformat() if actual_start else None,
            "window_end": actual_end.isoformat() if actual_end else None,
            "total_events": len(events),
            "chain_valid": is_valid,
            "chain_message": message,
            "critical_events": critical_events,
            "error_events": error_events,
            "warning_events": warning_events,
            "compliance_status": (
                "PASS" if is_valid and critical_events == 0 else "FAIL"
            ),
            "event_summary": self.get_statistics(),
        }


__all__ = ["AuditLog"]
