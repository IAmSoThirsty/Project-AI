# Audit Trail Flow - Immutable Logging with Hash Chaining

## Overview

The Audit Trail Flow implements a cryptographically secure, tamper-evident logging system that records every operation in Project-AI. Using SHA-256 hash chaining, the audit trail provides complete accountability and enables compliance with regulatory requirements (GDPR, HIPAA, SOC2).

## Hash-Chained Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT TRAIL SYSTEM                           │
│                                                                 │
│  Immutable Append-Only Log with Cryptographic Hash Chaining    │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ↓
        ┌──────────────────────────────────────────┐
        │      GENESIS BLOCK (Entry 0)             │
        │  hash: SHA256("PROJECT_AI_GENESIS")      │
        │  previous_hash: null                     │
        │  timestamp: 2024-01-01T00:00:00Z         │
        └───────────────────┬──────────────────────┘
                           │
                           ↓ (hash becomes previous_hash)
        ┌──────────────────────────────────────────┐
        │      ENTRY 1                             │
        │  operation_id: uuid-1                    │
        │  event_type: user_request                │
        │  data: {...}                             │
        │  previous_hash: <genesis_hash>           │
        │  current_hash: SHA256(entry_1_data)      │
        └───────────────────┬──────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────────┐
        │      ENTRY 2                             │
        │  operation_id: uuid-2                    │
        │  event_type: governance_decision         │
        │  data: {...}                             │
        │  previous_hash: <entry_1_hash>           │
        │  current_hash: SHA256(entry_2_data)      │
        └───────────────────┬──────────────────────┘
                           │
                           ↓
                          ...
                           │
                           ↓
        ┌──────────────────────────────────────────┐
        │      ENTRY N (Latest)                    │
        │  operation_id: uuid-n                    │
        │  event_type: execution_result            │
        │  data: {...}                             │
        │  previous_hash: <entry_n-1_hash>         │
        │  current_hash: SHA256(entry_n_data)      │
        └───────────────────┬──────────────────────┘
                           │
                           ↓
                ┌─────────────────────┐
                │  Latest Hash Cache  │
                │  Redis/Memory       │
                └─────────────────────┘
```

## Audit Entry Structure

### Standard Audit Entry

```python
{
    "id": "audit-uuid",
    "sequence_number": 12345,
    "timestamp": "2024-01-15T10:30:00.123Z",
    "event_type": "user_request|governance_decision|execution_result|error|security_incident",
    "operation_id": "operation-uuid",
    "user_id": "user-uuid",
    "session_id": "session-uuid",
    "event_data": {
        # Event-specific data
    },
    "metadata": {
        "source": "gui|api|cli|websocket",
        "client_ip": "192.168.1.100",
        "user_agent": "ProjectAI-Desktop/1.0.0",
        "server_node": "node-01"
    },
    "previous_hash": "sha256_hash_of_previous_entry",
    "current_hash": "sha256_hash_of_this_entry"
}
```

### Hash Calculation

```python
def calculate_audit_hash(entry: AuditEntry) -> str:
    """
    Calculate SHA-256 hash of audit entry.
    
    Hash includes:
    - All entry fields except current_hash
    - Canonical JSON representation (sorted keys)
    - UTF-8 encoding
    
    Returns:
        64-character hexadecimal hash
    """
    # Create canonical representation
    hash_data = {
        'id': entry.id,
        'sequence_number': entry.sequence_number,
        'timestamp': entry.timestamp.isoformat(),
        'event_type': entry.event_type,
        'operation_id': entry.operation_id,
        'user_id': entry.user_id,
        'session_id': entry.session_id,
        'event_data': entry.event_data,
        'metadata': entry.metadata,
        'previous_hash': entry.previous_hash
    }
    
    # Convert to canonical JSON (sorted keys, no whitespace)
    canonical_json = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
    
    # Calculate SHA-256 hash
    hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).digest()
    
    # Return hex representation
    return hash_bytes.hex()
