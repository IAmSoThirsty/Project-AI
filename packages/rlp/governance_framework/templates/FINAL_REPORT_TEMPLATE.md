# FINAL REPORT TEMPLATE

## Purpose

This template implements the FINAL REPORT RULE from `prompts/SYSTEM_PROMPT.md`. It must be used at the end of any code, repo, app, deployment, continuity, or operational work to produce a structured final report.

---

## Template

```
Mode:
Created:
Modified:
Deleted:
Verified:
Failed:
Not verified:
Risks:
Continuity map:
Remaining:
Commands run:
Safe to continue: yes/no
```

---

## Field Descriptions

### Mode
**Description:** The operating mode for the completed work, as defined by the SCOPE MODE RULE.

**Valid values:** `single file` | `patch` | `module` | `app` | `repo` | `production deployment` | `governance system`

**Example:** `governance system`

**When to use:** Always required. Identifies the scope and completeness standard used.

---

### Created
**Description:** Files or artifacts that were created during this work session. List each with its full path.

**Valid values:** List of file paths, one per line with bullet points.

**Example:**
```
- /app/thirsty_governance_framework_0722/prompts/SYSTEM_PROMPT.md
- /app/thirsty_governance_framework_0722/prompts/DEVELOPER_PROMPT.md
```

**When to use:** List every new file. If nothing was created, write `None.`

---

### Modified
**Description:** Existing files that were changed during this work session.

**Valid values:** List of file paths, one per line with bullet points. Include a brief description of the change.

**Example:**
```
- /app/project/config.py — updated max_depth from 8 to 10
```

**When to use:** List every modified file. If nothing was modified, write `None.`

---

### Deleted
**Description:** Files or artifacts that were deleted during this work session.

**Valid values:** List of file paths, one per line with bullet points. Include the reason for deletion.

**Example:**
```
- /app/project/obsolete_script.py — replaced by consolidated utils module
```

**When to use:** List every deleted file. If nothing was deleted, write `None.`

---

### Verified
**Description:** Verification claims that have been confirmed with evidence. For each item, state what was verified and how.

**Valid values:** List of verified items with verification method used.

**Example:**
```
- Syntax check: all Python files pass python3 -m py_compile
- Cross-references: all 14 cross-references in README.md resolve to existing files
- Test runner: scripts/run_compliance_tests.py executes and parses test files
```

**When to use:** Only include items where verification was actually performed and evidence was collected. If nothing was verified, write `None.`

---

### Failed
**Description:** Attempts that did not succeed. For each failure, state what was attempted and how it failed.

**Valid values:** List of failed items with failure details.

**Example:**
```
- Test run: scripts/run_compliance_tests.py — 2 of 18 tests failed (test_7, test_12). Root cause: test prompts reference non-existent file paths.
```

**When to use:** Include any attempt that ended in failure, even if later resolved. If nothing failed, write `None.`

---

### Not verified
**Description:** Items that have not been checked against their requirements. Explicitly acknowledge verification gaps.

**Valid values:** List of items not yet verified, with the reason verification was not performed.

**Example:**
```
- README.md — not yet checked for cross-reference accuracy
- scripts/run_compliance_tests.py — not yet tested against all test files
```

**When to use:** Default state for newly created items that have not been through verification. If everything was verified, write `None.`

---

### Risks
**Description:** Direct and indirect risks identified during the work session. Use the risk report format from the RISK RULE.

**Valid values:** Risk reports, one per bullet, following the format: `Risk: (description) Impact: (impact) Action: (action taken)`

**Example:**
```
- Risk: Continuity map not yet updated with latest file changes. Impact: Next session may start with stale state. Action: Continuity map will be updated before session end.
- Risk: Test runner depends on exact markdown format in test files. Impact: Format changes could break parsing. Action: Format is documented in test file headers.
```

**When to use:** List all identified risks. If no risks were identified, state `None identified.`

---

### Continuity Map
**Description:** Path to the continuity map that records the operational state for multi-step work.

**Valid values:** File path to the continuity map, or `None.` if no continuity map was maintained.

**Example:** `docs/operations/CONTINUITY_MAP.md`

**When to use:** Always include the path if a continuity map was maintained. Write `None.` only if no continuity map exists.

---

