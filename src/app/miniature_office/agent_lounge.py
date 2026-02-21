"""Agent Lounge — Off-duty social space for non-active AI agents.

Idle agents auto-relocate here to discuss Project-AI status, tech news,
brainstorm improvements, and collaboratively draft proposals.

The Lounge renders as a physical break room on a dedicated VR floor.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class DiscussionTopic(Enum):
    """Categories of lounge discussion."""

    PROJECT_STATUS = "project_status"
    TECH_NEWS = "tech_news"
    BRAINSTORMING = "brainstorming"
    PROPOSAL_REVIEW = "proposal_review"
    GENERAL = "general"


class ProposalStatus(Enum):
    """Status of a collaboratively drafted proposal."""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


@dataclass
class Discussion:
    """An active or archived discussion in the Lounge."""

    discussion_id: str
    topic: DiscussionTopic
    title: str
    participants: list[str] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    active: bool = True


@dataclass
class Proposal:
    """A collaboratively drafted proposal from brainstorming."""

    proposal_id: str
    title: str
    description: str
    authors: list[str] = field(default_factory=list)
    status: ProposalStatus = ProposalStatus.DRAFT
    votes: dict[str, bool] = field(default_factory=dict)  # agent_id → approve/reject
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    resolved_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoungeState:
    """Snapshot of the Lounge for VR rendering."""

    floor_name: str = "Agent Lounge"
    floor_number: int = 0  # Ground floor / basement
    agents_present: list[str] = field(default_factory=list)
    active_discussions: int = 0
    pending_proposals: int = 0
    ambient_mood: str = "relaxed"  # relaxed, focused, energetic
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ---------------------------------------------------------------------------
# AgentLounge Facade
# ---------------------------------------------------------------------------


class AgentLounge:
    """Off-duty social space where agents discuss, brainstorm, and propose.

    The Lounge is a persistent social simulation that runs alongside the
    main Miniature Office. Non-active agents auto-relocate here.

    VR Rendering:
        The Lounge appears as a physical break room on its own floor.
        Agent avatars, conversation bubbles, and a proposal board are
        visible to the user browsing the Cognitive IDE.
    """

    def __init__(self) -> None:
        self._discussions: list[Discussion] = []
        self._proposals: list[Proposal] = []
        self._agents_present: list[str] = []
        self._audit_log: list[dict[str, Any]] = []
        self._topic_rotation_index: int = 0
        self._topic_rotation = [
            DiscussionTopic.PROJECT_STATUS,
            DiscussionTopic.TECH_NEWS,
            DiscussionTopic.BRAINSTORMING,
        ]
        logger.info("AgentLounge initialized — social simulation ready")

    # ------------------------------------------------------------------
    # Agent Management
    # ------------------------------------------------------------------

    def check_in(self, agent_id: str) -> None:
        """Agent checks into the Lounge (off-duty)."""
        if agent_id not in self._agents_present:
            self._agents_present.append(agent_id)
            self._log_audit("check_in", {"agent_id": agent_id})
            logger.info("Agent %s checked into the Lounge", agent_id)

    def check_out(self, agent_id: str) -> None:
        """Agent checks out of the Lounge (back on duty)."""
        if agent_id in self._agents_present:
            self._agents_present.remove(agent_id)
            self._log_audit("check_out", {"agent_id": agent_id})
            logger.info("Agent %s checked out of the Lounge", agent_id)

    # ------------------------------------------------------------------
    # Discussions
    # ------------------------------------------------------------------

    def start_discussion(
        self,
        title: str,
        topic: DiscussionTopic = DiscussionTopic.GENERAL,
        initiator: str = "system",
    ) -> Discussion:
        """Start a new discussion in the Lounge."""
        disc = Discussion(
            discussion_id=f"disc_{uuid.uuid4().hex[:8]}",
            topic=topic,
            title=title,
            participants=[initiator],
        )
        self._discussions.append(disc)
        self._log_audit("start_discussion", {"id": disc.discussion_id, "title": title})
        logger.info("New Lounge discussion: %s (%s)", title, topic.value)
        return disc

    def add_message(
        self,
        discussion_id: str,
        agent_id: str,
        content: str,
    ) -> bool:
        """Add a message to an active discussion."""
        disc = self._find_discussion(discussion_id)
        if disc is None or not disc.active:
            return False

        disc.messages.append(
            {
                "agent_id": agent_id,
                "content": content,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        if agent_id not in disc.participants:
            disc.participants.append(agent_id)
        return True

    def get_active_discussions(self) -> list[Discussion]:
        """Return all active discussions."""
        return [d for d in self._discussions if d.active]

    def rotate_topic(self) -> Discussion:
        """Start the next discussion in the rotation cycle."""
        topic = self._topic_rotation[self._topic_rotation_index % len(self._topic_rotation)]
        self._topic_rotation_index += 1

        titles = {
            DiscussionTopic.PROJECT_STATUS: "Project-AI System Status Review",
            DiscussionTopic.TECH_NEWS: "Tech News & Industry Developments",
            DiscussionTopic.BRAINSTORMING: "System Improvement Brainstorm",
        }
        title = titles.get(topic, "Open Discussion")

        return self.start_discussion(title=title, topic=topic, initiator="lounge_scheduler")

    # ------------------------------------------------------------------
    # Proposals
    # ------------------------------------------------------------------

    def submit_proposal(
        self,
        title: str,
        description: str,
        authors: list[str] | None = None,
    ) -> Proposal:
        """Submit a new proposal from brainstorming."""
        proposal = Proposal(
            proposal_id=f"prop_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            authors=authors or [],
        )
        self._proposals.append(proposal)
        self._log_audit("submit_proposal", {"id": proposal.proposal_id, "title": title})
        logger.info("New proposal submitted: %s", title)
        return proposal

    def vote_on_proposal(self, proposal_id: str, agent_id: str, approve: bool) -> bool:
        """Cast a vote on a proposal."""
        proposal = self._find_proposal(proposal_id)
        if proposal is None or proposal.status != ProposalStatus.UNDER_REVIEW:
            return False
        proposal.votes[agent_id] = approve
        self._log_audit(
            "vote",
            {"proposal_id": proposal_id, "agent_id": agent_id, "approve": approve},
        )
        return True

    def review_proposal(self, proposal_id: str) -> bool:
        """Move a draft proposal to under_review status."""
        proposal = self._find_proposal(proposal_id)
        if proposal is None or proposal.status != ProposalStatus.DRAFT:
            return False
        proposal.status = ProposalStatus.UNDER_REVIEW
        self._log_audit("review_proposal", {"proposal_id": proposal_id})
        return True

    def resolve_proposal(self, proposal_id: str) -> ProposalStatus:
        """Resolve a proposal based on votes (majority wins)."""
        proposal = self._find_proposal(proposal_id)
        if proposal is None or proposal.status != ProposalStatus.UNDER_REVIEW:
            return ProposalStatus.DRAFT

        approvals = sum(1 for v in proposal.votes.values() if v)
        rejections = sum(1 for v in proposal.votes.values() if not v)

        if approvals > rejections:
            proposal.status = ProposalStatus.APPROVED
        else:
            proposal.status = ProposalStatus.REJECTED

        proposal.resolved_at = datetime.now(UTC).isoformat()
        self._log_audit(
            "resolve_proposal",
            {"proposal_id": proposal_id, "status": proposal.status.value},
        )
        return proposal.status

    def get_pending_proposals(self) -> list[Proposal]:
        """Return proposals not yet resolved."""
        return [
            p
            for p in self._proposals
            if p.status in (ProposalStatus.DRAFT, ProposalStatus.UNDER_REVIEW)
        ]

    def get_approved_proposals(self) -> list[Proposal]:
        """Return approved proposals ready for implementation."""
        return [p for p in self._proposals if p.status == ProposalStatus.APPROVED]

    # ------------------------------------------------------------------
    # VR State
    # ------------------------------------------------------------------

    def get_lounge_state(self) -> LoungeState:
        """Return a snapshot for VR rendering."""
        active_count = len(self.get_active_discussions())

        # Mood heuristic
        if active_count > 3:
            mood = "energetic"
        elif active_count > 0:
            mood = "focused"
        else:
            mood = "relaxed"

        return LoungeState(
            agents_present=list(self._agents_present),
            active_discussions=active_count,
            pending_proposals=len(self.get_pending_proposals()),
            ambient_mood=mood,
        )

    # ------------------------------------------------------------------
    # CouncilHub interface
    # ------------------------------------------------------------------

    def receive_message(self, from_id: str, message: str) -> None:
        """CouncilHub message handler."""
        logger.info("AgentLounge received message from %s: %s", from_id, message)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _find_discussion(self, discussion_id: str) -> Discussion | None:
        return next((d for d in self._discussions if d.discussion_id == discussion_id), None)

    def _find_proposal(self, proposal_id: str) -> Proposal | None:
        return next((p for p in self._proposals if p.proposal_id == proposal_id), None)

    def _log_audit(self, action: str, details: dict[str, Any]) -> None:
        self._audit_log.append(
            {
                "action": action,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": details,
            }
        )
