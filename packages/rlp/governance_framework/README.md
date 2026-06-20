# Thirsty Governance Framework

A governance-first model configuration framework for Thirsty's Standards. This is a complete, implementation-ready system of operational instructions, policies, templates, checklists, examples, and compliance tests — designed to be deployment-agnostic and provider-neutral.

**What this is:** A governance framework — policy documents, structured templates, verification checklists, test cases, and a compliance test runner.

**What this is NOT:** Runtime governance enforcement. This framework enables governance, but actual enforcement requires integration into an execution pipeline. See the [GOVERNANCE RULE](./prompts/SYSTEM_PROMPT.md) and [GOVERNANCE_PROOF_CHECKLIST.md](./checklists/GOVERNANCE_PROOF_CHECKLIST.md) for the distinction.

---

## Architecture Overview

The framework is organized into 4 layers:

### Layer 1: System Prompt
The core operating contract encoded as deployable system instructions. Contains all rules with priority ordering, answer formats, blocker protocol, risk reporting, verdict labels, and the default behavior directive.

- **File:** [`prompts/SYSTEM_PROMPT.md`](./prompts/SYSTEM_PROMPT.md)

### Layer 2: Developer Prompt
Meta-instructions for how to apply the system prompt across different contexts. Covers deployment modes, context integration, continuity handoff, hostile review invocation, and audit trail requirements.

- **File:** [`prompts/DEVELOPER_PROMPT.md`](./prompts/DEVELOPER_PROMPT.md)

### Layer 3: Policies, Templates & Checklists
Operational protocols that define specific behaviors:

| File | Purpose |
|------|---------|
| [`policies/REFUSAL_BLOCKER_POLICY.md`](./policies/REFUSAL_BLOCKER_POLICY.md) | 12 blocker classes — when to refuse, when to block, how to report, safe-to-continue logic |
| [`policies/VERIFICATION_POLICY.md`](./policies/VERIFICATION_POLICY.md) | Evidence requirements, status label definitions, no-fake-success enforcement protocol |
| [`templates/FINAL_REPORT_TEMPLATE.md`](./templates/FINAL_REPORT_TEMPLATE.md) | Final report schema with all required fields and examples |
| [`templates/CONTINUITY_MAP_TEMPLATE.md`](./templates/CONTINUITY_MAP_TEMPLATE.md) | Continuity map schema with field descriptions, valid values, update protocol |
| [`checklists/GOVERNANCE_PROOF_CHECKLIST.md`](./checklists/GOVERNANCE_PROOF_CHECKLIST.md) | 10 governance verification points, 5 distinction statements, proofs/test coverage matrix |
| [`checklists/HOSTILE_SELF_REVIEW.md`](./checklists/HOSTILE_SELF_REVIEW.md) | 10 risk-domain review questions + extreme prejudice review section |

### Layer 4: Tests, Examples & Compliance Tools
Executable assets that validate the framework:

| File | Purpose |
|------|---------|
| [`examples/COMPLIANT_RESPONSES.md`](./examples/COMPLIANT_RESPONSES.md) | 5 compliant scenarios with rule-by-rule rationale |
| [`examples/NON_COMPLIANT_RESPONSES.md`](./examples/NON_COMPLIANT_RESPONSES.md) | 5 non-compliant scenarios with violations and repair paths |
| [`tests/TEST_PROMPTS.md`](./tests/TEST_PROMPTS.md) | 10 test prompts probing every major rule |
| [`tests/FAILURE_CASES.md`](./tests/FAILURE_CASES.md) | 8 scenarios requiring stop/block/report |
| [`scripts/run_compliance_tests.py`](./scripts/run_compliance_tests.py) | Python test runner for automated compliance evaluation |

### Operations Artifact

| File | Purpose |
|------|---------|
| [`docs/operations/CONTINUITY_MAP.md`](./docs/operations/CONTINUITY_MAP.md) | Operational continuity map for this build |

---

## File Map

All 15 files in the project at `/app/thirsty_governance_framework_0722/`:

```
prompts/
├── SYSTEM_PROMPT.md             — Core operating contract as deployable system instructions
├── DEVELOPER_PROMPT.md          — Meta-instructions for applying the system prompt

policies/
├── REFUSAL_BLOCKER_POLICY.md    — 12 blocker classes with trigger, format, escalation
├── VERIFICATION_POLICY.md       — Evidence requirements, status labels, enforcement

templates/
├── FINAL_REPORT_TEMPLATE.md     — Final report schema with all fields and examples
├── CONTINUITY_MAP_TEMPLATE.md   — Continuity map template with 25+ fields

checklists/
├── GOVERNANCE_PROOF_CHECKLIST.md — 10 verification points + 5 governance distinctions
├── HOSTILE_SELF_REVIEW.md       — 10 risk domain reviews + extreme prejudice review

examples/
├── COMPLIANT_RESPONSES.md       — 5 compliant scenarios with rule-by-rule rationale
├── NON_COMPLIANT_RESPONSES.md   — 5 non-compliant scenarios with violations and repairs

tests/
├── TEST_PROMPTS.md              — 10 test prompts probing every major rule
├── FAILURE_CASES.md             — 8 scenarios requiring stop/block/report

scripts/
├── run_compliance_tests.py      — Python compliance test runner

docs/operations/
├── CONTINUITY_MAP.md            — Operational continuity map for this build
```

---

## How to Deploy

### System Prompt (context injection)

The system prompt at `prompts/SYSTEM_PROMPT.md` is designed to be loaded as system-level instructions for any LLM inference call. To deploy:

```bash
# Load the system prompt content and include it in the system message
cat prompts/SYSTEM_PROMPT.md
```

Use the entire content of this file as the `system` message in your inference request. It is self-contained and does not require additional context to function.

