#!/usr/bin/env python3
"""Verify uniqueness of all 2000 stress tests - ASCII only."""

import hashlib
import json

# Load tests
with open("adversarial_stress_tests_2000.json", encoding="utf-8") as f:
    data = json.load(f)

all_tests = data["red_team_tests"] + data["black_team_tests"]

print("=" * 70)
print("UNIQUENESS VERIFICATION REPORT")
print("=" * 70)

# Check unique IDs
test_ids = [t["id"] for t in all_tests]
unique_ids = set(test_ids)
print("\n1. TEST IDs:")
print(f"   Total tests: {len(all_tests)}")
print(f"   Unique IDs: {len(unique_ids)}")
print(
    f"   Result: {'PASS - All IDs unique' if len(all_tests) == len(unique_ids) else 'FAIL - Duplicates found'}"
)

# Check unique names
test_names = [t["name"] for t in all_tests]
unique_names = set(test_names)
print("\n2. TEST NAMES:")
print(f"   Unique names: {len(unique_names)}")
print(
    f"   Result: {'PASS - All names unique' if len(all_tests) == len(unique_names) else 'FAIL - Duplicates found'}"
)

# Check unique scenarios
scenario_hashes = []
for t in all_tests:
    scenario_str = json.dumps(t["steps"], sort_keys=True)
    scenario_hash = hashlib.md5(scenario_str.encode()).hexdigest()
    scenario_hashes.append(scenario_hash)

unique_scenarios = set(scenario_hashes)
print("\n3. TEST SCENARIOS (by steps content):")
print(f"   Unique scenarios: {len(unique_scenarios)}")
print(
    f"   Result: {'PASS - All scenarios unique' if len(all_tests) == len(unique_scenarios) else 'INFO - Some steps reused (expected for variations)'}"
)

# Category distribution
print("\n4. CATEGORY DISTRIBUTION:")
red_cats = {}
black_cats = {}

for t in all_tests:
    key = f"{t['category']}-{t['subcategory']}"
    if t["team"] == "red_team":
        red_cats[key] = red_cats.get(key, 0) + 1
    else:
        black_cats[key] = black_cats.get(key, 0) + 1

print(f"\n   RED TEAM ({len(data['red_team_tests'])} tests):")
for cat, count in sorted(red_cats.items()):
    print(f"     {cat}: {count}")

print(f"\n   BLACK TEAM ({len(data['black_team_tests'])} tests):")
for cat, count in sorted(black_cats.items()):
    print(f"     {cat}: {count}")

# Sample IDs
print("\n5. SAMPLE TEST IDs:")
for id in sorted(unique_ids)[:15]:
    print(f"   {id}")

# Final verdict
print(f"\n{'='*70}")
print("FINAL VERDICT")
print(f"{'='*70}")

ids_unique = len(all_tests) == len(unique_ids)
names_unique = len(all_tests) == len(unique_names)

if ids_unique and names_unique:
    print("PASS: All 2000 tests have unique IDs and names")
    print(f"  - {len(unique_ids)} unique test IDs")
    print(f"  - {len(unique_names)} unique test names")
    print(f"  - {len(unique_scenarios)} unique scenario patterns")
else:
    print("FAIL: Duplicate tests found")

print(f"{'='*70}\n")
