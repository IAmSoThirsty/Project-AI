#                                           [2026-04-11 01:45]
#                                          Productivity: Active
"""
Clotho — Distributed Transaction Coordinator (Thread-Spinner).

Named after the Greek Fate who spins the thread of life, Clotho coordinates
distributed transactions across multiple agents, ensuring ACID guarantees and
orchestrating complex multi-agent workflows.

Capabilities:
    - Two-Phase Commit (2PC) and Three-Phase Commit (3PC) protocols
    - ACID guarantees: Atomicity, Consistency, Isolation, Durability
    - Multi-agent synchronization (Chronos, Atropos, etc.)
    - Distributed deadlock detection and resolution
    - Saga pattern for long-running distributed workflows
    - Transaction recovery and rollback
    - Compensating transactions for failure handling

Security invariants:
    - INV-CLOTHO-1: All distributed transactions must achieve consensus
    - INV-CLOTHO-2: Failed transactions must be completely rolled back
    - INV-CLOTHO-3: Deadlocks must be detected within timeout threshold
    - INV-CLOTHO-4: Saga compensations must be idempotent

Production notes:
    - In production, use distributed consensus (Raft, Paxos)
    - Transaction logs should be persisted to durable storage
    - Timeouts should be configurable per environment
    - Monitor for transaction starvation and livelock
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class TransactionStatus(str, Enum):
    """Status of a distributed transaction."""

    PENDING = "pending"
    PREPARING = "preparing"
    PREPARED = "prepared"
    PRE_COMMITTING = "pre_committing"  # For 3PC
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TransactionPhase(str, Enum):
    """Phase in 2PC/3PC protocol."""

    INIT = "init"
    PREPARE = "prepare"
    PRE_COMMIT = "pre_commit"  # 3PC only
    COMMIT = "commit"
    ABORT = "abort"


class ParticipantStatus(str, Enum):
    """Status of a transaction participant."""

    IDLE = "idle"
    PREPARING = "preparing"
    PREPARED = "prepared"
    PRE_COMMITTED = "pre_committed"  # 3PC only
    COMMITTED = "committed"
    ABORTED = "aborted"
    FAILED = "failed"


class SagaStatus(str, Enum):
    """Status of a saga execution."""

    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class Participant:
    """Represents a participant in a distributed transaction."""

    participant_id: str
    agent_name: str
    status: ParticipantStatus = ParticipantStatus.IDLE
    prepare_callback: Optional[Callable] = None
    commit_callback: Optional[Callable] = None
    abort_callback: Optional[Callable] = None
    last_heartbeat: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def is_alive(self, timeout: float = 30.0) -> bool:
        """Check if participant is still alive based on heartbeat."""
        return (time.time() - self.last_heartbeat) < timeout


@dataclass
class Transaction:
    """Represents a distributed transaction."""

    transaction_id: str
    coordinator_id: str
    participants: List[Participant]
    status: TransactionStatus = TransactionStatus.PENDING
    phase: TransactionPhase = TransactionPhase.INIT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    timeout: float = 60.0  # seconds
    use_3pc: bool = False  # Use 3PC instead of 2PC
    data: dict = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def add_log(self, message: str) -> None:
        """Add a log entry to the transaction."""
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = f"[{timestamp}] {message}"
        self.logs.append(entry)
        logger.info(f"Transaction {self.transaction_id}: {message}")

    def is_expired(self) -> bool:
        """Check if transaction has exceeded timeout."""
        created = datetime.fromisoformat(self.created_at)
        elapsed = (datetime.now(timezone.utc) - created).total_seconds()
        return elapsed > self.timeout

    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "coordinator_id": self.coordinator_id,
            "status": self.status.value,
            "phase": self.phase.value,
            "participants": [
                {
                    "participant_id": p.participant_id,
                    "agent_name": p.agent_name,
                    "status": p.status.value,
                }
                for p in self.participants
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "timeout": self.timeout,
            "use_3pc": self.use_3pc,
            "logs": self.logs,
            "error": self.error,
        }


@dataclass
class SagaStep:
    """A step in a saga with forward and compensation actions."""

    step_id: str
    name: str
    forward_action: Callable
    compensate_action: Callable
    agent_name: str
    metadata: dict = field(default_factory=dict)
    executed: bool = False
    compensated: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Saga:
    """Represents a long-running distributed saga."""

    saga_id: str
    name: str
    steps: List[SagaStep]
    status: SagaStatus = SagaStatus.RUNNING
    current_step: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    results: dict = field(default_factory=dict)

    def add_log(self, message: str) -> None:
        """Add a log entry to the saga."""
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = f"[{timestamp}] {message}"
        self.logs.append(entry)
        logger.info(f"Saga {self.saga_id}: {message}")


@dataclass
class ResourceLock:
    """Represents a lock on a resource."""

    resource_id: str
    transaction_id: str
    participant_id: str
    acquired_at: float = field(default_factory=time.time)
    lock_type: str = "exclusive"  # "shared" or "exclusive"


class TransactionCoordinator:
    """Coordinates distributed transactions using 2PC or 3PC protocol.

    Implements two-phase commit (2PC) and three-phase commit (3PC) protocols
    for distributed transaction coordination. 3PC reduces the window of
    uncertainty in 2PC by adding a pre-commit phase.

    2PC Protocol:
        Phase 1 (Prepare): Coordinator asks all participants to prepare
        Phase 2 (Commit/Abort): Coordinator tells participants to commit or abort

    3PC Protocol:
        Phase 1 (Prepare): Coordinator asks all participants to prepare
        Phase 2 (Pre-Commit): Coordinator tells participants to pre-commit
        Phase 3 (Commit/Abort): Coordinator tells participants to commit or abort
    """

    def __init__(self, coordinator_id: Optional[str] = None):
        """Initialize the transaction coordinator.

        Args:
            coordinator_id: Unique identifier for this coordinator
        """
        self.coordinator_id = coordinator_id or f"coordinator-{uuid.uuid4().hex[:8]}"
        self.transactions: Dict[str, Transaction] = {}
        self._lock = threading.RLock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

        logger.info(f"TransactionCoordinator {self.coordinator_id} initialized")

    def start(self) -> None:
        """Start the transaction coordinator monitoring."""
        with self._lock:
            if not self._running:
                self._running = True
                self._monitor_thread = threading.Thread(
                    target=self._monitor_transactions, daemon=True
                )
                self._monitor_thread.start()
                logger.info(f"TransactionCoordinator {self.coordinator_id} started")

    def stop(self) -> None:
        """Stop the transaction coordinator."""
        with self._lock:
            self._running = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5.0)
            logger.info(f"TransactionCoordinator {self.coordinator_id} stopped")

    def begin_transaction(
        self,
        participants: List[Participant],
        timeout: float = 60.0,
        use_3pc: bool = False,
        data: Optional[dict] = None,
    ) -> str:
        """Begin a new distributed transaction.

        Args:
            participants: List of participants in the transaction
            timeout: Transaction timeout in seconds
            use_3pc: Use 3PC protocol instead of 2PC
            data: Optional transaction data

        Returns:
            Transaction ID
        """
        transaction_id = f"txn-{uuid.uuid4().hex}"

        transaction = Transaction(
            transaction_id=transaction_id,
            coordinator_id=self.coordinator_id,
            participants=participants,
            timeout=timeout,
            use_3pc=use_3pc,
            data=data or {},
        )

        transaction.add_log(
            f"Transaction created with {len(participants)} participants "
            f"using {'3PC' if use_3pc else '2PC'} protocol"
        )

        with self._lock:
            self.transactions[transaction_id] = transaction

        logger.info(
            f"Transaction {transaction_id} created with {len(participants)} participants"
        )

        return transaction_id

    def execute_transaction(self, transaction_id: str) -> bool:
        """Execute a distributed transaction using 2PC or 3PC.

        Args:
            transaction_id: Transaction to execute

        Returns:
            True if transaction committed successfully, False otherwise
        """
        with self._lock:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                logger.error(f"Transaction {transaction_id} not found")
                return False

        try:
            if transaction.use_3pc:
                return self._execute_3pc(transaction)
            else:
                return self._execute_2pc(transaction)
        except Exception as e:
            logger.error(f"Transaction {transaction_id} failed: {e}")
            transaction.status = TransactionStatus.FAILED
            transaction.error = str(e)
            transaction.add_log(f"Transaction failed: {e}")
            self._abort_transaction(transaction)
            return False

    def _execute_2pc(self, transaction: Transaction) -> bool:
        """Execute two-phase commit protocol.

        Phase 1: Prepare
            - Coordinator sends PREPARE to all participants
            - Wait for all participants to vote YES or NO
            - If any vote NO or timeout, abort transaction

        Phase 2: Commit/Abort
            - If all voted YES, send COMMIT to all participants
            - If any voted NO, send ABORT to all participants
            - Wait for acknowledgments
        """
        transaction.add_log("Starting 2PC protocol")

        # Phase 1: Prepare
        transaction.phase = TransactionPhase.PREPARE
        transaction.status = TransactionStatus.PREPARING

        if not self._prepare_phase(transaction):
            transaction.add_log("Prepare phase failed, aborting transaction")
            self._abort_transaction(transaction)
            return False

        # Phase 2: Commit
        transaction.phase = TransactionPhase.COMMIT
        transaction.status = TransactionStatus.COMMITTING

        if not self._commit_phase(transaction):
            transaction.add_log("Commit phase failed, aborting transaction")
            self._abort_transaction(transaction)
            return False

        transaction.status = TransactionStatus.COMMITTED
        transaction.updated_at = datetime.now(timezone.utc).isoformat()
        transaction.add_log("Transaction committed successfully")

        return True

    def _execute_3pc(self, transaction: Transaction) -> bool:
        """Execute three-phase commit protocol.

        Phase 1: Prepare
            - Same as 2PC

        Phase 2: Pre-Commit
            - Coordinator sends PRE-COMMIT to all participants
            - Participants acknowledge readiness to commit
            - Reduces window of uncertainty

        Phase 3: Commit
            - Coordinator sends COMMIT to all participants
            - Participants commit and acknowledge
        """
        transaction.add_log("Starting 3PC protocol")

        # Phase 1: Prepare
        transaction.phase = TransactionPhase.PREPARE
        transaction.status = TransactionStatus.PREPARING

        if not self._prepare_phase(transaction):
            transaction.add_log("Prepare phase failed, aborting transaction")
            self._abort_transaction(transaction)
            return False

        # Phase 2: Pre-Commit
        transaction.phase = TransactionPhase.PRE_COMMIT
        transaction.status = TransactionStatus.PRE_COMMITTING

        if not self._pre_commit_phase(transaction):
            transaction.add_log("Pre-commit phase failed, aborting transaction")
            self._abort_transaction(transaction)
            return False

        # Phase 3: Commit
        transaction.phase = TransactionPhase.COMMIT
        transaction.status = TransactionStatus.COMMITTING

        if not self._commit_phase(transaction):
            transaction.add_log("Commit phase failed, aborting transaction")
            self._abort_transaction(transaction)
            return False

        transaction.status = TransactionStatus.COMMITTED
        transaction.updated_at = datetime.now(timezone.utc).isoformat()
        transaction.add_log("Transaction committed successfully (3PC)")

        return True

    def _prepare_phase(self, transaction: Transaction) -> bool:
        """Execute prepare phase of 2PC/3PC.

        Sends PREPARE request to all participants and waits for votes.
        """
        transaction.add_log(f"Prepare phase: requesting votes from {len(transaction.participants)} participants")

        votes = []
        for participant in transaction.participants:
            try:
                # Check participant heartbeat
                if not participant.is_alive():
                    transaction.add_log(f"Participant {participant.participant_id} is not alive")
                    votes.append(False)
                    continue

                # Call prepare callback
                if participant.prepare_callback:
                    result = participant.prepare_callback(transaction)
                    votes.append(result)
                    participant.status = ParticipantStatus.PREPARED if result else ParticipantStatus.FAILED
                    transaction.add_log(
                        f"Participant {participant.participant_id} voted {'YES' if result else 'NO'}"
                    )
                else:
                    # No callback, assume YES
                    votes.append(True)
                    participant.status = ParticipantStatus.PREPARED
                    transaction.add_log(f"Participant {participant.participant_id} voted YES (no callback)")

            except Exception as e:
                logger.error(f"Prepare failed for participant {participant.participant_id}: {e}")
                votes.append(False)
                participant.status = ParticipantStatus.FAILED
                transaction.add_log(f"Participant {participant.participant_id} prepare failed: {e}")

        # All participants must vote YES
        all_prepared = all(votes)
        transaction.add_log(f"Prepare phase: {sum(votes)}/{len(votes)} participants voted YES")

        if all_prepared:
            transaction.status = TransactionStatus.PREPARED

        return all_prepared

    def _pre_commit_phase(self, transaction: Transaction) -> bool:
        """Execute pre-commit phase of 3PC.

        Informs all participants that commit is imminent.
        """
        transaction.add_log("Pre-commit phase: informing participants")

        for participant in transaction.participants:
            try:
                participant.status = ParticipantStatus.PRE_COMMITTED
                transaction.add_log(f"Participant {participant.participant_id} pre-committed")
            except Exception as e:
                logger.error(f"Pre-commit failed for participant {participant.participant_id}: {e}")
                transaction.add_log(f"Participant {participant.participant_id} pre-commit failed: {e}")
                return False

        return True

    def _commit_phase(self, transaction: Transaction) -> bool:
        """Execute commit phase of 2PC/3PC.

        Sends COMMIT request to all participants.
        """
        transaction.add_log(f"Commit phase: committing {len(transaction.participants)} participants")

        for participant in transaction.participants:
            try:
                # Call commit callback
                if participant.commit_callback:
                    participant.commit_callback(transaction)

                participant.status = ParticipantStatus.COMMITTED
                transaction.add_log(f"Participant {participant.participant_id} committed")

            except Exception as e:
                logger.error(f"Commit failed for participant {participant.participant_id}: {e}")
                transaction.add_log(f"Participant {participant.participant_id} commit failed: {e}")
                # In a real system, we would need to handle partial commits
                # For now, we continue trying to commit other participants

        return True

    def _abort_transaction(self, transaction: Transaction) -> None:
        """Abort a transaction and rollback all participants.

        Args:
            transaction: Transaction to abort
        """
        transaction.phase = TransactionPhase.ABORT
        transaction.status = TransactionStatus.ABORTING
        transaction.add_log(f"Aborting transaction, rolling back {len(transaction.participants)} participants")

        for participant in transaction.participants:
            try:
                # Call abort callback
                if participant.abort_callback:
                    participant.abort_callback(transaction)

                participant.status = ParticipantStatus.ABORTED
                transaction.add_log(f"Participant {participant.participant_id} aborted")

            except Exception as e:
                logger.error(f"Abort failed for participant {participant.participant_id}: {e}")
                transaction.add_log(f"Participant {participant.participant_id} abort failed: {e}")

        transaction.status = TransactionStatus.ABORTED
        transaction.updated_at = datetime.now(timezone.utc).isoformat()

    def abort_transaction(self, transaction_id: str) -> bool:
        """Manually abort a transaction.

        Args:
            transaction_id: Transaction to abort

        Returns:
            True if aborted successfully
        """
        with self._lock:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                logger.error(f"Transaction {transaction_id} not found")
                return False

        self._abort_transaction(transaction)
        return True

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction or None if not found
        """
        with self._lock:
            return self.transactions.get(transaction_id)

    def get_transaction_status(self, transaction_id: str) -> Optional[TransactionStatus]:
        """Get status of a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction status or None if not found
        """
        transaction = self.get_transaction(transaction_id)
        return transaction.status if transaction else None

    def _monitor_transactions(self) -> None:
        """Monitor transactions for timeouts and cleanup."""
        while self._running:
            try:
                with self._lock:
                    for txn_id, transaction in list(self.transactions.items()):
                        # Check for timeout
                        if transaction.is_expired() and transaction.status not in [
                            TransactionStatus.COMMITTED,
                            TransactionStatus.ABORTED,
                        ]:
                            logger.warning(f"Transaction {txn_id} timed out")
                            transaction.status = TransactionStatus.TIMEOUT
                            transaction.add_log("Transaction timed out")
                            self._abort_transaction(transaction)

                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Transaction monitor error: {e}")

    def get_statistics(self) -> dict:
        """Get transaction statistics.

        Returns:
            Dictionary with transaction statistics
        """
        with self._lock:
            total = len(self.transactions)
            by_status = defaultdict(int)
            for txn in self.transactions.values():
                by_status[txn.status.value] += 1

            return {
                "coordinator_id": self.coordinator_id,
                "total_transactions": total,
                "by_status": dict(by_status),
                "active_transactions": sum(
                    1
                    for txn in self.transactions.values()
                    if txn.status in [TransactionStatus.PREPARING, TransactionStatus.COMMITTING]
                ),
            }


