import logging
import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from src.app.governance.acceptance_ledger import AcceptanceType, get_acceptance_ledger
from src.app.governance.runtime_enforcer import (
    EnforcementContext,
    TierLevel,
    get_runtime_enforcer,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sra_verify")

def verify_sra():
    logger.info("Starting SRA Verification...")

    # Pre-step: Accept MSA for 'verifier'
    ledger = get_acceptance_ledger()
    try:
        ledger.append_acceptance(
            user_id="verifier",
            user_email="verifier@project-ai.internal",
            acceptance_type=AcceptanceType.INITIAL_MSA,
            tier=TierLevel.SOLO,
            jurisdiction="Geneva-Sovereign-Zone",
            document_hash="da39a3ee5e6b4b0d3255bfef95601890afd80709" # Empty hash for test
        )
        logger.info("Ledger acceptance recorded for 'verifier'.")
    except Exception as e:
        logger.warning("Could not record acceptance (maybe crypto is missing): %s", e)
        # Continuing anyway, enforcer might be in dev mode or we'll see if it fails.

    enforcer = get_runtime_enforcer()

    # Mock ledger to bypass crypto requirement for 'verifier'
    ledger = get_acceptance_ledger()

    class MockEntry:
        def __init__(self, acceptance_type, tier):
            self.acceptance_type = acceptance_type
            self.tier = tier
            self.metadata = {"government_authorized": True}
            self.timestamp = 0

    def mock_get_user_acceptances(uid):
        if uid == "verifier":
            return [MockEntry(AcceptanceType.INITIAL_MSA, TierLevel.SOLO)]
        return []

    ledger.get_user_acceptances = mock_get_user_acceptances
    logger.info("Mocked ledger get_user_acceptances for 'verifier'.")
    logger.info("Test 1: Standard Action (ALLOW expected)")
    context = EnforcementContext(
        user_id="verifier",
        action="read_doc",
        is_commercial=False,
        tier_required=TierLevel.SOLO
    )
    result = enforcer.enforce(context)
    logger.info("Result: %s, Reason: %s", result.verdict, result.reason)

    # 2. Test SRA Repair (DIRECTNESS_CORRUPTION)
    logger.info("Test 2: SRA Repair (DIRECTNESS_CORRUPTION)")
    context_repair = EnforcementContext(
        user_id="verifier",
        action="generate_response",
        metadata={"violation_kind": "DIRECTNESS_CORRUPTION", "pid": 1234}
    )
    result_repair = enforcer.enforce(context_repair)
    logger.info("Result: %s, Reason: %s", result_repair.verdict, result_repair.reason)

    # 3. Test SAFE-HALT (CONTROL_FLOW_INTEGRITY_BREACH - null entry)
    logger.info("Test 3: SAFE-HALT (CONTROL_FLOW_INTEGRITY_BREACH)")
    context_halt = EnforcementContext(
        user_id="verifier",
        action="critical_sys_call",
        metadata={"violation_kind": "CONTROL_FLOW_INTEGRITY_BREACH"}
    )
    result_halt = enforcer.enforce(context_halt)
    logger.info("Result: %s, Reason: %s", result_halt.verdict, result_halt.reason)

if __name__ == "__main__":
    verify_sra()
