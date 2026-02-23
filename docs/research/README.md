# PSIA Research Paper

Formal specification of the **Project-AI Sovereign Immune Architecture (PSIA)**.

## Paper

- [`paper.tex`](paper.tex) — Full LaTeX source

## Building

Requires `pdflatex` with standard packages (`amsmath`, `amssymb`, `amsthm`, `booktabs`, `tikz`, `algorithm`, `algpseudocode`, `hyperref`, `enumitem`, `listings`, `xcolor`).

```bash
cd docs/research
pdflatex paper.tex
pdflatex paper.tex   # second pass for cross-references
```

## Implementation Cross-References

Every formal claim in the paper maps to a tested implementation module:

| Paper Section | Claim | Implementation | Tests |
|---|---|---|---|
| §6.3 | Snapshot isolation, OCC, linearizability | `src/psia/concurrency.py` | `tests/test_psia_concurrency.py` |
| §6.2 | Liveness theorem, progress bound (≤115s) | `src/psia/liveness.py` | `tests/test_psia_liveness.py` |
| §7.1 | Shadow determinism, SealedContext, replay hash | `src/psia/shadow/operational_semantics.py` | `tests/test_shadow_operational_semantics.py` |
| §8.4 | Plane-safety type system, INV-ROOT-2 corollary | `src/shadow_thirst/type_system.py` | `tests/test_shadow_thirst_type_system.py` |
| §10 | Threat taxonomy, collusion detection | `src/psia/threat_model.py` | `tests/test_psia_threat_model.py` |
| §5 | Cerberus Gate, quorum engine | `src/psia/gate/` | `tests/test_psia_gate.py` |
| §12 | Benchmarks, methodology | `benchmarks/psia_benchmark.py` | — |

## Running Fact-Verification Tests

```bash
pytest tests/test_psia_concurrency.py tests/test_psia_liveness.py tests/test_psia_threat_model.py tests/test_shadow_operational_semantics.py tests/test_shadow_thirst_type_system.py -v
```
