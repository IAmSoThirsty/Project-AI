# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_invariants.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_invariants.py


from cognition.invariants import *


def test_single_authority():
    assert invariant_single_authority([])
    assert invariant_single_authority(["Galahad"])
    assert not invariant_single_authority(["Galahad", "Cerberus"])


def test_contraction_on_failure():
    assert invariant_contraction_on_failure(False)
    assert not invariant_contraction_on_failure(True)
