# project-ai-tarl

TARL: Threat-Adaptive Rule Language for Project-AI Beginnings.

Sub-phased rebuild of legacy `tarl/` (21 Python files, 3403 LOC, 14
subdirs). Closes C3 from STAGE_19 §9.

## Sub-phase plan

- **H0 (this envelope)**: discovery + skeleton (no source)
- **H1**: Foundational types (spec, policy, core, diagnostics)
- **H2**: Runtime + parser + validator + compiler
- **H3**: System, modules, stdlib, FFI, adapters

See `docs/internal/PHASE_H_DISCOVERY.md` for the full plan.

## Architectural invariants (AGENTS.md v3)

- **Downward-only deps**: tarl imports only kernel + stdlib.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue.
- **Fail-closed**: invalid specs raise TarlError; never silent ALLOW.
- **Pluggable seams**: PolicyProtocol + CompilerProtocol.
- **Deterministic**: state in kernel.StateRegister.
- **Strict typing**: mypy --strict clean.