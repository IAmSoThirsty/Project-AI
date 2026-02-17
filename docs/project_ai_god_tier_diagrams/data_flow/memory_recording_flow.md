# Memory Recording Flow - Five-Channel Architecture

## Overview

The Memory Recording Flow implements a five-channel recording system that captures comprehensive context for every operation in Project-AI. This architecture enables complete operational transparency, learning from past interactions, and deterministic behavior replay.

## Five-Channel Architecture

```
                    ┌──────────────────────────────────┐
                    │     MEMORY ENGINE                │
                    │  Five-Channel Recording System   │
                    └──────────────────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
   ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
   │   ATTEMPT       │   │   DECISION      │   │    RESULT       │
   │   Channel       │   │   Channel       │   │   Channel       │
   │                 │   │                 │   │                 │
   │ • User request  │   │ • Governance    │   │ • Execution     │
   │ • Intent        │   │   decisions     │   │   output        │
   │ • Context       │   │ • Approval/     │   │ • Status code   │
   │ • Timestamp     │   │   Rejection     │   │ • Side effects  │
   │ • Entities      │   │ • Rationale     │   │ • Duration      │
   └─────────────────┘   └─────────────────┘   └─────────────────┘
            │                      │                      │
            │             ┌────────▼────────┐   ┌────────▼────────┐
            │             │  REFLECTION     │   │    ERROR        │
            │             │   Channel       │   │   Channel       │
            │             │                 │   │                 │
            │             │ • Post-exec     │   │ • Exceptions    │
            │             │   analysis      │   │ • Stack traces  │
            │             │ • Learning      │   │ • Recovery      │
            │             │ • Improvements  │   │   actions       │
            │             │ • Insights      │   │ • Root cause    │
            │             └─────────────────┘   └─────────────────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   ↓
                    ┌──────────────────────────────────┐
                    │    POSTGRESQL DATABASE           │
                    │                                  │
                    │  • memory_records table          │
                    │  • Indexed by operation_id       │
                    │  • Partitioned by timestamp      │
                    │  • JSONB columns for flexibility │
                    └──────────────────────────────────┘
```

## Channel Definitions

### Channel 1: Attempt

**Purpose**: Record the initial user request before any processing.

**Data Captured**:

```python
{
    "operation_id": "uuid-v4",
    "channel": "attempt",
    "timestamp": "2024-01-15T10:30:00.123Z",
    "user_id": "user-uuid",
    "session_id": "session-uuid",
    "request": {
        "content": "natural language request",
        "type": "command|query|analysis",
        "intent": "detected_intent",
        "confidence": 0.95,
        "entities": [
            {"type": "person", "value": "John", "span": [10, 14]},
            {"type": "date", "value": "2024-01-15", "span": [20, 30]}
        ]
    },
    "context": {
        "previous_operations": ["op-uuid-1", "op-uuid-2"],
        "user_preferences": {},
        "persona_state": {
            "mood": "curious",
            "energy": 0.8
        },
        "environmental": {
            "platform": "desktop",
            "client_version": "1.0.0",
            "network_quality": "excellent"
        }
    },
    "metadata": {
        "source": "gui|api|cli|websocket",
        "client_ip": "192.168.1.100",
        "user_agent": "ProjectAI-Desktop/1.0.0"
    }
}
```

**Database Schema**:

