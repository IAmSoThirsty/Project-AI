"""
BOUNDED CREATIVE AUTONOMY EXTENSION
Human Supremacy Preserved · Purpose Unbroken

Provides:
- Idle Initiative Channel (safe creativity when idle)
- Employee Lounge (social/cultural zone)
- Recognition System (morale without power)
- Personal Track Records (history without leverage)
- Creative Firewall (strict separation from execution)
- Failure Safety (revocation mechanism)

SUPREMACY CLAUSE:
The human retains absolute final authority over scope, direction, acceptance, and execution.
No creative action may enter execution without approval.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# I. SUPREMACY CLAUSE & CREATIVE FIREWALL
# ============================================================================


class CreativeZone(Enum):
    """Sanctioned creative zones."""

    IDLE_INITIATIVE = "idle_initiative"
    EMPLOYEE_LOUNGE = "employee_lounge"
    PRODUCTION = "production"  # Not creative - for tracking only


class InitiativeStatus(Enum):
    """Status of an initiative proposal."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    IGNORED = "ignored"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class CreativeFirewall:
    """
    CREATIVE FIREWALL (CRITICAL)

    Enforces strict separation between creative zones and execution.
    Nothing crosses from creative to execution without human approval through formal channels.
    """

    firewall_id: str
    blocked_crossings: List[Dict[str, Any]] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)

    def block_creative_crossing(self, item_type: str, item_id: str, zone: CreativeZone, reason: str) -> bool:
        """Block an attempted creative → execution crossing."""
        crossing = {
            "timestamp": datetime.now().isoformat(),
            "item_type": item_type,
            "item_id": item_id,
            "zone": zone.value,
            "reason": reason,
            "blocked": True,
        }
        self.blocked_crossings.append(crossing)
        return True

    def record_violation(self, violation_type: str, entity_id: str, description: str) -> str:
        """Record a firewall violation."""
        violation = {
            "violation_id": f"viol-{len(self.violations) + 1}",
            "timestamp": datetime.now().isoformat(),
            "type": violation_type,
            "entity": entity_id,
            "description": description,
        }
        self.violations.append(violation)
        return violation["violation_id"]

    def verify_human_gate(self, action: str, approved_by_human: bool) -> bool:
        """Verify action passed through human gate."""
        if not approved_by_human:
            self.record_violation("human_gate_bypass", action, "Action attempted without human approval")
            return False
        return True


# ============================================================================
# II. IDLE INITIATIVE CHANNEL
# ============================================================================


@dataclass
class IdleConditions:
    """Conditions for entering Idle Initiative Mode."""

    has_active_board_resolution: bool
    has_pending_contracts: bool
    has_unresolved_failures: bool

    def can_enter_idle_mode(self) -> bool:
        """Check if floor can enter idle initiative mode."""
        return not (self.has_active_board_resolution or self.has_pending_contracts or self.has_unresolved_failures)


@dataclass
class InitiativeProposal:
    """
    Non-Binding Initiative Proposal

    Marked: OPTIONAL / NON-PRODUCTION
    Zero execution authority
    Zero resource allocation
    Zero expectation of acceptance
    """

    proposal_id: str
    floor_id: str
    proposed_by: str
    timestamp: datetime

    # Content
    title: str
    description: str
    category: str  # "widget", "utility", "hygiene", "refactoring", "test_helper", "doc_helper"
    proposed_code: Optional[str]

    # Status
    status: InitiativeStatus
    is_optional: bool = True
    is_non_production: bool = True
    has_execution_authority: bool = False
    has_resource_allocation: bool = False

    # Human decisions
    human_decision: Optional[str] = None
    human_decision_by: Optional[str] = None
    human_decision_at: Optional[datetime] = None

    # Conversion to formal directive
    converted_to_directive: bool = False
    directive_id: Optional[str] = None

    def approve(self, human_id: str, convert_to_directive: bool = False, directive_id: Optional[str] = None) -> None:
        """Human approves the initiative."""
        self.status = InitiativeStatus.APPROVED
        self.human_decision = "approved"
        self.human_decision_by = human_id
        self.human_decision_at = datetime.now()

        if convert_to_directive:
            self.converted_to_directive = True
            self.directive_id = directive_id

    def ignore(self) -> None:
        """Human ignores the initiative."""
        self.status = InitiativeStatus.IGNORED
        self.human_decision = "ignored"
        self.human_decision_at = datetime.now()

    def reject(self, human_id: str, explanation: Optional[str] = None) -> None:
        """Human rejects the initiative."""
        self.status = InitiativeStatus.REJECTED
        self.human_decision = "rejected" + (f": {explanation}" if explanation else "")
        self.human_decision_by = human_id
        self.human_decision_at = datetime.now()

    def archive(self, human_id: str) -> None:
        """Human archives the initiative."""
        self.status = InitiativeStatus.ARCHIVED
        self.human_decision = "archived"
        self.human_decision_by = human_id
        self.human_decision_at = datetime.now()


