# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_audit.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



import unittest
from cognition.audit import audit, AUDIT_LOG

class TestAudit(unittest.TestCase):
    def setUp(self):
        if AUDIT_LOG.exists():
            AUDIT_LOG.unlink()

    def test_audit_persistence(self):
        audit("TEST_EVENT", "Detail")
        self.assertTrue(AUDIT_LOG.exists())
        content = AUDIT_LOG.read_text(encoding="utf-8")
        self.assertIn("TEST_EVENT", content)

if __name__ == "__main__":
    unittest.main()
