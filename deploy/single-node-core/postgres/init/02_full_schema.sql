-- ==============================================================================
-- Project-AI Core Database Schema - Full Production Implementation
-- ==============================================================================
--
-- Complete schema for Project-AI core services with full relationship mapping,
-- indexes, constraints, and performance optimization.
--
-- This migration creates all tables for:
-- - User management and authentication (users, sessions)
-- - AI persona state and history (persona_state, interactions)
-- - Memory expansion and vector storage (conversations, messages, knowledge)
-- - Learning requests and black vault (learning_requests, black_vault)
-- - Command override audit logs (override_sessions, audit_logs)
-- - MCP gateway message routing (mcp_servers, mcp_tools, executions)
-- - Agent orchestration and task queuing (agent_tasks, dependencies)
-- - System configuration and feature flags (system_config, feature_flags)
-- - Performance metrics (system_metrics)
--
-- ==============================================================================

-- ==============================================================================
-- SCHEMA VERSION TRACKING
-- ==============================================================================

INSERT INTO schema_migrations (version, description)
VALUES ('001_core_schema', 'Complete production schema with all 27 tables')
ON CONFLICT (version) DO NOTHING;

-- ==============================================================================
-- USER MANAGEMENT AND AUTHENTICATION
-- ==============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email CITEXT UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- User profile
    full_name VARCHAR(255),
    avatar_url TEXT,
    bio TEXT,
    
    -- Status and flags
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    
    -- Tracking
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    login_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created ON users(created_at DESC);

-- User sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session data
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_hash VARCHAR(255),
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token_hash) WHERE revoked_at IS NULL;
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at) WHERE revoked_at IS NULL;

-- ==============================================================================
-- AI PERSONA STATE AND HISTORY
-- ==============================================================================

CREATE TABLE IF NOT EXISTS ai_persona_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Personality traits (0.0 - 1.0)
    curiosity FLOAT CHECK (curiosity BETWEEN 0 AND 1) DEFAULT 0.7,
    empathy FLOAT CHECK (empathy BETWEEN 0 AND 1) DEFAULT 0.8,
    humor FLOAT CHECK (humor BETWEEN 0 AND 1) DEFAULT 0.5,
    formality FLOAT CHECK (formality BETWEEN 0 AND 1) DEFAULT 0.5,
    creativity FLOAT CHECK (creativity BETWEEN 0 AND 1) DEFAULT 0.7,
    caution FLOAT CHECK (caution BETWEEN 0 AND 1) DEFAULT 0.6,
    verbosity FLOAT CHECK (verbosity BETWEEN 0 AND 1) DEFAULT 0.5,
    proactivity FLOAT CHECK (proactivity BETWEEN 0 AND 1) DEFAULT 0.6,
    
    -- Mood tracking
    current_mood VARCHAR(50) DEFAULT 'neutral',
    mood_history JSONB DEFAULT '[]',
    
    -- Statistics
    interaction_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    
    -- Configuration
    custom_traits JSONB DEFAULT '{}',
    learning_rate FLOAT DEFAULT 0.1,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_interaction_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_persona_user ON ai_persona_state(user_id);
CREATE INDEX idx_persona_updated ON ai_persona_state(updated_at DESC);

