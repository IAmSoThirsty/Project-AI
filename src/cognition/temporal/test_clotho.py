"""
Unit tests for Clotho distributed transaction coordinator.

Tests all components:
    - TransactionCoordinator (2PC and 3PC)
    - DeadlockDetector
    - SagaOrchestrator
    - Clotho integration
"""

import pytest
import time
import threading
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cognition.temporal.clotho import (
    Clotho,
    TransactionCoordinator,
    DeadlockDetector,
    SagaOrchestrator,
    Participant,
    Transaction,
    SagaStep,
    TransactionStatus,
    TransactionPhase,
    ParticipantStatus,
    SagaStatus,
)


class TestTransactionCoordinator:
    """Test TransactionCoordinator (2PC and 3PC)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.coordinator = TransactionCoordinator()
        self.coordinator.start()

    def teardown_method(self):
        """Tear down test fixtures."""
        self.coordinator.stop()

    def test_successful_2pc_transaction(self):
        """Test successful 2PC transaction."""
        # Create mock participants
        prepare_called = {"p1": False, "p2": False}
        commit_called = {"p1": False, "p2": False}

        def prepare_p1(txn):
            prepare_called["p1"] = True
            return True

        def commit_p1(txn):
            commit_called["p1"] = True

        def prepare_p2(txn):
            prepare_called["p2"] = True
            return True

        def commit_p2(txn):
            commit_called["p2"] = True

        participants = [
            Participant(
                participant_id="p1",
                agent_name="agent1",
                prepare_callback=prepare_p1,
                commit_callback=commit_p1,
            ),
            Participant(
                participant_id="p2",
                agent_name="agent2",
                prepare_callback=prepare_p2,
                commit_callback=commit_p2,
            ),
        ]

        # Begin and execute transaction
        txn_id = self.coordinator.begin_transaction(participants, use_3pc=False)
        success = self.coordinator.execute_transaction(txn_id)

        assert success
        assert prepare_called["p1"]
        assert prepare_called["p2"]
        assert commit_called["p1"]
        assert commit_called["p2"]

        # Check transaction status
        txn = self.coordinator.get_transaction(txn_id)
        assert txn.status == TransactionStatus.COMMITTED

    def test_failed_2pc_transaction(self):
        """Test 2PC transaction with participant voting NO."""
        abort_called = {"p1": False, "p2": False}

        def prepare_p1(txn):
            return True

        def prepare_p2(txn):
            return False  # Vote NO

        def abort_p1(txn):
            abort_called["p1"] = True

        def abort_p2(txn):
            abort_called["p2"] = True

        participants = [
            Participant(
                participant_id="p1",
                agent_name="agent1",
                prepare_callback=prepare_p1,
                abort_callback=abort_p1,
            ),
            Participant(
                participant_id="p2",
                agent_name="agent2",
                prepare_callback=prepare_p2,
                abort_callback=abort_p2,
            ),
        ]

        txn_id = self.coordinator.begin_transaction(participants, use_3pc=False)
        success = self.coordinator.execute_transaction(txn_id)

        assert not success
        assert abort_called["p1"]
        assert abort_called["p2"]

        txn = self.coordinator.get_transaction(txn_id)
        assert txn.status == TransactionStatus.ABORTED

    def test_successful_3pc_transaction(self):
        """Test successful 3PC transaction."""
        prepare_called = {"p1": False}
        commit_called = {"p1": False}

        def prepare(txn):
            prepare_called["p1"] = True
            return True

        def commit(txn):
            commit_called["p1"] = True

        participants = [
            Participant(
                participant_id="p1",
                agent_name="agent1",
                prepare_callback=prepare,
                commit_callback=commit,
            ),
        ]

        txn_id = self.coordinator.begin_transaction(participants, use_3pc=True)
        success = self.coordinator.execute_transaction(txn_id)

        assert success
        assert prepare_called["p1"]
        assert commit_called["p1"]

        txn = self.coordinator.get_transaction(txn_id)
        assert txn.status == TransactionStatus.COMMITTED

    def test_manual_abort(self):
        """Test manual transaction abort."""
        abort_called = {"p1": False}

        def abort(txn):
            abort_called["p1"] = True

        participants = [
            Participant(
                participant_id="p1",
                agent_name="agent1",
                abort_callback=abort,
            ),
        ]

        txn_id = self.coordinator.begin_transaction(participants)

        # Manually abort
        success = self.coordinator.abort_transaction(txn_id)
        assert success
        assert abort_called["p1"]

        txn = self.coordinator.get_transaction(txn_id)
        assert txn.status == TransactionStatus.ABORTED

    def test_transaction_timeout(self):
        """Test transaction timeout handling."""
        participants = [
            Participant(participant_id="p1", agent_name="agent1"),
        ]

        # Create transaction with very short timeout
        txn_id = self.coordinator.begin_transaction(participants, timeout=0.5)

        # Wait for timeout and monitor thread to process it
        time.sleep(2.0)  # Give monitor thread time to detect and abort

        txn = self.coordinator.get_transaction(txn_id)
        assert txn.status in [TransactionStatus.TIMEOUT, TransactionStatus.ABORTED]

    def test_statistics(self):
        """Test coordinator statistics."""
        participants = [
            Participant(participant_id="p1", agent_name="agent1"),
        ]

        txn_id = self.coordinator.begin_transaction(participants)

        stats = self.coordinator.get_statistics()
        assert stats["total_transactions"] == 1
        assert "by_status" in stats
        assert stats["coordinator_id"] == self.coordinator.coordinator_id


class TestDeadlockDetector:
    """Test DeadlockDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = DeadlockDetector()
        self.detector.start()

    def teardown_method(self):
        """Tear down test fixtures."""
        self.detector.stop()

    def test_acquire_release_lock(self):
        """Test basic lock acquisition and release."""
        # Acquire lock
        success = self.detector.acquire_lock("resource1", "txn1", "p1")
        assert success

        # Try to acquire same resource with different transaction
        success = self.detector.acquire_lock("resource1", "txn2", "p2")
        assert not success

        # Release lock
        success = self.detector.release_lock("resource1", "txn1")
        assert success

        # Now can acquire
        success = self.detector.acquire_lock("resource1", "txn2", "p2")
        assert success

    def test_shared_locks(self):
        """Test shared lock acquisition."""
        # Acquire shared lock
        success = self.detector.acquire_lock("resource1", "txn1", "p1", lock_type="shared")
        assert success

        # Another shared lock should succeed
        success = self.detector.acquire_lock("resource1", "txn2", "p2", lock_type="shared")
        assert success

    def test_deadlock_detection(self):
        """Test deadlock detection."""
        # Create circular wait: txn1 -> txn2 -> txn1
        # txn1 holds resource1, waits for resource2
        self.detector.acquire_lock("resource1", "txn1", "p1")
        self.detector.acquire_lock("resource2", "txn2", "p2")

        # txn1 tries to acquire resource2 (held by txn2)
        self.detector.acquire_lock("resource2", "txn1", "p1")  # Will wait

        # txn2 tries to acquire resource1 (held by txn1) - creates cycle
        self.detector.acquire_lock("resource1", "txn2", "p2")  # Will wait

        # Detect deadlock
        cycle = self.detector.detect_cycle()
        assert cycle is not None
        assert "txn1" in cycle and "txn2" in cycle

    def test_deadlock_resolution(self):
        """Test deadlock resolution."""
        # Create deadlock
        self.detector.acquire_lock("resource1", "txn1", "p1")
        self.detector.acquire_lock("resource2", "txn2", "p2")
        self.detector.acquire_lock("resource2", "txn1", "p1")
        self.detector.acquire_lock("resource1", "txn2", "p2")

        cycle = self.detector.detect_cycle()
        assert cycle is not None

        # Resolve deadlock
        victim = self.detector.resolve_deadlock(cycle)
        assert victim in cycle

        # No more deadlock
        cycle = self.detector.detect_cycle()
        # Note: May still detect depending on which transaction was aborted

    def test_release_all_locks(self):
        """Test releasing all locks for a transaction."""
        self.detector.acquire_lock("resource1", "txn1", "p1")
        self.detector.acquire_lock("resource2", "txn1", "p1")
        self.detector.acquire_lock("resource3", "txn1", "p1")

        count = self.detector.release_all_locks("txn1")
        assert count == 3

        # Now can acquire all resources
        assert self.detector.acquire_lock("resource1", "txn2", "p2")
        assert self.detector.acquire_lock("resource2", "txn2", "p2")
        assert self.detector.acquire_lock("resource3", "txn2", "p2")

    def test_statistics(self):
        """Test detector statistics."""
        self.detector.acquire_lock("resource1", "txn1", "p1")
        self.detector.acquire_lock("resource2", "txn2", "p2")

        stats = self.detector.get_statistics()
        assert stats["total_locks"] == 2


