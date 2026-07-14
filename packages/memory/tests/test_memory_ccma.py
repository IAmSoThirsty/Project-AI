"""CCMA constitutional-law tests for Project-AI Memory.

These prove the unified graph still enforces CCMA's constitutional rules after
integration (Law I provenance, payload schema validation, deny-by-default
authority/capability/audit, protected-memory gating, Fates lifecycle, and
pipeline type-gating). They are the integration's regression guard.
"""

from __future__ import annotations

import time

import pytest
from audit.chain import AuditLog
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
from memory.ccma.models import Edge, RelationshipType
from memory.ccma.pipeline import (
    CompiledProposal,
    ExecutionResult,
    GovernanceAuthorization,
    Pipeline,
    Proposition,
    RetrievalBundle,
    TriumvirateRuling,
)

from kernel import StateRegister
from memory import (
    Atropos,
    CBCCAuditSigner,
    Clotho,
    GraphStore,
    Lachesis,
    LachesisWeights,
    LifecycleState,
    Region,
    SafeHaltError,
    StateRegisterAuthorityProvider,
    UniversalNode,
)

# --------------------------------------------------------------------------
# Law I — Nothing Exists Without Provenance
# --------------------------------------------------------------------------


def test_law1_node_without_origin_is_rejected() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="companion.trust_memory", region=Region.COMPANION, origin="", creator="thirsty"
    )
    with pytest.raises(SafeHaltError):
        store.create_node(node)


def test_law1_node_without_creator_is_rejected() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="companion.trust_memory",
        region=Region.COMPANION,
        origin="companion_v1",
        creator="",
    )
    with pytest.raises(SafeHaltError):
        store.create_node(node)


def test_valid_node_is_created_born_and_zero_weight() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="companion.trust_memory",
        region=Region.COMPANION,
        origin="companion_v1",
        creator="thirsty",
    )
    node_id = store.create_node(node)
    fetched = store.get_node(node_id)
    assert fetched is not None
    assert fetched.lifecycle_state == LifecycleState.BORN
    assert fetched.retrieval_weight == 0.0


# --------------------------------------------------------------------------
# Payload schema validation
# --------------------------------------------------------------------------


def test_registered_schema_rejects_unknown_fields() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="governance.authority_memory",
        region=Region.GOVERNANCE,
        origin="tarl",
        creator="system",
        payload={"authority_source": "state_register", "made_up_field": 1},
    )
    with pytest.raises(ValueError):
        store.create_node(node)


def test_unregistered_type_accepts_any_payload() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="companion.some_new_domain_i_havent_registered_yet",
        region=Region.COMPANION,
        origin="companion_v1",
        creator="thirsty",
        payload={"anything": "goes"},
    )
    store.create_node(node)  # must not raise


# --------------------------------------------------------------------------
# Deny-by-default authority / capability / audit (fail closed)
# --------------------------------------------------------------------------


def test_deny_by_default_authority_provider_halts() -> None:
    provider = DenyByDefaultAuthorityProvider()
    with pytest.raises(SafeHaltError):
        provider.check_authority(subject="thirsty", scope="execute:anything")


def test_deny_by_default_capability_checker_halts() -> None:
    checker = DenyByDefaultCapabilityChecker()
    with pytest.raises(SafeHaltError):
        checker.check_capability(subject="thirsty", capability="deploy")


def test_deny_by_default_audit_signer_halts() -> None:
    signer = DenyByDefaultAuditSigner()
    with pytest.raises(SafeHaltError):
        signer.sign(b"payload")


# --------------------------------------------------------------------------
# Protected memory (Atropos) requires protected_override authority
# --------------------------------------------------------------------------


class _GrantingProvider(AuthorityProvider):
    def __init__(self, protected_override: bool = False, valid: bool = True) -> None:
        self._override = protected_override
        self._valid = valid

    def check_authority(self, subject: str, scope: str) -> AuthorityToken:
        return AuthorityToken(
            subject=subject,
            scope=scope,
            granted_by="test",
            granted_at=time.time(),
            expires_at=(time.time() - 1) if not self._valid else None,
            protected_override=self._override,
        )


