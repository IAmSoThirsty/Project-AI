-- Project-AI Sovereign Schema Implementation
-- Canonical DDL for regulator-ready data persistence

CREATE SCHEMA IF NOT EXISTS sovereign;

-- 1. Sovereign Intent Ledger (Governance Layer)
CREATE TABLE IF NOT EXISTS sovereign.intent_ledger (
    intent_hash CHAR(64) PRIMARY KEY,
    actor_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_resource TEXT NOT NULL,
    context_json JSONB,
    governance_verdict VARCHAR(20) CHECK (governance_verdict IN ('APPROVED', 'DENIED', 'PENDING')),
    tarl_version VARCHAR(50) NOT NULL,
    triumvirate_votes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_intent_hash_governance ON sovereign.intent_ledger(governance_verdict);

-- 2. Reflexive Audit Trail (Substrate Layer)
CREATE TABLE IF NOT EXISTS sovereign.reflex_audit (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    action_taken VARCHAR(50) NOT NULL,
    reason_code VARCHAR(100),
    logic_divergence BOOLEAN DEFAULT FALSE,
    substrate_signature BYTEA -- Ed25519 signature from OctoReflex
);

-- 3. Sovereign Vault Metadata
CREATE TABLE IF NOT EXISTS sovereign.vault_metadata (
    resource_id VARCHAR(255) PRIMARY KEY,
    owner_identity VARCHAR(255) NOT NULL,
    kms_key_arn TEXT NOT NULL,
    retention_policy VARCHAR(50) DEFAULT '7_YEARS_OBJECT_LOCK',
    access_control_list JSONB
);

-- Enforce absolute integrity constraints
ALTER TABLE sovereign.intent_ledger ADD CONSTRAINT intent_ledger_integrity CHECK (length(intent_hash) = 64);
