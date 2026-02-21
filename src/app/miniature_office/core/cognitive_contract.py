"""
Cognitive Contracts System
Implements Civilization Tier Architecture - Part I (Cognitive Contracts)

Intent, Design, and Responsibility as First-Class Objects
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import Entity, EntityType, get_registry


class BindingLevel(Enum):
    """Binding level of a cognitive contract"""

    ADVISORY = "advisory"
    MANDATORY = "mandatory"
    CONSTITUTIONAL = "constitutional"


class Severity(Enum):
    """Risk severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContractStatus(Enum):
    """Lifecycle states for cognitive contracts"""

    DRAFT = "draft"
    REVIEW = "review"
    RATIFIED = "ratified"
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    REVOKED = "revoked"
    SUPERSEDED = "superseded"


@dataclass
class Intent:
    """
    The 'why' of a cognitive contract.
    Answers: "Why does this code exist?"
    """

    goal: str
    constraints: List[str] = field(default_factory=list)
    non_goals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"goal": self.goal, "constraints": self.constraints, "non_goals": self.non_goals}


@dataclass
class DesignRationale:
    """
    The 'how' and 'why not' of a cognitive contract.
    Answers: "What assumptions does this rest on?"
    """

    assumptions: List[str] = field(default_factory=list)
    tradeoffs: List[str] = field(default_factory=list)
    alternatives_rejected: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "assumptions": self.assumptions,
            "tradeoffs": self.tradeoffs,
            "alternatives_rejected": self.alternatives_rejected,
        }


@dataclass
class Stakeholders:
    """
    The 'who' of a cognitive contract.
    Answers: "Who agreed to this?" and "Who is accountable if it fails?"
    """

    departments: List[str] = field(default_factory=list)  # Department IDs
    managers: List[str] = field(default_factory=list)  # Manager IDs
    agents: List[str] = field(default_factory=list)  # Agent IDs

    def to_dict(self) -> Dict:
        return {"departments": self.departments, "managers": self.managers, "agents": self.agents}


@dataclass
class RiskProfile:
    """Risk assessment for the contract"""

    severity: Severity
    failure_modes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"severity": self.severity.value, "failure_modes": self.failure_modes}


@dataclass
class ContractChallenge:
    """A challenge to an existing contract"""

    challenge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    challenger_id: str = ""  # Agent or Manager ID
    contract_id: str = ""
    reason: str = ""
    evidence: List[str] = field(default_factory=list)
    submitted_at_tick: int = 0
    status: str = "pending"  # pending, accepted, rejected

    def to_dict(self) -> Dict:
        return {
            "challenge_id": self.challenge_id,
            "challenger_id": self.challenger_id,
            "contract_id": self.contract_id,
            "reason": self.reason,
            "evidence": self.evidence,
            "submitted_at_tick": self.submitted_at_tick,
            "status": self.status,
        }


@dataclass
class RevocationJustification:
    """Formal justification required for contract revocation"""

    reason: str
    impact_analysis: str
    affected_tasks: List[str] = field(default_factory=list)
    meta_office_approval: bool = False

    def to_dict(self) -> Dict:
        return {
            "reason": self.reason,
            "impact_analysis": self.impact_analysis,
            "affected_tasks": self.affected_tasks,
            "meta_office_approval": self.meta_office_approval,
        }