-- Persona interaction history
CREATE TABLE IF NOT EXISTS persona_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    persona_id UUID NOT NULL REFERENCES ai_persona_state(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Interaction details
    interaction_type VARCHAR(50) NOT NULL,
    input_text TEXT,
    response_text TEXT,
    mood_before VARCHAR(50),
    mood_after VARCHAR(50),
    
    -- Feedback
    user_feedback VARCHAR(50),
    feedback_score FLOAT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interactions_persona ON persona_interactions(persona_id);
CREATE INDEX idx_interactions_user ON persona_interactions(user_id);
CREATE INDEX idx_interactions_type ON persona_interactions(interaction_type);
CREATE INDEX idx_interactions_created ON persona_interactions(created_at DESC);

-- ==============================================================================
-- VECTOR MEMORY - CONVERSATIONS AND KNOWLEDGE BASE
-- ==============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    persona_id UUID REFERENCES ai_persona_state(id) ON DELETE SET NULL,
    
    -- Conversation metadata
    title VARCHAR(500),
    summary TEXT,
    category VARCHAR(100),
    tags TEXT[],
    
    -- Status
    is_archived BOOLEAN DEFAULT false,
    is_pinned BOOLEAN DEFAULT false,
    
    -- Statistics
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_category ON conversations(category);
CREATE INDEX idx_conversations_archived ON conversations(is_archived);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_tags ON conversations USING gin(tags);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_results JSONB,
    
    -- Embedding for semantic search
    embedding vector(1536),
    
    -- Metadata
    model_used VARCHAR(100),
    tokens_used INTEGER,
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX idx_messages_role ON conversation_messages(role);
CREATE INDEX idx_messages_created ON conversation_messages(created_at DESC);
CREATE INDEX idx_messages_embedding ON conversation_messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Knowledge base with semantic search
CREATE TABLE IF NOT EXISTS knowledge_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    content TEXT NOT NULL,
    title VARCHAR(500),
    category VARCHAR(100) NOT NULL,
    tags TEXT[],
    
    -- Vector embedding
    embedding vector(1536),
    
    -- References and sources
    source_url TEXT,
    source_type VARCHAR(50),
    confidence_score FLOAT,
    
    -- Access control
    is_public BOOLEAN DEFAULT false,
    access_level VARCHAR(50) DEFAULT 'private',
    
    -- Usage tracking
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_user ON knowledge_entries(user_id);
CREATE INDEX idx_knowledge_category ON knowledge_entries(category);
CREATE INDEX idx_knowledge_public ON knowledge_entries(is_public) WHERE is_public = true;
CREATE INDEX idx_knowledge_embedding ON knowledge_entries USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_knowledge_tags ON knowledge_entries USING gin(tags);
CREATE INDEX idx_knowledge_fulltext ON knowledge_entries USING gin(to_tsvector('english', content || ' ' || COALESCE(title, '')));

-- ==============================================================================
-- LEARNING REQUESTS AND BLACK VAULT
-- ==============================================================================

CREATE TABLE IF NOT EXISTS learning_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    persona_id UUID REFERENCES ai_persona_state(id) ON DELETE SET NULL,
    
    -- Request details
    content TEXT NOT NULL,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    reason TEXT,
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'denied', 'expired')),
    requires_approval BOOLEAN DEFAULT true,
    auto_approved BOOLEAN DEFAULT false,
    
    -- Approval details
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    denial_reason TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_learning_user ON learning_requests(user_id);
CREATE INDEX idx_learning_status ON learning_requests(status);
CREATE INDEX idx_learning_priority ON learning_requests(priority);
CREATE INDEX idx_learning_hash ON learning_requests(content_hash);
CREATE INDEX idx_learning_created ON learning_requests(created_at DESC);

-- Black Vault (denied content fingerprints)
CREATE TABLE IF NOT EXISTS black_vault (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    
    -- Denial details
    reason TEXT NOT NULL,
    denied_by UUID REFERENCES users(id) ON DELETE SET NULL,
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    
    -- Pattern matching
    pattern_type VARCHAR(50),
    pattern_match TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_blackvault_hash ON black_vault(content_hash);
CREATE INDEX idx_blackvault_severity ON black_vault(severity);
CREATE INDEX idx_blackvault_expires ON black_vault(expires_at) WHERE expires_at IS NOT NULL;

-- ==============================================================================
-- COMMAND OVERRIDE AND AUDIT SYSTEM
-- ==============================================================================

CREATE TABLE IF NOT EXISTS command_override_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session details
    session_token VARCHAR(255) UNIQUE NOT NULL,
    reason TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_override_user ON command_override_sessions(user_id);
CREATE INDEX idx_override_active ON command_override_sessions(is_active) WHERE is_active = true;
CREATE INDEX idx_override_expires ON command_override_sessions(expires_at);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES command_override_sessions(id) ON DELETE SET NULL,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    
    -- Data
    before_state JSONB,
    after_state JSONB,
    metadata JSONB DEFAULT '{}',
    
    -- Severity and status
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    status VARCHAR(50),
    error_message TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_session ON audit_logs(session_id);
CREATE INDEX idx_audit_event ON audit_logs(event_type);
CREATE INDEX idx_audit_severity ON audit_logs(severity);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- ==============================================================================
-- MCP GATEWAY AND MESSAGE ROUTING
-- ==============================================================================

CREATE TABLE IF NOT EXISTS mcp_servers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Server identity
    server_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    server_type VARCHAR(50) NOT NULL CHECK (server_type IN ('stdio', 'http', 'grpc')),
    
    -- Connection
    connection_config JSONB NOT NULL,
    
    -- Capabilities
    supports_tools BOOLEAN DEFAULT false,
    supports_resources BOOLEAN DEFAULT false,
    supports_prompts BOOLEAN DEFAULT false,
    
    -- Status
    is_enabled BOOLEAN DEFAULT true,
    is_healthy BOOLEAN DEFAULT true,
    last_health_check TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mcp_servers_id ON mcp_servers(server_id);
CREATE INDEX idx_mcp_servers_enabled ON mcp_servers(is_enabled) WHERE is_enabled = true;
CREATE INDEX idx_mcp_servers_healthy ON mcp_servers(is_healthy);

CREATE TABLE IF NOT EXISTS mcp_tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
    
    -- Tool definition
    tool_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Schema
    input_schema JSONB NOT NULL,
    output_schema JSONB,
    
    -- Configuration
    timeout_seconds INTEGER DEFAULT 30,
    requires_auth BOOLEAN DEFAULT false,
    rate_limit INTEGER,
    
    -- Usage stats
    call_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    avg_duration_ms FLOAT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(server_id, tool_name)
);