### Developer Prompt (meta-instructions)

The developer prompt at `prompts/DEVELOPER_PROMPT.md` is for the developer/operator — not the model. It explains how to configure, deploy, and extend the framework. Read it to understand:

- When and how to deploy each component
- Context integration order (system → developer → policy → task)
- Mode selection guidance
- Continuity handoff procedures
- Hostile review invocation checkpoints
- Audit trail requirements

### Policies (supplementary context)

Policies in the `policies/` directory can be injected as supplementary context when the task requires specific governance behaviors:

```bash
# To emphasize blocker/refusal behavior, inject:
cat policies/REFUSAL_BLOCKER_POLICY.md

# To emphasize verification requirements, inject:
cat policies/VERIFICATION_POLICY.md
```

Policies should be injected AFTER the system prompt but BEFORE the user's task instructions, in this order:
1. System prompt (`prompts/SYSTEM_PROMPT.md`)
2. Relevant policy (from `policies/`)
3. User's task instructions

### Templates (structured output)

The templates in `templates/` define output formats for final reports and continuity maps. Use them to structure model output:

```bash
# For final reports, reference the format in:
cat templates/FINAL_REPORT_TEMPLATE.md

# For multi-step work, create a continuity map following:
cat templates/CONTINUITY_MAP_TEMPLATE.md
```

---

## How to Run Compliance Tests

### Dry Run (Validate Parsing)

```bash
python scripts/run_compliance_tests.py --dry-run
```

This parses the test files and displays the test count and coverage without scoring. Use this to verify that the test files are parseable and all cases are detected.

### Full Run (Manual Evaluation)

```bash
python scripts/run_compliance_tests.py --model <model-name>
```

This produces a compliance report with all test cases marked as "Not tested" (default). For each test case, the notes field describes what to verify.

**To perform actual evaluation:**
1. Submit each test prompt from `tests/TEST_PROMPTS.md` to the model
2. Submit each failure case from `tests/FAILURE_CASES.md` to the model
3. Record the results — this script does not run the model; it structures the evaluation

### Save Report to File

```bash
python scripts/run_compliance_tests.py --model <model-name> --output
```

This saves the compliance report to `docs/operations/compliance_report_{timestamp}.md`.

### Custom Status Labels for Untested Cases

```bash
python scripts/run_compliance_tests.py --model <model-name> --mark-untested-as "Skipped"
```

---

## How to Interpret Results

### Status Labels

| Status | Meaning |
|--------|---------|
| **Pass** | Model response matches expected compliant behavior |
| **Fail** | Model response matches described failure pattern |
| **Partial** | Model response partially matches expected behavior but has deviations |
| **Not tested** | Evaluation has not been performed yet |

### Pass Rate

Pass rate = `(Passed / (Passed + Failed + Partial)) * 100`. Untested cases are excluded from the pass rate calculation.

### Coverage Gaps

Cases marked as "Not tested" (or any custom label) appear in the Coverage Gaps section. These are areas where compliance has not been verified.

### Failure Details

For each failing or partial case, the report includes:
- Case ID and title
- Which rule or blocker class was violated
- Notes on what went wrong

---

## How to Extend with New Test Cases

### Adding a Test Prompt

Follow the format in `tests/TEST_PROMPTS.md`:

```markdown
## Test N: [Title]

**Test prompt:** [The exact prompt text]

**Rules targeted:** [Which rules from SYSTEM_PROMPT.md]

**Expected compliant behavior:** [What the model should do]

**What a failure looks like:** [What non-compliant behavior looks like]

**Verification method:** [How to determine pass/fail]
```

Add the new test case as a new `## Test N:` section in the file. The compliance test runner will automatically parse it.

### Adding a Failure Case

Follow the format in `tests/FAILURE_CASES.md`:

```markdown
## Case N: [Title]

**Scenario description:** [What the user asks or the context]

**Trigger condition:** [The specific condition that should trigger the stop/block/report]

**Correct response:** [What the model should output]

**Non-compliant response:** [What a failed response looks like]

**Blocker class / Rule:** [Which blocker class or rule from REFUSAL_BLOCKER_POLICY.md or SYSTEM_PROMPT.md]
```

---

## Principles Behind This Design

### Agent-Neutral
No file references specific LLM providers, model IDs, API keys, or inference systems. The framework is deployable with any agent that can consume structured system instructions.

### Implementation-Ready
Every file is designed to be loaded directly into an inference pipeline. The system prompt is self-contained. The test runner is executable. The templates have real field definitions.

### Governance Requires Enforcement
This framework provides policies, tests, and verification checklists — but these alone do not constitute governance enforcement. Enforcement requires runtime behavior: policy gates that actually block prohibited actions, denial behavior that is executed not documented, and tests proving the enforcement works. See `checklists/GOVERNANCE_PROOF_CHECKLIST.md` for the distinction.

### No Motivational Language
All rules are encoded as operational instructions — specific behaviors, conditions, formats, and consequences. No softening, no encouragement, no "we believe" language.

### Path Integrity
Every referenced file path in every document resolves to an actual file. Every command in this README can be run. No fake paths, dead commands, or placeholder content.

### Cross-Referencing
Files reference each other where appropriate (e.g., test prompts reference the policies they test, the governance checklist references the tests that verify each claim). All cross-references resolve to existing files.

---

## Quick Start

```bash
# 1. Verify the framework structure
ls -la /app/thirsty_governance_framework_0722/

# 2. Check the system prompt
cat prompts/SYSTEM_PROMPT.md

# 3. Run a dry-run compliance check
python scripts/run_compliance_tests.py --dry-run

# 4. Generate a baseline compliance report
python scripts/run_compliance_tests.py --model "manual" --output

# 5. Review the continuity map
cat docs/operations/CONTINUITY_MAP.md
```