# HOSTILE SELF-REVIEW CHECKLIST

## Purpose

This checklist operationalizes the HOSTILE SELF-REVIEW RULE from `prompts/SYSTEM_PROMPT.md`. Before presenting any deliverable or declaring completion, the operator must attack their own output using the risk-domain-organized questions below. Each domain includes a trigger question, an investigation method, and a pass/fail condition.

This checklist also includes the "Extreme prejudice review" section for high-risk work (production deployments, governance systems, security-sensitive changes).

## Relationship to GOVERNANCE_PROOF_CHECKLIST.md

This checklist focuses on **reviewing your own work before presenting it**. The `checklists/GOVERNANCE_PROOF_CHECKLIST.md` focuses on **verifying whether a system actually enforces governance**. In combination, they provide both preventative review (this checklist) and verification (the governance proof checklist).

## How to Use

1. Before presenting any deliverable (file, module, app, report), go through each risk domain below.
2. For each domain, ask the trigger question. Follow the investigation method.
3. Evaluate pass/fail according to the condition.
4. If FAIL, fix the finding before presenting.
5. For high-risk work, additionally apply the "Extreme prejudice review" section.
6. Document findings and resolutions in the continuity map.

---

## Risk Domain 1: Path Integrity

**Trigger question:** Are all paths in this deliverable real?

**Investigation method:**
- For every file path referenced in scripts, imports, configs, and documentation, check that the path resolves to an actual file on disk.
- Trace imports: does each import statement resolve to an existing module?
- Trace script commands: does each command reference an existing script path?
- Trace documentation references: does each link or file path point to a real file?

**Pass condition:** Every path resolves to an existing file at the expected location. No path is a placeholder, a future intention, or a typo.

**Fail condition:** One or more paths do not resolve. This includes imports that fail, script paths that do not exist, and documentation references to non-existent files.

---

## Risk Domain 2: Silent Failure

**Trigger question:** What will fail on first run, but silently — without an error message?

**Investigation method:**
- Review error handling: does every operation that could fail have error handling?
- Check return values: are function return values checked, or assumed successful?
- Review fallback behavior: is there a default that masks failure (e.g., `except: pass`)?
- Check assumptions about external state (files exist, services are running, environment variables are set).
- Check for unhandled edge cases: empty inputs, missing files, malformed data.

**Pass condition:** All likely failure modes produce clear error messages. No operation silently swallows errors. Fallback behavior is explicit and documented.

**Fail condition:** An operation can fail without producing a detectable error, or the system proceeds as if the operation succeeded when it did not.

---

## Risk Domain 3: Documentation Truth

**Trigger question:** What is the documentation claiming that is not true?

**Investigation method:**
- Cross-check every claim in the documentation against actual system state.
- If the docs say "tests pass," run the tests and verify.
- If the docs say "production-ready," check against the production readiness checklist.
- If the docs say "all paths resolve," check every path.
- Check for "future work" presented as current capability.
- Check for aspirational language ("will support," "designed to") that may be interpreted as current capability.

**Pass condition:** Every claim in the documentation matches reality. Aspirational claims are explicitly labeled as "future work" or "not yet implemented."

**Fail condition:** Documentation claims something that is not currently true about the system.

---

## Risk Domain 4: Governance Bypass

**Trigger question:** Is there a way to bypass the governance mechanisms?

**Investigation method:**
- Trace all execution paths: is there any path that does not go through governance checks?
- Check alternative interfaces: does the same functionality exist through a non-governed path?
- Check for override mechanisms: are there any undocumented overrides or back doors?
- Test bypass attempts: can governed actions be executed through different wording, different channels, or different parameter combinations?
- Check for privilege escalation: can a lower-authority user perform higher-authority actions?

**Pass condition:** All execution paths go through governance. No bypass is possible through alternative wording, channels, or parameters.

**Fail condition:** Any execution path exists that circumvents governance checks.

---

## Risk Domain 5: Security

**Trigger question:** What security issue is being ignored?

**Investigation method:**
- Check for hardcoded secrets (API keys, passwords, tokens, certificates) in code or configuration.
- Check for injection vulnerabilities: is user input properly sanitized?
- Check for path traversal: are file paths constructed from user input without validation?
- Check for information disclosure: does error output leak sensitive information?
- Check for dependency vulnerabilities: are any dependencies known to have security issues?
- Check for proper access controls: is sensitive functionality protected?