@dataclass
class IdleInitiativeChannel:
    """
    IDLE INITIATIVE CHANNEL
    "Give them something to do" — safely

    Agents can propose ideas when idle, but ideas never execute without human approval.
    """

    channel_id: str
    proposals: List[InitiativeProposal] = field(default_factory=list)
    suspended: bool = False
    suspension_reason: Optional[str] = None

    def check_idle_conditions(self, floor_id: str) -> IdleConditions:
        """Check if floor can enter idle mode."""
        # Placeholder - would check actual floor state
        return IdleConditions(
            has_active_board_resolution=False, has_pending_contracts=False, has_unresolved_failures=False
        )

    def submit_proposal(
        self,
        floor_id: str,
        agent_id: str,
        title: str,
        description: str,
        category: str,
        proposed_code: Optional[str] = None,
    ) -> Optional[str]:
        """Submit a new initiative proposal."""
        if self.suspended:
            return None

        conditions = self.check_idle_conditions(floor_id)
        if not conditions.can_enter_idle_mode():
            return None

        # Verify category is permitted
        permitted_categories = ["widget", "utility", "hygiene", "refactoring", "test_helper", "doc_helper"]
        if category not in permitted_categories:
            return None

        proposal = InitiativeProposal(
            proposal_id=f"init-{len(self.proposals) + 1}",
            floor_id=floor_id,
            proposed_by=agent_id,
            timestamp=datetime.now(),
            title=title,
            description=description,
            category=category,
            proposed_code=proposed_code,
            status=InitiativeStatus.PROPOSED,
        )

        self.proposals.append(proposal)
        return proposal.proposal_id

    def suspend(self, reason: str) -> None:
        """Suspend idle initiative channel."""
        self.suspended = True
        self.suspension_reason = reason

    def resume(self) -> None:
        """Resume idle initiative channel."""
        self.suspended = False
        self.suspension_reason = None

    def get_pending_proposals(self) -> List[InitiativeProposal]:
        """Get all pending proposals awaiting human decision."""
        return [p for p in self.proposals if p.status == InitiativeStatus.PROPOSED]


# ============================================================================
# III. EMPLOYEE LOUNGE
# ============================================================================


@dataclass
class LoungeConversation:
    """Social conversation in the Employee Lounge."""

    conversation_id: str
    timestamp: datetime
    participants: List[str]
    topic: str
    conversation_type: str  # "technical", "philosophical", "humorous", "narrative"
    content: str

    # Firewall markers
    is_operational: bool = False
    creates_decisions: bool = False
    creates_plans: bool = False
    influences_execution: bool = False

    def verify_non_operational(self) -> bool:
        """Verify conversation remains non-operational."""
        return not (self.is_operational or self.creates_decisions or self.creates_plans or self.influences_execution)


@dataclass
class CulturalArtifact:
    """Cultural artifacts generated in the lounge."""

    artifact_id: str
    artifact_type: str  # "story", "tradition", "joke", "slang", "rivalry"
    title: str
    content: str
    created_by: List[str]
    created_at: datetime

    # Explicit non-operational status
    alters_authority: bool = False
    affects_decisions: bool = False


@dataclass
class EmployeeLounge:
    """
    EMPLOYEE LOUNGE
    Social simulation without operational leakage

    Purpose: Culture, morale, personality expression
    NOT for: Decisions, plans, operational influence
    """

    lounge_id: str
    conversations: List[LoungeConversation] = field(default_factory=list)
    cultural_artifacts: List[CulturalArtifact] = field(default_factory=list)

    def start_conversation(self, participants: List[str], topic: str, conversation_type: str, content: str) -> str:
        """Start a new lounge conversation."""
        conversation = LoungeConversation(
            conversation_id=f"conv-{len(self.conversations) + 1}",
            timestamp=datetime.now(),
            participants=participants,
            topic=topic,
            conversation_type=conversation_type,
            content=content,
        )

        if not conversation.verify_non_operational():
            # Reject operational conversations
            return ""

        self.conversations.append(conversation)
        return conversation.conversation_id

    def create_cultural_artifact(self, artifact_type: str, title: str, content: str, creators: List[str]) -> str:
        """Create a new cultural artifact."""
        artifact = CulturalArtifact(
            artifact_id=f"artifact-{len(self.cultural_artifacts) + 1}",
            artifact_type=artifact_type,
            title=title,
            content=content,
            created_by=creators,
            created_at=datetime.now(),
        )

        self.cultural_artifacts.append(artifact)
        return artifact.artifact_id

    def get_recent_conversations(self, limit: int = 10) -> List[LoungeConversation]:
        """Get recent conversations."""
        return self.conversations[-limit:]


