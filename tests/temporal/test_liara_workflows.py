"""
Tests for Liara Crisis Response Workflows.

Tests the crisis response workflow, activities, and LiaraTemporalAgency
integration with Temporal.io.
"""

import pytest

# Crisis workflow data structures
from app.temporal.workflows import CrisisRequest, CrisisResult, MissionPhase


class TestCrisisDataModels:
    """Test crisis response data models."""

    def test_mission_phase_creation(self):
        """Test MissionPhase data class."""
        mission = MissionPhase(
            phase_id="test-phase-1",
            agent_id="agent-001",
            action="reconnaissance",
            target="target-alpha",
            priority=1,
        )

        assert mission.phase_id == "test-phase-1"
        assert mission.agent_id == "agent-001"
        assert mission.action == "reconnaissance"
        assert mission.target == "target-alpha"
        assert mission.priority == 1

    def test_crisis_request_creation(self):
        """Test CrisisRequest data class."""
        missions = [
            MissionPhase(
                phase_id="phase-1",
                agent_id="agent-001",
                action="deploy",
                target="target-1",
            )
        ]

        request = CrisisRequest(
            target_member="target-alpha",
            missions=missions,
            crisis_id="crisis-123",
            initiated_by="user-1",
        )

        assert request.target_member == "target-alpha"
        assert len(request.missions) == 1
        assert request.crisis_id == "crisis-123"
        assert request.initiated_by == "user-1"

    def test_crisis_result_success(self):
        """Test CrisisResult for successful completion."""
        result = CrisisResult(
            success=True,
            crisis_id="crisis-123",
            completed_phases=4,
            failed_phases=None,
            error=None,
        )

        assert result.success is True
        assert result.crisis_id == "crisis-123"
        assert result.completed_phases == 4
        assert result.failed_phases is None
        assert result.error is None

    def test_crisis_result_failure(self):
        """Test CrisisResult for partial failure."""
        result = CrisisResult(
            success=False,
            crisis_id="crisis-456",
            completed_phases=2,
            failed_phases=["phase-3", "phase-4"],
            error="Mission phase execution failed",
        )

        assert result.success is False
        assert result.crisis_id == "crisis-456"
        assert result.completed_phases == 2
        assert len(result.failed_phases) == 2
        assert result.error is not None


class TestLiaraTemporalAgency:
    """Test LiaraTemporalAgency class."""

    def test_agency_initialization(self):
        """Test agency initialization with default parameters."""
        from cognition.liara.agency import LiaraTemporalAgency

        agency = LiaraTemporalAgency()

        assert agency.temporal_host == "localhost:7233"
        assert agency.namespace == "default"
        assert agency.task_queue == "liara-crisis-tasks"
        assert agency._connected is False

    def test_agency_custom_parameters(self):
        """Test agency initialization with custom parameters."""
        from cognition.liara.agency import LiaraTemporalAgency

        agency = LiaraTemporalAgency(
            temporal_host="temporal.example.com:7233",
            namespace="production",
            task_queue="custom-queue",
        )

        assert agency.temporal_host == "temporal.example.com:7233"
        assert agency.namespace == "production"
        assert agency.task_queue == "custom-queue"

    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """Test connection lifecycle (requires running Temporal server)."""
        from cognition.liara.agency import LiaraTemporalAgency

        agency = LiaraTemporalAgency()

        # Initially not connected
        assert agency._connected is False

        # Note: This test requires a running Temporal server
        # In CI/CD, this test should be skipped or use a mock
        # For now, just verify the methods exist
        assert hasattr(agency, "connect")
        assert hasattr(agency, "disconnect")


class TestCrisisActivities:
    """Test crisis response activities."""

    @pytest.mark.asyncio
    async def test_validate_crisis_request_valid(self):
        """Test crisis request validation with valid data."""
        from app.temporal.activities import validate_crisis_request

        request = {
            "target_member": "target-alpha",
            "missions": [
                {
                    "phase_id": "phase-1",
                    "agent_id": "agent-001",
                    "action": "deploy",
                    "target": "target-alpha",
                }
            ],
        }

        result = await validate_crisis_request(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_crisis_request_invalid_target(self):
        """Test crisis request validation with invalid target."""
        from app.temporal.activities import validate_crisis_request

        request = {
            "target_member": "",  # Invalid
            "missions": [
                {
                    "phase_id": "phase-1",
                    "agent_id": "agent-001",
                    "action": "deploy",
                    "target": "target-alpha",
                }
            ],
        }

        result = await validate_crisis_request(request)
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_crisis_request_no_missions(self):
        """Test crisis request validation with no missions."""
        from app.temporal.activities import validate_crisis_request

        request = {
            "target_member": "target-alpha",
            "missions": [],  # No missions
        }

        result = await validate_crisis_request(request)
        assert result is False

    @pytest.mark.asyncio
    async def test_perform_agent_mission(self):
        """Test agent mission execution."""
        from app.temporal.activities import perform_agent_mission

        mission = {
            "phase_id": "test-phase",
            "agent_id": "test-agent",
            "action": "test-action",
            "target": "test-target",
        }

        result = await perform_agent_mission(mission)
        assert result is True


@pytest.mark.integration
class TestCrisisWorkflowIntegration:
    """
    Integration tests for crisis response workflow.

    These tests require a running Temporal server and should be
    marked as integration tests.
    """

    @pytest.mark.skip(reason="Requires running Temporal server")
    @pytest.mark.asyncio
    async def test_end_to_end_crisis_response(self):
        """Test complete crisis response workflow."""
        from cognition.liara.agency import LiaraTemporalAgency

        async with LiaraTemporalAgency() as agency:
            missions = [
                {
                    "phase_id": "phase-1",
                    "agent_id": "agent-001",
                    "action": "deploy",
                    "target": "test-target",
                    "priority": 1,
                }
            ]

            workflow_id = await agency.trigger_crisis_response(
                target_member="test-target",
                missions=missions,
                initiated_by="test-user",
            )

            assert workflow_id is not None
            assert "crisis-workflow-" in workflow_id

            # Wait for completion
            result = await agency.wait_for_crisis_completion(workflow_id)

            assert result["success"] is True
            assert result["completed_phases"] == 1
