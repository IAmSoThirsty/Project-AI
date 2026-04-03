#                                           [2026-03-03 13:45]
#                                          Productivity: Active
import pytest

from cognition.hydra_guard import hydra_check


def test_hydra_block():
    with pytest.raises(RuntimeError):
        hydra_check(True, "expansion_attempt")
