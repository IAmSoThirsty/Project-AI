"""
Task Lifecycle and Mission Logic System
Implements Codex Sections 2 (Mission Logic) and 4 (Operational Workflows)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional

from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import Entity, EntityType


class TaskState(Enum):
    """Task lifecycle states (Codex 4.1)"""

    SCHEDULED = "scheduled"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    APPROVAL = "approval"
    MERGED = "merged"
    DEPLOYED = "deployed"


class DirectiveLevel(Enum):
    """Levels in the directive tree (Codex 2.1)"""

    USER_INTENT = "user_intent"
    ARCHITECT_INTENT = "architect_intent"
    TASK_NODE = "task_node"


@dataclass
class AcceptanceCriteria:
    """Acceptance criteria for a directive or task"""

    criteria_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    validator: Optional[Callable[[], bool]] = None
    is_met: bool = False
    checked_at: Optional[datetime] = None

    def check(self) -> bool:
        """Check if criteria is met"""
        if self.validator:
            self.is_met = self.validator()
        self.checked_at = datetime.now(timezone.utc)
        return self.is_met


@dataclass
class Condition:
    """Precondition or postcondition for a directive"""

    condition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    checker: Optional[Callable[[], bool]] = None
    is_satisfied: bool = False

    def check(self) -> bool:
        """Check if condition is satisfied"""
        if self.checker:
            self.is_satisfied = self.checker()
        return self.is_satisfied


class Directive(Entity):
    """
    Directive in the directive tree (Codex 2.1).
    Highest node: User Intent
    Intermediate: Architect Intent
    Lowest: Task Nodes
    """

    def __init__(
        self,
        directive_id: str,
        name: str,
        level: DirectiveLevel,
        description: str = "",
        parent_directive_id: Optional[str] = None,
    ):
        super().__init__(directive_id, EntityType.ARTIFACT, name)
        self.level = level
        self.description = description
        self.parent_directive_id = parent_directive_id
        self.child_directives: List[str] = []

        # Directive formalism (Codex 2.1)
        self.preconditions: List[Condition] = []
        self.postconditions: List[Condition] = []
        self.acceptance_criteria: List[AcceptanceCriteria] = []

        # Log creation
        get_audit_log().log_event(
            EventType.DIRECTIVE_CREATED,
            target_id=self.entity_id,
            data={
                "level": level.value,
                "description": description,
                "parent_directive_id": parent_directive_id,
            },
        )

    def add_precondition(
        self, description: str, checker: Optional[Callable] = None
    ) -> Condition:
        """Add a precondition"""
        condition = Condition(description=description, checker=checker)
        self.preconditions.append(condition)
        return condition

    def add_postcondition(
        self, description: str, checker: Optional[Callable] = None
    ) -> Condition:
        """Add a postcondition"""
        condition = Condition(description=description, checker=checker)
        self.postconditions.append(condition)
        return condition

    def add_acceptance_criterion(
        self, description: str, validator: Optional[Callable] = None
    ) -> AcceptanceCriteria:
        """Add an acceptance criterion"""
        criterion = AcceptanceCriteria(description=description, validator=validator)
        self.acceptance_criteria.append(criterion)
        return criterion

    def check_preconditions(self) -> bool:
        """Check if all preconditions are satisfied"""
        return all(cond.check() for cond in self.preconditions)

    def check_postconditions(self) -> bool:
        """Check if all postconditions are satisfied"""
        return all(cond.check() for cond in self.postconditions)

    def check_acceptance(self) -> bool:
        """Check if all acceptance criteria are met"""
        return all(criterion.check() for criterion in self.acceptance_criteria)

    def is_ready_for_commit(self) -> bool:
        """
        Tasks are only committed to output when all criteria pass (Codex 2.1)
        """
        return (
            self.check_preconditions()
            and self.check_postconditions()
            and self.check_acceptance()
        )


class Task(Directive):
    """
    Task with full lifecycle management (Codex 4.1).
    Tasks are the lowest level of directives.
    """

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str = "",
        parent_directive_id: Optional[str] = None,
        assigned_agent_id: Optional[str] = None,
    ):
        super().__init__(
            task_id, name, DirectiveLevel.TASK_NODE, description, parent_directive_id
        )
        self.state = TaskState.SCHEDULED
        self.assigned_agent_id = assigned_agent_id
        self.blocked_reason: Optional[str] = None
        self.state_history: List[Dict] = []
        self.ambiguity_score: float = 0.0

        self._record_state_change(TaskState.SCHEDULED, "Task created")

    def _record_state_change(self, new_state: TaskState, reason: str):
        """Record state change in history and audit log"""
        old_state = self.state if hasattr(self, "state") else None
        self.state = new_state

        change_record = {
            "from_state": old_state.value if old_state else None,
            "to_state": new_state.value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.state_history.append(change_record)

        get_audit_log().log_event(
            EventType.TASK_STATE_CHANGED,
            target_id=self.entity_id,
            actor_id=self.assigned_agent_id,
            data=change_record,
        )

    def can_transition_to(self, new_state: TaskState) -> bool:
        """
        Check if transition to new state is valid.
        Movement only when all prerequisite states resolved (Codex 4.1)
        """
        valid_transitions = {
            TaskState.SCHEDULED: [TaskState.IN_REVIEW, TaskState.BLOCKED],
            TaskState.IN_REVIEW: [
                TaskState.BLOCKED,
                TaskState.APPROVAL,
                TaskState.SCHEDULED,
            ],
            TaskState.BLOCKED: [TaskState.SCHEDULED, TaskState.IN_REVIEW],
            TaskState.APPROVAL: [
                TaskState.MERGED,
                TaskState.IN_REVIEW,
                TaskState.BLOCKED,
            ],
            TaskState.MERGED: [TaskState.DEPLOYED, TaskState.BLOCKED],
            TaskState.DEPLOYED: [TaskState.BLOCKED],  # Can roll back
        }

        return new_state in valid_transitions.get(self.state, [])

    def transition_to(self, new_state: TaskState, reason: str = "") -> bool:
        """
        Transition to a new state if valid.
        Returns True if transition succeeded.
        """
        if not self.can_transition_to(new_state):
            return False

        # Special checks for certain states
        if new_state == TaskState.APPROVAL:
            if not self.check_postconditions():
                return False

        if new_state == TaskState.MERGED:
            if not self.is_ready_for_commit():
                return False

        self._record_state_change(new_state, reason)
        return True

    def block(self, reason: str):
        """Block the task with a reason"""
        if self.transition_to(TaskState.BLOCKED, reason):
            self.blocked_reason = reason

    def unblock(self):
        """Unblock the task"""
        if self.state == TaskState.BLOCKED:
            self.blocked_reason = None
            self.transition_to(TaskState.SCHEDULED, "Unblocked")

    def set_ambiguity_score(self, score: float):
        """Set the ambiguity score for meeting detection (Codex 4.2)"""
        self.ambiguity_score = max(0.0, min(1.0, score))

    def needs_meeting(self, threshold: float = 0.5) -> bool:
        """
        Check if task ambiguity exceeds threshold requiring a meeting.
        Codex 4.2: Meetings held when task contains ambiguity ≥ threshold
        """
        return self.ambiguity_score >= threshold


@dataclass
class DecisionTranscript:
    """
    First-class stateful object produced by meetings (Codex 4.2)
    """

    transcript_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    meeting_date: datetime = field(default_factory=datetime.utcnow)
    participants: List[str] = field(default_factory=list)  # Agent IDs
    ambiguity_addressed: str = ""
    decisions_made: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    resolution: str = ""

    def to_dict(self) -> Dict:
        return {
            "transcript_id": self.transcript_id,
            "task_id": self.task_id,
            "meeting_date": self.meeting_date.isoformat(),
            "participants": self.participants,
            "ambiguity_addressed": self.ambiguity_addressed,
            "decisions_made": self.decisions_made,
            "action_items": self.action_items,
            "resolution": self.resolution,
        }


class MeetingSystem:
    """
    Meeting system for resolving task ambiguity (Codex 4.2)
    """

    def __init__(self):
        self.transcripts: Dict[str, DecisionTranscript] = {}

    def hold_meeting(
        self,
        task: Task,
        participants: List[str],
        ambiguity_addressed: str,
        decisions_made: List[str],
        resolution: str,
    ) -> DecisionTranscript:
        """
        Hold a meeting and produce a decision transcript.
        Meetings aren't cosmetic - they produce first-class artifacts (Codex 4.2)
        """
        transcript = DecisionTranscript(
            task_id=task.entity_id,
            participants=participants,
            ambiguity_addressed=ambiguity_addressed,
            decisions_made=decisions_made,
            resolution=resolution,
        )

        self.transcripts[transcript.transcript_id] = transcript

        # Log meeting in audit log
        get_audit_log().log_event(
            EventType.MEETING_HELD,
            target_id=task.entity_id,
            data={
                "transcript_id": transcript.transcript_id,
                "participants": participants,
                "resolution": resolution,
            },
        )

        # Reduce task ambiguity after meeting
        task.set_ambiguity_score(0.0)

        return transcript

    def get_transcript(self, transcript_id: str) -> Optional[DecisionTranscript]:
        """Retrieve a meeting transcript"""
        return self.transcripts.get(transcript_id)

    def get_task_transcripts(self, task_id: str) -> List[DecisionTranscript]:
        """Get all transcripts for a task"""
        return [t for t in self.transcripts.values() if t.task_id == task_id]


# Global meeting system
_meeting_system = MeetingSystem()


def get_meeting_system() -> MeetingSystem:
    """Get the global meeting system"""
    return _meeting_system


def get_task_by_id(task_id: str) -> Optional[Task]:
    """Get a task by ID from the entity registry"""
    from app.miniature_office.core.entity import get_registry

    entity = get_registry().get(task_id)
    if entity and isinstance(entity, Task):
        return entity
    return None
