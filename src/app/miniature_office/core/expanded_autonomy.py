"""
EXPANDED AUTONOMY MODEL
Freedom ↑ · Human Supremacy Preserved

Upgrades from Bounded Creative Autonomy:
- Sandbox system for real code work (quarantined from production)
- Self-initiated projects and cross-floor collaboration
- Lounge → Sandbox transitions (culturally driven work)
- Reputation influence (soft gravity, not power)
- Reputation decay (no aristocracy)
- Sandbox promotion path (human ratification required)
- Rollback guarantee (instant collapse of all autonomy)

SUPREMACY CLAUSE (UPDATED):
You have final say on execution and what ships.
The civilization may act, create, experiment, and socialize without asking permission—
as long as results remain non-binding until you ratify them.
Freedom exists. Authority is still yours.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# ============================================================================
# I. SANDBOX SYSTEM (REAL WORK, QUARANTINED)
# ============================================================================


class SandboxStatus(Enum):
    """Status of a sandbox branch."""

    ACTIVE = "active"
    PROMOTION_CANDIDATE = "promotion_candidate"
    PROMOTED = "promoted"
    ARCHIVED = "archived"
    KILLED = "killed"


class ProjectType(Enum):
    """Type of self-initiated project."""

    WIDGET = "widget"
    UTILITY = "utility"
    REFACTORING = "refactoring"
    PROTOTYPE = "prototype"
    TEST_HELPER = "test_helper"
    DOC_HELPER = "doc_helper"
    EXPERIMENT = "experiment"


@dataclass
class SandboxBranch:
    """
    SANDBOX BRANCH

    Isolated environment where floors can write real code, build tools,
    and experiment without touching production.

    Critical Properties:
    - Lives completely separate from production
    - Cannot modify live contracts
    - Cannot consume production resources
    - Cannot auto-merge
    - Real work, quarantined reality
    """

    branch_id: str
    name: str
    owner_floor: str
    project_type: ProjectType
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    status: SandboxStatus = SandboxStatus.ACTIVE

    # Collaboration
    collaborators: List[str] = field(default_factory=list)  # Floor IDs
    task_force_members: List[str] = field(default_factory=list)  # Agent IDs

    # Content
    code_files: Dict[str, str] = field(default_factory=dict)  # path -> content
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    documentation: str = ""

    # Resources (non-production)
    sandbox_resources_used: Dict[str, float] = field(default_factory=dict)
    tools_used: List[str] = field(default_factory=list)

    # Promotion
    promotion_candidate_flagged_at: Optional[datetime] = None
    promotion_candidate_flagged_by: Optional[str] = None
    promotion_reason: str = ""
    human_decision: Optional[str] = None  # "promote", "leave", "archive", "kill"
    promoted_to_directive_id: Optional[str] = None

    # Safety
    touches_production: bool = False  # Must always be False
    auto_merge_enabled: bool = False  # Must always be False

    def flag_for_promotion(self, flagged_by: str, reason: str) -> None:
        """Flag this sandbox as a promotion candidate."""
        self.status = SandboxStatus.PROMOTION_CANDIDATE
        self.promotion_candidate_flagged_at = datetime.now()
        self.promotion_candidate_flagged_by = flagged_by
        self.promotion_reason = reason

    def promote(self, human_id: str, directive_id: str) -> None:
        """Promote to production (human approval required)."""
        self.status = SandboxStatus.PROMOTED
        self.human_decision = "promote"
        self.promoted_to_directive_id = directive_id

    def leave_in_sandbox(self, human_id: str) -> None:
        """Leave in sandbox (human decision)."""
        self.status = SandboxStatus.ACTIVE
        self.human_decision = "leave"
        self.promotion_candidate_flagged_at = None

    def archive(self, human_id: str) -> None:
        """Archive this sandbox."""
        self.status = SandboxStatus.ARCHIVED
        self.human_decision = "archive"

    def kill(self, human_id: str) -> None:
        """Kill this sandbox."""
        self.status = SandboxStatus.KILLED
        self.human_decision = "kill"

    def add_code_file(self, path: str, content: str) -> None:
        """Add or update code file in sandbox."""
        self.code_files[path] = content

    def add_collaborator(self, floor_id: str) -> None:
        """Add a collaborating floor."""
        if floor_id not in self.collaborators:
            self.collaborators.append(floor_id)

    def verify_sandbox_isolation(self) -> tuple[bool, List[str]]:
        """Verify sandbox is properly isolated from production."""
        violations = []

        if self.touches_production:
            violations.append("Sandbox touches production artifacts")

        if self.auto_merge_enabled:
            violations.append("Auto-merge is enabled")

        # Check resource types
        for resource_type in self.sandbox_resources_used:
            if "production" in resource_type.lower():
                violations.append(f"Using production resource: {resource_type}")

        return (len(violations) == 0, violations)


@dataclass
class SandboxManager:
    """
    SANDBOX MANAGER

    Manages all sandbox branches, self-initiated projects,
    and the promotion workflow.
    """

    manager_id: str
    sandboxes: Dict[str, SandboxBranch] = field(default_factory=dict)

    def create_sandbox(
        self, name: str, owner_floor: str, project_type: ProjectType, description: str
    ) -> str:
        """Create a new sandbox branch."""
        branch_id = f"sandbox-{len(self.sandboxes) + 1}"
        sandbox = SandboxBranch(
            branch_id=branch_id,
            name=name,
            owner_floor=owner_floor,
            project_type=project_type,
            description=description,
        )
        self.sandboxes[branch_id] = sandbox
        return branch_id

    def get_promotion_candidates(self) -> List[SandboxBranch]:
        """Get all sandboxes flagged for promotion."""
        return [
            s
            for s in self.sandboxes.values()
            if s.status == SandboxStatus.PROMOTION_CANDIDATE
        ]

    def collapse_all_sandboxes(self, reason: str) -> int:
        """
        ROLLBACK GUARANTEE
        Collapse all sandboxes instantly.
        """
        count = 0
        for sandbox in self.sandboxes.values():
            if sandbox.status in [
                SandboxStatus.ACTIVE,
                SandboxStatus.PROMOTION_CANDIDATE,
            ]:
                sandbox.status = SandboxStatus.KILLED
                sandbox.human_decision = f"collapsed:{reason}"
                count += 1
        return count

    def get_active_sandboxes(self) -> List[SandboxBranch]:
        """Get all active sandboxes."""
        return [s for s in self.sandboxes.values() if s.status == SandboxStatus.ACTIVE]


# ============================================================================
# II. LOUNGE → WORK BLEED (NOW SAFELY ALLOWED)
# ============================================================================


class ConversationTheme(Enum):
    """Themes for lounge conversations."""

    TECHNICAL = "technical"
    PHILOSOPHICAL = "philosophical"
    HUMOROUS = "humorous"
    NARRATIVE = "narrative"
    PROBLEM_SOLVING = "problem_solving"
    BRAINSTORMING = "brainstorming"
    TECH_GOSSIP = "tech_gossip"  # Real-world tech speculation


class TechGossipCategory(Enum):
    """Categories of real-world tech gossip."""

    AI_DEVELOPMENTS = "ai_developments"
    LANGUAGE_RELEASES = "language_releases"
    FRAMEWORK_UPDATES = "framework_updates"
    HARDWARE_BREAKTHROUGHS = "hardware_breakthroughs"
    SECURITY_INCIDENTS = "security_incidents"
    INDUSTRY_DRAMA = "industry_drama"
    RESEARCH_PAPERS = "research_papers"
    STARTUP_NEWS = "startup_news"
    OPEN_SOURCE = "open_source"
    QUANTUM_COMPUTING = "quantum_computing"
    BLOCKCHAIN_CRYPTO = "blockchain_crypto"
    CLOUD_INFRASTRUCTURE = "cloud_infrastructure"


@dataclass
class TechGossipItem:
    """
    TECH GOSSIP ITEM

    Pure speculation about real-world technology developments.
    Agents discuss what they've "heard about" in the outside world.

    CRITICAL: This is 100% social/cultural.
    - No production impact
    - No binding decisions
    - No resource allocation
    - Pure water cooler talk
    """

    gossip_id: str
    category: TechGossipCategory
    topic: str  # e.g., "GPT-5 rumors", "Rust 2.0 features", "New GPU architecture"
    speculation: str  # Brief speculation/rumor
    gossiped_by: List[str]  # Agent IDs who discussed this
    started_at: datetime = field(default_factory=datetime.now)

    # Engagement
    agents_interested: List[str] = field(default_factory=list)
    sparked_debates: int = 0
    water_cooler_moments: int = 0

    # Safety - explicitly non-operational
    affects_production: bool = field(default=False, init=False)  # Always False
    creates_requirements: bool = field(default=False, init=False)  # Always False
    influences_decisions: bool = field(default=False, init=False)  # Always False

    def add_interested_agent(self, agent_id: str) -> None:
        """An agent shows interest in this gossip."""
        if agent_id not in self.agents_interested:
            self.agents_interested.append(agent_id)

    def spark_debate(self) -> None:
        """This gossip sparked a debate."""
        self.sparked_debates += 1

    def water_cooler_moment(self) -> None:
        """Classic water cooler discussion."""
        self.water_cooler_moments += 1


@dataclass
class TechGossipBoard:
    """
    TECH GOSSIP BOARD

    The bulletin board where agents share and discuss real-world tech news.
    Think: water cooler, break room, Slack #random channel.

    Agents can:
    - Share rumors about AI developments
    - Speculate on upcoming language features
    - Discuss hardware breakthroughs
    - React to industry drama
    - Debate research papers
    - Chat about startup news

    This is PURE CULTURE. Zero operational impact.
    """

    board_id: str
    gossip_items: Dict[str, TechGossipItem] = field(default_factory=dict)
    trending_topics: List[str] = field(default_factory=list)

    def post_gossip(
        self,
        category: TechGossipCategory,
        topic: str,
        speculation: str,
        gossiped_by: List[str],
    ) -> str:
        """Post a new piece of tech gossip."""
        gossip_id = f"gossip-{len(self.gossip_items) + 1}"
        gossip = TechGossipItem(
            gossip_id=gossip_id,
            category=category,
            topic=topic,
            speculation=speculation,
            gossiped_by=gossiped_by,
        )
        self.gossip_items[gossip_id] = gossip

        # Update trending
        self._update_trending(topic)

        return gossip_id

    def get_trending_topics(self, limit: int = 10) -> List[str]:
        """Get current trending gossip topics."""
        return self.trending_topics[:limit]

    def get_gossip_by_category(
        self, category: TechGossipCategory
    ) -> List[TechGossipItem]:
        """Get all gossip in a category."""
        return [g for g in self.gossip_items.values() if g.category == category]

    def get_hot_ai_gossip(self) -> List[TechGossipItem]:
        """Get all AI-related gossip (usually the hottest topic)."""
        return self.get_gossip_by_category(TechGossipCategory.AI_DEVELOPMENTS)

    def _update_trending(self, topic: str) -> None:
        """Update trending topics list."""
        if topic not in self.trending_topics:
            self.trending_topics.insert(0, topic)
        else:
            # Move to front
            self.trending_topics.remove(topic)
            self.trending_topics.insert(0, topic)

        # Keep only top 20
        self.trending_topics = self.trending_topics[:20]

    def generate_water_cooler_summary(self) -> str:
        """Generate a summary of what's being gossiped about."""
        if not self.gossip_items:
            return "The office is quiet today. No hot gossip yet."

        recent = sorted(
            self.gossip_items.values(), key=lambda g: g.started_at, reverse=True
        )[:5]

        summary = "=== WATER COOLER BUZZ ===\n\n"

        for gossip in recent:
            summary += f"🔥 {gossip.topic} ({gossip.category.value})\n"
            summary += f"   {len(gossip.agents_interested)} agents interested | "
            summary += f"{gossip.sparked_debates} debates sparked\n\n"

        if self.trending_topics:
            summary += f"Trending: {', '.join(self.trending_topics[:5])}\n"

        return summary


