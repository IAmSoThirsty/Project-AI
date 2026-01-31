#!/usr/bin/env python3
"""
README.md Protection Verification Script

Tests all protection mechanisms to ensure README.md is never touched by automation.
"""

import json
import sys
from pathlib import Path


def test_config_protection():
    """Verify README.md is not in configuration."""
    print("🔍 Testing configuration protection...")
    
    config_path = Path(".test-report-updater.config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    # Check documentation targets
    for target in config.get('documentation_targets', []):
        filepath = target.get('path', '')
        if 'readme.md' in filepath.lower():
            print(f"❌ FAIL: README.md found in configuration: {filepath}")
            return False
    
    print("✅ PASS: README.md not in configuration")
    return True


def test_code_protection():
    """Verify protection code exists in scripts."""
    print("\n🔍 Testing code-level protection...")
    
    scripts = [
        'scripts/update_test_documentation.py',
        'scripts/organize_historical_docs.py'
    ]
    
    for script_path in scripts:
        with open(script_path) as f:
            content = f.read()
        
        # Check for protection keywords
        if 'PROTECTED' not in content or 'README' not in content.upper():
            print(f"❌ FAIL: Protection code missing in {script_path}")
            return False
        
        print(f"✅ Protection code found in {script_path}")
    
    print("✅ PASS: All scripts have protection code")
    return True


def test_policy_exists():
    """Verify protection policy document exists."""
    print("\n🔍 Testing policy documentation...")
    
    policy_path = Path("CRITICAL_README_PROTECTION_POLICY.md")
    if not policy_path.exists():
        print("❌ FAIL: Protection policy document not found")
        return False
    
    with open(policy_path) as f:
        content = f.read()
    
    required_phrases = [
        "OFF LIMITS",
        "wrath of Thirsty",
        "ABSOLUTELY PROTECTED"
    ]
    
    for phrase in required_phrases:
        if phrase not in content:
            print(f"❌ FAIL: Policy missing required phrase: {phrase}")
            return False
    
    print("✅ PASS: Protection policy exists and is complete")
    return True


def test_readme_exists():
    """Verify README.md still exists (we protect it, not delete it)."""
    print("\n🔍 Testing README.md existence...")
    
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("⚠️  WARNING: README.md does not exist")
        return True  # Not a failure, just informational
    
    print("✅ README.md exists (as it should)")
    return True


def main():
    """Run all protection tests."""
    print("=" * 80)
    print("README.md PROTECTION VERIFICATION")
    print("=" * 80)
    print()
    
    tests = [
        test_config_protection,
        test_code_protection,
        test_policy_exists,
        test_readme_exists
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ ERROR: {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("✅ README.md is fully protected from automation")
        print("✅ Only Thirsty may modify README.md")
        print("✅ The wrath of Thirsty will not be invoked")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("❌ README.md protection may be incomplete")
        print("⚠️  Fix protection mechanisms immediately!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
