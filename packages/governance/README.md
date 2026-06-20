# Project-AI Governance

This is the AI-side governance layer. It evaluates kernel invariants before governor votes, honors
unilateral veto, preserves `ESCALATE`, and denies on missing governors or evaluator faults. It
returns canonical kernel decisions with hash-bound evidence. It does not execute actions or issue
capabilities.