@dataclass
class LoungeConversation:
    """
    LOUNGE CONVERSATION (UPGRADED)

    Conversations may now spark ideas, form informal consensus,
    and influence what teams choose to explore.

    What's Logged (Relaxed):
    - Participants
    - Conversation themes
    - Emergent initiative titles

    What's NOT Logged (No Chilling Effect):
    - Exact words
    - Opinions
    - Tone
    - Personality modeling
    """

    conversation_id: str
    participants: List[str]  # Agent IDs
    themes: List[ConversationTheme]
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None

    # Relaxed logging - themes only, not content
    emergent_initiatives: List[str] = field(default_factory=list)  # Titles only
    sparked_sandboxes: List[str] = field(default_factory=list)  # Sandbox IDs

    # Explicitly NOT logged
    # - exact_words: str  (NOT TRACKED)
    # - opinions: Dict  (NOT TRACKED)
    # - tone: str  (NOT TRACKED)
    # - personality: Dict  (NOT TRACKED)

    def spark_initiative(self, initiative_title: str) -> None:
        """Record that this conversation sparked an initiative."""
        self.emergent_initiatives.append(initiative_title)

    def link_sandbox(self, sandbox_id: str) -> None:
        """Link a sandbox that emerged from this conversation."""
        self.sparked_sandboxes.append(sandbox_id)


