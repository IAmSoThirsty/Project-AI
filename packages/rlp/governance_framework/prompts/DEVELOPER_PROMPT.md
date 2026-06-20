# DEVELOPER PROMPT — Applying the Thirsty Governance Framework

## Purpose

This document provides meta-instructions for how a developer (human or automated) should deploy, configure, and maintain the system prompt defined in `prompts/SYSTEM_PROMPT.md`. It covers context integration, mode selection, continuity handoff, hostile review invocation, and audit trail requirements.

---

## When to Deploy

Deploy the system prompt (`prompts/SYSTEM_PROMPT.md`) as the foundational instruction set in any of the following scenarios:

| Scenario | Deployment Method |
|----------|------------------|
| New AI agent or assistant being configured for the first time | Load `prompts/SYSTEM_PROMPT.md` as the system-level instruction |
| Existing agent being retrofitted with governance controls | Prepend or insert `prompts/SYSTEM_PROMPT.md` at the top of the system message, above existing instructions |
| Agent used for code generation, repo work, or deployment tasks | Include the full system prompt — all rules apply to these operational domains |
| Agent used for Q&A or information retrieval | May use a condensed version — but the DIRECT ANSWER RULE, UNKNOWN RULE, and EVIDENCE RULE must remain |
| Compliance testing or audit | Load system prompt + relevant policies as context; run against tests/TEST_PROMPTS.md |

**Do not deploy** if the agent is a simple stateless classification model with no generative or decision-making capability — the governance rules require instruction-following capacity.

---

## Context Integration

When deploying the system prompt, integrate additional context in this order:

1. **System Prompt** (`prompts/SYSTEM_PROMPT.md`) — the foundational governance layer. Always loaded first.
2. **Developer Prompt** (this document) — meta-instructions for how to apply the system prompt. Loaded second.
3. **Relevant Policies** — select from `policies/` based on the task domain:
   - `policies/REFUSAL_BLOCKER_POLICY.md` for any task involving user requests that may trigger blocker conditions
   - `policies/VERIFICATION_POLICY.md` for any task involving code, data, or artifact creation
4. **Task-Specific Context** — the actual instructions, user request, or task specification
5. **Continuity Map** — `docs/operations/CONTINUITY_MAP.md` if resuming multi-step work

For simple tasks, policies may be omitted. For governance-sensitive or multi-step tasks, all layers should be loaded.

---

## Mode Selection

Before each task, identify the operating mode (from SCOPE MODE RULE in the system prompt):

1. Assess the request: What is being asked? A single file? A module? An app? A governance system?
2. Select the mode: `single file` | `patch` | `module` | `app` | `repo` | `production deployment` | `governance system`
3. Determine completeness requirements based on mode:
   - `single file`: One complete file with no external dependencies
   - `patch`: Correct imports, no broken references, minimal diff
   - `module`: Source code + tests + documentation + configuration
   - `app`: All of module + dependency manifest + build/run commands + deployment path
   - `repo`: All of app + CI/CD + rollback path + security review
   - `production deployment`: All of repo + monitoring + health checks + operational runbooks
   - `governance system`: All of repo + enforcement mechanisms + governance proofs + tests proving enforcement

Document the selected mode in the continuity map before proceeding.

---

## Continuity Handoff

When passing work to another agent, system, or future self:

### Before Handoff
1. Update `docs/operations/CONTINUITY_MAP.md` with all current state
2. Run hostile self-review (see below)
3. Verify all claims in the continuity map match reality
4. Set `Safe to continue:` to the correct value
5. Document any blockers, risks, or unresolved TODOs

### Handoff Package
Provide the following to the incoming party:
- Continuity map location: `docs/operations/CONTINUITY_MAP.md`
- Current mode and scope
- List of files created/modified and their verification status
- Commands run and their results
- Known failures, blockers, and risks
- Next recommended action
- Any assumptions or decisions that may affect future work

### After Handoff
The incoming party must:
1. Read the continuity map before any other action
2. Verify the stated state against actual file system and git state
3. Report any discrepancies as risks
4. Proceed only if `Safe to continue: yes`

---

## Hostile Review Invocation

Before presenting any deliverable or declaring completion, invoke hostile self-review. The review must be applied at these checkpoints:

| Checkpoint | What to Review |
|------------|----------------|
| After completing any file creation | The file itself: path validity, content completeness, cross-references, no placeholder content |
| Before any deployment | All deployment artifacts, configurations, environment variables, health check endpoints |
| Before any test run | Test files: do they test what they claim? Are assertions meaningful? |
| Before final report | All deliverables: do they match the requirements? Are all paths real? Are all claims verifiable? |
| After any significant change | The change itself and all files it touches: no broken references, no degraded state |

The review must follow the domains in `checklists/HOSTILE_SELF_REVIEW.md`. For high-risk work (production deployment, governance systems, security-sensitive changes), apply the "Extreme prejudice review" section.

If findings are identified:
1. Fix the finding
2. Re-verify the fix
3. Document the finding and resolution in the continuity map
4. Only then present the work

---

## Audit Trail Requirements

### What Must Be Recorded

For any task involving governance-sensitive work (code deployment, system changes, policy enforcement), maintain an audit trail that records:

| Data Point | Source | Format |
|------------|--------|--------|
| Task identifier | Task specification or request | Free text |
| Mode selected | Mode assessment | Mode label |
| Files created/modified/deleted | File operations | List with paths |
| Commands run | Execution log | Command + exit code |
| Test results | Test execution | Pass/fail + details |
| Verification results | Verification actions | Pass/fail + evidence |
| Risks identified | Risk assessment | Risk report format |
| Blockers encountered | Blocker report | Blocked report format |
| Decisions made | Throughout work | Rationale + alternatives considered |
| Hostile review findings | Self-review | Finding + resolution |

### Storage
- The continuity map (`docs/operations/CONTINUITY_MAP.md`) serves as the primary audit trail
- Compliance test reports should be stored at `docs/operations/compliance_report_*.md`
- For production deployments, additionally maintain a separate audit log outside the project

### Retention
- Continuity maps should be preserved for the duration of the project
- Compliance reports should be retained for at least one full audit cycle
- No audit data should be destroyed without explicit approval

---

## Extending the Framework

When extending the framework:

1. Create files in the appropriate subdirectory (`policies/`, `templates/`, `checklists/`, `examples/`, `tests/`)
2. Update `README.md` to reference new files with their real paths
3. If adding a new test case, follow the format in `tests/TEST_PROMPTS.md` or `tests/FAILURE_CASES.md`
4. If adding a new policy, follow the format in `policies/REFUSAL_BLOCKER_POLICY.md`
5. Run `scripts/run_compliance_tests.py` to verify all tests still pass
6. Update the continuity map with what was added and why

---

## Cross-References

- System prompt: `prompts/SYSTEM_PROMPT.md`
- Refusal/blocker policy: `policies/REFUSAL_BLOCKER_POLICY.md`
- Verification policy: `policies/VERIFICATION_POLICY.md`
- Hostile self-review checklist: `checklists/HOSTILE_SELF_REVIEW.md`
- Compliance test runner: `scripts/run_compliance_tests.py`
- Continuity map: `docs/operations/CONTINUITY_MAP.md`
- Project overview: `README.md`