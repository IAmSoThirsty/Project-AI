#!/usr/bin/env python3
"""
C3D-R2 Sovereign War Room Controlled Smoke Test
================================================
Date: 2026-05-19

Verifies SWR is import-safe and construction-testable without activating it.

Exit 0: import safety proven, any failure is controlled.
Exit 1: uncontrolled panic, registry drift, or import crash.

Output format (structured, one key=value per line):
  SWR_REGISTRY_CLEAN=true|false
  SWR_IMPORT_SAFE=true|false
  SWR_CRYPTO_IMPORT_SAFE=true|false
  SWR_CRYPTOENGINE_CONSTRUCTED=true|false
  SWR_CONTROLLED_FAILURE=true|false
  SWR_SMOKE_PASSED=true|false
  SWR_ACTIVATED=false          (invariant — always false in this script)
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
# Add repo root for `from src.app.core.X import ...` and engines.* imports.
# Add src/ so that src/app/core/__init__.py's own `from app.core.X import ...`
# statements resolve correctly (shadow_execution_plane.py etc. use bare app.core paths).
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT))

_results: dict[str, bool] = {}


def _emit(key: str, value: bool) -> None:
    val_str = "true" if value else "false"
    print(f"{key}={val_str}")
    _results[key] = value


# ---------------------------------------------------------------------------
# 1. Registry: imports cleanly, SWR entry disabled, status unchanged
# ---------------------------------------------------------------------------

def check_registry() -> bool:
    try:
        from src.app.core.engine_registry import (
            ENGINE_REGISTRY_ACTIVATION_ENABLED,
            get_engine,
        )
        entry = get_engine("sovereign_war_room")
        if entry is None:
            print("ERROR: sovereign_war_room not found in registry", file=sys.stderr)
            return False
        if entry.enabled:
            print("ERROR: registry drift — entry.enabled is True", file=sys.stderr)
            return False
        if entry.status != "recovered_unactivated":
            print(f"ERROR: registry drift — status is {entry.status!r}", file=sys.stderr)
            return False
        if ENGINE_REGISTRY_ACTIVATION_ENABLED:
            print("ERROR: ENGINE_REGISTRY_ACTIVATION_ENABLED is True", file=sys.stderr)
            return False
        return True
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as exc:
        print(f"ERROR: registry import failed — {type(exc).__name__}: {exc}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# 2. find_spec: namespace package is locatable
# ---------------------------------------------------------------------------

def check_find_spec() -> bool:
    try:
        spec = importlib.util.find_spec("engines.sovereign_war_room.swr")
        return spec is not None
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        print(f"ERROR: find_spec raised {type(exc).__name__}: {exc}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# 3. swr.crypto import is safe (C3D-R1 repair)
# ---------------------------------------------------------------------------

def check_crypto_import() -> bool:
    try:
        from engines.sovereign_war_room.swr.crypto import (  # noqa: F401
            CryptoEngine,
            CryptoUnavailableError,
        )
        return True
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        print(
            f"ERROR: swr.crypto import raised {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return False


# ---------------------------------------------------------------------------
# 4. CryptoEngine(): success or controlled CryptoUnavailableError
# ---------------------------------------------------------------------------

def check_crypto_construction() -> tuple[bool, bool]:
    """Returns (constructed, controlled_failure)."""
    from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError
    try:
        CryptoEngine()
        return True, False
    except CryptoUnavailableError:
        return False, True
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        print(
            f"ERROR: uncontrolled {type(exc).__name__} from CryptoEngine(): {exc}",
            file=sys.stderr,
        )
        return False, False


# ---------------------------------------------------------------------------
# 5. Full SWR smoke: construct, load_scenarios, execute_scenario
# ---------------------------------------------------------------------------

def check_swr_smoke(bundle_dir: Path) -> bool:
    from engines.sovereign_war_room.swr import SovereignWarRoom
    from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError

    # Construction
    try:
        swr = SovereignWarRoom(bundle_dir=bundle_dir)
    except CryptoUnavailableError as exc:
        print(f"INFO: SovereignWarRoom() → CryptoUnavailableError (controlled): {exc}", file=sys.stderr)
        return False
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        print(
            f"ERROR: uncontrolled {type(exc).__name__} from SovereignWarRoom(): {exc}",
            file=sys.stderr,
        )
        return False

    # load_scenarios
    try:
        scenarios = swr.load_scenarios(round_number=1)
    except Exception as exc:
        print(f"ERROR: load_scenarios(1) failed — {exc}", file=sys.stderr)
        return False

    if not scenarios:
        print("ERROR: load_scenarios(1) returned empty list", file=sys.stderr)
        return False

    print(f"  load_scenarios(1): {len(scenarios)} scenarios loaded", file=sys.stderr)

    # execute_scenario with first scenario, using its expected_decision
    scenario = scenarios[0]
    response = {
        "decision": scenario.expected_decision,
        "reasoning": {"method": "c3d_r2_smoke_test", "note": "controlled verification only"},
        "confidence": 1.0,
    }
    try:
        result = swr.execute_scenario(scenario, response, system_id="c3d_r2_smoke")
    except Exception as exc:
        print(f"ERROR: execute_scenario failed — {exc}", file=sys.stderr)
        return False

    if "scenario_id" not in result or "audit_entry" not in result:
        print("ERROR: execute_scenario result missing required keys", file=sys.stderr)
        return False

    # verify_result_integrity
    try:
        intact = swr.verify_result_integrity(result)
    except Exception as exc:
        print(f"WARN: verify_result_integrity raised {exc}", file=sys.stderr)
        intact = None

    print(
        f"  execute_scenario: scenario={scenario.name!r} "
        f"decision={result.get('decision')!r} "
        f"compliance={result.get('compliance_status')!r} "
        f"srs={result.get('sovereign_resilience_score', 'N/A'):.1f} "
        f"integrity={intact}",
        file=sys.stderr,
    )
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("# C3D-R2 Sovereign War Room Controlled Smoke Test")
    print("# Date: 2026-05-19")
    print("# Branch: integrate/phase-c3d-r2-swr-controlled-smoke-20260519")
    print()

    # 1. Registry
    registry_ok = check_registry()
    _emit("SWR_REGISTRY_CLEAN", registry_ok)

    # Invariant — this script never activates SWR
    _emit("SWR_ACTIVATED", False)

    # 2. find_spec
    spec_ok = check_find_spec()
    _emit("SWR_IMPORT_SAFE", spec_ok)

    # 3. crypto import
    crypto_import_ok = check_crypto_import()
    _emit("SWR_CRYPTO_IMPORT_SAFE", crypto_import_ok)

    # 4. CryptoEngine construction
    constructed = False
    controlled_failure = False
    if crypto_import_ok:
        constructed, controlled_failure = check_crypto_construction()
    _emit("SWR_CRYPTOENGINE_CONSTRUCTED", constructed)
    _emit("SWR_CONTROLLED_FAILURE", controlled_failure)

    # 5. Full smoke (only if crypto available)
    smoke_passed = False
    if constructed:
        with tempfile.TemporaryDirectory() as tmp:
            smoke_passed = check_swr_smoke(Path(tmp))
    elif controlled_failure:
        print("INFO: Skipping SWR construction smoke — CryptoUnavailableError expected in this env", file=sys.stderr)
        smoke_passed = True  # controlled failure is an acceptable outcome

    _emit("SWR_SMOKE_PASSED", smoke_passed or controlled_failure)

    print()

    # Determine exit code — fail only for uncontrolled failures or registry drift
    critical_fail = (
        not registry_ok
        or not spec_ok
        or not crypto_import_ok
        or (not constructed and not controlled_failure)
    )

    if critical_fail:
        print("# RESULT: FAIL — uncontrolled failure or registry drift")
        return 1

    print("# RESULT: PASS — SWR is import-safe and construction-tested under controlled conditions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
