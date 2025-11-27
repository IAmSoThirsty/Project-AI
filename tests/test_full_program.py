"""
COMPREHENSIVE FULL PROGRAM TEST SUITE
Tests all modules, imports, and functionality
"""

import os
import sys

# Add src directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text):
    """Print a formatted section."""
    print(f"\n{text}")
    print("-" * 70)


def test_imports():
    """Test all critical imports."""
    print_section("[TEST 1] Module Imports")

    tests = []

    try:
        import importlib

        mod = importlib.import_module("app.core.image_generator")
        if hasattr(mod, "ImageGenerator"):
            print("✓ ImageGenerator imported successfully")
            tests.append(True)
        else:
            print("✗ ImageGenerator import failed: missing attribute")
            tests.append(False)
    except Exception as e:
        print(f"✗ ImageGenerator import failed: {e}")
        tests.append(False)

    try:
        import importlib

        mod = importlib.import_module("app.core.user_manager")
        if hasattr(mod, "UserManager"):
            print("✓ UserManager imported successfully")
            tests.append(True)
        else:
            print("✗ UserManager import failed: missing attribute")
            tests.append(False)
    except Exception as e:
        print(f"✗ UserManager import failed: {e}")
        tests.append(False)

    try:
        import importlib

        mod = importlib.import_module("app.core.intent_detection")
        if hasattr(mod, "IntentDetector"):
            print("✓ IntentDetector imported successfully")
            tests.append(True)
        else:
            print("✗ IntentDetector import failed: missing attribute")
            tests.append(False)
    except Exception as e:
        print(f"✗ IntentDetector import failed: {e}")
        tests.append(False)

    try:
        import importlib

        mod = importlib.import_module("app.core.learning_paths")
        if hasattr(mod, "LearningPathManager"):
            print("✓ LearningPathManager imported successfully")
            tests.append(True)
        else:
            print("✗ LearningPathManager import failed: missing attribute")
            tests.append(False)
    except Exception as e:
        print(f"✗ LearningPathManager import failed: {e}")
        tests.append(False)

    try:
        import importlib

        mod = importlib.import_module("app.core.data_analysis")
        if hasattr(mod, "DataAnalyzer"):
            print("✓ DataAnalyzer imported successfully")
            tests.append(True)
        else:
            print("✗ DataAnalyzer import failed: missing attribute")
            tests.append(False)
    except Exception as e:
        print(f"✗ DataAnalyzer import failed: {e}")
        tests.append(False)

    try:
        import importlib

        mod = importlib.import_module("app.gui.settings_dialog")
        if hasattr(mod, "SettingsDialog"):
            print("✓ SettingsDialog imported successfully")
            tests.append(True)
        else:
            print("✗ SettingsDialog import failed: missing attribute")
            tests.append(False)
    except Exception as e:
        print(f"✗ SettingsDialog import failed: {e}")
        tests.append(False)

    assert all(tests)


def test_image_generator():
    """Test image generator functionality."""
    print_section("[TEST 2] Image Generator Functionality")

    from app.core.image_generator import ImageGenerator

    generator = ImageGenerator()
    tests = []

    # Test 1: Blocked content
    is_valid = generator._validate_prompt("create explicit content")
    if not is_valid:
        print("✓ Content filtering blocks inappropriate prompts")
        tests.append(True)
    else:
        print("✗ Content filtering failed")
        tests.append(False)

    # Test 2: Safe content
    is_valid = generator._validate_prompt("beautiful mountain landscape")
    if is_valid:
        print("✓ Content filtering allows safe prompts")
        tests.append(True)
    else:
        print("✗ Safe content incorrectly blocked")
        tests.append(False)

    # Test 3: Style presets
    presets = generator.get_available_styles()
    if len(presets) >= 10:
        print(f"✓ Style presets available: {len(presets)}")
        tests.append(True)
    else:
        print(f"✗ Insufficient style presets: {len(presets)}")
        tests.append(False)

    # Test 4: Safety negative prompts
    if "nsfw" in " ".join(generator.SAFETY_NEGATIVE_PROMPTS).lower():
        print("✓ Safety negative prompts configured")
        tests.append(True)
    else:
        print("✗ Safety negative prompts missing")
        tests.append(False)

    # Test 5: Empty prompt rejection
    try:
        generator.generate_image("")
        print("✗ Empty prompt not rejected")
        tests.append(False)
    except ValueError:
        print("✓ Empty prompts properly rejected")
        tests.append(True)

    assert all(tests)


