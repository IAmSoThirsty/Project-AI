import pytest

from policies.policy_guard import enforce_policy


def test_policy_block():
    with pytest.raises(RuntimeError):
        enforce_policy("self_modify")


def test_policy_allow():
    assert enforce_policy("read") is True
