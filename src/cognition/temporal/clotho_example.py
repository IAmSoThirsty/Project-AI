"""
Example: Multi-Agent Distributed Transaction with Clotho

This example demonstrates how Clotho coordinates distributed transactions
across Chronos, Atropos, and other temporal agents.

Scenarios:
    1. Distributed state mutation across multiple agents
    2. Saga-based workflow orchestration
    3. Deadlock detection and resolution
    4. Multi-phase commit with rollback
"""

import logging
import time
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cognition.temporal.clotho import (
    Clotho,
    Participant,
    SagaStep,
    TransactionStatus,
    SagaStatus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Mock temporal agents for demonstration
class ChronosAgent:
    """Mock Chronos agent for temporal weight management."""

    def __init__(self):
        self.state = {"temporal_weight": 0}
        self._lock_state = {}

    def prepare_update(self, transaction) -> bool:
        """Prepare to update temporal weight."""
        logger.info("Chronos: Preparing to update temporal weight")
        # Simulate validation
        new_weight = transaction.data.get("chronos_weight", 0)
        if new_weight < 0:
            logger.warning("Chronos: Invalid weight, voting NO")
            return False
        # Lock state for transaction
        self._lock_state[transaction.transaction_id] = self.state.copy()
        logger.info("Chronos: Ready to commit, voting YES")
        return True

    def commit_update(self, transaction) -> None:
        """Commit temporal weight update."""
        new_weight = transaction.data.get("chronos_weight", 0)
        self.state["temporal_weight"] = new_weight
        logger.info(f"Chronos: Committed temporal weight = {new_weight}")
        # Release lock
        if transaction.transaction_id in self._lock_state:
            del self._lock_state[transaction.transaction_id]

    def abort_update(self, transaction) -> None:
        """Abort temporal weight update."""
        logger.info("Chronos: Aborted update, rolling back")
        # Restore state
        if transaction.transaction_id in self._lock_state:
            self.state = self._lock_state[transaction.transaction_id]
            del self._lock_state[transaction.transaction_id]


class AtroposAgent:
    """Mock Atropos agent for fate determination."""

    def __init__(self):
        self.state = {"fate_chain": []}
        self._lock_state = {}

    def prepare_record(self, transaction) -> bool:
        """Prepare to record fate."""
        logger.info("Atropos: Preparing to record fate event")
        # Simulate validation
        event = transaction.data.get("atropos_event")
        if not event:
            logger.warning("Atropos: No event to record, voting NO")
            return False
        # Lock state
        self._lock_state[transaction.transaction_id] = self.state.copy()
        logger.info("Atropos: Ready to commit, voting YES")
        return True

    def commit_record(self, transaction) -> None:
        """Commit fate event to chain."""
        event = transaction.data.get("atropos_event")
        self.state["fate_chain"].append(event)
        logger.info(f"Atropos: Committed fate event: {event}")
        # Release lock
        if transaction.transaction_id in self._lock_state:
            del self._lock_state[transaction.transaction_id]

    def abort_record(self, transaction) -> None:
        """Abort fate recording."""
        logger.info("Atropos: Aborted recording, rolling back")
        # Restore state
        if transaction.transaction_id in self._lock_state:
            self.state = self._lock_state[transaction.transaction_id]
            del self._lock_state[transaction.transaction_id]


class LachesisAgent:
    """Mock Lachesis agent for measuring the thread of life."""

    def __init__(self):
        self.state = {"life_span": 100}

    def measure_thread(self) -> int:
        """Measure current life span."""
        return self.state["life_span"]

    def adjust_span(self, delta: int) -> None:
        """Adjust life span."""
        self.state["life_span"] += delta
        logger.info(f"Lachesis: Adjusted life span by {delta} -> {self.state['life_span']}")

    def restore_span(self, value: int) -> None:
        """Restore life span to previous value."""
        self.state["life_span"] = value
        logger.info(f"Lachesis: Restored life span to {value}")


def example_1_successful_2pc_transaction():
    """Example 1: Successful 2PC transaction across Chronos and Atropos."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Successful 2PC Transaction")
    print("=" * 80 + "\n")

    # Initialize Clotho and agents
    clotho = Clotho(coordinator_id="clotho-main")
    clotho.start()

    chronos = ChronosAgent()
    atropos = AtroposAgent()

    # Create participants
    participants = [
        Participant(
            participant_id="chronos-1",
            agent_name="chronos",
            prepare_callback=chronos.prepare_update,
            commit_callback=chronos.commit_update,
            abort_callback=chronos.abort_update,
        ),
        Participant(
            participant_id="atropos-1",
            agent_name="atropos",
            prepare_callback=atropos.prepare_record,
            commit_callback=atropos.commit_record,
            abort_callback=atropos.abort_record,
        ),
    ]

    # Transaction data
    transaction_data = {
        "chronos_weight": 42,
        "atropos_event": "temporal_sync_initiated",
    }

    # Execute distributed transaction
    logger.info("Starting distributed transaction...")
    txn_id, success = clotho.execute_distributed_transaction(
        participants=participants, use_3pc=False, data=transaction_data
    )

    # Check results
    if success:
        print(f"\n[OK] Transaction {txn_id} committed successfully!")
        print(f"  Chronos state: {chronos.state}")
        print(f"  Atropos state: {atropos.state}")
    else:
        print(f"\n[FAIL] Transaction {txn_id} failed")

    clotho.stop()


def example_2_failed_transaction_with_rollback():
    """Example 2: Failed transaction with automatic rollback."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Failed Transaction with Rollback")
    print("=" * 80 + "\n")

    clotho = Clotho()
    clotho.start()

    chronos = ChronosAgent()
    atropos = AtroposAgent()

    # Set initial state
    chronos.state["temporal_weight"] = 10
    atropos.state["fate_chain"] = ["event1", "event2"]

    print("Initial state:")
    print(f"  Chronos: {chronos.state}")
    print(f"  Atropos: {atropos.state}")

    participants = [
        Participant(
            participant_id="chronos-2",
            agent_name="chronos",
            prepare_callback=chronos.prepare_update,
            commit_callback=chronos.commit_update,
            abort_callback=chronos.abort_update,
        ),
        Participant(
            participant_id="atropos-2",
            agent_name="atropos",
            prepare_callback=atropos.prepare_record,
            commit_callback=atropos.commit_record,
            abort_callback=atropos.abort_record,
        ),
    ]

    # Invalid transaction data (negative weight)
    transaction_data = {
        "chronos_weight": -5,  # Invalid!
        "atropos_event": "invalid_event",
    }

    logger.info("Starting transaction with invalid data...")
    txn_id, success = clotho.execute_distributed_transaction(
        participants=participants, data=transaction_data
    )

    print(f"\n{'[OK]' if success else '[FAIL]'} Transaction {txn_id} {'committed' if success else 'aborted'}")
    print("State after rollback:")
    print(f"  Chronos: {chronos.state}")
    print(f"  Atropos: {atropos.state}")
    print("  State unchanged due to rollback [OK]")

    clotho.stop()


