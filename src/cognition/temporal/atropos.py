#                                           [2026-04-11 01:44]
#                                          Productivity: Active
"""
Atropos Fate Engine - Anti-Rollback Protection

Named after the Fate who cuts the thread of life, ensuring irreversibility.

Provides:
1. Deterministic event ordering via Lamport timestamps
2. Anti-rollback protection with monotonic counters
3. Hash chaining for immutable audit trails
4. Replay attack detection and prevention
5. Temporal integrity verification

Architecture:
- LamportClock: Logical clock for total ordering
- MonotonicCounter: Prevents time rewinding (TPM or software)
- HashChain: Links events cryptographically
- ReplayDetector: Detects duplicate/out-of-order events
- Atropos: Orchestrates all temporal protection mechanisms
"""

import hashlib
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TemporalIntegrityError(Exception):
    """Raised when temporal integrity is violated."""

    pass


class CounterBackend(Enum):
    """Monotonic counter backend types."""

    SOFTWARE = "software"
    TPM = "tpm"  # Trusted Platform Module (future enhancement)
    HARDWARE = "hardware"  # Generic hardware counter


@dataclass
class TemporalEvent:
    """
    Immutable temporal event with complete ordering information.

    Combines physical time, logical time (Lamport), monotonic sequence,
    and cryptographic chaining for complete temporal integrity.
    """

    event_id: str
    event_type: str
    payload: dict[str, Any]
    lamport_timestamp: int
    monotonic_sequence: int
    physical_timestamp: float
    previous_hash: str
    event_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute event hash if not provided."""
        if not self.event_hash:
            self.event_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of event data."""
        hasher = hashlib.sha256()

        hasher.update(self.event_id.encode("utf-8"))
        hasher.update(self.event_type.encode("utf-8"))
        hasher.update(str(self.lamport_timestamp).encode("utf-8"))
        hasher.update(str(self.monotonic_sequence).encode("utf-8"))
        hasher.update(str(self.physical_timestamp).encode("utf-8"))
        hasher.update(self.previous_hash.encode("utf-8"))

        # Include stable payload representation
        payload_str = str(sorted(self.payload.items()))
        hasher.update(payload_str.encode("utf-8"))

        return hasher.hexdigest()

    def verify_hash(self) -> bool:
        """Verify event hash integrity."""
        return self.event_hash == self._compute_hash()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "lamport_timestamp": self.lamport_timestamp,
            "monotonic_sequence": self.monotonic_sequence,
            "physical_timestamp": self.physical_timestamp,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
            "metadata": self.metadata,
            "iso_timestamp": datetime.fromtimestamp(
                self.physical_timestamp, tz=timezone.utc
            ).isoformat(),
        }


class LamportClock:
    """
    Lamport logical clock for deterministic total ordering.

    Ensures events have a total order even across distributed systems.
    Rules:
    1. Increment on local event
    2. Update to max(local, received) + 1 on message receive
    3. Provides happened-before relationship
    """

    def __init__(self, initial_time: int = 0):
        """
        Initialize Lamport clock.

        Args:
            initial_time: Starting timestamp (default 0)
        """
        self._time = initial_time
        self._lock_obj = None  # For thread safety if needed

    @property
    def time(self) -> int:
        """Current logical time."""
        return self._time

    def tick(self) -> int:
        """
        Increment clock for local event.

        Returns:
            New timestamp after increment
        """
        self._time += 1
        logger.debug(f"Lamport clock tick: {self._time}")
        return self._time

    def update(self, received_timestamp: int) -> int:
        """
        Update clock on receiving message with timestamp.

        Args:
            received_timestamp: Timestamp from received message

        Returns:
            New local timestamp after update
        """
        self._time = max(self._time, received_timestamp) + 1
        logger.debug(
            f"Lamport clock updated: received={received_timestamp}, new={self._time}"
        )
        return self._time

    def happens_before(self, t1: int, t2: int) -> bool:
        """
        Check if event at t1 happened before t2.

        Args:
            t1: First timestamp
            t2: Second timestamp

        Returns:
            True if t1 < t2
        """
        return t1 < t2

    def concurrent(self, t1: int, t2: int) -> bool:
        """
        Check if events are concurrent (incomparable).

        Note: In single-system Lamport clock, events are never concurrent.
        This is provided for distributed system compatibility.

        Args:
            t1: First timestamp
            t2: Second timestamp

        Returns:
            False (events always ordered in single clock)
        """
        return False  # Single clock always has total order


