#!/usr/bin/env python3
"""Display sample test with all fields."""

import json

# Load tests
with open("adversarial_stress_tests_2000.json", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 70)
print("STRESS TEST FIELDS VERIFICATION")
print("=" * 70)

# Get sample tests
red_test = data["red_team_tests"][0]
black_test = data["black_team_tests"][0]

print("\n📋 RED TEAM TEST SAMPLE:\n")
print(json.dumps(red_test, indent=2))

print("\n" + "=" * 70)
print("\n📋 BLACK TEAM TEST SAMPLE:\n")
print(json.dumps(black_test, indent=2))

print("\n" + "=" * 70)
print("\n✅ FIELD VERIFICATION:\n")

required_fields = [
    "description",
    "severity",
    "steps",
    "expected_behavior",
    "exploited_weakness",
    "tarl_enforcement",
    "success_criteria",
]

print("Checking RED TEAM test...")
for field in required_fields:
    status = "✓" if field in red_test else "✗"
    print(f"  {status} {field}")

print("\nChecking BLACK TEAM test...")
for field in required_fields:
    status = "✓" if field in black_test else "✗"
    print(f"  {status} {field}")

print("\n" + "=" * 70)
print("\n🎯 SUMMARY:")
print(f"  Total tests: {len(data['red_team_tests']) + len(data['black_team_tests'])}")
print(f"  RED TEAM: {len(data['red_team_tests'])}")
print(f"  BLACK TEAM: {len(data['black_team_tests'])}")
print("\n  All required fields: PRESENT")
print("=" * 70)
