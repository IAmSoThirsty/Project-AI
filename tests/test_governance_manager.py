"""
Tests for GovernanceManager implementation.
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.governance.governance_manager import GovernanceManager


@pytest.fixture()
def gm(tmp_path):
    """GovernanceManager with a temp state file so tests don't clash."""
    state_file = tmp_path / "governance_state.json"
    return GovernanceManager(state_file=state_file)


class TestInitialisation:
    def test_default_state(self, gm):
        assert gm.state["version"] == "1.0.0"
        assert gm.state["governance_model"] == "multi_stakeholder"
        assert gm.state["active_proposals"] == []

    def test_save_and_load(self, tmp_path):
        state_file = tmp_path / "state.json"
        gm1 = GovernanceManager(state_file=state_file)
        gm1.set_policy_rule("test_rule", 42)
        gm1.save_state()

        gm2 = GovernanceManager(state_file=state_file)
        assert gm2.get_policy_rule("test_rule") == 42


class TestStakeholderManagement:
    def test_add_stakeholder(self, gm):
        assert gm.add_stakeholder("s1", "Alice", role="admin", weight=2.0) is True
        assert len(gm.state["stakeholders"]) == 1

    def test_add_duplicate_stakeholder(self, gm):
        gm.add_stakeholder("s1", "Alice")
        assert gm.add_stakeholder("s1", "Alice Again") is False

    def test_remove_stakeholder(self, gm):
        gm.add_stakeholder("s1", "Alice")
        assert gm.remove_stakeholder("s1") is True
        assert len(gm.state["stakeholders"]) == 0

    def test_remove_nonexistent(self, gm):
        assert gm.remove_stakeholder("nope") is False


class TestProposalCreation:
    def test_create_proposal(self, gm):
        gm.add_stakeholder("s1", "Alice")
        pid = gm.create_proposal("Test", "Desc", "s1")
        assert pid  # non-empty UUID
        assert len(gm.state["active_proposals"]) == 1

    def test_create_by_unregistered_raises(self, gm):
        with pytest.raises(ValueError, match="not a registered stakeholder"):
            gm.create_proposal("Test", "Desc", "nobody")

    def test_create_by_observer_raises(self, gm):
        gm.add_stakeholder("obs", "Observer", role="observer")
        with pytest.raises(ValueError, match="not a registered stakeholder"):
            gm.create_proposal("Test", "Desc", "obs")


class TestVoting:
    def test_valid_vote(self, gm):
        gm.add_stakeholder("s1", "Alice")
        gm.add_stakeholder("s2", "Bob")
        pid = gm.create_proposal("P1", "D", "s1")
        assert gm.vote_on_proposal(pid, "s2", "yes") is True

    def test_invalid_vote_value(self, gm):
        gm.add_stakeholder("s1", "Alice")
        pid = gm.create_proposal("P1", "D", "s1")
        assert gm.vote_on_proposal(pid, "s1", "maybe") is False

    def test_duplicate_vote_prevented(self, gm):
        gm.add_stakeholder("s1", "Alice")
        gm.add_stakeholder("s2", "Bob")
        pid = gm.create_proposal("P1", "D", "s1")
        gm.vote_on_proposal(pid, "s2", "yes")
        assert gm.vote_on_proposal(pid, "s2", "no") is False

    def test_observer_cannot_vote(self, gm):
        gm.add_stakeholder("s1", "Alice")
        gm.add_stakeholder("obs", "Observer", role="observer")
        pid = gm.create_proposal("P1", "D", "s1")
        assert gm.vote_on_proposal(pid, "obs", "yes") is False

    def test_nonexistent_proposal(self, gm):
        gm.add_stakeholder("s1", "Alice")
        assert gm.vote_on_proposal("fake-id", "s1", "yes") is False

    def test_unregistered_voter(self, gm):
        gm.add_stakeholder("s1", "Alice")
        pid = gm.create_proposal("P1", "D", "s1")
        assert gm.vote_on_proposal(pid, "ghost", "yes") is False

    def test_weighted_vote(self, gm):
        gm.add_stakeholder("s1", "Alice", weight=3.0)
        gm.add_stakeholder("s2", "Bob", weight=1.0)
        pid = gm.create_proposal("P1", "D", "s1")
        gm.vote_on_proposal(pid, "s1", "yes")
        gm.vote_on_proposal(pid, "s2", "no")

        proposal = gm.state["active_proposals"][0]
        assert proposal["votes"]["yes"] == 3.0
        assert proposal["votes"]["no"] == 1.0


class TestQuorum:
    def test_quorum_met(self, gm):
        gm.add_stakeholder("s1", "Alice")
        gm.add_stakeholder("s2", "Bob")
        pid = gm.create_proposal("P1", "D", "s1")
        gm.vote_on_proposal(pid, "s1", "yes")
        gm.vote_on_proposal(pid, "s2", "yes")
        assert gm.check_quorum(pid) is True

    def test_quorum_not_met(self, gm):
        for i in range(10):
            gm.add_stakeholder(f"s{i}", f"User{i}")
        pid = gm.create_proposal("P1", "D", "s0")
        gm.vote_on_proposal(pid, "s0", "yes")
        # Only 1/10 voted — below 51%
        assert gm.check_quorum(pid) is False


class TestExecution:
    def test_execute_passing_proposal(self, gm):
        gm.add_stakeholder("s1", "Alice")
        gm.add_stakeholder("s2", "Bob")
        pid = gm.create_proposal("P1", "D", "s1")
        gm.vote_on_proposal(pid, "s1", "yes")
        gm.vote_on_proposal(pid, "s2", "yes")
        assert gm.execute_proposal(pid) is True
        assert len(gm.state["executed_proposals"]) == 1
        assert len(gm.state["active_proposals"]) == 0

    def test_execute_failing_proposal(self, gm):
        gm.add_stakeholder("s1", "Alice")
        gm.add_stakeholder("s2", "Bob")
        pid = gm.create_proposal("P1", "D", "s1")
        gm.vote_on_proposal(pid, "s1", "no")
        gm.vote_on_proposal(pid, "s2", "no")
        assert gm.execute_proposal(pid) is False

    def test_execute_applies_policy_change(self, gm):
        gm.add_stakeholder("s1", "Alice")
        pid = gm.create_proposal(
            "Set max_tokens",
            "Max tokens to 1000",
            "s1",
            proposal_type="policy_change",
            data={"rule_name": "max_tokens", "rule_value": 1000},
        )
        gm.vote_on_proposal(pid, "s1", "yes")
        gm.execute_proposal(pid)
        assert gm.get_policy_rule("max_tokens") == 1000

    def test_execute_no_quorum(self, gm):
        for i in range(10):
            gm.add_stakeholder(f"s{i}", f"User{i}")
        pid = gm.create_proposal("P1", "D", "s0")
        gm.vote_on_proposal(pid, "s0", "yes")
        assert gm.execute_proposal(pid) is False

    def test_execute_nonexistent_proposal(self, gm):
        assert gm.execute_proposal("fake") is False


class TestPolicyRules:
    def test_set_and_get(self, gm):
        gm.set_policy_rule("foo", "bar")
        assert gm.get_policy_rule("foo") == "bar"

    def test_get_nonexistent(self, gm):
        assert gm.get_policy_rule("missing") is None
