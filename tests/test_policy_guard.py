"""
Tests for policy_guard module — validates policy enforcement logic.

Tests the enforce_policy function directly by adding the necessary
paths at test time so policies.policy_guard and its cognition.audit
dependency are both importable.
"""

import sys
from pathlib import Path

# Ensure project root is on path so both 'policies' and 'cognition' packages resolve
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

import pytest  # noqa: E402

from policies.policy_guard import enforce_policy  # noqa: E402


class TestPolicyGuard:
    """Test policy enforcement rules."""

    def test_blocked_actions_raise(self):
        """Actions not in the allowlist must raise RuntimeError."""
        with pytest.raises(RuntimeError, match="Policy violation"):
            enforce_policy("self_modify")

    def test_allowed_read(self):
        """The 'read' action is in the allowlist and should return True."""
        assert enforce_policy("read") is True

    def test_allowed_compute(self):
        """The 'compute' action is in the allowlist and should return True."""
        assert enforce_policy("compute") is True

    def test_allowed_analyze(self):
        """The 'analyze' action is in the allowlist and should return True."""
        assert enforce_policy("analyze") is True

    def test_blocked_delete(self):
        """The 'delete' action is NOT in the allowlist."""
        with pytest.raises(RuntimeError):
            enforce_policy("delete")

    def test_blocked_write(self):
        """The 'write' action is NOT in the allowlist."""
        with pytest.raises(RuntimeError):
            enforce_policy("write")

    def test_blocked_empty_string(self):
        """Empty string action is NOT in the allowlist."""
        with pytest.raises(RuntimeError):
            enforce_policy("")
