# Runner Contract

The executor (`taar/executor.py`) is the single execution gate. There is no
second path.

## Order of operations (every run)

1. Load config (safe defaults if `taar.toml` missing).
2. Load registry; any validation error fails the facility closed.
3. **Admit**: agent known + enabled, task known + enabled, facility mode
   permits, capabilities granted, every command declared+allowed+granted,
   output paths within bounds, human approval not required, writer evidence
   present + hash-valid + classification admissible, no lock conflict.
4. Mint run_id (`YYYYmmddTHHMMSSffffffZ-hex8`).
5. Acquire lock; audit `run_admitted`.
6. Capture git state (branch, commit, dirty) — tolerant of git absence.
7. Execute commands in declared order. Builtins dispatch in-process;
   external commands run via `shlex.split` + `subprocess`, `shell=False`,
   task timeout enforced.
8. Readers/watchers: write evidence bundle (SHA-256 over canonical JSON,
   hash field excluded), plus stdout/stderr. Audit any classification
   escalation. Writers: builtins write the report/digest and
   `output.yaml` citing `source_evidence_hash`.
9. Audit `run_succeeded` / `run_failed`; release lock in `finally`.

## Status semantics

    ADMITTED   lock held, execution began
    SUCCEEDED  all commands executed; findings are fine
    FAILED     builtin refused (exit 3), command unavailable, executor error
    KILLED     timeout exceeded
    DENIED     admission refused (audited before raising)

Nonzero exit from an analysis tool is a **finding**, never a failure.