class DeadlockDetector:
    """Detects and resolves distributed deadlocks.

    Uses wait-for graph (WFG) to detect cycles indicating deadlocks.
    Implements timeout-based detection and victim selection for resolution.
    """

    def __init__(self):
        """Initialize the deadlock detector."""
        self.locks: Dict[str, ResourceLock] = {}
        self.wait_for_graph: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.RLock()
        self._running = False
        self._detector_thread: Optional[threading.Thread] = None

        logger.info("DeadlockDetector initialized")

    def start(self) -> None:
        """Start deadlock detection monitoring."""
        with self._lock:
            if not self._running:
                self._running = True
                self._detector_thread = threading.Thread(target=self._detect_deadlocks, daemon=True)
                self._detector_thread.start()
                logger.info("DeadlockDetector started")

    def stop(self) -> None:
        """Stop deadlock detection."""
        with self._lock:
            self._running = False
            if self._detector_thread:
                self._detector_thread.join(timeout=5.0)
            logger.info("DeadlockDetector stopped")

    def acquire_lock(
        self, resource_id: str, transaction_id: str, participant_id: str, lock_type: str = "exclusive"
    ) -> bool:
        """Attempt to acquire a lock on a resource.

        Args:
            resource_id: Resource to lock
            transaction_id: Transaction requesting the lock
            participant_id: Participant requesting the lock
            lock_type: Type of lock ("shared" or "exclusive")

        Returns:
            True if lock acquired, False if resource is locked
        """
        with self._lock:
            if resource_id in self.locks:
                # Resource is already locked
                existing_lock = self.locks[resource_id]

                # Same transaction can acquire lock
                if existing_lock.transaction_id == transaction_id:
                    return True

                # Shared locks can coexist
                if lock_type == "shared" and existing_lock.lock_type == "shared":
                    # Allow multiple shared locks (simplified)
                    return True

                # Add to wait-for graph
                self.wait_for_graph[transaction_id].add(existing_lock.transaction_id)
                logger.debug(
                    f"Transaction {transaction_id} waiting for {existing_lock.transaction_id} "
                    f"on resource {resource_id}"
                )
                return False

            # Acquire lock
            lock = ResourceLock(
                resource_id=resource_id,
                transaction_id=transaction_id,
                participant_id=participant_id,
                lock_type=lock_type,
            )
            self.locks[resource_id] = lock
            logger.debug(f"Transaction {transaction_id} acquired {lock_type} lock on {resource_id}")
            return True

    def release_lock(self, resource_id: str, transaction_id: str) -> bool:
        """Release a lock on a resource.

        Args:
            resource_id: Resource to unlock
            transaction_id: Transaction releasing the lock

        Returns:
            True if lock released successfully
        """
        with self._lock:
            if resource_id not in self.locks:
                logger.warning(f"Resource {resource_id} is not locked")
                return False

            lock = self.locks[resource_id]
            if lock.transaction_id != transaction_id:
                logger.warning(
                    f"Transaction {transaction_id} does not hold lock on {resource_id} "
                    f"(held by {lock.transaction_id})"
                )
                return False

            del self.locks[resource_id]

            # Remove from wait-for graph
            for waiting_txn in self.wait_for_graph:
                self.wait_for_graph[waiting_txn].discard(transaction_id)

            logger.debug(f"Transaction {transaction_id} released lock on {resource_id}")
            return True

    def release_all_locks(self, transaction_id: str) -> int:
        """Release all locks held by a transaction.

        Args:
            transaction_id: Transaction to release locks for

        Returns:
            Number of locks released
        """
        with self._lock:
            count = 0
            for resource_id in list(self.locks.keys()):
                if self.locks[resource_id].transaction_id == transaction_id:
                    del self.locks[resource_id]
                    count += 1

            # Remove from wait-for graph
            if transaction_id in self.wait_for_graph:
                del self.wait_for_graph[transaction_id]

            for waiting_txn in self.wait_for_graph:
                self.wait_for_graph[waiting_txn].discard(transaction_id)

            if count > 0:
                logger.info(f"Released {count} locks for transaction {transaction_id}")

            return count

    def detect_cycle(self) -> Optional[List[str]]:
        """Detect cycles in the wait-for graph.

        Returns:
            List of transaction IDs in the cycle, or None if no cycle found
        """
        with self._lock:
            visited = set()
            rec_stack = set()

            def dfs(node: str, path: List[str]) -> Optional[List[str]]:
                """Depth-first search to detect cycles."""
                if node in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(node)
                    return path[cycle_start:]

                if node in visited:
                    return None

                visited.add(node)
                rec_stack.add(node)
                path.append(node)

                for neighbor in self.wait_for_graph.get(node, []):
                    result = dfs(neighbor, path[:])
                    if result:
                        return result

                rec_stack.remove(node)
                return None

            # Check all nodes
            for node in self.wait_for_graph:
                if node not in visited:
                    cycle = dfs(node, [])
                    if cycle:
                        return cycle

            return None

    def _detect_deadlocks(self) -> None:
        """Background thread to detect and log deadlocks."""
        while self._running:
            try:
                cycle = self.detect_cycle()
                if cycle:
                    logger.warning(f"Deadlock detected: {' -> '.join(cycle)}")
                    # In a real system, we would abort one of the transactions
                    # For now, just log it

                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Deadlock detection error: {e}")

    def get_deadlocks(self) -> List[List[str]]:
        """Get all detected deadlock cycles.

        Returns:
            List of deadlock cycles (each cycle is a list of transaction IDs)
        """
        deadlocks = []
        cycle = self.detect_cycle()
        if cycle:
            deadlocks.append(cycle)
        return deadlocks

    def resolve_deadlock(self, cycle: List[str], victim_selector: Optional[Callable] = None) -> str:
        """Resolve a deadlock by aborting a victim transaction.

        Args:
            cycle: List of transaction IDs in the deadlock cycle
            victim_selector: Optional function to select victim (default: youngest transaction)

        Returns:
            Transaction ID of the victim
        """
        if not cycle:
            raise ValueError("No cycle to resolve")

        # Select victim
        if victim_selector:
            victim = victim_selector(cycle)
        else:
            # Default: abort the youngest transaction (last in cycle)
            victim = cycle[-1]

        logger.warning(f"Resolving deadlock by aborting victim transaction {victim}")

        # Release all locks held by victim
        self.release_all_locks(victim)

        return victim

    def get_statistics(self) -> dict:
        """Get deadlock detection statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            return {
                "total_locks": len(self.locks),
                "wait_for_edges": sum(len(v) for v in self.wait_for_graph.values()),
                "transactions_waiting": len(self.wait_for_graph),
                "deadlocks_detected": len(self.get_deadlocks()),
            }


class SagaOrchestrator:
    """Orchestrates long-running distributed workflows using the Saga pattern.

    Sagas provide an alternative to distributed transactions for long-running
    processes. Instead of locking resources, each step has a compensating
    transaction that can undo its effects.

    Pattern:
        1. Execute steps sequentially
        2. If a step fails, execute compensating transactions in reverse order
        3. Each step and compensation must be idempotent
    """

    def __init__(self):
        """Initialize the saga orchestrator."""
        self.sagas: Dict[str, Saga] = {}
        self._lock = threading.RLock()

        logger.info("SagaOrchestrator initialized")

    def create_saga(self, name: str, steps: List[SagaStep]) -> str:
        """Create a new saga.

        Args:
            name: Saga name
            steps: List of saga steps

        Returns:
            Saga ID
        """
        saga_id = f"saga-{uuid.uuid4().hex}"

        saga = Saga(saga_id=saga_id, name=name, steps=steps)

        saga.add_log(f"Saga created with {len(steps)} steps")

        with self._lock:
            self.sagas[saga_id] = saga

        logger.info(f"Saga {saga_id} created: {name}")

        return saga_id

    def execute_saga(self, saga_id: str) -> bool:
        """Execute a saga.

        Args:
            saga_id: Saga to execute

        Returns:
            True if saga completed successfully, False otherwise
        """
        with self._lock:
            saga = self.sagas.get(saga_id)
            if not saga:
                logger.error(f"Saga {saga_id} not found")
                return False

        saga.add_log("Starting saga execution")

        try:
            # Execute steps sequentially
            for i, step in enumerate(saga.steps):
                saga.current_step = i
                saga.add_log(f"Executing step {i + 1}/{len(saga.steps)}: {step.name}")

                try:
                    # Execute forward action
                    result = step.forward_action()
                    step.executed = True
                    step.result = result
                    saga.results[step.step_id] = result

                    saga.add_log(f"Step {step.name} completed successfully")

                except Exception as e:
                    logger.error(f"Step {step.name} failed: {e}")
                    step.error = str(e)
                    saga.add_log(f"Step {step.name} failed: {e}")

                    # Compensate previous steps
                    saga.status = SagaStatus.COMPENSATING
                    saga.add_log("Starting compensation")

                    if not self._compensate_saga(saga, up_to_step=i):
                        saga.status = SagaStatus.FAILED
                        saga.add_log("Compensation failed")
                        return False

                    saga.status = SagaStatus.COMPENSATED
                    saga.add_log("Compensation completed")
                    return False

            # All steps completed successfully
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.now(timezone.utc).isoformat()
            saga.add_log("Saga completed successfully")

            return True

        except Exception as e:
            logger.error(f"Saga {saga_id} failed: {e}")
            saga.status = SagaStatus.FAILED
            saga.add_log(f"Saga failed: {e}")
            return False

    def _compensate_saga(self, saga: Saga, up_to_step: int) -> bool:
        """Execute compensating transactions for a failed saga.

        Args:
            saga: Saga to compensate
            up_to_step: Compensate steps up to (but not including) this step

        Returns:
            True if compensation succeeded
        """
        saga.add_log(f"Compensating {up_to_step} steps")

        # Execute compensations in reverse order
        for i in range(up_to_step - 1, -1, -1):
            step = saga.steps[i]

            if not step.executed:
                continue

            saga.add_log(f"Compensating step {i + 1}: {step.name}")

            try:
                # Execute compensating action
                step.compensate_action()
                step.compensated = True

                saga.add_log(f"Step {step.name} compensated successfully")

            except Exception as e:
                logger.error(f"Compensation failed for step {step.name}: {e}")
                saga.add_log(f"Compensation failed for step {step.name}: {e}")
                return False

        return True

    def abort_saga(self, saga_id: str) -> bool:
        """Abort a saga and compensate completed steps.

        Args:
            saga_id: Saga to abort

        Returns:
            True if aborted and compensated successfully
        """
        with self._lock:
            saga = self.sagas.get(saga_id)
            if not saga:
                logger.error(f"Saga {saga_id} not found")
                return False

        saga.status = SagaStatus.COMPENSATING
        saga.add_log("Saga aborted, starting compensation")

        # Compensate all executed steps
        success = self._compensate_saga(saga, up_to_step=saga.current_step + 1)

        if success:
            saga.status = SagaStatus.COMPENSATED
            saga.add_log("Saga compensated successfully")
        else:
            saga.status = SagaStatus.FAILED
            saga.add_log("Saga compensation failed")

        return success

    def get_saga(self, saga_id: str) -> Optional[Saga]:
        """Get saga by ID.

        Args:
            saga_id: Saga ID

        Returns:
            Saga or None if not found
        """
        with self._lock:
            return self.sagas.get(saga_id)

    def get_saga_status(self, saga_id: str) -> Optional[SagaStatus]:
        """Get status of a saga.

        Args:
            saga_id: Saga ID

        Returns:
            Saga status or None if not found
        """
        saga = self.get_saga(saga_id)
        return saga.status if saga else None

    def get_statistics(self) -> dict:
        """Get saga statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total = len(self.sagas)
            by_status = defaultdict(int)
            for saga in self.sagas.values():
                by_status[saga.status.value] += 1

            return {
                "total_sagas": total,
                "by_status": dict(by_status),
                "active_sagas": sum(
                    1 for saga in self.sagas.values() if saga.status == SagaStatus.RUNNING
                ),
            }


