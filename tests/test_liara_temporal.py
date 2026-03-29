# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_liara_temporal.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_liara_temporal.py


import pytest

from cognition.kernel_liara import maybe_activate_liara, restore_pillar
from cognition.liara_guard import STATE, LiaraViolation, authorize_liara, revoke_liara


def test_liara_single_role_only():
    # Clean state
    STATE.active_role = None
    STATE.expires_at = None

    authorize_liara("Galahad", 1)
    with pytest.raises(LiaraViolation):
        authorize_liara("Cerberus", 1)
    revoke_liara("cleanup")


def test_liara_activation_on_failure():
    # Clean state
    STATE.active_role = None
    STATE.expires_at = None

    role = maybe_activate_liara({"Galahad": False, "Cerberus": True, "CodexDeus": True})
    assert role == "Galahad"
    restore_pillar()


def test_liara_cooldown_enforced():
    # Clean state
    STATE.active_role = None
    STATE.expires_at = None

    role = maybe_activate_liara({"Cerberus": False, "Galahad": True, "CodexDeus": True})
    assert role == "Cerberus"
    restore_pillar()

    role2 = maybe_activate_liara(
        {"Cerberus": False, "Galahad": True, "CodexDeus": True}
    )
    assert role2 is None