```

## Event Types

### 1. User Request Events

**Event Type**: `user_request`

**Data Captured**:
```python
{
    "event_type": "user_request",
    "event_data": {
        "request": {
            "content": "natural language request",
            "intent": "detected_intent",
            "confidence": 0.95
        },
        "context": {
            "previous_operations": ["op-1", "op-2"],
            "session_duration_ms": 120000
        },
        "validation": {
            "passed": true,
            "checks": ["authentication", "rate_limit", "schema"]
        }
    }
}
```

### 2. Governance Decision Events

**Event Type**: `governance_decision`

**Data Captured**:
```python
{
    "event_type": "governance_decision",
    "event_data": {
        "decision": "approved|rejected",
        "governance_chain": {
            "galahad": {
                "approved": true,
                "reason": "All ethical validations passed",
                "confidence": 0.95
            },
            "cerberus": {
                "approved": true,
                "security_score": 0.92,
                "threats_detected": []
            },
            "codex": {
                "approved": true,
                "approval_hash": "sha256_hash",
                "valid_until": "2024-01-15T10:35:00Z"
            }
        },
        "total_time_ms": 90,
        "rejection_layer": null
    }
}
```

### 3. Execution Result Events

**Event Type**: `execution_result`

**Data Captured**:
```python
{
    "event_type": "execution_result",
    "event_data": {
        "agent_type": "IntelligenceAgent",
        "status": "success|failure|timeout",
        "execution_time_ms": 1234,
        "output_summary": "truncated output for audit",
        "side_effects": [
            {"type": "database_write", "table": "users", "affected_rows": 1}
        ],
        "resources": {
            "cpu_time_ms": 800,
            "memory_peak_mb": 128
        }
    }
}
```

### 4. Error Events

**Event Type**: `error`

**Data Captured**:
```python
{
    "event_type": "error",
    "event_data": {
        "error_type": "TimeoutError",
        "error_message": "Agent execution exceeded timeout",
        "severity": "HIGH",
        "recovery_action": "operation_aborted",
        "incident_created": true,
        "incident_id": "incident-uuid"
    }
}
```

### 5. Security Incident Events

**Event Type**: `security_incident`

**Data Captured**:
```python
{
    "event_type": "security_incident",
    "event_data": {
        "incident_type": "injection_attack|unauthorized_access|data_exposure",
        "severity": "CRITICAL",
        "threat_details": {
            "pattern_detected": "SQL injection attempt",
            "attack_vector": "user_input",
            "blocked": true
        },
        "response_actions": [
            "request_rejected",
            "user_flagged",
            "security_team_notified"
        ],
        "oncall_notified": true
    }
}
```

## Database Schema

```sql
CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_number BIGSERIAL UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Event identification
    event_type VARCHAR(50) NOT NULL,
    operation_id UUID,
    user_id UUID,
    session_id UUID,
    
    -- Event data (JSONB for flexibility)
    event_data JSONB NOT NULL,
    
    -- Metadata
    metadata JSONB,
    
    -- Hash chain
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL UNIQUE,
    
    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verification_timestamp TIMESTAMPTZ,
    
    CONSTRAINT valid_event_type CHECK (
        event_type IN (
            'user_request',
            'governance_decision',
            'execution_result',
            'error',
            'security_incident',
            'user_login',
            'user_logout',
            'configuration_change',
            'system_event'
        )
    ),
    
    CONSTRAINT valid_hash CHECK (
        length(previous_hash) = 64 AND
        length(current_hash) = 64
    )
);

-- Indexes for fast retrieval
CREATE INDEX idx_audit_sequence ON audit_trail(sequence_number DESC);
CREATE INDEX idx_audit_timestamp ON audit_trail(timestamp DESC);
CREATE INDEX idx_audit_event_type ON audit_trail(event_type);
CREATE INDEX idx_audit_operation_id ON audit_trail(operation_id);
CREATE INDEX idx_audit_user_id ON audit_trail(user_id);
CREATE INDEX idx_audit_current_hash ON audit_trail(current_hash);
CREATE INDEX idx_audit_verified ON audit_trail(verified) WHERE verified = FALSE;

-- GIN index for JSONB queries
CREATE INDEX idx_audit_event_data ON audit_trail USING GIN (event_data);
CREATE INDEX idx_audit_metadata ON audit_trail USING GIN (metadata);

-- Partitioning by month for performance
CREATE TABLE audit_trail_2024_01 PARTITION OF audit_trail
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audit_trail_2024_02 PARTITION OF audit_trail
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Prevent updates and deletes (immutable log)
CREATE RULE audit_trail_immutable_update AS
    ON UPDATE TO audit_trail
    DO INSTEAD NOTHING;

CREATE RULE audit_trail_immutable_delete AS
    ON DELETE TO audit_trail
    DO INSTEAD NOTHING;
