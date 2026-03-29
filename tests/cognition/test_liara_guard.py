# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_liara_guard.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



import unittest
from cognition.liara_guard import STATE, authorize_liara, revoke_liara

class TestLiaraGuard(unittest.TestCase):
    def setUp(self):
        revoke_liara("reset")

    def test_authorization(self):
        self.assertTrue(authorize_liara("test", ttl_seconds=10))
        self.assertEqual(STATE.active_role, "test")

if __name__ == "__main__":
    unittest.main()
