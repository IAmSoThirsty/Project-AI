"""
Tests for Temporal integration components.

These tests verify that the Temporal integration works correctly,
including workflows, activities, and the AI controller.
"""

import pytest

# Import all components to test
from integrations.temporal.activities.core_tasks import (
    process_ai_task,
    simulate_ai_call,
    validate_input,
)
from integrations.temporal.client import TemporalClient
from integrations.temporal.workflows.example_workflow import (
    ExampleWorkflow,
    WorkflowInput,
    WorkflowOutput,
)


class TestTemporalClient:
    """Tests for Temporal client wrapper."""

    def test_client_initialization(self):
        """Test client can be initialized with default settings."""
        client = TemporalClient()
        assert client.host == "localhost:7233"
        assert client.namespace == "default"
        assert client.task_queue == "project-ai-tasks"

    def test_client_custom_settings(self):
        """Test client can be initialized with custom settings."""
        client = TemporalClient(
            host="custom-host:7233",
            namespace="custom-namespace",
            task_queue="custom-queue",
        )
        assert client.host == "custom-host:7233"
        assert client.namespace == "custom-namespace"
        assert client.task_queue == "custom-queue"


class TestWorkflowDataClasses:
    """Tests for workflow input/output data classes."""

    def test_workflow_input_creation(self):
        """Test WorkflowInput can be created."""
        input_data = WorkflowInput(
            data="test data", user_id="user123", options={"key": "value"}
        )
        assert input_data.data == "test data"
        assert input_data.user_id == "user123"
        assert input_data.options == {"key": "value"}

    def test_workflow_output_creation(self):
        """Test WorkflowOutput can be created."""
        output = WorkflowOutput(
            success=True,
            result="test result",
            steps_completed=["step1", "step2"],
        )
        assert output.success is True
        assert output.result == "test result"
        assert output.steps_completed == ["step1", "step2"]

    def test_workflow_output_error(self):
        """Test WorkflowOutput can represent errors."""
        output = WorkflowOutput(success=False, error="Test error")
        assert output.success is False
        assert output.error == "Test error"
        assert output.result is None


class TestActivities:
    """Tests for Temporal activities (can run without Temporal server)."""

    @pytest.mark.asyncio
    async def test_validate_input_valid(self):
        """Test input validation with valid data."""
        result = await validate_input("This is valid input data")
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_input_too_short(self):
        """Test input validation rejects short data."""
        result = await validate_input("ab")
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_input_too_long(self):
        """Test input validation rejects oversized data."""
        result = await validate_input("x" * 20000)
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_input_dangerous_content(self):
        """Test input validation rejects dangerous patterns."""
        result = await validate_input("<script>alert('xss')</script>")
        assert result is False

    @pytest.mark.asyncio
    async def test_simulate_ai_call(self):
        """Test AI call simulation."""
        result = await simulate_ai_call("Test prompt")
        assert "AI Response" in result
        assert "Test prompt" in result or "Processed" in result

    @pytest.mark.asyncio
    async def test_process_ai_task(self):
        """Test AI task processing."""
        task_data = {
            "input": "test input",
            "ai_response": "test response",
            "user_id": "user123",
        }
        result = await process_ai_task(task_data)
        assert "Task processed successfully" in result
        assert "user123" in result


@pytest.mark.integration
class TestIntegrationStructure:
    """Integration tests for the overall structure."""

    def test_imports_work(self):
        """Test that all components can be imported."""
        # If we got here, imports worked
        assert TemporalClient is not None
        assert ExampleWorkflow is not None
        assert WorkflowInput is not None
        assert validate_input is not None
        assert simulate_ai_call is not None
        assert process_ai_task is not None

    def test_workflow_class_exists(self):
        """Test workflow class is properly defined."""
        assert hasattr(ExampleWorkflow, "run")
        assert callable(ExampleWorkflow.run)
