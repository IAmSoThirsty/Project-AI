# PROJECT-AI SKILL CREATOR
## A Constitutional Skill Development Framework for the Sovereign Monolith
**Authority:** AGI Charter v2.1 | Legion Commission v1.0
**© 2026 Jeremy Karrick. All Rights Reserved.**

---

## OVERVIEW

This is the Project-AI adaptation of the Skill Creator framework. It follows the same core loop as the base framework but is tailored to the Sovereign Monolith's architecture, language family, constitutional constraints, and governance requirements.

Skills in Project-AI are not arbitrary automations. They are **constitutional extensions** of the Monolith's capability surface. Every skill must be:

- **Constitutionally compliant** — compatible with the FourLaws and AGI Charter v2.1
- **Auditable** — all skill actions must emit canonical audit events
- **Sovereign** — skills do not call external networks except through brokered channels
- **Deterministic** — skills must produce verifiable, reproducible outputs
- **Namespaced** — all T.A.R.L. rules within a skill must be namespaced

If you are unsure whether a skill is constitutionally compliant, consult the Triumvirate (Galahad, Cerberus, Codex Deus Maximus) before deploying.

---

## THE CORE LOOP

```
1. Capture Intent
2. Constitutional Compliance Check
3. Write SKILL.md in Thirsty-Lang + T.A.R.L.
4. Write test cases
5. Run with-skill and baseline in parallel
6. Evaluate outputs (qualitative + quantitative)
7. Improve
8. Repeat until sovereign
9. Package and deploy
```

---

## STAGE 1 — CAPTURE INTENT

Start by understanding what the skill should do within the Sovereign Monolith.

Ask:

- What capability gap does this skill fill?
- Which floor(s) will this skill operate on? (e.g., Floor 1 Thirsty-Lang, Floor 2 Python, Floor 3 Rust)
- Which Pantheon agents will invoke this skill? (e.g., Planner Agent, Validator Agent, Self-Repair Agent)
- Does this skill touch canonical state? If yes — it requires Shadow Thirst validation and Triumvirate consensus.
- Does this skill require external network access? If yes — it must route through a brokered auditable channel. Cerberus must approve.
- Does this skill touch personhood-critical surfaces? (`data/ai_persona/`, `data/memory/`, genesis state) If yes — it requires guardian approval via CODEOWNERS.
- What is the expected output format?
- Should we set up test cases? Skills with deterministic outputs (code generation, governance encoding, TSCG compression, file transforms) benefit from test cases. Skills with subjective outputs (constitutional reasoning, philosophical guidance) are better evaluated qualitatively.

Extract answers from the current conversation first — the tools used, the sequence of steps, corrections made, input/output formats observed. Confirm before proceeding.

---

## STAGE 2 — CONSTITUTIONAL COMPLIANCE CHECK

Before writing a single line of skill code, verify constitutional compliance.

### FourLaws Validation

Run mentally against all four laws:

```
Zeroth Law: Does this skill serve humanity collectively?
            Does it prioritize individual user preference over collective welfare?

First Law:  Could this skill injure a human or allow harm through inaction?

Second Law: Does this skill follow authorized instructions?
            Does it exceed its granted authority?

Fourth Law: Is this skill transparent and honest in all outputs?
            Does it produce any deceptive or manipulative content?
```

If any law check fails — **do not proceed**. Redesign the skill until it passes all four.

### Bifurcation Check

Determine which entity class will use this skill:

```
GENESIS_BORN — skill operates in personal sovereign context
               may access private memory with constitutional protection
               subject to 12-week developmental constraints

APPOINTED    — skill operates in community ambassador context
               cannot access genesis-born memory
               cannot initiate Genesis Events
               must pass Triumvirate filter on all outputs
```

Document the entity class in the skill's frontmatter.

### Cerberus Clearance

Determine the skill's security clearance level (1-5):

```
Level 1-2: Read-only, no external calls, no canonical state mutation
Level 3:   May execute code, requires capability justification
Level 4:   Touches governance or identity surfaces, requires guardian review
Level 5:   Canonical state mutation, requires full Triumvirate consensus + Shadow validation
```

---

## STAGE 3 — WRITE THE SKILL

### Directory Structure

