"""
TARL OS - Comprehensive Test Suite
Tests for all TARL OS subsystems
Copyright (c) 2026 Project-AI - God Tier AI Operating System
"""

import sys
import unittest
from pathlib import Path

# Add tarl_os to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tarl_os.bridge import TARLOSBridge


class TestTARLOSBridge(unittest.TestCase):
    """Test the TARL OS bridge functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.bridge = TARLOSBridge()

    def test_initialization(self):
        """Test that the bridge initializes correctly."""
        self.assertIsNotNone(self.bridge)
        self.assertEqual(len(self.bridge.module_paths), 5)

    def test_module_paths_exist(self):
        """Test that all module paths are valid."""
        for name, path in self.bridge.module_paths.items():
            self.assertTrue(
                path.exists(), f"Module path does not exist: {name} at {path}"
            )

    def test_load_module(self):
        """Test loading a module."""
        result = self.bridge.load_module("scheduler")
        self.assertTrue(result)
        self.assertIn("scheduler", self.bridge.module_cache)

    def test_system_status(self):
        """Test getting system status."""
        status = self.bridge.get_system_status()

        self.assertIn("tarl_os_version", status)
        self.assertEqual(status["tarl_os_version"], "2.0")
        self.assertIn("modules_available", status)
        self.assertGreaterEqual(status["modules_available"], 5)

    def test_initialize_kernel(self):
        """Test kernel initialization."""
        results = self.bridge.initialize_kernel()

        # Check all subsystems initialized
        self.assertIn("scheduler", results)
        self.assertIn("memory", results)
        self.assertIn("config", results)
        self.assertIn("secrets", results)
        self.assertIn("rbac", results)

        # Check each subsystem returned success
        for name, result in results.items():
            self.assertIsNotNone(result, f"{name} returned None")
            self.assertIn("status", result, f"{name} missing status")


class TestModuleIntegrity(unittest.TestCase):
    """Test the integrity of Thirsty-Lang modules."""

    def setUp(self):
        """Set up test fixtures."""
        self.tarl_os_root = Path(__file__).parent.parent

    def test_scheduler_module_exists(self):
        """Test scheduler module exists and has content."""
        scheduler_path = self.tarl_os_root / "kernel" / "scheduler.thirsty"
        self.assertTrue(scheduler_path.exists())

        content = scheduler_path.read_text()
        self.assertGreater(len(content), 1000)
        self.assertIn("shield scheduler", content)
        self.assertIn("initScheduler", content)
        self.assertIn("createProcess", content)

    def test_memory_module_exists(self):
        """Test memory manager module exists and has content."""
        memory_path = self.tarl_os_root / "kernel" / "memory.thirsty"
        self.assertTrue(memory_path.exists())

        content = memory_path.read_text()
        self.assertGreater(len(content), 1000)
        self.assertIn("shield memoryManager", content)
        self.assertIn("initMemoryManager", content)
        self.assertIn("allocateMemory", content)


class TestSecurityFeatures(unittest.TestCase):
    """Test security features in modules."""

    def setUp(self):
        """Set up test fixtures."""
        self.tarl_os_root = Path(__file__).parent.parent

    def test_all_modules_use_shield(self):
        """Test that all modules use the shield construct."""
        module_dirs = [
            self.tarl_os_root / "kernel",
            self.tarl_os_root / "security",
            self.tarl_os_root / "config",
        ]

        for module_dir in module_dirs:
            if not module_dir.exists():
                continue

            for thirsty_file in module_dir.glob("*.thirsty"):
                content = thirsty_file.read_text()
                self.assertIn(
                    "shield",
                    content,
                    f"{thirsty_file.name} does not use 'shield' construct",
                )


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTARLOSBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestModuleIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityFeatures))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TARL OS Test Suite Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
