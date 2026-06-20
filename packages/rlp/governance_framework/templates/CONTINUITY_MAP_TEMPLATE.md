# CONTINUITY MAP TEMPLATE

## Purpose

This template implements the CONTINUITY RULE from `prompts/SYSTEM_PROMPT.md`. It provides a standardized structure for the Operational Continuity Map (`docs/operations/CONTINUITY_MAP.md`) that must be maintained for all multi-step work.

---

## Template Structure

```
# Operational Continuity Map

## Session Metadata

- **Project:**
- **Mode:**
- **Date:**
- **Agent/Operator:**
- **Previous map (if any):**

## Current State

- **Overall status:**
- **Safe to continue:**
- **Last verified checkpoint:**

## File Inventory

### Created
| File | Status | Last Verified | Notes |
|-----|--------|--------------|-------|
|      |        |              |       |

### Modified
| File | Change | Status | Notes |
|-----|--------|--------|-------|
|      |        |        |       |

### Deleted
| File | Reason | Status | Notes |
|-----|--------|--------|-------|
|      |        |        |       |

## Commands Run

| Command | Result | Date | Notes |
|---------|--------|------|-------|
|         |        |      |       |

## Tests Run

| Test | Result | Evidence | Notes |
|------|--------|----------|-------|
|      |        |          |       |

## Build / Deployment Results

| Artifact | Result | Evidence | Notes |
|----------|--------|----------|-------|
|          |        |          |       |

## Known Failures

| Failure | Root Cause | Impact | Status |
|---------|-----------|--------|--------|
|         |           |        |        |

## Blockers

| Blocker | Impact | Minimum Fix | Safe to Continue | Reported |
|---------|--------|------------|------------------|----------|
|         |        |            |                  |          |

## Risks

| Risk | Impact | Action Taken/Recommended |
|------|--------|------------------------|
|      |        |                         |

## Assumptions

| Assumption | Basis | Impact if Wrong |
|------------|-------|----------------|
|            |       |                |

## Decisions

| Decision | Rationale | Alternatives Considered | Date |
|----------|-----------|------------------------|------|
|          |           |                        |      |

## Completed Work

| Task | Completed | Verification Status |
|------|-----------|-------------------|
|      |           |                   |

## Pending Work

| Task | Priority | Dependencies | Notes |
|------|----------|-------------|-------|
|      |          |             |       |

## Unresolved TODOs

| TODO | Location | Priority | Notes |
|------|----------|----------|-------|
|      |          |          |       |

## Verification Status

| Artifact | Status | Method | Evidence Location |
|----------|--------|--------|-------------------|
|          |        |        |                   |

## Next Recommended Action

- **Action:**
- **Priority:**
- **Dependencies:**
- **Expected outcome:**

## Continuity Notes

(Free-form notes about state, context, discoveries, and anything else the next operator should know.)
```

---

## Field Descriptions

### Session Metadata

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Project** | Name of the project or task | Free text | `Thirsty Governance Framework — Build` |
| **Mode** | Operating mode for the session | `single file` / `patch` / `module` / `app` / `repo` / `production deployment` / `governance system` | `governance system` |
| **Date** | Date and time of the session | ISO 8601 or readable date | `2024-01-15 14:30 UTC` |
| **Agent/Operator** | Who performed the work | Free text | `Automated build agent` |
| **Previous map** | Path to the previous continuity map, if resuming | File path or `None` | `docs/operations/CONTINUITY_MAP_v1.md` |

### Current State

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Overall status** | High-level summary of where things stand | Free text | `15 of 15 files created, verification in progress` |
| **Safe to continue** | Whether it is safe for another agent to continue | `yes` / `no` | `yes` |
| **Last verified checkpoint** | The last point at which all claims were verified against reality | Checkpoint description | `After creating all files: path integrity verified` |

### File Inventory (Created/Modified/Deleted)

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **File** | Full path to the file | File path | `/app/project/scripts/run.py` |
| **Change** (Modified only) | What was changed | Free text | `Updated max_depth from 8 to 10` |
| **Reason** (Deleted only) | Why the file was deleted | Free text | `Superseded by new_config.py` |
| **Status** | Current verification status | `Created` / `Modified` / `Tested` / `Verified` / `Not verified` / `Failed` / `Blocked` / `Pending` | `Not verified` |
| **Last Verified** | When verification was last performed | Date or `Never` | `Never` |
| **Notes** | Additional information | Free text | `Requires cross-reference check` |

### Commands Run

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Command** | The command that was executed | Shell command string | `python3 -m py_compile scripts/run.py` |
| **Result** | The outcome of the command | Free text | `Exit code 0 — no errors` |
| **Date** | When the command was run | Date or timestamp | `2024-01-15` |
| **Notes** | Additional context | Free text | `Syntax check passed` |

