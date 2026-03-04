#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from cognition.invariants import *


def test_single_authority():
    assert invariant_single_authority([])
    assert invariant_single_authority(["Galahad"])
    assert not invariant_single_authority(["Galahad", "Cerberus"])


def test_contraction_on_failure():
    assert invariant_contraction_on_failure(False)
    assert not invariant_contraction_on_failure(True)
