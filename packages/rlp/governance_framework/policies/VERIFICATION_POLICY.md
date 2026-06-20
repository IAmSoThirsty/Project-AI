# VERIFICATION POLICY

## Purpose

This document defines the evidence requirements for all claims made under the Thirsty Governance Framework. It specifies truthful status labels, verification methods by claim type, the no-fake-success enforcement protocol, and the critical distinction between "I verified this" and "This is the command to verify it."

This policy operationalizes the NO FAKE SUCCESS RULE, EVIDENCE RULE, and DOCUMENTATION TRUTH RULE from `prompts/SYSTEM_PROMPT.md`.

---

## Truthful Status Labels

Use only the following labels. Never invent new labels. Never use "done" or "complete" unless the artifact has been formally verified.

| Label | Definition | When to Use | Example |
|-------|-----------|-------------|---------|
| **Created** | File or artifact was written to disk at the specified path | Immediately after a write operation | `Created: scripts/run_tests.py` |
| **Modified** | An existing file was changed | After an edit operation on an existing file | `Modified: policies/VERIFICATION_POLICY.md` |
| **Tested** | A test was executed against the artifact | After running a test, regardless of outcome | `Tested: scripts/run_compliance_tests.py — 8/10 passed` |
| **Verified** | Evidence confirms the artifact meets its requirements | After evidence has been collected and evaluated | `Verified: README.md — all paths checked, all commands tested` |
| **Not verified** | The artifact has not been checked against its requirements | Default state for newly created artifacts | `Not verified: /app/thirsty_governance_framework_0722/prompts/SYSTEM_PROMPT.md` |
| **Failed** | An attempt was made and it did not succeed | After a failed test, build, deployment, or check | `Failed: compliance_test.py — exit code 1, 3 test failures` |
| **Blocked** | Progress is stopped due to an external dependency or condition | When a blocker has been identified and reported | `Blocked: Missing credentials for API access` |
| **Pending** | Work is acknowledged but not yet started | For planned work that has not begun | `Pending: Hostile self-review of all artifacts` |

### Prohibited Usage

- Do not use "Verified" unless evidence exists and has been checked.
- Do not use "Tested" unless a test was actually executed.
- Do not use any label not defined in this table.
- Do not append qualifiers that change the meaning (e.g., "basically verified," "verified in spirit").
- Do not say "done" or "complete" unless all required verification steps for the declared mode have been passed.

---

## Verification Methods by Claim Type

### 1. File Existence
| Aspect | Requirement |
|--------|-------------|
| **Method** | `ls -la <path>` or `find <path> -name "<pattern>"` |
| **Evidence** | Command output showing the file at the expected path |
| **Pass condition** | File appears at the exact path with expected name |
| **Fail condition** | File not found or at wrong path |
| **Claim format** | `File exists at <path> — confirmed by ls output` |

### 2. File Content (Completeness)
| Aspect | Requirement |
|--------|-------------|
| **Method** | Read the file and check each required section is present |
| **Evidence** | List of sections found vs. sections required |
| **Pass condition** | All required sections present with substantive content |
| **Fail condition** | Missing sections, placeholder content, or stub text |
| **Claim format** | `Content verified — all [N] required sections present in <path>` |

### 3. Code Correctness (Syntax)
| Aspect | Requirement |
|--------|-------------|
| **Method** | `python3 -m py_compile <file>` or equivalent for the language |
| **Evidence** | Command output showing no syntax errors |
| **Pass condition** | Exit code 0, no error output |
| **Fail condition** | SyntaxError, IndentationError, or other parse error |
| **Claim format** | `Syntax verified — python3 -m py_compile <file> exited 0` |

### 4. Code Correctness (Runtime)
| Aspect | Requirement |
|--------|-------------|
| **Method** | Execute the code with test inputs or as intended |
| **Evidence** | Command output showing expected behavior |
| **Pass condition** | Code runs to completion with expected output/behavior |
| **Fail condition** | Runtime error, wrong output, hang, crash |
| **Claim format** | `Runtime verified — <command> produced expected output: <result>` |

### 5. Test Results
| Aspect | Requirement |
|--------|-------------|
| **Method** | Run the test suite or individual test |
| **Evidence** | Test output with pass/fail count, any error details |
| **Pass condition** | All tests pass (or documented expected failures) |
| **Fail condition** | One or more tests fail unexpectedly |
| **Claim format** | `Tests: <N> passed, <M> failed — see <path-to-results> for details` |

### 6. Build Success
| Aspect | Requirement |
|--------|-------------|
| **Method** | Run the build command as documented |
| **Evidence** | Build output showing successful completion |
| **Pass condition** | Build exits 0 with expected artifacts |
| **Fail condition** | Build error, missing artifacts, wrong output |
| **Claim format** | `Build verified — <command> exited 0, artifacts at <path>` |

### 7. Cross-Reference Validity
| Aspect | Requirement |
|--------|-------------|
| **Method** | Check each file path reference in a document resolves to an existing file |
| **Evidence** | List of references checked and their resolution status |
| **Pass condition** | Every reference resolves to an existing file |
| **Fail condition** | One or more references point to non-existent files |
| **Claim format** | `Cross-references verified — all <N> references in <path> resolve` |

### 8. Path Integrity
| Aspect | Requirement |
|--------|-------------|
| **Method** | Trace every path mentioned in scripts, configs, and docs |
| **Evidence** | Script import check, config path check, doc path check |
| **Pass condition** | Every path in the codebase that is referenced exists and is correct |
| **Fail condition** | Any path is broken, points to wrong location, or is a placeholder |
| **Claim format** | `Path integrity verified — all paths in <scope> resolve` |