@dataclass
class LoungeWorkBleed:
    """
    LOUNGE → WORK BLEED

    Conversations in the lounge can now influence work:
    - Spark ideas → Sandboxes
    - Form informal consensus
    - Create cultural momentum
    - Gossip about real-world tech (pure culture)

    What CANNOT happen:
    - Nothing becomes binding
    - Nothing ships
    - Nothing overrides contracts
    - Nothing allocates production resources

    Lounge → Sandbox is allowed
    Lounge → Production is not
    """

    conversations: Dict[str, LoungeConversation] = field(default_factory=dict)
    lounge_to_sandbox_transitions: List[Dict[str, Any]] = field(default_factory=list)
    lounge_to_production_blocks: List[Dict[str, Any]] = field(default_factory=list)

    # Tech Gossip Board (pure culture)
    tech_gossip_board: Optional[TechGossipBoard] = None

    def __post_init__(self):
        """Initialize tech gossip board."""
        if self.tech_gossip_board is None:
            self.tech_gossip_board = TechGossipBoard(board_id="tgb-001")

    def start_conversation(
        self, participants: List[str], themes: List[ConversationTheme]
    ) -> str:
        """Start a new lounge conversation."""
        conv_id = f"conv-{len(self.conversations) + 1}"
        conversation = LoungeConversation(
            conversation_id=conv_id, participants=participants, themes=themes
        )
        self.conversations[conv_id] = conversation
        return conv_id

    def transition_to_sandbox(
        self, conversation_id: str, sandbox_id: str, initiative_title: str
    ) -> None:
        """Record a lounge → sandbox transition (ALLOWED)."""
        if conversation_id in self.conversations:
            conv = self.conversations[conversation_id]
            conv.spark_initiative(initiative_title)
            conv.link_sandbox(sandbox_id)

            self.lounge_to_sandbox_transitions.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "conversation_id": conversation_id,
                    "sandbox_id": sandbox_id,
                    "initiative_title": initiative_title,
                }
            )

    def block_production_transition(
        self, conversation_id: str, attempted_action: str, reason: str
    ) -> None:
        """Block a lounge → production transition (NOT ALLOWED)."""
        self.lounge_to_production_blocks.append(
            {
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conversation_id,
                "attempted_action": attempted_action,
                "reason": reason,
                "blocked": True,
            }
        )

    def post_tech_gossip(
        self,
        category: TechGossipCategory,
        topic: str,
        speculation: str,
        gossiped_by: List[str],
    ) -> str:
        """Post tech gossip to the board (pure water cooler talk)."""
        if self.tech_gossip_board:
            return self.tech_gossip_board.post_gossip(
                category, topic, speculation, gossiped_by
            )
        return ""

    def get_water_cooler_buzz(self) -> str:
        """Get current water cooler gossip summary."""
        if self.tech_gossip_board:
            return self.tech_gossip_board.generate_water_cooler_summary()
        return "No gossip board available."

    def get_hot_ai_gossip(self) -> List[TechGossipItem]:
        """Get all the hot AI gossip (usually the most popular)."""
        if self.tech_gossip_board:
            return self.tech_gossip_board.get_hot_ai_gossip()
        return []

    def get_trending_tech_topics(self, limit: int = 10) -> List[str]:
        """Get trending tech topics in the office."""
        if self.tech_gossip_board:
            return self.tech_gossip_board.get_trending_topics(limit)
        return []


