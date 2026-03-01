--------------------------- MODULE audit_chain_verification ---------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS 
    Nodes,           \* Set of nodes participating in the chain
    MaxChainLength   \* Maximum length of the audit chain to check

VARIABLES 
    chain,           \* The sequence of audit blocks
    state_diverged   \* Boolean: has the shadow plane diverged?

-------------------------------------------------------------------------------------

\* A block consists of an index and a hash of (data + previous_hash)
Block(i, prev_hash, data) == [index |-> i, prev_hash |-> prev_hash, hash |-> (data + prev_hash)]

\* Initial state: chain is empty or has a genesis block
Init == 
    /\ chain = <<Block(0, 0, 100)>>
    /\ state_diverged = FALSE

\* Step: Add a block with dual-plane verification
AddBlock(node, data) ==
    LET prev_block == Last(chain)
        new_index == prev_block.index + 1
        canonical_hash == data + prev_block.hash
        shadow_hash == data + prev_block.hash \* Shadow plane simulation
    IN 
    /\ ~state_diverged
    /\ Len(chain) < MaxChainLength
    /\ IF canonical_hash = shadow_hash
       THEN chain' = Append(chain, Block(new_index, prev_block.hash, data)) /\ UNCHANGED state_diverged
       ELSE chain' = chain /\ state_diverged' = TRUE

Next == \E n \in Nodes, d \in {101, 102} : AddBlock(n, d)

-------------------------------------------------------------------------------------

\* INVARIANTS

\* 1. Hash Chain Integrity: Each block's prev_hash must match the hash of the preceding block.
ChainIntact == 
    \A i \in 2..Len(chain) : chain[i].prev_hash = chain[i-1].hash

\* 2. No Divergence: If the chain grows, the planes must have agreed.
NoUnnoticedDivergence == 
    state_diverged = FALSE => ChainIntact

=============================================================================
