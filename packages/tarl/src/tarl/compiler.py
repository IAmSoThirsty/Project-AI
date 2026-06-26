"""
tarl.compiler — Compile a TARL record into an executable form.

The compiler takes a TARL record + a TarlPolicy and produces a CompiledTarl
that holds the canonical hash + the bound policy. The CompiledTarl can
then be passed to TarlRuntime.execute().

This is the minimum surface from legacy `tarl/compiler/__init__.py`
(407 LOC). Captures the typed structure; defers advanced compilation
patterns to a later wave.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.compiler imports only tarl.core + tarl.policy
  + tarl.spec + tarl.validate + stdlib.
- Fail-closed: compilation failures raise TarlCompileError.
- Pluggable seams: Compiler Protocol + default_compile_policy().
- Deterministic: CompiledTarl.record_hash is stable across compilation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from tarl.core import TARL
from tarl.policy import TarlPolicy
from tarl.spec import TarlError
from tarl.validate import (
    allowed_authorities,
    validate_with_authorities,
)


class TarlCompileError(TarlError):
    """Raised when a TARL cannot be compiled."""


class Compiler(Protocol):
    """Pluggable TARL compiler."""

    def compile(self, record: TARL, policy: TarlPolicy) -> CompiledTarl: ...


@dataclass(frozen=True)
class CompiledTarl:
    """The result of compiling a TARL record + policy.

    Attributes:
        record: The original TARL record.
        policy_name: The name of the bound policy.
        record_hash: The TARL.hash() at compile time (for tamper-evidence).
        compiled_at: Opaque string identifying the compiler version.
    """

    record: TARL
    policy_name: str
    record_hash: str
    compiled_at: str = "tarl.compiler/v1"

    @property
    def canonical(self) -> dict[str, object]:
        """Return JSON-serializable dict of the compiled record."""
        return {
            "record": self.record.canonical(),
            "policy_name": self.policy_name,
            "record_hash": self.record_hash,
            "compiled_at": self.compiled_at,
        }


class DefaultCompiler:
    """Default compiler: validate record, bind policy, return CompiledTarl."""

    def compile(self, record: TARL, policy: TarlPolicy) -> CompiledTarl:
        if not isinstance(record, TARL):
            raise TarlCompileError(f"record must be TARL, got {type(record).__name__}")
        if not isinstance(policy, TarlPolicy):
            raise TarlCompileError(f"policy must be TarlPolicy, got {type(policy).__name__}")
        # Validate record against default authority allow-list
        auths = allowed_authorities(record)
        batch = validate_with_authorities(record, auths)
        if batch.has_errors:
            messages = "; ".join(d.message for d in batch.errors)
            raise TarlCompileError(f"record failed validation: {messages}")
        return CompiledTarl(
            record=record,
            policy_name=policy.name,
            record_hash=record.hash(),
        )


def default_compile_policy() -> Compiler:
    """Return the default compiler (validates + binds policy)."""
    return DefaultCompiler()


def compile_record(record: TARL, policy: TarlPolicy) -> CompiledTarl:
    """Convenience: compile a record with the default compiler."""
    return default_compile_policy().compile(record, policy)


__all__ = [
    "CompiledTarl",
    "Compiler",
    "DefaultCompiler",
    "TarlCompileError",
    "compile_record",
    "default_compile_policy",
]
