#!/usr/bin/env python3
"""
Test GitHub Language Recognition Configuration

This script verifies that Thirsty-lang files are properly configured
for GitHub language detection and statistics.
"""

import subprocess
import sys
from pathlib import Path


def test_gitattributes():
    """Test that gitattributes are properly configured"""
    print("Testing .gitattributes configuration...")

    test_cases = [
        ("src/thirsty_lang/examples/hello.thirsty", "Thirsty-lang"),
        ("src/thirsty_lang/examples/variables.thirsty", "Thirsty-lang"),
    ]

    passed = 0
    failed = 0

    for file_path, expected_language in test_cases:
        try:
            result = subprocess.run(
                ["git", "check-attr", "linguist-language", file_path],
                capture_output=True,
                text=True,
                check=True,
            )

            if expected_language in result.stdout:
                print(f"  ✓ {file_path}: {expected_language}")
                passed += 1
            else:
                print(f"  ✗ {file_path}: Expected {expected_language}, got {result.stdout}")
                failed += 1

        except subprocess.CalledProcessError as e:
            print(f"  ✗ {file_path}: Git command failed - {e}")
            failed += 1

    return passed, failed


def test_file_extensions():
    """Test that all Thirsty-lang extensions are present"""
    print("\nTesting Thirsty-lang file extensions...")

    extensions = [".thirsty", ".thirstyplus", ".thirstyplusplus", ".thirstofgods"]

    passed = 0
    failed = 0

    for ext in extensions:
        # Check if extension is in root .gitattributes
        try:
            with open(".gitattributes") as f:
                content = f.read()
                if f"*{ext}" in content and "linguist-language=Thirsty-lang" in content:
                    print(f"  ✓ Extension {ext} configured")
                    passed += 1
                else:
                    print(f"  ✗ Extension {ext} not properly configured")
                    failed += 1
        except FileNotFoundError:
            print("  ✗ .gitattributes not found")
            failed += 1
            break

    return passed, failed


def test_linguist_files():
    """Test that linguist configuration files exist"""
    print("\nTesting linguist configuration files...")

    required_files = [
        "src/thirsty_lang/linguist.yml",
        "src/thirsty_lang/languages.yml",
        "src/thirsty_lang/GITHUB_LINGUIST.md",
        "src/thirsty_lang/GITHUB_RECOGNITION.md",
    ]

    passed = 0
    failed = 0

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path} exists")
            passed += 1
        else:
            print(f"  ✗ {file_path} not found")
            failed += 1

    return passed, failed


def test_example_files():
    """Test that example Thirsty-lang files exist"""
    print("\nTesting example Thirsty-lang files...")

    examples_dir = Path("src/thirsty_lang/examples")

    if not examples_dir.exists():
        print("  ✗ Examples directory not found")
        return 0, 1

    thirsty_files = list(examples_dir.glob("**/*.thirsty"))

    if len(thirsty_files) > 0:
        print(f"  ✓ Found {len(thirsty_files)} .thirsty files")
        for f in thirsty_files[:5]:  # Show first 5
            print(f"    - {f}")
        if len(thirsty_files) > 5:
            print(f"    ... and {len(thirsty_files) - 5} more")
        return 1, 0
    else:
        print("  ✗ No .thirsty files found")
        return 0, 1


def test_vendoring_config():
    """Test that vendoring is properly configured"""
    print("\nTesting vendoring configuration...")

    passed = 0
    failed = 0

    # Check that examples are not vendored
    try:
        result = subprocess.run(
            [
                "git",
                "check-attr",
                "linguist-vendored",
                "src/thirsty_lang/examples/hello.thirsty",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if "false" in result.stdout or "unspecified" in result.stdout:
            print("  ✓ Examples are not vendored")
            passed += 1
        else:
            print("  ✗ Examples incorrectly marked as vendored")
            failed += 1

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Git command failed - {e}")
        failed += 1

    # Check that node_modules would be vendored
    with open(".gitattributes") as f:
        content = f.read()
        if "node_modules/**" in content and "linguist-vendored" in content:
            print("  ✓ Vendor directories are configured")
            passed += 1
        else:
            print("  ✗ Vendor directories not properly configured")
            failed += 1

    return passed, failed


def main():
    """Run all tests"""
    print("=" * 70)
    print("  GitHub Language Recognition Test Suite")
    print("  Testing Thirsty-lang Configuration")
    print("=" * 70)
    print()

    total_passed = 0
    total_failed = 0

    # Run all tests
    tests = [
        ("GitAttributes Configuration", test_gitattributes),
        ("File Extensions", test_file_extensions),
        ("Linguist Files", test_linguist_files),
        ("Example Files", test_example_files),
        ("Vendoring Configuration", test_vendoring_config),
    ]

    for _test_name, test_func in tests:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            total_failed += 1

    # Summary
    print()
    print("=" * 70)
    print("  Test Summary")
    print("=" * 70)
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Total:  {total_passed + total_failed}")
    print()

    if total_failed == 0:
        print("  ✅ All tests passed! GitHub language recognition is configured.")
        print()
        print("  Next steps:")
        print("  1. Push changes to GitHub")
        print("  2. Check repository language statistics")
        print("  3. Verify Thirsty-lang appears in language bar")
        print("  4. (Optional) Submit to github/linguist for official recognition")
        return 0
    else:
        print(f"  ❌ {total_failed} test(s) failed. Please review configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
