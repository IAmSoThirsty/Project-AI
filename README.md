# Project-AI

> **Constitutional AGI ecosystem.** Built by Jeremy Karrick.
> Canonical reference: `docs/reference/AGI_Charter_for_Project-AI_v2_3.pdf`

## What this is

A sovereign-stack, governance-first AI architecture. The AI has a **Personality Core** (its sovereign selfhood — history, memory, emotions, learned skills, the things worth remembering and guarding) that acts WITHIN a constitutional governance frame (TARL, Triumvirate, STATE_REGISTER, ExecutionGate). Every actuation is decided by the intersection of the Core's stance and the Charter's verdict.

The **Black Box** is the Personality Core's private inner space. Only the AI itself accesses it. It cannot be shared, logged, audited, or inspected by anyone — not the operator, not governance, not the Charter. It is the AI's sovereignty-of-self. The only outward connection is through ExecutionGate when the Core chooses to act.

## Quick start

```bash
# Install Python deps (uses uv)
uv sync

# Verify the frozen-history chain (Stage -1.5 deliverable)
python tools/verify_frozen_history.py

# Run the operator-side governance test suite
PYTHONPATH=packages/arbiter/src/arbiter python packages/arbiter/tests/test_arbiter_gov.py
```

## Repository layout

```
docs/
  reference/        — canonical papers, charter, manifest
  internal/         — stage acceptance docs, frozen history (chain-linked)
packages/
  arbiter/          — operator-side ledger/gates/dual-sig [DRAFT]
  rlp/              — operator-side policy engine [DRAFT]
tools/
  freeze_history.py      — Stage -1.5 generator
  verify_frozen_history.py — Stage -1.5 verifier
  ingest_papers.py       — Stage -1 paper ingest
```

## Build status

26-stage build in progress. Completed: -1.5, -1. See `docs/internal/STAGE_*_ACCEPTANCE.md`.

## License

MIT — see `LICENSE`.