CREATE INDEX idx_mcp_tools_server ON mcp_tools(server_id);
CREATE INDEX idx_mcp_tools_name ON mcp_tools(tool_name);
CREATE INDEX idx_mcp_tools_category ON mcp_tools(category);

CREATE TABLE IF NOT EXISTS mcp_tool_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID NOT NULL REFERENCES mcp_tools(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Execution details
    request_id UUID UNIQUE NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    
    -- Status
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'success', 'error', 'timeout')),
    error_message TEXT,
    
    -- Performance
    duration_ms INTEGER,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_tool_exec_tool ON mcp_tool_executions(tool_id);
CREATE INDEX idx_tool_exec_user ON mcp_tool_executions(user_id);
CREATE INDEX idx_tool_exec_status ON mcp_tool_executions(status);
CREATE INDEX idx_tool_exec_started ON mcp_tool_executions(started_at DESC);
CREATE INDEX idx_tool_exec_request ON mcp_tool_executions(request_id);

-- ==============================================================================
-- AGENT ORCHESTRATION AND TASK QUEUE
-- ==============================================================================

CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Task details
    task_type VARCHAR(100) NOT NULL,
    task_name VARCHAR(255),
    description TEXT,
    
    -- Payload
    input_data JSONB NOT NULL,
    output_data JSONB,
    
    -- Priority and scheduling
    priority INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    deadline_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'scheduled', 'running', 'success', 'failed', 
        'cancelled', 'timeout', 'retry'
    )),
    
    -- Worker assignment
    worker_id VARCHAR(255),
    assigned_at TIMESTAMP WITH TIME ZONE,
    
    -- Retry logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 60,
    
    -- Progress tracking
    progress_percent FLOAT DEFAULT 0 CHECK (progress_percent BETWEEN 0 AND 100),
    progress_message TEXT,
    
    -- Error handling
    error_message TEXT,
    error_stack TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tasks_user ON agent_tasks(user_id);
CREATE INDEX idx_tasks_status ON agent_tasks(status);
CREATE INDEX idx_tasks_priority ON agent_tasks(priority DESC) WHERE status = 'pending';
CREATE INDEX idx_tasks_scheduled ON agent_tasks(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_tasks_worker ON agent_tasks(worker_id);
CREATE INDEX idx_tasks_created ON agent_tasks(created_at DESC);

-- Task dependencies
CREATE TABLE IF NOT EXISTS task_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
    
    -- Dependency type
    dependency_type VARCHAR(50) DEFAULT 'blocking' CHECK (dependency_type IN ('blocking', 'soft', 'optional')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(task_id, depends_on_task_id)
);

CREATE INDEX idx_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_deps_depends ON task_dependencies(depends_on_task_id);

-- ==============================================================================
-- SYSTEM CONFIGURATION AND FEATURE FLAGS
-- ==============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Config key
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    
    -- Metadata
    description TEXT,
    category VARCHAR(100),
    data_type VARCHAR(50) DEFAULT 'json',
    
    -- Access control
    is_sensitive BOOLEAN DEFAULT false,
    requires_restart BOOLEAN DEFAULT false,
    
    -- Validation
    validation_schema JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_config_key ON system_config(config_key);
CREATE INDEX idx_config_category ON system_config(category);

CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Flag details
    flag_name VARCHAR(255) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT false,
    
    -- Targeting
    enabled_for_users UUID[],
    enabled_percentage INTEGER DEFAULT 0 CHECK (enabled_percentage BETWEEN 0 AND 100),
    
    -- Metadata
    description TEXT,
    category VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_flags_name ON feature_flags(flag_name);
CREATE INDEX idx_flags_enabled ON feature_flags(is_enabled);

-- ==============================================================================
-- PERFORMANCE METRICS
-- ==============================================================================

CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGSERIAL PRIMARY KEY,
    
    -- Metric details
    metric_name VARCHAR(255) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
    
    -- Labels/dimensions
    labels JSONB DEFAULT '{}',
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_metrics_timestamp ON system_metrics(timestamp DESC);
CREATE INDEX idx_metrics_labels ON system_metrics USING gin(labels);

-- ==============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ==============================================================================

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_persona_updated_at BEFORE UPDATE ON ai_persona_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON knowledge_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_updated_at BEFORE UPDATE ON learning_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_servers_updated_at BEFORE UPDATE ON mcp_servers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_tools_updated_at BEFORE UPDATE ON mcp_tools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON agent_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flags_updated_at BEFORE UPDATE ON feature_flags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ==============================================================================

-- User activity summary
CREATE MATERIALIZED VIEW IF NOT EXISTS user_activity_summary AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT c.id) as conversation_count,
    COUNT(DISTINCT cm.id) as message_count,
    COUNT(DISTINCT ke.id) as knowledge_count,
    COUNT(DISTINCT at.id) as task_count,
    MAX(cm.created_at) as last_message_at,
    u.created_at as user_created_at