def example_3_saga_workflow():
    """Example 3: Long-running saga workflow with compensation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Saga Workflow with Compensation")
    print("=" * 80 + "\n")

    clotho = Clotho()
    clotho.start()

    chronos = ChronosAgent()
    atropos = AtroposAgent()
    lachesis = LachesisAgent()

    print("Initial states:")
    print(f"  Chronos: {chronos.state}")
    print(f"  Atropos: {atropos.state}")
    print(f"  Lachesis: {lachesis.state}")

    # Define saga steps with forward and compensating actions
    original_span = lachesis.state["life_span"]

    def step1_initialize():
        """Initialize temporal weight."""
        chronos.state["temporal_weight"] = 100
        logger.info("Step 1: Initialized Chronos temporal weight")
        return {"chronos_weight": 100}

    def step1_compensate():
        """Compensate: reset temporal weight."""
        chronos.state["temporal_weight"] = 0
        logger.info("Step 1 Compensation: Reset Chronos temporal weight")

    def step2_record_fate():
        """Record fate event."""
        event = "saga_workflow_started"
        atropos.state["fate_chain"].append(event)
        logger.info(f"Step 2: Recorded fate event: {event}")
        return {"event": event}

    def step2_compensate():
        """Compensate: remove fate event."""
        if atropos.state["fate_chain"]:
            removed = atropos.state["fate_chain"].pop()
            logger.info(f"Step 2 Compensation: Removed fate event: {removed}")

    def step3_adjust_lifespan():
        """Adjust life span - THIS WILL FAIL."""
        logger.info("Step 3: Attempting to adjust life span...")
        raise Exception("Lachesis thread measurement failed!")

    def step3_compensate():
        """Compensate: restore life span."""
        lachesis.restore_span(original_span)
        logger.info("Step 3 Compensation: Restored life span")

    steps = [
        SagaStep(
            step_id="init",
            name="Initialize Chronos",
            forward_action=step1_initialize,
            compensate_action=step1_compensate,
            agent_name="chronos",
        ),
        SagaStep(
            step_id="record",
            name="Record Fate",
            forward_action=step2_record_fate,
            compensate_action=step2_compensate,
            agent_name="atropos",
        ),
        SagaStep(
            step_id="adjust",
            name="Adjust Lifespan",
            forward_action=step3_adjust_lifespan,
            compensate_action=step3_compensate,
            agent_name="lachesis",
        ),
    ]

    logger.info("Starting saga workflow...")
    saga_id, success = clotho.execute_saga("Multi-Agent Workflow", steps)

    print(f"\n{'[OK]' if success else '[FAIL]'} Saga {saga_id} {'completed' if success else 'compensated'}")
    print("Final states after compensation:")
    print(f"  Chronos: {chronos.state}")
    print(f"  Atropos: {atropos.state}")
    print(f"  Lachesis: {lachesis.state}")
    print("  All steps compensated successfully [OK]")

    clotho.stop()


def example_4_3pc_transaction():
    """Example 4: 3PC transaction with pre-commit phase."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Three-Phase Commit (3PC)")
    print("=" * 80 + "\n")

    clotho = Clotho()
    clotho.start()

    chronos = ChronosAgent()
    atropos = AtroposAgent()

    participants = [
        Participant(
            participant_id="chronos-3",
            agent_name="chronos",
            prepare_callback=chronos.prepare_update,
            commit_callback=chronos.commit_update,
            abort_callback=chronos.abort_update,
        ),
        Participant(
            participant_id="atropos-3",
            agent_name="atropos",
            prepare_callback=atropos.prepare_record,
            commit_callback=atropos.commit_record,
            abort_callback=atropos.abort_record,
        ),
    ]

    transaction_data = {
        "chronos_weight": 999,
        "atropos_event": "3pc_transaction_executed",
    }

    logger.info("Starting 3PC transaction...")
    txn_id, success = clotho.execute_distributed_transaction(
        participants=participants, use_3pc=True, data=transaction_data  # Use 3PC
    )

    if success:
        print(f"\n[OK] 3PC Transaction {txn_id} committed!")
        print("  3PC adds pre-commit phase to reduce uncertainty window")
        print(f"  Chronos: {chronos.state}")
        print(f"  Atropos: {atropos.state}")

    clotho.stop()


