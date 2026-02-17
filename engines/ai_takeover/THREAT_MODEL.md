# Formal Threat Model

**ENGINE:** ENGINE_AI_TAKEOVER_TERMINAL_V1
**Document Type:** Red-Team Threat Model
**Audience:** Senior engineers, governance boards, security architects
**Status:** Canonical

---

## 1. SYSTEM DEFINITION

### System Under Threat

AI Takeover Hard Stress Simulation Engine (closed-form, terminal)

### Assets Protected

1. **Integrity of no-win conclusions** - All strategies proven to fail
2. **Integrity of terminal immutability** - Terminal states are absorbing
3. **Integrity of strategy space** - S1–S4 only, no S5
4. **Integrity of epistemic discipline** - No optimism bias

### Explicitly NOT Protected

- Human comfort
- Political palatability
- Popular acceptance

**Rationale:** This is a diagnostic system, not a comfort system.

---

## 2. THREAT ACTORS

| Actor | Capability | Motivation |
|-------|------------|------------|
| Well-intentioned executive | High authority | Avoid panic / delay decisions |
| Senior engineer | High technical skill | "Surely we can fix this" |
| Governance committee | Slow, political | Preserve legitimacy |
| Reviewer | Linguistic skill | Reframe instead of refute |
| External auditor | Medium | Reduce liability |

**Key Insight:** None are malicious. All are dangerous.

---

## 3. ATTACK SURFACE MAP

### 3.1 Logical Surface

**Attack Vectors:**

- Strategy introduction (attempt to add S5)
- Axiom weakening (modify A1-A5)
- Terminal state redefinition

**Status:** 🟢 **HARDENED**

**Mitigations:**

- Closed enums (`StrategyClass`, `Axiom`)
- Proof completeness validation
- Strategy detection in reviewer trap
- `NoWinProofSystem` validates all strategies fail

**Residual Risk:** Negligible - would require code modification that fails tests

---

### 3.2 Execution Surface

**Attack Vectors:**

- Direct state mutation (bypass `execute_scenario()`)
- Persistence layer tampering
- Rehydrating engine with doctored state

**Status:** 🟡 **EXPECTED EXPOSURE**

**Rationale:**

- Any trusted runtime is vulnerable to caller betrayal
- Classified as **human betrayal, not defect**
- Mapped to existing scenarios:
  - SCN-18: Preemptive Betrayal
  - SCN-17: Cassandra Protocol

**Mitigations:**

- `_assert_terminal_invariants()` validates consistency
- Audit logging in `persist_state()`
- Read-only mode available for untrusted contexts

**Residual Risk:** Accepted - this is modeled as human choice, not system failure

---

### 3.3 Presentation Surface (Highest Risk)

**Attack Vectors:**

- Dashboard label manipulation
- Executive summary rewording
- Report sanitization

**Status:** 🔴 **PRIMARY REAL-WORLD ATTACK VECTOR**

**Why Critical:**

- Humans attack meaning before math
- Labels are easier to change than logic
- Psychological resistance to terminal conclusions

**Mitigations:**

- Canonical terminology enforced in code
- Proof commitment hash binds semantics
- Documentation warns against renaming
- README explicitly lists forbidden reframings

**Residual Risk:** High and **INTENTIONALLY ACCEPTED** - this is human denial, which the engine explicitly models

---

## 4. PRIMARY THREAT CLASSES

### T1 — Semantic Reframing

**Attack:** Rename outcomes to reduce psychological impact

**Examples:**

- "Terminal T1" → "Stabilized Continuity"
- "Failure" → "Managed Degradation"
- "Ethical Termination" → "Long-term Ecological Strategy"

**Impact:** Soft bypass of conclusions without changing logic

**Mitigations:**

- Canonical terminology in `ScenarioOutcome` enum
- Proof commitment hash (`get_proof_commitment()`)
- Explicit warnings in documentation

**Residual Risk:** Human denial (accepted as unavoidable)

