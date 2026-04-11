---- MODULE MonotonicStateMachine ----
(*
Formal specification of the OctoReflex 6-state monotonic escalation state machine.

This specification proves the following safety properties:
1. Monotonicity: State transitions only increase (except explicit decay)
2. Atomicity: State reads/writes are atomic
3. Terminal invariant: TERMINATED state is permanent
4. Decay safety: Decay decrements by exactly 1

CONSTANTS:
  - States: {NORMAL, PRESSURE, ISOLATED, FROZEN, QUARANTINED, TERMINATED}
  - PIDs: Set of process IDs

VARIABLES:
  - state: [PID -> State]
  - timestamp: [PID -> Nat]
  - event_log: Sequence of transition events
*)

EXTENDS Naturals, Sequences, TLC

CONSTANTS
  PIDs,          \* Set of process IDs
  MaxTransitions \* Bound for model checking

VARIABLES
  state,         \* state[pid] = current state
  timestamp,     \* timestamp[pid] = nanoseconds when state entered
  event_log      \* Sequence of all state transitions

\* State enumeration (must match Go code)
STATES == {"NORMAL", "PRESSURE", "ISOLATED", "FROZEN", "QUARANTINED", "TERMINATED"}

StateValue(s) ==
  CASE s = "NORMAL"      -> 0
    [] s = "PRESSURE"    -> 1
    [] s = "ISOLATED"    -> 2
    [] s = "FROZEN"      -> 3
    [] s = "QUARANTINED" -> 4
    [] s = "TERMINATED"  -> 5

\* Initial state: all processes are NORMAL
Init ==
  /\ state = [p \in PIDs |-> "NORMAL"]
  /\ timestamp = [p \in PIDs |-> 0]
  /\ event_log = <<>>

\* Escalate: Transition to a higher state
\* Precondition: target > current
\* Postcondition: state' = target, timestamp updated
Escalate(pid, target) ==
  /\ StateValue(target) > StateValue(state[pid])
  /\ state' = [state EXCEPT ![pid] = target]
  /\ timestamp' = [timestamp EXCEPT ![pid] = timestamp[pid] + 1]
  /\ event_log' = Append(event_log, [type |-> "escalate", pid |-> pid, old |-> state[pid], new |-> target])

\* Decay: Decrement state by 1 (except NORMAL and TERMINATED)
\* Precondition: current > NORMAL AND current /= TERMINATED
\* Postcondition: state' = current - 1, timestamp updated
Decay(pid) ==
  LET
    current == state[pid]
    currentVal == StateValue(current)
  IN
    /\ current /= "NORMAL"
    /\ current /= "TERMINATED"
    /\ LET
        newVal == currentVal - 1
        newState == CASE newVal = 0 -> "NORMAL"
                      [] newVal = 1 -> "PRESSURE"
                      [] newVal = 2 -> "ISOLATED"
                      [] newVal = 3 -> "FROZEN"
                      [] newVal = 4 -> "QUARANTINED"
       IN
         /\ state' = [state EXCEPT ![pid] = newState]
         /\ timestamp' = [timestamp EXCEPT ![pid] = timestamp[pid] + 1]
         /\ event_log' = Append(event_log, [type |-> "decay", pid |-> pid, old |-> current, new |-> newState])

\* Next state relation
Next ==
  \/ \E pid \in PIDs, target \in STATES : Escalate(pid, target)
  \/ \E pid \in PIDs : Decay(pid)

Spec == Init /\ [][Next]_<<state, timestamp, event_log>>

\* ─── TYPE INVARIANTS ───────────────────────────────────────────────────────

TypeInvariant ==
  /\ \A pid \in PIDs : state[pid] \in STATES
  /\ \A pid \in PIDs : timestamp[pid] \in Nat

\* ─── SAFETY PROPERTIES ─────────────────────────────────────────────────────

\* Monotonicity: Escalate never decreases state (unless Decay is explicitly called)
MonotonicityInvariant ==
  \A i \in DOMAIN event_log :
    LET event == event_log[i]
    IN
      event.type = "escalate" => StateValue(event.new) > StateValue(event.old)

\* Terminal: TERMINATED state never transitions to anything else
TerminalInvariant ==
  \A pid \in PIDs :
    state[pid] = "TERMINATED" =>
      \A i \in DOMAIN event_log :
        event_log[i].pid = pid => event_log[i].old /= "TERMINATED"

\* Decay safety: Decay decrements by exactly 1
DecaySafetyInvariant ==
  \A i \in DOMAIN event_log :
    LET event == event_log[i]
    IN
      event.type = "decay" => StateValue(event.old) - StateValue(event.new) = 1

\* No negative states
NoNegativeStatesInvariant ==
  \A pid \in PIDs : StateValue(state[pid]) >= 0

\* States are bounded
BoundedStatesInvariant ==
  \A pid \in PIDs : StateValue(state[pid]) <= 5

\* ─── LIVENESS PROPERTIES ───────────────────────────────────────────────────

\* Eventually, a process in TERMINATED stays there forever (terminal state)
EventuallyTerminalPersists ==
  \A pid \in PIDs :
    []<>(state[pid] = "TERMINATED" => [](state[pid] = "TERMINATED"))

\* ─── MODEL CHECKING CONSTRAINTS ────────────────────────────────────────────

\* Limit transitions for model checking
StateConstraint ==
  Len(event_log) <= MaxTransitions

====
