"""Diagnose import errors for all failing test files - get root cause."""
import subprocess
import sys

files = [
    "tests/test_cerberus_hydra.py",
    "tests/test_cli.py",
    "tests/test_contrarian_firewall.py",
    "tests/test_defense_engine_integration.py",
    "tests/test_enhanced_scenario_engine.py",
    "tests/test_extract_with_permissions.py",
    "tests/test_global_scenario_engine.py",
    "tests/test_hydra_50_engine.py",
    "tests/test_irreversibility_locks.py",
    "tests/test_leather_book_smoke.py",
    "tests/test_mcp_server.py",
    "tests/test_planetary_defense_monolith.py",
    "tests/test_policy_guard.py",
    "tests/test_tarl_load_chaos_soak.py",
    "tests/test_tarl_orchestration.py",
    "tests/test_tarl_orchestration_extended.py",
    "tests/test_tarl_orchestration_governance.py",
    "tests/test_temporal_integration.py",
    "tests/gradle_evolution/test_api.py",
    "tests/gradle_evolution/test_audit.py",
    "tests/gradle_evolution/test_capsules.py",
    "tests/gradle_evolution/test_cognition.py",
    "tests/gradle_evolution/test_constitutional.py",
    "tests/gradle_evolution/test_integration.py",
    "tests/gradle_evolution/test_security.py",
    "tests/gui_e2e/test_launch_and_login.py",
    "tests/temporal/test_config.py",
]

for f in files:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f, "--collect-only", "--tb=long", "-q"],
        capture_output=True,
        text=True,
    )
    combined = r.stdout + "\n" + r.stderr
    for line in combined.split("\n"):
        s = line.strip()
        if s.startswith("E") and ("ModuleNotFoundError" in s or "No module named" in s):
            print(f"{f}|{s}")
            break
    else:
        for line in combined.split("\n"):
            s = line.strip()
            if s.startswith("E") and "Error" in s:
                print(f"{f}|{s}")
                break
