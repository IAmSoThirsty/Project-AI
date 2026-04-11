"""
Locust Load Testing for Temporal Workflows
Python-based load testing with 1000+ concurrent agents
"""

import time
import uuid
import random
from typing import Dict, Any

from locust import HttpUser, task, between, events
from locust.runners import WorkerRunner


class TemporalWorkflowUser(HttpUser):
    """
    Simulates an agent executing Temporal workflows.
    Each user represents a concurrent agent in the system.
    """
    
    # Wait 1-3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts."""
        self.agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        self.workflows_completed = 0
        self.workflows_failed = 0
    
    @task(3)
    def execute_simple_workflow(self):
        """Execute a simple workflow (most common)."""
        workflow_id = f"simple-{self.agent_id}-{int(time.time())}"
        
        start_time = time.time()
        
        # Start workflow
        payload = {
            "workflowId": workflow_id,
            "taskQueue": "load-test-queue",
            "namespace": "default",
            "request": {
                "input_data": {
                    "agent_id": self.agent_id,
                    "operation": "simple_task",
                    "timestamp": time.time(),
                },
                "context": {
                    "test_run": "locust_load_test",
                    "correlation_id": workflow_id,
                },
                "timeout_seconds": 30,
                "max_retries": 3,
            },
        }
        
        with self.client.post(
            "/api/v1/workflows/start",
            json=payload,
            catch_response=True,
            name="Start Simple Workflow"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
                self._wait_for_completion(workflow_id, start_time, "simple")
            else:
                response.failure(f"Failed to start workflow: {response.status_code}")
                self.workflows_failed += 1
    
    @task(2)
    def execute_complex_workflow(self):
        """Execute a complex workflow with multiple steps."""
        workflow_id = f"complex-{self.agent_id}-{int(time.time())}"
        
        start_time = time.time()
        
        payload = {
            "workflowId": workflow_id,
            "taskQueue": "load-test-queue",
            "namespace": "default",
            "request": {
                "input_data": {
                    "agent_id": self.agent_id,
                    "operation": "complex_task",
                    "steps": ["step1", "step2", "step3"],
                    "data_size": random.randint(1000, 10000),
                },
                "context": {
                    "test_run": "locust_load_test",
                    "workflow_type": "complex",
                },
                "timeout_seconds": 60,
                "max_retries": 5,
            },
        }
        
        with self.client.post(
            "/api/v1/workflows/start",
            json=payload,
            catch_response=True,
            name="Start Complex Workflow"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
                self._wait_for_completion(workflow_id, start_time, "complex")
            else:
                response.failure(f"Failed to start workflow: {response.status_code}")
                self.workflows_failed += 1
    
    @task(1)
    def execute_long_running_workflow(self):
        """Execute a long-running workflow."""
        workflow_id = f"longrun-{self.agent_id}-{int(time.time())}"
        
        start_time = time.time()
        
        payload = {
            "workflowId": workflow_id,
            "taskQueue": "load-test-queue",
            "namespace": "default",
            "request": {
                "input_data": {
                    "agent_id": self.agent_id,
                    "operation": "long_running_task",
                    "duration_seconds": random.randint(30, 120),
                },
                "context": {
                    "test_run": "locust_load_test",
                    "workflow_type": "long_running",
                },
                "timeout_seconds": 180,
                "max_retries": 2,
            },
        }
        
        with self.client.post(
            "/api/v1/workflows/start",
            json=payload,
            catch_response=True,
            name="Start Long Running Workflow"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
                # Don't wait for long-running workflows to complete
                self.workflows_completed += 1
            else:
                response.failure(f"Failed to start workflow: {response.status_code}")
                self.workflows_failed += 1
    
    def _wait_for_completion(self, workflow_id: str, start_time: float, workflow_type: str):
        """Poll for workflow completion."""
        max_attempts = 60  # 60 * 0.5s = 30s timeout
        attempts = 0
        
        while attempts < max_attempts:
            time.sleep(0.5)
            
            with self.client.get(
                f"/api/v1/workflows/{workflow_id}/status",
                catch_response=True,
                name=f"Check {workflow_type.capitalize()} Workflow Status"
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "COMPLETED":
                            duration_ms = (time.time() - start_time) * 1000
                            response.success()
                            self.workflows_completed += 1
                            
                            # Record custom metric
                            events.request.fire(
                                request_type="workflow",
                                name=f"{workflow_type}_workflow_duration",
                                response_time=duration_ms,
                                response_length=0,
                                exception=None,
                                context={},
                            )
                            return
                        elif status in ["FAILED", "TERMINATED", "TIMED_OUT"]:
                            response.failure(f"Workflow {status}")
                            self.workflows_failed += 1
                            return
                    except Exception as e:
                        response.failure(f"Error parsing response: {e}")
                        self.workflows_failed += 1
                        return
            
            attempts += 1
        
        # Timeout
        self.workflows_failed += 1


class HighThroughputUser(HttpUser):
    """User that executes many small workflows rapidly."""
    
    wait_time = between(0.1, 0.5)  # Minimal wait time
    
    def on_start(self):
        self.agent_id = f"ht-agent-{uuid.uuid4().hex[:8]}"
    
    @task
    def fire_and_forget_workflow(self):
        """Execute workflow without waiting for completion."""
        workflow_id = f"ff-{self.agent_id}-{int(time.time() * 1000)}"
        
        payload = {
            "workflowId": workflow_id,
            "taskQueue": "load-test-queue",
            "namespace": "default",
            "request": {
                "input_data": {
                    "agent_id": self.agent_id,
                    "operation": "fire_and_forget",
                },
                "timeout_seconds": 10,
            },
        }
        
        with self.client.post(
            "/api/v1/workflows/start",
            json=payload,
            catch_response=True,
            name="Fire and Forget Workflow"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")


# Event handlers for custom statistics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the load test starts."""
    print("\n🚀 Starting Temporal load test...")
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the load test stops."""
    print("\n✅ Load test completed!")
    
    # Print custom statistics
    total_users = 0
    total_workflows_completed = 0
    total_workflows_failed = 0
    
    if isinstance(environment.runner, WorkerRunner):
        return  # Skip on worker nodes
    
    for user in environment.runner.user_classes:
        if hasattr(user, 'workflows_completed'):
            total_workflows_completed += user.workflows_completed
        if hasattr(user, 'workflows_failed'):
            total_workflows_failed += user.workflows_failed
    
    print(f"\nWorkflows Completed: {total_workflows_completed}")
    print(f"Workflows Failed: {total_workflows_failed}")
    
    if total_workflows_completed + total_workflows_failed > 0:
        success_rate = (total_workflows_completed / (total_workflows_completed + total_workflows_failed)) * 100
        print(f"Success Rate: {success_rate:.2f}%")


# Load test configuration (used by locustfile)
# Run with: locust -f locust-load-test.py --host=http://localhost:8080
