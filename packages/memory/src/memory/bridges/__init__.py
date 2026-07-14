"""Memory subsystem bridges: CCMA interfaces wired to real Beginnings subsystems.

Each module here implements one of CCMA's fail-closed ABC seams
(``AuthorityProvider`` / ``CapabilityChecker`` / ``AuditSigner``) or adapts a
real subsystem into a CCMA stage callable (``triumvirate_review`` / retrieval).

Nothing in ``bridges/`` fabricates authority, capability, or signatures — every
bridge delegates to the genuine Beginnings implementation:

* ``authority``   -> ``kernel.StateRegister``       (Law I authority source of truth)
* ``capability``  -> ``capability.CapabilityAuthority`` (T.A.R.L. HMAC tokens)
* ``audit``       -> ``audit.AuditLog``             (CBCC hash-linked chain)
* ``retrieval``   -> ``knowledge.VectorIndex``      (semantic/vector retrieval)
* ``triumvirate`` -> ``governance.TriumvirateGovernor`` (real constitutional review)
"""

from memory.bridges.audit import CBCCAuditSigner
from memory.bridges.authority import StateRegisterAuthorityProvider
from memory.bridges.capability import TARLCapabilityChecker
from memory.bridges.retrieval import (
    KnowledgeRetriever,
    build_query_from_context,
    node_to_text,
)
from memory.bridges.triumvirate import (
    TriumvirateReviewBridge,
    build_triumvirate,
    fail_closed_ruling,
)

__all__ = [
    "CBCCAuditSigner",
    "KnowledgeRetriever",
    "StateRegisterAuthorityProvider",
    "TARLCapabilityChecker",
    "TriumvirateReviewBridge",
    "build_query_from_context",
    "build_triumvirate",
    "fail_closed_ruling",
    "node_to_text",
]
