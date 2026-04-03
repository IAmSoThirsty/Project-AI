-- Project-AI Sovereign Governance Registry
-- SQL DDL for Sovereign Enterprise Maturity (Phase 2)

-- 1. Sovereign Identity Registry (Ed25519 Public Keys)
CREATE TABLE IF NOT EXISTS sovereign_identities (
    identity_id UUID PRIMARY KEY,
    public_key_hex TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT CHECK (role IN ('ADMIN', 'VERIFIER', 'ISSUER', 'USER')),
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_signed_at TIMESTAMP WITH TIME ZONE,
    
    -- Sovereign Metadata
    thirsty_metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_identities_role ON sovereign_identities(role);

-- 2. Immutable Event Registry
CREATE TABLE IF NOT EXISTS sovereign_events (
    event_id UUID PRIMARY KEY,
    block_index BIGINT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    payload BYTEA NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Dual-Plane Verification Hashes
    canonical_hash BYTEA NOT NULL,
    shadow_hash BYTEA NOT NULL,
    
    -- Proof verification
    signature BYTEA NOT NULL,
    signer_id UUID REFERENCES sovereign_identities(identity_id),
    
    -- Chain integrity
    previous_block_hash BYTEA NOT NULL,
    block_hash BYTEA NOT NULL UNIQUE
);

CREATE INDEX idx_events_type ON sovereign_events(event_type);
CREATE INDEX idx_events_timestamp ON sovereign_events(timestamp);

-- 3. Invariant Violation Log (Circuit Breaker)
CREATE TABLE IF NOT EXISTS invariant_violations (
    violation_id UUID PRIMARY KEY,
    event_id UUID REFERENCES sovereign_events(event_id),
    primary_state JSONB NOT NULL,
    shadow_state JSONB NOT NULL,
    divergence_details TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);