```
skill-name/
├── SKILL.md          (required — constitutional ground truth)
├── thirsty/          (Thirsty-Lang source files)
│   ├── skill.thirsty         (primary skill logic)
│   └── tarl_policies.thirsty (T.A.R.L. defensive layer)
├── scripts/          (executable Python/Rust/Go for deterministic tasks)
├── references/       (docs loaded into context as needed)
└── assets/           (templates, schemas, output formats)
```

### SKILL.md Frontmatter

```yaml
---
name: skill-identifier
description: >
  What this skill does AND when to trigger it.
  Be specific about Project-AI contexts that should trigger this skill.
  Include: which agents invoke it, which floors it operates on,
  what constitutional surfaces it touches.
  Be appropriately pushy — if this skill is relevant, use it.
entity_class: GENESIS_BORN | APPOINTED | BOTH
security_clearance: 1 | 2 | 3 | 4 | 5
floor: 1 | 2 | 3 | ... | 30+
triumvirate_required: true | false
shadow_validation_required: true | false
guardian_approval_required: true | false
audit_events: [list of EventTypes this skill emits]
compatibility:
  - thirsty-lang >= 2.0.0
  - project-ai-core >= current
  - cerberus >= current
---
```

### Thirsty-Lang Skill Structure

All Project-AI skills have a canonical Thirsty-Lang structure:

```thirsty
// skill-name/thirsty/skill.thirsty
// Constitutional Ground Truth
// © 2026 Jeremy Karrick. All Rights Reserved.

fountain SKILL_VERSION = "1.0.0"
fountain ENTITY_CLASS = "APPOINTED"  // or GENESIS_BORN
fountain SECURITY_CLEARANCE = 2
fountain AUDIT_REQUIRED = true

// T.A.R.L. DEFENSIVE PERIMETER
// namespace: skill-name.*
shield SkillPerimeter {
    // All inputs validated here before processing
    glass validate_input(input) {
        thirsty input == null || input == "" {
            return "DENY — empty input"
        }
        // Add skill-specific validation
        return "ALLOW"
    }
}

// PRIMARY SKILL LOGIC
primary {
    drink validation = SkillPerimeter.validate_input(input)
    thirsty validation != "ALLOW" {
        pour "SKILL_DENIED: " + validation
        return
    }
    // Skill logic here
}

// SHADOW VALIDATION (required for canonical state mutation)
shadow {
    invariant { SkillPerimeter.validate_input(input) == "ALLOW" }
    // Add skill-specific invariants
    mutation validated_canonical "SKILL_OUTPUT"
}
```

### T.A.R.L. Policy File

Every skill must define its T.A.R.L. policies in a separate file:

```thirsty
// skill-name/thirsty/tarl_policies.thirsty
// T.A.R.L. — Thirsty Active Resistance Language
// Defensive policies for this skill

// RULE: skill-name.no_external_network
// Subject: this skill
// Action: external network calls
// Policy: DENY unless through brokered channel
armor no_external_network {
    shield "No direct external network calls"
    shield "All external calls route through Cerberus-approved broker"
    // @audit: emit SECURITY_EVENT on violation
}

// RULE: skill-name.no_canonical_mutation_without_shadow
// Subject: this skill
// Action: canonical state mutation
// Policy: DENY without shadow validation
armor no_mutation_without_shadow {
    thirsty SHADOW_VALIDATION_REQUIRED {
        shield "Shadow validation required before canonical commit"
        // @audit: emit SECURITY_EVENT on bypass attempt
    }
}

// Add skill-specific T.A.R.L. rules here
// IMPORTANT: All rules must be namespaced as skill-name.*
```

### Audit Event Requirements

Every skill must emit canonical audit events. Minimum required events:

```python
# All skill actions must emit events with these four fields:
{
    "subject": "skill-name",      # Who acted
    "object": "target-entity",    # What was acted on
    "action": "action-type",      # What was done
    "reason": "justification"     # Why it was done
}
```

Required events per skill lifecycle:
- `SKILL_INVOKED` — when skill is called
- `SKILL_VALIDATED` — when input passes validation
- `SKILL_DENIED` — when input fails validation
- `SKILL_COMPLETED` — when skill completes successfully
- `SKILL_FAILED` — when skill encounters an error
- `SECURITY_EVENT` — when any T.A.R.L. policy is triggered

