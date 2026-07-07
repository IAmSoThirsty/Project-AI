# PROJECT_AI_ROOT_CANMOVE_REVIEW_V2.md

**Only rows where CanMove != NO after Git/FS correction pass.**

This file lists **7** candidate rows that cleared the narrow conservative re-evaluation (obvious generated/ignored-untracked + not high-risk, or prior archive/side evidence + current non-TRACKED status).

**CRITICAL:** 
- This does **not** authorize any movement.
- Even YES_LOW_RISK and YES_AFTER_OWNER_APPROVAL still require explicit owner approval on the specific row.
- All actions (if ever approved) must follow COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL with pre/post hash verification against PROJECT_AI_ROOT_HASH_MANIFEST_V2.csv, full validation, and rollback capability.
- High-risk items are excluded by design (see correction report).

---
## __pycache__
- Path: T:\Project-AI-main\__pycache__
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: GENERATED_OR_RUNTIME
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l '__pycache__' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.
## .hypothesis
- Path: T:\Project-AI-main\.hypothesis
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: UNKNOWN_REVIEW
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l '.hypothesis' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.
## .mypy_cache
- Path: T:\Project-AI-main\.mypy_cache
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: GENERATED_OR_RUNTIME
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l '.mypy_cache' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.
## .pytest_cache
- Path: T:\Project-AI-main\.pytest_cache
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: GENERATED_OR_RUNTIME
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l '.pytest_cache' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.
## .ruff_cache
- Path: T:\Project-AI-main\.ruff_cache
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: GENERATED_OR_RUNTIME
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l '.ruff_cache' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.
## ci-reports
- Path: T:\Project-AI-main\ci-reports
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: GENERATED_OR_RUNTIME
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l 'ci-reports' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.
## test-artifacts
- Path: T:\Project-AI-main\test-artifacts
- Corrected GitStatus: IGNORED
- GitTracked: False
- GitIgnored: True
- Existing classification: GENERATED_OR_RUNTIME
- ProposedOperation: COPY_VERIFY_THEN_REMOVE_AFTER_APPROVAL
- ProposedDestination: T:\Project-AI-consolidation-logs
- Why it might be movable: GitStatus=IGNORED; GitTracked=False; GitIgnored=True. Confirmed via read-only git commands (no index entry for the root item itself for IGNORED cases, matches .gitignore patterns, physical exists or absent as noted). Not present in high-risk active list. Prior V2 classification or CanMove suggested non-core material. Global untracked count=0 at time of correction.
- Why owner approval is still required: V2 high-assurance protocol + this correction pass. Low-risk label does not remove the requirement for owner sign-off. Tree is currently clean but hidden references, CI side-effects, or reproducibility impact possible. Owner must review the full row in the CORRECTED.csv and the correction report.
- Required validation before action: 1. git status --porcelain (must report 0 dirty) 2. Review exact row in PROJECT_AI_ROOT_CLASSIFICATION_MANIFEST_V2_CORRECTED.csv 3. python -m pytest --collect-only -q 4. ap validate agent_playbook (or --path .) 5. git grep -l 'test-artifacts' -- . (limit to source/docs if needed) 6. Confirm no active runtime/governance references 7. Owner explicit approval (documented) for this TopLevelItem 8. If proceeding: pre-hash from HASH_MANIFEST_V2, COPY_VERIFY, post-hash + validation, then remove only after all gates.

---
**End of movable candidates.** All other 194 - 7 rows have CanMove=NO after correction (default + high-risk force + insufficient git/fs evidence for relaxation).

No movement performed or authorized by this pass.