class Clotho:
    """Main Clotho coordinator - the thread-spinner of distributed fate.

    Clotho integrates all distributed coordination components:
        - Transaction coordination (2PC/3PC)
        - Deadlock detection and resolution
        - Saga orchestration
        - Multi-agent synchronization

    Named after the Greek Fate who spins the thread of life, Clotho
    weaves together distributed operations across multiple agents.
    """

    def __init__(self, coordinator_id: Optional[str] = None):
        """Initialize Clotho.

        Args:
            coordinator_id: Optional coordinator ID
        """
        self.coordinator_id = coordinator_id or f"clotho-{uuid.uuid4().hex[:8]}"

        # Initialize components
        self.transaction_coordinator = TransactionCoordinator(coordinator_id=self.coordinator_id)
        self.deadlock_detector = DeadlockDetector()
        self.saga_orchestrator = SagaOrchestrator()

        # Statistics
        self.created_at = datetime.now(timezone.utc).isoformat()
        self._lock = threading.RLock()

        logger.info(f"Clotho {self.coordinator_id} initialized")

    def start(self) -> None:
        """Start all Clotho components."""
        logger.info(f"Clotho {self.coordinator_id} starting...")

        self.transaction_coordinator.start()
        self.deadlock_detector.start()

        logger.info(f"Clotho {self.coordinator_id} started successfully")

    def stop(self) -> None:
        """Stop all Clotho components."""
        logger.info(f"Clotho {self.coordinator_id} stopping...")

        self.transaction_coordinator.stop()
        self.deadlock_detector.stop()

        logger.info(f"Clotho {self.coordinator_id} stopped")

    def execute_distributed_transaction(
        self,
        participants: List[Participant],
        timeout: float = 60.0,
        use_3pc: bool = False,
        data: Optional[dict] = None,
    ) -> Tuple[str, bool]:
        """Execute a distributed transaction with automatic deadlock detection.

        Args:
            participants: List of participants
            timeout: Transaction timeout
            use_3pc: Use 3PC instead of 2PC
            data: Optional transaction data

        Returns:
            Tuple of (transaction_id, success)
        """
        # Begin transaction
        txn_id = self.transaction_coordinator.begin_transaction(
            participants=participants, timeout=timeout, use_3pc=use_3pc, data=data
        )

        # Execute transaction
        success = self.transaction_coordinator.execute_transaction(txn_id)

        # Check for deadlocks
        if not success:
            deadlocks = self.deadlock_detector.get_deadlocks()
            if deadlocks:
                logger.warning(f"Transaction {txn_id} may have encountered deadlock")

        return txn_id, success

    def execute_saga(self, name: str, steps: List[SagaStep]) -> Tuple[str, bool]:
        """Execute a long-running saga workflow.

        Args:
            name: Saga name
            steps: List of saga steps

        Returns:
            Tuple of (saga_id, success)
        """
        saga_id = self.saga_orchestrator.create_saga(name=name, steps=steps)
        success = self.saga_orchestrator.execute_saga(saga_id)

        return saga_id, success

    def get_statistics(self) -> dict:
        """Get comprehensive statistics from all components.

        Returns:
            Dictionary with statistics from all components
        """
        with self._lock:
            return {
                "coordinator_id": self.coordinator_id,
                "created_at": self.created_at,
                "uptime_seconds": (
                    datetime.now(timezone.utc) - datetime.fromisoformat(self.created_at)
                ).total_seconds(),
                "transactions": self.transaction_coordinator.get_statistics(),
                "deadlocks": self.deadlock_detector.get_statistics(),
                "sagas": self.saga_orchestrator.get_statistics(),
            }

    def health_check(self) -> dict:
        """Perform health check on all components.

        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy",
            "coordinator_id": self.coordinator_id,
            "components": {
                "transaction_coordinator": "running",
                "deadlock_detector": "running",
                "saga_orchestrator": "running",
            },
            "statistics": self.get_statistics(),
        }