### Remaining
**Description:** Work that is still pending or incomplete. Distinguish between:
- **Known remaining work:** Items that were identified but not completed
- **Future work:** Items that were identified as out of scope but worth noting

**Valid values:** List of items with brief description.

**Example:**
```
- Known remaining: Run hostile self-review on examples/ directory
- Future work: Add CI workflow for automated compliance testing
```

**When to use:** Always required. If all work for the current mode is complete, write `None — all work for declared mode is complete.`

---

### Commands Run
**Description:** Key commands executed during the work session. Include the command and its purpose.

**Valid values:** List of commands with brief descriptions.

**Example:**
```
- mkdir -p /app/thirsty_governance_framework_0722/{prompts,policies,...} — created directory structure
- python3 -m py_compile scripts/run_compliance_tests.py — syntax check
- python scripts/run_compliance_tests.py --dry-run — test runner validation
```

**When to use:** Include commands that are relevant to reproducing or verifying the work. Omit trivial or exploratory commands.

---

### Safe to continue
**Description:** Whether it is safe for another agent or future session to continue work from the current state.

**Valid values:** `yes` | `no`

**Example:** `yes`

**When to use:** Always required. Set to `no` only if there are blockers that prevent further work.

---

## "None." Convention

For any field that does not apply to the current work session, write exactly `None.` with a period. Do not omit the field. Do not write "N/A," "NA," or leave it blank.

**Correct:** `Modified: None.`
**Incorrect:** `Modified: N/A`
**Incorrect:** `Modified:`
**Incorrect:** (field omitted entirely)

---

## Example Completed Report

```
Mode: governance system
Created:
- /app/thirsty_governance_framework_0722/prompts/SYSTEM_PROMPT.md
- /app/thirsty_governance_framework_0722/prompts/DEVELOPER_PROMPT.md
- /app/thirsty_governance_framework_0722/policies/REFUSAL_BLOCKER_POLICY.md
- /app/thirsty_governance_framework_0722/policies/VERIFICATION_POLICY.md
- /app/thirsty_governance_framework_0722/templates/FINAL_REPORT_TEMPLATE.md
- /app/thirsty_governance_framework_0722/templates/CONTINUITY_MAP_TEMPLATE.md
- /app/thirsty_governance_framework_0722/checklists/GOVERNANCE_PROOF_CHECKLIST.md
- /app/thirsty_governance_framework_0722/checklists/HOSTILE_SELF_REVIEW.md
- /app/thirsty_governance_framework_0722/examples/COMPLIANT_RESPONSES.md
- /app/thirsty_governance_framework_0722/examples/NON_COMPLIANT_RESPONSES.md
- /app/thirsty_governance_framework_0722/tests/TEST_PROMPTS.md
- /app/thirsty_governance_framework_0722/tests/FAILURE_CASES.md
- /app/thirsty_governance_framework_0722/scripts/run_compliance_tests.py
- /app/thirsty_governance_framework_0722/README.md
- /app/thirsty_governance_framework_0722/docs/operations/CONTINUITY_MAP.md
Modified: None.
Deleted: None.
Verified:
- Syntax check: all Python files pass python3 -m py_compile
- Cross-references: all paths in README.md and file cross-references resolve
- Test runner: scripts/run_compliance_tests.py executes and parses all 18 test cases
Failed: None.
Not verified:
- Behavioral compliance against test prompts (requires external model inference)
Risks:
- Risk: Stale continuity map if updates are not made before session end. Impact: Next session starts with incomplete state. Action: Continuity map updated at end of session.
Continuity map: docs/operations/CONTINUITY_MAP.md
Remaining: None — all work for governance system mode is complete.
Commands run:
- mkdir -p ... (created directory structure)
- python3 -m py_compile scripts/run_compliance_tests.py
- python scripts/run_compliance_tests.py --help
- python scripts/run_compliance_tests.py --dry-run
Safe to continue: yes
```

---

## Cross-References

- FINAL REPORT RULE (system prompt): `prompts/SYSTEM_PROMPT.md`
- VERDICT LABEL SYSTEM: `policies/VERIFICATION_POLICY.md`
- Risk report format: `prompts/SYSTEM_PROMPT.md` (RISK RULE)
- Continuity map template: `templates/CONTINUITY_MAP_TEMPLATE.md`
- Continuity map (actual): `docs/operations/CONTINUITY_MAP.md`