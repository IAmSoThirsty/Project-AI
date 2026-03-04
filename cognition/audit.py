#                                           [2026-03-03 13:45]
#                                          Productivity: Active
from datetime import datetime

AUDIT_LOG = __file__.replace("audit.py", "governance_audit.log")


def audit(event: str, detail=None):
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {event} | {detail}\n")