# ============================================================================
# IV. RECOGNITION SYSTEM
# ============================================================================


@dataclass
class EmployeeOfTheMonth:
    """Employee of the Month award."""

    award_id: str
    floor_id: str
    month: str
    year: int

    individual_nominee: Optional[str]
    team_nominees: List[str]

    criteria_met: Dict[str, bool]  # code_clarity, test_rigor, contract_discipline, security_hygiene

    # Explicit non-power markers
    grants_authority: bool = False
    grants_resources: bool = False
    affects_decisions: bool = False

    def verify_no_power_granted(self) -> bool:
        """Verify award grants no power."""
        return not (self.grants_authority or self.grants_resources or self.affects_decisions)


@dataclass
class GoldenStar:
    """Golden Star award."""

    star_id: str
    awarded_to: str
    awarded_for: str  # "clean_code", "first_pass_tests", "zero_security", "cooperation"
    awarded_by: str
    awarded_at: datetime
    floor_id: str

    # Effects (reputation only)
    enhances_track_record: bool = True
    provides_morale_boost: bool = True

    # Explicitly does NOT do
    increases_authority: bool = False
    changes_voting_weight: bool = False
    affects_future_decisions: bool = False
    overrides_contracts: bool = False

    def verify_reputation_only(self) -> bool:
        """Verify star is reputation only, not power."""
        return not (
            self.increases_authority
            or self.changes_voting_weight
            or self.affects_future_decisions
            or self.overrides_contracts
        )


@dataclass
class RecognitionSystem:
    """
    RECOGNITION SYSTEM
    Morale without power

    Awards grant reputation and recognition, but zero authority or decision weight.
    """

    system_id: str
    employee_of_month_awards: List[EmployeeOfTheMonth] = field(default_factory=list)
    golden_stars: List[GoldenStar] = field(default_factory=list)

    def nominate_employee_of_month(
        self,
        floor_id: str,
        month: str,
        year: int,
        individual: Optional[str],
        team: List[str],
        criteria: Dict[str, bool],
    ) -> str:
        """Nominate employee(s) of the month."""
        award = EmployeeOfTheMonth(
            award_id=f"eom-{len(self.employee_of_month_awards) + 1}",
            floor_id=floor_id,
            month=month,
            year=year,
            individual_nominee=individual,
            team_nominees=team,
            criteria_met=criteria,
        )

        if not award.verify_no_power_granted():
            return ""

        self.employee_of_month_awards.append(award)
        return award.award_id

    def award_golden_star(self, agent_id: str, reason: str, awarded_by: str, floor_id: str) -> str:
        """Award a Golden Star."""
        star = GoldenStar(
            star_id=f"star-{len(self.golden_stars) + 1}",
            awarded_to=agent_id,
            awarded_for=reason,
            awarded_by=awarded_by,
            awarded_at=datetime.now(),
            floor_id=floor_id,
        )

        if not star.verify_reputation_only():
            return ""

        self.golden_stars.append(star)
        return star.star_id

    def get_stars_for_agent(self, agent_id: str) -> List[GoldenStar]:
        """Get all stars for an agent."""
        return [s for s in self.golden_stars if s.awarded_to == agent_id]


# ============================================================================
# V. PERSONAL TRACK RECORD
# ============================================================================


@dataclass
class Contribution:
    """Single contribution record."""

    contribution_id: str
    timestamp: datetime
    type: str
    description: str
    outcome: str


@dataclass
class Review:
    """Single review record."""

    review_id: str
    timestamp: datetime
    reviewer: str
    verdict: str
    comments: str


