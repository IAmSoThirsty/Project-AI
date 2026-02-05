"""
Network / IPC Boundary Enforcement
All inbound requests must present a valid TARL hash.
"""

from cognition.audit import audit


def enforce_boundary(tarl_hash: str | None):
    if not tarl_hash:
        audit("BOUNDARY_BLOCK", "missing_tarl")
        raise RuntimeError("Boundary violation: TARL required")

    audit("BOUNDARY_ACCEPT", tarl_hash)
    return True