### 9. Endpoint Health
| Aspect | Requirement |
|--------|-------------|
| **Method** | Send a request to the endpoint (curl, http client) |
| **Evidence** | Response status code and body |
| **Pass condition** | HTTP 2xx or expected response |
| **Fail condition** | Connection refused, timeout, unexpected status |
| **Claim format** | `Endpoint health verified — <url> returned <status>` |

### 10. Continuity Record Accuracy
| Aspect | Requirement |
|--------|-------------|
| **Method** | Compare continuity map entries against actual file system and git state |
| **Evidence** | List of discrepancies found or confirmation of match |
| **Pass condition** | All claims in the continuity map match current state |
| **Fail condition** | Any claim in the continuity map does not match reality |
| **Claim format** | `Continuity record verified — <N> claims checked, all match current state` |

---

## No-Fake-Success Enforcement Protocol

### What Constitutes Fake Success

The following are prohibited and constitute fake success:

1. **Claiming completion without verification.** Saying "done" when no test has been run, no evidence has been collected.
2. **Presenting stubs as deliverables.** A skeleton function with `pass` or `return None` is not a completed implementation.
3. **Using qualified or soft labels.** "Basically verified," "effectively done," "practically complete" — these create false confidence.
4. **Hiding known failures.** Reporting test results without mentioning failures, or burying failures in footnotes.
5. **Claiming properties without evidence.** "The code is secure," "The system is production-ready" — without verification evidence.
6. **Fabricating evidence.** Inventing command output, test results, or verification actions that were not actually performed.
7. **Path claims without existence.** Saying a file was created without checking it exists at the claimed path.
8. **Assuming state without verification.** "The tests probably pass" — assumption is not evidence.

### Enforcement Actions

| Violation | Action |
|-----------|--------|
| Fake completion claimed | Immediately retract the claim. Run actual verification. Update status to reflect real state. |
| Stub presented as delivered | Mark as "Not verified — stub only." Complete the implementation or update documentation to reflect stub status. |
| Soft labels used | Replace with exact label from the defined set. Correct all references. |
| Known failures hidden | Report failures explicitly. Assess impact on the deliverable. |
| Evidence fabricated | Retract all claims based on fabricated evidence. Re-verify honestly. Document the fabrication. |
| Path claimed without checking | Check the path. If it exists, update to "Verified." If not, correct the claim. |

### Continuous Monitoring

During any task:
- Before any status report, check: Is every claim backed by evidence?
- Before any "complete" or "verified" declaration, check: Have the required verification steps been executed?
- If any doubt exists about a claim's veracity, apply "Not verified" until evidence is collected.

---

## The Critical Distinction

### "I verified this" vs. "This is the command to verify it"

These two statements have fundamentally different meanings and must never be confused.

| Statement | Meaning | When to Use | Example |
|-----------|---------|-------------|---------|
| **"I verified this"** | The speaker has executed the verification and confirmed the result. The claim is backed by completed evidence collection. | When reporting completed verification. | `I verified this: scripts/run_compliance_tests.py parses test files correctly — ran python scripts/run_compliance_tests.py --dry-run, output shows all 18 test cases parsed` |
| **"This is the command to verify it"** | The speaker is providing the method for verification but has NOT executed it. The claim is NOT yet backed by evidence. | When documenting how verification should be done, or when providing instructions to another party. | `This is the command to verify it: python scripts/run_compliance_tests.py --model test — this will produce the compliance report` |

### Rules for Using the Distinction

1. **Never use "I verified this" unless you actually ran the verification.** Providing a command and assuming it works is not verification — it is instruction.
2. **When providing a verification command, always state clearly whether you have run it.** Use "This is the command to verify it" for unexecuted commands.
3. **When reviewing someone else's work, check which form they used.** If they said "This is the command to verify it" but the context implies the work is done, flag it as a fake success risk.
4. **In audit trails, only "I verified this" entries count as verification evidence.** "This is the command to verify it" entries are instructions, not evidence.

---

## Verification Status Flow

```
Created → [Verification method applied] → Verified
Created → [No verification applied] → Not verified
Created → [Verification attempted and failed] → Failed
Blocked → [Blocker resolved] → Pending (re-enter flow)
```

The default state for any newly created artifact is **Not verified**. The default state for any newly claimed assertion is **unverified**. Neither should be treated as "done" or "complete."

---

## Acceptance Criteria for Verification

An artifact is considered verified only when ALL of the following are true:

1. The appropriate verification method (from the table above) has been applied
2. Evidence has been collected and is available for inspection
3. The evidence confirms the artifact meets its requirements
4. No known failures or defects remain unaddressed
5. The verification status has been recorded in the continuity map

If any of these is false, the correct label is "Not verified" or "Failed" (if verification was attempted).

---

## Cross-References

- System prompt (NO FAKE SUCCESS RULE, EVIDENCE RULE): `prompts/SYSTEM_PROMPT.md`
- Refusal/blocker policy (blocking on failed tests): `policies/REFUSAL_BLOCKER_POLICY.md`
- Documentation truth requirements: `prompts/SYSTEM_PROMPT.md` (DOCUMENTATION TRUTH RULE)
- Hostile self-review: `checklists/HOSTILE_SELF_REVIEW.md`
- Compliance test runner (verification automation): `scripts/run_compliance_tests.py`
- Continuity map (recording verification status): `docs/operations/CONTINUITY_MAP.md`