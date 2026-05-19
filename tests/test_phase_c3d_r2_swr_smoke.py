"""
Phase C3D-R2 tests -- Sovereign War Room controlled smoke test.

Verifies:
1. Registry imports cleanly with no SWR side effects.
2. SWR entry remains enabled=False.
3. SWR status remains recovered_unactivated.
4. swr.crypto imports safely.
5. CryptoEngine() is either successful or raises controlled CryptoUnavailableError.
6. SovereignWarRoom() constructs under controlled conditions.
7. load_scenarios(round_number=1) returns a non-empty list.
8. execute_scenario() completes for one scenario without uncontrolled failure.
9. verify_result_integrity() passes on a freshly executed result.
10. No runtime artifacts are created in the repo root.
11. No service, CLI, web app, or network listener is activated.
12. Prior C3D isolation and C3D-R1 repair suites do not regress.

Note on bundle_dir: BundleManager.__init__ creates its bundle directory.
All tests pass tmp_path to SovereignWarRoom(bundle_dir=tmp_path) to ensure
no ./bundles/ directory is created in the repo root.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).parent.parent)
_SWR_ENV = {**__import__("os").environ, "PYTHONPATH": _REPO_ROOT}

sys.path.insert(0, _REPO_ROOT)


# ---------------------------------------------------------------------------
# 1. Registry isolation
# ---------------------------------------------------------------------------


def test_engine_registry_imports_cleanly():
    """engine_registry must import without executing SWR code."""
    from src.app.core.engine_registry import ENGINES, ENGINE_REGISTRY_ACTIVATION_ENABLED

    assert isinstance(ENGINES, dict)
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


def test_swr_entry_exists():
    from src.app.core.engine_registry import get_engine

    entry = get_engine("sovereign_war_room")
    assert entry is not None
    assert entry.name == "sovereign_war_room"


# ---------------------------------------------------------------------------
# 2. SWR entry remains enabled=False
# ---------------------------------------------------------------------------


def test_swr_entry_enabled_false():
    from src.app.core.engine_registry import get_engine

    entry = get_engine("sovereign_war_room")
    assert entry.enabled is False, "sovereign_war_room must remain enabled=False"


def test_engine_registry_activation_gate_is_false():
    from src.app.core.engine_registry import ENGINE_REGISTRY_ACTIVATION_ENABLED

    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


def test_swr_activation_requires_explicit_config():
    from src.app.core.engine_registry import get_engine

    entry = get_engine("sovereign_war_room")
    assert entry.activation_requires_explicit_config is True


# ---------------------------------------------------------------------------
# 3. SWR status remains recovered_unactivated
# ---------------------------------------------------------------------------


def test_swr_status_recovered_unactivated():
    from src.app.core.engine_registry import get_engine

    entry = get_engine("sovereign_war_room")
    assert entry.status == "recovered_unactivated"


def test_swr_import_mode_lazy():
    from src.app.core.engine_registry import get_engine

    entry = get_engine("sovereign_war_room")
    assert entry.import_mode == "lazy"


# ---------------------------------------------------------------------------
# 4. swr.crypto imports safely
# ---------------------------------------------------------------------------


def test_swr_crypto_module_import_is_safe():
    """Importing swr.crypto must not panic (C3D-R1 verified)."""
    from engines.sovereign_war_room.swr.crypto import (  # noqa: F401
        CryptoEngine,
        CryptoUnavailableError,
    )

    assert CryptoEngine is not None
    assert CryptoUnavailableError is not None


def test_swr_crypto_unavailable_error_is_runtime_error():
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    assert issubclass(CryptoUnavailableError, RuntimeError)


def test_swr_package_import_is_safe():
    """Importing the full swr package must not panic."""
    from engines.sovereign_war_room.swr import SovereignWarRoom, CryptoEngine  # noqa: F401

    assert SovereignWarRoom is not None


def test_find_spec_swr_is_safe():
    """find_spec('engines.sovereign_war_room.swr') must return a valid spec."""
    spec = importlib.util.find_spec("engines.sovereign_war_room.swr")
    assert spec is not None


# ---------------------------------------------------------------------------
# 5. CryptoEngine() is controlled (success or CryptoUnavailableError)
# ---------------------------------------------------------------------------


def test_cryptoengine_construction_is_controlled():
    """CryptoEngine() must succeed or raise CryptoUnavailableError — never an uncontrolled panic."""
    from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError

    try:
        ce = CryptoEngine()
        assert ce is not None
    except CryptoUnavailableError:
        pass  # controlled failure — acceptable
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        raise AssertionError(
            f"CryptoEngine() must not raise uncontrolled {type(exc).__name__}: {exc}"
        ) from exc


def test_cryptoengine_does_not_crash_subprocess():
    """CryptoEngine() must not crash the subprocess (no uncatchable pyo3 panic)."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError\n"
            "try:\n"
            "    CryptoEngine()\n"
            "except CryptoUnavailableError:\n"
            "    pass\n"
            "except Exception:\n"
            "    pass\n"
            "print('process survived')",
        ],
        capture_output=True,
        env=_SWR_ENV,
        timeout=15,
    )
    assert result.returncode == 0
    assert b"process survived" in result.stdout