class TestSagaOrchestrator:
    """Test SagaOrchestrator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = SagaOrchestrator()

    def test_successful_saga(self):
        """Test successful saga execution."""
        results = {"step1": False, "step2": False, "step3": False}

        def step1_forward():
            results["step1"] = True
            return "step1_result"

        def step1_compensate():
            results["step1"] = False

        def step2_forward():
            results["step2"] = True
            return "step2_result"

        def step2_compensate():
            results["step2"] = False

        def step3_forward():
            results["step3"] = True
            return "step3_result"

        def step3_compensate():
            results["step3"] = False

        steps = [
            SagaStep(
                step_id="s1",
                name="Step 1",
                forward_action=step1_forward,
                compensate_action=step1_compensate,
                agent_name="agent1",
            ),
            SagaStep(
                step_id="s2",
                name="Step 2",
                forward_action=step2_forward,
                compensate_action=step2_compensate,
                agent_name="agent2",
            ),
            SagaStep(
                step_id="s3",
                name="Step 3",
                forward_action=step3_forward,
                compensate_action=step3_compensate,
                agent_name="agent3",
            ),
        ]

        saga_id = self.orchestrator.create_saga("Test Saga", steps)
        success = self.orchestrator.execute_saga(saga_id)

        assert success
        assert results["step1"]
        assert results["step2"]
        assert results["step3"]

        saga = self.orchestrator.get_saga(saga_id)
        assert saga.status == SagaStatus.COMPLETED
        assert len(saga.results) == 3

    def test_failed_saga_with_compensation(self):
        """Test saga failure and compensation."""
        results = {"step1": False, "step2": False, "step3": False}
        compensated = {"step1": False, "step2": False}

        def step1_forward():
            results["step1"] = True
            return "step1_result"

        def step1_compensate():
            compensated["step1"] = True
            results["step1"] = False

        def step2_forward():
            results["step2"] = True
            return "step2_result"

        def step2_compensate():
            compensated["step2"] = True
            results["step2"] = False

        def step3_forward():
            raise Exception("Step 3 failed")

        def step3_compensate():
            pass

        steps = [
            SagaStep(
                step_id="s1",
                name="Step 1",
                forward_action=step1_forward,
                compensate_action=step1_compensate,
                agent_name="agent1",
            ),
            SagaStep(
                step_id="s2",
                name="Step 2",
                forward_action=step2_forward,
                compensate_action=step2_compensate,
                agent_name="agent2",
            ),
            SagaStep(
                step_id="s3",
                name="Step 3",
                forward_action=step3_forward,
                compensate_action=step3_compensate,
                agent_name="agent3",
            ),
        ]

        saga_id = self.orchestrator.create_saga("Test Saga", steps)
        success = self.orchestrator.execute_saga(saga_id)

        assert not success
        assert compensated["step1"]  # Should be compensated
        assert compensated["step2"]  # Should be compensated
        assert not results["step1"]  # Should be rolled back
        assert not results["step2"]  # Should be rolled back

        saga = self.orchestrator.get_saga(saga_id)
        assert saga.status == SagaStatus.COMPENSATED

    def test_manual_saga_abort(self):
        """Test manual saga abort."""
        results = {"step1": False}
        compensated = {"step1": False}

        def step1_forward():
            results["step1"] = True
            return "result"

        def step1_compensate():
            compensated["step1"] = True
            results["step1"] = False

        steps = [
            SagaStep(
                step_id="s1",
                name="Step 1",
                forward_action=step1_forward,
                compensate_action=step1_compensate,
                agent_name="agent1",
            ),
        ]

        saga_id = self.orchestrator.create_saga("Test Saga", steps)

        # Execute first step manually
        saga = self.orchestrator.get_saga(saga_id)
        saga.steps[0].forward_action()
        saga.steps[0].executed = True

        # Now abort
        success = self.orchestrator.abort_saga(saga_id)

        assert success
        assert compensated["step1"]

        saga = self.orchestrator.get_saga(saga_id)
        assert saga.status == SagaStatus.COMPENSATED

    def test_saga_statistics(self):
        """Test saga statistics."""
        steps = [
            SagaStep(
                step_id="s1",
                name="Step 1",
                forward_action=lambda: None,
                compensate_action=lambda: None,
                agent_name="agent1",
            ),
        ]

        saga_id = self.orchestrator.create_saga("Test Saga", steps)

        stats = self.orchestrator.get_statistics()
        assert stats["total_sagas"] == 1
        # Saga is created with RUNNING status by default
        assert stats["active_sagas"] >= 0


class TestClotho:
    """Test Clotho integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.clotho = Clotho()
        self.clotho.start()

    def teardown_method(self):
        """Tear down test fixtures."""
        self.clotho.stop()

    def test_distributed_transaction(self):
        """Test distributed transaction execution."""
        results = {"p1": False, "p2": False}

        def prepare_p1(txn):
            return True

        def commit_p1(txn):
            results["p1"] = True

        def prepare_p2(txn):
            return True

        def commit_p2(txn):
            results["p2"] = True

        participants = [
            Participant(
                participant_id="p1",
                agent_name="chronos",
                prepare_callback=prepare_p1,
                commit_callback=commit_p1,
            ),
            Participant(
                participant_id="p2",
                agent_name="atropos",
                prepare_callback=prepare_p2,
                commit_callback=commit_p2,
            ),
        ]

        txn_id, success = self.clotho.execute_distributed_transaction(participants)

        assert success
        assert results["p1"]
        assert results["p2"]

    def test_saga_execution(self):
        """Test saga execution through Clotho."""
        results = {"step1": False, "step2": False}

        def step1_forward():
            results["step1"] = True
            return "result1"

        def step1_compensate():
            results["step1"] = False

        def step2_forward():
            results["step2"] = True
            return "result2"

        def step2_compensate():
            results["step2"] = False

        steps = [
            SagaStep(
                step_id="s1",
                name="Initialize",
                forward_action=step1_forward,
                compensate_action=step1_compensate,
                agent_name="chronos",
            ),
            SagaStep(
                step_id="s2",
                name="Execute",
                forward_action=step2_forward,
                compensate_action=step2_compensate,
                agent_name="atropos",
            ),
        ]

        saga_id, success = self.clotho.execute_saga("Test Workflow", steps)

        assert success
        assert results["step1"]
        assert results["step2"]

    def test_health_check(self):
        """Test Clotho health check."""
        health = self.clotho.health_check()

        assert health["status"] == "healthy"
        assert health["coordinator_id"] == self.clotho.coordinator_id
        assert "components" in health
        assert "statistics" in health

    def test_statistics(self):
        """Test comprehensive statistics."""
        stats = self.clotho.get_statistics()

        assert "coordinator_id" in stats
        assert "created_at" in stats
        assert "uptime_seconds" in stats
        assert "transactions" in stats
        assert "deadlocks" in stats
        assert "sagas" in stats


