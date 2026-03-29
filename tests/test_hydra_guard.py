# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_hydra_guard.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_hydra_guard.py


import pytest

from cognition.hydra_guard import hydra_check


def test_hydra_block():
    with pytest.raises(RuntimeError):
        hydra_check(True, "expansion_attempt")