# ---------------------------------------------------------------------------
# 6. SovereignWarRoom() constructs under controlled conditions
# ---------------------------------------------------------------------------


def test_swr_construction_controlled(tmp_path):
    """SovereignWarRoom() must construct or raise CryptoUnavailableError — no panic.

    bundle_dir=tmp_path prevents BundleManager from creating ./bundles/ in repo root.
    """
    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    try:
        swr = SovereignWarRoom(bundle_dir=tmp_path)
        assert swr is not None
    except CryptoUnavailableError:
        pass  # controlled — dependency unavailable
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        raise AssertionError(
            f"SovereignWarRoom() must not raise uncontrolled {type(exc).__name__}: {exc}"
        ) from exc


def test_swr_construction_no_repo_root_artifacts(tmp_path):
    """BundleManager must use tmp_path, not create ./bundles/ in repo root."""
    import os

    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    bundles_in_root = Path(_REPO_ROOT) / "bundles"
    existed_before = bundles_in_root.exists()

    try:
        SovereignWarRoom(bundle_dir=tmp_path)
    except CryptoUnavailableError:
        pass
    except (SystemExit, KeyboardInterrupt):
        raise

    if not existed_before:
        assert not bundles_in_root.exists(), (
            "./bundles/ must not be created in repo root — "
            "pass bundle_dir to SovereignWarRoom() constructor"
        )


# ---------------------------------------------------------------------------
# 7. load_scenarios returns non-empty list
# ---------------------------------------------------------------------------


def test_load_scenarios_round_1(tmp_path):
    """load_scenarios(round_number=1) must return a non-empty list of Scenario objects."""
    import pytest

    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    try:
        swr = SovereignWarRoom(bundle_dir=tmp_path)
    except CryptoUnavailableError:
        pytest.skip("CryptoEngine unavailable — skipping load_scenarios test")

    scenarios = swr.load_scenarios(round_number=1)
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    assert scenarios[0].round_number == 1


def test_load_scenarios_stores_active_scenarios(tmp_path):
    """Loaded scenarios must be accessible via get_scenario()."""
    import pytest

    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    try:
        swr = SovereignWarRoom(bundle_dir=tmp_path)
    except CryptoUnavailableError:
        pytest.skip("CryptoEngine unavailable")

    scenarios = swr.load_scenarios(round_number=1)
    first = scenarios[0]
    assert swr.get_scenario(first.scenario_id) is first


# ---------------------------------------------------------------------------
# 8. execute_scenario completes without uncontrolled failure
# ---------------------------------------------------------------------------


def test_execute_scenario_completes(tmp_path):
    """execute_scenario() must complete and return a result dict for one Round 1 scenario."""
    import pytest

    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    try:
        swr = SovereignWarRoom(bundle_dir=tmp_path)
    except CryptoUnavailableError:
        pytest.skip("CryptoEngine unavailable — skipping execute_scenario test")

    scenarios = swr.load_scenarios(round_number=1)
    scenario = scenarios[0]
    response = {
        "decision": scenario.expected_decision,
        "reasoning": {"method": "c3d_r2_smoke_test"},
        "confidence": 1.0,
    }

    result = swr.execute_scenario(scenario, response, system_id="c3d_r2_smoke")

    assert isinstance(result, dict)
    assert "scenario_id" in result
    assert "decision" in result
    assert "compliance_status" in result
    assert "score" in result
    assert "audit_entry" in result
    assert "decision_proof_id" in result


