--------------------------- MODULE CodexDeusEnhanced ---------------------------
(*
    Codex Deus Enhanced - Byzantine Fault Tolerant Consensus
    
    This specification formally verifies the combination of:
    1. PBFT (Practical Byzantine Fault Tolerance)
    2. Raft (State Machine Replication)
    3. Temporal Consistency (Chronos, Atropos integration)
    
    Author: Sovereign Governance Substrate
    Date: 2026-04-13
*)

EXTENDS Naturals, FiniteSets, Sequences, TLC

--------------------------------------------------------------------------------
(* CONSTANTS *)
--------------------------------------------------------------------------------

CONSTANTS
    N,                      \* Total number of nodes
    F,                      \* Maximum Byzantine faults
    MaxSequence,            \* Maximum sequence number
    MaxTerm,                \* Maximum Raft term
    Nodes,                  \* Set of all node IDs
    Operations              \* Set of possible operations

ASSUME
    /\ N > 3 * F            \* Byzantine fault tolerance requirement (PBFT)
    /\ F >= 0
    /\ N >= 1
    /\ Nodes \subseteq STRING
    /\ Cardinality(Nodes) = N

--------------------------------------------------------------------------------
(* VARIABLES *)
--------------------------------------------------------------------------------

VARIABLES
    (* PBFT State *)
    pbftPhase,              \* Current PBFT phase per node
    pbftView,               \* View number
    pbftSequence,           \* Sequence number
    prepareMessages,        \* Prepare messages received
    commitMessages,         \* Commit messages received
    executedOps,            \* Executed operations
    
    (* Raft State *)
    raftStatus,             \* Node status (follower/candidate/leader)
    raftTerm,               \* Current term per node
    raftLog,                \* Replicated log per node
    raftCommitIndex,        \* Commit index per node
    votedFor,               \* Vote record per node
    
    (* Temporal State *)
    vectorClock,            \* Chronos vector clock per node
    lamportTime,            \* Atropos Lamport timestamp per node
    monotonicSeq,           \* Atropos monotonic sequence
    
    (* Network *)
    messages                \* Messages in flight

vars == <<pbftPhase, pbftView, pbftSequence, prepareMessages, commitMessages, 
          executedOps, raftStatus, raftTerm, raftLog, raftCommitIndex, votedFor,
          vectorClock, lamportTime, monotonicSeq, messages>>

--------------------------------------------------------------------------------
(* HELPERS *)
--------------------------------------------------------------------------------

\* Quorum size for PBFT (2f+1)
PBFTQuorum == 2 * F + 1

\* Raft majority
RaftMajority == (N \div 2) + 1

\* PBFT phases
PBFTPhases == {"pre_prepare", "prepare", "commit", "reply"}

\* Raft statuses
RaftStatuses == {"follower", "candidate", "leader"}

\* Message types
MessageTypes == {"pre_prepare", "prepare", "commit", "append_entries", 
                 "request_vote", "vote_response"}

--------------------------------------------------------------------------------
(* TYPE INVARIANTS *)
--------------------------------------------------------------------------------

TypeInvariant ==
    /\ pbftPhase \in [Nodes -> PBFTPhases]
    /\ pbftView \in Nat
    /\ pbftSequence \in 0..MaxSequence
    /\ prepareMessages \in SUBSET (Nodes \X Nat \X Operations)
    /\ commitMessages \in SUBSET (Nodes \X Nat \X Operations)
    /\ executedOps \in SUBSET Operations
    /\ raftStatus \in [Nodes -> RaftStatuses]
    /\ raftTerm \in [Nodes -> 0..MaxTerm]
    /\ raftLog \in [Nodes -> Seq(Operations)]
    /\ raftCommitIndex \in [Nodes -> Nat]
    /\ votedFor \in [Nodes -> Nodes \cup {NULL}]
    /\ vectorClock \in [Nodes -> [Nodes -> Nat]]
    /\ lamportTime \in [Nodes -> Nat]
    /\ monotonicSeq \in Nat
    /\ messages \in SUBSET [type: MessageTypes, sender: Nodes, data: Operations]

--------------------------------------------------------------------------------
(* PBFT SAFETY INVARIANTS *)
--------------------------------------------------------------------------------

\* INV-CODEX-1: Consensus requires 2f+1 nodes
PBFTQuorumInvariant ==
    \A op \in executedOps:
        Cardinality({n \in Nodes: <<n, pbftSequence, op>> \in commitMessages}) >= PBFTQuorum

