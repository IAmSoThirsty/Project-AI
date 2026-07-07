# Consolidation Logs (recovered from Project-AI-consolidation-logs)

Operational audit trail of the project's root-cleanup
investigation (2026-06-08 to 2026-06-10), recovered from
``T:\08-Archive\Project-AI-consolidation-logs\``.

27 files, 3.7 MB total. Reference material that documents
the work that produced the
``docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md``.

## What's here

### Operational audit (3 .md + 1 .txt)

  - ``PROJECT_AI_VALIDATION_BLOCKER_DIAGNOSIS_V2.md`` —
    diagnosis of the validation blocker encountered
    during the root-cleanup phase
  - ``PROJECT_AI_VALIDATION_BLOCKER_EVIDENCE_V2.txt`` —
    supporting evidence (raw output, command traces)
  - ``PROJECT_AI_VALIDATION_BLOCKER_FIX_PLAN_V2.md`` —
    the proposed fix plan
  - ``PROJECT_AI_VALIDATION_BLOCKER_FIX_RESULT.md`` —
    the actual fix result
  - ``PROJECT_AI_VALIDATION_FIX_COMMIT_RESULT.md`` —
    the commit-result of the fix

### Root classification (4 .md + 4 .csv)

  - ``PROJECT_AI_ROOT_CANMOVE_REVIEW_V2.md`` — review of
    root entries that could be moved
  - ``PROJECT_AI_ROOT_CLASSIFICATION_SUMMARY_V2.md`` —
    classification summary
  - ``PROJECT_AI_ROOT_GIT_STATUS_CORRECTION_REPORT.md`` —
    the git-status correction report (long, 24 KB)
  - ``PROJECT_AI_ROOT_UNKNOWN_REVIEW_V2.md`` — review of
    unknown root entries
  - ``PROJECT_AI_ROOT_PROVENANCE_NOTES_V2.md`` —
    provenance notes for the root entries
  - ``PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST.csv`` —
    initial classification manifest
  - ``PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2.csv`` —
    V2 manifest (after correction pass)
  - ``PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv`` —
    V2 corrected manifest (final, 377 KB)
  - ``PROJECT_AI_ROOT_HASH_MANIFEST.csv`` — initial
    SHA-256 hash manifest
  - ``PROJECT_AI_ROOT_HASH_MANIFEST_V2.csv`` — V2 hash
    manifest

### Cache cleanup investigation (1 .md + 1 .ps1 + 1 .csv)

  - ``PROJECT_AI_CACHE_CLEANUP_APPROVAL_PACKET.md`` —
    the read-only approval packet (2.2 MB; long but
    contains the full investigation report and
    per-candidate details)
  - ``PROJECT_AI_CACHE_CLEANUP_COMMANDS_DRAFT.ps1`` —
    draft cleanup commands (NOT authorized, draft only)
  - ``PROJECT_AI_CACHE_CLEANUP_PRECHECK.csv`` — precheck
    data for the cleanup investigation

### Git-state snapshots (3 .txt + 2 .txt)

  - ``PROJECT_AI_CURRENT_LSFILES.txt``,
    ``PROJECT_AI_LSFILES.txt``,
    ``PROJECT_AI_LSFILES_V2.txt`` — three snapshots of
    `git ls-files` taken at different times (230 KB each)
  - ``PROJECT_AI_UNTRACKED.txt``,
    ``PROJECT_AI_UNTRACKED_V2.txt`` — untracked-file
    snapshots (both empty)

### Git-status correction (1 .ps1)

  - ``correct-v2-git-status.ps1`` — a PowerShell script
    that computes the corrected git-status
    (20 KB; uses the canonical path discipline; not for
    re-execution, but kept for reference)

### Step logs (3 .log)

  - ``step2.log``, ``step5.log``, ``step6.log`` —
    intermediate step output logs

## Port provenance

This commit copies the 27 files from
``T:\08-Archive\Project-AI-consolidation-logs\`` (the
frozen legacy source) into the canonical repo at
``docs/consolidation-logs/``. The
consolidation-logs archive remains in place; this is a
one-way copy. The archive is the frozen source-of-record
(with Google Drive backup per the rebuild's data
preservation policy); the canonical has the working
copies that evolve with the project.

The 2 empty untracked-file snapshots
(``PROJECT_AI_UNTRACKED.txt``,
``PROJECT_AI_UNTRACKED_V2.txt``) are kept for fidelity
— they document the state of the project's untracked
file tracking at the time of the investigation, and
their emptiness is itself meaningful data.

## See also

  - ``docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md`` —
    the inventory this consolidation work produced
  - ``docs/operations/CONTINUITY_MAP.md`` — operational
    continuity map
