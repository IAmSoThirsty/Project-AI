# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_consigliere.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_consigliere.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Comprehensive Consigliere Testing Suite
Tests for privacy-first AI assistant following Code of Omertà
"""

import unittest
import time
from unittest.mock import Mock, patch
from cryptography.fernet import Fernet

from thirstys_waterfall.consigliere import (
    ThirstyConsigliere,
    CapabilityManager,
    ActionLedger,
    PrivacyChecker,
)
from thirstys_waterfall.utils.Enterprise_Tier_encryption import GodTierEncryption


class TestCapabilityManager(unittest.TestCase):
    """Test capability management and permission system"""

    def setUp(self):
        """Setup test fixtures"""
        self.cipher = Fernet(Fernet.generate_key())
        self.cap_manager = CapabilityManager(self.cipher)

    def test_capability_manager_initialization(self):
        """Test capability manager initializes with defined capabilities"""
        self.assertGreater(len(self.cap_manager.capabilities), 0)

        # Verify key capabilities exist
        self.assertIn("page_content", self.cap_manager.capabilities)
        self.assertIn("browsing_history", self.cap_manager.capabilities)
        self.assertIn("filesystem", self.cap_manager.capabilities)

    def test_capability_risk_levels(self):
        """Test capabilities have appropriate risk levels"""
        # High risk capabilities
        high_risk = self.cap_manager.get_capability_info("browsing_history")
        self.assertEqual(high_risk["risk_level"], "high")

        # Low risk capabilities
        low_risk = self.cap_manager.get_capability_info("search")
        self.assertEqual(low_risk["risk_level"], "low")

    def test_low_risk_capability_auto_granted(self):
        """Test low-risk capabilities are auto-granted"""
        result = self.cap_manager.request_permission(
            "search", "Need to search for user"
        )
        self.assertTrue(result)

    def test_high_risk_capability_denied(self):
        """Test high-risk capabilities require explicit approval"""
        result = self.cap_manager.request_permission("filesystem", "Need file access")
        self.assertFalse(result)

    def test_unknown_capability_rejected(self):
        """Test unknown capabilities are rejected"""
        result = self.cap_manager.request_permission("invalid_capability", "Test")
        self.assertFalse(result)

    def test_permission_requests_logged(self):
        """Test all permission requests are logged"""
        self.cap_manager.request_permission("search", "Searching for info")
        self.cap_manager.request_permission("bookmarks", "Accessing bookmarks")

        self.assertEqual(len(self.cap_manager._permission_requests), 2)

        # Verify request structure
        request = self.cap_manager._permission_requests[0]
        self.assertIn("capability", request)
        self.assertIn("reason", request)
        self.assertIn("risk_level", request)
        self.assertIn("timestamp", request)


class TestActionLedger(unittest.TestCase):
    """Test action ledger and audit trail"""

    def setUp(self):
        """Setup test fixtures"""
        self.cipher = Fernet(Fernet.generate_key())
        self.ledger = ActionLedger(self.cipher, max_entries=5)

    def test_action_ledger_initialization(self):
        """Test ledger initializes empty"""
        self.assertEqual(len(self.ledger._entries), 0)
        self.assertEqual(self.ledger._entry_counter, 0)

    def test_add_entry_to_ledger(self):
        """Test adding entries to ledger"""
        self.ledger.add_entry(
            "search_performed", {"query": "test query", "encrypted": True}
        )

        entries = self.ledger.get_entries()
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry["action"], "search_performed")
        self.assertIn("details", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("id", entry)

    def test_ledger_max_entries_enforced(self):
        """Test ledger respects max entries limit"""
        # Add more than max_entries
        for i in range(10):
            self.ledger.add_entry(f"action_{i}", {"data": i})

        entries = self.ledger.get_entries()
        self.assertEqual(len(entries), 5)  # max_entries = 5

    def test_redact_entry(self):
        """Test entry redaction"""
        self.ledger.add_entry("sensitive_action", {"sensitive": "data"})

        entries = self.ledger.get_entries()
        entry_id = entries[0]["id"]

        self.ledger.redact_entry(entry_id)

        # Non-redacted view should not show redacted entry
        entries_clean = self.ledger.get_entries(include_redacted=False)
        self.assertEqual(len(entries_clean), 0)

        # Redacted view should show it as redacted
        entries_all = self.ledger.get_entries(include_redacted=True)
        self.assertEqual(len(entries_all), 1)
        self.assertTrue(entries_all[0]["redacted"])

    def test_one_click_deletion(self):
        """Test one-click deletion clears all entries"""
        self.ledger.add_entry("action1", {})
        self.ledger.add_entry("action2", {})
        self.ledger.add_entry("action3", {})

        self.assertEqual(len(self.ledger.get_entries()), 3)

        self.ledger.clear()

        self.assertEqual(len(self.ledger.get_entries()), 0)
        self.assertEqual(self.ledger._entry_counter, 0)


class TestPrivacyChecker(unittest.TestCase):
    """Test privacy auditing and leak detection"""

    def setUp(self):
        """Setup test fixtures"""
        self.checker = PrivacyChecker()

    def test_privacy_checker_initialization(self):
        """Test privacy checker has sensitive patterns"""
        self.assertGreater(len(self.checker.sensitive_patterns), 0)
        self.assertIn("email", self.checker.sensitive_patterns)
        self.assertIn("phone", self.checker.sensitive_patterns)
        self.assertIn("ssn", self.checker.sensitive_patterns)

    def test_safe_query_passes_audit(self):
        """Test safe queries pass privacy audit"""
        result = self.checker.audit_query("What is the weather today?")

        self.assertTrue(result["safe"])
        self.assertEqual(len(result["concerns"]), 0)
        self.assertEqual(len(result["suggestions"]), 0)

    def test_email_detected_in_query(self):
        """Test email addresses are detected"""
        result = self.checker.audit_query("Send email to user@example.com")

        self.assertFalse(result["safe"])
        self.assertIn("Query contains email", result["concerns"])

    def test_phone_number_detected(self):
        """Test phone numbers are detected"""
        result = self.checker.audit_query("Call me at 555-123-4567")

        self.assertFalse(result["safe"])
        self.assertIn("Query contains phone", result["concerns"])

    def test_ip_address_detected(self):
        """Test IP addresses are detected"""
        result = self.checker.audit_query("Connect to 192.168.1.1")

        self.assertFalse(result["safe"])
        self.assertIn("Query contains ip_address", result["concerns"])

    def test_multiple_sensitive_items_detected(self):
        """Test multiple sensitive items are all detected"""
        query = "Email admin@example.com at 555-1234 from 192.168.1.1"
        result = self.checker.audit_query(query)

        self.assertFalse(result["safe"])
        self.assertGreaterEqual(len(result["concerns"]), 2)

    def test_suggestions_provided_for_unsafe_queries(self):
        """Test suggestions are provided when query is unsafe"""
        result = self.checker.audit_query("Email me@example.com")

        self.assertFalse(result["safe"])
        self.assertGreater(len(result["suggestions"]), 0)


class TestThirstyConsigliere(unittest.TestCase):
    """Test main Consigliere engine"""

    def setUp(self):
        """Setup test fixtures"""
        self.config = {
            "on_device_inference": True,
            "no_training": True,
            "data_minimization": True,
            "zero_accept_all": True,
            "full_transparency": True,
        }
        self.Enterprise_Tier = GodTierEncryption()
        self.consigliere = ThirstyConsigliere(self.config, self.Enterprise_Tier)

    def tearDown(self):
        """Cleanup"""
        if self.consigliere._active:
            self.consigliere.stop()

    def test_consigliere_initialization(self):
        """Test Consigliere initializes with locked-down state"""
        self.assertFalse(self.consigliere._active)
        self.assertIsNotNone(self.consigliere.capability_manager)
        self.assertIsNotNone(self.consigliere.action_ledger)
        self.assertIsNotNone(self.consigliere._privacy_checker)

    def test_consigliere_start_stop(self):
        """Test Consigliere start and stop"""
        self.consigliere.start()
        self.assertTrue(self.consigliere._active)

        self.consigliere.stop()
        self.assertFalse(self.consigliere._active)
        # Ephemeral context should be cleared
        self.assertEqual(len(self.consigliere._ephemeral_context), 0)

    def test_locked_down_initialization(self):
        """Test everything starts locked down (zero accept all)"""
        # All capabilities should start disabled
        status = self.consigliere.get_status()
        self.assertTrue(status["code_of_omerta"]["zero_accept_all"])

    def test_capability_request_flow(self):
        """Test capability request workflow"""
        self.consigliere.start()

        # Request low-risk capability
        granted = self.consigliere.request_capability(
            "search", "Need to search for information"
        )
        self.assertTrue(granted)

    def test_data_minimization_applied(self):
        """Test data minimization is applied to context"""
        self.consigliere.start()

        context = {
            "url": "https://example.com/very/long/path?param1=value1&param2=value2",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "timestamp": time.time(),
            "page_title": "Example Page",
        }

        minimized = self.consigliere._minimize_data(context)

        # URL should be reduced to just domain
        self.assertIn("domain", minimized)
        self.assertEqual(minimized["domain"], "example.com")

        # User agent should be removed
        self.assertNotIn("user_agent", minimized)

    def test_on_device_inference_only(self):
        """Test all processing happens on-device"""
        self.consigliere.start()

        query = "What is the weather?"
        response = self.consigliere.assist(query)

        # Should indicate on-device processing
        self.assertIn("on_device", response)
        self.assertTrue(response["on_device"])

        # Should never make external API calls
        self.assertNotIn("external_api_used", response)

    def test_no_training_on_user_data(self):
        """Test no training happens on user data"""
        status = self.consigliere.get_status()

        self.assertTrue(status["code_of_omerta"]["no_training"])

    def test_ephemeral_context_window(self):
        """Test context is ephemeral (memory only)"""
        self.consigliere.start()

        # Add to context
        self.consigliere._add_to_context({"query": "test", "timestamp": time.time()})

        # Context should be in memory
        self.assertEqual(len(self.consigliere._ephemeral_context), 1)

        # Stop should clear context
        self.consigliere.stop()
        self.assertEqual(len(self.consigliere._ephemeral_context), 0)

    def test_action_ledger_integration(self):
        """Test action ledger tracks all actions"""
        self.consigliere.start()

        self.consigliere.assist("Test query")

        # Action should be logged
        entries = self.consigliere.action_ledger.get_entries()
        self.assertGreater(len(entries), 0)

    def test_privacy_audit_before_processing(self):
        """Test privacy audit runs before processing"""
        self.consigliere.start()

        # Safe query should process normally
        response = self.consigliere.assist("What is 2+2?")
        self.assertIn("response", response)

        # Unsafe query should be flagged
        unsafe_response = self.consigliere.assist("Email admin@example.com")
        self.assertIn("privacy_concerns", unsafe_response)

    def test_Enterprise_Tier_encryption_applied(self):
        """Test Enterprise Tier encryption is applied to all data"""
        self.consigliere.start()

        response = self.consigliere.assist("Test query")

        # Response should indicate encryption
        self.assertIn("encrypted", response)
        self.assertTrue(response["encrypted"])

    def test_transparency_in_responses(self):
        """Test responses include transparency about data used"""
        self.consigliere.start()

        response = self.consigliere.assist("Test query")

        # Should show what data was used
        self.assertIn("data_used", response)
        self.assertIn("capabilities_used", response)

    def test_wipe_everything_hard_delete(self):
        """Test wipe everything performs hard delete"""
        self.consigliere.start()

        # Add some data
        self.consigliere.assist("Query 1")
        self.consigliere.assist("Query 2")

        # Wipe everything
        self.consigliere.wipe_everything()

        # All data should be gone
        self.assertEqual(len(self.consigliere._ephemeral_context), 0)
        self.assertEqual(len(self.consigliere.action_ledger.get_entries()), 0)

    def test_status_reflects_code_of_omerta(self):
        """Test status shows Code of Omertà compliance"""
        status = self.consigliere.get_status()

        # code_of_omerta is in 'principles' dict
        self.assertIn("principles", status)
        principles = status["principles"]
        self.assertIn("code_of_omerta", principles)
        self.assertTrue(principles["code_of_omerta"])

        # Verify other code of omertà principles
        self.assertTrue(status["data_minimization"])
        self.assertTrue(status["on_device_only"])


class TestConsigliereIntegration(unittest.TestCase):
    """Integration tests for complete Consigliere workflow"""

    def setUp(self):
        """Setup test fixtures"""
        self.config = {"on_device_inference": True, "no_training": True}
        self.Enterprise_Tier = GodTierEncryption()
        self.consigliere = ThirstyConsigliere(self.config, self.Enterprise_Tier)
        self.consigliere.start()

    def tearDown(self):
        """Cleanup"""
        if self.consigliere._active:
            self.consigliere.stop()

    def test_full_query_workflow(self):
        """Test complete query workflow from request to response"""
        # Request capability
        granted = self.consigliere.request_capability("search", "Testing workflow")
        self.assertTrue(granted)

        # Perform query
        response = self.consigliere.assist("What is privacy?")

        # Verify response structure
        self.assertIn("response", response)
        self.assertIn("encrypted", response)
        self.assertIn("on_device", response)
        self.assertIn("data_used", response)

        # Verify action was logged
        entries = self.consigliere.action_ledger.get_entries()
        self.assertGreater(len(entries), 0)

    def test_privacy_escalation_workflow(self):
        """Test privacy concerns escalate properly"""
        # Query with sensitive data
        response = self.consigliere.assist(
            "Email me@example.com with my SSN 123-45-6789"
        )

        # Should have privacy concerns
        self.assertIn("privacy_concerns", response)
        concerns = response["privacy_concerns"]

        self.assertGreater(len(concerns["concerns"]), 0)
        self.assertGreater(len(concerns["suggestions"]), 0)


if __name__ == "__main__":
    unittest.main()
