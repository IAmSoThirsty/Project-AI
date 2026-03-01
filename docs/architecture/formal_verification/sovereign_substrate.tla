-----------------------------------------------------------------------------
-- MODULE sovereign_substrate
-- High-level TLA+ specification for the Project-AI Tier 0 Reflexive Bedrock
-----------------------------------------------------------------------------

EXTENDS Integers, Sequences, FiniteSets

VARIABLES 
    primary_state,    \* The state of the Primary Plane (Governance Layer)
    shadow_state,     \* The state of the Shadow Plane (Verification Layer)
    substrate_alive   \* Boolean representing if the OctoReflex kernel is active

vars == <<primary_state, shadow_state, substrate_alive>>

-----------------------------------------------------------------------------
\* Initial State: Both planes must be synchronized and substrate active
Init == 
    /\ primary_state = "IDLE"
    /\ shadow_state = "IDLE"
    /\ substrate_alive = TRUE

\* Transition: Execute Intent
\* The primary plane proposes a state change, and the shadow plane must agree.
Execute(intent) ==
    /\ primary_state' = intent
    /\ shadow_state' = intent
    /\ UNCHANGED substrate_alive

\* Transition: Reflexive Halt (The Bedrock Invariant)
\* If the primary and shadow planes diverge, the substrate MUST halt the system.
HaltOnDivergence ==
    /\ primary_state /= shadow_state
    /\ substrate_alive' = FALSE
    /\ UNCHANGED <<primary_state, shadow_state>>

\* Next State Logic
Next == 
    \/ \E intent \in {"READ", "WRITE", "EXECUTE"}: Execute(intent)
    \/ HaltOnDivergence

-----------------------------------------------------------------------------
\* INVARIANT: Sovereignty Integrity
\* The system is only allowed to be alive if the planes remain in sync.
SovereignInvariant == (substrate_alive = TRUE) => (primary_state = shadow_state)

THEOREM Spec => []SovereignInvariant
=============================================================================
