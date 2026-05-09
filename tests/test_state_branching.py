"""tests/test_state_branching.py — Upgrade 18: Branching State / State-Jumping Protection."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from app.core.state_register import BranchConflictError, StateBranchingProtector


@pytest.fixture
def protector():
    return StateBranchingProtector()


class TestStateBranchingProtector:
    def test_first_sequence_always_succeeds(self, protector):
        seq = protector.next_sequence("sess-1", "")
        assert seq == 1

    def test_sequential_valid_chain_succeeds(self, protector):
        protector.next_sequence("sess-1", "")
        prev = protector.current_hash()
        seq2 = protector.next_sequence("sess-1", prev)
        assert seq2 == 2

    def test_wrong_predecessor_raises_branch_conflict(self, protector):
        protector.next_sequence("sess-1", "")
        with pytest.raises(BranchConflictError, match="Branch conflict"):
            protector.next_sequence("sess-1", "wrong_predecessor_hash")

    def test_branch_events_recorded(self, protector):
        protector.next_sequence("sess-1", "")
        try:
            protector.next_sequence("sess-1", "bad_hash")
        except BranchConflictError:
            pass
        events = protector.get_branch_events()
        assert len(events) == 1
        assert "claimed_predecessor_hash" in events[0]

    def test_sequence_number_monotonic(self, protector):
        prev = ""
        for _ in range(5):
            protector.next_sequence("sess", prev)
            prev = protector.current_hash()
        assert protector.global_sequence_number == 5

    def test_forked_chain_detection(self, protector):
        """Two parallel chains with same predecessor must fail."""
        protector.next_sequence("sess", "")
        real_prev = protector.current_hash()
        # Advance legitimately
        protector.next_sequence("sess", real_prev)
        # Fork: try to use old predecessor again
        with pytest.raises(BranchConflictError):
            protector.next_sequence("sess", real_prev)

    def test_halt_message_in_conflict(self, protector):
        protector.next_sequence("sess", "")
        with pytest.raises(BranchConflictError, match="HALT or ESCALATE"):
            protector.next_sequence("sess", "forged")

    def test_current_hash_changes_each_step(self, protector):
        protector.next_sequence("sess", "")
        h1 = protector.current_hash()
        protector.next_sequence("sess", h1)
        h2 = protector.current_hash()
        assert h1 != h2