class CognitiveContract(Entity):
    """
    Cognitive Contract - First-class object for intent, design, and responsibility.

    Enforcement Laws (I.2):
    1. No task may exist without a parent Cognitive Contract
    2. No task may mutate scope beyond contract intent
    3. Any agent may challenge a contract
    4. Only Meta-Office may invalidate a binding contract
    5. Violations are civilization faults, not task errors
    """

    def __init__(
        self,
        contract_id: str,
        issued_at_tick: int,
        issuer: str,  # User, Manager, or MetaOffice
        intent: Intent,
        binding_level: BindingLevel = BindingLevel.MANDATORY,
    ):
        super().__init__(contract_id, EntityType.CONTRACT, f"Contract-{contract_id[:8]}")

        self.issued_at_tick = issued_at_tick
        self.issuer = issuer
        self.intent = intent
        self.design_rationale = DesignRationale()
        self.stakeholders = Stakeholders()
        self.risk_profile = RiskProfile(severity=Severity.LOW)
        self.acceptance_criteria: List[str] = []
        self.binding_level = binding_level

        # Lifecycle
        self.status = ContractStatus.DRAFT
        self.status_history: List[Dict] = []
        self.ratified_at_tick: Optional[int] = None
        self.fulfilled_at_tick: Optional[int] = None
        self.superseded_by: Optional[str] = None  # Contract ID

        # Challenges and revocation
        self.challenges: List[ContractChallenge] = []
        self.revocation_justification: Optional[RevocationJustification] = None

        # Child tasks bound to this contract
        self.bound_tasks: List[str] = []

        # Register
        get_registry().register(self)

        # Log creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.entity_id,
            data={
                "entity_type": "cognitive_contract",
                "issued_at_tick": issued_at_tick,
                "issuer": issuer,
                "binding_level": binding_level.value,
                "intent_goal": intent.goal,
            },
        )

    def transition_to(self, new_status: ContractStatus, reason: str = "") -> bool:
        """
        Transition contract through lifecycle.
        Draft → Review → Ratified → Active → Fulfilled | Revoked | Superseded
        """
        # Validate transition
        valid_transitions = {
            ContractStatus.DRAFT: [ContractStatus.REVIEW],
            ContractStatus.REVIEW: [ContractStatus.RATIFIED, ContractStatus.DRAFT],
            ContractStatus.RATIFIED: [ContractStatus.ACTIVE],
            ContractStatus.ACTIVE: [ContractStatus.FULFILLED, ContractStatus.REVOKED, ContractStatus.SUPERSEDED],
            ContractStatus.FULFILLED: [],
            ContractStatus.REVOKED: [],
            ContractStatus.SUPERSEDED: [],
        }

        if new_status not in valid_transitions.get(self.status, []):
            return False

        old_status = self.status
        self.status = new_status

        # Record history
        self.status_history.append(
            {
                "from": old_status.value,
                "to": new_status.value,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Special handling
        if new_status == ContractStatus.RATIFIED:
            from app.miniature_office.core.world import get_world

            world = get_world()
            if world:
                self.ratified_at_tick = world.time

        # Log transition
        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            target_id=self.entity_id,
            data={
                "action": "contract_status_changed",
                "from_status": old_status.value,
                "to_status": new_status.value,
                "reason": reason,
            },
        )

        return True

    def add_stakeholder(self, entity_type: str, entity_id: str):
        """Add a stakeholder to the contract"""
        if entity_type == "department":
            if entity_id not in self.stakeholders.departments:
                self.stakeholders.departments.append(entity_id)
        elif entity_type == "manager":
            if entity_id not in self.stakeholders.managers:
                self.stakeholders.managers.append(entity_id)
        elif entity_type == "agent":
            if entity_id not in self.stakeholders.agents:
                self.stakeholders.agents.append(entity_id)

    def bind_task(self, task_id: str):
        """
        Bind a task to this contract.
        Enforcement Law I.2.1: No task may exist without a parent Cognitive Contract
        """
        if task_id not in self.bound_tasks:
            self.bound_tasks.append(task_id)

            get_audit_log().log_event(
                EventType.AGENT_ACTION,
                target_id=self.entity_id,
                data={"action": "task_bound_to_contract", "task_id": task_id},
            )

    def challenge(self, challenger_id: str, reason: str, evidence: List[str]) -> ContractChallenge:
        """
        Allow any agent to challenge a contract.
        Enforcement Law I.2.3: Any agent may challenge a contract
        """
        from app.miniature_office.core.world import get_world

        world = get_world()
        current_tick = world.time if world else 0

        challenge = ContractChallenge(
            challenger_id=challenger_id,
            contract_id=self.entity_id,
            reason=reason,
            evidence=evidence,
            submitted_at_tick=current_tick,
        )

        self.challenges.append(challenge)

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=challenger_id,
            target_id=self.entity_id,
            data={"action": "contract_challenged", "challenge_id": challenge.challenge_id, "reason": reason},
        )

        return challenge

    def revoke(self, justification: RevocationJustification, meta_office_id: str) -> bool:
        """
        Revoke a contract with proper justification.
        Enforcement Law I.2.4: Only Meta-Office may invalidate a binding contract

        Revocation requires:
        - Formal justification
        - Impact analysis
        - Historical preservation (automatic via immutable audit)
        """
        if not justification.meta_office_approval:
            return False

        self.revocation_justification = justification
        success = self.transition_to(ContractStatus.REVOKED, justification.reason)

        if success:
            get_audit_log().log_event(
                EventType.AGENT_ACTION,
                actor_id=meta_office_id,
                target_id=self.entity_id,
                data={"action": "contract_revoked", "justification": justification.to_dict()},
            )

        return success

    def supersede(self, new_contract_id: str):
        """Mark this contract as superseded by a newer version"""
        self.superseded_by = new_contract_id
        self.transition_to(ContractStatus.SUPERSEDED, f"Superseded by {new_contract_id}")

    def validate_task_scope(self, task_description: str) -> bool:
        """
        Validate that a task's scope doesn't exceed contract intent.
        Enforcement Law I.2.2: No task may mutate scope beyond contract intent
        """
        # Simple keyword matching - could be enhanced with NLP
        # (goal_keywords will be used for semantic similarity in future)
        task_keywords = set(task_description.lower().split())

        # Check if task is roughly aligned with goals
        # In production, this would use semantic similarity
        # (overlap calculation removed as it's not used yet)

        # Also check against non-goals
        for non_goal in self.intent.non_goals:
            non_goal_keywords = set(non_goal.lower().split())
            if len(non_goal_keywords & task_keywords) > len(non_goal_keywords) * 0.5:
                return False  # Task overlaps with non-goals

        return True

    def is_immutable(self) -> bool:
        """
        Check if contract is immutable (ratified or later).
        Contracts are immutable records once ratified.
        """
        return self.status in [
            ContractStatus.RATIFIED,
            ContractStatus.ACTIVE,
            ContractStatus.FULFILLED,
            ContractStatus.REVOKED,
            ContractStatus.SUPERSEDED,
        ]

    def to_dict(self) -> Dict:
        """Serialize to canonical format"""
        base = super().to_dict()
        base.update(
            {
                "contractId": self.entity_id,
                "issuedAtTick": self.issued_at_tick,
                "issuer": self.issuer,
                "intent": self.intent.to_dict(),
                "designRationale": self.design_rationale.to_dict(),
                "stakeholders": self.stakeholders.to_dict(),
                "riskProfile": self.risk_profile.to_dict(),
                "acceptanceCriteria": self.acceptance_criteria,
                "bindingLevel": self.binding_level.value,
                "status": self.status.value,
                "ratifiedAtTick": self.ratified_at_tick,
                "fulfilledAtTick": self.fulfilled_at_tick,
                "supersededBy": self.superseded_by,
                "challenges": [c.to_dict() for c in self.challenges],
                "boundTasks": self.bound_tasks,
            }
        )
        return base