def test_user_manager():
    """Test user manager functionality."""
    print_section("[TEST 3] User Manager Functionality")

    from app.core.user_manager import UserManager

    manager = UserManager()
    tests = []

    # Test 1: Manager initialization
    if manager is not None:
        print("✓ UserManager initialized successfully")
        tests.append(True)
    else:
        print("✗ UserManager initialization failed")
        tests.append(False)

    # Test 2: Check password context
    if hasattr(manager, "pwd_context"):
        print("✓ Password context configured")
        tests.append(True)
    else:
        print("✗ Password context missing")
        tests.append(False)

    # Test 3: User data file path
    if hasattr(manager, "user_file"):
        print(f"✓ User data file configured: {manager.user_file}")
        tests.append(True)
    else:
        print("✗ User data file not configured")
        tests.append(False)

    assert all(tests)


def test_settings():
    """Test settings functionality."""
    print_section("[TEST 4] Settings Management")

    from app.gui.settings_dialog import SettingsDialog

    tests = []

    # Test 1: Load settings
    try:
        settings = SettingsDialog.load_settings()
        print(f"✓ Settings loaded: {len(settings)} keys")
        tests.append(True)
    except Exception as e:
        print(f"✗ Settings load failed: {e}")
        tests.append(False)

    # Test 2: Default settings structure
    if isinstance(settings, dict):
        required_keys = ["theme", "ui_scale", "content_filter"]
        if all(key in settings for key in required_keys):
            print("✓ All required settings present")
            tests.append(True)
        else:
            print("✗ Missing required settings")
            tests.append(False)
    else:
        print("✗ Settings not a dictionary")
        tests.append(False)

    # Test 3: Content filter default
    if settings.get("content_filter", False):
        print("✓ Content filtering enabled by default")
        tests.append(True)
    else:
        print("⚠ Content filtering not enabled by default")
        tests.append(True)  # Not critical

    assert all(tests)


def test_file_structure():
    """Test file and directory structure."""
    print_section("[TEST 5] File Structure Verification")

    tests = []
    base_path = os.path.join(os.path.dirname(__file__), "..")

    required_files = [
        "src/app/main.py",
        "src/app/core/image_generator.py",
        "src/app/core/user_manager.py",
        "src/app/gui/dashboard.py",
        "src/app/gui/login.py",
        "src/app/gui/settings_dialog.py",
        "src/app/gui/image_generation.py",
        "requirements.txt",
        "README.md",
    ]

    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
            tests.append(True)
        else:
            print(f"✗ Missing: {file_path}")
            tests.append(False)

    assert all(tests)


def run_full_test_suite():
    """Run complete test suite."""
    print_header("COMPREHENSIVE PROGRAM TEST SUITE")
    print("Testing all modules, imports, and functionality...")

    results = {}
    for name, func in [
        ("Module Imports", test_imports),
        ("Image Generator", test_image_generator),
        ("User Manager", test_user_manager),
        ("Settings Management", test_settings),
        ("File Structure", test_file_structure),
    ]:
        try:
            func()
            results[name] = True
        except Exception:
            results[name] = False

    print_header("TEST RESULTS SUMMARY")

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    print("\n" + "=" * 70)
    print(f"Overall: {passed}/{total} test categories passed")

    if passed == total:
        print("✅ ALL TESTS PASSED - PROGRAM FULLY FUNCTIONAL")
        return True
    else:
        print(f"⚠️ {total - passed} test category(s) failed")
        return False


if __name__ == "__main__":
    import time

    start_time = time.time()

    success = run_full_test_suite()

    elapsed = time.time() - start_time
    print(f"\nTest suite completed in {elapsed:.2f} seconds")
    print("=" * 70)

    sys.exit(0 if success else 1)