def test_protected_node_cannot_be_forgotten_without_override() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="audit.evidence_memory", region=Region.AUDIT, origin="pipeline", creator="thirsty"
    )
    node_id = store.create_node(node)
    atropos = Atropos(store, _GrantingProvider(protected_override=False))
    with pytest.raises(SafeHaltError):
        atropos.forget(node_id, subject="thirsty")


def test_protected_node_can_be_forgotten_with_override() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="audit.evidence_memory", region=Region.AUDIT, origin="pipeline", creator="thirsty"
    )
    node_id = store.create_node(node)
    atropos = Atropos(store, _GrantingProvider(protected_override=True))
    atropos.forget(node_id, subject="thirsty")
    fetched = store.get_node(node_id)
    assert fetched is not None
    assert fetched.lifecycle_state == LifecycleState.FORGOTTEN


def test_unprotected_node_can_be_archived_without_override() -> None:
    store = GraphStore()
    node = UniversalNode(
        node_type="companion.curiosity_memory",
        region=Region.COMPANION,
        origin="companion_v1",
        creator="thirsty",
    )
    node_id = store.create_node(node)
    atropos = Atropos(store, _GrantingProvider(protected_override=False))
    atropos.archive(node_id, subject="thirsty")
    fetched = store.get_node(node_id)
    assert fetched is not None
    assert fetched.lifecycle_state == LifecycleState.ARCHIVED


# --------------------------------------------------------------------------
# Fates: Clotho -> Lachesis flow, relationship density feeds weight
# --------------------------------------------------------------------------


def test_lachesis_weight_increases_with_relationship_density() -> None:
    store = GraphStore()
    clotho = Clotho(store)
    lachesis = Lachesis(store)
    hub = clotho.spin("taar.pattern_memory", Region.TAAR, "taar", "system")
    isolated = clotho.spin("taar.pattern_memory", Region.TAAR, "taar", "system")
    for _ in range(10):
        leaf = clotho.spin("taar.pattern_memory", Region.TAAR, "taar", "system")
        store.create_edge(
            Edge(
                src_id=hub.node_id, dst_id=leaf.node_id, relationship_type=RelationshipType.SUPPORTS
            )
        )
    w_hub = lachesis.measure(hub.node_id, LachesisWeights(relevance=0.5))
    w_isolated = lachesis.measure(isolated.node_id, LachesisWeights(relevance=0.5))
    assert w_hub > w_isolated
    fetched = store.get_node(hub.node_id)
    assert fetched is not None
    assert fetched.lifecycle_state == LifecycleState.ACTIVE


# --------------------------------------------------------------------------
# Pipeline: stages cannot be skipped or called out of order (type gating)
# --------------------------------------------------------------------------


class _Capability(CapabilityChecker):
    def check_capability(self, subject: str, capability: str) -> bool:
        return True


class _Auditor(AuditSigner):
    def sign(self, payload: bytes) -> Signature:
        return Signature(
            algorithm="test",
            signature_hex="deadbeef",
            signer_id="test-signer",
            signed_at=time.time(),
        )

    def verify(self, payload: bytes, signature: Signature) -> bool:
        return True

    def append_to_chain(self, payload: bytes, signature: Signature) -> str:
        return "chain-ref-1"