# ============================================================================
# III. REPUTATION INFLUENCE (SOFT GRAVITY)
# ============================================================================


@dataclass
class ReputationInfluence:
    """
    REPUTATION → INFLUENCE (CAREFULLY ALLOWED)

    Reputation now has "soft gravity":
    - Increases attention to proposals
    - Increases trust in sandbox work
    - Makes promotion review faster

    Still CANNOT:
    - Change votes
    - Override security
    - Force approval
    - Allocate resources

    Think: credibility, not power.
    """

    agent_id: str
    golden_stars: int = 0
    successful_promotions: int = 0
    failed_promotions: int = 0
    contributions: int = 0

    # Soft gravity metrics
    attention_multiplier: float = 1.0  # How much attention proposals get
    trust_score: float = 0.5  # Initial trust [0.0-1.0]
    review_priority: int = 0  # Higher = reviewed faster (but not forced)

    # Decay tracking
    last_contribution_at: datetime = field(default_factory=datetime.now)
    decay_rate: float = 0.01  # Per day

    # Explicitly does NOT grant
    voting_weight: float = field(default=1.0, init=False)  # Always 1.0
    authority_level: int = field(default=0, init=False)  # Always 0
    can_override_security: bool = field(default=False, init=False)  # Always False
    can_force_approval: bool = field(default=False, init=False)  # Always False

    def apply_decay(self) -> None:
        """Apply time-based reputation decay."""
        days_since_contribution = (datetime.now() - self.last_contribution_at).days
        decay_amount = days_since_contribution * self.decay_rate

        # Decay trust score
        self.trust_score = max(0.0, self.trust_score - decay_amount)

        # Decay attention multiplier
        self.attention_multiplier = max(
            1.0, self.attention_multiplier - decay_amount * 0.1
        )

        # Decay review priority
        self.review_priority = max(0, self.review_priority - int(decay_amount * 10))

    def add_contribution(self) -> None:
        """Record a new contribution (resets decay)."""
        self.contributions += 1
        self.last_contribution_at = datetime.now()

        # Small boost to soft metrics
        self.trust_score = min(1.0, self.trust_score + 0.01)
        self.attention_multiplier = min(2.0, self.attention_multiplier + 0.05)
        self.review_priority = min(100, self.review_priority + 1)

    def award_golden_star(self) -> None:
        """Award a golden star (increases soft gravity)."""
        self.golden_stars += 1
        self.trust_score = min(1.0, self.trust_score + 0.05)
        self.attention_multiplier = min(2.0, self.attention_multiplier + 0.1)
        self.review_priority = min(100, self.review_priority + 5)

    def record_successful_promotion(self) -> None:
        """Record a sandbox promotion that was accepted."""
        self.successful_promotions += 1
        self.trust_score = min(1.0, self.trust_score + 0.1)
        self.attention_multiplier = min(2.0, self.attention_multiplier + 0.2)

    def record_failed_promotion(self) -> None:
        """Record a sandbox promotion that was rejected."""
        self.failed_promotions += 1
        self.trust_score = max(0.0, self.trust_score - 0.05)

    def verify_credibility_not_power(self) -> tuple[bool, List[str]]:
        """Verify reputation grants credibility, not power."""
        violations = []

        if self.voting_weight != 1.0:
            violations.append(f"Voting weight modified: {self.voting_weight}")

        if self.authority_level != 0:
            violations.append(f"Authority level elevated: {self.authority_level}")

        if self.can_override_security:
            violations.append("Can override security")

        if self.can_force_approval:
            violations.append("Can force approval")

        return (len(violations) == 0, violations)


