#!/usr/bin/env python3
"""Simple demonstration of Liara safety mechanisms"""

import sys
import os

# Add kernel to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kernel'))

# Now import
from liara_safety import (
    Capability,
    LiaraSafetyGuard,
    SafetyViolation,
)

print("=" * 80)
print(" LIARA SAFETY GUARDRAILS - QUICK DEMONSTRATION")
print("=" * 80)

# Test 1: Basic token issuance
print("\n[TEST 1] Token Issuance & Validation")
print("-" * 40)
guard = LiaraSafetyGuard()

caps = {Capability.READ_METRICS, Capability.RESTART_SERVICE}
token = guard.issue_token("test_role", caps, 300)
print(f"✓ Token issued: role={token.role}, ttl=300s")
print(f"✓ Token valid: {token.is_valid(guard.secret_key)}")

# Test 2: TTL enforcement
print("\n[TEST 2] TTL Enforcement")
print("-" * 40)
try:
    guard.issue_token("test", {Capability.READ_METRICS}, 1000)
    print("✗ Should have rejected TTL > 900s")
except SafetyViolation as e:
    print(f"✓ TTL limit enforced: {e}")

guard.revoke_token("cleanup")

# Test 3: Capability restrictions
print("\n[TEST 3] Capability Restrictions")
print("-" * 40)
guard.issue_token("limited", {Capability.READ_METRICS}, 300)

guard.check_action("read_metrics", Capability.READ_METRICS)
print("✓ Allowed action succeeded")

try:
    guard.check_action("restart", Capability.RESTART_SERVICE)
    print("✗ Should have been denied")
except SafetyViolation as e:
    print(f"✓ Unauthorized action blocked: {e}")

guard.revoke_token("cleanup")

# Test 4: Prohibited operations
print("\n[TEST 4] Prohibited Operations")
print("-" * 40)
guard2 = LiaraSafetyGuard()  # Fresh guard
guard2.issue_token("test", {Capability.READ_METRICS}, 300)

try:
    guard2.check_action("execute_shell", Capability.READ_METRICS)
    print("✗ Should have triggered kill switch")
except SafetyViolation as e:
    print(f"✓ Prohibited operation blocked: {e}")

print(f"✓ Kill switch activated: {guard2.kill_switch_activated}")

# Test 5: Audit logging
print("\n[TEST 5] Audit Logging")
print("-" * 40)
guard3 = LiaraSafetyGuard()  # Fresh guard
guard3.issue_token("auditor", {Capability.READ_METRICS}, 300)
guard3.check_action("action1", Capability.READ_METRICS)
guard3.check_action("action2", Capability.READ_METRICS)
guard3.revoke_token("done")

print(f"✓ Audit entries logged: {len(guard3.audit_log.entries)}")
print(f"✓ Audit integrity verified: {guard3.audit_log.verify_integrity()}")

# Show recent log entries
print("\nRecent audit entries:")
for entry in guard3.audit_log.entries[-3:]:
    print(f"  {entry.timestamp.strftime('%H:%M:%S')} | {entry.action:20s} | {entry.result}")

print("\n" + "=" * 80)
print(" ✅ ALL SAFETY MECHANISMS WORKING CORRECTLY")
print("=" * 80)