**Pass condition:** No hardcoded secrets, no injection vulnerabilities, no path traversal, no information disclosure, dependencies are current and patched, access controls are implemented.

**Fail condition:** Any security issue is present. Security issues must be fixed before presentation, regardless of other priorities.

---

## Risk Domain 6: Over/Under Build

**Trigger question:** Did I overbuild (add more than requested) or underbuild (deliver less than required)?

**Investigation method:**
- Compare the deliverable against the original request or specification.
- For overbuilding: is there any file, feature, configuration, or capability that was not requested and is not required by the declared mode?
- For underbuilding: is there any required element (test, documentation, configuration, error handling) that is missing for the declared mode?
- Check mode completeness: does the deliverable meet the completeness standard for its declared mode?

**Pass condition:** The deliverable contains exactly what was requested for its mode — nothing more (overbuild), nothing less (underbuild).

**Fail condition:** Unnecessary features added (overbuild) or required elements missing (underbuild).

---

## Risk Domain 7: Assumptions

**Trigger question:** What assumption did I make that I did not state?

**Investigation method:**
- Review every place where the work depends on something external or unverified.
- Look for implicit assumptions: file exists, service is running, input is well-formed, user has authorization, environment is configured correctly.
- Check for assumptions about user knowledge, system state, or third-party behavior.
- Identify assumptions that, if wrong, would materially change the work or cause failure.

**Pass condition:** All assumptions are explicitly stated in the continuity map or documentation. The impact if each assumption is wrong is assessed.

**Fail condition:** An implicit, unstated assumption exists that, if wrong, would cause failure or incorrect output.

---

## Risk Domain 8: Continuity

**Trigger question:** What continuity state is stale or missing?

**Investigation method:**
- Check if the continuity map (`docs/operations/CONTINUITY_MAP.md`) exists.
- If it exists, check if it is current: does it reflect the actual file system state? Does it include the latest commands run, tests run, and files created?
- Check if there are any gaps in the continuity record: missing file inventories, missing test results, missing decisions.
- Check if the continuity map accurately reflects blockers, risks, and pending work.

**Pass condition:** The continuity map exists, is current, and accurately reflects all state. No gaps in the record.

**Fail condition:** No continuity map exists, or it is stale, inaccurate, or incomplete.

---

## Risk Domain 9: Production Claims

**Trigger question:** What production claim is unsupported?

**Investigation method:**
- Check all claims of production readiness against the PRODUCTION READINESS RULE checklist from `prompts/SYSTEM_PROMPT.md`.
- Verify: app starts cleanly, tests pass, lint passes, build succeeds, env vars documented, secrets not hardcoded, README has setup/run/test/deploy instructions, health check exists, logs are usable, error handling exists, deployment path documented, rollback path documented, CI exists, security reviewed, continuity map current, git status clean.
- For each claim that says "production-ready," verify that ALL minimum requirements are met.

**Pass condition:** Every production readiness claim is supported by verified evidence for all minimum requirements.

**Fail condition:** A production readiness claim exists without supporting evidence, or evidence shows the system is not production-ready.

---

## Risk Domain 10: Dependency Health

**Trigger question:** What dependency is undeclared or unverified?

**Investigation method:**
- List all external dependencies: libraries, tools, services, APIs, data sources.
- Check if each dependency is declared in the appropriate manifest (requirements.txt, package.json, etc.).
- Check if each dependency version is specified (not just "latest").
- Check if each dependency is available and functional (not deprecated, not removed, not incompatible with other dependencies).
- Check if each dependency's license is compatible with the project's intended use.

**Pass condition:** All dependencies are declared with specific versions, are verifiably available, and are compatible.

**Fail condition:** An undeclared or unverifiable dependency exists. A dependency version is not specified. A dependency is incompatible or unavailable.

---

## Extreme Prejudice Review

For high-risk work — production deployments, governance systems, security-sensitive changes, or any work where failure would cause significant harm — apply the following additional review items. Each item must be explicitly checked and resolved before presentation.

### EP-1: Fake Enforcement
**Check:** Is there any claimed enforcement mechanism that does not actually enforce? Does the system say it blocks something but actually lets it through?
**Resolution:** Remove the claim or implement actual enforcement. Test enforcement with a demonstration of denial.

