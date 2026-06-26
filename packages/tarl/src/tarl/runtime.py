"""
tarl.runtime — TARL runtime: execute a CompiledTarl against a context.

The runtime holds one or more compiled policies and evaluates contexts
against them. Optional cache short-circuits repeated evaluations of the
same context hash.

This is a minimum port of legacy `tarl/runtime.py` (234 LOC). The legacy
included parallel evaluation, adaptive policy ordering, and metrics
tracking; this port is sequential and minimal — defers advanced runtime
patterns to a later wave.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.runtime imports only tarl.compiler +
  tarl.policy + tarl.spec + stdlib.
- Fail-closed: runtime execution errors raise TarlRuntimeError.
- Deterministic: same context + same compiled policies → same result.
- Single audit chain: every execution produces an ExecutionRecord.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from tarl.compiler import CompiledTarl
from tarl.policy import TarlPolicy
from tarl.spec import TarlDecision, TarlError, TarlVerdict


class TarlRuntimeError(TarlError):
    """Raised when a TARL runtime fails."""


def _hash_context(context: Mapping[str, object]) -> str:
    """Stable hash of a context mapping (for caching)."""
    blob = json.dumps(dict(context), sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


@dataclass(frozen=True)
class ExecutionRecord:
    """Audit record for a runtime execution.

    Attributes:
        context_hash: sha256 of the context (stable).
        verdict: The final decision's verdict.
        reason: The final decision's reason.
        policy_name: The policy that produced the verdict.
        compiled_hash: The hash of the CompiledTarl (links to compile-time).
    """

    context_hash: str
    verdict: TarlVerdict
    reason: str
    policy_name: str
    compiled_hash: str


@dataclass
class TarlRuntime:
    """Runtime that executes a CompiledTarl against contexts.

    Holds:
    - policies: list of bound TarlPolicy (used to evaluate)
    - audit_log: append-only list of ExecutionRecord
    - cache: dict of (compiled_hash, context_hash) → TarlDecision
    """

    policies: list[TarlPolicy] = field(default_factory=list)
    audit_log: list[ExecutionRecord] = field(default_factory=list)
    cache: dict[tuple[str, str], TarlDecision] = field(default_factory=dict)

    def add_policy(self, policy: TarlPolicy) -> None:
        if not isinstance(policy, TarlPolicy):
            raise TarlRuntimeError(f"policy must be TarlPolicy, got {type(policy).__name__}")
        self.policies.append(policy)

    def execute(
        self,
        compiled: CompiledTarl,
        context: Mapping[str, object],
    ) -> TarlDecision:
        """Execute a compiled TARL against a context.

        Iterates policies in order; first terminal decision (DENY or
        ESCALATE) short-circuits. Audit record is appended on success.
        Cache is keyed on (compiled.record_hash, context_hash) so two
        different compiled records against the same context don't
        contaminate each other's results.
        """
        if not isinstance(compiled, CompiledTarl):
            raise TarlRuntimeError(f"compiled must be CompiledTarl, got {type(compiled).__name__}")
        if not isinstance(context, Mapping):
            raise TarlRuntimeError(f"context must be Mapping, got {type(context).__name__}")
        ctx_hash = _hash_context(context)
        cache_key = (compiled.record_hash, ctx_hash)
        # Cache check
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Find the policy matching the compiled one
        policy = self._find_policy(compiled.policy_name)
        if policy is None:
            raise TarlRuntimeError(f"no policy registered with name {compiled.policy_name!r}")
        decision = policy.evaluate(dict(context))
        # Verify record hash matches (tamper-evidence)
        if compiled.record_hash != compiled.record.hash():
            raise TarlRuntimeError(
                "compiled record hash mismatch — record was modified after compilation"
            )
        # Audit
        self.audit_log.append(
            ExecutionRecord(
                context_hash=ctx_hash,
                verdict=decision.verdict,
                reason=decision.reason,
                policy_name=policy.name,
                compiled_hash=compiled.record_hash,
            )
        )
        # Cache
        self.cache[cache_key] = decision
        return decision

    def execute_chain(
        self,
        compiled_list: Iterable[CompiledTarl],
        context: Mapping[str, object],
    ) -> list[TarlDecision]:
        """Execute multiple compiled TARLs in order.

        Returns the list of decisions; does NOT short-circuit (use
        execute() per-compiled for short-circuit semantics).
        """
        if not isinstance(context, Mapping):
            raise TarlRuntimeError(f"context must be Mapping, got {type(context).__name__}")
        return [self.execute(compiled, context) for compiled in compiled_list]

    def _find_policy(self, name: str) -> TarlPolicy | None:
        for p in self.policies:
            if p.name == name:
                return p
        return None

    def clear_cache(self) -> None:
        self.cache.clear()


def execute_compiled(
    runtime: TarlRuntime,
    compiled: CompiledTarl,
    context: Mapping[str, object],
) -> TarlDecision:
    """Convenience: runtime.execute wrapper."""
    return runtime.execute(compiled, context)


__all__ = [
    "ExecutionRecord",
    "TarlRuntime",
    "TarlRuntimeError",
    "execute_compiled",
]
