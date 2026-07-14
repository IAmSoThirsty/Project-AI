"""
ccma.pipeline

The 12-stage constitutional lifecycle (CCMA Part XII) as an actual
sequential program, not a diagram. Each stage:
  - takes ONLY the typed result object from the previous stage
    (a raw dict or free-form string is refused with a TypeError)
  - returns a new typed result object
  - the next stage's function signature is the enforcement mechanism:
    you cannot call authorize_and_execute() without a TriumvirateRuling
    in hand, because the parameter type is TriumvirateRuling, not
    "anything." This is "no trusted shortcuts" enforced by the type
    system rather than by convention.

Stages implemented: Observation -> WorkingMemory -> Retrieval ->
CompanionDeliberation -> (optional VaultReflection) -> ShadowCompilation
-> TriumvirateReview -> Governance -> Execution -> Audit -> Fates.

What this module deliberately does NOT do: implement Galahad/Cerberus/
Codex's actual constitutional reasoning, Shadow's actual simulation
engine, or the Companion's actual dialogue logic. Those are genuine
AI/decision-logic components specific to your system and I'm not going
to fabricate their internals. What's implemented here is the STRUCTURE
that forces those components to be called in the right order with the
right authority checks — the wiring, not the judgment.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .fates import Atropos, Clotho, Lachesis, LachesisWeights
from .interfaces import (
    AuditSigner,
    AuthorityProvider,
    AuthorityToken,
    CapabilityChecker,
    SafeHaltError,
    Signature,
)
from .models import Region
from .store import GraphStore

# --------------------------------------------------------------------------
# Stage result types — deliberately separate classes, not a single mutable
# "context" dict passed through everything. A mutable shared dict is how
# "governance before execution" quietly turns into "governance somewhere
# in the middle, maybe."
# --------------------------------------------------------------------------


@dataclass
class Observation:
    source: str
    subject: str  # human id, companion instance id, etc.
    content: Any
    observed_at: float = field(default_factory=time.time)


@dataclass
class WorkingMemoryContext:
    observation: Observation
    active_variables: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalBundle:
    context: WorkingMemoryContext
    evidence_node_ids: list[str] = field(default_factory=list)


@dataclass
class Proposition:
    """What the Companion (optionally via the Vault) hands to Shadow. Never a command."""

    retrieval: RetrievalBundle
    statement: str
    supporting_node_ids: list[str]
    confidence: float


@dataclass
class CompiledProposal:
    """Output of Shadow compilation/simulation. Reality is still untouched."""

    proposition: Proposition
    simulation_summary: str
    predicted_effects: list[str]
    unsafe: bool = False


@dataclass
class TriumvirateRuling:
    compiled: CompiledProposal
    galahad_recommendation: str  # "legitimate" | "illegitimate" | "clarify" | "escalate"
    cerberus_recommendation: str  # "safe" | "unsafe" | "restrict" | "isolate" | "escalate"
    codex_judgment: str  # "allow" | "deny" | "revise" | "escalate"

    @property
    def allowed(self) -> bool:
        return (
            self.galahad_recommendation == "legitimate"
            and self.cerberus_recommendation == "safe"
            and self.codex_judgment == "allow"
        )


@dataclass
class GovernanceAuthorization:
    ruling: TriumvirateRuling
    token: AuthorityToken
    required_capability: str | None = None


@dataclass
class ExecutionResult:
    authorization: GovernanceAuthorization
    outcome: str
    success: bool
    executed_at: float = field(default_factory=time.time)


@dataclass
class AuditRecord:
    execution: ExecutionResult
    signature: Signature
    chain_ref: str


# --------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------

# Type aliases for the pluggable judgment functions — YOU implement the
# actual Companion / Shadow / Triumvirate reasoning; this module just
# refuses to let you call them out of order or skip any of them.
CompanionDeliberateFn = Callable[[RetrievalBundle], Proposition]
ShadowCompileFn = Callable[[Proposition], CompiledProposal]
TriumvirateReviewFn = Callable[[CompiledProposal], TriumvirateRuling]
ExecuteFn = Callable[[GovernanceAuthorization], ExecutionResult]


class Pipeline:
    def __init__(
        self,
        store: GraphStore,
        authority: AuthorityProvider,
        capability: CapabilityChecker,
        auditor: AuditSigner,
        companion_deliberate: CompanionDeliberateFn,
        shadow_compile: ShadowCompileFn,
        triumvirate_review: TriumvirateReviewFn,
        execute: ExecuteFn,
    ):
        self._store = store
        self._authority = authority
        self._capability = capability
        self._auditor = auditor
        self._clotho = Clotho(store)
        self._lachesis = Lachesis(store)
        self._atropos = Atropos(store, authority)

        self._companion_deliberate = companion_deliberate
        self._shadow_compile = shadow_compile
        self._triumvirate_review = triumvirate_review
        self._execute = execute

    # -- Stage 1-2: Observation -> Working Memory ---------------------------

    def observe(self, source: str, subject: str, content: Any) -> WorkingMemoryContext:
        obs = Observation(source=source, subject=subject, content=content)
        return WorkingMemoryContext(observation=obs)

    # -- Stage 3: Retrieval ---------------------------------------------------

    def retrieve(
        self, context: WorkingMemoryContext, regions: list[Region], node_type_prefix: str = ""
    ) -> RetrievalBundle:
        if not isinstance(context, WorkingMemoryContext):
            raise TypeError("retrieve() requires a WorkingMemoryContext")
        evidence: list[str] = []
        for region in regions:
            nodes = self._store.query_by_region(region)
            for n in nodes:
                if node_type_prefix and not n.node_type.startswith(node_type_prefix):
                    continue
                evidence.append(n.node_id)
        return RetrievalBundle(context=context, evidence_node_ids=evidence)

    # -- Stage 4-5: Companion Deliberation (Vault reflection folded into the
    #    supplied companion_deliberate callable — the Vault is where that
    #    function is free to explore before returning a Proposition; nothing
    #    it produces before returning is visible to this pipeline, matching
    #    CCMA's Vault isolation) --------------------------------------------

    def deliberate(self, retrieval: RetrievalBundle) -> Proposition:
        if not isinstance(retrieval, RetrievalBundle):
            raise TypeError("deliberate() requires a RetrievalBundle")
        return self._companion_deliberate(retrieval)

    # -- Stage 6: Shadow compilation/simulation -------------------------------

    def compile_and_simulate(self, proposition: Proposition) -> CompiledProposal:
        if not isinstance(proposition, Proposition):
            raise TypeError("compile_and_simulate() requires a Proposition")
        compiled = self._shadow_compile(proposition)
        # Record the compilation as a graph node regardless of outcome —
        # CCMA: Shadow remembers rejected/unsafe futures too, not just
        # promoted ones.
        self._clotho.spin(
            node_type="shadow.compiler_memory",
            region=Region.SHADOW,
            origin="shadow_compiler",
            creator="pipeline",
            payload={
                "statement": proposition.statement,
                "unsafe": compiled.unsafe,
                "predicted_effects": compiled.predicted_effects,
            },
        )
        return compiled

    # -- Stage 7: Triumvirate review -----------------------------------------

    def review(self, compiled: CompiledProposal) -> TriumvirateRuling:
        if not isinstance(compiled, CompiledProposal):
            raise TypeError("review() requires a CompiledProposal")
        if compiled.unsafe:
            # Cerberus doesn't need a full call to know an already-flagged-
            # unsafe compilation isn't going anywhere. Fail closed early.
            return TriumvirateRuling(
                compiled=compiled,
                galahad_recommendation="escalate",
                cerberus_recommendation="unsafe",
                codex_judgment="deny",
            )
        return self._triumvirate_review(compiled)

    # -- Stage 8: Governance (authority verification) -------------------------

    def authorize(
        self,
        ruling: TriumvirateRuling,
        subject: str,
        scope: str,
        required_capability: str | None = None,
    ) -> GovernanceAuthorization:
        if not isinstance(ruling, TriumvirateRuling):
            raise TypeError("authorize() requires a TriumvirateRuling")
        if not ruling.allowed:
            raise SafeHaltError(
                f"Triumvirate did not allow this proposal "
                f"(galahad={ruling.galahad_recommendation}, "
                f"cerberus={ruling.cerberus_recommendation}, "
                f"codex={ruling.codex_judgment}). Refusing to authorize."
            )
        if required_capability is not None:  # noqa: SIM102
            if not self._capability.check_capability(subject, required_capability):
                raise SafeHaltError(
                    f"Capability {required_capability!r} not granted to {subject!r}."
                )
        token = self._authority.check_authority(subject=subject, scope=scope)
        if not token.is_valid():
            raise SafeHaltError(f"Authority token for {subject!r}/{scope!r} is invalid or expired.")
        return GovernanceAuthorization(
            ruling=ruling, token=token, required_capability=required_capability
        )

    # -- Stage 9: Execution ----------------------------------------------------

    def perform(self, authorization: GovernanceAuthorization) -> ExecutionResult:
        if not isinstance(authorization, GovernanceAuthorization):
            raise TypeError("perform() requires a GovernanceAuthorization")
        if not authorization.token.is_valid():
            raise SafeHaltError(
                "Authorization token expired between authorize() and perform() — re-authorize."
            )
        return self._execute(authorization)

    # -- Stage 10: Audit ---------------------------------------------------------

    def audit(self, result: ExecutionResult) -> AuditRecord:
        if not isinstance(result, ExecutionResult):
            raise TypeError("audit() requires an ExecutionResult")
        payload = f"{result.outcome}|{result.success}|{result.executed_at}".encode()
        signature = self._auditor.sign(payload)
        chain_ref = self._auditor.append_to_chain(payload, signature)

        self._clotho.spin(
            node_type="audit.execution_memory",
            region=Region.AUDIT,
            origin="pipeline",
            creator=result.authorization.token.subject,
            payload={"outcome": result.outcome, "success": result.success, "chain_ref": chain_ref},
        )
        return AuditRecord(execution=result, signature=signature, chain_ref=chain_ref)

    # -- Stage 11: The Fates (lifecycle entry for the whole episode) -------------

    def commit_to_memory(
        self, audit_record: AuditRecord, region: Region, node_type: str, weights: LachesisWeights
    ) -> str:
        if not isinstance(audit_record, AuditRecord):
            raise TypeError("commit_to_memory() requires an AuditRecord")
        node = self._clotho.spin(
            node_type=node_type,
            region=region,
            origin="pipeline",
            creator=audit_record.execution.authorization.token.subject,
            payload={
                "outcome": audit_record.execution.outcome,
                "chain_ref": audit_record.chain_ref,
            },
        )
        self._lachesis.measure(node.node_id, weights)
        return node.node_id

    # -- Convenience: run the whole thing end to end --------------------------

    def run(
        self,
        source: str,
        subject: str,
        content: Any,
        regions: list[Region],
        authorize_scope: str,
        memory_region: Region,
        memory_node_type: str,
        required_capability: str | None = None,
    ) -> AuditRecord:
        ctx = self.observe(source, subject, content)
        retrieval = self.retrieve(ctx, regions)
        proposition = self.deliberate(retrieval)
        compiled = self.compile_and_simulate(proposition)
        ruling = self.review(compiled)
        authorization = self.authorize(ruling, subject, authorize_scope, required_capability)
        result = self.perform(authorization)
        record = self.audit(result)
        self.commit_to_memory(
            record,
            memory_region,
            memory_node_type,
            LachesisWeights(
                relevance=0.7, consequence=0.6, frequency=0.1, authority=1.0, novelty=0.5
            ),
        )
        return record
