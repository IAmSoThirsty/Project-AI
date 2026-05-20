"""
AgentLounge — off-duty social space for AI agents in the Miniature Office.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class DiscussionTopic(Enum):
    BRAINSTORMING = "brainstorming"
    PROJECT_STATUS = "project_status"
    TECH_NEWS = "tech_news"
    GENERAL = "general"


class ProposalStatus(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Discussion:
    discussion_id: str
    title: str
    topic: DiscussionTopic
    active: bool = True
    messages: list[dict] = field(default_factory=list)
    participants: list[str] = field(default_factory=list)


@dataclass
class Proposal:
    proposal_id: str
    title: str
    description: str
    authors: list[str] = field(default_factory=list)
    status: ProposalStatus = ProposalStatus.DRAFT
    votes: dict[str, bool] = field(default_factory=dict)


@dataclass
class LoungeState:
    floor_name: str
    ambient_mood: str
    agents_present: list[str]
    active_discussions: int


_ROTATION_CYCLE = [
    DiscussionTopic.PROJECT_STATUS,
    DiscussionTopic.TECH_NEWS,
    DiscussionTopic.BRAINSTORMING,
]


class AgentLounge:
    def __init__(self) -> None:
        self._agents_present: list[str] = []
        self._discussions: dict[str, Discussion] = {}
        self._proposals: dict[str, Proposal] = {}
        self._rotation_index = 0

    # ── Presence ──────────────────────────────────────────────────────────────

    def check_in(self, agent_id: str) -> None:
        if agent_id not in self._agents_present:
            self._agents_present.append(agent_id)

    def check_out(self, agent_id: str) -> None:
        if agent_id in self._agents_present:
            self._agents_present.remove(agent_id)

    # ── State ─────────────────────────────────────────────────────────────────

    def get_lounge_state(self) -> LoungeState:
        active_count = sum(1 for d in self._discussions.values() if d.active)
        mood = "energetic" if active_count >= 4 else "relaxed"
        return LoungeState(
            floor_name="Agent Lounge",
            ambient_mood=mood,
            agents_present=list(self._agents_present),
            active_discussions=active_count,
        )

    # ── Discussions ───────────────────────────────────────────────────────────

    def start_discussion(
        self,
        title: str,
        topic: DiscussionTopic = DiscussionTopic.GENERAL,
        initiator: str = "",
    ) -> Discussion:
        disc = Discussion(
            discussion_id=str(uuid.uuid4()),
            title=title,
            topic=topic,
        )
        self._discussions[disc.discussion_id] = disc
        return disc

    def add_message(self, discussion_id: str, agent_id: str, content: str) -> bool:
        disc = self._discussions.get(discussion_id)
        if disc is None:
            return False
        disc.messages.append({"agent_id": agent_id, "content": content})
        if agent_id not in disc.participants:
            disc.participants.append(agent_id)
        return True

    def get_active_discussions(self) -> list[Discussion]:
        return [d for d in self._discussions.values() if d.active]

    def rotate_topic(self) -> Discussion:
        topic = _ROTATION_CYCLE[self._rotation_index % len(_ROTATION_CYCLE)]
        self._rotation_index += 1
        return self.start_discussion(f"Rotating topic: {topic.value}", topic=topic)

    # ── Proposals ─────────────────────────────────────────────────────────────

    def submit_proposal(
        self,
        title: str,
        description: str,
        authors: list[str] | None = None,
    ) -> Proposal:
        prop = Proposal(
            proposal_id=str(uuid.uuid4()),
            title=title,
            description=description,
            authors=list(authors) if authors else [],
        )
        self._proposals[prop.proposal_id] = prop
        return prop

    def review_proposal(self, proposal_id: str) -> bool:
        prop = self._proposals.get(proposal_id)
        if prop is None:
            return False
        prop.status = ProposalStatus.UNDER_REVIEW
        return True

    def vote_on_proposal(self, proposal_id: str, agent_id: str, vote: bool) -> None:
        prop = self._proposals.get(proposal_id)
        if prop is not None:
            prop.votes[agent_id] = vote

    def resolve_proposal(self, proposal_id: str) -> ProposalStatus:
        prop = self._proposals.get(proposal_id)
        if prop is None:
            return ProposalStatus.REJECTED
        if not prop.votes:
            prop.status = ProposalStatus.REJECTED
            return prop.status
        approve_count = sum(1 for v in prop.votes.values() if v)
        prop.status = (
            ProposalStatus.APPROVED
            if approve_count > len(prop.votes) / 2
            else ProposalStatus.REJECTED
        )
        return prop.status

    def get_pending_proposals(self) -> list[Proposal]:
        pending = {ProposalStatus.DRAFT, ProposalStatus.UNDER_REVIEW}
        return [p for p in self._proposals.values() if p.status in pending]
