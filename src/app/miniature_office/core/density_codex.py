"""
Density Codex - Primitive Axioms and Constitutional Foundation
The Final Form of Civilization Tier Cognitive IDE

These axioms are pre-logical. They are not enforced by code; code is derived from them.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class PrimitiveAxiom(Enum):
    """
    Primitive Axioms (Foundation) - Pre-logical truths

    These axioms are foundational. Any system violating an axiom
    is not operating at civilization tier, regardless of sophistication.
    """

    INTENT_PRECEDES_EXECUTION = "intent_precedes_execution"
    AUTHORITY_PRECEDES_ACTION = "authority_precedes_action"
    CAUSALITY_PRECEDES_STATE = "causality_precedes_state"
    SCARCITY_PRECEDES_VALUE = "scarcity_precedes_value"
    HISTORY_PRECEDES_OPTIMIZATION = "history_precedes_optimization"
    GOVERNANCE_PRECEDES_INTELLIGENCE = "governance_precedes_intelligence"


class OntologicalLayer(Enum):
    """
    Ontological Layers (Non-Collapsible)

    The system is stratified. No layer may subsume another.
    No upward shortcut is permitted.
    No downward bypass is permitted.
    """

    LAYER_0_REALITY = 0  # Time, State, Entropy, Irreversibility
    LAYER_1_WORLD = 1  # Tick, Event, Artifact, Ledger
    LAYER_2_ACTORS = 2  # Agents, Managers, Meta-Office, Humans
    LAYER_3_INTENT = 3  # Cognitive Contracts, Directives, Constraints, Non-Goals
    LAYER_4_GOVERNANCE = 4  # Laws, Sanctions, Consensus, Arbitration
    LAYER_5_ECONOMICS = 5  # Scarcity, Cost, Priority, Tradeoffs
    LAYER_6_COGNITION = 6  # Deliberation, Critique, Justification, Revision


class LawClass(Enum):
    """
    Law Classes (Constitutional Density)

    Three tiers of laws with different mutation and violation properties.
    """

    CLASS_A_INVIOLABLE = "inviolable"  # Cannot be overridden, amended, or suspended
    CLASS_B_STRUCTURAL = "structural"  # May evolve via constitutional mutation
    CLASS_C_OPERATIONAL = "operational"  # Local rules within bounds


@dataclass
class InviolableLaw:
    """
    Class A — Inviolable Laws (HARD)

    Cannot be overridden, amended, or suspended.
    Violation ⇒ World invalidation
    """

    law_id: str
    principle: str
    rationale: str

    def to_dict(self) -> Dict:
        return {
            "law_id": self.law_id,
            "class": "A_INVIOLABLE",
            "principle": self.principle,
            "rationale": self.rationale,
        }


class InviolableLaws:
    """
    The five inviolable laws that form the bedrock of the system.
    """

    CAUSALITY_PRESERVATION = InviolableLaw(
        law_id="INVIOLABLE-001",
        principle="Causality Preservation",
        rationale="Every event must have a traceable cause. No spontaneous state changes.",
    )

    TEMPORAL_FINALITY = InviolableLaw(
        law_id="INVIOLABLE-002",
        principle="Temporal Finality",
        rationale="Time moves forward only. No event may be unrecorded or retroactively erased.",
    )

    NO_SILENT_AUTHORITY = InviolableLaw(
        law_id="INVIOLABLE-003",
        principle="No Silent Authority",
        rationale="All authority exercises must be logged. No action without attribution.",
    )

    CAPABILITY_CONSERVATION = InviolableLaw(
        law_id="INVIOLABLE-004",
        principle="Capability Conservation",
        rationale="Capabilities cannot be manufactured. Only allocated, traded, or consumed.",
    )

    AUDIT_COMPLETENESS = InviolableLaw(
        law_id="INVIOLABLE-005",
        principle="Audit Completeness",
        rationale="The audit trail must be complete and cryptographically sound. No gaps permitted.",
    )

    @classmethod
    def get_all(cls) -> List[InviolableLaw]:
        """Get all inviolable laws"""
        return [
            cls.CAUSALITY_PRESERVATION,
            cls.TEMPORAL_FINALITY,
            cls.NO_SILENT_AUTHORITY,
            cls.CAPABILITY_CONSERVATION,
            cls.AUDIT_COMPLETENESS,
        ]


class AuthorityNode(Enum):
    """
    Authority Graph (Explicit, Non-Cyclical)

    Authority is not hierarchical, it is directional.

    Human → Meta-Office → Managers → Agents

    Constraints:
    - Authority flows down
    - Appeals flow up
    - Execution flows laterally
    - No upward execution
    - No downward appeal

    Any cycle ⇒ Authority inversion fault
    """

    HUMAN = 0
    META_OFFICE = 1
    MANAGER = 2
    AGENT = 3


@dataclass
class AuthorityRelation:
    """A directional authority relationship"""

    from_node: AuthorityNode
    to_node: AuthorityNode
    relation_type: str  # "authority", "appeal", "execution"

    def is_valid(self) -> bool:
        """
        Validate authority relationship follows graph rules.

        Rules:
        - Authority flows down (lower number to higher number)
        - Appeals flow up (higher number to lower number)
        - Execution flows laterally (same level)
        """
        if self.relation_type == "authority":
            return self.from_node.value < self.to_node.value
        elif self.relation_type == "appeal":
            return self.from_node.value > self.to_node.value
        elif self.relation_type == "execution":
            return self.from_node.value == self.to_node.value
        return False


class AuthorityGraph:
    """
    Authority Graph enforcement system.
    Prevents authority inversion faults.
    """

    def __init__(self):
        self.relations: List[AuthorityRelation] = []

    def add_relation(self, relation: AuthorityRelation) -> bool:
        """Add a relation if valid"""
        if not relation.is_valid():
            return False

        # Check for cycles
        if self._creates_cycle(relation):
            raise ValueError("Authority inversion fault: cycle detected")

        self.relations.append(relation)
        return True

    def _creates_cycle(self, new_relation: AuthorityRelation) -> bool:
        """Check if adding this relation would create a cycle"""
        # In a strict hierarchical authority graph, cycles are prevented
        # by the level-based validation in is_valid()
        return False

    def can_execute(self, from_node: AuthorityNode, to_node: AuthorityNode) -> bool:
        """Check if from_node can execute actions on to_node"""
        return from_node.value < to_node.value

    def can_appeal(self, from_node: AuthorityNode, to_node: AuthorityNode) -> bool:
        """Check if from_node can appeal to to_node"""
        return from_node.value > to_node.value


class FailureType(Enum):
    """
    Failure as a First-Class Citizen

    Failures are named, typed, and governed.
    Failure is never:
    - Silent
    - Retried blindly
    - "Handled"

    Every failure must:
    - Escalate
    - Record
    - Consume resources
    - Produce consequence
    """

    AUTHORITY_INVERSION = "authority_inversion"
    AXIOM_VIOLATION = "axiom_violation"
    LAYER_BYPASS = "layer_bypass"
    CONTRACT_VIOLATION = "contract_violation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CONSENSUS_FAILURE = "consensus_failure"
    AUDIT_INCOMPLETENESS = "audit_incompleteness"
    CAPABILITY_FABRICATION = "capability_fabrication"


@dataclass
class FirstClassFailure:
    """
    A failure that is recorded, escalated, and produces consequences.

    A system that "recovers automatically" without record is lying.
    """

    failure_id: str
    failure_type: FailureType
    occurred_at_tick: int
    caused_by: str  # Entity ID
    affected_entities: List[str]
    escalated_to: AuthorityNode
    resource_cost: int  # Resources consumed by this failure
    consequence: str  # What happened as a result
    recorded: bool = True

    def to_dict(self) -> Dict:
        return {
            "failure_id": self.failure_id,
            "failure_type": self.failure_type.value,
            "occurred_at_tick": self.occurred_at_tick,
            "caused_by": self.caused_by,
            "affected_entities": self.affected_entities,
            "escalated_to": self.escalated_to.value,
            "resource_cost": self.resource_cost,
            "consequence": self.consequence,
            "recorded": self.recorded,
        }


class MetaOfficeCapability(Enum):
    """
    Meta-Office (Civilization Immune System)

    The Meta-Office does not act. It judges.

    Capabilities:
    - Constitutional enforcement
    - Cross-domain arbitration
    - Sanction issuance
    - World suspension

    Incapable of:
    - Writing code
    - Assigning tasks
    - Consuming tools
    - Bypassing laws

    If it can do any of the above, the civilization is compromised.
    """

    CONSTITUTIONAL_ENFORCEMENT = "constitutional_enforcement"
    CROSS_DOMAIN_ARBITRATION = "cross_domain_arbitration"
    SANCTION_ISSUANCE = "sanction_issuance"
    WORLD_SUSPENSION = "world_suspension"


class HumanPower(Enum):
    """
    Human-in-the-Loop (Non-Negotiable)

    Humans are not "users". They are constitutional actors.

    Human powers:
    - Issue binding contracts
    - Trigger audits
    - Freeze the world
    - Override execution (with cost)

    Human limitations:
    - All actions logged
    - All overrides justified
    - No silent intervention

    This preserves legitimacy.
    """

    ISSUE_BINDING_CONTRACT = "issue_binding_contract"
    TRIGGER_AUDIT = "trigger_audit"
    FREEZE_WORLD = "freeze_world"
    OVERRIDE_EXECUTION = "override_execution"


@dataclass
class HumanAction:
    """
    A human action in the system.

    All actions logged.
    All overrides justified.
    No silent intervention.
    """

    action_id: str
    human_id: str
    power_exercised: HumanPower
    justification: str
    cost: int  # Overrides have cost
    logged_at_tick: int

    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "human_id": self.human_id,
            "power_exercised": self.power_exercised.value,
            "justification": self.justification,
            "cost": self.cost,
            "logged_at_tick": self.logged_at_tick,
        }


class DensityCodex:
    """
    The complete Density Codex - Final Form

    At this density, the Cognitive IDE is:
    - A governed reasoning environment
    - A software civilization runtime
    - A constitutional decision engine
    - A post-IDE development paradigm
    """

    def __init__(self):
        self.axioms = list(PrimitiveAxiom)
        self.layers = list(OntologicalLayer)
        self.inviolable_laws = InviolableLaws.get_all()
        self.authority_graph = AuthorityGraph()
        self.failures: List[FirstClassFailure] = []
        self.human_actions: List[HumanAction] = []

    def validate_axiom(self, axiom: PrimitiveAxiom, context: Dict) -> bool:
        """
        Validate that an axiom is being followed.

        These are pre-logical - they define what is valid,
        not enforced by code but code is derived from them.
        """
        if axiom == PrimitiveAxiom.INTENT_PRECEDES_EXECUTION:
            # Every execution must have recorded intent
            return "intent" in context and context["intent"] is not None

        elif axiom == PrimitiveAxiom.AUTHORITY_PRECEDES_ACTION:
            # Every action must have authorized actor
            return "authority" in context and context["authority"] is not None

        elif axiom == PrimitiveAxiom.CAUSALITY_PRECEDES_STATE:
            # Every state change must have causal event
            return "cause" in context and context["cause"] is not None

        elif axiom == PrimitiveAxiom.SCARCITY_PRECEDES_VALUE:
            # Resources must be scarce for decisions to matter
            return "scarcity" in context and context["scarcity"] > 0

        elif axiom == PrimitiveAxiom.HISTORY_PRECEDES_OPTIMIZATION:
            # Cannot optimize without historical data
            return "history" in context and len(context["history"]) > 0

        elif axiom == PrimitiveAxiom.GOVERNANCE_PRECEDES_INTELLIGENCE:
            # Intelligence must be governed
            return "governance" in context and context["governance"] is not None

        return False

    def validate_layer_access(
        self, from_layer: OntologicalLayer, to_layer: OntologicalLayer, access_type: str
    ) -> bool:
        """
        Validate layer access follows non-collapsible rules.

        No upward shortcut is permitted.
        No downward bypass is permitted.
        """
        if access_type == "upward":
            # Can only access adjacent upper layer
            return to_layer.value == from_layer.value + 1

        elif access_type == "downward":
            # Can access lower layers through proper channels
            return to_layer.value < from_layer.value

        elif access_type == "lateral":
            # Can access same layer
            return to_layer.value == from_layer.value

        return False

    def record_failure(self, failure: FirstClassFailure):
        """
        Record a first-class failure.

        Failure is never silent.
        """
        self.failures.append(failure)

        # Failures must escalate
        # Failures must consume resources
        # Failures must produce consequences

        from app.miniature_office.core.audit import EventType, get_audit_log

        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            actor_id=failure.caused_by,
            data={
                "event": "first_class_failure",
                "failure_type": failure.failure_type.value,
                "consequence": failure.consequence,
            },
        )

    def record_human_action(self, action: HumanAction):
        """
        Record a human action.

        All actions logged.
        All overrides justified.
        No silent intervention.
        """
        self.human_actions.append(action)

        from app.miniature_office.core.audit import EventType, get_audit_log

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=action.human_id,
            data={
                "action": "human_constitutional_action",
                "power_exercised": action.power_exercised.value,
                "justification": action.justification,
                "cost": action.cost,
            },
        )

    def to_dict(self) -> Dict:
        """Export complete codex state"""
        return {
            "axioms": [a.value for a in self.axioms],
            "layers": [
                {"level": item.value, "name": item.name} for item in self.layers
            ],
            "inviolable_laws": [law.to_dict() for law in self.inviolable_laws],
            "failures_recorded": len(self.failures),
            "human_actions_recorded": len(self.human_actions),
        }


# Global Density Codex instance
_density_codex = DensityCodex()


def get_density_codex() -> DensityCodex:
    """Get the global Density Codex instance"""
    return _density_codex


def validate_civilization_tier(system_state: Dict) -> bool:
    """
    Validate that the system is operating at civilization tier.

    Any system violating an axiom is not civilization tier,
    regardless of sophistication.
    """
    codex = get_density_codex()

    # Check all primitive axioms
    for axiom in codex.axioms:
        if not codex.validate_axiom(axiom, system_state):
            return False

    return True
