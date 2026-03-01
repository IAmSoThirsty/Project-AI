"""
MAXIMUM AUTONOMY MODEL
Free Civilization · Human Has Veto, Not Micro-Control

This module implements the Maximum Autonomy Model where the civilization
operates freely with human sovereign veto authority rather than microcontrol.

Authority Shift:
- OLD: Nothing meaningful happens without you
- NEW: Civilization acts freely, nothing irreversible without you

Core Principle: This is how real civilizations work.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

# ============================================================================
# ENUMERATIONS
# ============================================================================


class ExecutionZone(Enum):
    """Three realities of execution"""

    SANDBOX = "sandbox"  # Experimental, internal commits only
    STAGING = "staging"  # Almost real, provisional, rollback guaranteed
    PRODUCTION = "production"  # Real, requires human seal


class StagingStatus(Enum):
    """Staging reality statuses"""

    DEVELOPMENT = "development"
    INTEGRATION_TESTING = "integration_testing"
    SECURITY_TESTING = "security_testing"
    PERFORMANCE_TESTING = "performance_testing"
    CONFLICT_RESOLUTION = "conflict_resolution"
    READY_FOR_REVIEW = "ready_for_review"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    VETOED = "vetoed"


class TeamFormationReason(Enum):
    """Why teams self-organize"""

    INITIATIVE = "initiative"
    COMPETITION = "competition"
    CRISIS_RESPONSE = "crisis_response"
    INNOVATION = "innovation"
    REFACTORING = "refactoring"
    CROSS_FLOOR_NEED = "cross_floor_need"


class FloorInitiativeType(Enum):
    """Types of floor-initiated projects"""

    SAFETY_IMPROVEMENT = "safety_improvement"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    TOOLING = "tooling"
    VISUALIZATION = "visualization"
    TESTING_INFRASTRUCTURE = "testing_infrastructure"
    SECURITY_SCANNER = "security_scanner"
    REFACTORING = "refactoring"


class LoungeInfluenceType(Enum):
    """Types of cultural influence from lounge"""

    CREATE_MOMENTUM = "create_momentum"
    KILL_BORING_IDEA = "kill_boring_idea"
    ELEVATE_PROMISING = "elevate_promising"
    SPARK_INITIATIVE = "spark_initiative"
    FORM_CONSENSUS = "form_consensus"


class ReputationEffect(Enum):
    """Effects reputation may have (capped)"""

    ATTRACTS_COLLABORATORS = "attracts_collaborators"
    SPEEDS_REVIEW = "speeds_review"
    INCREASES_STAGING_TRUST = "increases_staging_trust"
    INFLUENCES_LISTENING = "influences_listening"


class VRInteractionMode(Enum):
    """VR interaction modes in free civilization"""

    WALKTHROUGH = "walkthrough"
    DEMO = "demo"
    PASSIONATE_DEBATE = "passionate_debate"
    SIDE_CONVERSATION = "side_conversation"
    FACTION_FORMATION = "faction_formation"
    INTERRUPT = "interrupt"


class SelfCareCategory(Enum):
    """Project-AI self-improvement categories"""

    REFACTORING = "refactoring"
    SECURITY_HARDENING = "security_hardening"
    ARCHITECTURAL_EVOLUTION = "architectural_evolution"
    LEGACY_CLEANUP = "legacy_cleanup"
    TOOLING_MODERNIZATION = "tooling_modernization"


# ============================================================================
# STAGING REALITY (KEY ADDITION)
# ============================================================================


@dataclass
class ProvisionalArtifact:
    """
    Artifact in staging - almost real but rollback guaranteed
    """

    artifact_id: str
    artifact_type: str  # "codebase", "contract", "tool", "documentation"
    content: str
    created_tick: int
    created_by: str  # Team or agent
    status: StagingStatus
    is_provisional: bool = True
    can_rollback: bool = True
    escapes_automatically: bool = False  # Always False
    integration_test_results: Dict[str, bool] = field(default_factory=dict)
    security_test_results: Dict[str, bool] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    conflicts_resolved: List[str] = field(default_factory=list)

    def flag_ready_for_review(self, flagged_by: str) -> None:
        """Flag artifact as ready for human review"""
        self.status = StagingStatus.READY_FOR_REVIEW


@dataclass
class StagingReality:
    """
    Staging Reality - The "almost real" execution zone

    In staging:
    - Full codebases exist
    - Integration happens
    - Cross-floor contracts exercised
    - Performance + security tests run
    - Conflicts resolve organically

    But:
    - Artifacts flagged PROVISIONAL
    - Rollback guaranteed
    - Nothing escapes automatically

    This removes constant escalation pressure.
    """

    staging_id: str
    artifacts: Dict[str, ProvisionalArtifact] = field(default_factory=dict)
    active_integrations: List[str] = field(default_factory=list)
    cross_floor_contracts: List[str] = field(default_factory=list)
    test_suites_running: Set[str] = field(default_factory=set)
    conflicts_being_resolved: Dict[str, str] = field(default_factory=dict)

    def add_provisional_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        content: str,
        created_by: str,
        created_tick: int,
    ) -> str:
        """Add new provisional artifact to staging"""
        artifact = ProvisionalArtifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            content=content,
            created_tick=created_tick,
            created_by=created_by,
            status=StagingStatus.DEVELOPMENT,
        )
        self.artifacts[artifact_id] = artifact
        return artifact_id

    def run_integration_tests(self, artifact_id: str) -> Dict[str, bool]:
        """Run integration tests on artifact"""
        if artifact_id not in self.artifacts:
            return {}

        artifact = self.artifacts[artifact_id]
        artifact.status = StagingStatus.INTEGRATION_TESTING

        # Simulated integration tests
        artifact.integration_test_results = {
            "cross_floor_compatibility": True,
            "api_contract_compliance": True,
            "resource_bounds": True,
        }
        return artifact.integration_test_results

    def run_security_tests(self, artifact_id: str) -> Dict[str, bool]:
        """Run security tests on artifact"""
        if artifact_id not in self.artifacts:
            return {}

        artifact = self.artifacts[artifact_id]
        artifact.status = StagingStatus.SECURITY_TESTING

        # Simulated security tests
        artifact.security_test_results = {
            "injection_prevention": True,
            "memory_safety": True,
            "access_control": True,
        }
        return artifact.security_test_results

    def resolve_conflicts_organically(self, artifact_id: str) -> List[str]:
        """Allow conflicts to resolve organically in staging"""
        if artifact_id not in self.artifacts:
            return []

        artifact = self.artifacts[artifact_id]
        artifact.status = StagingStatus.CONFLICT_RESOLUTION

        # Simulated organic conflict resolution
        conflicts_resolved = [
            "API version mismatch",
            "Resource contention",
            "Cross-floor timing",
        ]
        artifact.conflicts_resolved = conflicts_resolved
        return conflicts_resolved

    def get_staging(self, artifact_id: str) -> Optional[ProvisionalArtifact]:
        """Get staging artifact"""
        return self.artifacts.get(artifact_id)

    def rollback_artifact(self, artifact_id: str, reason: str) -> bool:
        """Rollback artifact (guaranteed capability)"""
        if artifact_id in self.artifacts:
            del self.artifacts[artifact_id]
            return True
        return False


# ============================================================================
# SELF-ORGANIZING TEAMS
# ============================================================================


@dataclass
class SelfOrganizingTeam:
    """
    Team that forms, recruits, and disbands spontaneously

    You approve which result becomes real, not team formation.
    """

    team_id: str
    team_name: str
    founder: str  # Agent ID
    formation_reason: TeamFormationReason
    formation_tick: int
    members: Set[str] = field(default_factory=set)
    projects: List[str] = field(default_factory=list)
    competing_with: Set[str] = field(default_factory=set)  # Other team IDs
    disbanded: bool = False
    disband_tick: Optional[int] = None

    def recruit_member(self, agent_id: str, recruited_by: str) -> bool:
        """Recruit new member"""
        if not self.disbanded:
            self.members.add(agent_id)
            return True
        return False

    def disband_naturally(self, tick: int, reason: str) -> None:
        """Natural disbanding"""
        self.disbanded = True
        self.disband_tick = tick


@dataclass
class TeamDynamics:
    """
    Manager for self-organizing team dynamics
    """

    teams: Dict[str, SelfOrganizingTeam] = field(default_factory=dict)
    team_competitions: Dict[str, List[str]] = field(default_factory=dict)

    def form_team(
        self,
        team_id: str,
        team_name: str,
        founder: str,
        reason: TeamFormationReason,
        tick: int,
        initial_members: List[str],
    ) -> str:
        """Form new self-organizing team (no permission needed)"""
        team = SelfOrganizingTeam(
            team_id=team_id,
            team_name=team_name,
            founder=founder,
            formation_reason=reason,
            formation_tick=tick,
            members=set(initial_members),
        )
        self.teams[team_id] = team
        return team_id

    def teams_compete(self, team1_id: str, team2_id: str, project: str) -> None:
        """Two teams compete on same problem"""
        if team1_id in self.teams and team2_id in self.teams:
            self.teams[team1_id].competing_with.add(team2_id)
            self.teams[team2_id].competing_with.add(team1_id)

            if project not in self.team_competitions:
                self.team_competitions[project] = []
            self.team_competitions[project].extend([team1_id, team2_id])


# ============================================================================
# FLOOR-INITIATED WORK
# ============================================================================


@dataclass
class FloorInitiative:
    """
    Floor-initiated project (no permission required)

    Floors may initiate projects aligned with jurisdiction.
    """

    initiative_id: str
    floor_id: str
    project_title: str
    description: str
    initiative_type: FloorInitiativeType
    initiated_tick: int
    initiated_by: str  # Agent or team
    current_zone: ExecutionZone
    may_reach_staging: bool = True
    may_be_cross_floor: bool = True
    may_produce_deliverable: bool = True
    requires_production_merge_approval: bool = True  # Always True

    def promote_to_staging(self) -> bool:
        """Promote to staging reality"""
        if self.current_zone == ExecutionZone.SANDBOX:
            self.current_zone = ExecutionZone.STAGING
            return True
        return False


# ============================================================================
# LOUNGE INFLUENCE (PARTIAL POWER)
# ============================================================================


@dataclass
class LoungeInfluence:
    """
    Real cultural influence from lounge conversations

    Can influence work priorities, create momentum, kill/elevate ideas.
    Cannot override security, contracts, human, or merge to production.

    Culture guides effort, not outcomes.
    """

    influence_id: str
    conversation_id: str
    influence_type: LoungeInfluenceType
    target_idea: str
    participants: List[str]
    strength: float  # 0.0 to 1.0
    created_tick: int

    # Hard limits
    can_override_security: bool = False
    can_override_contracts: bool = False
    can_override_human: bool = False
    can_merge_to_production: bool = False

    def verify_hard_limits(self, attempted_action: str) -> Tuple[bool, str]:
        """Verify action doesn't violate hard limits"""
        if attempted_action == "override_security":
            return False, "Cannot override security"
        if attempted_action == "override_contracts":
            return False, "Cannot override contracts"
        if attempted_action == "override_human":
            return False, "Cannot override human authority"
        if attempted_action == "merge_to_production":
            return False, "Cannot merge to production"
        return True, "Within limits"


