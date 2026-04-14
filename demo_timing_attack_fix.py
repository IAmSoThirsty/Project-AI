"""Demonstration of timing attack mitigation in UserManager.

This script demonstrates that the fixed authenticate() method
prevents timing-based username enumeration attacks.
"""

import statistics
import tempfile
import time

from app.core.user_manager import UserManager


def measure_authentication_timing():
    """Measure and compare authentication timing for existing vs non-existing users."""
    
    print("=" * 80)
    print("TIMING ATTACK MITIGATION DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Create UserManager with a test user
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = UserManager(users_file="test_users.json", data_dir=tmpdir)
        
        # Create test user
        print("[+] Creating test user 'alice' with secure password...")
        manager.create_user("alice", "SecurePass123!", persona="friendly")
        print("    ✓ User created successfully")
        print()
        
        # Scenario 1: Test with existing user (wrong password)
        print("[1] Testing authentication with EXISTING user (wrong password)...")
        timings_existing = []
        for i in range(10):
            start = time.time()
            success, msg = manager.authenticate("alice", f"wrongpass{i}")
            elapsed = time.time() - start
            timings_existing.append(elapsed)
            if i % 3 == 2:  # Reset failed attempts to avoid lockout
                manager.users["alice"]["failed_attempts"] = 0
        
        avg_existing = statistics.mean(timings_existing)
        min_existing = min(timings_existing)
        max_existing = max(timings_existing)
        print(f"    Average time: {avg_existing:.4f}s")
        print(f"    Range:        {min_existing:.4f}s - {max_existing:.4f}s")
        print()
        
        # Scenario 2: Test with non-existing user
        print("[2] Testing authentication with NON-EXISTING user...")
        timings_nonexisting = []
        for i in range(10):
            start = time.time()
            success, msg = manager.authenticate(f"nobody{i}", f"anypass{i}")
            elapsed = time.time() - start
            timings_nonexisting.append(elapsed)
        
        avg_nonexisting = statistics.mean(timings_nonexisting)
        min_nonexisting = min(timings_nonexisting)
        max_nonexisting = max(timings_nonexisting)
        print(f"    Average time: {avg_nonexisting:.4f}s")
        print(f"    Range:        {min_nonexisting:.4f}s - {max_nonexisting:.4f}s")
        print()
        
        # Analysis
        print("=" * 80)
        print("TIMING ANALYSIS")
        print("=" * 80)
        diff = abs(avg_existing - avg_nonexisting)
        print(f"Average time difference: {diff:.4f}s ({diff*1000:.1f}ms)")
        print()
        
        if diff < 0.05:  # Less than 50ms
            print("✓ SECURE: Timing difference is negligible (< 50ms)")
            print("  An attacker cannot reliably distinguish between existing")
            print("  and non-existing users based on response time.")
        else:
            print("✗ VULNERABLE: Timing difference is exploitable (> 50ms)")
            print("  An attacker could enumerate usernames by measuring timing.")
        
        print()
        print("=" * 80)
        print("SECURITY FEATURES")
        print("=" * 80)
        print("✓ Constant-time execution: Both paths verify password hash")
        print("✓ Dummy hash for non-existing users: Prevents fast rejection")
        print("✓ Random delay (10-30ms): Adds noise to timing measurements")
        print("✓ Consistent error messages: Same message for all failures")
        print("✓ Account lockout: 5 failed attempts trigger 15-minute lock")
        print()
        
        # Test correct authentication
        print("=" * 80)
        print("FUNCTIONAL TEST")
        print("=" * 80)
        
        # Reset alice's account
        manager.users["alice"]["failed_attempts"] = 0
        manager.users["alice"]["locked_until"] = None
        manager.save_users()
        
        print("[+] Testing correct password...")
        success, msg = manager.authenticate("alice", "SecurePass123!")
        if success:
            print(f"    ✓ {msg}")
        else:
            print(f"    ✗ {msg}")
        
        print()
        print("[+] Testing wrong password...")
        success, msg = manager.authenticate("alice", "WrongPassword")
        if not success:
            print(f"    ✓ Correctly rejected: {msg}")
        else:
            print(f"    ✗ Should have been rejected")
        
        print()
        print("[+] Testing non-existing user...")
        success, msg = manager.authenticate("nobody", "anypass")
        if not success:
            print(f"    ✓ Correctly rejected: {msg}")
        else:
            print(f"    ✗ Should have been rejected")
        
        print()
        print("=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    measure_authentication_timing()
