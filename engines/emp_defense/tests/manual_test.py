#!/usr/bin/env python3
"""
Manual test runner for EMP Defense Engine (no pytest required).
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from engines.emp_defense import (
    EMPDefenseEngine,
    EMPScenario,
    load_scenario_preset,
)


def test_basic_functionality():
    """Test basic engine functionality."""
    print("=" * 60)
    print("EMP Defense Engine - Manual Test Suite")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Engine creation
    print("\n[TEST 1] Engine creation...")
    try:
        engine = EMPDefenseEngine()
        assert engine is not None
        assert not engine.initialized
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 2: Engine initialization
    print("\n[TEST 2] Engine initialization...")
    try:
        engine = EMPDefenseEngine()
        result = engine.init()
        assert result is True
        assert engine.initialized
        assert engine.state is not None
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 3: Simulation tick
    print("\n[TEST 3] Simulation tick...")
    try:
        engine = EMPDefenseEngine()
        engine.init()
        result = engine.tick()
        assert result is True
        assert engine.state.simulation_day == 7
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 4: Event injection
    print("\n[TEST 4] Event injection...")
    try:
        engine = EMPDefenseEngine()
        engine.init()
        event_id = engine.inject_event("recovery_effort", {"region": "NA"})
        assert event_id.startswith("evt_")
        assert len(engine.events) >= 1
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 5: State observation
    print("\n[TEST 5] State observation...")
    try:
        engine = EMPDefenseEngine()
        engine.init()
        state = engine.observe()
        assert isinstance(state, dict)
        assert "simulation_day" in state
        assert "global_population" in state
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 6: Artifact export
    print("\n[TEST 6] Artifact export...")
    try:
        engine = EMPDefenseEngine()
        engine.init()
        engine.tick()
        result = engine.export_artifacts()
        assert result is True
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 7: Scenario presets
    print("\n[TEST 7] Scenario presets...")
    try:
        config = load_scenario_preset(EMPScenario.STANDARD)
        assert config.scenario == "standard"
        assert config.grid_failure_pct == 0.90
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Test 8: Full simulation
    print("\n[TEST 8] Full simulation run (52 weeks)...")
    try:
        config = load_scenario_preset(EMPScenario.STANDARD)
        engine = EMPDefenseEngine(config)
        engine.init()

        for _week in range(52):
            engine.tick()

        final_state = engine.observe()
        assert final_state["simulation_day"] == 52 * 7
        print("✅ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)

    return tests_failed == 0


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
