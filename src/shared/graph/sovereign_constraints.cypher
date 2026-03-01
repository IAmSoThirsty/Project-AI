// Project-AI Sovereign Graph Constraints
// Neo4j Cypher for Sovereign Enterprise Maturity (Phase 2)

// 1. Unique Identity Enforcement
CREATE CONSTRAINT identity_id_unique IF NOT EXISTS
FOR (i:Identity) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT public_key_unique IF NOT EXISTS
FOR (i:Identity) REQUIRE i.publicKey IS UNIQUE;

// 2. Sovereign Relationship Invariants
CREATE INDEX identity_role_idx IF NOT EXISTS
FOR (i:Identity) ON (i.role);

// 3. Event Chain Constraints
CREATE CONSTRAINT event_block_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.blockIndex IS UNIQUE;

CREATE CONSTRAINT event_hash_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.blockHash IS UNIQUE;

// 4. Governance Trust Graph
CREATE INDEX trust_level_idx IF NOT EXISTS
FOR ()-[r:TRUSTS]-() ON (r.level);
