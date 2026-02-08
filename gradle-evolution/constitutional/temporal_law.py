"""
Temporal Law Enforcement
========================

Integrates Temporal workflows with constitutional policy enforcement.
Provides time-bound policy evaluation and workflow-based governance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from temporalio.client import Client

logger = logging.getLogger(__name__)


class TemporalLawEnforcer:
    """
    Enforces constitutional policies through Temporal workflows.
    Enables time-travel debugging and temporal policy queries.
    """

    def __init__(
        self,
        temporal_client: Client | None = None,
        task_queue: str = "constitutional-enforcement"
    ):
        """
        Initialize temporal law enforcer.

        Args:
            temporal_client: Optional Temporal client (creates default if None)
            task_queue: Temporal task queue name
        """
        self.temporal_client = temporal_client
        self.task_queue = task_queue
        self.workflow_cache: dict[str, str] = {}  # action_id -> workflow_id
        logger.info(f"Temporal law enforcer initialized with queue: {task_queue}")

    async def enforce_with_timeout(
        self,
        action: str,
        metadata: dict[str, Any],
        timeout_seconds: int = 30
    ) -> dict[str, Any]:
        """
        Enforce policy with temporal timeout.

        Args:
            action: Action to validate
            metadata: Action metadata
            timeout_seconds: Enforcement timeout

        Returns:
            Enforcement result with decision and metadata
        """
        try:
            if not self.temporal_client:
                logger.warning("Temporal client not available, using local enforcement")
                return self._local_enforcement(action, metadata)

            # Start enforcement workflow
            workflow_id = f"enforce-{action}-{datetime.utcnow().timestamp()}"

            handle = await self.temporal_client.start_workflow(
                "PolicyEnforcementWorkflow",
                args=[action, metadata],
                id=workflow_id,
                task_queue=self.task_queue,
            )

            self.workflow_cache[action] = workflow_id

            # Wait for result with timeout
            result = await asyncio.wait_for(
                handle.result(),
                timeout=timeout_seconds
            )

            logger.info(f"Temporal enforcement completed: {action}")
            return result

        except TimeoutError:
            logger.error(f"Enforcement timeout for action: {action}")
            return {
                "allowed": False,
                "reason": f"Policy enforcement timeout ({timeout_seconds}s)",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error in temporal enforcement: {e}", exc_info=True)
            return {
                "allowed": False,
                "reason": f"Enforcement error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def query_historical_decision(
        self,
        action: str,
        timestamp: datetime
    ) -> dict[str, Any] | None:
        """
        Query historical policy decision at a specific point in time.

        Args:
            action: Action to query
            timestamp: Point in time for query

        Returns:
            Historical decision data or None if not found
        """
        try:
            workflow_id = self.workflow_cache.get(action)
            if not workflow_id or not self.temporal_client:
                logger.warning(f"No workflow found for action: {action}")
                return None

            handle = self.temporal_client.get_workflow_handle(workflow_id)

            # Query workflow at specific time
            result = await handle.query(
                "get_decision_at_time",
                args=[timestamp.isoformat()]
            )

            logger.debug(f"Historical query result for {action}: {result}")
            return result

        except Exception as e:
            logger.error(f"Error querying historical decision: {e}", exc_info=True)
            return None

    async def schedule_periodic_review(
        self,
        action: str,
        metadata: dict[str, Any],
        interval_hours: int = 24
    ) -> str:
        """
        Schedule periodic policy review for an action.

        Args:
            action: Action to review
            metadata: Action metadata
            interval_hours: Review interval in hours

        Returns:
            Scheduled workflow ID
        """
        try:
            if not self.temporal_client:
                raise RuntimeError("Temporal client not available")

            workflow_id = f"review-{action}-{datetime.utcnow().timestamp()}"

            handle = await self.temporal_client.start_workflow(
                "PeriodicPolicyReview",
                args=[action, metadata, interval_hours],
                id=workflow_id,
                task_queue=self.task_queue,
            )

            logger.info(
                f"Scheduled periodic review for {action} "
                f"every {interval_hours}h: {workflow_id}"
            )
            return workflow_id

        except Exception as e:
            logger.error(f"Error scheduling periodic review: {e}", exc_info=True)
            raise

    async def enforce_time_bounded_policy(
        self,
        action: str,
        metadata: dict[str, Any],
        valid_until: datetime
    ) -> dict[str, Any]:
        """
        Enforce time-bounded policy that expires at specified time.

        Args:
            action: Action to validate
            metadata: Action metadata
            valid_until: Expiration timestamp

        Returns:
            Enforcement result
        """
        try:
            now = datetime.utcnow()

            if now > valid_until:
                logger.warning(f"Time-bounded policy expired for {action}")
                return {
                    "allowed": False,
                    "reason": f"Policy expired at {valid_until.isoformat()}",
                    "timestamp": now.isoformat(),
                }

            # Calculate remaining time
            remaining = (valid_until - now).total_seconds()

            # Enforce with remaining time as timeout
            result = await self.enforce_with_timeout(
                action,
                metadata,
                timeout_seconds=int(remaining)
            )

            result["expires_at"] = valid_until.isoformat()
            result["remaining_seconds"] = remaining

            return result

        except Exception as e:
            logger.error(f"Error in time-bounded enforcement: {e}", exc_info=True)
            return {
                "allowed": False,
                "reason": f"Time-bounded enforcement error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _local_enforcement(
        self,
        action: str,
        metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Fallback local enforcement when Temporal is unavailable.

        Args:
            action: Action to validate
            metadata: Action metadata

        Returns:
            Local enforcement result
        """
        # Basic risk-based decision
        risk_level = metadata.get("risk_level", 0)

        if risk_level > 3:
            return {
                "allowed": False,
                "reason": f"High risk level {risk_level} in local mode",
                "timestamp": datetime.utcnow().isoformat(),
                "fallback": True,
            }

        return {
            "allowed": True,
            "reason": "Allowed by local enforcement",
            "timestamp": datetime.utcnow().isoformat(),
            "fallback": True,
        }

    async def get_enforcement_history(
        self,
        action: str,
        lookback_hours: int = 24
    ) -> list[dict[str, Any]]:
        """
        Get enforcement history for an action.

        Args:
            action: Action to query
            lookback_hours: Hours to look back

        Returns:
            List of historical enforcement decisions
        """
        try:
            workflow_id = self.workflow_cache.get(action)
            if not workflow_id or not self.temporal_client:
                return []

            handle = self.temporal_client.get_workflow_handle(workflow_id)

            history = await handle.query(
                "get_enforcement_history",
                args=[lookback_hours]
            )

            return history or []

        except Exception as e:
            logger.error(f"Error getting enforcement history: {e}", exc_info=True)
            return []

    async def cleanup_expired_workflows(self, max_age_days: int = 30) -> int:
        """
        Clean up expired workflow data.

        Args:
            max_age_days: Maximum age of workflows to keep

        Returns:
            Number of workflows cleaned up
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=max_age_days)
            cleaned = 0

            for action, workflow_id in list(self.workflow_cache.items()):
                # Extract timestamp from workflow_id
                # Expected format: <action>-<timestamp>
                try:
                    timestamp_str = workflow_id.split("-")[-1]
                    timestamp = datetime.fromtimestamp(float(timestamp_str))

                    if timestamp < cutoff:
                        del self.workflow_cache[action]
                        cleaned += 1
                except (ValueError, IndexError) as parse_error:
                    # Log parse failures to detect format changes
                    logger.warning(
                        f"Failed to parse timestamp from workflow_id '{workflow_id}': {parse_error}. "
                        f"Expected format: <action>-<timestamp>"
                    )
                    continue

            logger.info(f"Cleaned up {cleaned} expired workflows")
            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning up workflows: {e}", exc_info=True)
            return 0


__all__ = ["TemporalLawEnforcer"]