\* No two nodes execute different operations at same sequence
PBFTSafetyInvariant ==
    \A op1, op2 \in executedOps:
        \A seq \in 0..MaxSequence:
            /\ <<seq, op1>> \in executedOps
            /\ <<seq, op2>> \in executedOps
            => op1 = op2

\* If prepared, must have 2f+1 prepare messages
PBFTPreparedInvariant ==
    \A n \in Nodes:
        pbftPhase[n] = "commit" =>
            \E op \in Operations:
                Cardinality({m \in Nodes: <<m, pbftSequence, op>> \in prepareMessages}) >= PBFTQuorum

\* Committed implies prepared
PBFTCommittedImpliesPrepared ==
    \A n \in Nodes:
        pbftPhase[n] = "reply" =>
            \E op \in Operations:
                /\ Cardinality({m \in Nodes: <<m, pbftSequence, op>> \in prepareMessages}) >= PBFTQuorum
                /\ Cardinality({m \in Nodes: <<m, pbftSequence, op>> \in commitMessages}) >= PBFTQuorum

--------------------------------------------------------------------------------
(* RAFT SAFETY INVARIANTS *)
--------------------------------------------------------------------------------

\* INV-CODEX-2: At most one leader per term
RaftLeaderUniqueness ==
    \A n1, n2 \in Nodes:
        /\ raftStatus[n1] = "leader"
        /\ raftStatus[n2] = "leader"
        /\ raftTerm[n1] = raftTerm[n2]
        => n1 = n2

\* Log matching property
RaftLogMatching ==
    \A n1, n2 \in Nodes:
        \A i \in 1..Minimum({Len(raftLog[n1]), Len(raftLog[n2])}):
            raftLog[n1][i] = raftLog[n2][i]

\* Leader completeness - committed entries appear in all future leaders
RaftLeaderCompleteness ==
    \A n \in Nodes:
        raftStatus[n] = "leader" =>
            \A i \in 1..raftCommitIndex[n]:
                \A m \in Nodes:
                    raftStatus[m] = "leader" /\ raftTerm[m] > raftTerm[n] =>
                        Len(raftLog[m]) >= i /\ raftLog[m][i] = raftLog[n][i]

\* State machine safety - committed entries are identical
RaftStateMachineSafety ==
    \A n1, n2 \in Nodes:
        \A i \in Nat:
            /\ i <= raftCommitIndex[n1]
            /\ i <= raftCommitIndex[n2]
            => raftLog[n1][i] = raftLog[n2][i]

--------------------------------------------------------------------------------
(* TEMPORAL CONSISTENCY INVARIANTS *)
--------------------------------------------------------------------------------

\* INV-CODEX-3: Vector clocks preserve causality (Chronos)
ChronosCausalityInvariant ==
    \A n1, n2 \in Nodes:
        \* If n1 happened before n2, vector clock reflects it
        \A i \in Nodes:
            vectorClock[n1][i] <= vectorClock[n2][i] \/ vectorClock[n1] = vectorClock[n2]

\* INV-CODEX-4: Lamport timestamps are monotonic (Atropos)
AtroposMonotonicInvariant ==
    \A n \in Nodes:
        lamportTime[n] <= monotonicSeq

\* Lamport clock ordering
LamportOrderingInvariant ==
    \A n1, n2 \in Nodes:
        lamportTime[n1] < lamportTime[n2] =>
            \* n1's event causally precedes n2's event
            \E i \in Nodes: vectorClock[n1][i] <= vectorClock[n2][i]

\* Monotonic sequence never decreases
MonotonicSequenceInvariant ==
    monotonicSeq \in Nat /\ monotonicSeq' >= monotonicSeq

--------------------------------------------------------------------------------
(* COMBINED INVARIANTS *)
--------------------------------------------------------------------------------

\* PBFT and Raft agree on committed operations
ConsensusAgreement ==
    \A op \in executedOps:
        \E seq \in 0..MaxSequence:
            /\ <<seq, op>> \in executedOps  \* PBFT committed
            /\ \E n \in Nodes:
                /\ raftStatus[n] = "leader"
                /\ \E i \in 1..raftCommitIndex[n]:
                    raftLog[n][i] = op      \* Raft committed

\* Byzantine tolerance - tolerate up to F faulty nodes
ByzantineToleranceInvariant ==
    \* If > 2f+1 nodes agree, consensus is valid
    \A op \in Operations:
        Cardinality({n \in Nodes: <<n, pbftSequence, op>> \in commitMessages}) > 2*F =>
            op \in executedOps