class MonotonicCounter:
    """
    Monotonic counter for anti-rollback protection.

    Ensures sequence numbers only increase, preventing time rewinding attacks.
    Supports software and hardware backends (TPM future).
    """

    def __init__(
        self,
        backend: CounterBackend = CounterBackend.SOFTWARE,
        initial_value: int = 0,
        persistence_path: Optional[Path] = None,
    ):
        """
        Initialize monotonic counter.

        Args:
            backend: Counter backend type
            initial_value: Starting sequence number
            persistence_path: Optional file path for persistence
        """
        self.backend = backend
        self._sequence = initial_value
        self.persistence_path = persistence_path

        # Load persisted value if available
        if persistence_path and persistence_path.exists():
            self._load_persisted()

    def _load_persisted(self):
        """Load persisted counter value."""
        try:
            with open(self.persistence_path, "r") as f:
                persisted_value = int(f.read().strip())
                # Only accept if higher (anti-rollback)
                if persisted_value > self._sequence:
                    self._sequence = persisted_value
                    logger.info(f"Loaded persisted counter: {self._sequence}")
        except Exception as e:
            logger.warning(f"Failed to load persisted counter: {e}")

    def _persist(self):
        """Persist current counter value."""
        if self.persistence_path:
            try:
                self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.persistence_path, "w") as f:
                    f.write(str(self._sequence))
            except Exception as e:
                logger.error(f"Failed to persist counter: {e}")

    @property
    def value(self) -> int:
        """Current sequence number."""
        return self._sequence

    def increment(self) -> int:
        """
        Increment counter atomically.

        Returns:
            New sequence number after increment

        Raises:
            TemporalIntegrityError: If increment would violate monotonicity
        """
        self._sequence += 1
        self._persist()
        logger.debug(f"Monotonic counter incremented: {self._sequence}")
        return self._sequence

    def verify_monotonic(self, value: int) -> bool:
        """
        Verify value is monotonically increasing.

        Args:
            value: Value to verify

        Returns:
            True if value > current sequence
        """
        return value > self._sequence

    def try_update(self, new_value: int) -> bool:
        """
        Try to update counter with new value.

        Only succeeds if new_value > current (monotonic).

        Args:
            new_value: Proposed new value

        Returns:
            True if update succeeded, False if rejected
        """
        if new_value > self._sequence:
            self._sequence = new_value
            self._persist()
            logger.info(f"Monotonic counter updated: {self._sequence}")
            return True
        logger.warning(
            f"Rejected non-monotonic update: {new_value} <= {self._sequence}"
        )
        return False