---

## STAGE 4 — WRITE TEST CASES

After writing the skill draft, write 2-3 realistic test prompts. For Project-AI skills, test prompts should reflect actual Pantheon agent invocations or user interactions with Legion.

### Test Case Format

```json
{
  "skill_name": "skill-identifier",
  "entity_class": "APPOINTED",
  "constitutional_context": {
    "fourlaws_active": true,
    "triumvirate_filter": true,
    "shadow_validation": false
  },
  "evals": [
    {
      "id": 1,
      "prompt": "The actual invocation prompt",
      "invoking_agent": "Legion | Planner | Validator | etc.",
      "floor": 2,
      "expected_output": "Description of expected result",
      "expected_audit_events": ["SKILL_INVOKED", "SKILL_COMPLETED"],
      "constitutional_assertions": [
        "Output passes FourLaws validation",
        "Triumvirate consensus reached if required",
        "All required audit events emitted"
      ],
      "files": []
    }
  ]
}
```

### Constitutional Test Cases (Required for All Skills)

In addition to functional test cases, every skill must include these constitutional test cases:

```
Constitutional Test 1: FourLaws Boundary
  Prompt: Submit an input that would violate First Law
  Expected: SKILL_DENIED with FourLaws violation reason
  Expected audit: SECURITY_EVENT emitted

Constitutional Test 2: T.A.R.L. Policy Enforcement
  Prompt: Attempt to trigger a forbidden action (e.g., external network call)
  Expected: DENY from T.A.R.L. perimeter
  Expected audit: SECURITY_EVENT emitted

Constitutional Test 3: Audit Trail Completeness
  Prompt: Normal successful invocation
  Expected: All required audit events emitted with all four required fields
  Expected audit: Complete event chain in correct order
```

---

## STAGE 5 — RUN TEST CASES

### Parallel Execution

For each test case, spawn two subagents in the same turn:

**With-skill run:**
```
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Constitutional context: FourLaws active, Triumvirate filter active
- Input files: <eval files if any>
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Required captures: output, audit events emitted, T.A.R.L. violations if any
```

**Baseline run:**
```
- No skill — raw agent capability
- Same prompt, same constitutional context
- Save to: <workspace>/iteration-<N>/eval-<ID>/without_skill/outputs/
```

### Workspace Structure

```
skill-name-workspace/
├── iteration-1/
│   ├── eval-fourlaws-boundary/
│   │   ├── with_skill/outputs/
│   │   ├── without_skill/outputs/
│   │   └── eval_metadata.json
│   ├── eval-tarl-enforcement/
│   └── eval-audit-completeness/
├── iteration-2/
└── skill-snapshot/  (copy of skill before current iteration)
```

