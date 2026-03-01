"""
Agent System with Capability Profiles and Consensus Mechanism
Implements Codex Sections 2.2 (Consensus Bands) and 3.1 (Teams & Roles)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import (
    Entity,
    EntityType,
    RelationType,
    get_registry,
)
from app.miniature_office.core.mission import Task


class AgentRole(Enum):
    """Agent roles as defined in Codex 3.1"""

    ARCHITECT = "architect"  # Design authority
    BUILDER = "builder"  # Implementation
    VERIFIER = "verifier"  # Correctness
    SECURITY = "security"  # Threat modeling
    DOC_AGENT = "doc_agent"  # Communication
    MANAGER = "manager"  # Meta-agent for consensus


@dataclass
class CapabilityProfile:
    """
    Capability profile for agents (Codex 1.2)
    Defines what an agent can do to avoid ambiguous task assignments
    """

    languages: Set[str] = field(default_factory=set)
    tools: Set[str] = field(default_factory=set)
    domains: Set[str] = field(default_factory=set)
    skills: Set[str] = field(default_factory=set)
    security_clearance: int = 1  # 1-5 scale

    def can_handle_task(self, required_capabilities: Dict[str, Any]) -> bool:
        """Check if agent has required capabilities for a task"""
        if "languages" in required_capabilities:
            required_langs = set(required_capabilities["languages"])
            if not required_langs.issubset(self.languages):
                return False

        if "tools" in required_capabilities:
            required_tools = set(required_capabilities["tools"])
            if not required_tools.issubset(self.tools):
                return False

        if "security_clearance" in required_capabilities:
            if self.security_clearance < required_capabilities["security_clearance"]:
                return False

        return True

    def to_dict(self) -> Dict:
        return {
            "languages": list(self.languages),
            "tools": list(self.tools),
            "domains": list(self.domains),
            "skills": list(self.skills),
            "security_clearance": self.security_clearance,
        }


class Agent(Entity):
    """
    Base agent class with role-specific behaviors.
    All agents are autonomous workers with specific capabilities (Codex 1.1)
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        department_id: Optional[str] = None,
        capabilities: Optional[CapabilityProfile] = None,
    ):
        super().__init__(agent_id, EntityType.AGENT, name)
        self.role = role
        self.department_id = department_id
        self.capabilities = capabilities or CapabilityProfile()
        self.current_task_id: Optional[str] = None
        self.task_history: List[str] = []
        self.status = "idle"  # idle, working, blocked, in_meeting

        # Register agent
        get_registry().register(self)

        # Log creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.entity_id,
            data={
                "entity_type": "agent",
                "role": role.value,
                "department_id": department_id,
            },
        )

    def assign_task(self, task: Task) -> bool:
        """Assign a task to this agent"""
        # Check capability match
        if not self.capabilities.can_handle_task(
            task.metadata.get("required_capabilities", {})
        ):
            return False

        self.current_task_id = task.entity_id
        task.assigned_agent_id = self.entity_id
        self.status = "working"

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=self.entity_id,
            target_id=task.entity_id,
            data={"action": "task_assigned"},
        )

        return True

    def complete_task(self):
        """Mark current task as complete"""
        if self.current_task_id:
            self.task_history.append(self.current_task_id)

            get_audit_log().log_event(
                EventType.AGENT_ACTION,
                actor_id=self.entity_id,
                target_id=self.current_task_id,
                data={"action": "task_completed"},
            )

            self.current_task_id = None
            self.status = "idle"

    def perform_action(
        self, action: str, target_id: Optional[str] = None, data: Optional[Dict] = None
    ):
        """Perform a generic action and log it"""
        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=self.entity_id,
            target_id=target_id,
            data={"action": action, **(data or {})},
        )


class Manager(Agent):
    """
    Manager meta-agent for consensus enforcement (Codex 2.2).
    Managers enforce consensus and verify output readiness.
    """

    def __init__(self, manager_id: str, name: str, department_id: Optional[str] = None):
        super().__init__(manager_id, name, AgentRole.MANAGER, department_id)
        self.managed_agents: List[str] = []

    def add_managed_agent(self, agent: Agent):
        """Add an agent under this manager's supervision"""
        self.managed_agents.append(agent.entity_id)
        self.declare_relationship(agent, RelationType.MANAGES)