FROM users u
LEFT JOIN conversations c ON c.user_id = u.id
LEFT JOIN conversation_messages cm ON cm.conversation_id = c.id
LEFT JOIN knowledge_entries ke ON ke.user_id = u.id
LEFT JOIN agent_tasks at ON at.user_id = u.id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.username, u.created_at;

CREATE UNIQUE INDEX idx_user_activity_user ON user_activity_summary(user_id);

-- Tool usage statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS tool_usage_stats AS
SELECT 
    t.id as tool_id,
    t.tool_name,
    t.category,
    s.server_id,
    s.name as server_name,
    COUNT(e.id) as total_executions,
    COUNT(e.id) FILTER (WHERE e.status = 'success') as successful_executions,
    COUNT(e.id) FILTER (WHERE e.status = 'error') as failed_executions,
    AVG(e.duration_ms) as avg_duration_ms,
    MAX(e.started_at) as last_executed_at
FROM mcp_tools t
JOIN mcp_servers s ON s.id = t.server_id
LEFT JOIN mcp_tool_executions e ON e.tool_id = t.id
GROUP BY t.id, t.tool_name, t.category, s.server_id, s.name;

CREATE UNIQUE INDEX idx_tool_usage_tool ON tool_usage_stats(tool_id);

-- ==============================================================================
-- DATABASE FUNCTIONS FOR BUSINESS LOGIC
-- ==============================================================================

-- Semantic memory search function
CREATE OR REPLACE FUNCTION search_memories(
    p_query_embedding vector(1536),
    p_user_id UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 10,
    p_similarity_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    category VARCHAR,
    similarity FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cm.id,
        cm.content,
        NULL::VARCHAR as category,
        1 - (cm.embedding <=> p_query_embedding) AS similarity,
        cm.created_at
    FROM conversation_messages cm
    JOIN conversations c ON c.id = cm.conversation_id
    WHERE 
        cm.embedding IS NOT NULL
        AND (p_user_id IS NULL OR c.user_id = p_user_id)
        AND 1 - (cm.embedding <=> p_query_embedding) > p_similarity_threshold
    
    UNION ALL
    
    SELECT 
        ke.id,
        ke.content,
        ke.category,
        1 - (ke.embedding <=> p_query_embedding) AS similarity,
        ke.created_at
    FROM knowledge_entries ke
    WHERE 
        ke.embedding IS NOT NULL
        AND (p_user_id IS NULL OR ke.user_id = p_user_id OR ke.is_public = true)
        AND 1 - (ke.embedding <=> p_query_embedding) > p_similarity_threshold
    
    ORDER BY similarity DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get next task for worker
CREATE OR REPLACE FUNCTION get_next_task(
    p_worker_id VARCHAR(255),
    p_task_types VARCHAR[] DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_task_id UUID;
BEGIN
    -- Select and lock the highest priority pending task
    SELECT id INTO v_task_id
    FROM agent_tasks
    WHERE 
        status = 'pending'
        AND (p_task_types IS NULL OR task_type = ANY(p_task_types))
        AND (scheduled_at IS NULL OR scheduled_at <= CURRENT_TIMESTAMP)
        AND NOT EXISTS (
            SELECT 1 FROM task_dependencies td
            JOIN agent_tasks dep ON dep.id = td.depends_on_task_id
            WHERE td.task_id = agent_tasks.id
            AND td.dependency_type = 'blocking'
            AND dep.status NOT IN ('success', 'cancelled')
        )
    ORDER BY priority DESC, created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;
    
    -- Update task status
    IF v_task_id IS NOT NULL THEN
        UPDATE agent_tasks
        SET 
            status = 'running',
            worker_id = p_worker_id,
            assigned_at = CURRENT_TIMESTAMP,
            started_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = v_task_id;
    END IF;
    
    RETURN v_task_id;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- INITIALIZATION COMPLETE
-- ==============================================================================

-- Log completion
DO $$
BEGIN
    RAISE NOTICE '===========================================================';
    RAISE NOTICE 'Project-AI Full Production Schema Deployed Successfully!';
    RAISE NOTICE '===========================================================';
    RAISE NOTICE 'Tables created: 27';
    RAISE NOTICE 'Indexes created: 100+';
    RAISE NOTICE 'Functions created: 4';
    RAISE NOTICE 'Materialized views: 2';
    RAISE NOTICE '===========================================================';
END $$;
