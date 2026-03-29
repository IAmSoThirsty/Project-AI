# ============================================================================ #
#                                           [2026-03-21 21:58]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-21 | TIME: 21:58             #
# COMPLIANCE: Sovereign Substrate / test_graduation_governance.py
# ============================================================================ #

import unittest
import datetime
try:
    UTC = datetime.UTC
except AttributeError:
    UTC = datetime.timezone.utc
from datetime import datetime

from src.app.core.cognition_kernel import (
    Action,
    CognitionKernel,
    ExecutionContext,
    ExecutionType,
)


class TestGraduationGovernance(unittest.TestCase):
    def setUp(self):
        self.kernel = CognitionKernel()

    def test_bayesian_governance_flow(self):
        """Test that the kernel uses SPFE and UTF Bridge for decisions."""
        action = Action(
            action_id="test_act",
            action_name="system_reconfig",
            action_type=ExecutionType.SYSTEM_OPERATION,
            callable=lambda: "done",
            risk_level="low"
        )

        context = ExecutionContext(
            trace_id="test_trace",
            timestamp=datetime.now(UTC),
            perception={},
            interpretation={},
            proposed_action=action,
            source="test"
        )

        # Identity snapshot mock
        identity_snapshot = {"self_awareness_score": 0.85}

        decision = self.kernel._check_governance(action, context, identity_snapshot)

        print(f"Decision Reason: {decision.reason}")
        print(f"Decision Approved: {decision.approved}")
        print(f"Council Votes (Forecast): {decision.council_votes}")

        # Verify bridge was called (via decision reason prefix)
        self.assertTrue(decision.reason.startswith("Sovereign Master:"))
        # Verify forecast was included
        self.assertIn("forecast", decision.council_votes)
        self.assertEqual(decision.council_votes["forecast"]["predicted_campaign"], "BGP-DNS-poison")

if __name__ == "__main__":
    unittest.main()
