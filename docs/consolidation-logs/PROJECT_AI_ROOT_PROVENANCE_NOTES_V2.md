# PROJECT_AI_ROOT_PROVENANCE_NOTES_V2.md

**step2.log provenance (DC01 scripts copy):**
- Prior activity: Copied DC01 PowerShell scripts into IT\pentest\labs\DC01\Scripts\ (now appears as top-level "IT" item).
- Current manifest row: Classified SIDE_SYSTEM (per BOUNDARY_AUDIT + current evidence + step2 context).
- References in active code: Low (per prior RESPONSIBILITY_RECOVERY_AUDIT).
- Recommendation: Leave untouched pending owner review of its specific manifest row(s). step2.log is **provenance of prior copy only**; does not prove current active use or grant movement rights.

**step5.log provenance (pre-phase2 alert webhooks):**
- Prior activity: Copied pre-phase2 alert webhook JSONs into archive\pre-phase2\data\alert_webhook\ (under top-level "archive").
- Current status: ARCHIVE_DOC / DUPLICATE_OR_MIRROR per logic.
- References: Historical (DELETED_FILES_HISTORY, RESPONSIBILITY_RECOVERY).
- Recommendation: Treated strictly as archive/provenance material. No movement/COPY_VERIFY without owner approval after full manifest review.

**step6.log provenance (StormDesk):**
- Prior activity: Copied Storm Desk into StormDesk\ top-level.
- Current status: SIDE_SYSTEM (per BOUNDARY_AUDIT).
- References: Separate subsystem; not part of core Project-AI runtime/governance/agent/test per prior audits.
- Recommendation: Provenance noted. Even if CanMove=true for the row, OwnerApprovalRequired=YES. Do not move until owner reviews the manifest row and explicitly approves.

These logs (step2/5/6) are used **strictly as provenance** of prior consolidation copies into the tree. They do not override high-assurance defaults (UNKNOWN_REVIEW / CanMove=NO / Owner=YES) for any item. Any future movement requires the full Phase 3 evidence chain + explicit owner approval per the protocol.

No other high-confidence provenance from the listed prior audit files alters the default posture for root items. All decisions remain traceable to the manifest CSV + these notes + the git state at time of generation (see PROJECT_AI_ROOT_HASH_MANIFEST_V2.csv and LSFILES_V2.txt).
