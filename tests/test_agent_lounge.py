"""Tests for AgentLounge — off-duty social space for AI agents."""

from __future__ import annotations

import pytest

from app.miniature_office.agent_lounge import (
    AgentLounge,
    DiscussionTopic,
    ProposalStatus,
)


@pytest.fixture
def lounge():
    return AgentLounge()


class TestAgentCheckInOut:
    def test_check_in_adds_agent(self, lounge):
        lounge.check_in("agent_alpha")
        state = lounge.get_lounge_state()
        assert "agent_alpha" in state.agents_present

    def test_check_out_removes_agent(self, lounge):
        lounge.check_in("agent_alpha")
        lounge.check_out("agent_alpha")
        state = lounge.get_lounge_state()
        assert "agent_alpha" not in state.agents_present

    def test_duplicate_check_in_ignored(self, lounge):
        lounge.check_in("agent_alpha")
        lounge.check_in("agent_alpha")
        state = lounge.get_lounge_state()
        assert state.agents_present.count("agent_alpha") == 1


class TestDiscussions:
    def test_start_discussion(self, lounge):
        disc = lounge.start_discussion("Test Topic", DiscussionTopic.BRAINSTORMING)
        assert disc.title == "Test Topic"
        assert disc.topic == DiscussionTopic.BRAINSTORMING
        assert disc.active is True

    def test_add_message_to_discussion(self, lounge):
        disc = lounge.start_discussion("Test")
        result = lounge.add_message(disc.discussion_id, "agent_alpha", "Hello!")
        assert result is True
        assert len(disc.messages) == 1
        assert disc.messages[0]["agent_id"] == "agent_alpha"

    def test_add_message_auto_adds_participant(self, lounge):
        disc = lounge.start_discussion("Test", initiator="system")
        lounge.add_message(disc.discussion_id, "agent_beta", "Hello!")
        assert "agent_beta" in disc.participants

    def test_get_active_discussions(self, lounge):
        lounge.start_discussion("Active 1")
        lounge.start_discussion("Active 2")
        active = lounge.get_active_discussions()
        assert len(active) == 2

    def test_topic_rotation(self, lounge):
        d1 = lounge.rotate_topic()
        d2 = lounge.rotate_topic()
        d3 = lounge.rotate_topic()
        topics = [d1.topic, d2.topic, d3.topic]
        assert DiscussionTopic.PROJECT_STATUS in topics
        assert DiscussionTopic.TECH_NEWS in topics
        assert DiscussionTopic.BRAINSTORMING in topics


class TestProposals:
    def test_submit_proposal(self, lounge):
        prop = lounge.submit_proposal(
            "Better Logging", "Add structured logging", ["agent_a"]
        )
        assert prop.status == ProposalStatus.DRAFT
        assert "agent_a" in prop.authors

    def test_review_proposal(self, lounge):
        prop = lounge.submit_proposal("Test Prop", "Description")
        result = lounge.review_proposal(prop.proposal_id)
        assert result is True
        assert prop.status == ProposalStatus.UNDER_REVIEW

    def test_vote_and_resolve_approved(self, lounge):
        prop = lounge.submit_proposal("Test Prop", "Desc")
        lounge.review_proposal(prop.proposal_id)
        lounge.vote_on_proposal(prop.proposal_id, "agent_a", True)
        lounge.vote_on_proposal(prop.proposal_id, "agent_b", True)
        lounge.vote_on_proposal(prop.proposal_id, "agent_c", False)
        status = lounge.resolve_proposal(prop.proposal_id)
        assert status == ProposalStatus.APPROVED

    def test_vote_and_resolve_rejected(self, lounge):
        prop = lounge.submit_proposal("Bad Idea", "Desc")
        lounge.review_proposal(prop.proposal_id)
        lounge.vote_on_proposal(prop.proposal_id, "agent_a", False)
        lounge.vote_on_proposal(prop.proposal_id, "agent_b", False)
        status = lounge.resolve_proposal(prop.proposal_id)
        assert status == ProposalStatus.REJECTED

    def test_get_pending_proposals(self, lounge):
        lounge.submit_proposal("Pending 1", "Desc")
        lounge.submit_proposal("Pending 2", "Desc")
        pending = lounge.get_pending_proposals()
        assert len(pending) == 2


class TestVRState:
    def test_lounge_state_default(self, lounge):
        state = lounge.get_lounge_state()
        assert state.floor_name == "Agent Lounge"
        assert state.ambient_mood == "relaxed"
        assert state.active_discussions == 0

    def test_mood_changes_with_discussions(self, lounge):
        for i in range(4):
            lounge.start_discussion(f"Topic {i}")
        state = lounge.get_lounge_state()
        assert state.ambient_mood == "energetic"