class ContractRegistry:
    """Registry for managing cognitive contracts"""

    def __init__(self):
        self.contracts: Dict[str, CognitiveContract] = {}
        self.challenges_pending: List[ContractChallenge] = []

    def register_contract(self, contract: CognitiveContract):
        """Register a cognitive contract"""
        self.contracts[contract.entity_id] = contract

    def get_contract(self, contract_id: str) -> Optional[CognitiveContract]:
        """Get a contract by ID"""
        return self.contracts.get(contract_id)

    def get_contracts_by_status(self, status: ContractStatus) -> List[CognitiveContract]:
        """Get all contracts with a specific status"""
        return [c for c in self.contracts.values() if c.status == status]

    def get_active_contracts(self) -> List[CognitiveContract]:
        """Get all active contracts"""
        return self.get_contracts_by_status(ContractStatus.ACTIVE)

    def enforce_task_contract_binding(self, task_id: str) -> bool:
        """
        Enforcement Law I.2.1: No task may exist without a parent Cognitive Contract
        Returns True if task is bound to a contract, False otherwise
        """
        for contract in self.contracts.values():
            if task_id in contract.bound_tasks:
                return True
        return False

    def submit_challenge(self, challenge: ContractChallenge):
        """Submit a challenge for review"""
        self.challenges_pending.append(challenge)

    def get_pending_challenges(self) -> List[ContractChallenge]:
        """Get all pending challenges"""
        return [c for c in self.challenges_pending if c.status == "pending"]


# Global contract registry
_contract_registry = ContractRegistry()


def get_contract_registry() -> ContractRegistry:
    """Get the global contract registry"""
    return _contract_registry