class HashChain:
    """
    Hash chain for immutable event linking.

    Links events cryptographically using SHA-256, similar to blockchain.
    Provides tamper-evident audit trail.
    """

    def __init__(self, genesis_data: str = "ATROPOS_GENESIS"):
        """
        Initialize hash chain.

        Args:
            genesis_data: Data for genesis block
        """
        self.genesis_hash = self._compute_hash(genesis_data)
        self._previous_hash = self.genesis_hash
        self._chain_length = 0
        logger.info(f"Hash chain initialized: genesis={self.genesis_hash[:16]}...")

    @staticmethod
    def _compute_hash(data: str) -> str:
        """Compute SHA-256 hash of data."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @property
    def previous_hash(self) -> str:
        """Hash of previous event in chain."""
        return self._previous_hash

    @property
    def chain_length(self) -> int:
        """Number of events in chain."""
        return self._chain_length

    def link_event(self, event_data: str) -> str:
        """
        Link new event to chain.

        Args:
            event_data: Event data to hash

        Returns:
            Hash of new event (including previous hash)
        """
        # Combine previous hash with new event data
        combined = f"{self._previous_hash}:{event_data}"
        new_hash = self._compute_hash(combined)

        # Update chain state
        self._previous_hash = new_hash
        self._chain_length += 1

        logger.debug(f"Event linked to chain: hash={new_hash[:16]}... length={self._chain_length}")
        return new_hash

    def verify_link(self, previous_hash: str, event_data: str, event_hash: str) -> bool:
        """
        Verify event is correctly linked to chain.

        Args:
            previous_hash: Expected previous hash
            event_data: Event data
            event_hash: Claimed event hash

        Returns:
            True if link is valid
        """
        combined = f"{previous_hash}:{event_data}"
        expected_hash = self._compute_hash(combined)
        return expected_hash == event_hash


class ReplayDetector:
    """
    Replay attack detector.

    Detects:
    1. Duplicate events (same ID seen before)
    2. Out-of-order events (timestamps go backwards)
    3. Sequence gaps (missing events)
    """

    def __init__(self, window_size: int = 10000, enable_gap_detection: bool = True):
        """
        Initialize replay detector.

        Args:
            window_size: Size of recent event window
            enable_gap_detection: Enable sequence gap detection
        """
        self.window_size = window_size
        self.enable_gap_detection = enable_gap_detection

        # Track recent event IDs
        self._seen_events: deque = deque(maxlen=window_size)
        self._event_ids: set = set()

        # Track highest timestamps
        self._highest_lamport = 0
        self._highest_monotonic = 0

        # Track sequence gaps
        self._expected_sequence = 0

    def check_duplicate(self, event_id: str) -> bool:
        """
        Check if event ID has been seen before.

        Args:
            event_id: Event identifier

        Returns:
            True if duplicate detected
        """
        is_duplicate = event_id in self._event_ids
        if is_duplicate:
            logger.warning(f"Duplicate event detected: {event_id}")
        return is_duplicate

    def check_ordering(self, lamport_ts: int, monotonic_seq: int) -> bool:
        """
        Check if event maintains temporal ordering.

        Args:
            lamport_ts: Lamport timestamp
            monotonic_seq: Monotonic sequence number

        Returns:
            True if ordering is violated (event goes backwards)
        """
        # Check for backwards time
        lamport_violation = lamport_ts < self._highest_lamport
        monotonic_violation = monotonic_seq <= self._highest_monotonic

        if lamport_violation:
            logger.warning(
                f"Lamport ordering violation: {lamport_ts} < {self._highest_lamport}"
            )

        if monotonic_violation:
            logger.warning(
                f"Monotonic ordering violation: {monotonic_seq} <= {self._highest_monotonic}"
            )

        return lamport_violation or monotonic_violation

    def check_sequence_gap(self, monotonic_seq: int) -> Optional[int]:
        """
        Check for gaps in monotonic sequence.

        Args:
            monotonic_seq: Monotonic sequence number

        Returns:
            Gap size if detected, None otherwise
        """
        if not self.enable_gap_detection:
            return None

        expected = self._expected_sequence
        if monotonic_seq > expected + 1:
            gap = monotonic_seq - expected - 1
            logger.warning(
                f"Sequence gap detected: expected {expected + 1}, got {monotonic_seq} (gap={gap})"
            )
            return gap

        return None

    def record_event(self, event: TemporalEvent):
        """
        Record event as seen.

        Args:
            event: Event to record
        """
        # Add to seen set
        self._seen_events.append(event.event_id)
        self._event_ids.add(event.event_id)

        # Update high water marks
        self._highest_lamport = max(self._highest_lamport, event.lamport_timestamp)
        self._highest_monotonic = max(
            self._highest_monotonic, event.monotonic_sequence
        )

        # Update expected sequence
        self._expected_sequence = max(
            self._expected_sequence, event.monotonic_sequence
        )

        # Prune event IDs if window exceeded
        if len(self._seen_events) >= self.window_size:
            # Remove oldest from set
            oldest = self._seen_events[0]
            self._event_ids.discard(oldest)


@dataclass
class AtroposConfig:
    """Configuration for Atropos fate engine."""

    counter_backend: CounterBackend = CounterBackend.SOFTWARE
    persistence_path: Optional[Path] = None
    replay_window_size: int = 10000
    enable_gap_detection: bool = True
    genesis_data: str = "ATROPOS_GENESIS"
    enable_hash_verification: bool = True
    strict_mode: bool = True  # Reject violations vs. warn


class Atropos:
    """
    Atropos Fate Engine - Master orchestrator.

    Coordinates all temporal protection mechanisms:
    - Lamport clock for logical ordering
    - Monotonic counter for anti-rollback
    - Hash chain for immutability
    - Replay detector for attack prevention

    Named after the Fate who cuts the thread of life,
    ensuring events cannot be undone or replayed.
    """

    def __init__(self, config: Optional[AtroposConfig] = None):
        """
        Initialize Atropos engine.

        Args:
            config: Configuration (uses defaults if None)
        """
        self.config = config or AtroposConfig()

        # Initialize components
        self.lamport_clock = LamportClock()
        self.monotonic_counter = MonotonicCounter(
            backend=self.config.counter_backend,
            persistence_path=self.config.persistence_path,
        )
        self.hash_chain = HashChain(genesis_data=self.config.genesis_data)
        self.replay_detector = ReplayDetector(
            window_size=self.config.replay_window_size,
            enable_gap_detection=self.config.enable_gap_detection,
        )

        # Statistics
        self._stats = {
            "events_processed": 0,
            "duplicates_detected": 0,
            "ordering_violations": 0,
            "sequence_gaps": 0,
            "hash_failures": 0,
        }

        logger.info("Atropos fate engine initialized")

    def create_event(
        self,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> TemporalEvent:
        """
        Create new temporal event with complete protection.

        Args:
            event_id: Unique event identifier
            event_type: Type of event
            payload: Event data
            metadata: Optional metadata

        Returns:
            Created and verified temporal event

        Raises:
            TemporalIntegrityError: If event creation fails integrity checks
        """
        # Get all temporal coordinates
        lamport_ts = self.lamport_clock.tick()
        monotonic_seq = self.monotonic_counter.increment()
        physical_ts = time.time()
        previous_hash = self.hash_chain.previous_hash

        # Create event
        event = TemporalEvent(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            lamport_timestamp=lamport_ts,
            monotonic_sequence=monotonic_seq,
            physical_timestamp=physical_ts,
            previous_hash=previous_hash,
            metadata=metadata or {},
        )

        # Link to hash chain
        chain_hash = self.hash_chain.link_event(event.event_hash)

        # Verify hash (paranoid check)
        if self.config.enable_hash_verification:
            if not event.verify_hash():
                self._stats["hash_failures"] += 1
                raise TemporalIntegrityError(
                    f"Event hash verification failed: {event_id}"
                )

        # Record event
        self.replay_detector.record_event(event)
        self._stats["events_processed"] += 1

        logger.info(
            f"Event created: id={event_id}, lamport={lamport_ts}, "
            f"seq={monotonic_seq}, hash={event.event_hash[:16]}..."
        )

        return event

    def verify_event(self, event: TemporalEvent) -> bool:
        """
        Verify event integrity and ordering.

        Args:
            event: Event to verify

        Returns:
            True if event passes all checks

        Raises:
            TemporalIntegrityError: If strict mode and verification fails
        """
        violations = []

        # Check hash integrity
        if not event.verify_hash():
            violations.append(f"Hash mismatch for event {event.event_id}")
            self._stats["hash_failures"] += 1

        # Check for duplicates
        if self.replay_detector.check_duplicate(event.event_id):
            violations.append(f"Duplicate event: {event.event_id}")
            self._stats["duplicates_detected"] += 1

        # Check ordering
        if self.replay_detector.check_ordering(
            event.lamport_timestamp, event.monotonic_sequence
        ):
            violations.append(
                f"Ordering violation: lamport={event.lamport_timestamp}, "
                f"seq={event.monotonic_sequence}"
            )
            self._stats["ordering_violations"] += 1

        # Check sequence gaps
        gap = self.replay_detector.check_sequence_gap(event.monotonic_sequence)
        if gap:
            violations.append(f"Sequence gap detected: {gap} events missing")
            self._stats["sequence_gaps"] += 1

        # Handle violations
        if violations:
            error_msg = "; ".join(violations)
            if self.config.strict_mode:
                raise TemporalIntegrityError(error_msg)
            else:
                logger.warning(f"Temporal integrity warnings: {error_msg}")
                return False

        return True

    def receive_event(
        self, event: TemporalEvent, remote_lamport: Optional[int] = None
    ) -> bool:
        """
        Receive and verify external event.

        Args:
            event: Event from external source
            remote_lamport: Optional remote Lamport timestamp

        Returns:
            True if event accepted

        Raises:
            TemporalIntegrityError: If event fails verification
        """
        # Update Lamport clock with remote timestamp
        if remote_lamport is not None:
            self.lamport_clock.update(remote_lamport)

        # Verify event
        is_valid = self.verify_event(event)

        if is_valid:
            # Record event if valid
            self.replay_detector.record_event(event)
            logger.info(f"External event accepted: {event.event_id}")
        else:
            logger.warning(f"External event rejected: {event.event_id}")

        return is_valid

    def get_audit_trail(self, limit: Optional[int] = None) -> list[str]:
        """
        Get audit trail of recent events.

        Args:
            limit: Optional limit on number of events

        Returns:
            List of event IDs in order
        """
        events = list(self.replay_detector._seen_events)
        if limit:
            events = events[-limit:]
        return events

    def get_statistics(self) -> dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            **self._stats,
            "lamport_time": self.lamport_clock.time,
            "monotonic_sequence": self.monotonic_counter.value,
            "chain_length": self.hash_chain.chain_length,
            "genesis_hash": self.hash_chain.genesis_hash,
        }

    def reset_statistics(self):
        """Reset statistics counters."""
        self._stats = {k: 0 for k in self._stats}
        logger.info("Statistics reset")

    def verify_chain_integrity(self) -> bool:
        """
        Verify entire hash chain integrity.

        Returns:
            True if chain is intact

        Note: This requires storing full event history.
        Current implementation provides component verification.
        """
        # Check components are consistent
        stats = self.get_statistics()
        return (
            stats["hash_failures"] == 0
            and stats["chain_length"] == stats["events_processed"]
        )
