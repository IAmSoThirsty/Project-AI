# project-ai-caretaker

Caretaker constitutional inference runtime (operator-side, experimental).
Ported from `thirsty_governance_framework_0722` `governance_core/caretaker`.

## What this package does

Caretaker hosts a model as an *untrusted* component beneath a constitutional
layer: governance is executable code, not prompt text; continuity is a hash
chain, not serialization.

```
User -> API/CLI -> Session & Continuity -> Governance Runtime
                                              |- T.A.R.L. policy
                                              |- Triumvirate
                                              |- Constitutional Validator
                                              `- Audit Ledger
                                            -> Actualizer Engine
                                            -> Inference Provider
                                                 |- Ollama
                                                 `- Mock (deterministic)
                                            -> Model (untrusted)
```

Entry points: `caretaker.runtime.GovernanceRuntime` (the orchestration
pipeline) and the `caretaker` CLI (`caretaker.cli:main`).

## Authority boundary (AGENTS.md)

Caretaker's constitution, triumvirate, and ledger govern its **own** hosted
inference only. Canonical Project-AI verdict authority (`ALLOW`/`DENY`/
`ESCALATE`) remains `packages/governance`. Operator-side packages may only
invoke AI-side execution through the execution gate — see AGENTS.md section
2.2, which lists Caretaker alongside `arbiter`, `rlp`, and `taar` as an
operator-side experimental package.

## Status: Pre-Alpha, thin test coverage

`Development Status :: 2 - Pre-Alpha` (see `pyproject.toml`). The ~18 source
modules under `src/caretaker/` (constitution, continuity, memory, session,
runtime, `governance/*`, `policies/tarl`, `providers/*`, `api`, `cli`) have
one test file, `tests/test_caretaker_constitution.py`, covering the
constitution module only. `api.py`, `cli.py`, `runtime.py`, `session.py`,
`memory.py`, `continuity.py`, and the entire `governance/` submodule have
**no test coverage yet**. Do not treat this package as production-ready or
as exercising real governance authority until that coverage exists — see
the Creation Completeness and No Fake Success rules in `AGENTS.md`.