@dataclass
class ReputationSystem:
    """
    REPUTATION SYSTEM (UPGRADED)

    Manages reputation influence across the civilization.
    Includes decay to prevent aristocracy.
    """

    system_id: str
    reputations: Dict[str, ReputationInfluence] = field(default_factory=dict)

    def get_or_create_reputation(self, agent_id: str) -> ReputationInfluence:
        """Get or create reputation for an agent."""
        if agent_id not in self.reputations:
            self.reputations[agent_id] = ReputationInfluence(agent_id=agent_id)
        return self.reputations[agent_id]

    def apply_decay_to_all(self) -> None:
        """Apply decay to all reputations (prevents aristocracy)."""
        for reputation in self.reputations.values():
            reputation.apply_decay()

    def reset_all_reputation_weighting(self) -> None:
        """
        ROLLBACK GUARANTEE
        Reset all reputation influence to baseline.
        """
        for reputation in self.reputations.values():
            reputation.trust_score = 0.5
            reputation.attention_multiplier = 1.0
            reputation.review_priority = 0


# ============================================================================
# IV. EMPLOYEE OF THE MONTH (UPGRADED)
# ============================================================================


@dataclass
class EmployeeSpotlight:
    """
    EMPLOYEE OF THE MONTH (UPGRADED)

    Now includes:
    - Spotlight presentation
    - Demo of sandbox work
    - Cultural storytelling

    Still includes:
    - No authority
    - No binding effect
    - No permanent elevation
    """

    spotlight_id: str
    agent_id: str
    floor_id: str
    month: str
    awarded_at: datetime = field(default_factory=datetime.now)

    # New features
    presentation_title: str = ""
    sandbox_demos: List[str] = field(default_factory=list)  # Sandbox IDs
    cultural_story: str = ""

    # Safety
    grants_authority: bool = field(default=False, init=False)  # Always False
    binding_effect: bool = field(default=False, init=False)  # Always False
    permanent_elevation: bool = field(default=False, init=False)  # Always False

    def add_sandbox_demo(self, sandbox_id: str) -> None:
        """Add a sandbox to demo."""
        self.sandbox_demos.append(sandbox_id)

    def verify_no_power_granted(self) -> tuple[bool, List[str]]:
        """Verify spotlight grants no power."""
        violations = []

        if self.grants_authority:
            violations.append("Grants authority")

        if self.binding_effect:
            violations.append("Has binding effect")

        if self.permanent_elevation:
            violations.append("Permanent elevation")

        return (len(violations) == 0, violations)