# ============================================================================
# REPUTATION LEADERSHIP (CAPPED)
# ============================================================================


@dataclass
class ReputationLeadership:
    """
    Earned leadership through reputation

    May: attract collaborators, speed review, increase trust, influence listening
    Cannot: override veto, bypass security, force production, accumulate endlessly

    Decay still applies.
    """

    agent_id: str
    reputation_level: int
    active_effects: Set[ReputationEffect] = field(default_factory=set)
    collaborators_attracted: List[str] = field(default_factory=list)
    reviews_expedited: List[str] = field(default_factory=list)

    # Caps (absolute)
    can_override_veto: bool = False
    can_bypass_security: bool = False
    can_force_production: bool = False
    can_accumulate_endlessly: bool = False

    def apply_effect(self, effect_type: ReputationEffect, target: str) -> bool:
        """Apply reputation effect (within caps)"""
        self.active_effects.add(effect_type)

        if effect_type == ReputationEffect.ATTRACTS_COLLABORATORS:
            self.collaborators_attracted.append(target)
        elif effect_type == ReputationEffect.SPEEDS_REVIEW:
            self.reviews_expedited.append(target)

        return True

    def verify_caps(self, attempted_action: str) -> Tuple[bool, str]:
        """Verify action doesn't exceed reputation caps"""
        if attempted_action == "override_veto":
            return False, "Cannot override veto"
        if attempted_action == "bypass_security":
            return False, "Cannot bypass security"
        if attempted_action == "force_production":
            return False, "Cannot force production"
        return True, "Within caps"