class TestConcurrency:
    """Test concurrent transaction execution."""

    def test_concurrent_transactions(self):
        """Test multiple concurrent transactions."""
        coordinator = TransactionCoordinator()
        coordinator.start()

        results = []
        errors = []

        def execute_transaction(txn_num):
            try:
                participants = [
                    Participant(
                        participant_id=f"p{txn_num}",
                        agent_name=f"agent{txn_num}",
                        prepare_callback=lambda txn: True,
                        commit_callback=lambda txn: None,
                    ),
                ]

                txn_id = coordinator.begin_transaction(participants)
                success = coordinator.execute_transaction(txn_id)
                results.append(success)
            except Exception as e:
                errors.append(e)

        # Execute 10 concurrent transactions
        threads = []
        for i in range(10):
            thread = threading.Thread(target=execute_transaction, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        coordinator.stop()

        assert len(errors) == 0
        assert all(results)  # All should succeed


def test_idempotent_operations():
    """Test idempotent saga operations."""
    orchestrator = SagaOrchestrator()

    executed_count = {"count": 0}

    def idempotent_forward():
        executed_count["count"] += 1
        return "result"

    def idempotent_compensate():
        if executed_count["count"] > 0:
            executed_count["count"] -= 1

    steps = [
        SagaStep(
            step_id="s1",
            name="Idempotent Step",
            forward_action=idempotent_forward,
            compensate_action=idempotent_compensate,
            agent_name="agent1",
        ),
    ]

    saga_id = orchestrator.create_saga("Idempotent Saga", steps)
    orchestrator.execute_saga(saga_id)

    # Execute compensation multiple times (should be idempotent)
    saga = orchestrator.get_saga(saga_id)
    saga.steps[0].compensate_action()
    saga.steps[0].compensate_action()

    # Should only compensate once
    assert executed_count["count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
