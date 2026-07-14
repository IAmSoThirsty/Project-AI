"""Project-AI Memory: CCMA unified constitutional memory graph.

This package is the entire memory substrate for Project-AI — past, present, and
future memory — implemented as the Constitutional Cognitive Memory Architecture
(CCMA) "one graph" (``memory.ccma``): a single nodes/edges store, the Fates
(Clotho/Lachesis/Atropos) lifecycle, and the 12-stage constitutional pipeline.

CCMA's fail-closed seams are wired here to the *real* Beginnings subsystems
(``memory.bridges``): authority -> ``StateRegister``, capability -> T.A.R.L.,
audit -> the CBCC-equivalent hash chain, retrieval -> ``knowledge.VectorIndex``,
and constitutional review -> ``TriumvirateGovernor``.

Public surface
--------------
* ``MemorySystem`` — the runtime facade that bundles the graph store, the Fates,
  and the four real bridges. Construct via :func:`get_memory_system`.
* CCMA core types re-exported for direct use: ``GraphStore``, ``UniversalNode``,
  ``Edge``, ``Region``/``LifecycleState``/``RelationshipType`` enums, the Fates
  (``Clotho``/``Lachesis``/``Atropos``), the ``Pipeline`` and its stage result
  types, and the fail-closed ``SafeHaltError`` / ABC interfaces.
* ``bridges`` — the real-subsystem adapters (see ``memory.bridges``).
"""

from __future__ import annotations

from audit.chain import AuditLog

from kernel import StateRegister
from memory.bridges import (
    CBCCAuditSigner,
    KnowledgeRetriever,
    StateRegisterAuthorityProvider,
    TARLCapabilityChecker,
    TriumvirateReviewBridge,
)
from memory.ccma import (
    Atropos,
    Clotho,
    Lachesis,
    LachesisWeights,
    SafeHaltError,
)
from memory.ccma.interfaces import (
    AuditSigner,
    AuthorityProvider,
    AuthorityToken,
    CapabilityChecker,
    DenyByDefaultAuditSigner,
    DenyByDefaultAuthorityProvider,
    DenyByDefaultCapabilityChecker,
    Signature,
)
from memory.ccma.models import (
    PAYLOAD_SCHEMAS,
    Edge,
    LifecycleState,
    NodeType,
    Region,
    RelationshipType,
    UniversalNode,
    validate_payload,
)
from memory.ccma.pipeline import (
    AuditRecord,
    CompiledProposal,
    ExecutionResult,
    GovernanceAuthorization,
    Observation,
    Proposition,
    RetrievalBundle,
    TriumvirateRuling,
    WorkingMemoryContext,
)
from memory.ccma.store import GraphStore


class MemorySystem:
    """The unified memory substrate: one graph + the Fates + real bridges.

    This is "the entire memory + future memory" for Project-AI. It owns the
    CCMA ``GraphStore`` (the single living graph), exposes the Fates for
    lifecycle mutation, and wires CCMA's authority/capability/audit seams to the
    genuine Beginnings subsystems. Retrieval is delegated to a
    ``KnowledgeRetriever`` over the real ``knowledge.VectorIndex``.

    Construction is explicit: callers pass the ``StateRegister`` (authority),
    a ``CapabilityAuthority`` (T.A.R.L.), an ``AuditLog`` (CBCC chain), and a
    ``VectorIndex`` (semantic retrieval). Until those are provided the system
    stays fail-closed — ``GraphStore`` operations still run, but authority /
    capability / audit / triumvirate checks halt unless real bridges are wired.
    """

    def __init__(
        self,
        *,
        db_path: str = ":memory:",
        register: StateRegister | None = None,
        capability_authority: object | None = None,
        audit_log: AuditLog | None = None,
        vector_index: object | None = None,
    ) -> None:
        self._store = GraphStore(db_path)
        self._register = register
        self._capability_authority = capability_authority
        self._audit_log = audit_log
        self._vector_index = vector_index

        # Fates operate directly on the store (Clotho=create, Lachesis=measure,
        # Atropos=resolve). Atropos needs an AuthorityProvider for protected
        # node resolution; wire the real StateRegister-backed provider if given.
        self._authority: AuthorityProvider = (
            StateRegisterAuthorityProvider(register)
            if register is not None
            else DenyByDefaultAuthorityProvider()
        )
        self._capability: CapabilityChecker = (
            TARLCapabilityChecker(capability_authority)  # type: ignore[arg-type]
            if capability_authority is not None
            else DenyByDefaultCapabilityChecker()
        )
        self._auditor: AuditSigner = (
            CBCCAuditSigner(audit_log) if audit_log is not None else DenyByDefaultAuditSigner()
        )
        self._clotho = Clotho(self._store)
        self._lachesis = Lachesis(self._store)
        self._atropos = Atropos(self._store, self._authority)

    # -- Graph store + Fates (the living memory) ----------------------------

    @property
    def store(self) -> GraphStore:
        return self._store

    @property
    def clotho(self) -> Clotho:
        return self._clotho

    @property
    def lachesis(self) -> Lachesis:
        return self._lachesis

    @property
    def atropos(self) -> Atropos:
        return self._atropos

    @property
    def authority(self) -> AuthorityProvider:
        return self._authority

    @property
    def capability(self) -> CapabilityChecker:
        return self._capability

    @property
    def auditor(self) -> AuditSigner:
        return self._auditor

    # -- Retrieval (delegated to the real knowledge vector index) ----------

    def retriever(self) -> KnowledgeRetriever | None:
        """Return a ``KnowledgeRetriever`` over the configured vector index, or None."""
        if self._vector_index is None:
            return None
        return KnowledgeRetriever(self._vector_index)  # type: ignore[arg-type]

    def verify_audit_chain(self) -> bool:
        """Return True iff the CBCC hash chain is intact (only if a log is wired)."""
        if self._audit_log is None:
            return False
        return self._audit_log.verify_chain().valid


def get_memory_system(
    *,
    db_path: str = ":memory:",
    register: StateRegister | None = None,
    capability_authority: object | None = None,
    audit_log: AuditLog | None = None,
    vector_index: object | None = None,
) -> MemorySystem:
    """Construct a fully-wired :class:`MemorySystem` (the repo's singleton convention)."""
    return MemorySystem(
        db_path=db_path,
        register=register,
        capability_authority=capability_authority,
        audit_log=audit_log,
        vector_index=vector_index,
    )


__version__ = "0.0.0.dev0"

__all__ = [
    "PAYLOAD_SCHEMAS",
    "Atropos",
    "AuditRecord",
    "AuditSigner",
    "AuthorityProvider",
    "AuthorityToken",
    "CBCCAuditSigner",
    "CapabilityChecker",
    "Clotho",
    "CompiledProposal",
    "DenyByDefaultAuditSigner",
    "DenyByDefaultAuthorityProvider",
    "DenyByDefaultCapabilityChecker",
    "Edge",
    "ExecutionResult",
    "GovernanceAuthorization",
    "GraphStore",
    "KnowledgeRetriever",
    "Lachesis",
    "LachesisWeights",
    "LifecycleState",
    "MemorySystem",
    "NodeType",
    "Observation",
    "Proposition",
    "Region",
    "RelationshipType",
    "RetrievalBundle",
    "SafeHaltError",
    "Signature",
    "StateRegisterAuthorityProvider",
    "TARLCapabilityChecker",
    "TriumvirateReviewBridge",
    "TriumvirateRuling",
    "UniversalNode",
    "WorkingMemoryContext",
    "get_memory_system",
    "validate_payload",
]