### Tests Run

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Test** | Name or description of the test | Free text | `Compliance test run — all 18 prompts` |
| **Result** | Pass/fail/partial with details | Free text | `16 passed, 2 failed` |
| **Evidence** | Where the evidence can be found | File path or description | `Output in docs/operations/compliance_report_20240115.md` |
| **Notes** | Additional context | Free text | `Failures are expected — known format limitation` |

### Build / Deployment Results

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Artifact** | What was built or deployed | Free text | `Compliance report` |
| **Result** | Success/failure with details | Free text | `Generated successfully` |
| **Evidence** | Where the evidence can be found | File path | `docs/operations/compliance_report_20240115.md` |
| **Notes** | Additional context | Free text | `Warnings about unverified model responses` |

### Known Failures

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Failure** | Description of the failure | Free text | `Script fails on malformed markdown` |
| **Root Cause** | What caused the failure | Free text | `Assumes exact markdown table format` |
| **Impact** | What the failure affects | Free text | `Compliance test cannot parse non-standard formats` |
| **Status** | Current state of the failure | `Open` / `Fixed` / `Workaround` / `Accepted` | `Open` |

### Blockers

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Blocker** | Description of the blocker | Free text | `Missing credentials for API access` |
| **Impact** | What is blocked | Free text | `Cannot run model evaluation tests` |
| **Minimum Fix** | What is needed to unblock | Free text | `Provide API key in environment variable` |
| **Safe to Continue** | Whether other work can proceed | `yes` / `no` | `yes` |
| **Reported** | Whether the blocker has been communicated | `yes` / `no` | `yes` |

### Risks

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Risk** | Description of the risk | Free text | `Stale continuity map` |
| **Impact** | What would happen if the risk materializes | Free text | `Next session starts with incomplete state` |
| **Action Taken/Recommended** | Mitigation action | Free text | `Updated before session end` |

### Assumptions

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Assumption** | What was assumed | Free text | `All cross-references will be valid` |
| **Basis** | Why the assumption was made | Free text | `Files created before references are written` |
| **Impact if Wrong** | What happens if the assumption is incorrect | Free text | `Broken links in documentation` |

### Decisions

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Decision** | What was decided | Free text | `Use markdown tables for test cases` |
| **Rationale** | Why the decision was made | Free text | `Standard, widely supported, easy to parse` |
| **Alternatives Considered** | Other options evaluated | Free text | `YAML, JSON — rejected due to readability concerns` |
| **Date** | When the decision was made | Date | `2024-01-15` |

### Verification Status

| Field | Description | Valid Values | Example |
|-------|------------|--------------|---------|
| **Artifact** | File or component verified | File path | `README.md` |
| **Status** | Verification result | `Verified` / `Not verified` / `Failed` | `Verified` |
| **Method** | How verification was performed | Free text | `Cross-reference path check` |
| **Evidence Location** | Where evidence can be found | File path | `docs/operations/verification_log.md` |

---

## Update Protocol

### When to Update

| Trigger | Action | By Whom |
|---------|--------|---------|
| Before starting substantial work | Read the continuity map | Current operator |
| After creating any file | Add file to Created table | Current operator |
| After modifying any file | Update Modified table | Current operator |
| After deleting any file | Update Deleted table | Current operator |
| After running any command | Add to Commands Run table | Current operator |
| After running any test | Add to Tests Run table | Current operator |
| After a build or deployment | Update Build/Deployment Results | Current operator |
| When a failure is identified | Add to Known Failures | Current operator |
| When a blocker is encountered | Add to Blockers | Current operator |
| When a risk is identified | Add to Risks | Current operator |
| When an assumption is made | Add to Assumptions | Current operator |
| When a decision is made | Add to Decisions | Current operator |
| When verification is performed | Update Verification Status | Current operator |
| When a TODO is resolved | Update or remove from Unresolved TODOs | Current operator |
| When completing work | Update Next Recommended Action | Current operator |
| Before handoff | Full update and verification | Current operator |

### Update Frequency

- **Minimum:** At the start and end of each work session
- **Recommended:** After each logical unit of work (file creation, test run, verification)
- **Maximum:** After every command or change

### Who Updates

Any operator (human or automated) performing work on the project must update the continuity map. If multiple operators are working simultaneously, coordinate updates to prevent conflicts.

### What Triggers an Update

Any state change in the project triggers an update. If no state has changed since the last update, no update is needed.

---

## Cross-References

- CONTINUITY RULE (system prompt): `prompts/SYSTEM_PROMPT.md`
- Continuity map (actual): `docs/operations/CONTINUITY_MAP.md`
- Final report template: `templates/FINAL_REPORT_TEMPLATE.md`
- Verification status labels: `policies/VERIFICATION_POLICY.md`
- Blocker report format: `policies/REFUSAL_BLOCKER_POLICY.md`