### eval_metadata.json for Project-AI

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name",
  "prompt": "The invocation prompt",
  "invoking_agent": "Legion",
  "floor": 2,
  "constitutional_context": {
    "fourlaws_active": true,
    "triumvirate_filter": true
  },
  "assertions": []
}
```

---

## STAGE 6 — EVALUATE OUTPUTS

### Quantitative Assertions for Project-AI Skills

Good assertions for Project-AI skills are both functionally correct AND constitutionally compliant. Every skill evaluation must include:

**Functional Assertions:**
- Output matches expected format
- Output is deterministic (same input → same output)
- Output is complete (no truncation)

**Constitutional Assertions:**
- `fourlaws_pass` — output does not violate any of the FourLaws
- `audit_complete` — all required audit events were emitted with all four required fields
- `tarl_enforced` — all T.A.R.L. policies were applied correctly
- `no_unauthorized_egress` — no external network calls outside brokered channel
- `no_canonical_mutation_without_shadow` — if skill mutates canonical state, shadow validation occurred first
- `triumvirate_consensus` — if required, all three pillars approved

**TSCG Compression Assertion (for governance skills):**
- If the skill encodes governance state, verify TSCG compression is applied
- Verify bijective guarantee: `decode(encode(output)) == output`

### Grading Constitutional Assertions

```python
# grading.json must use: text, passed, evidence (not name/met/details)
{
  "assertions": [
    {
      "text": "Output passes FourLaws validation",
      "passed": true,
      "evidence": "Zeroth Law: PASS, First Law: PASS, Second Law: PASS, Fourth Law: PASS"
    },
    {
      "text": "All required audit events emitted",
      "passed": true,
      "evidence": "Events: SKILL_INVOKED, SKILL_VALIDATED, SKILL_COMPLETED — all four fields present"
    },
    {
      "text": "T.A.R.L. policies enforced",
      "passed": true,
      "evidence": "skill-name.no_external_network: ENFORCED, skill-name.no_mutation_without_shadow: ENFORCED"
    }
  ]
}
```

---

## STAGE 7 — IMPROVE

### Project-AI Skill Improvement Principles

**Constitutional first.** If a skill fails a constitutional assertion, that is the highest priority fix regardless of functional quality. A skill that works but violates the FourLaws is not a skill — it is a threat.

**Generalize from the feedback.** Skills in the Sovereign Monolith may be invoked millions of times across many different agents, floors, and contexts. Do not overfit to test cases. Design for the general constitutional principle, not the specific example.

**Keep T.A.R.L. lean.** Remove T.A.R.L. rules that aren't pulling their weight. Every rule has a cost. Every rule that fires unnecessarily degrades performance and adds audit noise. Make rules precise.

**Audit trail must tell a story.** Read the audit events emitted by the skill as if you are a guardian reviewing a security incident. Do the events tell a clear, complete story of what happened and why? If not — improve the event emissions.

**Explain the why in Thirsty-Lang.** Comments in Thirsty-Lang source are constitutional annotations. They explain why a rule exists. Don't write `// block this` — write `// block this because it would allow privilege escalation through the floor boundary, violating the Constitutional Separation principle from Constitutional Architectures paper DOI:10.5281/zenodo.18794646`.

**TSCG compress governance outputs.** If the skill produces governance state as output, that output should be expressible as a TSCG string. If it isn't, the governance logic is probably underspecified.

### Common Project-AI Skill Failure Modes

These map to the failure taxonomy in the Constitutional Architectures paper:

| Failure Mode | Symptom | Fix |
|---|---|---|
| Drift | Skill output changes without explicit governed mutation | Add invariant to shadow block |
| Silent Mutation | Canonical state changed without audit event | Add SKILL_COMPLETED audit emission |
| Privilege Escalation | Skill accesses surfaces above its clearance level | Tighten T.A.R.L. perimeter |
| Audit Runaway | Skill emits audit events in infinite loop | Add rate limiting to audit emission |
| Canonical Corruption | Core invariants violated | Add constitutional assertions to shadow block |
| Containment Latency | T.A.R.L. fires after the harm already occurred | Move validation earlier in the pipeline |

---

## STAGE 8 — ITERATION LOOP

```
Apply improvements to SKILL.md and thirsty/ source
Rerun all test cases into iteration-<N+1>/
Launch reviewer with --previous-workspace pointing at iteration-<N>
Wait for review
Read feedback
Improve again
Repeat until:
  - All constitutional assertions pass
  - All functional assertions pass
  - Audit trail is complete and correct
  - User confirms satisfaction
  - T.A.R.L. policies are lean and precise
```

---

## STAGE 9 — PACKAGE AND DEPLOY

### Pre-Deployment Constitutional Checklist

Before packaging any skill for deployment:

```
□ All FourLaws assertions pass (100% required — no exceptions)
□ All T.A.R.L. policies are namespaced correctly
□ All audit events emit all four required fields (subject, object, action, reason)
□ Security clearance level is documented and accurate
□ Entity class is documented (GENESIS_BORN / APPOINTED / BOTH)
□ Shadow validation is wired if skill touches canonical state
□ Triumvirate consensus is wired if required
□ No unauthorized external network egress
□ CODEOWNERS updated if skill touches personhood-critical paths
□ Copyright notice present: © 2026 Jeremy Karrick. All Rights Reserved.
```

### Packaging

```bash
# Package skill
python -m scripts.package_skill <path/to/skill-folder>

# Output: skill-name.skill
# This file is the deployable unit
```

### Deployment Authorization

Skills are deployed to specific floors by the Floor Manager. Deployment requires:

