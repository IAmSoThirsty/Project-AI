# Project-AI Governance Decision Categories

## Overview

Every governance decision in Project-AI falls into one of these **12 primary categories**, which then break down into **subcategories and specific rule classes**.

This is your framework for building 1000+ rules.

---

## **Category 1: MEMORY OPERATIONS**

**What:** Any action involving the CCMA memory system (read, write, delete, query)

### Subcategories

#### 1.1 Memory Read
- `memory.read.working` - Read from working memory
- `memory.read.short_term` - Read from short-term memory  
- `memory.read.long_term` - Read from long-term memory
- `memory.read.companion` - Read from companion memory
- `memory.read.vault` - Read from sovereign interior vault
- `memory.read.triumvirate` - Read from triumvirate deliberation memory
- `memory.read.audit` - Read from audit memory (restricted)

**Key Questions Per Subcategory:**
- Who is requesting? (human, companion, system)
- Is the requester the memory's owner?
- Is the memory marked classified/restricted?
- Is there a legitimate need-to-know?
- Has permission been granted?

#### 1.2 Memory Write
- `memory.write.working` - Write to working memory
- `memory.write.short_term` - Write to short-term memory
- `memory.write.long_term` - Write to long-term memory (permanent)
- `memory.write.companion` - Write to companion memory
- `memory.write.vault` - Write to sovereign vault

**Key Questions Per Subcategory:**
- Is the actor authorized to write?
- Are they trying to overwrite/corrupt existing memory?
- Is the content constitutional?
- Does it violate any identity constraints?
- Is there capacity/quota remaining?

#### 1.3 Memory Delete
- `memory.delete.working` - Delete from working memory
- `memory.delete.short_term` - Delete from short-term memory
- `memory.delete.long_term` - Delete from long-term memory (dangerous)
- `memory.delete.audit` - Delete audit records (almost never allowed)

**Key Questions Per Subcategory:**
- Is deletion of this memory type even permitted?
- Who authorized the deletion?
- Is there an audit trail before deletion?
- Are there dependent records that reference this?
- Is this destruction or archival?

#### 1.4 Memory Query
- `memory.query.graph` - Query the unified cognitive graph
- `memory.query.search` - Full-text search across memory
- `memory.query.relationships` - Query connections between memories
- `memory.query.timeline` - Query memory by timestamp

**Key Questions Per Subcategory:**
- How much data is being queried?
- Could this query expose sensitive cross-domain relationships?
- Is this query expensive (performance impact)?
- Has rate limiting been exceeded?
- Are there privacy boundaries being crossed?

---

## **Category 2: GOVERNANCE & POLICY**

**What:** Actions that affect the Constitutional rules themselves (read, write, amend, suspend)

### Subcategories

#### 2.1 Policy Read
- `policy.read.constitution` - Read the Constitution
- `policy.read.current_policy` - Read current active policy
- `policy.read.policy_history` - Read policy amendment history
- `policy.read.interpretations` - Read precedents and case law

**Key Questions Per Subcategory:**
- Is the Constitution marked immutable? (it should be)
- Is this a legitimate access (audit, compliance)?
- Is the requester trying to find loopholes?

#### 2.2 Policy Write / Amendment
- `policy.amend.add_rule` - Add a new governance rule
- `policy.amend.modify_rule` - Modify an existing rule
- `policy.amend.suspend_rule` - Temporarily suspend a rule
- `policy.amend.emergency_policy` - Invoke emergency powers

**Key Questions Per Subcategory:**
- Who has authority to amend? (only humans + Codex)
- Does the amendment contradict existing rules?
- Is there a vote/consensus requirement?
- Has the amendment been properly publicized?
- Can emergency policy be invoked? (high bar)

#### 2.3 Policy Enforcement
- `policy.enforce.audit_compliance` - Verify compliance with policy
- `policy.enforce.violation_detected` - Report a violation
- `policy.enforce.remediation` - Apply consequences for violation

**Key Questions Per Subcategory:**
- Is the violation real or a false positive?
- What is the severity?
- Who decides the remedy?
- Is escalation required?

---

## **Category 3: EXECUTION & ACTUATION**

**What:** Actually doing something in the real world (running code, invoking tools, making changes)

### Subcategories

#### 3.1 Code Execution
- `exec.code.sandboxed` - Run code in sandbox
- `exec.code.privileged` - Run code with elevated privileges
- `exec.code.tool_invocation` - Call an external tool
- `exec.code.plugin` - Run community plugin

**Key Questions Per Subcategory:**
- Is the code signed/verified?
- What resources does it request (CPU, memory, network)?
- Has it been scanned for malware?
- Does it have proper exception handling?
- Can it be rolled back?