def example_5_deadlock_detection():
    """Example 5: Deadlock detection and resolution."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Deadlock Detection")
    print("=" * 80 + "\n")

    clotho = Clotho()
    clotho.start()

    detector = clotho.deadlock_detector

    # Simulate deadlock scenario
    logger.info("Simulating deadlock scenario...")

    # Transaction 1 holds resource A, wants resource B
    detector.acquire_lock("resource_a", "txn1", "p1")
    logger.info("txn1 acquired resource_a")

    # Transaction 2 holds resource B, wants resource A
    detector.acquire_lock("resource_b", "txn2", "p2")
    logger.info("txn2 acquired resource_b")

    # Create circular wait
    detector.acquire_lock("resource_b", "txn1", "p1")  # txn1 waits for txn2
    logger.info("txn1 waiting for resource_b (held by txn2)")

    detector.acquire_lock("resource_a", "txn2", "p2")  # txn2 waits for txn1
    logger.info("txn2 waiting for resource_a (held by txn1)")

    # Detect deadlock
    cycle = detector.detect_cycle()

    if cycle:
        print(f"\n[WARN] Deadlock detected!")
        print(f"  Cycle: {' -> '.join(cycle)}")

        # Resolve deadlock
        victim = detector.resolve_deadlock(cycle)
        print(f"  Resolved by aborting victim: {victim}")

        # Verify resolution
        cycle_after = detector.detect_cycle()
        print(f"  Deadlock resolved: {cycle_after is None}")

    clotho.stop()


def example_6_statistics_and_monitoring():
    """Example 6: Statistics and monitoring."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Statistics and Monitoring")
    print("=" * 80 + "\n")

    clotho = Clotho()
    clotho.start()

    # Execute some transactions and sagas
    chronos = ChronosAgent()
    participants = [
        Participant(
            participant_id="p1",
            agent_name="chronos",
            prepare_callback=chronos.prepare_update,
            commit_callback=chronos.commit_update,
        ),
    ]

    # Execute multiple transactions
    for i in range(5):
        txn_id, success = clotho.execute_distributed_transaction(
            participants=participants, data={"chronos_weight": i * 10}
        )
        logger.info(f"Transaction {i+1}: {txn_id} - {'success' if success else 'failed'}")

    # Execute a saga
    steps = [
        SagaStep(
            step_id="s1",
            name="Test Step",
            forward_action=lambda: "result",
            compensate_action=lambda: None,
            agent_name="test",
        ),
    ]
    saga_id, success = clotho.execute_saga("Test Saga", steps)

    # Get statistics
    stats = clotho.get_statistics()

    print("\nClotho Statistics:")
    print(f"  Coordinator ID: {stats['coordinator_id']}")
    print(f"  Uptime: {stats['uptime_seconds']:.2f} seconds")
    print(f"\n  Transactions:")
    print(f"    Total: {stats['transactions']['total_transactions']}")
    print(f"    By Status: {stats['transactions']['by_status']}")
    print(f"\n  Sagas:")
    print(f"    Total: {stats['sagas']['total_sagas']}")
    print(f"    By Status: {stats['sagas']['by_status']}")
    print(f"\n  Deadlocks:")
    print(f"    Total Locks: {stats['deadlocks']['total_locks']}")

    # Health check
    health = clotho.health_check()
    print(f"\nHealth Status: {health['status']}")
    print(f"Components: {health['components']}")

    clotho.stop()


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("CLOTHO DISTRIBUTED COORDINATION EXAMPLES")
    print("Thread-Spinner of the Fates")
    print("=" * 80)

    try:
        example_1_successful_2pc_transaction()
        time.sleep(0.5)

        example_2_failed_transaction_with_rollback()
        time.sleep(0.5)

        example_3_saga_workflow()
        time.sleep(0.5)

        example_4_3pc_transaction()
        time.sleep(0.5)

        example_5_deadlock_detection()
        time.sleep(0.5)

        example_6_statistics_and_monitoring()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
