# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_kernel_liara.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



import unittest
from cognition.kernel_liara import maybe_activate_liara, restore_pillar

class TestKernelLiara(unittest.TestCase):
    def test_activation(self):
        status = {"pillar_alpha": False}
        activated = maybe_activate_liara(status)
        self.assertEqual(activated, "pillar_alpha")
        restore_pillar()

if __name__ == "__main__":
    unittest.main()