@dataclass
class ConsensusVote:
    """A vote in a consensus decision"""

    agent_id: str
    vote: bool  # True = approve, False = reject
    weight: float = 1.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConsensusDecision:
    """
    Result of a consensus process (Codex 2.2)
    """

    subject: str  # What is being decided
    target_id: str  # Entity being voted on
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    votes: List[ConsensusVote] = field(default_factory=list)
    threshold: float = 0.66  # 2/3 majority by default
    outcome: Optional[bool] = None
    override_log: Optional[str] = None  # Nothing silently overrides
    decided_at: Optional[datetime] = None

    def add_vote(
        self, agent_id: str, vote: bool, weight: float = 1.0, reasoning: str = ""
    ):
        """Add a vote to the consensus"""
        consensus_vote = ConsensusVote(
            agent_id=agent_id, vote=vote, weight=weight, reasoning=reasoning
        )
        self.votes.append(consensus_vote)

    def calculate_outcome(self) -> bool:
        """
        Calculate weighted consensus (Codex 2.2)
        Returns True if consensus reached
        """
        if not self.votes:
            return False

        total_weight = sum(v.weight for v in self.votes)
        approve_weight = sum(v.weight for v in self.votes if v.vote)

        approval_ratio = approve_weight / total_weight if total_weight > 0 else 0
        self.outcome = approval_ratio >= self.threshold
        self.decided_at = datetime.utcnow()

        return self.outcome

    def issue_override(self, manager_id: str, reason: str, new_outcome: bool):
        """
        Issue an override (Codex 2.2).
        Nothing ever silently overrides - it must be logged.
        """
        self.override_log = f"Manager {manager_id} overrode decision. Reason: {reason}"
        old_outcome = self.outcome
        self.outcome = new_outcome

        get_audit_log().log_event(
            EventType.OVERRIDE_ISSUED,
            actor_id=manager_id,
            target_id=self.target_id,
            data={
                "decision_id": self.decision_id,
                "old_outcome": old_outcome,
                "new_outcome": new_outcome,
                "reason": reason,
            },
        )

    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "subject": self.subject,
            "target_id": self.target_id,
            "votes": [
                {
                    "agent_id": v.agent_id,
                    "vote": v.vote,
                    "weight": v.weight,
                    "reasoning": v.reasoning,
                }
                for v in self.votes
            ],
            "threshold": self.threshold,
            "outcome": self.outcome,
            "override_log": self.override_log,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
        }


class ConsensusSystem:
    """
    Consensus Band system for conflict resolution (Codex 2.2).
    Implements Manager Review and Weighted Consensus.
    """

    def __init__(self):
        self.decisions: Dict[str, ConsensusDecision] = {}

    def initiate_consensus(
        self, subject: str, target_id: str, threshold: float = 0.66
    ) -> ConsensusDecision:
        """Start a new consensus decision process"""
        decision = ConsensusDecision(
            subject=subject, target_id=target_id, threshold=threshold
        )
        self.decisions[decision.decision_id] = decision
        return decision

    def finalize_consensus(self, decision_id: str) -> bool:
        """
        Finalize a consensus decision and log it.
        Returns the outcome.
        """
        decision = self.decisions.get(decision_id)
        if not decision:
            return False

        outcome = decision.calculate_outcome()

        get_audit_log().log_event(
            EventType.CONSENSUS_REACHED,
            target_id=decision.target_id,
            data={
                "decision_id": decision_id,
                "subject": decision.subject,
                "outcome": outcome,
                "vote_count": len(decision.votes),
            },
        )

        return outcome

    def get_decision(self, decision_id: str) -> Optional[ConsensusDecision]:
        """Retrieve a consensus decision"""
        return self.decisions.get(decision_id)


# Global consensus system
_consensus_system = ConsensusSystem()


def get_consensus_system() -> ConsensusSystem:
    """Get the global consensus system"""
    return _consensus_system