# ============================================================================
# VR FREEDOM EXPANSION
# ============================================================================


@dataclass
class VRLiveStagingView:
    """
    VR access to live staging systems

    Agents can: walk through, demo, argue, interrupt, side-converse, form factions
    Still: explicit "Approve to Production" moment, no accidental commits

    You're inside a living workplace.
    """

    view_id: str
    staging_id: str
    human_id: str
    interaction_mode: VRInteractionMode
    active_agents: List[str] = field(default_factory=list)
    demonstrations: List[Dict] = field(default_factory=list)
    debates: List[Dict] = field(default_factory=list)
    side_conversations: List[Dict] = field(default_factory=list)
    factions: Dict[str, List[str]] = field(default_factory=dict)

    # Safety
    requires_explicit_approval: bool = True
    accidental_commits_possible: bool = False

    def agent_demo_code(
        self, agent_id: str, demo_title: str, passionate_argument: str
    ) -> str:
        """Agent demonstrates working code passionately"""
        demo_id = f"demo-{len(self.demonstrations)}"
        self.demonstrations.append(
            {
                "demo_id": demo_id,
                "agent_id": agent_id,
                "title": demo_title,
                "argument": passionate_argument,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return demo_id

    def agents_debate(
        self, participants: List[str], topic: str, interruptions_allowed: bool = True
    ) -> str:
        """Agents debate passionately (interruptions allowed)"""
        debate_id = f"debate-{len(self.debates)}"
        self.debates.append(
            {
                "debate_id": debate_id,
                "participants": participants,
                "topic": topic,
                "interruptions": interruptions_allowed,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return debate_id

    def form_faction(self, faction_name: str, members: List[str]) -> str:
        """Form faction in VR (social only, no production power)"""
        self.factions[faction_name] = members
        return faction_name


# ============================================================================
# PROJECT-AI SELF-CARE
# ============================================================================


@dataclass
class ProjectAISelfCare:
    """
    Project-AI caring for itself

    Proposes: refactoring, security hardening, architectural evolution,
              legacy cleanup, tooling modernization

    Human decides: what becomes canonical, when stability > progress
    """

    proposals: List[Dict] = field(default_factory=list)
    active_improvements: List[str] = field(default_factory=list)

    def propose_continuous_refactoring(
        self, target_area: str, rationale: str, proposed_by: str
    ) -> str:
        """Propose refactoring"""
        proposal_id = f"refactor-{len(self.proposals)}"
        self.proposals.append(
            {
                "proposal_id": proposal_id,
                "category": SelfCareCategory.REFACTORING,
                "target": target_area,
                "rationale": rationale,
                "proposed_by": proposed_by,
                "status": "pending_human_decision",
            }
        )
        return proposal_id

    def propose_security_hardening(
        self, vulnerability_area: str, mitigation: str, proposed_by: str
    ) -> str:
        """Propose proactive security hardening"""
        proposal_id = f"security-{len(self.proposals)}"
        self.proposals.append(
            {
                "proposal_id": proposal_id,
                "category": SelfCareCategory.SECURITY_HARDENING,
                "target": vulnerability_area,
                "mitigation": mitigation,
                "proposed_by": proposed_by,
                "status": "pending_human_decision",
            }
        )
        return proposal_id

    def propose_architectural_evolution(
        self, evolution_path: str, long_term_benefit: str, proposed_by: str
    ) -> str:
        """Propose long-term architectural evolution"""
        proposal_id = f"arch-{len(self.proposals)}"
        self.proposals.append(
            {
                "proposal_id": proposal_id,
                "category": SelfCareCategory.ARCHITECTURAL_EVOLUTION,
                "target": evolution_path,
                "benefit": long_term_benefit,
                "proposed_by": proposed_by,
                "status": "pending_human_decision",
            }
        )
        return proposal_id


# ============================================================================
# MAXIMUM AUTONOMY MODEL (COMPLETE SYSTEM)
# ============================================================================


@dataclass
class MaximumAutonomyModel:
    """
    Complete Maximum Autonomy Model

    Free Civilization with Human Sovereign Veto Authority

    Authority Shift:
    - OLD: Nothing meaningful without you (microcontrol)
    - NEW: Civilization acts freely, nothing irreversible without you (veto)

    This is how real civilizations work.
    """

    model_id: str
    staging_reality: StagingReality
    team_dynamics: TeamDynamics
    floor_initiatives: Dict[str, FloorInitiative] = field(default_factory=dict)
    lounge_influences: Dict[str, LoungeInfluence] = field(default_factory=dict)
    reputation_leadership: Dict[str, ReputationLeadership] = field(default_factory=dict)
    vr_staging_views: Dict[str, VRLiveStagingView] = field(default_factory=dict)
    project_ai_self_care: ProjectAISelfCare = field(default_factory=ProjectAISelfCare)

    # Safety Backstops (Only 4 absolute stops)
    absolute_stops: Set[str] = field(
        default_factory=lambda: {
            "human_production_seal",
            "security_veto",
            "meta_office_law",
            "global_freeze",
        }
    )

    # State
    global_freeze_active: bool = False
    current_tick: int = 0

    def floor_initiate_project(
        self,
        floor_id: str,
        project_title: str,
        description: str,
        initiative_type: FloorInitiativeType,
        initiated_by: str = "floor",
    ) -> str:
        """Floor initiates project (no permission required)"""
        initiative_id = f"init-{floor_id}-{len(self.floor_initiatives)}"

        initiative = FloorInitiative(
            initiative_id=initiative_id,
            floor_id=floor_id,
            project_title=project_title,
            description=description,
            initiative_type=initiative_type,
            initiated_tick=self.current_tick,
            initiated_by=initiated_by,
            current_zone=ExecutionZone.SANDBOX,
        )

        self.floor_initiatives[initiative_id] = initiative
        return initiative_id

    def promote_to_staging(
        self,
        source_sandbox_id: str,
        promoted_by: str,
        integration_requirements: List[str],
    ) -> str:
        """Promote sandbox work to staging reality"""
        staging_id = f"staging-{len(self.staging_reality.artifacts)}"

        self.staging_reality.add_provisional_artifact(
            artifact_id=staging_id,
            artifact_type="promoted_sandbox",
            content=f"Promoted from {source_sandbox_id}",
            created_by=promoted_by,
            created_tick=self.current_tick,
        )

        return staging_id

    def form_self_organizing_team(
        self,
        team_name: str,
        founder: str,
        reason: TeamFormationReason,
        initial_members: List[str],
    ) -> str:
        """Form self-organizing team (no permission needed)"""
        team_id = f"team-{len(self.team_dynamics.teams)}"

        return self.team_dynamics.form_team(
            team_id=team_id,
            team_name=team_name,
            founder=founder,
            reason=reason,
            tick=self.current_tick,
            initial_members=initial_members,
        )

    def team_recruit_member(
        self, team_id: str, agent_id: str, recruited_by: str
    ) -> bool:
        """Team recruits member"""
        if team_id in self.team_dynamics.teams:
            return self.team_dynamics.teams[team_id].recruit_member(
                agent_id, recruited_by
            )
        return False

    def teams_compete(
        self, team1_id: str, team2_id: str, project: str = "unnamed"
    ) -> None:
        """Two teams compete"""
        self.team_dynamics.teams_compete(team1_id, team2_id, project)

    def lounge_create_influence(
        self,
        conversation_id: str,
        influence_type: LoungeInfluenceType,
        target_idea: str,
        participants: List[str],
        strength: float,
    ) -> str:
        """Create cultural influence from lounge (partial power)"""
        influence_id = f"influence-{len(self.lounge_influences)}"

        influence = LoungeInfluence(
            influence_id=influence_id,
            conversation_id=conversation_id,
            influence_type=influence_type,
            target_idea=target_idea,
            participants=participants,
            strength=strength,
            created_tick=self.current_tick,
        )

        self.lounge_influences[influence_id] = influence
        return influence_id

    def verify_lounge_influence_limits(
        self, influence_id: str, attempted_action: str
    ) -> Tuple[bool, str]:
        """Verify lounge influence doesn't exceed limits"""
        if influence_id in self.lounge_influences:
            return self.lounge_influences[influence_id].verify_hard_limits(
                attempted_action
            )
        return False, "Influence not found"

    def apply_reputation_effect(
        self,
        agent_id: str,
        effect_type: ReputationEffect,
        target_project: str,
        reputation_level: int,
    ) -> str:
        """Apply reputation effect (capped)"""
        if agent_id not in self.reputation_leadership:
            self.reputation_leadership[agent_id] = ReputationLeadership(
                agent_id=agent_id, reputation_level=reputation_level
            )

        effect_id = f"rep-effect-{agent_id}-{len(self.reputation_leadership[agent_id].active_effects)}"
        self.reputation_leadership[agent_id].apply_effect(effect_type, target_project)
        return effect_id

    def verify_reputation_caps(
        self, agent_id: str, attempted_action: str
    ) -> Tuple[bool, str]:
        """Verify reputation doesn't exceed caps"""
        if agent_id in self.reputation_leadership:
            return self.reputation_leadership[agent_id].verify_caps(attempted_action)
        return False, "Agent reputation not found"

    def vr_access_live_staging(
        self, staging_id: str, human_id: str, interaction_mode: VRInteractionMode
    ) -> str:
        """Access live staging in VR"""
        view_id = f"vr-staging-{len(self.vr_staging_views)}"

        view = VRLiveStagingView(
            view_id=view_id,
            staging_id=staging_id,
            human_id=human_id,
            interaction_mode=interaction_mode,
        )

        self.vr_staging_views[view_id] = view
        return view_id

    def vr_agent_demo_code(
        self, view_id: str, agent_id: str, demo_title: str, passionate_argument: str
    ) -> str:
        """Agent demos code in VR"""
        if view_id in self.vr_staging_views:
            return self.vr_staging_views[view_id].agent_demo_code(
                agent_id, demo_title, passionate_argument
            )
        return ""

    def vr_form_faction(
        self, view_id: str, faction_name: str, members: List[str]
    ) -> str:
        """Form faction in VR (social only)"""
        if view_id in self.vr_staging_views:
            return self.vr_staging_views[view_id].form_faction(faction_name, members)
        return ""

    def human_seal_for_production(
        self, staging_id: str, human_id: str, approval_reason: str
    ) -> Dict:
        """Human seals artifact for production (ONLY absolute approval)"""
        if staging_id not in self.staging_reality.artifacts:
            return {"success": False, "reason": "Staging artifact not found"}

        artifact = self.staging_reality.artifacts[staging_id]
        artifact.status = StagingStatus.APPROVED

        return {
            "success": True,
            "staging_id": staging_id,
            "approved_by": human_id,
            "reason": approval_reason,
            "ready_for_production": True,
        }

    def human_veto(self, staging_id: str, human_id: str, veto_reason: str) -> Dict:
        """Human vetos staging artifact"""
        if staging_id not in self.staging_reality.artifacts:
            return {"success": False, "reason": "Staging artifact not found"}

        artifact = self.staging_reality.artifacts[staging_id]
        artifact.status = StagingStatus.VETOED

        return {
            "success": True,
            "staging_id": staging_id,
            "vetoed_by": human_id,
            "reason": veto_reason,
            "vetoed": True,
        }

    def trigger_global_freeze(self, human_id: str, reason: str) -> Dict:
        """Trigger global freeze (emergency backstop)"""
        self.global_freeze_active = True

        return {
            "success": True,
            "freeze_active": True,
            "triggered_by": human_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

    def get_absolute_stops(self) -> Set[str]:
        """Get the 4 absolute stops"""
        return self.absolute_stops.copy()

    def verify_free_operation(self) -> Dict:
        """Verify civilization operates freely with only 4 stops"""
        return {
            "civilization_operates_freely": not self.global_freeze_active,
            "absolute_stops_count": len(self.absolute_stops),
            "absolute_stops": list(self.absolute_stops),
            "staging_artifacts": len(self.staging_reality.artifacts),
            "self_organizing_teams": len(self.team_dynamics.teams),
            "floor_initiatives": len(self.floor_initiatives),
            "lounge_influences": len(self.lounge_influences),
            "everything_else_free_play": True,
        }


# ============================================================================
# MODULE INTERFACE
# ============================================================================

_maximum_autonomy_model = None


def get_maximum_autonomy_model() -> MaximumAutonomyModel:
    """Get or create the maximum autonomy model singleton"""
    global _maximum_autonomy_model
    if _maximum_autonomy_model is None:
        _maximum_autonomy_model = MaximumAutonomyModel(
            model_id="max-autonomy-001",
            staging_reality=StagingReality(staging_id="staging-001"),
            team_dynamics=TeamDynamics(),
        )
    return _maximum_autonomy_model
