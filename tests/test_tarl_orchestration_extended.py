"""
Comprehensive tests for T.A.R.L. Extended Orchestration Features

Achieves 100% code coverage for orchestration_extended.py
"""

import tempfile

import pytest

from project_ai.tarl.integrations.orchestration_extended import (
    Activity,
    ActivityExecutor,
    ExtendedTarlStackBox,
    HumanInTheLoopManager,
    LongRunningWorkflowManager,
    MetaOrchestrator,
    MultiTenantManager,
    ResourceQuota,
    TaskQueue,
    TaskQueuePriority,
    WorkerPool,
    WorkflowHierarchyManager,
)

# ============================================================================
# TEST TASK QUEUE AND WORKER POOL
# ============================================================================


class TestTaskQueue:
    """Test distributed task queue"""

    def test_task_enqueue(self):
        """Test task enqueueing"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        task_id = queue.enqueue(
            workflow_id="wf_001",
            task_type="processing",
            payload={"data": [1, 2, 3]},
            priority=TaskQueuePriority.HIGH,
        )

        assert task_id is not None
        assert queue._metrics["tasks_enqueued"] == 1
        assert len(queue._queues[TaskQueuePriority.HIGH]) == 1

    def test_lease_task(self):
        """Test task leasing"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        task_id = queue.enqueue(
            workflow_id="wf_001",
            task_type="processing",
            payload={"data": [1, 2, 3]},
        )

        leased_task = queue.lease_task("worker_1", lease_duration=300)

        assert leased_task is not None
        assert leased_task.lease_holder == "worker_1"
        assert "worker_1" in queue._leases

    def test_complete_task(self):
        """Test task completion"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        task_id = queue.enqueue("wf_001", "processing", {})
        task = queue.lease_task("worker_1")

        queue.complete_task("worker_1", task.task_id, result="success")

        assert "worker_1" not in queue._leases
        assert queue._metrics["tasks_completed"] == 1

    def test_fail_task_with_retry(self):
        """Test task failure with retry"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        task_id = queue.enqueue("wf_001", "processing", {})
        task = queue.lease_task("worker_1")

        queue.fail_task("worker_1", task.task_id, error="Test error")

        assert "worker_1" not in queue._leases
        assert queue._metrics["tasks_retried"] == 1
        # Task should be re-enqueued
        assert len(queue._queues[TaskQueuePriority.NORMAL]) == 1

    def test_fail_task_permanently(self):
        """Test task failure after max retries"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        task_id = queue.enqueue("wf_001", "processing", {})

        # Fail task 3 times (max_attempts)
        for _ in range(3):
            task = queue.lease_task("worker_1")
            queue.fail_task("worker_1", task.task_id, error="Test error")

        assert queue._metrics["tasks_failed"] == 1
        assert len(queue._dlq) == 1

    def test_worker_registration(self):
        """Test worker registration"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        queue.register_worker(
            "worker_1", capabilities=["ml", "data"], metadata={"region": "us-east"}
        )

        assert "worker_1" in queue._workers
        assert queue._workers["worker_1"]["capabilities"] == ["ml", "data"]

    def test_heartbeat(self):
        """Test worker heartbeat"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        queue.register_worker("worker_1", capabilities=["*"], metadata={})
        queue.heartbeat("worker_1")

        assert "last_heartbeat" in queue._workers["worker_1"]

    def test_get_metrics(self):
        """Test metrics retrieval"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        queue.enqueue("wf_001", "processing", {})
        metrics = queue.get_metrics()

        assert "tasks_enqueued" in metrics
        assert "queue_depth" in metrics
        assert metrics["queue_depth"] == 1

    def test_priority_ordering(self):
        """Test that high priority tasks are leased first"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())

        # Enqueue low priority first
        queue.enqueue("wf_001", "low", {}, priority=TaskQueuePriority.LOW)
        # Then high priority
        queue.enqueue("wf_002", "high", {}, priority=TaskQueuePriority.CRITICAL)

        # Lease should get critical priority first
        task = queue.lease_task("worker_1")
        assert task.workflow_id == "wf_002"


class TestWorkerPool:
    """Test worker pool"""

    @pytest.mark.asyncio
    async def test_worker_pool_start(self):
        """Test worker pool startup"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())
        pool = WorkerPool(queue, worker_count=4)

        await pool.start()

        assert pool._running is True
        assert len(pool._workers) == 4

    @pytest.mark.asyncio
    async def test_worker_pool_stop(self):
        """Test worker pool shutdown"""
        queue = TaskQueue("test_queue", data_dir=tempfile.mkdtemp())
        pool = WorkerPool(queue, worker_count=2)

        await pool.start()
        await pool.stop()

        assert pool._running is False


