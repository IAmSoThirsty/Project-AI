"""
Policy Scheduler
================

Dynamic policy scheduling for time-based and condition-based policy enforcement.
Provides automated policy transitions and scheduled reviews.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class ScheduledPolicy:
    """Represents a scheduled policy activation."""

    def __init__(
        self,
        policy_id: str,
        policy_data: dict[str, Any],
        activation_time: datetime,
        expiration_time: datetime | None = None,
        conditions: dict[str, Any] | None = None
    ):
        """
        Initialize scheduled policy.

        Args:
            policy_id: Unique policy identifier
            policy_data: Policy configuration
            activation_time: When policy activates
            expiration_time: Optional expiration time
            conditions: Optional activation conditions
        """
        self.policy_id = policy_id
        self.policy_data = policy_data
        self.activation_time = activation_time
        self.expiration_time = expiration_time
        self.conditions = conditions or {}
        self.is_active = False
        self.activation_count = 0


class PolicyScheduler:
    """
    Dynamic policy scheduler for time-based and conditional policy enforcement.
    Enables automatic policy transitions and scheduled reviews.
    """

    def __init__(self):
        """Initialize policy scheduler."""
        self.scheduled_policies: dict[str, ScheduledPolicy] = {}
        self.active_policies: set[str] = set()
        self.policy_history: list[dict[str, Any]] = []
        self.policy_callbacks: dict[str, list[Callable]] = {}
        self._scheduler_task: asyncio.Task | None = None
        logger.info("Policy scheduler initialized")

    def schedule_policy(
        self,
        policy_id: str,
        policy_data: dict[str, Any],
        activation_time: datetime,
        expiration_time: datetime | None = None,
        conditions: dict[str, Any] | None = None
    ) -> None:
        """
        Schedule a policy for future activation.

        Args:
            policy_id: Unique policy identifier
            policy_data: Policy configuration
            activation_time: When to activate policy
            expiration_time: Optional expiration time
            conditions: Optional activation conditions
        """
        try:
            scheduled = ScheduledPolicy(
                policy_id=policy_id,
                policy_data=policy_data,
                activation_time=activation_time,
                expiration_time=expiration_time,
                conditions=conditions
            )

            self.scheduled_policies[policy_id] = scheduled

            logger.info(
                f"Scheduled policy '{policy_id}' "
                f"for {activation_time.isoformat()}"
            )

        except Exception as e:
            logger.error(f"Error scheduling policy: {e}", exc_info=True)

    def schedule_recurring_policy(
        self,
        policy_id: str,
        policy_data: dict[str, Any],
        interval_hours: int,
        duration_hours: int = 1,
        start_time: datetime | None = None
    ) -> None:
        """
        Schedule a recurring policy activation.

        Args:
            policy_id: Policy identifier
            policy_data: Policy configuration
            interval_hours: Hours between activations
            duration_hours: Duration of each activation
            start_time: Optional start time (default: now)
        """
        try:
            start = start_time or datetime.utcnow()

            # Schedule next 30 days of recurrences
            current = start
            end = start + timedelta(days=30)

            recurrence_count = 0
            while current < end:
                activation = current
                expiration = current + timedelta(hours=duration_hours)

                recurring_id = f"{policy_id}_recurring_{recurrence_count}"

                self.schedule_policy(
                    policy_id=recurring_id,
                    policy_data=policy_data,
                    activation_time=activation,
                    expiration_time=expiration
                )

                current += timedelta(hours=interval_hours)
                recurrence_count += 1

            logger.info(
                f"Scheduled {recurrence_count} recurrences of policy '{policy_id}'"
            )

        except Exception as e:
            logger.error(f"Error scheduling recurring policy: {e}", exc_info=True)

    async def start_scheduler(self) -> None:
        """Start the policy scheduler background task."""
        if self._scheduler_task:
            logger.warning("Scheduler already running")
            return

        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Policy scheduler started")

    async def stop_scheduler(self) -> None:
        """Stop the policy scheduler background task."""
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None
            logger.info("Policy scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        try:
            while True:
                await self._process_scheduled_policies()
                await asyncio.sleep(60)  # Check every minute
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)

    async def _process_scheduled_policies(self) -> None:
        """Process scheduled policies for activation/expiration."""
        try:
            now = datetime.utcnow()

            for policy_id, scheduled in list(self.scheduled_policies.items()):
                # Check for activation
                if not scheduled.is_active and now >= scheduled.activation_time:
                    if self._check_conditions(scheduled.conditions):
                        await self._activate_policy(scheduled)

                # Check for expiration
                if scheduled.is_active and scheduled.expiration_time:
                    if now >= scheduled.expiration_time:
                        await self._deactivate_policy(scheduled)

        except Exception as e:
            logger.error(f"Error processing scheduled policies: {e}", exc_info=True)

    def _check_conditions(self, conditions: dict[str, Any]) -> bool:
        """Check if policy activation conditions are met."""
        if not conditions:
            return True

        # Example condition checks
        # In practice, this would evaluate complex conditions

        if "min_build_count" in conditions:
            # Would check against actual build count
            return True

        if "security_level" in conditions:
            # Would check against current security level
            return True

        return True

    async def _activate_policy(self, scheduled: ScheduledPolicy) -> None:
        """Activate a scheduled policy."""
        try:
            scheduled.is_active = True
            scheduled.activation_count += 1
            self.active_policies.add(scheduled.policy_id)

            self._record_policy_event(
                scheduled.policy_id,
                "activated",
                scheduled.policy_data
            )

            # Execute callbacks
            await self._execute_callbacks(scheduled.policy_id, "activate")

            logger.info(f"Activated policy: {scheduled.policy_id}")

        except Exception as e:
            logger.error(f"Error activating policy: {e}", exc_info=True)

    async def _deactivate_policy(self, scheduled: ScheduledPolicy) -> None:
        """Deactivate a scheduled policy."""
        try:
            scheduled.is_active = False
            self.active_policies.discard(scheduled.policy_id)

            self._record_policy_event(
                scheduled.policy_id,
                "deactivated",
                scheduled.policy_data
            )

            # Execute callbacks
            await self._execute_callbacks(scheduled.policy_id, "deactivate")

            logger.info(f"Deactivated policy: {scheduled.policy_id}")

        except Exception as e:
            logger.error(f"Error deactivating policy: {e}", exc_info=True)

    def register_callback(
        self,
        policy_id: str,
        callback: Callable
    ) -> None:
        """
        Register callback for policy events.

        Args:
            policy_id: Policy to monitor
            callback: Async callback function
        """
        if policy_id not in self.policy_callbacks:
            self.policy_callbacks[policy_id] = []

        self.policy_callbacks[policy_id].append(callback)
        logger.debug(f"Registered callback for policy: {policy_id}")

    async def _execute_callbacks(
        self,
        policy_id: str,
        event_type: str
    ) -> None:
        """Execute callbacks for policy event."""
        callbacks = self.policy_callbacks.get(policy_id, [])

        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(policy_id, event_type)
                else:
                    callback(policy_id, event_type)
            except Exception as e:
                logger.error(f"Error executing callback: {e}", exc_info=True)

    def get_active_policies(self) -> list[dict[str, Any]]:
        """
        Get currently active policies.

        Returns:
            List of active policy data
        """
        active = []
        for policy_id in self.active_policies:
            scheduled = self.scheduled_policies.get(policy_id)
            if scheduled:
                active.append({
                    "policy_id": policy_id,
                    "policy_data": scheduled.policy_data,
                    "activation_time": scheduled.activation_time.isoformat(),
                    "expiration_time": (
                        scheduled.expiration_time.isoformat()
                        if scheduled.expiration_time else None
                    ),
                    "activation_count": scheduled.activation_count,
                })

        return active

    def get_upcoming_policies(
        self,
        hours_ahead: int = 24
    ) -> list[dict[str, Any]]:
        """
        Get policies scheduled for future activation.

        Args:
            hours_ahead: Hours to look ahead

        Returns:
            List of upcoming policies
        """
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=hours_ahead)

        upcoming = []
        for scheduled in self.scheduled_policies.values():
            if not scheduled.is_active and scheduled.activation_time <= cutoff:
                upcoming.append({
                    "policy_id": scheduled.policy_id,
                    "policy_data": scheduled.policy_data,
                    "activation_time": scheduled.activation_time.isoformat(),
                    "time_until_activation": (
                        scheduled.activation_time - now
                    ).total_seconds() / 3600,  # hours
                })

        # Sort by activation time
        upcoming.sort(key=lambda x: x["activation_time"])

        return upcoming

    def _record_policy_event(
        self,
        policy_id: str,
        event_type: str,
        policy_data: dict[str, Any]
    ) -> None:
        """Record policy event to history."""
        self.policy_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "policy_id": policy_id,
            "event_type": event_type,
            "policy_data": policy_data,
        })

        # Keep last 10000 events
        if len(self.policy_history) > 10000:
            self.policy_history = self.policy_history[-10000:]

    def get_policy_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get policy event history.

        Args:
            limit: Maximum number of events

        Returns:
            List of policy events
        """
        return self.policy_history[-limit:]


__all__ = ["PolicyScheduler", "ScheduledPolicy"]
