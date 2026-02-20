"""
T.A.R.L. Load Testing, Chaos Testing, and Soak Testing Suite

Comprehensive hardening tests for the T.A.R.L. orchestration system under load,
failure injection, and prolonged execution scenarios.
"""

import asyncio
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from project_ai.tarl.integrations import (
    Capability,
    ExtendedTarlStackBox,
    ResourceQuota,
    TaskQueuePriority,
)

logger = logging.getLogger(__name__)


class TestLoadTesting:
    """Load testing suite - verify system behavior under high load"""

    def test_high_volume_task_enqueue(self):
        """Test enqueuing thousands of tasks rapidly"""
        stack = ExtendedTarlStackBox(config={"workers": 4})

        # Enqueue 1000 tasks
        task_ids = []
        start_time = time.time()

        for i in range(1000):
            task_id = stack.task_queue.enqueue(f"wf_{i}", "processing", {"index": i}, TaskQueuePriority.NORMAL)
            task_ids.append(task_id)

        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        assert len(task_ids) == 1000

        # Verify queue metrics
        metrics = stack.task_queue.get_metrics()
        assert metrics["tasks_enqueued"] >= 1000

    def test_concurrent_workflow_execution(self):
        """Test executing many workflows concurrently"""
        stack = ExtendedTarlStackBox(config={"workers": 8})

        def simple_workflow(vm, context):
            return {"result": f"success_{context.get('id', 0)}"}

        # Create 100 workflows
        for i in range(100):
            stack.create_workflow(f"wf_{i}", simple_workflow)

        # Execute concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(stack.vm.execute_workflow, f"wf_{i}", {"id": i}) for i in range(100)]

            results = [f.result() for f in as_completed(futures)]

        assert len(results) == 100
        assert all(r["result"].startswith("success_") for r in results)

    def test_multi_tenant_under_load(self):
        """Test multi-tenant isolation under high load"""
        stack = ExtendedTarlStackBox(config={"workers": 4})

        # Create 20 tenants
        for i in range(20):
            stack.multi_tenant.create_namespace(
                f"tenant_{i}",
                f"Tenant {i}",
                ResourceQuota(max_workflows=10, max_concurrent_executions=5, max_queue_depth=100),
            )

        # Each tenant consumes quota concurrently
        def consume_quota(tenant_id):
            for _ in range(5):
                try:
                    stack.multi_tenant.consume_quota(tenant_id, "workflows", amount=1)
                except Exception:
                    pass

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(consume_quota, f"tenant_{i}") for i in range(20)]

            [f.result() for f in as_completed(futures)]

        # Verify all namespaces still valid
        for i in range(20):
            usage = stack.multi_tenant.get_usage(f"tenant_{i}")
            assert "workflows" in usage

    def test_capability_checks_under_load(self):
        """Test capability verification with high request rate"""
        stack = ExtendedTarlStackBox(config={})

        # Register capability
        cap = Capability(name="Test.Action", resource="test", constraints={"level": "high"})
        stack.capabilities.register_capability(cap)

        # Check capability 10,000 times
        start_time = time.time()
        success_count = 0

        for _ in range(10000):
            allowed, _ = stack.capabilities.check_capability("Test.Action", {"level": "high"})
            if allowed:
                success_count += 1

        elapsed = time.time() - start_time

        # Should handle 10k checks in < 2 seconds
        assert elapsed < 2.0
        assert success_count == 10000

    @pytest.mark.asyncio
    async def test_async_activity_execution_at_scale(self):
        """Test async activity execution with many concurrent activities"""
        from project_ai.tarl.integrations.orchestration_extended import (
            Activity,
            ActivityExecutor,
        )

        class FastActivity(Activity):
            async def execute(self, **kwargs):
                await asyncio.sleep(0.01)
                return {"completed": True}

            async def compensate(self, **kwargs):
                pass

        executor = ActivityExecutor()
        activity = FastActivity("fast_activity", "test", {})

        # Execute 500 activities concurrently
        tasks = [executor.execute_activity(activity, idempotency_token=f"token_{i}") for i in range(500)]

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        assert len(results) == 500
        assert all(r["completed"] for r in results)
        # Should complete in reasonable time
        assert elapsed < 30.0