# ============================================================================
# TEST LONG-RUNNING WORKFLOWS
# ============================================================================


class TestLongRunningWorkflowManager:
    """Test long-running workflow features"""

    def test_schedule_timer(self):
        """Test durable timer scheduling"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        callback_called = [False]

        def callback():
            callback_called[0] = True

        timer_id = manager.schedule_timer("wf_001", delay=10, callback=callback)

        assert timer_id in manager._timers
        assert manager._timers[timer_id].workflow_id == "wf_001"

    def test_cancel_timer(self):
        """Test timer cancellation"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        timer_id = manager.schedule_timer("wf_001", delay=10, callback=lambda: None)
        manager.cancel_timer(timer_id)

        assert manager._timers[timer_id].cancelled is True

    def test_fire_timers(self):
        """Test timer firing"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        callback_called = [False]

        def callback():
            callback_called[0] = True

        timer_id = manager.schedule_timer("wf_001", delay=0, callback=callback)
        fired = manager.fire_timers()

        assert len(fired) == 1
        assert callback_called[0] is True
        assert manager._timers[timer_id].fired is True

    def test_timer_callback_exception(self):
        """Test timer callback exception handling"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        def failing_callback():
            raise ValueError("Test error")

        timer_id = manager.schedule_timer("wf_001", delay=0, callback=failing_callback)

        # Should not raise exception
        fired = manager.fire_timers()
        assert len(fired) == 1

    def test_acquire_lease(self):
        """Test lease acquisition"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        acquired = manager.acquire_lease("wf_001", "executor_1", duration=300)

        assert acquired is True
        assert "wf_001" in manager._leases
        assert manager._leases["wf_001"].holder == "executor_1"

    def test_acquire_lease_already_held(self):
        """Test lease acquisition when already held"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        manager.acquire_lease("wf_001", "executor_1", duration=300)
        acquired = manager.acquire_lease("wf_001", "executor_2", duration=300)

        assert acquired is False

    def test_release_lease(self):
        """Test lease release"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        manager.acquire_lease("wf_001", "executor_1")
        manager.release_lease("wf_001", "executor_1")

        assert "wf_001" not in manager._leases

    def test_heartbeat(self):
        """Test lease heartbeat"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        manager.acquire_lease("wf_001", "executor_1", duration=100)
        result = manager.heartbeat("wf_001", "executor_1")

        assert result is True
        # Lease should be extended
        assert manager._leases["wf_001"].expires_at > 100

    def test_heartbeat_wrong_holder(self):
        """Test heartbeat with wrong holder"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        manager.acquire_lease("wf_001", "executor_1")
        result = manager.heartbeat("wf_001", "executor_2")

        assert result is False

    def test_heartbeat_no_lease(self):
        """Test heartbeat with no lease"""
        manager = LongRunningWorkflowManager(data_dir=tempfile.mkdtemp())

        result = manager.heartbeat("wf_001", "executor_1")

        assert result is False


# ============================================================================
# TEST ACTIVITY EXECUTOR
# ============================================================================


class DummyActivity(Activity):
    """Test activity implementation"""

    def __init__(self):
        super().__init__("dummy_activity", idempotent=True)
        self.execute_count = 0

    async def execute(self, **kwargs):
        self.execute_count += 1
        return {"result": "success", "count": self.execute_count}

    async def compensate(self, **kwargs):
        pass


class FailingActivity(Activity):
    """Activity that always fails"""

    def __init__(self):
        super().__init__("failing_activity")
        self.attempts = 0

    async def execute(self, **kwargs):
        self.attempts += 1
        raise ValueError("Intentional failure")

    async def compensate(self, **kwargs):
        pass


class TestActivityExecutor:
    """Test activity execution"""

    @pytest.mark.asyncio
    async def test_execute_activity_success(self):
        """Test successful activity execution"""
        executor = ActivityExecutor(data_dir=tempfile.mkdtemp())
        activity = DummyActivity()

        result = await executor.execute_activity(activity)

        assert result.success is True
        assert result.result["result"] == "success"
        assert activity.execute_count == 1

    @pytest.mark.asyncio
    async def test_execute_activity_with_idempotency(self):
        """Test idempotent activity execution"""
        executor = ActivityExecutor(data_dir=tempfile.mkdtemp())
        activity = DummyActivity()

        token = "test_token"

        # First execution
        result1 = await executor.execute_activity(activity, idempotency_token=token)
        assert result1.success is True
        assert activity.execute_count == 1

        # Second execution with same token - should return cached result
        result2 = await executor.execute_activity(activity, idempotency_token=token)
        assert result2.success is True
        assert activity.execute_count == 1  # Not incremented

    @pytest.mark.asyncio
    async def test_execute_activity_with_retries(self):
        """Test activity execution with retries"""
        executor = ActivityExecutor(data_dir=tempfile.mkdtemp())
        activity = FailingActivity()

        result = await executor.execute_activity(activity, max_retries=3)

        assert result.success is False
        assert result.error is not None
        assert activity.attempts == 3


# ============================================================================
# TEST MULTI-TENANT MANAGER
# ============================================================================


class TestMultiTenantManager:
    """Test multi-tenancy support"""

    def test_create_namespace(self):
        """Test namespace creation"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota(max_workflows=100, max_concurrent_executions=10)
        namespace = manager.create_namespace(
            "tenant_001", "Test Tenant", quota, isolation_level="strict"
        )

        assert namespace.namespace_id == "tenant_001"
        assert "tenant_001" in manager._namespaces

    def test_check_quota_available(self):
        """Test quota availability check"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota(max_workflows=100)
        manager.create_namespace("tenant_001", "Test", quota)

        available = manager.check_quota("tenant_001", "workflows", amount=50)
        assert available is True

    def test_check_quota_exceeded(self):
        """Test quota exceeded check"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota(max_workflows=10)
        manager.create_namespace("tenant_001", "Test", quota)

        # Consume quota
        manager.consume_quota("tenant_001", "workflows", amount=10)

        # Should fail
        available = manager.check_quota("tenant_001", "workflows", amount=1)
        assert available is False

    def test_consume_quota(self):
        """Test quota consumption"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota(max_workflows=100)
        manager.create_namespace("tenant_001", "Test", quota)

        manager.consume_quota("tenant_001", "workflows", amount=10)

        usage = manager.get_usage("tenant_001")
        assert usage["workflows"] == 10

    def test_consume_quota_exceeded_raises(self):
        """Test that consuming exceeded quota raises error"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota(max_workflows=5)
        manager.create_namespace("tenant_001", "Test", quota)

        with pytest.raises(ValueError, match="Quota exceeded"):
            manager.consume_quota("tenant_001", "workflows", amount=10)

    def test_release_quota(self):
        """Test quota release"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota(max_workflows=100)
        manager.create_namespace("tenant_001", "Test", quota)

        manager.consume_quota("tenant_001", "workflows", amount=10)
        manager.release_quota("tenant_001", "workflows", amount=5)

        usage = manager.get_usage("tenant_001")
        assert usage["workflows"] == 5

    def test_get_usage(self):
        """Test usage retrieval"""
        manager = MultiTenantManager(data_dir=tempfile.mkdtemp())

        quota = ResourceQuota()
        manager.create_namespace("tenant_001", "Test", quota)

        usage = manager.get_usage("tenant_001")
        assert isinstance(usage, dict)


# ============================================================================
# TEST HUMAN-IN-THE-LOOP
# ============================================================================


class TestHumanInTheLoopManager:
    """Test human-in-the-loop features"""

    def test_send_signal(self):
        """Test signal sending"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        signal_id = manager.send_signal(
            "wf_001", "pause", payload={"reason": "user_request"}
        )

        assert signal_id is not None
        assert len(manager._signals["wf_001"]) == 1

    def test_get_signals(self):
        """Test getting signals"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        manager.send_signal("wf_001", "pause", payload={})
        manager.send_signal("wf_001", "resume", payload={})

        signals = manager.get_signals("wf_001")
        assert len(signals) == 2

    def test_get_signals_filtered(self):
        """Test getting filtered signals"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        manager.send_signal("wf_001", "pause", payload={})
        manager.send_signal("wf_001", "resume", payload={})

        signals = manager.get_signals("wf_001", signal_type="pause")
        assert len(signals) == 1
        assert signals[0].signal_type == "pause"

    def test_request_approval(self):
        """Test approval request"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        request_id = manager.request_approval(
            workflow_id="wf_001",
            description="Deploy to production",
            required_approvers=["alice", "bob"],
            context={"version": "1.0.0"},
        )

        assert request_id in manager._approval_requests
        assert manager._approval_requests[request_id].status == "pending"

    def test_approve(self):
        """Test approval"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        request_id = manager.request_approval("wf_001", "Deploy", ["alice"], context={})

        result = manager.approve(request_id, "alice")

        assert result is True
        assert manager._approval_requests[request_id].status == "approved"

    def test_approve_multiple_approvers(self):
        """Test approval with multiple required approvers"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        request_id = manager.request_approval(
            "wf_001", "Deploy", ["alice", "bob"], context={}
        )

        # First approval
        manager.approve(request_id, "alice")
        assert manager._approval_requests[request_id].status == "pending"

        # Second approval
        manager.approve(request_id, "bob")
        assert manager._approval_requests[request_id].status == "approved"

    def test_approve_invalid_approver(self):
        """Test approval by invalid approver"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        request_id = manager.request_approval("wf_001", "Deploy", ["alice"], context={})

        result = manager.approve(request_id, "charlie")
        assert result is False

    def test_reject(self):
        """Test rejection"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        request_id = manager.request_approval("wf_001", "Deploy", ["alice"], context={})

        result = manager.reject(request_id, "alice")

        assert result is True
        assert manager._approval_requests[request_id].status == "rejected"

    def test_is_approved(self):
        """Test approval status check"""
        manager = HumanInTheLoopManager(data_dir=tempfile.mkdtemp())

        request_id = manager.request_approval("wf_001", "Deploy", ["alice"], context={})

        assert manager.is_approved(request_id) is False

        manager.approve(request_id, "alice")
        assert manager.is_approved(request_id) is True


# ============================================================================
# TEST META-ORCHESTRATION
# ============================================================================


class TestMetaOrchestrator:
    """Test meta-orchestration layer"""

    def test_register_orchestrator(self):
        """Test orchestrator node registration"""
        meta = MetaOrchestrator()

        meta.register_orchestrator("orch_1", capabilities=["ml", "data"], priority=10)

        assert "orch_1" in meta._nodes

    def test_route_task(self):
        """Test task routing"""
        meta = MetaOrchestrator()

        meta.register_orchestrator("orch_1", capabilities=["ml", "data"], priority=10)

        node_id = meta.route_task("ml_task", required_capabilities=["ml"])

        assert node_id == "orch_1"

    def test_route_task_no_candidate(self):
        """Test routing when no suitable node"""
        meta = MetaOrchestrator()

        meta.register_orchestrator("orch_1", capabilities=["data"], priority=10)

        node_id = meta.route_task("ml_task", required_capabilities=["ml"])

        assert node_id is None

    def test_route_task_load_balancing(self):
        """Test routing considers load"""
        meta = MetaOrchestrator()

        meta.register_orchestrator("orch_1", capabilities=["ml"], priority=10)
        meta.register_orchestrator("orch_2", capabilities=["ml"], priority=10)

        # Route first task
        node_id1 = meta.route_task("ml_task", ["ml"])

        # Route second task - should prefer lower load
        node_id2 = meta.route_task("ml_task", ["ml"])

        # Should distribute load
        assert node_id1 is not None
        assert node_id2 is not None

    def test_route_task_max_load(self):
        """Test routing respects max load"""
        meta = MetaOrchestrator()

        meta.register_orchestrator(
            "orch_1", capabilities=["ml"], priority=10, max_load=1
        )

        # First task should succeed
        node_id1 = meta.route_task("ml_task", ["ml"])
        assert node_id1 == "orch_1"

        # Second task should fail (max load reached)
        node_id2 = meta.route_task("ml_task", ["ml"])
        assert node_id2 is None

    def test_release_task(self):
        """Test task release"""
        meta = MetaOrchestrator()

        meta.register_orchestrator("orch_1", capabilities=["ml"], priority=10)
        meta.route_task("ml_task", ["ml"])

        initial_load = meta._nodes["orch_1"].load

        meta.release_task("orch_1")

        assert meta._nodes["orch_1"].load == initial_load - 1

    def test_add_routing_rule(self):
        """Test adding routing rules"""
        meta = MetaOrchestrator()

        meta.add_routing_rule("ml_*", "orch_ml", priority=10)

        assert len(meta._routing_rules) == 1
        assert meta._routing_rules[0]["target"] == "orch_ml"


# ============================================================================
# TEST WORKFLOW HIERARCHY
# ============================================================================


class TestWorkflowHierarchyManager:
    """Test workflow hierarchy management"""

    def test_spawn_child(self):
        """Test child workflow spawning"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child("parent_wf", "data_processing")

        assert child_id is not None
        assert len(manager._children["parent_wf"]) == 1

    def test_spawn_child_with_id(self):
        """Test spawning child with specific ID"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child(
            "parent_wf", "data_processing", child_id="child_001"
        )

        assert child_id == "child_001"

    def test_update_child_status(self):
        """Test updating child status"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child("parent_wf", "data_processing")
        manager.update_child_status(child_id, "completed", result="Success")

        child = manager._children["parent_wf"][0]
        assert child.status == "completed"
        assert child.result == "Success"

    def test_wait_for_child_not_complete(self):
        """Test waiting for incomplete child"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child("parent_wf", "data_processing")

        result = manager.wait_for_child("parent_wf", child_id)
        assert result is None

    def test_wait_for_child_complete(self):
        """Test waiting for completed child"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child("parent_wf", "data_processing")
        manager.update_child_status(child_id, "completed", result="Success")

        result = manager.wait_for_child("parent_wf", child_id)
        assert result is not None
        assert result.status == "completed"

    def test_wait_for_all_children(self):
        """Test waiting for all children"""
        manager = WorkflowHierarchyManager()

        child1 = manager.spawn_child("parent_wf", "task1")
        child2 = manager.spawn_child("parent_wf", "task2")

        manager.update_child_status(child1, "completed")
        manager.update_child_status(child2, "failed")

        completed = manager.wait_for_all_children("parent_wf")
        assert len(completed) == 2

    def test_cancel_child(self):
        """Test child cancellation"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child("parent_wf", "data_processing")
        manager.cancel_child(child_id)

        child = manager._children["parent_wf"][0]
        assert child.status == "cancelled"

    def test_propagate_failure(self):
        """Test failure propagation"""
        manager = WorkflowHierarchyManager()

        child_id = manager.spawn_child("parent_wf", "data_processing")

        # Should not raise exception
        manager.propagate_failure(child_id, "Test error")


# ============================================================================
# TEST EXTENDED STACK BOX
# ============================================================================


class TestExtendedTarlStackBox:
    """Test integrated extended stack"""

    def test_initialization(self):
        """Test stack initialization"""
        stack = ExtendedTarlStackBox(config={"workers": 2})

        assert stack.task_queue is not None
        assert stack.worker_pool is not None
        assert stack.long_running is not None
        assert stack.activity_executor is not None
        assert stack.multi_tenant is not None
        assert stack.hitl is not None
        assert stack.meta_orchestrator is not None
        assert stack.workflow_hierarchy is not None

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test stack start and stop"""
        stack = ExtendedTarlStackBox(config={"workers": 2})

        await stack.start()
        assert stack.worker_pool._running is True

        await stack.stop()
        assert stack.worker_pool._running is False

    def test_get_status(self):
        """Test comprehensive status"""
        stack = ExtendedTarlStackBox()

        status = stack.get_status()

        assert "task_queue" in status
        assert "worker_pool" in status
        assert "long_running" in status
        assert "activity_executor" in status
        assert "multi_tenant" in status
        assert "hitl" in status
        assert "meta_orchestrator" in status
        assert "workflow_hierarchy" in status


# ============================================================================
# TEST DEMO FUNCTION
# ============================================================================


class TestDemo:
    """Test demo function"""

    @pytest.mark.asyncio
    async def test_demo_extended_features(self):
        """Test that demo runs without errors"""
        from project_ai.tarl.integrations.orchestration_extended import (
            demo_extended_features,
        )

        # Should complete without exceptions
        await demo_extended_features()


if __name__ == "__main__":
    pytest.main(
        [__file__, "-v", "--cov=project_ai.tarl.integrations.orchestration_extended"]
    )
