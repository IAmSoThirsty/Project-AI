-- ==============================================================================
-- PostgreSQL Initialization Script - Project-AI Core Stack
-- ==============================================================================
--
-- This script initializes the PostgreSQL database with required extensions
-- and configurations for the Project-AI core stack.
--
-- Extensions installed:
-- 1. pgvector - Vector similarity search for AI embeddings and memory
-- 2. pg_trgm - Trigram-based text similarity and fuzzy search
-- 3. pg_stat_statements - Query performance tracking
-- 4. uuid-ossp - UUID generation for distributed systems
-- 5. hstore - Key-value storage for flexible metadata
--
-- ==============================================================================

-- Enable required extensions
-- Note: Extensions must be created by a superuser or database owner

-- ==============================================================================
-- 1. PGVECTOR - Vector Similarity Search
-- ==============================================================================
-- Used for:
-- - AI conversation embeddings and semantic search
-- - Long-term memory storage with vector similarity
-- - Knowledge base similarity matching
-- - Document and code embedding search
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify pgvector installation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        RAISE NOTICE 'pgvector extension installed successfully';
    ELSE
        RAISE EXCEPTION 'Failed to install pgvector extension';
    END IF;
END $$;

-- ==============================================================================
-- 2. PG_TRGM - Trigram Text Search
-- ==============================================================================
-- Used for:
-- - Fuzzy text search in conversations and knowledge base
-- - Autocomplete and typo-tolerant search
-- - Similar string matching
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify pg_trgm installation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'
    ) THEN
        RAISE NOTICE 'pg_trgm extension installed successfully';
    ELSE
        RAISE EXCEPTION 'Failed to install pg_trgm extension';
    END IF;
END $$;

-- ==============================================================================
-- 3. PG_STAT_STATEMENTS - Query Performance Tracking
-- ==============================================================================
-- Used for:
-- - Query performance monitoring
-- - Slow query identification
-- - Database optimization
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Verify pg_stat_statements installation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
    ) THEN
        RAISE NOTICE 'pg_stat_statements extension installed successfully';
    ELSE
        RAISE WARNING 'pg_stat_statements extension not installed - may need shared_preload_libraries';
    END IF;
END $$;

-- ==============================================================================
-- 4. UUID-OSSP - UUID Generation
-- ==============================================================================
-- Used for:
-- - Distributed unique identifiers
-- - Cross-service entity references
-- - Secure random identifiers
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify uuid-ossp installation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp'
    ) THEN
        RAISE NOTICE 'uuid-ossp extension installed successfully';
    ELSE
        RAISE EXCEPTION 'Failed to install uuid-ossp extension';
    END IF;
END $$;

-- ==============================================================================
-- 5. HSTORE - Key-Value Store
-- ==============================================================================
-- Used for:
-- - Flexible metadata storage
-- - Dynamic schema attributes
-- - Configuration key-value pairs
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS hstore;

-- Verify hstore installation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'hstore'
    ) THEN
        RAISE NOTICE 'hstore extension installed successfully';
    ELSE
        RAISE EXCEPTION 'Failed to install hstore extension';
    END IF;
END $$;

-- ==============================================================================
-- 6. CITEXT - Case-Insensitive Text
-- ==============================================================================
-- Used for:
-- - Case-insensitive email addresses
-- - Username comparisons
-- - Case-insensitive unique constraints
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS citext;

-- ==============================================================================
-- DATABASE CONFIGURATION
-- ==============================================================================

-- Set timezone to UTC for consistency
SET timezone = 'UTC';

-- Configure search path
ALTER DATABASE project_ai SET search_path TO public;

-- ==============================================================================
-- CORE SCHEMA TABLES (Future migration will create application tables)
-- ==============================================================================

-- Create schema version tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Record this initialization
INSERT INTO schema_migrations (version, description)
VALUES ('00_init_extensions', 'Initial extension setup: pgvector, pg_trgm, uuid-ossp, hstore, citext')
ON CONFLICT (version) DO NOTHING;

-- ==============================================================================
-- EXAMPLE VECTOR MEMORY TABLE (demonstrating pgvector usage)
-- ==============================================================================

-- Create vector memory table for AI conversation embeddings
-- This is an example - actual schema will be created by application migrations
CREATE TABLE IF NOT EXISTS vector_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS vector_memory_embedding_idx 
    ON vector_memory 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create index for metadata filtering
CREATE INDEX IF NOT EXISTS vector_memory_metadata_idx 
    ON vector_memory 
    USING gin (metadata);

-- Create index for conversation lookup
CREATE INDEX IF NOT EXISTS vector_memory_conversation_idx 
    ON vector_memory (conversation_id);

-- Create index for full-text search with pg_trgm
CREATE INDEX IF NOT EXISTS vector_memory_content_trgm_idx 
    ON vector_memory 
    USING gin (content gin_trgm_ops);

-- ==============================================================================
-- HELPER FUNCTIONS
-- ==============================================================================

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to vector_memory table
CREATE TRIGGER update_vector_memory_updated_at
    BEFORE UPDATE ON vector_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function for similarity search (example usage of pgvector)
CREATE OR REPLACE FUNCTION search_similar_memories(
    query_embedding vector(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity FLOAT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vm.id,
        vm.content,
        1 - (vm.embedding <=> query_embedding) AS similarity,
        vm.metadata
    FROM vector_memory vm
    WHERE 1 - (vm.embedding <=> query_embedding) > similarity_threshold
    ORDER BY vm.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function for fuzzy text search (example usage of pg_trgm)
CREATE OR REPLACE FUNCTION search_fuzzy_text(
    search_query TEXT,
    similarity_threshold FLOAT DEFAULT 0.3,
    max_results INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vm.id,
        vm.content,
        similarity(vm.content, search_query) AS similarity
    FROM vector_memory vm
    WHERE similarity(vm.content, search_query) > similarity_threshold
    ORDER BY similarity(vm.content, search_query) DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- PERFORMANCE TUNING
-- ==============================================================================

-- Analyze tables to update statistics
ANALYZE vector_memory;

-- ==============================================================================
-- VERIFICATION
-- ==============================================================================

-- Verify all extensions are installed
DO $$
DECLARE
    ext_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO ext_count
    FROM pg_extension
    WHERE extname IN ('vector', 'pg_trgm', 'pg_stat_statements', 'uuid-ossp', 'hstore', 'citext');
    
    RAISE NOTICE 'Installed % out of 6 required extensions', ext_count;
    
    IF ext_count < 5 THEN
        RAISE WARNING 'Not all extensions were installed. Check PostgreSQL logs.';
    END IF;
END $$;

-- Display extension versions
SELECT 
    extname AS extension,
    extversion AS version,
    'Installed' AS status
FROM pg_extension
WHERE extname IN ('vector', 'pg_trgm', 'pg_stat_statements', 'uuid-ossp', 'hstore', 'citext')
ORDER BY extname;

-- ==============================================================================
-- INITIALIZATION COMPLETE
-- ==============================================================================

-- Log completion
DO $$
BEGIN
    RAISE NOTICE '=============================================================';
    RAISE NOTICE 'Project-AI PostgreSQL initialization complete!';
    RAISE NOTICE '=============================================================';
    RAISE NOTICE 'Extensions installed: pgvector, pg_trgm, pg_stat_statements, uuid-ossp, hstore, citext';
    RAISE NOTICE 'Example tables created: vector_memory, schema_migrations';
    RAISE NOTICE 'Helper functions created: search_similar_memories, search_fuzzy_text';
    RAISE NOTICE '=============================================================';
END $$;
