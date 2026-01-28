import pytest
from cognition.liara_guard import authorize_liara, revoke_liara, LiaraViolation, STATE
from cognition.kernel_liara import maybe_activate_liara, restore_pillar

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
    
    role = maybe_activate_liara({
        "Galahad": False,
        "Cerberus": True,
        "CodexDeus": True
    })
    assert role == "Galahad"
    restore_pillar()

def test_liara_cooldown_enforced():
    # Clean state
    STATE.active_role = None
    STATE.expires_at = None
    
    role = maybe_activate_liara({
        "Cerberus": False,
        "Galahad": True,
        "CodexDeus": True
    })
    assert role == "Cerberus"
    restore_pillar()

    role2 = maybe_activate_liara({
        "Cerberus": False,
        "Galahad": True,
        "CodexDeus": True
    })
    assert role2 is None