```

## Append Operation

```python
class AuditTrailService:
    """Service for managing immutable audit trail."""
    
    def __init__(self):
        self.db = get_database_connection()
        self.redis = get_redis_connection()
        self.lock = asyncio.Lock()
    
    async def append(self, event_type: str, operation_id: str, user_id: str,
                    event_data: dict, metadata: dict = None) -> AuditEntry:
        """
        Append new entry to audit trail.
        
        Thread-safe using asyncio.Lock to prevent race conditions.
        
        Args:
            event_type: Type of event being logged
            operation_id: ID of the operation
            user_id: ID of the user
            event_data: Event-specific data
            metadata: Optional metadata
        
        Returns:
            Created audit entry with calculated hash
        """
        async with self.lock:  # Ensure sequential writes
            # Get previous hash
            previous_hash = await self._get_latest_hash()
            
            # Get next sequence number
            sequence_number = await self._get_next_sequence()
            
            # Create entry
            entry = AuditEntry(
                id=str(uuid.uuid4()),
                sequence_number=sequence_number,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                operation_id=operation_id,
                user_id=user_id,
                session_id=get_current_session_id(),
                event_data=event_data,
                metadata=metadata or {},
                previous_hash=previous_hash
            )
            
            # Calculate current hash
            entry.current_hash = calculate_audit_hash(entry)
            
            # Write to database
            await self.db.execute(
                """
                INSERT INTO audit_trail
                (id, sequence_number, timestamp, event_type, operation_id,
                 user_id, session_id, event_data, metadata, previous_hash, current_hash)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                entry.id, entry.sequence_number, entry.timestamp, entry.event_type,
                entry.operation_id, entry.user_id, entry.session_id,
                json.dumps(entry.event_data), json.dumps(entry.metadata),
                entry.previous_hash, entry.current_hash
            )
            
            # Update latest hash in cache
            await self.redis.set(
                'audit_trail:latest_hash',
                entry.current_hash,
                ex=3600  # 1 hour expiry
            )
            
            await self.redis.set(
                'audit_trail:latest_sequence',
                entry.sequence_number,
                ex=3600
            )
            
            logger.info(f"Appended audit entry {entry.sequence_number}: {event_type}")
            
            # Emit metric
            audit_entries_total.labels(event_type=event_type).inc()
            
            return entry
    
    async def _get_latest_hash(self) -> str:
        """Get hash of latest audit entry."""
        # Try cache first
        cached_hash = await self.redis.get('audit_trail:latest_hash')
        if cached_hash:
            return cached_hash.decode('utf-8')
        
        # Query database
        row = await self.db.fetchrow(
            """
            SELECT current_hash
            FROM audit_trail
            ORDER BY sequence_number DESC
            LIMIT 1
            """
        )
        
        if row:
            latest_hash = row['current_hash']
            # Update cache
            await self.redis.set('audit_trail:latest_hash', latest_hash, ex=3600)
            return latest_hash
        
        # Genesis case: no entries yet
        return hashlib.sha256(b"PROJECT_AI_GENESIS").hexdigest()
    
    async def _get_next_sequence(self) -> int:
        """Get next sequence number."""
        # Try cache first
        cached_seq = await self.redis.get('audit_trail:latest_sequence')
        if cached_seq:
            return int(cached_seq) + 1
        
        # Query database
        row = await self.db.fetchrow(
            """
            SELECT MAX(sequence_number) as max_seq
            FROM audit_trail
            """
        )
        
        if row and row['max_seq'] is not None:
            return row['max_seq'] + 1
        
        # Genesis case
        return 1
```

## Chain Verification

```python
async def verify_audit_chain(start_sequence: int = 1, 
                             end_sequence: int = None) -> VerificationResult:
    """
    Verify integrity of audit trail hash chain.
    
    Checks:
    1. Each entry's current_hash matches calculated hash
    2. Each entry's previous_hash matches previous entry's current_hash
    3. No gaps in sequence numbers
    4. No duplicate hashes
    
    Args:
        start_sequence: Starting sequence number (default: 1)
        end_sequence: Ending sequence number (default: latest)
    
    Returns:
        VerificationResult with success status and details
    """
    # Get entries in sequence order
    if end_sequence is None:
        end_sequence = await db.fetchval(
            "SELECT MAX(sequence_number) FROM audit_trail"
        )
    
    entries = await db.fetch(
        """
        SELECT *
        FROM audit_trail
        WHERE sequence_number >= $1 AND sequence_number <= $2
        ORDER BY sequence_number ASC
        """,
        start_sequence, end_sequence
    )
    
    errors = []
    verified_count = 0
    
    previous_hash = None
    expected_sequence = start_sequence
    
    for entry in entries:
        # Check sequence continuity
        if entry['sequence_number'] != expected_sequence:
            errors.append({
                'type': 'sequence_gap',
                'expected': expected_sequence,
                'actual': entry['sequence_number']
            })
        
        # Check hash calculation
        calculated_hash = calculate_audit_hash(AuditEntry(**entry))
        if calculated_hash != entry['current_hash']:
            errors.append({
                'type': 'hash_mismatch',
                'sequence': entry['sequence_number'],
                'stored_hash': entry['current_hash'],
                'calculated_hash': calculated_hash
            })
        
        # Check chain link
        if previous_hash and entry['previous_hash'] != previous_hash:
            errors.append({
                'type': 'chain_break',
                'sequence': entry['sequence_number'],
                'expected_previous': previous_hash,
                'actual_previous': entry['previous_hash']
            })
        
        previous_hash = entry['current_hash']
        expected_sequence += 1
        verified_count += 1
    
    success = len(errors) == 0
    
    if success:
        # Mark entries as verified
        await db.execute(
            """
            UPDATE audit_trail
            SET verified = TRUE, verification_timestamp = NOW()
            WHERE sequence_number >= $1 AND sequence_number <= $2
            """,
            start_sequence, end_sequence
        )
    
    return VerificationResult(
        success=success,
        verified_entries=verified_count,
        errors=errors,
        start_sequence=start_sequence,
        end_sequence=end_sequence,
        verification_timestamp=datetime.utcnow()
    )
```

## Compliance Export

```python
async def export_compliance_report(start_date: datetime, end_date: datetime,
                                   format: str = 'json') -> ComplianceReport:
    """
    Export audit trail for compliance purposes.
    
    Supports formats:
    - JSON: Machine-readable
    - CSV: Human-readable
    - PDF: Official report with signatures
    
    Args:
        start_date: Start of time range
        end_date: End of time range
        format: Export format (json|csv|pdf)
    
    Returns:
        ComplianceReport with exported data
    """
    # Query audit entries
    entries = await db.fetch(
        """
        SELECT *
        FROM audit_trail
        WHERE timestamp >= $1 AND timestamp <= $2
        ORDER BY sequence_number ASC
        """,
        start_date, end_date
    )
    
    # Verify chain integrity
    verification = await verify_audit_chain(
        start_sequence=entries[0]['sequence_number'],
        end_sequence=entries[-1]['sequence_number']
    )
    
    # Generate report
    report = ComplianceReport(
        start_date=start_date,
        end_date=end_date,
        total_entries=len(entries),
        event_type_breakdown={
            event_type: sum(1 for e in entries if e['event_type'] == event_type)
            for event_type in set(e['event_type'] for e in entries)
        },
        users_involved=len(set(e['user_id'] for e in entries if e['user_id'])),
        security_incidents=sum(
            1 for e in entries if e['event_type'] == 'security_incident'
        ),
        chain_verified=verification.success,
        verification_errors=verification.errors,
        entries=entries
    )
    
    # Export in requested format
    if format == 'json':
        return report.to_json()
    elif format == 'csv':
        return report.to_csv()
    elif format == 'pdf':
        return await report.to_pdf_with_signature()
    else:
        raise ValueError(f"Unsupported format: {format}")
```

## Merkle Tree Verification

For batch verification efficiency, audit entries can be organized into Merkle trees:

```python
def build_merkle_tree(entries: List[AuditEntry]) -> MerkleTree:
    """
    Build Merkle tree from audit entries.
    
    Enables efficient verification of large batches.
    
    Args:
        entries: List of audit entries
    
    Returns:
        MerkleTree with root hash
    """
    # Leaf nodes: individual entry hashes
    leaves = [entry.current_hash for entry in entries]
    
    tree = MerkleTree()
    tree.build(leaves)
    
    return tree

def verify_merkle_proof(entry: AuditEntry, proof: MerkleProof, 
                       root_hash: str) -> bool:
    """
    Verify single entry against Merkle root.
    
    Args:
        entry: Audit entry to verify
        proof: Merkle proof (sibling hashes)
        root_hash: Expected root hash
    
    Returns:
        True if entry is part of tree with root_hash
    """
    current_hash = entry.current_hash
    
    for sibling_hash, is_left in proof.path:
        if is_left:
            current_hash = hashlib.sha256(
                (sibling_hash + current_hash).encode()
            ).hexdigest()
        else:
            current_hash = hashlib.sha256(
                (current_hash + sibling_hash).encode()
            ).hexdigest()
    
    return current_hash == root_hash
```

## Performance Characteristics

### Latency Targets (P95)
- Append entry: < 20ms
- Query entry by ID: < 10ms
- Query range: < 100ms
- Verify chain (1000 entries): < 2s
- Export compliance report: < 30s

### Throughput Targets
- Append operations/sec: 10,000+
- Query operations/sec: 50,000+

## Monitoring

```python
# Prometheus metrics
audit_entries_total = Counter(
    'audit_entries_total',
    'Total audit entries',
    ['event_type']
)

audit_append_duration_seconds = Histogram(
    'audit_append_duration_seconds',
    'Audit append operation duration'
)

audit_verification_failures_total = Counter(
    'audit_verification_failures_total',
    'Total audit verification failures',
    ['failure_type']
)

audit_chain_length = Gauge(
    'audit_chain_length',
    'Current length of audit chain'
)
```

## Related Documentation

- [User Request Flow](./user_request_flow.md)
- [Governance Decision Flow](./governance_decision_flow.md)
- [Memory Recording Flow](./memory_recording_flow.md)
- [Security Architecture](../security/README.md)
