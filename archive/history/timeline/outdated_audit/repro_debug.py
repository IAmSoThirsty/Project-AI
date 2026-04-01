import logging
import os
import sys
import tempfile

# Add src to sys.path
sys.path.append(os.getcwd())

from src.app.governance.sovereign_audit_log import SovereignAuditLog

logging.basicConfig(level=logging.DEBUG)

def repro():
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Using tmpdir: {tmpdir}")
        audit = SovereignAuditLog(data_dir=tmpdir)

        print("Initial initialization done.")

        try:
            success = audit.log_event(
                event_type="test_event",
                data={"key": "value"},
                actor="test_actor",
                description="Test event with signature",
            )
            print(f"Log event success: {success}")
        except Exception as e:
            print(f"Caught exception in repro: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    repro()
