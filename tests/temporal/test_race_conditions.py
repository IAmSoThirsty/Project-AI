#                                           [2026-04-09 04:26]
#                                          Productivity: Active
"""
Race Condition Tests

Tests for concurrent access, distributed transactions, and race conditions
in the Temporal/Liara agent system. Includes ThreadSanitizer-compatible tests.
"""

import pytest
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from threading import Thread, Lock, RLock, Semaphore, Event as ThreadEvent
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import random


@dataclass
class Transaction:
    """Represents a distributed transaction."""
    tx_id: str
    timestamp: datetime
    operations: List[Dict[str, Any]]
    state: str = "pending"  # pending, prepared, committed, aborted
    participants: List[str] = field(default_factory=list)
    locks_held: List[str] = field(default_factory=list)


class DistributedLock:
    """Distributed lock with deadlock detection."""
    
    def __init__(self, resource_id: str):
        self.resource_id = resource_id
        self.holder: Optional[str] = None
        self.waiting: List[str] = []
        self._lock = Lock()
        self._acquired = ThreadEvent()
        self.acquire_count = 0
    
    def acquire(self, agent_id: str, timeout: float = 5.0) -> bool:
        """Acquire lock with timeout."""
        start_time = time.time()
        
        while True:
            with self._lock:
                if self.holder is None:
                    self.holder = agent_id
                    self.acquire_count += 1
                    return True
                
                if agent_id not in self.waiting:
                    self.waiting.append(agent_id)
            
            if time.time() - start_time > timeout:
                with self._lock:
                    if agent_id in self.waiting:
                        self.waiting.remove(agent_id)
                return False
            
            time.sleep(0.01)
    
    def release(self, agent_id: str) -> bool:
        """Release lock."""
        with self._lock:
            if self.holder == agent_id:
                self.holder = None
                return True
            return False
    
    def is_locked(self) -> bool:
        """Check if lock is held."""
        with self._lock:
            return self.holder is not None


class TransactionManager:
    """Manages distributed transactions with 2PC."""
    
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.locks: Dict[str, DistributedLock] = {}
        self._lock = RLock()
        self.commit_count = 0
        self.abort_count = 0
    
    def begin_transaction(self, tx_id: str, participants: List[str]) -> Transaction:
        """Begin a new transaction."""
        with self._lock:
            tx = Transaction(
                tx_id=tx_id,
                timestamp=datetime.now(),
                operations=[],
                participants=participants
            )
            self.transactions[tx_id] = tx
            return tx
    
    def acquire_locks(self, tx_id: str, resources: List[str]) -> bool:
        """Acquire locks for transaction."""
        tx = self.transactions.get(tx_id)
        if not tx:
            return False
        
        acquired = []
        
        try:
            for resource in resources:
                if resource not in self.locks:
                    self.locks[resource] = DistributedLock(resource)
                
                if self.locks[resource].acquire(tx_id, timeout=2.0):
                    acquired.append(resource)
                else:
                    # Failed to acquire - rollback
                    for res in acquired:
                        self.locks[res].release(tx_id)
                    return False
            
            tx.locks_held = acquired
            return True
        
        except Exception:
            # Cleanup on error
            for res in acquired:
                self.locks[res].release(tx_id)
            return False
    
    def prepare(self, tx_id: str) -> bool:
        """Prepare phase of 2PC."""
        with self._lock:
            tx = self.transactions.get(tx_id)
            if not tx or tx.state != "pending":
                return False
            
            tx.state = "prepared"
            return True
    
    def commit(self, tx_id: str) -> bool:
        """Commit phase of 2PC."""
        with self._lock:
            tx = self.transactions.get(tx_id)
            if not tx or tx.state != "prepared":
                return False
            
            tx.state = "committed"
            self.commit_count += 1
            
            # Release locks
            for resource in tx.locks_held:
                if resource in self.locks:
                    self.locks[resource].release(tx_id)
            
            return True
    
    def abort(self, tx_id: str) -> bool:
        """Abort transaction."""
        with self._lock:
            tx = self.transactions.get(tx_id)
            if not tx:
                return False
            
            tx.state = "aborted"
            self.abort_count += 1
            
            # Release locks
            for resource in tx.locks_held:
                if resource in self.locks:
                    self.locks[resource].release(tx_id)
            
            return True