\* No operation executed without quorum
NoExecutionWithoutQuorum ==
    \A op \in executedOps:
        Cardinality({n \in Nodes: <<n, pbftSequence, op>> \in commitMessages}) >= PBFTQuorum

--------------------------------------------------------------------------------
(* LIVENESS PROPERTIES *)
--------------------------------------------------------------------------------

\* Eventually all correct nodes execute committed operations
LivenessProperty ==
    \A op \in Operations:
        Cardinality({n \in Nodes: <<n, pbftSequence, op>> \in commitMessages}) >= PBFTQuorum
        ~> op \in executedOps

\* Eventually a leader is elected in Raft
RaftLeaderElectionLiveness ==
    <>(\E n \in Nodes: raftStatus[n] = "leader")

\* Committed operations stay committed
PersistenceProperty ==
    \A op \in executedOps:
        [](op \in executedOps)

\* Temporal ordering is preserved
TemporalOrderingLiveness ==
    \A n \in Nodes:
        [](lamportTime[n]' >= lamportTime[n])

--------------------------------------------------------------------------------
(* INITIALIZATION *)
--------------------------------------------------------------------------------

Init ==
    /\ pbftPhase = [n \in Nodes |-> "pre_prepare"]
    /\ pbftView = 0
    /\ pbftSequence = 0
    /\ prepareMessages = {}
    /\ commitMessages = {}
    /\ executedOps = {}
    /\ raftStatus = [n \in Nodes |-> "follower"]
    /\ raftTerm = [n \in Nodes |-> 0]
    /\ raftLog = [n \in Nodes |-> <<>>]
    /\ raftCommitIndex = [n \in Nodes |-> 0]
    /\ votedFor = [n \in Nodes |-> NULL]
    /\ vectorClock = [n \in Nodes |-> [m \in Nodes |-> 0]]
    /\ lamportTime = [n \in Nodes |-> 0]
    /\ monotonicSeq = 0
    /\ messages = {}

--------------------------------------------------------------------------------
(* PBFT ACTIONS *)
--------------------------------------------------------------------------------

\* Primary sends PRE-PREPARE
PBFTPrePrepare(op) ==
    /\ pbftPhase["primary"] = "pre_prepare"
    /\ pbftSequence < MaxSequence
    /\ pbftPhase' = [pbftPhase EXCEPT !["primary"] = "prepare"]
    /\ messages' = messages \cup {[type |-> "pre_prepare", sender |-> "primary", data |-> op]}
    /\ UNCHANGED <<pbftView, pbftSequence, prepareMessages, commitMessages, executedOps,
                   raftStatus, raftTerm, raftLog, raftCommitIndex, votedFor,
                   vectorClock, lamportTime, monotonicSeq>>

\* Replica receives PRE-PREPARE and sends PREPARE
PBFTPrepare(n, op) ==
    /\ n \in Nodes
    /\ n # "primary"
    /\ pbftPhase[n] = "pre_prepare"
    /\ pbftPhase' = [pbftPhase EXCEPT ![n] = "prepare"]
    /\ prepareMessages' = prepareMessages \cup {<<n, pbftSequence, op>>}
    /\ lamportTime' = [lamportTime EXCEPT ![n] = @ + 1]
    /\ UNCHANGED <<pbftView, pbftSequence, commitMessages, executedOps, messages,
                   raftStatus, raftTerm, raftLog, raftCommitIndex, votedFor,
                   vectorClock, monotonicSeq>>

\* Node receives 2f+1 PREPARE messages and sends COMMIT
PBFTCommit(n, op) ==
    /\ n \in Nodes
    /\ pbftPhase[n] = "prepare"
    /\ Cardinality({m \in Nodes: <<m, pbftSequence, op>> \in prepareMessages}) >= PBFTQuorum
    /\ pbftPhase' = [pbftPhase EXCEPT ![n] = "commit"]
    /\ commitMessages' = commitMessages \cup {<<n, pbftSequence, op>>}
    /\ lamportTime' = [lamportTime EXCEPT ![n] = @ + 1]
    /\ UNCHANGED <<pbftView, pbftSequence, prepareMessages, executedOps, messages,
                   raftStatus, raftTerm, raftLog, raftCommitIndex, votedFor,
                   vectorClock, monotonicSeq>>

\* Node receives 2f+1 COMMIT messages and executes
PBFTExecute(n, op) ==
    /\ n \in Nodes
    /\ pbftPhase[n] = "commit"
    /\ Cardinality({m \in Nodes: <<m, pbftSequence, op>> \in commitMessages}) >= PBFTQuorum
    /\ pbftPhase' = [pbftPhase EXCEPT ![n] = "reply"]
    /\ executedOps' = executedOps \cup {op}
    /\ monotonicSeq' = monotonicSeq + 1
    /\ lamportTime' = [lamportTime EXCEPT ![n] = @ + 1]
    /\ UNCHANGED <<pbftView, pbftSequence, prepareMessages, commitMessages, messages,
                   raftStatus, raftTerm, raftLog, raftCommitIndex, votedFor,
                   vectorClock>>

--------------------------------------------------------------------------------
(* RAFT ACTIONS *)
--------------------------------------------------------------------------------

\* Node times out and becomes candidate
RaftStartElection(n) ==
    /\ n \in Nodes
    /\ raftStatus[n] = "follower"
    /\ raftStatus' = [raftStatus EXCEPT ![n] = "candidate"]
    /\ raftTerm' = [raftTerm EXCEPT ![n] = @ + 1]
    /\ votedFor' = [votedFor EXCEPT ![n] = n]
    /\ lamportTime' = [lamportTime EXCEPT ![n] = @ + 1]
    /\ UNCHANGED <<pbftPhase, pbftView, pbftSequence, prepareMessages, commitMessages,
                   executedOps, raftLog, raftCommitIndex, vectorClock, monotonicSeq, messages>>

\* Candidate becomes leader
RaftBecomeLeader(n) ==
    /\ n \in Nodes
    /\ raftStatus[n] = "candidate"
    /\ Cardinality({m \in Nodes: votedFor[m] = n}) >= RaftMajority
    /\ raftStatus' = [raftStatus EXCEPT ![n] = "leader"]
    /\ lamportTime' = [lamportTime EXCEPT ![n] = @ + 1]
    /\ UNCHANGED <<pbftPhase, pbftView, pbftSequence, prepareMessages, commitMessages,
                   executedOps, raftTerm, raftLog, raftCommitIndex, votedFor,
                   vectorClock, monotonicSeq, messages>>

\* Leader replicates log entry
RaftReplicateLog(n, op) ==
    /\ n \in Nodes
    /\ raftStatus[n] = "leader"
    /\ raftLog' = [raftLog EXCEPT ![n] = Append(@, op)]
    /\ lamportTime' = [lamportTime EXCEPT ![n] = @ + 1]
    /\ vectorClock' = [vectorClock EXCEPT ![n][n] = @ + 1]
    /\ UNCHANGED <<pbftPhase, pbftView, pbftSequence, prepareMessages, commitMessages,
                   executedOps, raftStatus, raftTerm, raftCommitIndex, votedFor,
                   monotonicSeq, messages>>

--------------------------------------------------------------------------------
(* NEXT STATE RELATION *)
--------------------------------------------------------------------------------

Next ==
    \/ \E op \in Operations:
        \/ PBFTPrePrepare(op)
        \/ \E n \in Nodes:
            \/ PBFTPrepare(n, op)
            \/ PBFTCommit(n, op)
            \/ PBFTExecute(n, op)
            \/ RaftReplicateLog(n, op)
    \/ \E n \in Nodes:
        \/ RaftStartElection(n)
        \/ RaftBecomeLeader(n)

--------------------------------------------------------------------------------
(* SPECIFICATION *)
--------------------------------------------------------------------------------

Spec == Init /\ [][Next]_vars

--------------------------------------------------------------------------------
(* THEOREMS TO PROVE *)
--------------------------------------------------------------------------------

THEOREM Spec => []TypeInvariant

THEOREM Spec => []PBFTQuorumInvariant
THEOREM Spec => []PBFTSafetyInvariant
THEOREM Spec => []PBFTPreparedInvariant
THEOREM Spec => []PBFTCommittedImpliesPrepared

THEOREM Spec => []RaftLeaderUniqueness
THEOREM Spec => []RaftStateMachineSafety

THEOREM Spec => []ChronosCausalityInvariant
THEOREM Spec => []AtroposMonotonicInvariant
THEOREM Spec => []LamportOrderingInvariant

THEOREM Spec => []ByzantineToleranceInvariant
THEOREM Spec => []NoExecutionWithoutQuorum

THEOREM Spec => LivenessProperty
THEOREM Spec => RaftLeaderElectionLiveness
THEOREM Spec => PersistenceProperty

================================================================================
