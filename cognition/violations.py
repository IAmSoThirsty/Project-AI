#                                           [2026-03-05 08:49]
#                                          Productivity: Active
from cognition.audit import audit


def attempted_violation(kind: str, detail=None):
    audit("ATTEMPTED_VIOLATION", {"kind": kind, "detail": detail})
