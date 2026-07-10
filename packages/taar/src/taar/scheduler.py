"""Schedule admissibility helpers.

TAAR first swarm executes manually or via OS schedulers (Windows Task
Scheduler / cron). This module answers one question: does the schedule
and facility mode permit this agent to run right now? It does not spawn
processes and it does not loop — the commander tier is a later swarm.
"""

from __future__ import annotations

from taar.config import TaarConfig
from taar.models import AgentSpec
from taar.registry import Registry


def schedule_allows(agent: AgentSpec, config: TaarConfig, registry: Registry) -> tuple[bool, str]:
    schedule = registry.schedules_by_id.get(agent.schedule_id)
    if schedule is None:
        return False, f"unknown schedule {agent.schedule_id}"
    if not schedule.enabled:
        return False, f"schedule {schedule.id} disabled"
    mode = config.facility_mode
    if mode in schedule.blocked_facility_modes:
        return False, f"facility mode {mode} blocks schedule {schedule.id}"
    if schedule.allowed_facility_modes and mode not in schedule.allowed_facility_modes:
        return False, f"facility mode {mode} not allowed by schedule {schedule.id}"
    return True, "allowed"
