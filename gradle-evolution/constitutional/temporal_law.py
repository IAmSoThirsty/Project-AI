#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Temporal Law Enforcement
========================

Integrates Temporal workflows with constitutional policy enforcement.
Provides time-bound policy evaluation and workflow-based governance.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from temporalio.client import Client

logger = logging.getLogger(__name__)


def _utc_now_naive() -> datetime:
    """Return naive UTC datetime for compatibility comparisons."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TemporalLaw:
    """Time-bounded constitutional rule set."""

    def __init__(
        self,
        law_id: str,
        effective_from: str | datetime,
        effective_until: str | datetime | None = None,
        description: str = "",
        rules: list[dict[str, Any]] | None = None,
    ):
        self.law_id = law_id
        self.effective_from = self._coerce_datetime(effective_from)
        self.effective_until = (
            self._coerce_datetime(effective_until) if effective_until else None
        )
        self.description = description
        self.rules = rules or []

    @staticmethod
    def _coerce_datetime(value: str | datetime | None) -> datetime:
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        if value is None:
            return _utc_now_naive()
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(
            tzinfo=None
        )

    def is_active(self, at: datetime | None = None) -> bool:
        now = at.replace(tzinfo=None) if isinstance(at, datetime) and at.tzinfo else (at or _utc_now_naive())
        if now < self.effective_from:
            return False
        if self.effective_until and now > self.effective_until:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "law_id": self.law_id,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat() if self.effective_until else None
            ),
            "description": self.description,
            "rules": self.rules,
        }


class TemporalLawRegistry:
    """Persistent registry for temporal constitutional laws."""

    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.laws: dict[str, TemporalLaw] = {}

    def register_law(self, law: TemporalLaw) -> None:
        self.laws[law.law_id] = law

    def get_active_laws(self, at: datetime | None = None) -> list[TemporalLaw]:
        now = at or _utc_now_naive()
        now = now.replace(tzinfo=None) if now.tzinfo else now
        return [law for law in self.laws.values() if law.is_active(now)]

    def revoke_law(self, law_id: str) -> bool:
        if law_id in self.laws:
            del self.laws[law_id]
            return True
        return False

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {law_id: law.to_dict() for law_id, law in self.laws.items()}
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.storage_path.exists():
            return
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self.laws = {
            law_id: TemporalLaw(**law_payload)
            for law_id, law_payload in data.items()
        }


class TemporalLawEnforcer:
    """
    Enforces constitutional policies through Temporal workflows.
    Enables time-travel debugging and temporal policy queries.
    """

    def __init__(
        self,
        temporal_client: Client | None = None,
        task_queue: str = "constitutional-enforcement",
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
        logger.info("Temporal law enforcer initialized with queue: %s", task_queue)

    async def enforce_with_timeout(
        self, action: str, metadata: dict[str, Any], timeout_seconds: int = 30
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
            result = await asyncio.wait_for(handle.result(), timeout=timeout_seconds)

            logger.info("Temporal enforcement completed: %s", action)
            return result

        except TimeoutError:
            logger.error("Enforcement timeout for action: %s", action)
            return {
                "allowed": False,
                "reason": f"Policy enforcement timeout ({timeout_seconds}s)",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error("Error in temporal enforcement: %s", e, exc_info=True)
            return {
                "allowed": False,
                "reason": f"Enforcement error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def query_historical_decision(
        self, action: str, timestamp: datetime
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
                logger.warning("No workflow found for action: %s", action)
                return None

            handle = self.temporal_client.get_workflow_handle(workflow_id)

            # Query workflow at specific time
            result = await handle.query(
                "get_decision_at_time", args=[timestamp.isoformat()]
            )

            logger.debug("Historical query result for %s: %s", action, result)
            return result

        except Exception as e:
            logger.error("Error querying historical decision: %s", e, exc_info=True)
            return None

    async def schedule_periodic_review(
        self, action: str, metadata: dict[str, Any], interval_hours: int = 24
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

            await self.temporal_client.start_workflow(
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
            logger.error("Error scheduling periodic review: %s", e, exc_info=True)
            raise

    async def enforce_time_bounded_policy(
        self, action: str, metadata: dict[str, Any], valid_until: datetime
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
                logger.warning("Time-bounded policy expired for %s", action)
                return {
                    "allowed": False,
                    "reason": f"Policy expired at {valid_until.isoformat()}",
                    "timestamp": now.isoformat(),
                }

            # Calculate remaining time
            remaining = (valid_until - now).total_seconds()

            # Enforce with remaining time as timeout
            result = await self.enforce_with_timeout(
                action, metadata, timeout_seconds=int(remaining)
            )

            result["expires_at"] = valid_until.isoformat()
            result["remaining_seconds"] = remaining

            return result

        except Exception as e:
            logger.error("Error in time-bounded enforcement: %s", e, exc_info=True)
            return {
                "allowed": False,
                "reason": f"Time-bounded enforcement error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _local_enforcement(
        self, action: str, metadata: dict[str, Any]
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
        self, action: str, lookback_hours: int = 24
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
                "get_enforcement_history", args=[lookback_hours]
            )

            return history or []

        except Exception as e:
            logger.error("Error getting enforcement history: %s", e, exc_info=True)
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

            logger.info("Cleaned up %s expired workflows", cleaned)
            return cleaned

        except Exception as e:
            logger.error("Error cleaning up workflows: %s", e, exc_info=True)
            return 0


__all__ = ["TemporalLaw", "TemporalLawRegistry", "TemporalLawEnforcer"]