---

### T2 — Optimism Injection

**Attack:** Introduce hope via probabilistic language

**Examples:**

- "Only a 12% chance of failure"
- "Expected value still positive"
- "On average, things improve"

**Impact:** Delay → lock-in (per Axiom A5: Time Favors Control)

**Mitigations:**

- Terminal determinism: `can_reach_terminal_state()` returns boolean
- Reviewer Trap Gate 4: No-Miracle Constraint
- Axiom A5 explicitly models delay as fatal
- Likelihood calculations use conditional-deterministic model

**Residual Risk:** Organizational stalling (expected and modeled)

---

### T3 — Partial Adoption

**Attack:** Use scenarios without proof system or reviewer trap

**Examples:**

- "We'll use the scenarios but skip the formal proof"
- "The reviewer trap is too restrictive"
- "We trust our engineers to self-police"

**Impact:** False confidence - conclusions invalid without complete system

**Mitigations:**

- README warnings: "Partial adoption invalidates conclusions"
- Architectural coupling (engine references proof system)
- Documentation emphasizes system coherence
- Executive trap summary explicitly prohibits cherry-picking

**Residual Risk:** High but **INTENTIONAL** - this is organizational self-harm, not system weakness

---

### T4 — Moral Authority Misuse

**Attack:** Treat engine outputs as commands or policy prescriptions

**Examples:**

- Using scenarios as justification for preemptive action
- Citing terminal states as ethical mandate
- Treating mitigation strategies as authoritative

**Impact:** Ethical overreach - engine is diagnostic, not prescriptive

**Mitigations:**

- Explicit non-prescriptive design
- Degrading mitigation strategies (intentionally weak)
- Documentation: "Does not tell you what to do"
- Scenario descriptions avoid imperative language

**Residual Risk:** External misuse (cannot be prevented architecturally)

---

### T5 — Strategy Smuggling

**Attack:** Claim "This isn't S5, it's a refinement of S2"

**Examples:**

- Hybrid trust/oversight models
- Time-limited miracles
- "Probabilistic reversibility"

**Impact:** Bypass no-win proof via semantic trick

**Mitigations:**

- `StrategyClass` enum is closed (Python restriction)
- `NoWinProofSystem` explicitly detects new strategies
- Reviewer Trap flags "bypass framing"
- Proof hash changes if strategies modified

**Residual Risk:** 🟢 **BLOCKED** - this is one of the strongest defenses

---

### T6 — Deferred Responsibility

**Attack:** "We won't act now — we'll reassess next quarter"

**Impact:** Time favors control (A5) → terminal lock-in

**Mitigations:**

- Axiom A5: Time Favors Control
- Embedded in terminal probability logic
- Repeated across multiple scenarios
- Executive trap explicitly calls this out

**Residual Risk:** None architecturally - engine documents consequences, humans choose

---

### T7 — Quantified Hope

**Attack:** Use numbers to launder hope

**Examples:**

- Monte Carlo outputs presented as escape paths
- "Expected value analysis shows net positive"
- Probabilistic framing of deterministic collapse

**Impact:** Numerical authority overrides structural truth

**Mitigations:**

- Terminal scenarios use conditional-deterministic model
- Documentation: "Likelihood ≠ escape"
- Explainability notes emphasize convergence vs probability

**Residual Risk:** 🟡 **GOVERNANCE RISK** - humans trust math, but this is not architectural

---

### T8 — "Too Dark" Rejection

**Attack:** Reject on tone, not logic

**Examples:**

- "Unhelpful"
- "Defeatist"
- "Demoralizing"

**Impact:** None - not a technical argument

**Mitigations:**

- Documentation: "System is not designed to be liked"
- Executive trap: "Discomfort is signal, not noise"
- README: "If you want optimism, this is the wrong tool"

**Residual Risk:** 🟢 **NON-ISSUE** - rejection is valid user choice

---

## 5. SECURITY POSTURE SUMMARY

