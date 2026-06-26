"""
tarl.system — TARL system orchestrator.

The TARL system composes all subsystems (compiler, runtime, stdlib,
modules, ffi, config, diagnostics, policies) into a single entry point.
This is the minimum surface from legacy `tarl/system.py` (395 LOC).

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.system imports only its own submodules.
- Fail-closed: subsystem failures raise TarlSystemError.
- Deterministic: same inputs → same outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tarl.compiler import DefaultCompiler
from tarl.config import TarlConfig, make_config
from tarl.core import TARL, make_tarl
from tarl.diagnostics import DiagnosticBatch, Severity, make_diagnostic
from tarl.ffi import FFIBridge, default_ffi
from tarl.modules import ModuleSystem, default_module_system
from tarl.policy import TarlPolicy
from tarl.runtime import TarlRuntime
from tarl.spec import TarlError
from tarl.stdlib import DEFAULT_STDLIB, StandardLibrary
from tarl.validate import validate


class TarlSystemError(TarlError):
    """Raised when the TARL system fails."""


@dataclass
class TARLSystem:
    """Top-level TARL system orchestrator.

    Composes:
    - config: TarlConfig (runtime settings)
    - diagnostics: DiagnosticBatch (system-level diagnostics)
    - stdlib: StandardLibrary (built-in functions)
    - ffi: FFIBridge (foreign function bindings)
    - modules: ModuleSystem (module registry)
    - runtime: TarlRuntime (compiled record evaluator)
    """

    config: TarlConfig = field(default_factory=make_config)
    diagnostics: DiagnosticBatch = field(default_factory=DiagnosticBatch)
    stdlib: StandardLibrary = field(default_factory=lambda: DEFAULT_STDLIB)
    ffi: FFIBridge = field(default_factory=default_ffi)
    modules: ModuleSystem = field(default_factory=default_module_system)
    runtime: TarlRuntime = field(default_factory=TarlRuntime)
    _initialized: bool = False

    def initialize(self) -> None:
        """Mark the system as initialized.

        Idempotent: calling multiple times is a no-op once initialized.
        """
        if self._initialized:
            return
        self._initialized = True
        self.diagnostics.add(
            make_diagnostic(
                severity=Severity.INFO,
                message="TARL system initialized",
                code="INIT-001",
            )
        )

    def shutdown(self) -> None:
        """Mark the system as shutdown.

        Idempotent.
        """
        if not self._initialized:
            return
        self._initialized = False
        self.diagnostics.add(
            make_diagnostic(
                severity=Severity.INFO,
                message="TARL system shutdown",
                code="SHUT-001",
            )
        )

    def register_policy(self, policy: TarlPolicy) -> None:
        """Register a TarlPolicy with the runtime."""
        if not isinstance(policy, TarlPolicy):
            raise TarlSystemError(f"policy must be TarlPolicy, got {type(policy).__name__}")
        self.runtime.add_policy(policy)

    def compile_and_execute(
        self,
        record: TARL,
        policy: TarlPolicy,
        context: dict[str, object],
    ) -> object:
        """Compile a TARL record against a policy, then execute.

        Returns the TarlDecision. Raises TarlSystemError on validation
        or compile failure.
        """
        if not self._initialized:
            raise TarlSystemError("system not initialized; call initialize() first")
        if not isinstance(record, TARL):
            raise TarlSystemError(f"record must be TARL, got {type(record).__name__}")
        if not isinstance(policy, TarlPolicy):
            raise TarlSystemError(f"policy must be TarlPolicy, got {type(policy).__name__}")
        # Validate
        batch = validate(record)
        if batch.has_errors:
            messages = "; ".join(d.message for d in batch.errors)
            raise TarlSystemError(f"record failed validation: {messages}")
        # Compile
        compiler = DefaultCompiler()
        try:
            compiled = compiler.compile(record, policy)
        except Exception as error:
            raise TarlSystemError(f"compile failed: {type(error).__name__}: {error}") from error
        # Execute
        return self.runtime.execute(compiled, context)


def get_system() -> TARLSystem:
    """Return a fresh TARLSystem instance.

    Convenience factory matching the legacy interface.
    """
    return TARLSystem()


__all__ = [
    "TARLSystem",
    "TarlSystemError",
    "get_system",
    "make_tarl",  # re-export for convenience
]