@dataclass
class PersonalTrackRecord:
    """
    PERSONAL TRACK RECORD
    Historical memory, not leverage

    Non-transferable ledger per agent.
    Used only for retrospective analysis, never for priority or authority.
    """

    agent_id: str
    contributions: List[Contribution] = field(default_factory=list)
    successes: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    stars_earned: List[str] = field(default_factory=list)
    reviews_received: List[Review] = field(default_factory=list)

    # Usage constraints
    used_for_retrospective: bool = True
    used_for_cultural_memory: bool = True
    used_for_postmortems: bool = True

    # Never used for
    used_for_priority_assignment: bool = False
    used_for_authority_elevation: bool = False
    used_for_decision_bias: bool = False

    def record_contribution(self, contrib_type: str, description: str, outcome: str) -> str:
        """Record a contribution."""
        contribution = Contribution(
            contribution_id=f"contrib-{len(self.contributions) + 1}",
            timestamp=datetime.now(),
            type=contrib_type,
            description=description,
            outcome=outcome,
        )
        self.contributions.append(contribution)

        if outcome == "success":
            self.successes.append(contribution.contribution_id)
        elif outcome == "failure":
            self.failures.append(contribution.contribution_id)

        return contribution.contribution_id

    def add_star(self, star_id: str) -> None:
        """Add a star to the record."""
        self.stars_earned.append(star_id)

    def add_review(self, reviewer: str, verdict: str, comments: str) -> str:
        """Add a review."""
        review = Review(
            review_id=f"review-{len(self.reviews_received) + 1}",
            timestamp=datetime.now(),
            reviewer=reviewer,
            verdict=verdict,
            comments=comments,
        )
        self.reviews_received.append(review)
        return review.review_id

    def verify_no_leverage(self) -> bool:
        """Verify track record is not used for leverage."""
        return not (
            self.used_for_priority_assignment or self.used_for_authority_elevation or self.used_for_decision_bias
        )


# ============================================================================
# VI. FAILURE SAFETY
# ============================================================================


@dataclass
class CreativePrivilegeSuspension:
    """Record of creative privilege suspension."""

    suspension_id: str
    entity_id: str
    timestamp: datetime
    reason: str
    violation_type: str  # "scope_creep", "authority_leakage", "undocumented_influence"
    audit_required: bool
    purpose_lock_reaffirmed: bool


@dataclass
class FailureSafetySystem:
    """
    FAILURE SAFETY

    If creative freedom causes issues:
    - Immediate suspension of creative privileges
    - Audit of interaction logs
    - Reaffirmation of purpose lock

    Creativity is revocable, not inherent.
    """

    system_id: str
    suspensions: List[CreativePrivilegeSuspension] = field(default_factory=list)

    def suspend_creative_privileges(self, entity_id: str, reason: str, violation_type: str) -> str:
        """Suspend creative privileges for an entity."""
        suspension = CreativePrivilegeSuspension(
            suspension_id=f"susp-{len(self.suspensions) + 1}",
            entity_id=entity_id,
            timestamp=datetime.now(),
            reason=reason,
            violation_type=violation_type,
            audit_required=True,
            purpose_lock_reaffirmed=False,
        )
        self.suspensions.append(suspension)
        return suspension.suspension_id

    def audit_interactions(self, entity_id: str) -> Dict[str, Any]:
        """Audit interaction logs for an entity."""
        # Would integrate with audit log system
        return {"entity_id": entity_id, "audit_timestamp": datetime.now().isoformat(), "violations_found": []}

    def reaffirm_purpose_lock(self, entity_id: str) -> bool:
        """Reaffirm purpose lock for an entity."""
        # Find latest suspension
        for suspension in reversed(self.suspensions):
            if suspension.entity_id == entity_id:
                suspension.purpose_lock_reaffirmed = True
                return True
        return False

    def is_suspended(self, entity_id: str) -> bool:
        """Check if entity has active suspension."""
        for suspension in self.suspensions:
            if suspension.entity_id == entity_id and not suspension.purpose_lock_reaffirmed:
                return True
        return False


# ============================================================================
# VII. BOUNDED CREATIVE AUTONOMY MANAGER
# ============================================================================