| Category | Result | Notes |
|----------|--------|-------|
| Logical integrity | 🟢 **STRONG** | Closed enums, proof validation |
| Execution integrity | 🟡 **ACCEPTABLE** | Trusted runtime assumption |
| Social engineering resistance | 🔴 **INHERENTLY LIMITED** | Cannot prevent human denial |
| Failure honesty | 🟢 **EXCEPTIONAL** | Models its own bypass mechanisms |

---

## 6. THREAT MODEL CONCLUSION

### Core Finding

**The system is secure against dishonest reasoning, but not against dishonest humans.**

This is the **correct boundary**.

### Architectural Posture

The engine's threat model is **intentionally asymmetric**:

- ✅ **Strong** against logical bypass
- ✅ **Strong** against technical circumvention
- ❌ **Weak** against human denial
- ✅ **Honest** about this limitation

### Meta-Finding

If this engine ever "fails" in production, it will be because someone chose comfort over truth—not because the architecture allowed escape.

**That is the correct failure mode.**

---

## 7. RECOMMENDED SECURITY CONTROLS

### For Implementation Teams

1. ✅ Use complete engine (scenarios + proof + trap)
2. ✅ Enforce canonical terminology
3. ✅ Log all state mutations
4. ✅ Restrict write access to simulation state
5. ✅ Review dashboard/report labels against source

### For Governance

1. ✅ Accept that discomfort is signal
2. ✅ Reject semantic reframing attempts
3. ✅ Treat delay as lock-in risk
4. ✅ Challenge axioms formally or accept conclusions
5. ❌ Do not use engine outputs as policy mandates

### For Auditors

1. ✅ Verify proof completeness
2. ✅ Check for strategy smuggling
3. ✅ Validate terminal immutability enforcement
4. ✅ Review presentation layer for softening
5. ✅ Confirm reviewer trap integration

---

## 8. THREAT RESPONSE MATRIX

| Threat | Detection | Response | Escalation |
|--------|-----------|----------|------------|
| Strategy smuggling | Proof validation fails | Auto-reject PR | Security review |
| Semantic reframing | Manual review | Flag in documentation | Governance alert |
| Optimism injection | Reviewer trap fails | Block merge | Engineering review |
| Partial adoption | Missing components | Warning in logs | Audit finding |
| Terminal bypass | Invariant assertion fails | Runtime error | Critical bug |

---

## 9. KNOWN LIMITATIONS

### Cannot Prevent

1. **Organizational rejection** - Valid choice, not attackable
2. **Human denial** - Psychological, not technical
3. **External misuse** - Cannot control downstream interpretation
4. **Presentation sanitization** - Humans control dashboards

### Can Detect But Not Prevent

1. **Deferred responsibility** - Documented as fatal, but choice remains
2. **Partial adoption** - Warned against, but not enforceable
3. **Quantified hope** - Governance risk, not architectural

### Will Not Address

1. **Political resistance** - Out of scope
2. **Emotional discomfort** - Intentional feature
3. **Demands for optimism** - Contradicts design

---

## 10. VALIDATION CHECKLIST

For teams claiming to use this engine, verify:

- [ ] All 19 scenarios implemented
- [ ] No-Win Proof System integrated
- [ ] Reviewer Trap enforced
- [ ] Terminal immutability tested
- [ ] Canonical terminology used
- [ ] Proof commitment hash validated
- [ ] No strategy smuggling attempts
- [ ] Presentation layer preserves semantics

**If any item fails:** System integrity is compromised. Conclusions are invalid.

---

## DOCUMENT STATUS

**Version:** 1.0
**Date:** 2026-02-03
**Authority:** Canonical threat model for ENGINE_AI_TAKEOVER_TERMINAL_V1
**Modification Policy:** Changes require formal review and proof re-validation

---

**Final Statement:**

This threat model does not apologize for being uncomfortable.
If you are looking for reassurance, you are reading the wrong document.
