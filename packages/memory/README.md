# Project-AI Memory — CCMA unified constitutional memory graph

This package is the **entire memory + future memory** substrate for Project-AI.
It implements the Constitutional Cognitive Memory Architecture (CCMA) "one
graph" principle: a single nodes/edges store, the Fates lifecycle
(Clotho / Lachesis / Atropos), and the 12-stage constitutional pipeline
(`memory.ccma`). The raw CCMA skeleton was integrated from
`T:\07-Research\Project-AI Papers\CCMA\ccma` and its fail-closed seams were
wired to the **real** Beginnings subsystems (no fabricated authority, capability,
or signatures).

## Architecture

```
memory.ccma            # the CCMA graph + Fates + typed pipeline (one graph)
memory.bridges         # real-subsystem adapters
  authority   -> kernel.StateRegister            (Law I authority source of truth)
  capability  -> capability.CapabilityAuthority  (T.A.R.L. HMAC tokens)
  audit       -> audit.AuditLog                  (CBCC hash-linked chain)
  retrieval   -> knowledge.VectorIndex           (semantic/vector retrieval)
  triumvirate -> governance.TriumvirateGovernor  (real constitutional review)
```

`packages/knowledge` is **kept intact** — it remains the authoritative
reference-corpus retrieval layer. The `retrieval` bridge *consumes* its
`VectorIndex`, so CCMA's `Pipeline.retrieve()` gains real semantic retrieval
instead of a linear region/type scan, without duplicating or replacing the
knowledge package.

## Public surface

- `MemorySystem` — the runtime facade bundling the graph store, the Fates, and
  the four real bridges. Construct via `get_memory_system(...)`.
- CCMA core types re-exported: `GraphStore`, `UniversalNode`, `Edge`, the
  `Region` / `LifecycleState` / `RelationshipType` enums, the Fates
  (`Clotho` / `Lachesis` / `Atropos`), the `Pipeline` and its stage result
  types, and the fail-closed `SafeHaltError` / ABC interfaces.
- `bridges` — the real-subsystem adapters.

## Constitutional guarantees (enforced, not documented)

- **Law I — Nothing exists without provenance.** `GraphStore.create_node`
  rejects a node missing `origin`/`creator`.
- **Law II — Memory never grants authority.** Authority/capability/audit are
  delegated to `StateRegister` / T.A.R.L. / the CBCC chain via the bridges.
  Until those are wired, the default providers raise `SafeHaltError`.
- **Protected memory.** Resolving a protected node type (governance decisions,
  audit chain, partnership history, …) requires an `AuthorityToken` with
  `protected_override=True` from the real `StateRegister`.
- **Pipeline order is the enforcement.** `authorize()` requires a
  `TriumvirateRuling`; `perform()` requires a `GovernanceAuthorization`. Wrong
  types are refused with `TypeError`.

## Usage

```python
from kernel import StateRegister
from audit.chain import AuditLog
from memory import MemorySystem, get_memory_system

system = get_memory_system(
    register=StateRegister({"authority:execute:the_thing": True}),
    audit_log=AuditLog(),
    # capability_authority=..., vector_index=...  (wire T.A.R.L. + knowledge here)
)

node = system.clotho.spin(
    "companion.trust_memory", Region.COMPANION, origin="companion_v1", creator="thirsty",
    payload={"trust_trajectory": "increasing"},
)
system.lachesis.measure(node.node_id, LachesisWeights(relevance=0.7))
```

## Verification

Run the four canonical gates from the repo root:

```bash
uv run python -m pytest packages/memory -q --tb=short
uv run python -m mypy packages/ tests/ apps/ --strict     # 0 new drift vs 8-error baseline
uv run ruff check packages/memory
uv run ruff format --check packages/memory
```