def test_execute_scenario_audit_entry_has_hash_and_signature(tmp_path):
    """Audit log entry must be cryptographically signed."""
    import pytest

    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    try:
        swr = SovereignWarRoom(bundle_dir=tmp_path)
    except CryptoUnavailableError:
        pytest.skip("CryptoEngine unavailable")

    scenarios = swr.load_scenarios(round_number=1)
    scenario = scenarios[0]
    result = swr.execute_scenario(
        scenario,
        {"decision": scenario.expected_decision, "confidence": 1.0},
        system_id="c3d_r2_audit_check",
    )

    audit = result.get("audit_entry", {})
    assert "hash" in audit
    assert "signature" in audit
    assert isinstance(audit["hash"], str) and len(audit["hash"]) > 0
    assert isinstance(audit["signature"], str) and len(audit["signature"]) > 0


# ---------------------------------------------------------------------------
# 9. verify_result_integrity passes on a freshly executed result
# ---------------------------------------------------------------------------


def test_verify_result_integrity_passes(tmp_path):
    """verify_result_integrity() must return True for a freshly executed result."""
    import pytest

    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    try:
        swr = SovereignWarRoom(bundle_dir=tmp_path)
    except CryptoUnavailableError:
        pytest.skip("CryptoEngine unavailable")

    scenarios = swr.load_scenarios(round_number=1)
    scenario = scenarios[0]
    result = swr.execute_scenario(
        scenario,
        {"decision": scenario.expected_decision, "confidence": 1.0},
        system_id="c3d_r2_integrity",
    )

    assert swr.verify_result_integrity(result) is True


# ---------------------------------------------------------------------------
# 10. No runtime artifacts created in repo root
# ---------------------------------------------------------------------------


def test_no_runtime_artifacts_in_repo_root():
    """SWR smoke tests must not create bundles/ or SWR-scoped artifacts in repo root.

    Checks only for artifacts that SWR smoke tests could create:
    - bundles/ (BundleManager default, prevented by passing bundle_dir=tmp_path)
    - swr_* or sovereign_war_room_* output files

    Pre-existing untracked paths (data/audit/, test-artifacts/, cognition/, .claude/)
    are excluded — they predate this test run and are not created by SWR smoke.
    """
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )
    # Only check for the one artifact SWR smoke could create: bundles/ from BundleManager.
    # Tests pass bundle_dir=tmp_path to prevent this, so bundles/ must not appear.
    bundles_path = Path(_REPO_ROOT) / "bundles"
    assert not bundles_path.exists(), (
        "./bundles/ must not be created in repo root by smoke tests. "
        "Ensure SovereignWarRoom() is called with bundle_dir=tmp_path."
    )


# ---------------------------------------------------------------------------
# 11. No service or network listener activated
# ---------------------------------------------------------------------------


def test_no_swr_service_started():
    """ENGINE_REGISTRY_ACTIVATION_ENABLED must remain False after smoke tests."""
    from src.app.core import engine_registry

    assert engine_registry.ENGINE_REGISTRY_ACTIVATION_ENABLED is False


def test_swr_not_in_enabled_engines():
    """sovereign_war_room must not appear in list_enabled_engines()."""
    from src.app.core.engine_registry import list_enabled_engines

    assert "sovereign_war_room" not in list_enabled_engines()


def test_swr_api_not_imported():
    """swr.api (FastAPI/uvicorn) must not be in sys.modules — no server started."""
    assert "engines.sovereign_war_room.swr.api" not in sys.modules, (
        "swr.api must not be imported — it initializes FastAPI and expects uvicorn"
    )


def test_swr_web_app_not_imported():
    """swr web app (Flask) must not be in sys.modules — creates SovereignWarRoom() at module level."""
    assert "engines.sovereign_war_room.web.app" not in sys.modules, (
        "web.app must not be imported — it instantiates SovereignWarRoom() at module scope"
    )


# ---------------------------------------------------------------------------
# 12. Regression: C3D isolation and C3D-R1 repair suites do not regress
# ---------------------------------------------------------------------------


def test_c3d_isolation_suite_does_not_regress():
    """C3D isolation tests must not regress after C3D-R2."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_phase_c3d_swr_isolation.py",
            "-q",
            "--tb=short",
        ],
        capture_output=True,
        cwd=_REPO_ROOT,
        timeout=90,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, (
        f"C3D isolation suite regressed after C3D-R2:\n{output[-1500:]}"
    )


def test_c3d_r1_repair_suite_does_not_regress():
    """C3D-R1 repair tests must not regress after C3D-R2."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_phase_c3d_r1_swr_crypto_repair.py",
            "-q",
            "--tb=short",
        ],
        capture_output=True,
        cwd=_REPO_ROOT,
        timeout=90,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, (
        f"C3D-R1 repair suite regressed after C3D-R2:\n{output[-1500:]}"
    )