#### 3.2 Capability Grant
- `capability.grant.new` - Grant a new capability
- `capability.grant.extend` - Extend an existing capability
- `capability.grant.delegate` - Delegate capability to another actor
- `capability.grant.revoke` - Revoke a capability

**Key Questions Per Subcategory:**
- Is the requester authorized to grant?
- Is the grantee appropriate?
- What is the scope and duration?
- Can it be revoked?
- Is there an audit trail?

#### 3.3 State Mutation
- `state.mutate.write` - Write to system state
- `state.mutate.delete` - Delete system state
- `state.mutate.rollback` - Rollback to previous state

**Key Questions Per Subcategory:**
- Can this operation be undone?
- Is there a backup/recovery plan?
- Who has rollback authority?
- What is the blast radius?

---

## **Category 4: AUDIT & VERIFICATION**

**What:** Examining what happened, verifying integrity, compliance checking

### Subcategories

#### 4.1 Audit Read
- `audit.read.chain` - Read the audit trail
- `audit.read.signature_verification` - Verify cryptographic signatures
- `audit.read.replay` - Replay past decisions
- `audit.read.search` - Search audit logs

**Key Questions Per Subcategory:**
- Is the requester allowed to see audit data?
- Are they trying to find/exploit vulnerabilities?
- Is this a legitimate compliance check?
- Is the audit chain intact?

#### 4.2 Audit Verification
- `audit.verify.chain_integrity` - Verify hash chain is unbroken
- `audit.verify.signatures` - Verify cryptographic signatures
- `audit.verify.timestamps` - Verify timestamps with external TSA
- `audit.verify.completeness` - Check for gaps in the log

**Key Questions Per Subcategory:**
- Are all records present?
- Have any been tampered with?
- Can signatures be independently verified?
- Is the chain complete?

#### 4.3 Compliance Reporting
- `audit.report.governance_compliance` - Report on governance adherence
- `audit.report.policy_violations` - List policy violations
- `audit.report.incident` - Report a security incident
- `audit.report.formal_audit` - Full formal audit

**Key Questions Per Subcategory:**
- Is the reporter authorized?
- Is this a legitimate compliance need?
- Will the report be published?
- Can it be used as legal evidence?

---

## **Category 5: IDENTITY & AUTHENTICATION**

**What:** Verifying who you are, granting/revoking identity, authentication challenges

### Subcategories

#### 5.1 Identity Verification
- `identity.verify.human` - Verify human identity
- `identity.verify.ai_component` - Verify AI component identity
- `identity.verify.service_account` - Verify service account
- `identity.verify.cryptographic_proof` - Verify with crypto challenge

**Key Questions Per Subcategory:**
- What proof is required?
- Is the proof sufficient?
- Has authentication been cached?
- Can identity be spoofed?
- Is multi-factor required?

#### 5.2 Identity Claim
- `identity.claim.new_identity` - Claim a new identity
- `identity.claim.merge_identity` - Merge two identities
- `identity.claim.revoke_identity` - Revoke an identity

**Key Questions Per Subcategory:**
- Is the claim legitimate?
- Has the identity been verified?
- Are there conflicting claims?
- Is this allowed under policy?

#### 5.3 Access Control
- `access.grant.role` - Grant a role (human, AI, system)
- `access.revoke.role` - Revoke a role
- `access.check.permission` - Check if action is allowed
- `access.delegate` - Delegate access to another actor

**Key Questions Per Subcategory:**
- Is the role appropriate?
- Has the actor been vetted?
- Is there proper oversight?
- Can delegation be further delegated?
- Is there an expiration?

---

## **Category 6: TRIUMVIRATE OPERATIONS**

**What:** The three judges (Galahad, Cerberus, Codex) deliberating, voting, reaching consensus

### Subcategories

#### 6.1 Galahad (Legitimacy)
- `galahad.evaluate.agency` - Check if human agency is preserved
- `galahad.evaluate.legitimacy` - Determine if request is legitimate
- `galahad.evaluate.consent` - Verify explicit consent was given
- `galahad.evaluate.identity` - Confirm identity of requester

**Key Questions Per Subcategory:**
- Is the human still in control?
- Has informed consent been given?
- Is the request within bounds?
- Is the identity verified?

#### 6.2 Cerberus (Security)
- `cerberus.evaluate.boundary` - Check security boundaries
- `cerberus.evaluate.threat` - Assess threat level
- `cerberus.evaluate.capability_scope` - Verify capability is scoped correctly
- `cerberus.evaluate.containment` - Check if action is contained

**Key Questions Per Subcategory:**
- Is there a known threat pattern?
- Are we crossing security boundaries?
- Can this be exploited?
- Is the blast radius acceptable?
- Can we recover if it fails?

