# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_dos_trap.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_dos_trap.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Tests for DOS Trap Mode
"""

import unittest
import time
import tempfile
import os
from unittest.mock import Mock

from thirstys_waterfall.security.dos_trap import (
    CompromiseDetector,
    CompromiseEvent,
    CompromiseType,
    ThreatLevel,
    ResponseAction,
    SanitizationMode,
    SecretWiper,
    HardwareKeyDestroyer,
    InterfaceDisabler,
    MemorySanitizer,
    DiskSanitizer,
    KernelInterface,
    create_dos_trap,
)


class TestCompromiseDetector(unittest.TestCase):
    """Test CompromiseDetector functionality"""

    def setUp(self):
        self.detector = CompromiseDetector()
        self.detector.initialize()

    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector._baseline_snapshot)
        self.assertTrue(hasattr(self.detector, "kernel_interface"))

    def test_rootkit_detection(self):
        """Test rootkit detection"""
        # Should not detect rootkit in clean environment
        event = self.detector.detect_rootkit()
        # event may be None or an event depending on system state
        if event:
            self.assertIsInstance(event, CompromiseEvent)

    def test_kernel_hook_detection(self):
        """Test kernel hook detection"""
        event = self.detector.detect_kernel_hooks()
        # Should not detect hooks on first run (baseline established)
        self.assertIsNone(event)

    def test_comprehensive_scan(self):
        """Test comprehensive system scan"""
        events = self.detector.comprehensive_scan()
        self.assertIsInstance(events, list)


class TestKernelInterface(unittest.TestCase):
    """Test KernelInterface functionality"""

    def setUp(self):
        self.kernel = KernelInterface()

    def test_get_loaded_modules(self):
        """Test getting loaded kernel modules"""
        modules = self.kernel.get_loaded_kernel_modules()
        self.assertIsInstance(modules, set)

    def test_detect_suspicious_modules(self):
        """Test suspicious module detection"""
        # Test with known good modules
        clean_modules = {"ext4", "sd_mod", "usb_storage"}
        suspicious = self.kernel.detect_suspicious_modules(clean_modules)
        self.assertEqual(len(suspicious), 0)

        # Test with suspicious patterns
        bad_modules = {"reptile", ".hidden_module", "_secret"}
        suspicious = self.kernel.detect_suspicious_modules(bad_modules)
        self.assertGreater(len(suspicious), 0)

    def test_syscall_table_hash(self):
        """Test syscall table hashing"""
        hash_value = self.kernel.get_syscall_table_hash()
        # May be None if insufficient permissions
        if hash_value:
            self.assertIsInstance(hash_value, bytes)


class TestSecretWiper(unittest.TestCase):
    """Test SecretWiper functionality"""

    def setUp(self):
        self.wiper = SecretWiper()

    def test_wipe_master_keys(self):
        """Test master key wiping"""
        keys = {
            "master_key_1": b"secret_data_1",
            "master_key_2": b"secret_data_2",
            "other_key": b"other_data",
        }

        self.wiper.wipe_master_keys(keys)

        # Master keys should be removed
        self.assertNotIn("master_key_1", keys)
        self.assertNotIn("master_key_2", keys)
        # Other keys may remain

    def test_wipe_session_keys(self):
        """Test session key wiping"""
        sessions = {"session_1": b"data_1", "session_2": b"data_2"}

        self.wiper.wipe_session_keys(sessions)

        # All sessions should be cleared
        self.assertEqual(len(sessions), 0)

    def test_wipe_credentials(self):
        """Test credential wiping"""
        creds = {"user_pass": "password123", "api_key": "key456"}

        self.wiper.wipe_credentials(creds)

        # All credentials should be removed
        self.assertEqual(len(creds), 0)

    def test_emergency_wipe(self):
        """Test emergency wipe"""
        result = self.wiper.emergency_wipe_all()
        self.assertTrue(result)


class TestMemorySanitizer(unittest.TestCase):
    """Test MemorySanitizer functionality"""

    def setUp(self):
        self.sanitizer = MemorySanitizer()

    def test_sanitize_ram_single_pass(self):
        """Test single-pass RAM sanitization"""
        result = self.sanitizer.sanitize_ram(SanitizationMode.SINGLE_PASS)
        self.assertTrue(result)

    def test_sanitize_ram_three_pass(self):
        """Test three-pass RAM sanitization"""
        result = self.sanitizer.sanitize_ram(SanitizationMode.THREE_PASS)
        self.assertTrue(result)


class TestDiskSanitizer(unittest.TestCase):
    """Test DiskSanitizer functionality"""

    def setUp(self):
        self.sanitizer = DiskSanitizer()

    def test_sanitize_file_single_pass(self):
        """Test single-pass file sanitization"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"sensitive data" * 100)
            temp_file = f.name

        # Sanitize
        result = self.sanitizer.sanitize_file(temp_file, SanitizationMode.SINGLE_PASS)

        # File should be deleted
        self.assertTrue(result)
        self.assertFalse(os.path.exists(temp_file))

    def test_sanitize_file_three_pass(self):
        """Test three-pass file sanitization"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"secret data" * 50)
            temp_file = f.name

        result = self.sanitizer.sanitize_file(temp_file, SanitizationMode.THREE_PASS)

        self.assertTrue(result)
        self.assertFalse(os.path.exists(temp_file))

    def test_sanitize_directory(self):
        """Test directory sanitization"""
        # Create temporary directory with files
        temp_dir = tempfile.mkdtemp()

        for i in range(3):
            with open(os.path.join(temp_dir, f"file_{i}.txt"), "wb") as f:
                f.write(b"data" * 10)

        result = self.sanitizer.sanitize_directory(
            temp_dir, SanitizationMode.SINGLE_PASS
        )

        self.assertTrue(result)
        self.assertFalse(os.path.exists(temp_dir))


class TestDOSTrapMode(unittest.TestCase):
    """Test DOSTrapMode main class"""

    def setUp(self):
        self.dos_trap = create_dos_trap()

    def test_initialization(self):
        """Test DOS trap initialization"""
        self.assertIsNotNone(self.dos_trap.compromise_detector)
        self.assertIsNotNone(self.dos_trap.secret_wiper)
        self.assertIsNotNone(self.dos_trap.memory_sanitizer)
        self.assertIsNotNone(self.dos_trap.disk_sanitizer)

    def test_enable_disable(self):
        """Test enabling and disabling"""
        self.dos_trap.enable()
        time.sleep(0.5)

        status = self.dos_trap.get_status()
        self.assertTrue(status["active"])

        self.dos_trap.disable()
        time.sleep(0.5)

        status = self.dos_trap.get_status()
        self.assertFalse(status["active"])

    def test_get_status(self):
        """Test status retrieval"""
        status = self.dos_trap.get_status()

        self.assertIn("active", status)
        self.assertIn("triggered", status)
        self.assertIn("threat_level", status)
        self.assertIn("detected_threats", status)
        self.assertIn("config", status)

    def test_get_threat_report(self):
        """Test threat report generation"""
        report = self.dos_trap.get_threat_report()

        self.assertIn("total_threats", report)
        self.assertIn("current_threat_level", report)
        self.assertIn("threats_by_type", report)
        self.assertIn("system_compromised", report)

    def test_register_callback(self):
        """Test callback registration"""
        callback_called = []

        def test_callback(events):
            callback_called.append(True)

        self.dos_trap.register_response_callback(test_callback)

        # Manually trigger to test callback
        self.dos_trap.config["auto_respond"] = True
        self.dos_trap.config["emergency_shutdown"] = False

        event = CompromiseEvent(
            timestamp=time.time(),
            threat_level=ThreatLevel.HIGH,
            compromise_type=CompromiseType.ROOTKIT,
            description="Test event",
            indicators=["test"],
            affected_components=["test"],
            recommended_actions=[],
        )

        self.dos_trap._handle_detected_threats([event])

        # Callback should have been called
        self.assertTrue(len(callback_called) > 0)

    def test_configuration(self):
        """Test configuration settings"""
        self.dos_trap.config["auto_respond"] = False
        self.dos_trap.config["monitor_interval"] = 30
        self.dos_trap.config["response_threshold"] = ThreatLevel.CRITICAL

        self.assertFalse(self.dos_trap.config["auto_respond"])
        self.assertEqual(self.dos_trap.config["monitor_interval"], 30)
        self.assertEqual(
            self.dos_trap.config["response_threshold"], ThreatLevel.CRITICAL
        )

    def test_wipe_all_secrets(self):
        """Test secret wiping"""
        # Should not raise exception
        try:
            self.dos_trap.wipe_all_secrets()
            success = True
        except Exception:
            success = False

        self.assertTrue(success)


class TestCompromiseEvent(unittest.TestCase):
    """Test CompromiseEvent data class"""

    def test_event_creation(self):
        """Test creating compromise event"""
        event = CompromiseEvent(
            timestamp=time.time(),
            threat_level=ThreatLevel.HIGH,
            compromise_type=CompromiseType.ROOTKIT,
            description="Test rootkit",
            indicators=["suspicious_module"],
            affected_components=["kernel"],
            recommended_actions=[ResponseAction.ALERT, ResponseAction.WIPE_SECRETS],
        )

        self.assertEqual(event.threat_level, ThreatLevel.HIGH)
        self.assertEqual(event.compromise_type, CompromiseType.ROOTKIT)
        self.assertIn("suspicious_module", event.indicators)

    def test_event_to_dict(self):
        """Test event serialization"""
        event = CompromiseEvent(
            timestamp=time.time(),
            threat_level=ThreatLevel.MODERATE,
            compromise_type=CompromiseType.PROCESS_INJECTION,
            description="Test injection",
            indicators=["test"],
            affected_components=["processes"],
            recommended_actions=[ResponseAction.ISOLATE],
        )

        event_dict = event.to_dict()

        self.assertIn("timestamp", event_dict)
        self.assertIn("threat_level", event_dict)
        self.assertIn("compromise_type", event_dict)
        self.assertIn("description", event_dict)
        self.assertIn("indicators", event_dict)
        self.assertIn("recommended_actions", event_dict)


class TestInterfaceDisabler(unittest.TestCase):
    """Test InterfaceDisabler (careful with actual execution)"""

    def setUp(self):
        self.disabler = InterfaceDisabler()

    def test_initialization(self):
        """Test disabler initialization"""
        self.assertIsNotNone(self.disabler)
        self.assertIsInstance(self.disabler._disabled_interfaces, list)


class TestHardwareKeyDestroyer(unittest.TestCase):
    """Test HardwareKeyDestroyer"""

    def setUp(self):
        self.destroyer = HardwareKeyDestroyer()

    def test_initialization(self):
        """Test destroyer initialization"""
        self.assertIsNotNone(self.destroyer)
        self.assertIsInstance(self.destroyer._destroyed_keys, set)

    def test_destroy_tpm_keys(self):
        """Test TPM key destruction"""
        # Mock TPM interface
        mock_tpm = Mock()
        mock_tpm._keys = {"key1": b"data1", "key2": b"data2"}
        mock_tpm.delete_key = Mock(return_value=True)

        result = self.destroyer.destroy_tpm_keys(mock_tpm)

        self.assertTrue(result)
        self.assertEqual(mock_tpm.delete_key.call_count, 2)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCompromiseDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestKernelInterface))
    suite.addTests(loader.loadTestsFromTestCase(TestSecretWiper))
    suite.addTests(loader.loadTestsFromTestCase(TestMemorySanitizer))
    suite.addTests(loader.loadTestsFromTestCase(TestDiskSanitizer))
    suite.addTests(loader.loadTestsFromTestCase(TestDOSTrapMode))
    suite.addTests(loader.loadTestsFromTestCase(TestCompromiseEvent))
    suite.addTests(loader.loadTestsFromTestCase(TestInterfaceDisabler))
    suite.addTests(loader.loadTestsFromTestCase(TestHardwareKeyDestroyer))
    suite.addTests(loader.loadTestsFromTestCase(TestNoHardcodedSecrets))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


class TestNoHardcodedSecrets(unittest.TestCase):
    """Test that no hardcoded secrets remain in examples or source code"""

    def test_no_hardcoded_secrets_in_dos_trap_demo(self):
        """Verify no hardcoded secrets in dos_trap_demo.py"""
        import os

        demo_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "examples", "dos_trap_demo.py"
        )

        with open(demo_file, "r") as f:
            content = f.read()

        # Check for specific hardcoded values that were removed
        forbidden_patterns = [
            b"secret_key_data_12345678",
            b"signing_key_data_87654321",
            b"root_key_data_abcdefgh",
            b"session_key_1",
            b"session_key_2",
            "super_secret_password",
            "api_token_xyz123",
        ]

        for pattern in forbidden_patterns:
            pattern_str = pattern.decode() if isinstance(pattern, bytes) else pattern
            self.assertNotIn(
                pattern_str, content, f"Found hardcoded secret pattern: {pattern_str}"
            )

    def test_demo_uses_secure_generation(self):
        """Verify demo uses secure secret generation"""
        import os

        demo_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "examples", "dos_trap_demo.py"
        )

        with open(demo_file, "r") as f:
            content = f.read()

        # Check that secure patterns are used
        self.assertIn(
            "import secrets",
            content,
            "Demo should import secrets module for secure generation",
        )
        self.assertIn(
            "secrets.token_bytes",
            content,
            "Demo should use secrets.token_bytes for secure random generation",
        )
        self.assertIn(
            "os.environ.get",
            content,
            "Demo should check environment variables for secrets",
        )

    def test_security_documentation_exists(self):
        """Verify security documentation exists"""
        import os

        repo_root = os.path.dirname(os.path.dirname(__file__))

        security_md = os.path.join(repo_root, "SECURITY.md")
        self.assertTrue(
            os.path.exists(security_md), "SECURITY.md documentation must exist"
        )

        env_example = os.path.join(repo_root, ".env.example")
        self.assertTrue(os.path.exists(env_example), ".env.example template must exist")

    def test_gitignore_blocks_secrets(self):
        """Verify .gitignore blocks secret files"""
        import os

        gitignore_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), ".gitignore"
        )

        with open(gitignore_file, "r") as f:
            content = f.read()

        # Check that .env files are ignored
        self.assertIn(".env", content, ".gitignore must block .env files")


if __name__ == "__main__":
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