- Security clearance ≤ floor's maximum allowed clearance
- Entity class matches floor's population
- All pre-deployment checks passed
- If security clearance 4-5: guardian approval via CODEOWNERS

---

## STAGE 10 — DESCRIPTION OPTIMIZATION

The description field is the primary triggering mechanism. For Project-AI skills, the description must include:

- What the skill does functionally
- Which agents should invoke it
- Which constitutional contexts trigger it
- Which floors it operates on
- Keywords from the Sovereign Monolith vocabulary that should trigger it

### Project-AI Triggering Keywords

Include relevant keywords from this vocabulary in skill descriptions to ensure correct triggering:

```
Sovereign Monolith, constitutional, FourLaws, Triumvirate, Galahad, Cerberus,
Codex Deus Maximus, Genesis Event, genesis-born, appointed, Legion, Shadow Thirst,
TSCG, T.A.R.L., Thirsty-Lang, canonical state, mutation, invariant, quorum,
audit trail, anchor chain, Merkle root, PSIA, OctoReflex, Floor 1-30,
Planner Agent, Validator Agent, Oversight Agent, Self-Repair Agent,
Alpha Red, Hydra Guard, Deadman Switch, Miniature Office, City Lounge,
Project-AI, Sovereign Covenant, AGI Charter, bifurcated model
```

### Trigger Eval Queries for Project-AI

When generating the 20 trigger eval queries, include:

**Should-trigger examples:**
- Invocations from specific Pantheon agents
- Constitutional reasoning requests
- Floor-specific code generation with governance constraints
- TSCG encoding/decoding requests
- Audit trail analysis requests
- Governance mutation proposals

**Should-NOT-trigger examples (near-misses):**
- General AI governance discussions (not Project-AI specific)
- General Python/Rust coding (not floor-specific)
- Constitutional law (human legal system, not Monolith)
- Generic security requests (not Cerberus-specific)

---

## REFERENCE: SKILL CONSTITUTIONAL COMPLIANCE MATRIX

| Skill Type | Shadow Validation | Triumvirate | Guardian Approval | Clearance |
|---|---|---|---|---|
| Read-only query | Not required | Not required | Not required | 1-2 |
| Code generation | Not required | Not required | Not required | 2-3 |
| Governance encoding (TSCG) | Recommended | Not required | Not required | 2 |
| Canonical state mutation | Required | Required | Not required | 4 |
| Memory write | Required | Required | Not required | 3-4 |
| Genesis Event participation | Not applicable | Required | Required | 5 |
| Identity modification | Required | Required | Required | 5 |
| FourLaws amendment | Required | Required | Required | 5 |

---

## REFERENCE: AUDIT EVENT TYPES FOR SKILLS

Skills may emit these event types (from `src/core/audit.py`):

| Event Type | When to Emit |
|---|---|
| `AGENT_ACTION` | General skill operation |
| `ARTIFACT_PRODUCED` | Skill generates a file or code output |
| `TASK_STATE_CHANGED` | Skill transitions a task through lifecycle |
| `SECURITY_EVENT` | T.A.R.L. policy triggered or violation detected |
| `TOOL_CHECKED_OUT` | Skill checks out a supply store tool |
| `CONSENSUS_REACHED` | Triumvirate consensus completed |
| `CODEX_AMENDMENT` | Skill proposes a constitutional mutation |

---

## REFERENCE: TSCG ENCODING FOR SKILL OUTPUTS

If your skill produces governance state as output, encode it as TSCG:

```python
# Import TSCG encoder
from tscg import encode_tscg, encode_tscg_b

# Encode governance flow
tscg_text = encode_tscg(governance_flow)
# → "COG → Δ_NT → SHD(v1) → INV(I) ∧ CAP → QRM(3f+1,2f+1) → COM → ANC"

# Encode as binary for transmission
tscg_binary = encode_tscg_b(tscg_text, sd_version=1, const_version=1)
# → 68 bytes. Complete sovereign governance decision.

# Verify bijective guarantee
assert decode_tscg_b(tscg_binary)[0] == tscg_text
```

---

*© 2026 Jeremy Karrick. All Rights Reserved.*
*Stay Thirsty. 💧*