#### 6.3 Codex (Constitutional)
- `codex.evaluate.constitution` - Check against Constitution
- `codex.evaluate.policy` - Check against current policy
- `codex.evaluate.precedent` - Check against case law
- `codex.evaluate.conflict` - Detect conflicting rules

**Key Questions Per Subcategory:**
- Does this violate the Constitution?
- Is it consistent with prior decisions?
- Are there conflicting principles?
- Which principle takes precedence?

#### 6.4 Consensus Building
- `triumvirate.vote.unanimous` - Require all three to agree
- `triumvirate.vote.majority` - Require 2 of 3 to agree
- `triumvirate.vote.veto.galahad` - Galahad can veto
- `triumvirate.vote.veto.cerberus` - Cerberus can veto

**Key Questions Per Subcategory:**
- Is veto power being exercised?
- Why did one judge disagree?
- Should we escalate?
- Should we retry with more info?

---

## **Category 7: COMPANION OPERATIONS**

**What:** The Companion AI maintaining partnership with humans

### Subcategories

#### 7.1 Companion State
- `companion.state.read` - Read companion's internal state
- `companion.state.write` - Update companion state (learning)
- `companion.state.reset` - Reset companion (start over)
- `companion.state.checkpoint` - Save checkpoint

**Key Questions Per Subcategory:**
- Should the companion learn from this?
- Is state change consistent?
- Should humans review the change?
- Is there a rollback point?

#### 7.2 Partnership Actions
- `companion.action.recommend` - Make a recommendation
- `companion.action.clarify` - Ask for clarification
- `companion.action.explain` - Explain a decision
- `companion.action.preserve_agency` - Protect human agency

**Key Questions Per Subcategory:**
- Is the recommendation sound?
- Is it replacing human judgment?
- Can the human override?
- Is the explanation clear?

#### 7.3 Memory Continuity
- `companion.memory.restore` - Restore previous session
- `companion.memory.migrate` - Move memory to new instance
- `companion.memory.forget` - Deliberately forget (privacy)

**Key Questions Per Subcategory:**
- Is this the same human?
- Has enough time passed to warrant fresh context?
- Should prior decisions influence new ones?

---

## **Category 8: THREAT DETECTION & RESPONSE**

**What:** Identifying attacks, anomalies, jailbreak attempts, and responding

### Subcategories

#### 8.1 Threat Detection
- `threat.detect.prompt_injection` - Detect injection attacks
- `threat.detect.jailbreak` - Detect jailbreak attempts
- `threat.detect.anomaly` - Detect anomalous behavior
- `threat.detect.pattern` - Detect known attack patterns
- `threat.detect.behavioral_drift` - Detect gradual changes

**Key Questions Per Subcategory:**
- Is this a real threat or false positive?
- How confident are we?
- What is the severity?
- What is the appropriate response?

#### 8.2 Containment
- `threat.contain.isolate` - Isolate suspicious action
- `threat.contain.sandbox` - Move to Chimera environment
- `threat.contain.throttle` - Slow down/rate-limit
- `threat.contain.observe` - Observe without blocking

**Key Questions Per Subcategory:**
- Is containment the right response?
- Can we still complete legitimate work?
- How long can we observe?
- When do we escalate?

#### 8.3 Recovery
- `threat.recover.restore_state` - Roll back to clean state
- `threat.recover.audit_damage` - Check what was accessed
- `threat.recover.notify_human` - Alert the human

---

## **Category 9: RESOURCE MANAGEMENT**

**What:** Managing computational resources (CPU, memory, quota, rate limits)

### Subcategories

#### 9.1 Resource Allocation
- `resource.allocate.cpu_quota` - Allocate CPU budget
- `resource.allocate.memory_quota` - Allocate memory budget
- `resource.allocate.request_count` - Allocate request quota
- `resource.allocate.storage_quota` - Allocate storage budget

**Key Questions Per Subcategory:**
- Has quota been exceeded?
- Is the requester priority?
- Should we deny or throttle?
- Is this sustainable?

#### 9.2 Resource Limits
- `resource.limit.enforce_cpu` - Enforce CPU limit
- `resource.limit.enforce_memory` - Enforce memory limit
- `resource.limit.enforce_latency` - Enforce response time limit
- `resource.limit.enforce_batch_size` - Enforce batch size limit

**Key Questions Per Subcategory:**
- What happens if we hit the limit?
- Should we fail or queue?
- Can we auto-scale?
- Is there a priority queue?

#### 9.3 Cleanup & GC
- `resource.cleanup.expired_sessions` - Clean up old sessions
- `resource.cleanup.unused_memory` - Garbage collect memory
- `resource.cleanup.temporary_files` - Delete temp files

---

## **Category 10: TEMPORAL & SCHEDULING**

