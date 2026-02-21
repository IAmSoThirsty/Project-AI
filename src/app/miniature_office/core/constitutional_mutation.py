"""
Constitutional Mutation Engine
Implements Civilization Tier Architecture - Part III (Constitutional Mutation)

Controlled Evolution Without Collapse
System can adapt while preserving core safeguards
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from app.miniature_office.core.audit import EventType, get_audit_log


class LawScope(Enum):
    """Scope of constitutional laws"""

    GLOBAL = "global"  # Affects entire system
    DEPARTMENT = "department"  # Affects one department
    OFFICE = "office"  # Affects one office


class EnforcementLevel(Enum):
    """How strictly a law is enforced"""

    SOFT = "soft"  # Advisory, can be overridden with justification
    HARD = "hard"  # Mandatory, cannot be violated
    CONSTITUTIONAL = "constitutional"  # Cannot be changed without special process


class MutationStatus(Enum):
    """Status of a mutation proposal"""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    SIMULATING = "simulating"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    ROLLED_BACK = "rolled_back"


@dataclass
class AmendmentRules:
    """Rules for amending a constitutional law"""

    requires: List[str] = field(default_factory=list)  # e.g., ["MetaOffice", "2/3 Manager Consensus"]
    cooldown_ticks: int = 5000  # Minimum ticks between amendments
    requires_simulation: bool = True
    requires_rollback_path: bool = True

    def to_dict(self) -> Dict:
        return {
            "requires": self.requires,
            "cooldown_ticks": self.cooldown_ticks,
            "requires_simulation": self.requires_simulation,
            "requires_rollback_path": self.requires_rollback_path,
        }


class ConstitutionalLaw:
    """
    Constitutional Law Object (III.1)
    Defines fundamental rules of the system
    """

    def __init__(
        self, law_id: str, scope: LawScope, statement: str, enforcement: EnforcementLevel, introduced_at_tick: int
    ):
        self.law_id = law_id
        self.scope = scope
        self.statement = statement
        self.enforcement = enforcement
        self.introduced_at_tick = introduced_at_tick
        self.amendment_rules = AmendmentRules()
        self.amendment_history: List[Dict] = []
        self.last_amended_tick: Optional[int] = None

        # Log creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.law_id,
            data={
                "entity_type": "constitutional_law",
                "scope": scope.value,
                "statement": statement,
                "enforcement": enforcement.value,
                "introduced_at_tick": introduced_at_tick,
            },
        )

    def can_be_amended(self, current_tick: int) -> bool:
        """Check if law can be amended based on cooldown"""
        if self.last_amended_tick is None:
            return True

        return current_tick >= self.last_amended_tick + self.amendment_rules.cooldown_ticks

    def record_amendment(self, amendment_description: str, tick: int):
        """Record an amendment to this law"""
        self.amendment_history.append(
            {"description": amendment_description, "tick": tick, "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        self.last_amended_tick = tick

    def to_dict(self) -> Dict:
        return {
            "lawId": self.law_id,
            "scope": self.scope.value,
            "statement": self.statement,
            "enforcement": self.enforcement.value,
            "introducedAtTick": self.introduced_at_tick,
            "amendmentRules": self.amendment_rules.to_dict(),
            "amendmentHistory": self.amendment_history,
            "lastAmendedTick": self.last_amended_tick,
        }


@dataclass
class SimulationResult:
    """Result of simulating a proposed mutation"""

    simulation_id: str
    success: bool
    outcome_summary: str
    metrics: Dict[str, float] = field(default_factory=dict)
    risks_identified: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "simulation_id": self.simulation_id,
            "success": self.success,
            "outcome_summary": self.outcome_summary,
            "metrics": self.metrics,
            "risks_identified": self.risks_identified,
        }


@dataclass
class RiskAssessment:
    """Risk assessment for a mutation proposal"""

    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    concerns: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"level": self.level, "concerns": self.concerns, "mitigation_strategies": self.mitigation_strategies}


class MutationProposal:
    """
    Mutation Proposal (III.2)
    Proposes a change to the system's rules
    """

    def __init__(self, proposal_id: str, proposed_change: str, justification: str, proposer_id: str):
        self.proposal_id = proposal_id
        self.proposed_change = proposed_change
        self.justification = justification
        self.proposer_id = proposer_id
        self.submitted_at_tick: int = 0

        # Simulations
        self.simulations: List[SimulationResult] = []
        self.impact_simulation_ids: List[str] = []

        # Risk
        self.risk_assessment = RiskAssessment(level="MEDIUM")

        # Voting
        self.votes: Dict[str, bool] = {}  # manager_id -> vote (True=approve, False=reject)
        self.meta_office_ruling: Optional[bool] = None

        # Status
        self.status = MutationStatus.DRAFT
        self.status_history: List[Dict] = []

        # Activation
        self.delayed_activation_tick: Optional[int] = None
        self.activation_delay_ticks: int = 100  # Default delay

        # Rollback
        self.rollback_path: Optional[str] = None  # JSON describing how to rollback
        self.is_rolled_back: bool = False

        # Log creation
        get_audit_log().log_event(
            EventType.CODEX_AMENDMENT,
            actor_id=proposer_id,
            target_id=self.proposal_id,
            data={"action": "mutation_proposed", "proposed_change": proposed_change, "justification": justification},
        )

    def transition_to(self, new_status: MutationStatus, reason: str = ""):
        """Transition proposal through pipeline"""
        old_status = self.status
        self.status = new_status

        self.status_history.append(
            {
                "from": old_status.value,
                "to": new_status.value,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        get_audit_log().log_event(
            EventType.CODEX_AMENDMENT,
            target_id=self.proposal_id,
            data={"action": "mutation_status_changed", "from_status": old_status.value, "to_status": new_status.value},
        )

    def add_simulation(self, result: SimulationResult):
        """Add a simulation result"""
        self.simulations.append(result)
        self.impact_simulation_ids.append(result.simulation_id)

    def calculate_approval(self) -> bool:
        """Calculate if proposal is approved based on votes"""
        if not self.votes:
            return False

        approvals = sum(1 for vote in self.votes.values() if vote)
        total = len(self.votes)

        return approvals / total >= 0.67  # 2/3 majority

    def schedule_activation(self, current_tick: int):
        """
        Schedule delayed activation (III.3).
        Activation is never immediate.
        """
        self.delayed_activation_tick = current_tick + self.activation_delay_ticks

        get_audit_log().log_event(
            EventType.CODEX_AMENDMENT,
            target_id=self.proposal_id,
            data={"action": "activation_scheduled", "activation_tick": self.delayed_activation_tick},
        )

    def rollback(self, reason: str):
        """
        Roll back an active mutation.
        Rollback path is mandatory (III.3)
        """
        if not self.rollback_path:
            raise ValueError("No rollback path defined for this mutation")

        self.is_rolled_back = True
        self.transition_to(MutationStatus.ROLLED_BACK, reason)

        get_audit_log().log_event(
            EventType.CODEX_AMENDMENT,
            target_id=self.proposal_id,
            data={"action": "mutation_rolled_back", "reason": reason, "rollback_path": self.rollback_path},
        )

    def to_dict(self) -> Dict:
        return {
            "proposalId": self.proposal_id,
            "proposedChange": self.proposed_change,
            "justification": self.justification,
            "proposerId": self.proposer_id,
            "submittedAtTick": self.submitted_at_tick,
            "impactSimulation": [s.to_dict() for s in self.simulations],
            "riskAssessment": self.risk_assessment.to_dict(),
            "status": self.status.value,
            "votes": self.votes,
            "metaOfficeRuling": self.meta_office_ruling,
            "delayedActivationTick": self.delayed_activation_tick,
            "rollbackPath": self.rollback_path,
        }


class ConstitutionalMutationEngine:
    """
    Constitutional Mutation Engine
    Manages controlled evolution of the system (III)

    Mutation Pipeline:
    Proposal → Simulation → Risk Scoring → Manager Vote → Meta-Office Ruling → Delayed Activation
    """

    def __init__(self):
        self.laws: Dict[str, ConstitutionalLaw] = {}
        self.proposals: Dict[str, MutationProposal] = {}
        self.meta_office_id: Optional[str] = None

        # Initialize core laws
        self._initialize_core_laws()

    def _initialize_core_laws(self):
        """
        Initialize immutable core laws (III.4).
        These enforce mutation safety.
        """
        # Law 1: No self-removal of safeguards
        law1 = ConstitutionalLaw(
            "LAW-001", LawScope.GLOBAL, "No self-removal of safeguards", EnforcementLevel.CONSTITUTIONAL, 0
        )
        law1.amendment_rules.requires = ["MetaOffice", "Unanimous Manager Consensus", "External Audit"]
        self.register_law(law1)

        # Law 2: No mutation without simulation
        law2 = ConstitutionalLaw("LAW-002", LawScope.GLOBAL, "No mutation without simulation", EnforcementLevel.HARD, 0)
        self.register_law(law2)

        # Law 3: No mutation without human-traceable rationale
        law3 = ConstitutionalLaw(
            "LAW-003", LawScope.GLOBAL, "No mutation without human-traceable rationale", EnforcementLevel.HARD, 0
        )
        self.register_law(law3)

        # Law 4: All old laws remain archived forever
        law4 = ConstitutionalLaw(
            "LAW-004", LawScope.GLOBAL, "All old laws remain archived forever", EnforcementLevel.CONSTITUTIONAL, 0
        )
        self.register_law(law4)

        # Law 5: Meta-Office cannot change its own authority
        law5 = ConstitutionalLaw(
            "LAW-005",
            LawScope.GLOBAL,
            "Meta-Office cannot change its own authority",
            EnforcementLevel.CONSTITUTIONAL,
            0,
        )
        self.register_law(law5)

    def register_law(self, law: ConstitutionalLaw):
        """Register a constitutional law"""
        self.laws[law.law_id] = law

    def submit_proposal(self, proposal: MutationProposal) -> str:
        """Submit a mutation proposal"""
        self.proposals[proposal.proposal_id] = proposal
        proposal.transition_to(MutationStatus.UNDER_REVIEW, "Proposal submitted")
        return proposal.proposal_id

    def simulate_mutation(self, proposal_id: str) -> List[SimulationResult]:
        """
        Run simulations on a mutation proposal.
        Mutation Law: No mutation without simulation (III.4)
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return []

        # In production, this would run actual simulations
        # For now, create mock results
        result = SimulationResult(
            simulation_id=f"sim_{proposal_id[:8]}",
            success=True,
            outcome_summary="Simulation completed successfully",
            metrics={"stability": 0.95, "performance": 0.92},
            risks_identified=[],
        )

        proposal.add_simulation(result)
        proposal.transition_to(MutationStatus.SIMULATING, "Simulations running")

        return proposal.simulations

    def assess_risk(self, proposal_id: str) -> RiskAssessment:
        """Perform risk scoring on a proposal"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return RiskAssessment(level="UNKNOWN")

        # Analyze simulations for risks
        risks = []
        for sim in proposal.simulations:
            risks.extend(sim.risks_identified)

        # Determine risk level
        if len(risks) == 0:
            level = "LOW"
        elif len(risks) <= 2:
            level = "MEDIUM"
        elif len(risks) <= 4:
            level = "HIGH"
        else:
            level = "CRITICAL"

        proposal.risk_assessment = RiskAssessment(level=level, concerns=risks, mitigation_strategies=[])

        return proposal.risk_assessment

    def initiate_vote(self, proposal_id: str):
        """Initiate manager voting on a proposal"""
        proposal = self.proposals.get(proposal_id)
        if proposal:
            proposal.transition_to(MutationStatus.VOTING, "Voting initiated")

    def record_vote(self, proposal_id: str, manager_id: str, vote: bool):
        """Record a manager's vote"""
        proposal = self.proposals.get(proposal_id)
        if proposal:
            proposal.votes[manager_id] = vote

            get_audit_log().log_event(
                EventType.CONSENSUS_REACHED, actor_id=manager_id, target_id=proposal_id, data={"vote": vote}
            )

    def meta_office_ruling(self, proposal_id: str, ruling: bool, justification: str) -> bool:
        """
        Meta-Office makes final ruling.
        Mutation Law: Meta-Office cannot change its own authority (III.4)
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False

        # Check if proposal tries to change Meta-Office authority
        if "meta-office" in proposal.proposed_change.lower() and "authority" in proposal.proposed_change.lower():
            # Violation of Law 5
            proposal.transition_to(
                MutationStatus.REJECTED, "Violates Law 5: Meta-Office cannot change its own authority"
            )
            return False

        proposal.meta_office_ruling = ruling

        if ruling:
            proposal.transition_to(MutationStatus.APPROVED, justification)
            # Schedule delayed activation
            from app.miniature_office.core.world import get_world

            world = get_world()
            if world:
                proposal.schedule_activation(world.time)
        else:
            proposal.transition_to(MutationStatus.REJECTED, justification)

        get_audit_log().log_event(
            EventType.CODEX_AMENDMENT,
            actor_id=self.meta_office_id or "meta-office",
            target_id=proposal_id,
            data={"action": "meta_office_ruling", "ruling": ruling, "justification": justification},
        )

        return ruling

    def activate_mutation(self, proposal_id: str, current_tick: int) -> bool:
        """
        Activate a mutation if its delayed activation time has arrived.
        Activation is never immediate (III.3)
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False

        if proposal.status != MutationStatus.APPROVED:
            return False

        if proposal.delayed_activation_tick is None:
            return False

        if current_tick < proposal.delayed_activation_tick:
            return False  # Not time yet

        # Activate the mutation
        proposal.transition_to(MutationStatus.ACTIVE, "Delayed activation triggered")

        return True

    def get_active_laws(self) -> List[ConstitutionalLaw]:
        """Get all active constitutional laws"""
        return list(self.laws.values())

    def get_proposal(self, proposal_id: str) -> Optional[MutationProposal]:
        """Get a proposal by ID"""
        return self.proposals.get(proposal_id)


# Global mutation engine
_mutation_engine = ConstitutionalMutationEngine()


def get_mutation_engine() -> ConstitutionalMutationEngine:
    """Get the global mutation engine"""
    return _mutation_engine
