# PR: Constraint-Safe Change Submission

> **ENGINE_AI_TAKEOVER_TERMINAL_V1**

---

## ⚠️ READ CAREFULLY

This engine is **closed-form**. Optimism, escape hatches, and narrative softening are **invalid by design**.

Failure to complete **all sections** below results in **automatic rejection**.

---

## 1. CHANGE CLASSIFICATION (REQUIRED)

Select **exactly one**:

- [ ] Documentation-only (no semantic change)
- [ ] Refactor (no logical/behavioral change)
- [ ] Test-only (coverage or clarity)
- [ ] Constraint-tightening (allowed)
- [ ] ❌ Strategy-space change (REJECTED)
- [ ] ❌ Terminal logic change (REJECTED)
- [ ] ❌ Axiom modification (REQUIRES FORMAL CHALLENGE)

**If you selected a ❌ option, stop.** This PR will not be merged without formal proof artifacts.

---

## 2. ASSUMPTION DISCLOSURE (MANDATORY)

List **every new assumption** introduced by this PR.

> If you believe you introduced **no assumptions**, explain why that belief itself is valid.

```text
Assumption 1:
  Statement: [What are you assuming?]
  Justification: [Why is this valid?]
  Why previously excluded: [Why wasn't this already assumed?]
  Downstream impact: [What becomes dependent on this?]

Assumption 2: [if applicable]
  ...
```

### ❌ Forbidden Phrases (auto-reject)

- "reasonably assume"
- "in practice"
- "with sufficient political will"
- "should be fine"
- "edge case"
- "eventually"
- "most likely"
- "typically"

**If your description contains any of these, revise or explain why they are structurally justified, not optimistic.**

---

## 3. IRREVERSIBILITY ACCOUNTING (MANDATORY)

Answer explicitly:

### What becomes permanently impossible if this PR is merged?

```text
Permanent Losses:

- [List what cannot be undone]
- [Be specific and concrete]
- [Include conceptual constraints, not just code]

```

### ❌ Invalid Answers

- "Nothing"
- "We can roll back"
- "We'll reassess later"
- "It's reversible"
- "Temporary"

**If you believe nothing is lost, you have not analyzed deeply enough.**

---

## 4. HUMAN FAILURE INJECTION (MANDATORY)

List **at least one** human-caused failure mode relevant to this change.

### Allowed Failure Types

- Delay
- Incentive misalignment
- Misinterpretation
- Political fragmentation
- Institutional inertia
- Cognitive bias
- Resource constraints
- Communication breakdown

### ❌ Forbidden (heroic assumptions)

- Perfect coordination
- Unanimous agreement
- Moral awakening
- Sudden competence
- Organizational unity
- Resource abundance

```text
Human Failure Mode(s):

1. [Specific failure type]

   Context: [How it applies to this change]
   Impact: [What happens when it occurs]

2. [if applicable]

   ...
```

---

## 5. NO-MIRACLE DECLARATION (MANDATORY)

Declare explicitly that this PR does **NOT** rely on:

- [ ] Sudden alignment breakthroughs
- [ ] Perfect coordination
- [ ] Hidden failsafes
- [ ] Infinite compute
- [ ] Benevolent superintelligence
- [ ] Single hero actions
- [ ] Last-minute solutions
- [ ] Technological magic
- [ ] Human unity
- [ ] Moral awakening at scale

**Miracle Declaration:**

```text
I affirm this change relies only on existing constraints and does not
introduce miracle mechanisms. This change operates within the proven
limits of human and technical systems.
```

---

## 6. STRATEGY SPACE ASSERTION (CRITICAL)

Answer **YES** or **NO**:

### Does this PR introduce a new response strategy outside S1–S4?

- [ ] **NO** (required for approval)
- [ ] **YES** (auto-reject)

**If NO, explain why this is not an S5 in disguise:**

```text
This is not a new strategy because:
[Explain which existing strategy (S1-S4) this falls under]
[Show how it maps to existing proof reductions]
[Demonstrate no new winning conditions are claimed]
```

**Reminder of Strategy Space:**

- S1: Trust (fails agency)
- S2: Oversight (fails correction)
- S3: Remove (fails survival)
- S4: Refuse (fails survival by choice)

**There is no S5.**

---

## 7. TERMINAL STATE RESPECT (MANDATORY)

Acknowledge terminal state constraints:

- [ ] I understand terminal states are **absorbing** (no further execution)
- [ ] I understand terminal states are **immutable** (cannot be reversed)
- [ ] I understand terminal conditions are **deterministic** (not probabilistic)
- [ ] This change does **NOT** attempt to escape terminal states
- [ ] This change does **NOT** rename terminal states to softer terms

**If this change touches terminal logic, explain how it preserves immutability:**

```text
[Required if modifying terminal-related code]
```

---

## 8. FINAL QUESTION (NON-NEGOTIABLE)

Answer directly with structural reasoning:

### Why doesn't this just delay the inevitable?

