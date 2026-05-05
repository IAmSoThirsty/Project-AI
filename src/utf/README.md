# Thirsty Stack Bootstrap

![Fully Hydrated](https://img.shields.io/badge/status-fully%20hydrated-2ea043)
![Shadow Approved](https://img.shields.io/badge/shadow-approved-6f42c1)
![Canonical Flow](https://img.shields.io/badge/flow-canonical-1f6feb)

This repository is the amplified bootstrap implementation of the canonical family order:

1. Thirsty-Lang
2. Thirst of Gods
3. T.A.R.L.
4. Shadow Thirst
5. TSCG
6. TSCG-B

## Amplifications integrated

- richer thirst vocabulary: `drip`, `flood`, `condense`, `evaporate`, `well`
- syntactic flow: `|>` piping, `thirst ... quench` guard expressions
- safe forms: `sip?()` and `pour?(...)`
- `spillage ... cleanup finally { ... }`
- `Quenched[T]` option type model with `empty`
- reservoir methods: `strain`, `transmute`, `distill`, `flood`
- parser diagnostics with multi-error recovery and `did you mean?`
- tracing and thirst-level execution output
- persistent REPL history, `:thirst`, `:drink`
- `thirsty doctor`, `thirsty new fountain`, `thirsty bench`, `thirsty fmt`
- true tail-call optimization for user-function tail calls
- real local package manager: publish / install / packages list
- Great Wells gallery and file-based repository flow
- importable stdlib namespace modules: `thirst::time`, `thirst::crypto`, `thirst::reservoir`
- property-style randomized tests for Shadow and codec layers
- strengthened Shadow Thirst analyzers and Mermaid visualization
- plugin hook for custom Shadow analyzers

## What is executable now

- **Thirsty-Lang / Thirst of Gods**: lexer, parser, AST, checker, interpreter, CLI, REPL, formatter, doctor, scaffold, bench, promote bridge, true tail-call optimization, namespace module imports.
- **T.A.R.L.**: deterministic policy parser/evaluator with `ALLOW | DENY | ESCALATE`.
- **Shadow Thirst**: mutation parser, analyzer suite, replay/promote scaffolding, visualization, plugin loader.
- **TSCG**: symbolic parser/encoder/decoder/checksum.
- **TSCG-B**: binary frame codec with CRC32 + SHA-256.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
PYTHONPATH=src python -m unittest discover -s tests -v
```

### Run a Thirsty program

```bash
thirsty run examples/hello.thirsty --trace --thirst-level 2
```

### Package and gallery flow

```bash
thirsty publish .
thirsty gallery list
thirsty install coolpkg
thirsty packages list
```

### Namespace imports

```bash
thirsty run examples/namespace_imports.thirsty
```

### Full stack hydration check

```bash
thirsty doctor .
```

### Analyze a Shadow Thirst mutation and visualize it

```bash
shadowthirst check examples/promote.shadowthirst
shadowthirst visualize examples/promote.shadowthirst
```

### Scaffold a new fountain project

```bash
thirsty new fountain MyProject
```

## Sacred texts

See:
- `docs/language/THIRST_MANIFESTO.md`
- `docs/language/SACRED_TEXTS.md`
- `docs/language/GREAT_WELLS.md`

## Notes

This is an executable amplified bootstrap, not a claim that every tier is already industrially complete. The goal is one living stack where the soul of the language is present in syntax, tooling, diagnostics, and flow.

## Additional docs

- `docs/language/PACKAGES_AND_GREAT_WELLS.md`