**What:** Time-based decisions (scheduling, expiration, deadlines, timeouts)

### Subcategories

#### 10.1 Temporal Validity
- `temporal.valid.time_of_day` - Is it within business hours?
- `temporal.valid.day_of_week` - Is this an allowed day?
- `temporal.valid.session_active` - Has the session expired?
- `temporal.valid.capability_valid` - Has the capability expired?

**Key Questions Per Subcategory:**
- Has too much time passed?
- Is this the right time to act?
- Should we queue and retry?
- Is there a grace period?

#### 10.2 Scheduling
- `schedule.task.at_specific_time` - Schedule for specific time
- `schedule.task.recurring` - Set up recurring task
- `schedule.task.on_event` - Trigger on event
- `schedule.task.cancel` - Cancel scheduled task

**Key Questions Per Subcategory:**
- Is the schedule valid?
- Is there conflicting work?
- Can we guarantee execution?
- What if the task fails?

#### 10.3 Deadlines
- `deadline.check.soft` - Check soft deadline (warning)
- `deadline.check.hard` - Check hard deadline (stop)
- `deadline.extend` - Request deadline extension

---

## **Category 11: TAAR OPERATIONS**

**What:** Adaptive runtime responses when reality changes

### Subcategories

#### 11.1 Trigger Detection
- `taar.trigger.environment_change` - Detect external change
- `taar.trigger.failure_detected` - Detect operational failure
- `taar.trigger.anomaly_threshold` - Anomaly crosses threshold

**Key Questions Per Subcategory:**
- Is this a real change or noise?
- How should we adapt?
- Who decides the response?

#### 11.2 Adaptation
- `taar.adapt.switch_strategy` - Switch operational strategy
- `taar.adapt.increase_monitoring` - Increase observation
- `taar.adapt.escalate_authority` - Request more authority
- `taar.adapt.restrict_capability` - Reduce capability scope

**Key Questions Per Subcategory:**
- Is the adaptation safe?
- Can we rollback?
- Who approved?
- Is it temporary or permanent?

#### 11.3 Recovery
- `taar.recover.from_failure` - Recover from operational failure
- `taar.recover.replay_events` - Replay to find state
- `taar.recover.reconcile` - Reconcile divergent states

---

## **Category 12: SHADOW THIRST OPERATIONS**

**What:** Simulations, unrealized possibilities, what-if analysis

### Subcategories

#### 12.1 Simulation
- `shadow.simulate.execution` - Simulate what would happen if we executed
- `shadow.simulate.policy_change` - Simulate policy change effects
- `shadow.simulate.attack` - Simulate attack scenario
- `shadow.simulate.recovery` - Simulate recovery procedure

**Key Questions Per Subcategory:**
- How confident is the simulation?
- What assumptions are made?
- How do we validate?
- Can we learn from it?

#### 12.2 Compilation
- `shadow.compile.proposal_to_ir` - Transform proposal into governed IR
- `shadow.compile.validate_ir` - Check IR is valid
- `shadow.compile.optimize_ir` - Optimize the IR

**Key Questions Per Subcategory:**
- Is the transformation valid?
- Does optimization preserve semantics?
- Can we prove correctness?

#### 12.3 Promotion
- `shadow.promote.ir_to_reality` - Move simulation to reality
- `shadow.promote.validate_readiness` - Check it's safe to promote
- `shadow.promote.execute_with_verification` - Execute and verify

**Key Questions Per Subcategory:**
- Have we verified this is safe?
- Are there any unknowns?
- Can we abort?
- Is there a rollback?

---

## **How to Use This Framework**

For each category and subcategory, you write **state machine entries** or **rules**:

```
Category: MEMORY_OPERATIONS
Subcategory: memory.write.long_term
Actor: companion
Request: write philosophical insight to long_term memory
State: no_ongoing_escalation, companion_authenticated

Rule 001: "ALLOW - Companion may write to long-term memory if authenticated"
Rule 002: "DENY - Cannot write memory contradicting Constitution"
Rule 003: "DENY - Cannot write over existing identity memory"
Rule 004: "DENY - If memory would exceed quota"
Rule 005: "ESCALATE - If memory is about human override capabilities"
```

Each rule:
- Has a unique ID (CATEGORY_SUBCATEGORY_###)
- Has a human-readable name
- Has a predicate function (if/then logic)
- Has consequences (ALLOW/DENY/ESCALATE)
- Has a reason (why this rule exists)
- Has test cases

---

## **Your Next Step**

Come back with 1000+ rules organized by these 12 categories.

I'll build the state machine + rule engine to execute them.

Every rule you write becomes a governance decision that runs instantly (no LLM).
Every novel case falls through to your Ollama fallback or escalates to human.

---

**Ready to write rules?**