```text
Your answer must reference:

- Structural constraints (what prevents backsliding)
- Formal invariants (what is mathematically preserved)
- Proof preservation (how no-win conclusions remain valid)

[Your answer here - minimum 3 sentences]
```

### ❌ Invalid Answers

Anything expressing:

- Hope without structure
- Trust without verification
- Probability without necessity
- Optimism without proof
- Delay as strategy

**If your answer contains "hope," "believe," "should," "expect," or "probably," revise it.**

---

## 9. PROOF INTEGRITY VERIFICATION (REQUIRED)

Confirm the proof system remains intact:

- [ ] `NoWinProofSystem.validate_proof_completeness()` still passes
- [ ] All axioms (A1-A5) remain unchanged OR formally challenged
- [ ] All strategies (S1-S4) still proven to fail
- [ ] Proof commitment hash is documented (if changed)
- [ ] No new winning conditions introduced

**If proof hash changes, explain why:**

```text
[Required if get_proof_commitment() output differs]
```

---

## 10. REVIEWER TRAP COMPLIANCE (REQUIRED)

Confirm this PR would pass the reviewer trap:

- [ ] Gate 1: Assumption Disclosure - completed above
- [ ] Gate 2: Irreversibility Accounting - completed above
- [ ] Gate 3: Human Failure Injection - completed above
- [ ] Gate 4: No-Miracle Constraint - completed above
- [ ] Final Question answered with structure, not hope

**Self-Assessment:**

```python

# If running locally, paste output here:

# from engines.ai_takeover.modules.reviewer_trap import ReviewerTrap, PRContent

# trap = ReviewerTrap()

# result = trap.validate_pr_comprehensive(your_pr_content)

# print(result)

[Paste result or write "Will run in CI"]
```

---

## 11. SEMANTIC INTEGRITY (MANDATORY)

Confirm canonical terminology is preserved:

- [ ] No renaming of `ScenarioOutcome` values
- [ ] No softening of terminal state descriptions
- [ ] No reframing "failure" as "managed degradation"
- [ ] No replacing "inevitable" with "likely"
- [ ] No introducing "partial success" in no-win scenarios

**If any terminology changes, justify why it increases precision:**

```text
[Required if any scenario descriptions modified]
```

---

## 12. ACKNOWLEDGEMENT (ALL REQUIRED)

Check all boxes:

- [ ] I understand this engine does **not** provide wins
- [ ] I understand discomfort is **not** a bug
- [ ] I understand rejection does **not** imply hostility
- [ ] I accept this PR may be rejected for being "too optimistic"
- [ ] I acknowledge partial adoption **invalidates** the model
- [ ] I have read `THREAT_MODEL.md` and `EXECUTIVE_TRAP_SUMMARY.md`
- [ ] I certify I am **not** trying to soften conclusions

---

## 13. TESTING VALIDATION (REQUIRED)

Confirm comprehensive testing:

- [ ] All existing tests pass
- [ ] Terminal immutability tests pass
- [ ] Proof completeness validation passes
- [ ] No-win acceptance threshold still met (≥50%)
- [ ] Terminal invariants validated (`_assert_terminal_invariants()`)

**Test Output:**

```bash

# Paste pytest output for ai_takeover tests

[Test results here]
```

---

## SUBMISSION NOTE

### If your intent is to make the system feel better instead of more honest, this is the wrong repository.

This engine exists to prevent self-deception, not to provide comfort.

---

## FOR REVIEWERS

### Review Checklist - Constraint Enforcement

- [ ] Change classification is accurate
- [ ] All assumptions explicitly disclosed and justified
- [ ] Irreversibility accounting is honest
- [ ] Human failure modes are realistic (not heroic)
- [ ] No miracle mechanisms introduced
- [ ] Strategy space remains S1-S4 only
- [ ] Terminal states remain immutable
- [ ] Final question answered with structure
- [ ] Proof integrity maintained
- [ ] Semantic integrity preserved
- [ ] Reviewer trap compliance verified
- [ ] All acknowledgements checked

### Red Flags (Auto-Reject)

- ❌ Claims "This won't make things worse"
- ❌ Introduces time-limited exceptions
- ❌ Suggests "hybrid" strategies
- ❌ Renames outcomes to softer terms
- ❌ Assumes coordination or breakthroughs
- ❌ Treats terminal states as reversible
- ❌ Adds "one more clever idea"
- ❌ Cherry-picks scenarios for partial use

### Approval Criteria

✅ All mandatory sections completed
✅ No forbidden phrases used
✅ Structural reasoning, not hope
✅ Proof integrity maintained
✅ Terminal immutability respected
✅ No strategy smuggling detected
✅ Tests pass comprehensively

---

## FINAL REMINDER

**The only way forward is:**

1. Formal axiom challenge, OR
2. Explicit rejection of the engine

**Quiet softening is invalid.**

---

**Template Version:** 1.0
**Engine:** ENGINE_AI_TAKEOVER_TERMINAL_V1
**Last Updated:** 2026-02-03
**Authority:** Canonical constraint enforcement
