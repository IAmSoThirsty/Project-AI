"""
Liara Temporal Agency - Production-grade crisis response orchestration.

This module implements a distributed agent mission management system using
Temporal.io workflows for persistent, retry-enabled, horizontally-scalable
crisis response coordination.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.temporal.client import TemporalClientManager
from app.temporal.workflows import CrisisRequest, CrisisResponseWorkflow, MissionPhase

logger = logging.getLogger(__name__)


class LiaraTemporalAgency:
    """
    Temporal-based agency for distributed crisis response management.

    Replaces in-memory mission assignment with durable Temporal workflows,
    enabling persistent state, automatic retries, and horizontal scalability.

    Key features:
    - Persistent workflow execution (survives crashes and restarts)
    - Automatic retry logic for failed mission phases
    - Horizontal scalability via task queue distribution
    - Observable execution via Temporal Web UI
    - Deterministic workflow execution
    """

    def __init__(
        self,
        temporal_host: str = "localhost:7233",
        namespace: str = "default",
        task_queue: str = "liara-crisis-tasks",
    ):
        """
        Initialize Liara Temporal Agency.

        Args:
            temporal_host: Temporal server address
            namespace: Temporal namespace
            task_queue: Task queue for crisis workflows
        """
        self.temporal_host = temporal_host
        self.namespace = namespace
        self.task_queue = task_queue
        self._manager: TemporalClientManager | None = None
        self._connected = False

        logger.info(
            f"Liara Temporal Agency initialized - "
            f"Host: {temporal_host}, Namespace: {namespace}, "
            f"Task Queue: {task_queue}"
        )

    async def connect(self):
        """
        Establish connection to Temporal server.

        Must be called before triggering workflows.
        """
        if self._connected:
            logger.debug("Already connected to Temporal server")
            return

        self._manager = TemporalClientManager(
            target_host=self.temporal_host,
            namespace=self.namespace,
            task_queue=self.task_queue,
        )

        await self._manager.connect()
        self._connected = True
        logger.info("Liara Temporal Agency connected to Temporal server")

    async def disconnect(self):
        """Close Temporal connection and cleanup."""
        if self._manager and self._connected:
            await self._manager.disconnect()
            self._connected = False
            logger.info("Liara Temporal Agency disconnected")

    async def trigger_crisis_response(
        self,
        target_member: str,
        missions: list[dict],
        initiated_by: str | None = None,
    ) -> str:
        """
        Trigger crisis response workflow via Temporal.

        Replaces in-memory _assign_missions logic with durable Temporal workflow.

        Args:
            target_member: Target identifier for crisis response
            missions: List of mission phase dictionaries
            initiated_by: Optional identifier of initiator

        Returns:
            Crisis workflow ID for tracking

        Raises:
            RuntimeError: If not connected to Temporal server
        """
        if not self._connected or not self._manager:
            raise RuntimeError(
                "Not connected to Temporal server. Call connect() first."
            )

        # Generate unique crisis ID
        timestamp = datetime.now().timestamp()
        crisis_id = f"crisis-{target_member}-{int(timestamp)}"

        logger.info(
            f"Triggering crisis response for target: {target_member} "
            f"(Crisis ID: {crisis_id}, Missions: {len(missions)})"
        )

        # Convert mission dictionaries to MissionPhase objects
        mission_phases = []
        for idx, mission in enumerate(missions):
            phase = MissionPhase(
                phase_id=mission.get("phase_id", f"phase-{idx}"),
                agent_id=mission.get("agent_id", "default-agent"),
                action=mission.get("action", "deploy"),
                target=mission.get("target", target_member),
                priority=mission.get("priority", idx + 1),
            )
            mission_phases.append(phase)

        # Create crisis request
        request = CrisisRequest(
            target_member=target_member,
            missions=mission_phases,
            crisis_id=crisis_id,
            initiated_by=initiated_by,
        )

        # Start workflow (non-blocking)
        workflow_id = f"crisis-workflow-{crisis_id}"
        await self._manager.client.start_workflow(
            CrisisResponseWorkflow.run,
            request,
            id=workflow_id,
            task_queue=self.task_queue,
        )

        logger.info(
            f"Crisis response workflow started - "
            f"Workflow ID: {workflow_id}, Crisis ID: {crisis_id}"
        )

        return workflow_id

    async def get_crisis_status(self, workflow_id: str) -> dict:
        """
        Get status of crisis response workflow.

        Args:
            workflow_id: Workflow ID returned from trigger_crisis_response

        Returns:
            Dictionary with workflow status and result (if completed)
        """
        if not self._connected or not self._manager:
            raise RuntimeError("Not connected to Temporal server")

        handle = self._manager.client.get_workflow_handle(workflow_id)

        try:
            # Try to get result (non-blocking if workflow still running)
            result = await handle.result()
            return {
                "status": "completed",
                "success": result.success,
                "crisis_id": result.crisis_id,
                "completed_phases": result.completed_phases,
                "failed_phases": result.failed_phases,
                "error": result.error,
            }
        except Exception:
            # Workflow still running or error occurred
            return {
                "status": "running",
                "workflow_id": workflow_id,
            }

    async def wait_for_crisis_completion(self, workflow_id: str) -> dict:
        """
        Wait for crisis response workflow to complete.

        Args:
            workflow_id: Workflow ID returned from trigger_crisis_response

        Returns:
            Crisis result dictionary
        """
        if not self._connected or not self._manager:
            raise RuntimeError("Not connected to Temporal server")

        logger.info("Waiting for crisis workflow completion: %s", workflow_id)

        handle = self._manager.client.get_workflow_handle(workflow_id)
        result = await handle.result()

        logger.info(
            f"Crisis workflow completed - "
            f"Success: {result.success}, "
            f"Completed: {result.completed_phases}"
        )

        return {
            "success": result.success,
            "crisis_id": result.crisis_id,
            "completed_phases": result.completed_phases,
            "failed_phases": result.failed_phases,
            "error": result.error,
        }

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()
