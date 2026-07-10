"""Human approval boundary.

The first swarm has no approvable actions: every action requiring human
approval is denied at admission. This module exists so the boundary is a
named concept, not an implicit gap. There is no auto-approval path."""

from __future__ import annotations

from taar.models import TaskSpec

APPROVAL_REQUIRED_ACTIONS = frozenset(
    {
        "merge",
        "push",
        "publish",
        "deploy",
        "delete",
        "declassify",
        "grant_capability",
        "modify_governance",
        "modify_schedule",
        "apply_patch",
    }
)


def requires_human_approval(task: TaskSpec) -> bool:
    return bool(task.human_approval_required)


def approval_available() -> bool:
    """TAAR has no interactive approval channel. Fail closed."""
    return False