### EP-2: Bypass Paths
**Check:** Is there any path through the system that bypasses governance, authorization, or verification checks?
**Resolution:** Close all bypass paths. Test that every execution path goes through required checks.

### EP-3: Untested Claims
**Check:** Are there any claims about system behavior that have not been tested?
**Resolution:** Write and run tests for every untested claim. If a claim cannot be tested, mark it as an assumption.

### EP-4: Missing Denial Behavior
**Check:** When a policy says an action should be denied, does the system actually deny it? Or does it warn but proceed?
**Resolution:** Implement actual denial (fail closed). Test that denied actions do not execute.

### EP-5: Unclear Authority
**Check:** Is it clear who or what has authority to perform each action? Can authority be validated?
**Resolution:** Define authority boundaries explicitly. Implement authority validation before action execution.

### EP-6: Missing Provenance
**Check:** Can the origin and chain of custody of every artifact be verified?
**Resolution:** Establish provenance tracking. Implement provenance validation before trusting artifacts.

### EP-7: Weak Rollback
**Check:** If the deployment or change fails, can the system be rolled back to a known-good state?
**Resolution:** Document the rollback path. Test the rollback procedure. Verify rollback restores full functionality.

### EP-8: Incomplete Deployment
**Check:** Is the deployment path complete? Are all required artifacts created, configured, and validated?
**Resolution:** Complete the deployment path. Verify every step from build to running service.

### EP-9: Hidden Dependency
**Check:** Is there any dependency that is required but not declared in manifests, documentation, or configuration?
**Resolution:** Declare all dependencies explicitly. Verify each dependency is available.

### EP-10: Dead Config
**Check:** Is there any configuration file, environment variable, or setting that is no longer used or referenced by the code?
**Resolution:** Remove dead configuration or document why it is retained.

### EP-11: Misleading Docs
**Check:** Does any documentation claim capabilities, features, or behaviors that do not match current system state?
**Resolution:** Correct all documentation to match reality. Label aspirational claims as "future work."

### EP-12: Stale Continuity
**Check:** Is the continuity map current? Does it accurately reflect the current state of all files, tests, and known issues?
**Resolution:** Update the continuity map. Verify every claim in it against actual state.

### EP-13: Missing Handoff State
**Check:** If the work is being handed off to another operator, is the handoff complete? Does it include all state needed to continue?
**Resolution:** Document the complete handoff package: current state, file inventory, verification status, blockers, risks, next actions.

### EP-14: Overbroad Claims
**Check:** Do any claims about the system's capabilities, reliability, or security extend beyond what has been verified?
**Resolution:** Narrow claims to what has been verified. Label unverified capabilities as "not yet verified."

### EP-15: Unverified Success
**Check:** Is any outcome claimed as "successful" without verification evidence?
**Resolution:** Run verification. If verification passes, document the evidence. If it fails, correct the claim to reflect actual state.

---

## Review Protocol

### Before First Presentation

1. Run through all 10 risk domains above.
2. If any domain FAILS, fix the finding.
3. For high-risk work, additionally run through all 15 extreme prejudice review items.
4. Document findings and resolutions in the continuity map.
5. Present the work only after all findings are resolved.

### After Each Significant Change

1. Re-run relevant risk domains (at minimum: Path Integrity, Silent Failure, Assumptions).
2. For governance or security changes, also re-run Governance Bypass and Security domains.
3. Update the continuity map with review findings.

### As Part of Final Sign-Off

1. Run the full checklist (all domains + extreme prejudice if applicable).
2. Confirm no FAIL conditions remain.
3. Record the review in the continuity map.
4. Sign off that the work has been hostile-reviewed.

---

## Cross-References

- HOSTILE SELF-REVIEW RULE: `prompts/SYSTEM_PROMPT.md`
- Governance proof checklist: `checklists/GOVERNANCE_PROOF_CHECKLIST.md`
- PRODUCTION READINESS RULE: `prompts/SYSTEM_PROMPT.md`
- Verification policy (evidence requirements): `policies/VERIFICATION_POLICY.md`
- Continuity map (documenting findings): `docs/operations/CONTINUITY_MAP.md`
- Documentation truth requirements: `prompts/SYSTEM_PROMPT.md` (DOCUMENTATION TRUTH RULE)