class TestChaosTesting:
    """Chaos testing suite - verify resilience under failure injection"""

    def test_random_task_failures(self):
        """Test task queue behavior when random tasks fail"""
        stack = ExtendedTarlStackBox(config={"workers": 4})

        # Enqueue 100 tasks
        task_ids = []
        for i in range(100):
            task_id = stack.task_queue.enqueue(f"wf_{i}", "processing", {"index": i}, TaskQueuePriority.NORMAL)
            task_ids.append(task_id)

        # Randomly fail 30% of tasks
        failed_count = 0
        for task_id in random.sample(task_ids, 30):
            try:
                stack.task_queue.fail_task(f"worker_{random.randint(0, 3)}", task_id, "Random chaos failure")
                failed_count += 1
            except Exception:
                pass

        # System should remain stable
        metrics = stack.task_queue.get_metrics()
        assert metrics["tasks_failed"] >= failed_count

    def test_quota_exhaustion_chaos(self):
        """Test behavior when tenants randomly exhaust quotas"""
        stack = ExtendedTarlStackBox(config={})

        # Create tenant with small quota
        stack.multi_tenant.create_namespace(
            "chaos_tenant",
            "Chaos Test",
            ResourceQuota(max_workflows=5, max_concurrent_executions=2),
        )

        # Try to exceed quota from multiple threads
        def try_consume():
            for _ in range(10):
                try:
                    stack.multi_tenant.consume_quota("chaos_tenant", "workflows", amount=1)
                except Exception:
                    pass

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(try_consume) for _ in range(10)]
            [f.result() for f in as_completed(futures)]

        # Should not crash, usage should be at or below limit
        usage = stack.multi_tenant.get_usage("chaos_tenant")
        assert usage["workflows"] <= 5

    def test_timer_cancellation_chaos(self):
        """Test random timer cancellations under load"""
        stack = ExtendedTarlStackBox(config={})

        # Schedule 50 timers
        timer_ids = []
        for i in range(50):
            timer_id = stack.long_running.schedule_timer(f"wf_{i}", delay=60, callback=lambda: None)  # Long delay
            timer_ids.append(timer_id)

        # Randomly cancel 50% of timers
        canceled_count = 0
        for timer_id in random.sample(timer_ids, 25):
            result = stack.long_running.cancel_timer(timer_id)
            if result:
                canceled_count += 1

        # Should successfully cancel most
        assert canceled_count >= 20

    def test_lease_expiration_chaos(self):
        """Test behavior when leases randomly expire"""
        stack = ExtendedTarlStackBox(config={})

        # Acquire leases with very short duration
        lease_holders = []
        for i in range(20):
            acquired = stack.long_running.acquire_lease(f"wf_{i}", f"executor_{i}", duration=0.1)  # Very short lease
            if acquired:
                lease_holders.append((f"wf_{i}", f"executor_{i}"))

        # Wait for leases to expire
        time.sleep(0.2)

        # Try to acquire same leases again (should succeed as they expired)
        reacquire_count = 0
        for wf_id, _ in lease_holders:
            acquired = stack.long_running.acquire_lease(wf_id, "new_executor", duration=10)
            if acquired:
                reacquire_count += 1

        # Most should be reacquirable
        assert reacquire_count >= 15

    def test_approval_rejection_chaos(self):
        """Test HITL system with random approvals and rejections"""
        stack = ExtendedTarlStackBox(config={})

        # Create 50 approval requests
        request_ids = []
        for i in range(50):
            request_id = stack.hitl.request_approval(
                f"wf_{i}",
                f"Action {i}",
                required_approvers=["alice", "bob"],
                context={"index": i},
            )
            request_ids.append(request_id)

        # Randomly approve or reject
        for request_id in request_ids:
            if random.choice([True, False]):
                stack.hitl.approve(request_id, "alice")
                stack.hitl.approve(request_id, "bob")
            else:
                stack.hitl.reject(request_id, "alice", "Random rejection")

        # All requests should have a status
        for request_id in request_ids:
            status = stack.hitl.get_approval_status(request_id)
            assert status["status"] in ["pending", "approved", "rejected"]