```sql
CREATE TABLE memory_attempt (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id UUID NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Request data (JSONB for flexibility)
    content TEXT NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    intent VARCHAR(100),
    confidence NUMERIC(3,2),
    entities JSONB,

    -- Context data
    context JSONB NOT NULL,
    previous_operations UUID[],

    -- Metadata
    source VARCHAR(20) NOT NULL,
    client_ip INET,
    user_agent TEXT,

    -- Indexes
    CONSTRAINT valid_request_type CHECK (request_type IN ('command', 'query', 'analysis'))
);

-- Indexes for fast retrieval
CREATE INDEX idx_attempt_operation_id ON memory_attempt(operation_id);
CREATE INDEX idx_attempt_user_id ON memory_attempt(user_id);
CREATE INDEX idx_attempt_timestamp ON memory_attempt(timestamp DESC);
CREATE INDEX idx_attempt_intent ON memory_attempt(intent);
CREATE INDEX idx_attempt_session ON memory_attempt(session_id);

-- GIN index for JSONB queries
CREATE INDEX idx_attempt_entities ON memory_attempt USING GIN (entities);
CREATE INDEX idx_attempt_context ON memory_attempt USING GIN (context);

-- Partitioning by month for performance
CREATE TABLE memory_attempt_2024_01 PARTITION OF memory_attempt
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**Recording Logic**:

```python
async def record_attempt(operation_id: str, request: EnrichedRequest) -> AttemptRecord:
    """Record initial user request to attempt channel."""

    attempt_data = {
        'operation_id': operation_id,
        'channel': 'attempt',
        'timestamp': datetime.utcnow(),
        'user_id': request.user_id,
        'session_id': request.session_id,
        'request': {
            'content': request.content,
            'type': request.type,
            'intent': request.intent.intent,
            'confidence': request.intent.confidence,
            'entities': [e.to_dict() for e in request.intent.entities]
        },
        'context': request.context,
        'metadata': {
            'source': request.source,
            'client_ip': request.client_ip,
            'user_agent': request.user_agent
        }
    }

    # Write to database

    async with db.transaction():
        record_id = await db.execute(
            """
            INSERT INTO memory_attempt
            (operation_id, user_id, session_id, timestamp, content, request_type,
             intent, confidence, entities, context, source, client_ip, user_agent)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id
            """,
            operation_id, request.user_id, request.session_id, attempt_data['timestamp'],
            request.content, request.type, request.intent.intent, request.intent.confidence,
            json.dumps([e.to_dict() for e in request.intent.entities]),
            json.dumps(request.context), request.source, request.client_ip, request.user_agent
        )

    logger.info(f"Recorded attempt for operation {operation_id}")

    return AttemptRecord(id=record_id, **attempt_data)