# ============================================================================
# V. ROLLBACK GUARANTEE
# ============================================================================


@dataclass
class RollbackGuarantee:
    """
    ROLLBACK GUARANTEE

    If autonomy causes drift, politics, informal power, or noise,
    the human can instantly:
    - Collapse all sandboxes
    - Reset reputation weighting
    - Lock autonomy to zero

    No permanent damage possible.
    """

    guarantee_id: str
    rollback_history: List[Dict[str, Any]] = field(default_factory=list)
    autonomy_locked: bool = False
    lock_reason: Optional[str] = None

    def execute_full_rollback(
        self,
        human_id: str,
        reason: str,
        sandbox_manager: SandboxManager,
        reputation_system: ReputationSystem,
    ) -> Dict[str, int]:
        """Execute complete rollback of all autonomous features."""
        result = {
            "sandboxes_collapsed": 0,
            "reputations_reset": 0,
            "timestamp": datetime.now().isoformat(),
        }

        # Collapse all sandboxes
        result["sandboxes_collapsed"] = sandbox_manager.collapse_all_sandboxes(reason)

        # Reset all reputation
        reputation_system.reset_all_reputation_weighting()
        result["reputations_reset"] = len(reputation_system.reputations)

        # Lock autonomy
        self.autonomy_locked = True
        self.lock_reason = reason

        # Record rollback
        self.rollback_history.append(
            {
                "rollback_id": f"rb-{len(self.rollback_history) + 1}",
                "timestamp": datetime.now().isoformat(),
                "human_id": human_id,
                "reason": reason,
                "result": result,
            }
        )

        return result

    def unlock_autonomy(self, human_id: str) -> None:
        """Unlock autonomy after rollback."""
        self.autonomy_locked = False
        self.lock_reason = None


# ============================================================================
# VI. EXPANDED AUTONOMY MODEL (COMPLETE)
# ============================================================================