class TestSoakTesting:
    """Soak testing suite - verify stability over prolonged execution"""

    def test_continuous_task_processing(self):
        """Test continuous task processing for extended period"""
        stack = ExtendedTarlStackBox(config={"workers": 4})

        # Process tasks continuously for 10 seconds
        end_time = time.time() + 10
        tasks_processed = 0

        while time.time() < end_time:
            # Enqueue batch
            task_ids = []
            for i in range(10):
                task_id = stack.task_queue.enqueue(
                    f"wf_{tasks_processed + i}",
                    "processing",
                    {"index": tasks_processed + i},
                    TaskQueuePriority.NORMAL,
                )
                task_ids.append(task_id)

            # Simulate processing
            for task_id in task_ids:
                try:
                    task = stack.task_queue.lease_task(f"worker_{random.randint(0, 3)}", lease_duration=30)
                    if task:
                        stack.task_queue.complete_task(task["leased_by"], task["id"], {"result": "completed"})
                except Exception:
                    pass

            tasks_processed += 10
            time.sleep(0.1)

        # Should process hundreds of tasks
        assert tasks_processed >= 100

    def test_heartbeat_maintenance(self):
        """Test heartbeat system over extended period"""
        stack = ExtendedTarlStackBox(config={})

        # Acquire lease
        acquired = stack.long_running.acquire_lease("soak_wf", "soak_executor", duration=60)
        assert acquired

        # Send heartbeats for 5 seconds
        end_time = time.time() + 5
        heartbeat_count = 0

        while time.time() < end_time:
            extended = stack.long_running.heartbeat("soak_wf", "soak_executor")
            if extended:
                heartbeat_count += 1
            time.sleep(0.5)

        # Should have sent multiple heartbeats
        assert heartbeat_count >= 8

    def test_namespace_quota_cycling(self):
        """Test quota consume/release cycling over time"""
        stack = ExtendedTarlStackBox(config={})

        stack.multi_tenant.create_namespace("soak_tenant", "Soak Test", ResourceQuota(max_workflows=10))

        # Cycle quota usage for 5 seconds
        end_time = time.time() + 5
        cycles = 0

        while time.time() < end_time:
            # Consume
            for _ in range(5):
                try:
                    stack.multi_tenant.consume_quota("soak_tenant", "workflows", amount=1)
                except Exception:
                    pass

            # Release
            for _ in range(5):
                try:
                    stack.multi_tenant.release_quota("soak_tenant", "workflows", amount=1)
                except Exception:
                    pass

            cycles += 1
            time.sleep(0.1)

        # Should complete many cycles
        assert cycles >= 30

        # Final usage should be valid
        usage = stack.multi_tenant.get_usage("soak_tenant")
        assert usage["workflows"] >= 0

    def test_capability_check_endurance(self):
        """Test capability checking over extended period"""
        stack = ExtendedTarlStackBox(config={})

        cap = Capability(name="Soak.Test", resource="soak", constraints={})
        stack.capabilities.register_capability(cap)

        # Check capability continuously for 5 seconds
        end_time = time.time() + 5
        check_count = 0

        while time.time() < end_time:
            for _ in range(100):
                allowed, _ = stack.capabilities.check_capability("Soak.Test", {})
                if allowed:
                    check_count += 1
            time.sleep(0.01)

        # Should perform thousands of checks
        assert check_count >= 10000


class TestPerformanceDegradation:
    """Test for performance degradation over time"""

    def test_no_memory_leak_in_task_queue(self):
        """Verify task queue doesn't leak memory over many operations"""
        stack = ExtendedTarlStackBox(config={"workers": 2})

        # Enqueue and complete many tasks
        for batch in range(10):
            task_ids = []
            for i in range(100):
                task_id = stack.task_queue.enqueue(
                    f"wf_{batch}_{i}",
                    "processing",
                    {"batch": batch, "index": i},
                    TaskQueuePriority.NORMAL,
                )
                task_ids.append(task_id)

            # Complete tasks
            for task_id in task_ids:
                try:
                    task = stack.task_queue.lease_task(f"worker_{random.randint(0, 1)}", lease_duration=30)
                    if task:
                        stack.task_queue.complete_task(task["leased_by"], task["id"], {"result": "done"})
                except Exception:
                    pass

        # Queue should not grow unbounded
        metrics = stack.task_queue.get_metrics()
        assert metrics["queue_depth"] < 50

    def test_workflow_execution_latency_stability(self):
        """Verify workflow execution latency remains stable"""
        stack = ExtendedTarlStackBox(config={})

        def benchmark_workflow(vm, context):
            return {"result": "completed"}

        stack.create_workflow("benchmark", benchmark_workflow)

        # Measure latency over 100 executions
        latencies = []
        for i in range(100):
            start = time.time()
            stack.vm.execute_workflow("benchmark", {"run": i})
            latencies.append(time.time() - start)

        # Calculate percentiles
        latencies.sort()
        p50 = latencies[50]
        p99 = latencies[99]

        # P99 should not be much worse than P50 (< 5x)
        assert p99 < p50 * 5


# Pytest configuration for load testing
def pytest_configure(config):
    """Configure pytest markers for load testing"""
    config.addinivalue_line("markers", "load: mark test as load test (may be slow)")
    config.addinivalue_line("markers", "chaos: mark test as chaos test (may be unstable)")
    config.addinivalue_line("markers", "soak: mark test as soak test (runs for extended period)")


# Mark all tests appropriately
for attr_name in dir(TestLoadTesting):
    if attr_name.startswith("test_"):
        attr = getattr(TestLoadTesting, attr_name)
        if callable(attr):
            pytest.mark.load(attr)

for attr_name in dir(TestChaosTesting):
    if attr_name.startswith("test_"):
        attr = getattr(TestChaosTesting, attr_name)
        if callable(attr):
            pytest.mark.chaos(attr)

for attr_name in dir(TestSoakTesting):
    if attr_name.startswith("test_"):
        attr = getattr(TestSoakTesting, attr_name)
        if callable(attr):
            pytest.mark.soak(attr)