```

### Channel 2: Decision

**Purpose**: Record governance decisions from the Triumvirate.

**Data Captured**:

```python
{
    "operation_id": "uuid-v4",
    "channel": "decision",
    "timestamp": "2024-01-15T10:30:00.500Z",
    "governance_chain": {
        "galahad": {
            "approved": true,
            "decision_time_ms": 25,
            "confidence": 0.95,
            "laws_checked": ["law_0", "law_1", "law_2", "law_3"],
            "law_violated": null,
            "reason": "All ethical validations passed",
            "rationale": "detailed explanation...",
            "escalation_required": false
        },
        "cerberus": {
            "approved": true,
            "decision_time_ms": 38,
            "security_score": 0.92,
            "checks_performed": 10,
            "threats_detected": [],
            "reason": "All security validations passed",
            "security_incident": false
        },
        "codex": {
            "approved": true,
            "decision_time_ms": 27,
            "policies_checked": ["data_retention", "access_control", "compliance"],
            "policy_violations": [],
            "compliance_status": {
                "GDPR": "compliant",
                "HIPAA": "compliant",
                "SOC2": "compliant"
            },
            "approval_hash": "sha256_hash_here",
            "valid_until": "2024-01-15T10:35:00Z",
            "reason": "All governance validations passed"
        }
    },
    "final_decision": {
        "approved": true,
        "total_time_ms": 90,
        "approval_hash": "sha256_hash_here",
        "rejection_layer": null,
        "rejection_reason": null
    }
}
```

**Database Schema**:

```sql
CREATE TABLE memory_decision (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id UUID NOT NULL REFERENCES memory_attempt(operation_id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Galahad (Ethics) decision
    galahad_approved BOOLEAN NOT NULL,
    galahad_confidence NUMERIC(3,2),
    galahad_reason TEXT,
    galahad_law_violated VARCHAR(10),
    galahad_time_ms INTEGER,

    -- Cerberus (Security) decision
    cerberus_approved BOOLEAN NOT NULL,
    cerberus_security_score NUMERIC(3,2),
    cerberus_checks_performed INTEGER,
    cerberus_security_incident BOOLEAN DEFAULT FALSE,
    cerberus_reason TEXT,
    cerberus_time_ms INTEGER,

    -- Codex (Policy) decision
    codex_approved BOOLEAN NOT NULL,
    codex_approval_hash VARCHAR(64),
    codex_valid_until TIMESTAMPTZ,
    codex_reason TEXT,
    codex_time_ms INTEGER,

    -- Final decision
    final_approved BOOLEAN NOT NULL,
    total_time_ms INTEGER,
    rejection_layer VARCHAR(20),
    rejection_reason TEXT,

    -- Full governance chain (JSONB)
    governance_chain JSONB NOT NULL,

    CONSTRAINT valid_rejection_layer CHECK (
        rejection_layer IS NULL OR rejection_layer IN ('galahad', 'cerberus', 'codex')
    )
);

CREATE INDEX idx_decision_operation_id ON memory_decision(operation_id);
CREATE INDEX idx_decision_timestamp ON memory_decision(timestamp DESC);
CREATE INDEX idx_decision_approved ON memory_decision(final_approved);
CREATE INDEX idx_decision_rejection_layer ON memory_decision(rejection_layer);
CREATE INDEX idx_decision_governance ON memory_decision USING GIN (governance_chain);
```

**Recording Logic**:

```python
async def record_decision(operation_id: str,
                         galahad: GalahadDecision,
                         cerberus: CerberusDecision,
                         codex: FinalDecision) -> DecisionRecord:
    """Record governance decision to decision channel."""

    governance_chain = {
        'galahad': {
            'approved': galahad.approved,
            'decision_time_ms': galahad.decision_time_ms,
            'confidence': galahad.confidence,
            'laws_checked': galahad.laws_checked,
            'law_violated': galahad.law_violated,
            'reason': galahad.reason,
            'rationale': galahad.rationale,
            'escalation_required': galahad.escalate_to_human
        },
        'cerberus': {
            'approved': cerberus.approved,
            'decision_time_ms': cerberus.decision_time_ms,
            'security_score': cerberus.security_score,
            'checks_performed': cerberus.checks_performed,
            'threats_detected': cerberus.threats_detected,
            'reason': cerberus.reason,
            'security_incident': cerberus.security_incident
        },
        'codex': {
            'approved': codex.approved,
            'decision_time_ms': codex.decision_time_ms,
            'approval_hash': codex.approval_hash,
            'valid_until': codex.valid_until,
            'reason': codex.reason,
            'compliance_status': codex.compliance_status
        }
    }

    final_decision = {
        'approved': codex.approved,
        'total_time_ms': sum([
            galahad.decision_time_ms,
            cerberus.decision_time_ms,
            codex.decision_time_ms
        ]),
        'approval_hash': codex.approval_hash if codex.approved else None,
        'rejection_layer': (
            'galahad' if not galahad.approved else
            'cerberus' if not cerberus.approved else
            'codex' if not codex.approved else None
        ),
        'rejection_reason': (
            galahad.reason if not galahad.approved else
            cerberus.reason if not cerberus.approved else
            codex.reason if not codex.approved else None
        )
    }

    async with db.transaction():
        record_id = await db.execute(
            """
            INSERT INTO memory_decision
            (operation_id, timestamp, galahad_approved, galahad_confidence,
             galahad_reason, galahad_law_violated, galahad_time_ms,
             cerberus_approved, cerberus_security_score, cerberus_checks_performed,
             cerberus_security_incident, cerberus_reason, cerberus_time_ms,
             codex_approved, codex_approval_hash, codex_valid_until, codex_reason,
             codex_time_ms, final_approved, total_time_ms, rejection_layer,
             rejection_reason, governance_chain)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14,
                    $15, $16, $17, $18, $19, $20, $21, $22, $23)
            RETURNING id
            """,
            operation_id, datetime.utcnow(),
            galahad.approved, galahad.confidence, galahad.reason,
            galahad.law_violated, galahad.decision_time_ms,
            cerberus.approved, cerberus.security_score, cerberus.checks_performed,
            cerberus.security_incident, cerberus.reason, cerberus.decision_time_ms,
            codex.approved, codex.approval_hash, codex.valid_until, codex.reason,
            codex.decision_time_ms, final_decision['approved'],
            final_decision['total_time_ms'], final_decision['rejection_layer'],
            final_decision['rejection_reason'], json.dumps(governance_chain)
        )

    logger.info(f"Recorded decision for operation {operation_id}: {final_decision['approved']}")

    return DecisionRecord(id=record_id, governance_chain=governance_chain,
                         final_decision=final_decision)
```

### Channel 3: Result

**Purpose**: Record execution results and outcomes.

**Data Captured**:

```python
{
    "operation_id": "uuid-v4",
    "channel": "result",
    "timestamp": "2024-01-15T10:30:03.200Z",
    "execution": {
        "agent_type": "IntelligenceAgent",
        "agent_version": "1.2.0",
        "execution_time_ms": 1234,
        "status": "success|failure|timeout",
        "status_code": 200
    },
    "output": {
        "type": "text|json|image|file",
        "content": "execution output",
        "size_bytes": 1024,
        "format": "utf-8|json|png|pdf"
    },
    "side_effects": [
        {
            "type": "database_write",
            "target": "users",
            "action": "update",
            "affected_rows": 1
        },
        {
            "type": "file_created",
            "path": "/data/outputs/result.json",
            "size_bytes": 2048
        }
    ],
    "resources": {
        "cpu_time_ms": 800,
        "memory_peak_mb": 128,
        "disk_io_mb": 5,
        "network_requests": 2
    },
    "metadata": {
        "retry_count": 0,
        "cached": false,
        "cache_key": null
    }
}
```

**Database Schema**:

```sql
CREATE TABLE memory_result (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id UUID NOT NULL REFERENCES memory_attempt(operation_id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Execution data
    agent_type VARCHAR(100) NOT NULL,
    agent_version VARCHAR(20),
    execution_time_ms INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    status_code INTEGER,

    -- Output data
    output_type VARCHAR(20) NOT NULL,
    output_content TEXT,
    output_size_bytes INTEGER,
    output_format VARCHAR(20),

    -- Side effects (JSONB array)
    side_effects JSONB,

    -- Resource usage
    cpu_time_ms INTEGER,
    memory_peak_mb INTEGER,
    disk_io_mb INTEGER,
    network_requests INTEGER,

    -- Metadata
    retry_count INTEGER DEFAULT 0,
    cached BOOLEAN DEFAULT FALSE,
    cache_key VARCHAR(64),

    -- Full result data (JSONB)
    result_data JSONB NOT NULL,

    CONSTRAINT valid_status CHECK (status IN ('success', 'failure', 'timeout')),
    CONSTRAINT valid_output_type CHECK (output_type IN ('text', 'json', 'image', 'file'))
);

CREATE INDEX idx_result_operation_id ON memory_result(operation_id);
CREATE INDEX idx_result_timestamp ON memory_result(timestamp DESC);
CREATE INDEX idx_result_agent_type ON memory_result(agent_type);
CREATE INDEX idx_result_status ON memory_result(status);
CREATE INDEX idx_result_execution_time ON memory_result(execution_time_ms);
CREATE INDEX idx_result_data ON memory_result USING GIN (result_data);
```

### Channel 4: Reflection

**Purpose**: Post-execution analysis and learning insights.

**Data Captured**:

```python
{
    "operation_id": "uuid-v4",
    "channel": "reflection",
    "timestamp": "2024-01-15T10:30:03.500Z",
    "analysis": {
        "success": true,
        "met_expectations": true,
        "quality_score": 0.88,
        "efficiency_score": 0.92
    },
    "learning": {
        "new_knowledge": [
            "User prefers concise responses",
            "Context from previous operation was helpful"
        ],
        "pattern_detected": "User follows up with clarification questions",
        "improvement_suggestions": [
            "Could have provided examples proactively",
            "Consider caching similar queries"
        ]
    },
    "impact": {
        "user_satisfaction_estimate": 0.85,
        "knowledge_base_updated": true,
        "persona_adjustments": {
            "mood": "satisfied",
            "confidence": 0.90
        }
    },
    "future_optimization": {
        "cache_candidate": true,
        "similar_operations": ["op-uuid-3", "op-uuid-7"],
        "suggested_shortcuts": ["Create quick command for this pattern"]
    }
}
```

**Database Schema**:

```sql
CREATE TABLE memory_reflection (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id UUID NOT NULL REFERENCES memory_attempt(operation_id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Analysis
    success BOOLEAN NOT NULL,
    met_expectations BOOLEAN,
    quality_score NUMERIC(3,2),
    efficiency_score NUMERIC(3,2),

    -- Learning insights (JSONB arrays)
    new_knowledge JSONB,
    patterns_detected TEXT[],
    improvement_suggestions JSONB,

    -- Impact assessment
    user_satisfaction_estimate NUMERIC(3,2),
    knowledge_base_updated BOOLEAN DEFAULT FALSE,
    persona_adjustments JSONB,

    -- Future optimization
    cache_candidate BOOLEAN DEFAULT FALSE,
    similar_operations UUID[],

    -- Full reflection data (JSONB)
    reflection_data JSONB NOT NULL
);

CREATE INDEX idx_reflection_operation_id ON memory_reflection(operation_id);
CREATE INDEX idx_reflection_timestamp ON memory_reflection(timestamp DESC);
CREATE INDEX idx_reflection_quality ON memory_reflection(quality_score DESC);
CREATE INDEX idx_reflection_cache ON memory_reflection(cache_candidate) WHERE cache_candidate = TRUE;
CREATE INDEX idx_reflection_data ON memory_reflection USING GIN (reflection_data);
```

### Channel 5: Error

**Purpose**: Record failures, exceptions, and recovery actions.

**Data Captured**:

```python
{
    "operation_id": "uuid-v4",
    "channel": "error",
    "timestamp": "2024-01-15T10:30:02.800Z",
    "error": {
        "type": "TimeoutError",
        "message": "Agent execution exceeded 60s timeout",
        "code": "AGENT_TIMEOUT",
        "severity": "HIGH"
    },
    "stack_trace": "full stack trace here...",
    "context": {
        "agent_type": "DataAnalysisAgent",
        "execution_stage": "data_processing",
        "input_size_mb": 150,
        "time_elapsed_ms": 60000
    },
    "recovery": {
        "action_taken": "operation_aborted",
        "retry_attempted": false,
        "fallback_used": null,
        "user_notified": true
    },
    "root_cause": {
        "analysis": "Input data size exceeded agent capacity",
        "contributing_factors": [
            "No pagination implemented",
            "Insufficient timeout configuration"
        ],
        "suggested_fix": "Implement chunked processing for large datasets"
    },
    "incident": {
        "id": "incident-uuid",
        "severity": "HIGH",
        "oncall_notified": true,
        "resolved": true,
        "resolution_time_minutes": 15
    }
}
```

**Database Schema**:

```sql
CREATE TABLE memory_error (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id UUID NOT NULL REFERENCES memory_attempt(operation_id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Error data
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_code VARCHAR(50),
    severity VARCHAR(20) NOT NULL,

    -- Stack trace
    stack_trace TEXT,

    -- Context (JSONB)
    error_context JSONB,

    -- Recovery actions
    recovery_action VARCHAR(50),
    retry_attempted BOOLEAN DEFAULT FALSE,
    fallback_used VARCHAR(100),
    user_notified BOOLEAN DEFAULT FALSE,

    -- Root cause analysis
    root_cause_analysis TEXT,
    contributing_factors TEXT[],
    suggested_fix TEXT,

    -- Incident tracking
    incident_id UUID,
    oncall_notified BOOLEAN DEFAULT FALSE,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_time_minutes INTEGER,

    -- Full error data (JSONB)
    error_data JSONB NOT NULL,

    CONSTRAINT valid_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE INDEX idx_error_operation_id ON memory_error(operation_id);
CREATE INDEX idx_error_timestamp ON memory_error(timestamp DESC);
CREATE INDEX idx_error_type ON memory_error(error_type);
CREATE INDEX idx_error_severity ON memory_error(severity);
CREATE INDEX idx_error_resolved ON memory_error(resolved) WHERE resolved = FALSE;
CREATE INDEX idx_error_data ON memory_error USING GIN (error_data);
```

## Parallel Recording Pattern

All five channels are recorded in parallel for maximum performance:

```python
async def record_complete_operation(operation: CompletedOperation):
    """Record operation across all five channels in parallel."""

    operation_id = operation.id

    # Start all recordings in parallel

    await asyncio.gather(
        record_attempt(operation_id, operation.request),
        record_decision(operation_id, operation.galahad, operation.cerberus, operation.codex),
        record_result(operation_id, operation.execution_result),
        record_reflection(operation_id, await generate_reflection(operation)),
        record_error(operation_id, operation.errors) if operation.errors else asyncio.sleep(0)
    )

    logger.info(f"Recorded operation {operation_id} across all channels")

    # Update operation status

    await db.execute(
        """
        UPDATE operations
        SET recording_complete = TRUE,
            recording_timestamp = NOW()
        WHERE operation_id = $1
        """,
        operation_id
    )

    # Emit metric

    memory_recordings_total.labels(channel='all').inc()
```

## Query Patterns

### Retrieve Complete Operation History

```python
async def get_complete_operation(operation_id: str) -> CompleteOperation:
    """Retrieve all five channels for an operation."""

    attempt, decision, result, reflection, error = await asyncio.gather(
        db.fetchrow("SELECT * FROM memory_attempt WHERE operation_id = $1", operation_id),
        db.fetchrow("SELECT * FROM memory_decision WHERE operation_id = $1", operation_id),
        db.fetchrow("SELECT * FROM memory_result WHERE operation_id = $1", operation_id),
        db.fetchrow("SELECT * FROM memory_reflection WHERE operation_id = $1", operation_id),
        db.fetchrow("SELECT * FROM memory_error WHERE operation_id = $1", operation_id)
    )

    return CompleteOperation(
        operation_id=operation_id,
        attempt=AttemptRecord(**attempt) if attempt else None,
        decision=DecisionRecord(**decision) if decision else None,
        result=ResultRecord(**result) if result else None,
        reflection=ReflectionRecord(**reflection) if reflection else None,
        error=ErrorRecord(**error) if error else None
    )
```

### Search Similar Operations

```python
async def search_similar_operations(intent: str, limit: int = 10) -> List[str]:
    """Find operations with similar intent."""

    similar = await db.fetch(
        """
        SELECT operation_id, content, confidence
        FROM memory_attempt
        WHERE intent = $1
        ORDER BY timestamp DESC
        LIMIT $2
        """,
        intent, limit
    )

    return [row['operation_id'] for row in similar]
```

### Analyze Error Patterns

```python
async def analyze_error_patterns(hours: int = 24) -> ErrorAnalysis:
    """Analyze error patterns over time window."""

    errors = await db.fetch(
        """
        SELECT error_type, error_code, severity, COUNT(*) as count
        FROM memory_error
        WHERE timestamp > NOW() - INTERVAL '$1 hours'
        GROUP BY error_type, error_code, severity
        ORDER BY count DESC
        """,
        hours
    )

    return ErrorAnalysis(
        time_window_hours=hours,
        total_errors=sum(row['count'] for row in errors),
        error_types={row['error_type']: row['count'] for row in errors},
        critical_errors=sum(row['count'] for row in errors if row['severity'] == 'CRITICAL')
    )
```

## Data Retention and Archival

**Hot Storage (PostgreSQL)**: 90 days

```sql
-- Automatic partition management
SELECT partman.create_parent('public.memory_attempt', 'timestamp', 'native', 'monthly');
SELECT partman.create_parent('public.memory_decision', 'timestamp', 'native', 'monthly');
SELECT partman.create_parent('public.memory_result', 'timestamp', 'native', 'monthly');
SELECT partman.create_parent('public.memory_reflection', 'timestamp', 'native', 'monthly');
SELECT partman.create_parent('public.memory_error', 'timestamp', 'native', 'monthly');

-- Retention policy: drop partitions older than 90 days
UPDATE partman.part_config
SET retention = '90 days',
    retention_keep_table = FALSE
WHERE parent_table IN (
    'public.memory_attempt',
    'public.memory_decision',
    'public.memory_result',
    'public.memory_reflection',
    'public.memory_error'
);
```

**Warm Storage (Object Store)**: 90 days - 7 years

```python
async def archive_old_memories():
    """Archive memories older than 90 days to object storage."""

    cutoff = datetime.utcnow() - timedelta(days=90)

    # Export to JSON

    operations = await db.fetch(
        """
        SELECT a.operation_id, a.*, d.*, r.*, ref.*, e.*
        FROM memory_attempt a
        LEFT JOIN memory_decision d USING (operation_id)
        LEFT JOIN memory_result r USING (operation_id)
        LEFT JOIN memory_reflection ref USING (operation_id)
        LEFT JOIN memory_error e USING (operation_id)
        WHERE a.timestamp < $1
        """,
        cutoff
    )

    # Upload to S3/MinIO

    for op in operations:
        archive_key = f"memories/{op['operation_id'][:2]}/{op['operation_id']}.json"
        await object_store.upload(
            bucket='memory-archive',
            key=archive_key,
            data=json.dumps(op, default=str),
            encryption='AES256'
        )

    logger.info(f"Archived {len(operations)} operations to warm storage")
```

**Cold Storage (Glacier)**: > 7 years (compliance)

## Performance Characteristics

### Latency Targets (P95)

- Single channel write: < 10ms
- All five channels (parallel): < 50ms
- Query single operation: < 20ms
- Search by intent: < 100ms

### Throughput Targets

- Memory writes/sec: 1,000+
- Concurrent operations: 500
- Query throughput: 5,000/sec

## Monitoring

```python

# Prometheus metrics

memory_recordings_total = Counter(
    'memory_recordings_total',
    'Total memory recordings',
    ['channel']
)

memory_recording_duration_seconds = Histogram(
    'memory_recording_duration_seconds',
    'Memory recording duration',
    ['channel']
)

memory_query_duration_seconds = Histogram(
    'memory_query_duration_seconds',
    'Memory query duration',
    ['query_type']
)
```

## Related Documentation

- [User Request Flow](./user_request_flow.md)
- [Governance Decision Flow](./governance_decision_flow.md)
- [Audit Trail Flow](./audit_trail_flow.md)
- [Component Architecture - Memory Engine](../component/memory_engine.md)