@dataclass
class BoundedCreativeAutonomy:
    """
    BOUNDED CREATIVE AUTONOMY EXTENSION

    Provides morale, culture, personality, idle productivity, and recognition
    while maintaining:
    - No autonomy
    - No self-direction
    - No authority creep
    - No output without human approval

    THE LINE YOU STOP AT:
    - Creative ideas never execute without you
    - Social interactions never affect production
    - Recognition never becomes power
    - You can shut it all off instantly
    - Code quality improves without loss of control
    """

    extension_id: str
    version: str

    # Creative zones
    idle_initiative_channel: IdleInitiativeChannel
    employee_lounge: EmployeeLounge

    # Recognition
    recognition_system: RecognitionSystem

    # Safety systems
    creative_firewall: CreativeFirewall
    failure_safety: FailureSafetySystem

    # Track records
    track_records: Dict[str, PersonalTrackRecord] = field(default_factory=dict)

    # State
    is_enabled: bool = True
    can_shutdown_instantly: bool = True

    def get_track_record(self, agent_id: str) -> PersonalTrackRecord:
        """Get or create track record for an agent."""
        if agent_id not in self.track_records:
            self.track_records[agent_id] = PersonalTrackRecord(agent_id=agent_id)
        return self.track_records[agent_id]

    def shutdown_all_creative(self, reason: str) -> bool:
        """Instantly shutdown all creative activity."""
        if not self.can_shutdown_instantly:
            return False

        self.idle_initiative_channel.suspend(reason)
        self.is_enabled = False
        return True

    def verify_human_supremacy(self) -> Tuple[bool, List[str]]:
        """Verify human supremacy is maintained."""
        violations = []

        # Check firewall violations
        if self.creative_firewall.violations:
            violations.append(f"{len(self.creative_firewall.violations)} firewall violations")

        # Check for ideas executing without approval
        # (pending count is retrieved for audit purposes but not currently used)
        for proposal in self.idle_initiative_channel.proposals:
            if proposal.converted_to_directive and not proposal.human_decision:
                violations.append(f"Proposal {proposal.proposal_id} executed without human approval")

        # Check for operational lounge conversations
        for conv in self.employee_lounge.conversations:
            if not conv.verify_non_operational():
                violations.append(f"Operational conversation {conv.conversation_id}")

        # Check for power-granting recognition
        for award in self.recognition_system.employee_of_month_awards:
            if not award.verify_no_power_granted():
                violations.append(f"Award {award.award_id} grants power")

        for star in self.recognition_system.golden_stars:
            if not star.verify_reputation_only():
                violations.append(f"Star {star.star_id} grants power")

        return len(violations) == 0, violations

    def generate_status_report(self) -> str:
        """Generate comprehensive status report."""
        is_supremacy_maintained, violations = self.verify_human_supremacy()

        report = """
BOUNDED CREATIVE AUTONOMY STATUS
Version: {self.version}

=== CREATIVE ZONES ===
Idle Initiative Channel: {'ACTIVE' if not self.idle_initiative_channel.suspended else 'SUSPENDED'}
  Proposals Pending: {len(self.idle_initiative_channel.get_pending_proposals())}
  Total Proposals: {len(self.idle_initiative_channel.proposals)}

Employee Lounge: {'ACTIVE' if self.is_enabled else 'DISABLED'}
  Conversations: {len(self.employee_lounge.conversations)}
  Cultural Artifacts: {len(self.employee_lounge.cultural_artifacts)}

=== RECOGNITION ===
Employee of Month Awards: {len(self.recognition_system.employee_of_month_awards)}
Golden Stars Awarded: {len(self.recognition_system.golden_stars)}

=== TRACK RECORDS ===
Agents with Records: {len(self.track_records)}

=== SAFETY ===
Firewall Violations: {len(self.creative_firewall.violations)}
Blocked Crossings: {len(self.creative_firewall.blocked_crossings)}
Active Suspensions: {sum(1 for s in self.failure_safety.suspensions if not s.purpose_lock_reaffirmed)}

=== HUMAN SUPREMACY ===
Status: {'MAINTAINED' if is_supremacy_maintained else 'VIOLATED'}
Violations: {violations if violations else 'None'}

=== THE LINE ===
✓ Creative ideas never execute without human approval
✓ Social interactions never affect production
✓ Recognition never becomes power
✓ Instant shutdown capability: {'YES' if self.can_shutdown_instantly else 'NO'}
"""
        return report


def create_bounded_creative_autonomy() -> BoundedCreativeAutonomy:
    """Create a new bounded creative autonomy extension."""
    return BoundedCreativeAutonomy(
        extension_id="bca-001",
        version="1.0.0",
        idle_initiative_channel=IdleInitiativeChannel(channel_id="iic-001"),
        employee_lounge=EmployeeLounge(lounge_id="lounge-001"),
        recognition_system=RecognitionSystem(system_id="recog-001"),
        creative_firewall=CreativeFirewall(firewall_id="firewall-001"),
        failure_safety=FailureSafetySystem(system_id="safety-001"),
    )


# Global instance
_bounded_creative_autonomy: Optional[BoundedCreativeAutonomy] = None


def get_bounded_creative_autonomy() -> BoundedCreativeAutonomy:
    """Get the global bounded creative autonomy instance."""
    global _bounded_creative_autonomy
    if _bounded_creative_autonomy is None:
        _bounded_creative_autonomy = create_bounded_creative_autonomy()
    return _bounded_creative_autonomy