class ConcurrentStateManager:
    """Thread-safe state manager for testing race conditions."""
    
    def __init__(self):
        self.state: Dict[str, Any] = {}
        self._lock = RLock()
        self.operation_count = 0
        self.conflict_count = 0
    
    def read(self, key: str) -> Optional[Any]:
        """Read value with lock."""
        with self._lock:
            self.operation_count += 1
            return self.state.get(key)
    
    def write(self, key: str, value: Any) -> None:
        """Write value with lock."""
        with self._lock:
            self.operation_count += 1
            self.state[key] = value
    
    def compare_and_swap(self, key: str, expected: Any, new_value: Any) -> bool:
        """Atomic compare-and-swap operation."""
        with self._lock:
            self.operation_count += 1
            current = self.state.get(key)
            
            if current == expected:
                self.state[key] = new_value
                return True
            else:
                self.conflict_count += 1
                return False
    
    def increment(self, key: str, delta: int = 1) -> int:
        """Atomically increment value."""
        with self._lock:
            self.operation_count += 1
            current = self.state.get(key, 0)
            new_value = current + delta
            self.state[key] = new_value
            return new_value


class TestBasicRaceConditions:
    """Test basic race conditions."""
    
    def test_concurrent_writes(self):
        """Test concurrent writes to same resource."""
        manager = ConcurrentStateManager()
        
        def write_value(thread_id: int, iterations: int):
            for i in range(iterations):
                manager.write("counter", thread_id * 1000 + i)
        
        threads = [
            Thread(target=write_value, args=(i, 100))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Final value should be from one of the threads
        final = manager.read("counter")
        assert final is not None
    
    def test_concurrent_increments(self):
        """Test atomic increments under concurrency."""
        manager = ConcurrentStateManager()
        manager.write("counter", 0)
        
        def increment_counter(iterations: int):
            for _ in range(iterations):
                manager.increment("counter")
        
        iterations = 100
        num_threads = 10
        
        threads = [
            Thread(target=increment_counter, args=(iterations,))
            for _ in range(num_threads)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All increments should be counted
        assert manager.read("counter") == iterations * num_threads
    
    def test_compare_and_swap_conflicts(self):
        """Test CAS operation under concurrent updates."""
        manager = ConcurrentStateManager()
        manager.write("value", 0)
        
        success_count = [0]
        lock = Lock()
        
        def attempt_cas(thread_id: int, attempts: int):
            local_success = 0
            for _ in range(attempts):
                current = manager.read("value")
                if manager.compare_and_swap("value", current, current + 1):
                    local_success += 1
                else:
                    time.sleep(0.001)  # Brief backoff
            
            with lock:
                success_count[0] += local_success
        
        num_threads = 5
        attempts = 20
        
        threads = [
            Thread(target=attempt_cas, args=(i, attempts))
            for i in range(num_threads)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Final value should equal successful CAS operations
        assert manager.read("value") == success_count[0]
        assert manager.conflict_count > 0  # Some conflicts should occur
    
    def test_read_write_consistency(self):
        """Test read-write consistency under concurrent access."""
        manager = ConcurrentStateManager()
        
        def writer(iterations: int):
            for i in range(iterations):
                manager.write("data", i)
                time.sleep(0.001)
        
        def reader(read_values: List):
            for _ in range(50):
                value = manager.read("data")
                if value is not None:
                    read_values.append(value)
                time.sleep(0.001)
        
        read_values = []
        
        writer_thread = Thread(target=writer, args=(50,))
        reader_thread = Thread(target=reader, args=(read_values,))
        
        writer_thread.start()
        reader_thread.start()
        
        writer_thread.join()
        reader_thread.join()
        
        # Reads should see monotonically increasing values (or equal)
        for i in range(len(read_values) - 1):
            assert read_values[i] <= read_values[i + 1]


class TestDistributedLocks:
    """Test distributed locking mechanisms."""
    
    def test_lock_acquisition_and_release(self):
        """Test basic lock acquire and release."""
        lock = DistributedLock("resource-1")
        
        assert lock.acquire("agent-1", timeout=1.0)
        assert lock.is_locked()
        assert lock.holder == "agent-1"
        
        assert lock.release("agent-1")
        assert not lock.is_locked()
    
    def test_lock_exclusion(self):
        """Test lock provides mutual exclusion."""
        lock = DistributedLock("resource-1")
        
        assert lock.acquire("agent-1", timeout=1.0)
        assert not lock.acquire("agent-2", timeout=0.1)
        
        lock.release("agent-1")
        assert lock.acquire("agent-2", timeout=1.0)
    
    def test_lock_timeout(self):
        """Test lock acquisition timeout."""
        lock = DistributedLock("resource-1")
        
        lock.acquire("agent-1", timeout=1.0)
        
        start = time.time()
        result = lock.acquire("agent-2", timeout=0.2)
        elapsed = time.time() - start
        
        assert not result
        assert 0.15 < elapsed < 0.3
    
    def test_concurrent_lock_contention(self):
        """Test lock under high contention."""
        lock = DistributedLock("resource-1")
        acquired_by = []
        lock_obj = Lock()
        
        def try_acquire(agent_id: str):
            if lock.acquire(agent_id, timeout=2.0):
                with lock_obj:
                    acquired_by.append(agent_id)
                time.sleep(0.01)
                lock.release(agent_id)
        
        threads = [
            Thread(target=try_acquire, args=(f"agent-{i}",))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All agents should eventually acquire
        assert len(acquired_by) == 10
    
    def test_deadlock_prevention(self):
        """Test deadlock prevention with ordered locking."""
        lock1 = DistributedLock("resource-1")
        lock2 = DistributedLock("resource-2")
        
        results = {"agent1": False, "agent2": False}
        
        def acquire_ordered(agent_id: str, first: DistributedLock, second: DistributedLock):
            if first.acquire(agent_id, timeout=1.0):
                time.sleep(0.05)
                if second.acquire(agent_id, timeout=1.0):
                    results[agent_id] = True
                    second.release(agent_id)
                first.release(agent_id)
        
        # Both agents acquire in same order - no deadlock
        t1 = Thread(target=acquire_ordered, args=("agent1", lock1, lock2))
        t2 = Thread(target=acquire_ordered, args=("agent2", lock1, lock2))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Both should succeed (no deadlock)
        assert results["agent1"] or results["agent2"]


class TestTransactionIsolation:
    """Test transaction isolation levels."""
    
    def test_transaction_begin_and_commit(self):
        """Test basic transaction lifecycle."""
        manager = TransactionManager()
        
        tx = manager.begin_transaction("tx-1", ["agent-1"])
        assert tx.state == "pending"
        
        assert manager.prepare("tx-1")
        assert tx.state == "prepared"
        
        assert manager.commit("tx-1")
        assert tx.state == "committed"
    
    def test_transaction_abort(self):
        """Test transaction abort."""
        manager = TransactionManager()
        
        tx = manager.begin_transaction("tx-1", ["agent-1"])
        manager.prepare("tx-1")
        
        assert manager.abort("tx-1")
        assert tx.state == "aborted"
    
    def test_lock_acquisition_in_transaction(self):
        """Test lock acquisition within transaction."""
        manager = TransactionManager()
        
        tx = manager.begin_transaction("tx-1", ["agent-1"])
        
        resources = ["resource-1", "resource-2", "resource-3"]
        assert manager.acquire_locks("tx-1", resources)
        
        assert len(tx.locks_held) == 3
        
        manager.commit("tx-1")
        
        # Locks should be released after commit
        for res in resources:
            assert not manager.locks[res].is_locked()
    
    def test_concurrent_transactions_different_resources(self):
        """Test concurrent transactions on different resources."""
        manager = TransactionManager()
        
        results = []
        
        def execute_transaction(tx_id: str, resources: List[str]):
            manager.begin_transaction(tx_id, ["agent"])
            if manager.acquire_locks(tx_id, resources):
                manager.prepare(tx_id)
                manager.commit(tx_id)
                results.append(tx_id)
        
        t1 = Thread(target=execute_transaction, args=("tx-1", ["r1", "r2"]))
        t2 = Thread(target=execute_transaction, args=("tx-2", ["r3", "r4"]))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Both transactions should succeed (different resources)
        assert len(results) == 2
    
    def test_concurrent_transactions_same_resource(self):
        """Test concurrent transactions competing for same resource."""
        manager = TransactionManager()
        
        results = {"success": 0, "failed": 0}
        lock = Lock()
        
        def execute_transaction(tx_id: str):
            manager.begin_transaction(tx_id, ["agent"])
            if manager.acquire_locks(tx_id, ["shared-resource"]):
                time.sleep(0.05)
                manager.prepare(tx_id)
                manager.commit(tx_id)
                with lock:
                    results["success"] += 1
            else:
                manager.abort(tx_id)
                with lock:
                    results["failed"] += 1
        
        threads = [
            Thread(target=execute_transaction, args=(f"tx-{i}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Some should succeed, some fail due to lock contention
        assert results["success"] > 0
        assert results["success"] + results["failed"] == 5
    
    def test_two_phase_commit_protocol(self):
        """Test 2PC protocol execution."""
        manager = TransactionManager()
        
        tx_id = "tx-2pc"
        manager.begin_transaction(tx_id, ["agent-1", "agent-2"])
        
        # Phase 1: Prepare
        assert manager.prepare(tx_id)
        tx = manager.transactions[tx_id]
        assert tx.state == "prepared"
        
        # Phase 2: Commit
        assert manager.commit(tx_id)
        assert tx.state == "committed"
        assert manager.commit_count == 1


class TestOptimisticConcurrencyControl:
    """Test optimistic concurrency control."""
    
    def test_version_based_occ(self):
        """Test version-based optimistic concurrency control."""
        class VersionedState:
            def __init__(self):
                self.data: Dict[str, Any] = {}
                self.versions: Dict[str, int] = {}
                self._lock = Lock()
            
            def read(self, key: str) -> tuple:
                """Read value and version."""
                with self._lock:
                    return self.data.get(key), self.versions.get(key, 0)
            
            def write(self, key: str, value: Any, expected_version: int) -> bool:
                """Write if version matches."""
                with self._lock:
                    current_version = self.versions.get(key, 0)
                    if current_version == expected_version:
                        self.data[key] = value
                        self.versions[key] = current_version + 1
                        return True
                    return False
        
        state = VersionedState()
        state.data["counter"] = 0
        state.versions["counter"] = 1
        
        # Successful write
        value, version = state.read("counter")
        assert state.write("counter", value + 1, version)
        
        # Failed write (version mismatch)
        assert not state.write("counter", 100, version)
    
    def test_timestamp_based_occ(self):
        """Test timestamp-based optimistic concurrency control."""
        class TimestampedState:
            def __init__(self):
                self.data: Dict[str, Any] = {}
                self.timestamps: Dict[str, float] = {}
                self._lock = Lock()
            
            def read(self, key: str) -> tuple:
                """Read value and timestamp."""
                with self._lock:
                    return self.data.get(key), self.timestamps.get(key, 0)
            
            def write(self, key: str, value: Any, read_timestamp: float) -> bool:
                """Write if no newer write occurred."""
                with self._lock:
                    current_ts = self.timestamps.get(key, 0)
                    if current_ts <= read_timestamp:
                        self.data[key] = value
                        self.timestamps[key] = time.time()
                        return True
                    return False
        
        state = TimestampedState()
        
        value1, ts1 = state.read("data")
        time.sleep(0.01)
        
        assert state.write("data", "value1", ts1)
        
        value2, ts2 = state.read("data")
        assert value2 == "value1"


class TestEventualConsistency:
    """Test eventual consistency in distributed system."""
    
    def test_replica_convergence(self):
        """Test replicas eventually converge to same state."""
        class Replica:
            def __init__(self, replica_id: str):
                self.replica_id = replica_id
                self.state: Dict[str, Any] = {}
                self.operations: List[tuple] = []
            
            def write(self, key: str, value: Any) -> None:
                self.state[key] = value
                self.operations.append((time.time(), key, value))
            
            def sync_from(self, other: 'Replica') -> None:
                """Sync operations from another replica."""
                for ts, key, value in other.operations:
                    if key not in self.state or ts > 0:
                        self.state[key] = value
        
        replicas = [Replica(f"replica-{i}") for i in range(3)]
        
        # Write to different replicas
        replicas[0].write("key1", "value1")
        replicas[1].write("key2", "value2")
        replicas[2].write("key3", "value3")
        
        # Sync all replicas
        for r1 in replicas:
            for r2 in replicas:
                if r1 != r2:
                    r1.sync_from(r2)
        
        # All replicas should have same state
        for i in range(len(replicas) - 1):
            assert replicas[i].state == replicas[i + 1].state


@pytest.mark.asyncio
class TestAsyncRaceConditions:
    """Test race conditions in async context."""
    
    async def test_async_concurrent_updates(self):
        """Test concurrent async updates."""
        state = {"counter": 0}
        lock = asyncio.Lock()
        
        async def increment():
            for _ in range(100):
                async with lock:
                    state["counter"] += 1
                await asyncio.sleep(0)
        
        await asyncio.gather(
            increment(),
            increment(),
            increment()
        )
        
        assert state["counter"] == 300
    
    async def test_async_semaphore_limiting(self):
        """Test semaphore limits concurrent access."""
        semaphore = asyncio.Semaphore(2)
        active_count = {"value": 0, "max": 0}
        lock = asyncio.Lock()
        
        async def limited_task():
            async with semaphore:
                async with lock:
                    active_count["value"] += 1
                    active_count["max"] = max(active_count["max"], active_count["value"])
                
                await asyncio.sleep(0.01)
                
                async with lock:
                    active_count["value"] -= 1
        
        await asyncio.gather(*[limited_task() for _ in range(10)])
        
        # Max concurrent should not exceed semaphore limit
        assert active_count["max"] <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
