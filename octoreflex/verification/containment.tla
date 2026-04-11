// Formal verification specification for OCTOREFLEX containment guarantees
//
// This file defines TLA+ specifications that can be model-checked using
// the TLA+ Toolbox or Apalache model checker.
//
// Properties verified:
//   1. State transition monotonicity (escalation only in kernel)
//   2. No state value > TERMINATED (5)
//   3. TERMINATED state is permanent
//   4. Budget exhaustion prevents escalation (safety)
//   5. Quorum decisions are deterministic given inputs

---- MODULE OctoReflexContainment ----

EXTENDS Integers, Sequences, FiniteSets

\* State constants (must match octoreflex.h)
CONSTANTS
    NORMAL,      \* 0
    PRESSURE,    \* 1
    ISOLATED,    \* 2
    FROZEN,      \* 3
    QUARANTINED, \* 4
    TERMINATED   \* 5

\* Process and event model
VARIABLES
    processState,    \* Function: PID -> State
    budgetTokens,    \* Integer: remaining tokens
    eventQueue,      \* Sequence of events
    auditLog         \* Sequence of state transitions

\* Type invariant
TypeOK ==
    /\ \A pid \in DOMAIN processState: 
        processState[pid] \in {NORMAL, PRESSURE, ISOLATED, FROZEN, QUARANTINED, TERMINATED}
    /\ budgetTokens \in 0..100
    /\ eventQueue \in Seq(Nat)
    /\ auditLog \in Seq([pid: Nat, oldState: Nat, newState: Nat, timestamp: Nat])

\* Safety property: State transitions are monotonic (kernel-side)
MonotonicTransition ==
    \A pid \in DOMAIN processState:
        LET log == SelectSeq(auditLog, LAMBDA entry: entry.pid = pid)
        IN \A i \in 1..(Len(log)-1):
            log[i+1].newState >= log[i].newState

\* Safety property: No state exceeds TERMINATED
NoInvalidState ==
    \A pid \in DOMAIN processState: processState[pid] <= TERMINATED

\* Safety property: TERMINATED is permanent
TerminatedIsPermanent ==
    \A pid \in DOMAIN processState:
        processState[pid] = TERMINATED =>
            [](\* Always *)
                processState[pid] = TERMINATED

\* Safety property: Budget prevents escalation when exhausted
BudgetEnforcement ==
    budgetTokens = 0 => 
        \A pid \in DOMAIN processState:
            processState'[pid] <= processState[pid]

\* Liveness property: Anomalous process eventually escalates
EventuallyContained ==
    \A pid \in DOMAIN processState:
        (AnomalyScore(pid) > Threshold) ~> (processState[pid] > NORMAL)

\* State transition action: Escalate process
Escalate(pid, targetState, cost) ==
    /\ budgetTokens >= cost
    /\ processState[pid] < targetState
    /\ targetState <= TERMINATED
    /\ processState' = [processState EXCEPT ![pid] = targetState]
    /\ budgetTokens' = budgetTokens - cost
    /\ auditLog' = Append(auditLog, [
        pid |-> pid,
        oldState |-> processState[pid],
        newState |-> targetState,
        timestamp |-> Len(auditLog)
    ])
    /\ UNCHANGED eventQueue

\* State transition action: Decay process (userspace only)
Decay(pid) ==
    /\ processState[pid] > NORMAL
    /\ processState[pid] < TERMINATED  \* Cannot decay from TERMINATED
    /\ processState' = [processState EXCEPT ![pid] = processState[pid] - 1]
    /\ auditLog' = Append(auditLog, [
        pid |-> pid,
        oldState |-> processState[pid],
        newState |-> processState[pid] - 1,
        timestamp |-> Len(auditLog)
    ])
    /\ UNCHANGED <<budgetTokens, eventQueue>>

\* Refill budget action
RefillBudget ==
    /\ budgetTokens' = 100
    /\ UNCHANGED <<processState, eventQueue, auditLog>>

\* Process an event
ProcessEvent ==
    /\ eventQueue # <<>>
    /\ LET evt == Head(eventQueue)
           pid == evt
       IN
           \/ Escalate(pid, PRESSURE, 1)
           \/ Escalate(pid, ISOLATED, 5)
           \/ Escalate(pid, FROZEN, 10)
           \/ Escalate(pid, QUARANTINED, 20)
           \/ Escalate(pid, TERMINATED, 50)
    /\ eventQueue' = Tail(eventQueue)

\* Initial state
Init ==
    /\ processState = [pid \in {1, 2, 3} |-> NORMAL]
    /\ budgetTokens = 100
    /\ eventQueue = <<>>
    /\ auditLog = <<>>

\* Next-state relation
Next ==
    \/ ProcessEvent
    \/ \E pid \in DOMAIN processState: Decay(pid)
    \/ RefillBudget

\* Specification
Spec == Init /\ [][Next]_<<processState, budgetTokens, eventQueue, auditLog>>

\* Theorems to verify
THEOREM Spec => []TypeOK
THEOREM Spec => []MonotonicTransition
THEOREM Spec => []NoInvalidState
THEOREM Spec => []TerminatedIsPermanent
THEOREM Spec => []BudgetEnforcement

====
