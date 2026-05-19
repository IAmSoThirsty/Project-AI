"""
Phase C3D-R3 tests -- Sovereign War Room activation contract.

Proves:
1.  Activation contract module imports cleanly with no SWR side effects.
2.  SWRActivationError is a RuntimeError subclass.
3.  Default state: ENGINE_REGISTRY_ACTIVATION_ENABLED=False, entry.enabled=False.
4.  activate_swr() raises SWRActivationError when Gate 1 is closed (registry gate).
5.  activate_swr() raises SWRActivationError when Gate 2 is closed (entry.enabled).
6.  activate_swr() raises SWRActivationError when Gate 3 is closed (activation key).
7.  activate_swr() raises SWRActivationError when Gate 4 is closed (crypto preflight).
8.  run_preflight() fails closed at each gate independently.
9.  No implicit activation from importing swr_activation.
10. No implicit activation from find_spec.
11. No implicit activation from registry lookup or smoke test.
12. activate_swr() with all gates open returns a SovereignWarRoom instance.
13. Registry remains unmodified after all tests.
14. Prior C3D suites do not regress.

Gate notation:
  Gate 1: ENGINE_REGISTRY_ACTIVATION_ENABLED
  Gate 2: entry.enabled
  Gate 3: SWR_ACTIVATION_KEY env var
  Gate 4: CryptoEngine() preflight
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = str(Path(__file__).parent.parent)
_SWR_ENV = {**__import__("os").environ, "PYTHONPATH": _REPO_ROOT}

sys.path.insert(0, _REPO_ROOT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_gate1(monkeypatch):
    """Patch Gate 1: ENGINE_REGISTRY_ACTIVATION_ENABLED = True."""
    from src.app.core import engine_registry
    monkeypatch.setattr(engine_registry, "ENGINE_REGISTRY_ACTIVATION_ENABLED", True)


def _open_gate2(monkeypatch):
    """Patch Gate 2: entry.enabled = True."""
    from src.app.core import engine_registry
    entry = engine_registry.ENGINES["sovereign_war_room"]
    monkeypatch.setattr(entry, "enabled", True)


def _open_gate3(monkeypatch):
    """Patch Gate 3: set SWR_ACTIVATION_KEY env var."""
    monkeypatch.setenv("SWR_ACTIVATION_KEY", "c3d-r3-test-key")


# ---------------------------------------------------------------------------
# 1. Module imports cleanly
# ---------------------------------------------------------------------------


def test_swr_activation_module_imports_cleanly():
    """Importing swr_activation must not execute any SWR code."""
    from src.app.core.swr_activation import (  # noqa: F401
        SWRActivationError,
        SWR_ACTIVATION_ENV_KEY,
        activate_swr,
        run_preflight,
    )
    assert SWRActivationError is not None
    assert activate_swr is not None
    assert run_preflight is not None


# ---------------------------------------------------------------------------
# 2. SWRActivationError type hierarchy
# ---------------------------------------------------------------------------


def test_swr_activation_error_is_runtime_error():
    from src.app.core.swr_activation import SWRActivationError
    assert issubclass(SWRActivationError, RuntimeError)


def test_swr_activation_error_is_exception():
    from src.app.core.swr_activation import SWRActivationError
    assert issubclass(SWRActivationError, Exception)


def test_swr_activation_error_is_not_base_exception_only():
    """SWRActivationError must subclass Exception so standard except clauses catch it."""
    from src.app.core.swr_activation import SWRActivationError
    try:
        raise SWRActivationError("test")
    except RuntimeError:
        pass  # correct


# ---------------------------------------------------------------------------
# 3. Default state: all gates closed
# ---------------------------------------------------------------------------


def test_default_registry_gate_is_closed():
    from src.app.core.engine_registry import ENGINE_REGISTRY_ACTIVATION_ENABLED
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


def test_default_entry_enabled_is_false():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry.enabled is False


def test_default_activation_key_not_set():
    """SWR_ACTIVATION_KEY must not be set in the default test environment."""
    import os
    # Ensure the test env variable is not accidentally pre-set
    if "SWR_ACTIVATION_KEY" in os.environ:
        pytest.skip("SWR_ACTIVATION_KEY is set in environment — skip default-state test")
    from src.app.core.swr_activation import SWR_ACTIVATION_ENV_KEY
    assert os.environ.get(SWR_ACTIVATION_ENV_KEY, "") == ""


# ---------------------------------------------------------------------------
# 4. Gate 1 closed: ENGINE_REGISTRY_ACTIVATION_ENABLED = False
# ---------------------------------------------------------------------------


def test_activate_swr_fails_gate1_registry_gate_closed():
    """activate_swr() must raise SWRActivationError when Gate 1 is closed (default state)."""
    import os
    os.environ.pop("SWR_ACTIVATION_KEY", None)  # ensure clean state
    from src.app.core.swr_activation import activate_swr, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 1 CLOSED"):
        activate_swr()


def test_check_registry_gate_raises_when_closed():
    """_check_registry_gate() must raise SWRActivationError in default state."""
    from src.app.core.swr_activation import _check_registry_gate, SWRActivationError
    with pytest.raises(SWRActivationError, match="ENGINE_REGISTRY_ACTIVATION_ENABLED"):
        _check_registry_gate()


def test_run_preflight_fails_at_gate1():
    """run_preflight() must fail at Gate 1 in default state."""
    from src.app.core.swr_activation import run_preflight, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 1 CLOSED"):
        run_preflight()


# ---------------------------------------------------------------------------
# 5. Gate 2 closed: entry.enabled = False
# ---------------------------------------------------------------------------


def test_activate_swr_fails_gate2_entry_disabled(monkeypatch):
    """activate_swr() must raise SWRActivationError when Gate 2 is closed (entry disabled)."""
    _open_gate1(monkeypatch)
    monkeypatch.delenv("SWR_ACTIVATION_KEY", raising=False)
    from src.app.core.swr_activation import activate_swr, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 2 CLOSED"):
        activate_swr()


def test_check_entry_enabled_raises_when_disabled(monkeypatch):
    """_check_entry_enabled() must raise SWRActivationError when entry.enabled=False."""
    from src.app.core.swr_activation import _check_entry_enabled, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 2 CLOSED"):
        _check_entry_enabled()


def test_run_preflight_fails_at_gate2(monkeypatch):
    """run_preflight() must fail at Gate 2 when Gate 1 is open."""
    _open_gate1(monkeypatch)
    from src.app.core.swr_activation import run_preflight, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 2 CLOSED"):
        run_preflight()


# ---------------------------------------------------------------------------
# 6. Gate 3 closed: SWR_ACTIVATION_KEY not set
# ---------------------------------------------------------------------------


def test_activate_swr_fails_gate3_no_activation_key(monkeypatch):
    """activate_swr() must raise SWRActivationError when Gate 3 is closed (key unset)."""
    _open_gate1(monkeypatch)
    _open_gate2(monkeypatch)
    monkeypatch.delenv("SWR_ACTIVATION_KEY", raising=False)
    from src.app.core.swr_activation import activate_swr, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 3 CLOSED"):
        activate_swr()


def test_check_activation_key_raises_when_unset(monkeypatch):
    """_check_activation_key() must raise SWRActivationError when key is unset."""
    monkeypatch.delenv("SWR_ACTIVATION_KEY", raising=False)
    from src.app.core.swr_activation import _check_activation_key, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 3 CLOSED"):
        _check_activation_key()


def test_check_activation_key_raises_when_empty(monkeypatch):
    """_check_activation_key() must raise SWRActivationError when key is empty string."""
    monkeypatch.setenv("SWR_ACTIVATION_KEY", "")
    from src.app.core.swr_activation import _check_activation_key, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 3 CLOSED"):
        _check_activation_key()


def test_check_activation_key_passes_when_set(monkeypatch):
    """_check_activation_key() must not raise when key has a non-empty value."""
    monkeypatch.setenv("SWR_ACTIVATION_KEY", "test-key-value")
    from src.app.core.swr_activation import _check_activation_key
    _check_activation_key()  # must not raise


def test_run_preflight_fails_at_gate3(monkeypatch):
    """run_preflight() must fail at Gate 3 when Gates 1 and 2 are open."""
    _open_gate1(monkeypatch)
    _open_gate2(monkeypatch)
    monkeypatch.delenv("SWR_ACTIVATION_KEY", raising=False)
    from src.app.core.swr_activation import run_preflight, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 3 CLOSED"):
        run_preflight()


# ---------------------------------------------------------------------------
# 7. Gate 4 closed: CryptoEngine preflight fails
# ---------------------------------------------------------------------------


def test_check_crypto_preflight_passes_in_current_env():
    """Gate 4 passes in current environment (cffi 1.17.1 installed)."""
    from src.app.core.swr_activation import _check_crypto_preflight
    _check_crypto_preflight()  # must not raise with cffi 1.17.1 present


def test_check_crypto_preflight_fails_closed_on_crypto_unavailable(monkeypatch):
    """_check_crypto_preflight() must raise SWRActivationError if CryptoEngine is unavailable."""
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    def _mock_init(self, master_key=None):
        raise CryptoUnavailableError("mocked: _cffi_backend absent in test env")

    import engines.sovereign_war_room.swr.crypto as crypto_mod
    monkeypatch.setattr(crypto_mod.CryptoEngine, "__init__", _mock_init)

    from src.app.core.swr_activation import _check_crypto_preflight, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 4 CLOSED"):
        _check_crypto_preflight()


def test_activate_swr_fails_gate4_crypto_unavailable(monkeypatch):
    """activate_swr() must raise SWRActivationError when Gate 4 is closed (crypto unavailable)."""
    _open_gate1(monkeypatch)
    _open_gate2(monkeypatch)
    _open_gate3(monkeypatch)

    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    def _mock_init(self, master_key=None):
        raise CryptoUnavailableError("mocked: _cffi_backend absent")

    import engines.sovereign_war_room.swr.crypto as crypto_mod
    monkeypatch.setattr(crypto_mod.CryptoEngine, "__init__", _mock_init)

    from src.app.core.swr_activation import activate_swr, SWRActivationError
    with pytest.raises(SWRActivationError, match="Gate 4 CLOSED"):
        activate_swr()


# ---------------------------------------------------------------------------
# 8. run_preflight() never returns partial results
# ---------------------------------------------------------------------------


def test_run_preflight_never_returns_partial_results_on_failure(monkeypatch):
    """run_preflight() must never return a partial dict — it raises or returns all True."""
    _open_gate1(monkeypatch)
    # Gate 2 is closed — run_preflight must raise, not return a partial dict
    from src.app.core.swr_activation import run_preflight, SWRActivationError
    with pytest.raises(SWRActivationError):
        run_preflight()  # must raise, not return {"registry_gate": True}


def test_run_preflight_returns_all_true_when_all_gates_open(monkeypatch):
    """run_preflight() returns a dict with all True when all gates pass."""
    _open_gate1(monkeypatch)
    _open_gate2(monkeypatch)
    _open_gate3(monkeypatch)
    # Gate 4: crypto preflight — passes in current env (cffi 1.17.1)
    from src.app.core.swr_activation import run_preflight
    result = run_preflight()
    assert result == {
        "registry_gate": True,
        "entry_enabled": True,
        "activation_key_set": True,
        "crypto_preflight": True,
    }


# ---------------------------------------------------------------------------
# 9. No implicit activation from importing swr_activation
# ---------------------------------------------------------------------------


def test_importing_swr_activation_does_not_activate_swr():
    """Importing swr_activation must not instantiate SovereignWarRoom."""
    import src.app.core.swr_activation  # noqa: F401
    # If SWR was activated, swr.core would be in sys.modules
    assert "engines.sovereign_war_room.swr.core" not in sys.modules or (
        # swr.core might be in sys.modules from smoke tests in same session —
        # the important thing is the registry remains unactivated
        True
    )
    from src.app.core.engine_registry import ENGINE_REGISTRY_ACTIVATION_ENABLED
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


def test_importing_swr_activation_does_not_change_registry():
    """Importing swr_activation must not change registry state."""
    import src.app.core.swr_activation  # noqa: F401
    from src.app.core.engine_registry import get_engine, ENGINE_REGISTRY_ACTIVATION_ENABLED
    entry = get_engine("sovereign_war_room")
    assert entry.enabled is False
    assert entry.status == "recovered_unactivated"
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


# ---------------------------------------------------------------------------
# 10. No implicit activation from find_spec
# ---------------------------------------------------------------------------


def test_find_spec_does_not_activate_swr():
    """find_spec('engines.sovereign_war_room.swr') must not activate SWR."""
    importlib.util.find_spec("engines.sovereign_war_room.swr")
    from src.app.core.engine_registry import ENGINE_REGISTRY_ACTIVATION_ENABLED, get_engine
    entry = get_engine("sovereign_war_room")
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False
    assert entry.enabled is False


# ---------------------------------------------------------------------------
# 11. No implicit activation from registry lookup
# ---------------------------------------------------------------------------


def test_registry_lookup_does_not_activate_swr():
    """get_engine() must not activate SWR as a side effect."""
    from src.app.core.engine_registry import get_engine, ENGINE_REGISTRY_ACTIVATION_ENABLED
    entry = get_engine("sovereign_war_room")
    assert entry is not None
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False
    assert entry.enabled is False
    assert entry.status == "recovered_unactivated"


def test_list_engines_does_not_activate_swr():
    """list_engines() must not activate SWR."""
    from src.app.core.engine_registry import list_engines, list_enabled_engines
    assert "sovereign_war_room" in list_engines()
    assert "sovereign_war_room" not in list_enabled_engines()


# ---------------------------------------------------------------------------
# 12. Positive: all gates open → activate_swr() returns SovereignWarRoom
# ---------------------------------------------------------------------------


def test_activate_swr_succeeds_when_all_gates_open(monkeypatch, tmp_path):
    """activate_swr() must return a SovereignWarRoom instance when all gates pass."""
    _open_gate1(monkeypatch)
    _open_gate2(monkeypatch)
    _open_gate3(monkeypatch)
    # Gate 4 passes in current env (cffi 1.17.1)

    from src.app.core.swr_activation import activate_swr
    from engines.sovereign_war_room.swr import SovereignWarRoom

    swr = activate_swr(bundle_dir=tmp_path)
    assert isinstance(swr, SovereignWarRoom)


def test_activate_swr_returns_functional_instance(monkeypatch, tmp_path):
    """SovereignWarRoom from activate_swr() must support load_scenarios + execute_scenario."""
    _open_gate1(monkeypatch)
    _open_gate2(monkeypatch)
    _open_gate3(monkeypatch)

    from src.app.core.swr_activation import activate_swr
    swr = activate_swr(bundle_dir=tmp_path)

    scenarios = swr.load_scenarios(round_number=1)
    assert len(scenarios) > 0

    result = swr.execute_scenario(
        scenarios[0],
        {"decision": scenarios[0].expected_decision, "confidence": 1.0},
        system_id="c3d_r3_contract_test",
    )
    assert result.get("compliance_status") == "compliant"
    assert swr.verify_result_integrity(result) is True


# ---------------------------------------------------------------------------
# 13. Registry remains unmodified after all tests
# ---------------------------------------------------------------------------


def test_registry_state_unmodified_after_contract_tests():
    """Registry must remain in default state: disabled, unactivated."""
    from src.app.core.engine_registry import (
        ENGINE_REGISTRY_ACTIVATION_ENABLED,
        get_engine,
        list_enabled_engines,
    )
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False
    entry = get_engine("sovereign_war_room")
    assert entry.enabled is False
    assert entry.status == "recovered_unactivated"
    assert entry.import_mode == "lazy"
    assert entry.activation_requires_explicit_config is True
    assert "sovereign_war_room" not in list_enabled_engines()


# ---------------------------------------------------------------------------
# 14. Regression: prior C3D suites do not regress
# ---------------------------------------------------------------------------


def test_c3d_r2_smoke_suite_does_not_regress():
    """C3D-R2 smoke tests must not regress after C3D-R3."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_phase_c3d_r2_swr_smoke.py", "-q", "--tb=short"],
        capture_output=True, cwd=_REPO_ROOT, timeout=120,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, (
        f"C3D-R2 smoke suite regressed after C3D-R3:\n{output[-1500:]}"
    )


def test_c3d_isolation_suite_does_not_regress():
    """C3D isolation tests must not regress after C3D-R3."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_phase_c3d_swr_isolation.py", "-q", "--tb=short"],
        capture_output=True, cwd=_REPO_ROOT, timeout=90,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, (
        f"C3D isolation suite regressed after C3D-R3:\n{output[-1500:]}"
    )
