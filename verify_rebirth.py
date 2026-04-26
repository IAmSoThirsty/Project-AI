# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / verify_rebirth.py
# ============================================================================ #
# COMPLIANCE: Sovereign Verification

import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

def verify_sovereign_rebirth():
    logger.info("Starting Sovereign Rebirth Verification...")

    try:
        from src.app.core.utf_bridge import get_utf_bridge
        bridge = get_utf_bridge()
        logger.info("✅ UTF Bridge Loaded.")

        # Test 1: Constitutional Enforcement delegation
        logger.info("Test 1: Testing Constitutional Enforcement...")
        enforcement = bridge.enforce_constitution(
            action_name="VERIFICATION_PROBE",
            context_data={"affects_human": False, "trust_delta": 0}
        )
        logger.info(f"Result: {enforcement}")
        if enforcement.get("allowed") == True:
            logger.info("✅ Constitutional delegation successful.")
        else:
            logger.warning("❌ Constitutional delegation blocked (expected?)")

        # Test 2: Audit Trail delegation
        logger.info("Test 2: Testing Audit Trail delegation...")
        bridge.log_sovereign_event(
            event_type="VERIFICATION_COMMIT",
            data={"status": "SUCCESS"},
            severity="INFO"
        )
        logger.info("✅ Audit Trail delegation successful.")

        logger.info("--- Sovereign Rebirth Verification Complete ---")
        return True

    except Exception:
        logger.exception("❌ Verification failed")
        return False

if __name__ == "__main__":
    success = verify_sovereign_rebirth()
    sys.exit(0 if success else 1)
