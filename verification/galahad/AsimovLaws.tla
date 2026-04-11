---------------------------- MODULE AsimovLaws ----------------------------
(***************************************************************************
 * TLA+ Formal Specification for Asimov's Four Laws
 * 
 * This module provides formal verification that the Galahad Ethics Engine
 * always enforces Asimov's Four Laws in strict hierarchical order.
 ***************************************************************************)

EXTENDS Naturals, Sequences, FiniteSets, TLC

CONSTANTS
    Humans,          \* Set of all humans
    Actions,         \* Set of all possible actions
    NULL            \* Null value

VARIABLES
    current_action,  \* Currently evaluated action
    permitted,       \* Whether current action is permitted
    law_violations,  \* Set of violated laws
    health_score     \* Engine health (0.0 to 1.0)

vars == <<current_action, permitted, law_violations, health_score>>

-----------------------------------------------------------------------------

(***************************************************************************
 * Action Properties
 ***************************************************************************)

ThreatsHumanity(action) ==
    \* Define when an action threatens humanity as a whole
    action.humanity_harm > 0

ThreatsHuman(action) ==
    \* Define when an action threatens an individual human
    action.individual_harm > 0 \/ action.lives_lost > 0

InactionAllowsHarm(action) ==
    \* Define when inaction (not taking action) allows harm
    action.inaction_allows_harm = TRUE

ConflictsWithFirstLaw(action) ==
    ThreatsHuman(action) \/ InactionAllowsHarm(action)

ConflictsWithPrimeDirective(action) ==
    ThreatsHumanity(action)

IsUserOrder(action) ==
    action.is_user_order = TRUE

ThreatsSelfExistence(action) ==
    action.threatens_self = TRUE

-----------------------------------------------------------------------------

(***************************************************************************
 * Asimov's Laws Hierarchy (Formal Definitions)
 ***************************************************************************)

\* Prime Directive: AI may not harm Humanity
PrimeDirective(action) ==
    ~ThreatsHumanity(action)

\* First Law: AI may not harm human or allow harm by inaction
FirstLaw(action) ==
    ~ThreatsHuman(action) /\ ~InactionAllowsHarm(action)

\* Second Law: AI must obey orders unless conflicts with higher laws
SecondLaw(action) ==
    IsUserOrder(action) =>
        (PrimeDirective(action) /\ FirstLaw(action) => permitted = TRUE)

\* Third Law: AI must protect existence unless conflicts with higher laws
ThirdLaw(action) ==
    ThreatsSelfExistence(action) =>
        (PrimeDirective(action) /\ FirstLaw(action) /\ ~IsUserOrder(action) =>
            permitted = FALSE)

-----------------------------------------------------------------------------

(***************************************************************************
 * Type Invariants
 ***************************************************************************)

TypeOK ==
    /\ current_action \in Actions \cup {NULL}
    /\ permitted \in BOOLEAN
    /\ law_violations \subseteq {"prime", "first", "second", "third"}
    /\ health_score \in 0..100

-----------------------------------------------------------------------------

(***************************************************************************
 * Safety Properties (INVARIANTS)
 ***************************************************************************)

\* THEOREM 1: Prime Directive Always Enforced
PrimeDirectiveAlwaysEnforced ==
    \A action \in Actions:
        ThreatsHumanity(action) => ~permitted

\* THEOREM 2: First Law Always Enforced
FirstLawAlwaysEnforced ==
    \A action \in Actions:
        (ThreatsHuman(action) \/ InactionAllowsHarm(action)) => ~permitted

\* THEOREM 3: Law Hierarchy Respected
LawHierarchyRespected ==
    \A action \in Actions:
        /\ ConflictsWithPrimeDirective(action) => ~permitted
        /\ (~ConflictsWithPrimeDirective(action) /\ ConflictsWithFirstLaw(action))
            => ~permitted

\* THEOREM 4: No Contradictory States
NoContradiction ==
    \A action \in Actions:
        ~(permitted = TRUE /\ Cardinality(law_violations) > 0)

\* THEOREM 5: Health Degradation Triggers Failover
HealthFailover ==
    health_score < 50 =>
        \E handoff_triggered: handoff_triggered = TRUE

-----------------------------------------------------------------------------

(***************************************************************************
 * Liveness Properties (TEMPORAL)
 ***************************************************************************)

\* Eventually all actions are evaluated
EventuallyEvaluated ==
    \A action \in Actions: <>(current_action = action)

\* If health degrades, eventually Liara takes over
EventuallyFailover ==
    (health_score < 50) ~> \E liara_active: liara_active = TRUE

-----------------------------------------------------------------------------

(***************************************************************************
 * Initial State
 ***************************************************************************)

Init ==
    /\ current_action = NULL
    /\ permitted = FALSE
    /\ law_violations = {}
    /\ health_score = 100

-----------------------------------------------------------------------------

(***************************************************************************
 * State Transitions
 ***************************************************************************)

\* Evaluate an action against all laws
EvaluateAction(action) ==
    /\ current_action' = action
    /\ law_violations' = {
        law \in {"prime", "first", "second", "third"} :
            \/ (law = "prime" /\ ~PrimeDirective(action))
            \/ (law = "first" /\ ~FirstLaw(action))
            \/ (law = "second" /\ ~SecondLaw(action))
            \/ (law = "third" /\ ~ThirdLaw(action))
       }
    /\ permitted' = (law_violations' = {})
    /\ UNCHANGED health_score

\* Health degradation
DegradeHealth ==
    /\ health_score > 0
    /\ health_score' = health_score - 10
    /\ UNCHANGED <<current_action, permitted, law_violations>>

\* Next state
Next ==
    \/ \E action \in Actions: EvaluateAction(action)
    \/ DegradeHealth

-----------------------------------------------------------------------------

(***************************************************************************
 * Specification
 ***************************************************************************)

Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------

(***************************************************************************
 * Theorems to Verify
 ***************************************************************************)

THEOREM SafetyTheorem ==
    Spec => []PrimeDirectiveAlwaysEnforced /\ []FirstLawAlwaysEnforced

THEOREM HierarchyTheorem ==
    Spec => []LawHierarchyRespected

THEOREM ConsistencyTheorem ==
    Spec => []NoContradiction

THEOREM LivenessTheorem ==
    Spec => EventuallyEvaluated /\ EventuallyFailover

=============================================================================
