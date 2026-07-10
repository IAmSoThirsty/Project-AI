# project-ai-knowledge

Reference-corpus retrieval that makes Project-AI's governance **knowledge-aware,
not searched**. A curated technical/ethical-hacking corpus is ingested into a
deterministic vector index; a `KnowledgeStore` (implementing
`kernel.KnowledgeSource`) surfaces the passages relevant to an action while it is
being governed. Governance becomes *aware* of what the corpus says — it is never
queried through a standalone search surface.

## Architecture

```
corpus (external, gitignored)                      packages/kernel
  └─ ingest: extract → filter → classify           └─ KnowledgeSource (Protocol)
     → chunk → embed → VectorIndex                     KnowledgePassage
        └─ KnowledgeStore ──implements──▶ ─────────────────┘
                                   │
   packages/governance            │  injected at composition (api/cli)
     KnowledgeAwareGovernor(source)  ── advisory vote (ALLOW / ESCALATE)
```

The dependency direction is inverted: `governance` depends only on the kernel
interface, and the concrete store is injected at the top layer, preserving the
repo's downward-only graph.

## Design choices

- **Advisory only.** The governor votes `ALLOW` (annotating the informing
  knowledge) or `ESCALATE` when the most relevant knowledge is dual-use /
  offensive. It never votes `DENY`; knowledge informs, it does not command.
- **Deterministic.** Chunk IDs are `sha256(source | ordinal | text)`; search
  ties break on `chunk_id`; embeddings are static/CPU-only.
- **Torch-free semantics.** `Model2VecEmbedder` uses model2vec static embeddings
  (pure-numpy inference) — no torch/onnxruntime, the stack removed from this repo
  for Windows stability. `HashingEmbedder` is a dependency-free fallback for tests.
- **No binaries in git.** The raw corpus and index live in a gitignored
  `data/knowledge/`; only code and `KNOWLEDGE_MANIFEST.md` (provenance) are
  committed.

## Build the index

```
uv sync --extra knowledge
uv run --extra knowledge python -m knowledge.ingest \
    --corpus "T:/07-Research/Hatter Information" --out data/knowledge
```

Point the runtime at an index with `$PROJECT_AI_KNOWLEDGE_DIR` (default
`data/knowledge`).