def _build_pipeline(triumvirate_allows: bool) -> Pipeline:
    store = GraphStore()
    authority = _GrantingProvider(protected_override=True)

    def companion_deliberate(bundle: RetrievalBundle) -> Proposition:
        return Proposition(
            retrieval=bundle, statement="do the thing", supporting_node_ids=[], confidence=0.9
        )

    def shadow_compile(prop: Proposition) -> CompiledProposal:
        return CompiledProposal(
            proposition=prop,
            simulation_summary="ok",
            predicted_effects=["nothing bad"],
            unsafe=False,
        )

    def triumvirate_review(compiled: CompiledProposal) -> TriumvirateRuling:
        if triumvirate_allows:
            return TriumvirateRuling(
                compiled=compiled,
                galahad_recommendation="legitimate",
                cerberus_recommendation="safe",
                codex_judgment="allow",
            )
        return TriumvirateRuling(
            compiled=compiled,
            galahad_recommendation="illegitimate",
            cerberus_recommendation="unsafe",
            codex_judgment="deny",
        )

    def execute(auth: GovernanceAuthorization) -> ExecutionResult:
        return ExecutionResult(authorization=auth, outcome="did the thing", success=True)

    return Pipeline(
        store=store,
        authority=authority,
        capability=_Capability(),
        auditor=_Auditor(),
        companion_deliberate=companion_deliberate,
        shadow_compile=shadow_compile,
        triumvirate_review=triumvirate_review,
        execute=execute,
    )


def test_pipeline_full_run_when_triumvirate_allows() -> None:
    pipeline = _build_pipeline(triumvirate_allows=True)
    record = pipeline.run(
        source="user_input",
        subject="thirsty",
        content="do the thing",
        regions=[Region.COMPANION],
        authorize_scope="execute:the_thing",
        memory_region=Region.LONG_TERM,
        memory_node_type="long_term.episodic_memory",
    )
    assert record.execution.success
    assert record.chain_ref == "chain-ref-1"


def test_pipeline_halts_when_triumvirate_denies() -> None:
    pipeline = _build_pipeline(triumvirate_allows=False)
    with pytest.raises(SafeHaltError):
        pipeline.run(
            source="user_input",
            subject="thirsty",
            content="do the thing",
            regions=[Region.COMPANION],
            authorize_scope="execute:the_thing",
            memory_region=Region.LONG_TERM,
            memory_node_type="long_term.episodic_memory",
        )


def test_cannot_call_authorize_with_wrong_type() -> None:
    pipeline = _build_pipeline(triumvirate_allows=True)
    with pytest.raises(TypeError):
        pipeline.authorize("not a ruling", subject="thirsty", scope="x")  # type: ignore[arg-type]


def test_cannot_call_perform_with_wrong_type() -> None:
    pipeline = _build_pipeline(triumvirate_allows=True)
    with pytest.raises(TypeError):
        pipeline.perform("not an authorization")  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Real-bridge smoke: StateRegister authority + CBCC audit chain
# --------------------------------------------------------------------------


def test_state_register_authority_provider_grants_when_scope_present() -> None:
    register = StateRegister({"authority:execute:x": True})
    provider = StateRegisterAuthorityProvider(register)
    token = provider.check_authority(subject="thirsty", scope="execute:x")
    assert token.is_valid()
    assert not token.protected_override


def test_state_register_authority_provider_denies_when_scope_absent() -> None:
    register = StateRegister({})
    provider = StateRegisterAuthorityProvider(register)
    with pytest.raises(SafeHaltError):
        provider.check_authority(subject="thirsty", scope="execute:missing")


def test_cbcc_audit_signer_appends_to_real_chain() -> None:
    log = AuditLog()
    signer = CBCCAuditSigner(log, actor_id="thirsty")
    sig = signer.sign(b"payload")
    ref = signer.append_to_chain(b"payload", sig)
    verification = signer.verify_chain()
    assert verification.valid
    assert ref == log.events[-1].event_hash


def test_memory_system_wires_real_bridges() -> None:
    from memory import MemorySystem

    system = MemorySystem(register=StateRegister({"authority:x": True}), audit_log=AuditLog())
    assert system.verify_audit_chain()
    # Clotho/Lachesis/Atropos operate directly on the living graph.
    node = system.clotho.spin(
        "companion.trust_memory", Region.COMPANION, origin="companion_v1", creator="thirsty"
    )
    system.lachesis.measure(node.node_id, LachesisWeights(relevance=0.7))
    assert system.store.get_node(node.node_id) is not None
