# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_boundary.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_boundary.py


import pytest

from cognition.boundary import enforce_boundary


def test_boundary_blocks_missing_tarl():
    with pytest.raises(RuntimeError):
        enforce_boundary(None)


def test_boundary_accepts_tarl():
    assert enforce_boundary("deadbeef") is True