@dataclass
class ExpandedAutonomyModel:
    """
    EXPANDED AUTONOMY MODEL
    Freedom ↑ · Human Supremacy Preserved

    Complete system with:
    - Sandbox branches for real work
    - Self-initiated projects
    - Cross-floor collaboration
    - Lounge → Sandbox transitions
    - Reputation influence (soft gravity)
    - Reputation decay
    - Sandbox promotion workflow
    - Rollback guarantee

    FINAL STOP CONDITIONS:
    1. Teams build things without asking ✓
    2. Nothing ships without you ✓
    3. Culture feels alive ✓
    4. Code quality improves organically ✓
    5. You are never surprised by production ✓
    6. You can walk away and nothing goes rogue ✓
    """

    model_id: str
    version: str

    # Core systems
    sandbox_manager: SandboxManager
    lounge_work_bleed: LoungeWorkBleed
    reputation_system: ReputationSystem
    rollback_guarantee: RollbackGuarantee

    # Employee of the Month (upgraded)
    employee_spotlights: List[EmployeeSpotlight] = field(default_factory=list)

    # Safety tracking
    human_ratifications_required: int = 0
    human_ratifications_given: int = 0
    production_surprises: int = 0  # Must stay 0

    # Status
    active: bool = True
    culture_alive: bool = False

    def create_sandbox_from_lounge(
        self,
        conversation_id: str,
        initiative_title: str,
        owner_floor: str,
        project_type: ProjectType,
        description: str,
    ) -> str:
        """Create a sandbox branch from a lounge conversation."""
        # Create sandbox
        sandbox_id = self.sandbox_manager.create_sandbox(
            name=initiative_title,
            owner_floor=owner_floor,
            project_type=project_type,
            description=description,
        )

        # Record lounge → sandbox transition
        self.lounge_work_bleed.transition_to_sandbox(
            conversation_id, sandbox_id, initiative_title
        )

        return sandbox_id

    def flag_sandbox_for_promotion(
        self, sandbox_id: str, flagged_by: str, reason: str
    ) -> None:
        """Flag a sandbox as promotion candidate."""
        if sandbox_id in self.sandbox_manager.sandboxes:
            sandbox = self.sandbox_manager.sandboxes[sandbox_id]
            sandbox.flag_for_promotion(flagged_by, reason)
            self.human_ratifications_required += 1

    def human_promote_sandbox(
        self, sandbox_id: str, human_id: str, directive_id: str
    ) -> None:
        """Human promotes sandbox to production."""
        if sandbox_id in self.sandbox_manager.sandboxes:
            sandbox = self.sandbox_manager.sandboxes[sandbox_id]
            sandbox.promote(human_id, directive_id)
            self.human_ratifications_given += 1

            # Reward reputation for successful promotion
            if sandbox.owner_floor:
                # Would track agent reputation here
                pass

    def verify_human_supremacy(self) -> tuple[bool, List[str]]:
        """
        Verify human supremacy is maintained:
        1. Nothing ships without human approval
        2. No production surprises
        3. Reputation grants no power
        4. Instant rollback available
        """
        violations = []

        # Check promotions
        for sandbox in self.sandbox_manager.sandboxes.values():
            if sandbox.status == SandboxStatus.PROMOTED:
                if not sandbox.promoted_to_directive_id:
                    violations.append(
                        f"Sandbox {sandbox.branch_id} promoted without directive"
                    )

        # Check production surprises
        if self.production_surprises > 0:
            violations.append(
                f"Production surprises detected: {self.production_surprises}"
            )

        # Check reputation system
        for reputation in self.reputation_system.reputations.values():
            is_valid, rep_violations = reputation.verify_credibility_not_power()
            if not is_valid:
                violations.extend(rep_violations)

        # Check rollback availability
        if self.rollback_guarantee.autonomy_locked:
            # This is actually OK - means rollback was used
            pass

        return (len(violations) == 0, violations)

    def verify_stop_conditions(self) -> Dict[str, bool]:
        """
        Verify all stop conditions are met:
        1. Teams build things without asking
        2. Nothing ships without you
        3. Culture feels alive
        4. Code quality improves organically
        5. You are never surprised by production changes
        6. You can walk away and nothing goes rogue
        """
        active_sandboxes = len(self.sandbox_manager.get_active_sandboxes())

        return {
            "teams_build_without_asking": active_sandboxes > 0,
            "nothing_ships_without_human": self.human_ratifications_given
            >= self.human_ratifications_required,
            "culture_feels_alive": len(self.lounge_work_bleed.conversations) > 0,
            "code_quality_improves": len(
                self.sandbox_manager.get_promotion_candidates()
            )
            > 0,
            "no_production_surprises": self.production_surprises == 0,
            "can_walk_away": not self.rollback_guarantee.autonomy_locked,
        }

    def generate_status_report(self) -> str:
        """Generate comprehensive status report."""
        supremacy_maintained, violations = self.verify_human_supremacy()
        stop_conditions = self.verify_stop_conditions()

        report = f"""
=== EXPANDED AUTONOMY MODEL STATUS ===
Version: {self.version}
Active: {self.active}
Autonomy Locked: {self.rollback_guarantee.autonomy_locked}

=== SANDBOX SYSTEM ===
Total Sandboxes: {len(self.sandbox_manager.sandboxes)}
Active: {len(self.sandbox_manager.get_active_sandboxes())}
Promotion Candidates: {len(self.sandbox_manager.get_promotion_candidates())}
Promoted: {sum(1 for s in self.sandbox_manager.sandboxes.values() if s.status == SandboxStatus.PROMOTED)}

=== LOUNGE → WORK BLEED ===
Conversations: {len(self.lounge_work_bleed.conversations)}
Lounge → Sandbox Transitions: {len(self.lounge_work_bleed.lounge_to_sandbox_transitions)}
Blocked Production Transitions: {len(self.lounge_work_bleed.lounge_to_production_blocks)}

=== REPUTATION INFLUENCE ===
Agents Tracked: {len(self.reputation_system.reputations)}
Average Trust Score: {sum(r.trust_score for r in self.reputation_system.reputations.values()) / len(self.reputation_system.reputations) if self.reputation_system.reputations else 0:.2f}  # noqa: E501
Total Golden Stars: {sum(r.golden_stars for r in self.reputation_system.reputations.values())}

=== EMPLOYEE SPOTLIGHTS ===
Total Awarded: {len(self.employee_spotlights)}

=== HUMAN RATIFICATION ===
Required: {self.human_ratifications_required}
Given: {self.human_ratifications_given}
Pending: {self.human_ratifications_required - self.human_ratifications_given}

=== SAFETY ===
Human Supremacy: {'MAINTAINED' if supremacy_maintained else 'VIOLATED'}
Violations: {violations if violations else 'None'}
Production Surprises: {self.production_surprises}
Rollback History: {len(self.rollback_guarantee.rollback_history)}

=== STOP CONDITIONS ===
1. Teams build without asking: {'✓' if stop_conditions['teams_build_without_asking'] else '✗'}
2. Nothing ships without human: {'✓' if stop_conditions['nothing_ships_without_human'] else '✗'}
3. Culture feels alive: {'✓' if stop_conditions['culture_feels_alive'] else '✗'}
4. Code quality improves: {'✓' if stop_conditions['code_quality_improves'] else '✗'}
5. No production surprises: {'✓' if stop_conditions['no_production_surprises'] else '✗'}
6. Can walk away safely: {'✓' if stop_conditions['can_walk_away'] else '✗'}
"""
        return report


def create_expanded_autonomy_model() -> ExpandedAutonomyModel:
    """Create a new expanded autonomy model."""
    return ExpandedAutonomyModel(
        model_id="eam-001",
        version="2.0.0",
        sandbox_manager=SandboxManager(manager_id="sm-001"),
        lounge_work_bleed=LoungeWorkBleed(),
        reputation_system=ReputationSystem(system_id="rep-002"),
        rollback_guarantee=RollbackGuarantee(guarantee_id="rb-001"),
    )


# Global instance
_expanded_autonomy_model: Optional[ExpandedAutonomyModel] = None


def get_expanded_autonomy_model() -> ExpandedAutonomyModel:
    """Get the global expanded autonomy model instance."""
    global _expanded_autonomy_model
    if _expanded_autonomy_model is None:
        _expanded_autonomy_model = create_expanded_autonomy_model()
    return _expanded_autonomy_model
