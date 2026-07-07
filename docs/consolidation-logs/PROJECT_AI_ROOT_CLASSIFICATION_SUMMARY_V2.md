# PROJECT_AI_ROOT_CLASSIFICATION_SUMMARY_V2.md

**Date:** 06/10/2026 07:05:49
**Repo:** T:\Project-AI-main (master)
**Protocol:** High-assurance read-only V2 (phases 0-7). Defaults: Classification=UNKNOWN_REVIEW, CanMove=NO, OwnerApprovalRequired=YES. Overrides only with strong evidence from current git/fs + prior audits (BOUNDARY_AUDIT.md, RESPONSIBILITY_RECOVERY_AUDIT.md, CAPABILITY_AUTHORITY_PROVENANCE.md, ACTIVE_MAP.md, DELETED_FILES_HISTORY.txt, PROJECT_AI_ACTIVE_MAP.md) + step2/5/6.log as **provenance only** (no movement authorization).

Total root items reviewed: 194

Count by Classification:
  UNKNOWN_REVIEW: 166
  ACTIVE_ROOT: 17
  GENERATED_OR_RUNTIME: 6
  ACTIVE_DOC: 3
  ARCHIVE_DOC: 1
  SIDE_SYSTEM: 1


Count by LifecycleStatus:
  UNKNOWN: 166
  ACTIVE: 17
  GENERATED: 6
  DOCUMENTATION: 3
  ARCHIVE: 1
  SIDE_SYSTEM: 1


Count by CanMove:
  False: 186
  True: 8


Items marked UNKNOWN_REVIEW: 166
Items marked SIDE_SYSTEM: 1
Items marked DUPLICATE_OR_MIRROR: 0
Items marked GENERATED_OR_RUNTIME: 6
Items marked CACHE_OR_ENVIRONMENT: 0
Items that appear active and must stay: 17
Items that require owner approval: 194

Suspicious/contradictory evidence: None detected. All high-risk items (src/, governance/, tests/, agent_playbook/, .github/ etc.) correctly defaulted or classified ACTIVE_ROOT with CanMove=NO per protocol.

Whether the repo is safe for structural movement yet: **NO**. Vast majority of core active areas classified CanMove=NO + OwnerApprovalRequired=YES. step2/5/6.log entries provide prior copy provenance (DC01, pre-phase2 webhooks, StormDesk) but do **not** authorize moves.

Final recommendation: Review the full V2 manifest (CSV) thoroughly before any action. No moves, untracks, or structural changes inside Project-AI-main until owner explicitly approves specific ProposedOperations case-by-case. This V2 replaces prior versions as the high-assurance baseline. Follow Phase 3+ only after owner sign-off on individual rows.
