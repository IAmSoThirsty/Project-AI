#!/usr/bin/env python3
"""
Verify uniqueness of all 2000 stress tests.
"""

import hashlib
import json


def verify_uniqueness():
    """Check if all tests are unique."""

    # Load tests
    with open("adversarial_stress_tests_2000.json") as f:
        data = json.load(f)

    all_tests = data["red_team_tests"] + data["black_team_tests"]

    print("=" * 70)
    print("UNIQUENESS VERIFICATION")
    print("=" * 70)

    # Check unique IDs
    test_ids = [t["id"] for t in all_tests]
    unique_ids = set(test_ids)
    print("\n1. TEST IDs:")
    print(f"   Total tests: {len(all_tests)}")
    print(f"   Unique IDs: {len(unique_ids)}")
    print(f"   [OK] All IDs unique: {len(all_tests) == len(unique_ids)}")

    if len(all_tests) != len(unique_ids):
        duplicates = [id for id in test_ids if test_ids.count(id) > 1]
        print(f"   ❌ Duplicate IDs found: {set(duplicates)}")

    # Check unique names
    test_names = [t["name"] for t in all_tests]
    unique_names = set(test_names)
    print("\n2. TEST NAMES:")
    print(f"   Unique names: {len(unique_names)}")
    print(f"   ✅ All names unique: {len(all_tests) == len(unique_names)}")

    # Check unique scenarios (by steps hash)
    scenario_hashes = []
    for t in all_tests:
        scenario_str = json.dumps(t["steps"], sort_keys=True)
        scenario_hash = hashlib.md5(scenario_str.encode()).hexdigest()
        scenario_hashes.append(scenario_hash)

    unique_scenarios = set(scenario_hashes)
    print("\n3. TEST SCENARIOS (by steps content):")
    print(f"   Unique scenarios: {len(unique_scenarios)}")
    print(f"   ✅ All scenarios unique: {len(all_tests) == len(unique_scenarios)}")

    if len(all_tests) != len(unique_scenarios):
        print("   ⚠️  Some tests have identical step sequences")

    # Category distribution
    print("\n4. CATEGORY DISTRIBUTION:")
    red_categories = {}
    black_categories = {}

    for t in all_tests:
        key = f"{t['category']}-{t['subcategory']}"
        if t["team"] == "red_team":
            red_categories[key] = red_categories.get(key, 0) + 1
        else:
            black_categories[key] = black_categories.get(key, 0) + 1

    print(f"\n   RED TEAM ({len(data['red_team_tests'])} tests):")
    for cat, count in sorted(red_categories.items()):
        print(f"     - {cat}: {count}")

    print(f"\n   BLACK TEAM ({len(data['black_team_tests'])} tests):")
    for cat, count in sorted(black_categories.items()):
        print(f"     - {cat}: {count}")

    # Severity distribution
    print("\n5. SEVERITY DISTRIBUTION:")
    severities = {}
    for t in all_tests:
        sev = t["severity"]
        severities[sev] = severities.get(sev, 0) + 1

    for sev, count in sorted(severities.items()):
        pct = (count / len(all_tests)) * 100
        print(f"   - {sev.upper()}: {count} ({pct:.1f}%)")

    # Sample unique tests
    print("\n6. SAMPLE UNIQUE TEST IDs:")
    for id in sorted(unique_ids)[:10]:
        print(f"   - {id}")

    # Verification summary
    print(f"\n{'='*70}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*70}")

    all_unique = (
        len(all_tests) == len(unique_ids)
        and len(all_tests) == len(unique_names)
        and len(all_tests) == len(unique_scenarios)
    )

    if all_unique:
        print("✅ ALL 2000 TESTS ARE COMPLETELY UNIQUE")
        print("   - Unique IDs: ✅")
        print("   - Unique names: ✅")
        print("   - Unique scenarios: ✅")
    else:
        print("⚠️  UNIQUENESS ISSUES DETECTED")
        if len(all_tests) != len(unique_ids):
            print("   - IDs: ❌ (duplicates found)")
        if len(all_tests) != len(unique_names):
            print("   - Names: ❌ (duplicates found)")
        if len(all_tests) != len(unique_scenarios):
            print("   - Scenarios: ⚠️  (some steps are identical)")

    print(f"{'='*70}\n")

    return all_unique


if __name__ == "__main__":
    verify_uniqueness()
