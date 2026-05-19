"""
Governance subsystem for Project-AI.

This package provides tools for multi-stakeholder governance, proposal
management, voting mechanisms, and policy enforcement.

Recovered proof modules (genesis_continuity, tsa_anchor_manager, tsa_provider,
external_merkle_anchor) are importable but runtime-activation is disabled by
default. Set GOVERNANCE_ANCHORING_ENABLED = True in config to enable TSA and
Merkle anchoring at runtime.
"""

from . import genesis_continuity
from . import tsa_anchor_manager
from . import tsa_provider
from . import external_merkle_anchor

# Runtime activation flag — disabled by default.
# Callers must explicitly set this True and supply credentials before
# TSAProvider or ExternalMerkleAnchor will attempt network/filesystem writes.
GOVERNANCE_ANCHORING_ENABLED: bool = False

__all__ = [
    "governance_manager",
    "genesis_continuity",
    "tsa_anchor_manager",
    "tsa_provider",
    "external_merkle_anchor",
    "GOVERNANCE_ANCHORING_ENABLED",
]
