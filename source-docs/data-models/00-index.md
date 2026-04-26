# Data Models Documentation Index

**Location**: `source-docs/data-models/`  
**Total Documents**: 15  
**Last Updated**: 2024-01-20  
**Maintainer**: Project-AI Core Team

---

## Overview

This directory contains comprehensive documentation for all data models, schemas, and ORM patterns in Project-AI. Each document covers schema structure, field specifications, CRUD operations, usage examples, security considerations, and integration patterns.

---

## Document Catalog

### Core User & Identity

#### 01. User Management Model
**File**: `01-user-management-model.md`  
**Module**: `src/app/core/user_manager.py` [[src/app/core/user_manager.py]]  
**Storage**: `data/users.json`

**Topics Covered**:
- User profile schema with bcrypt password hashing
- Account lockout system (5 attempts, 5-minute lockout)
- Fernet encryption for sensitive data
- Automatic migration from plaintext to hashed passwords
- Path traversal protection and atomic file operations
- Role-based user system (admin/user)

**Key Data Structures**:
- User document with password_hash, email, role, preferences
- Lockout tracking (failed_attempts, locked_until)
- Timestamp tracking (created_at, last_login)

---

#### 02. AI Persona Model
**File**: `02-ai-persona-model.md`  
**Module**: `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (AIPersona class)  
**Storage**: `data/ai_persona/state.json`

**Topics Covered**:
- 8 personality traits (curiosity, patience, empathy, helpfulness, playfulness, formality, assertiveness, thoughtfulness)
- 4-dimensional mood tracking (energy, enthusiasm, contentment, engagement)
- Interaction counting and user relationship tracking
- Continuous learning integration
- Trait adjustment system with user feedback

**Key Data Structures**:
- Personality trait dictionary (0.0-1.0 scale for each trait)
- Mood state dictionary (0.0-1.0 scale for each dimension)
- Metadata (interactions count, last_interaction timestamp)

---

#### 03. Memory & Knowledge Base Model
**File**: `03-memory-knowledge-base-model.md`  
**Module**: `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (MemoryExpansionSystem class)  
**Storage**: `data/memory/knowledge.json`

**Topics Covered**:
- 6 knowledge categories (technical, personal, general, context, preferences, facts)
- Conversation history logging with timestamps
- Category-based knowledge organization
- Duplicate detection via content hashing
- Search and retrieval by category and keywords

**Key Data Structures**:
- Knowledge item: id, content, timestamp, source, confidence, references
- Conversation entry: id, timestamp, role, message, context
- Metadata: total_conversations, total_knowledge_items, last_updated

---

#### 04. Learning Request & Black Vault Model
**File**: `04-learning-request-black-vault-model.md`  
**Module**: `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (LearningRequestManager class)  
**Storage**: `data/learning_requests/request_index.json`, `data/learning_requests/pending_secure/*.json`

**Topics Covered**:
- Human-in-the-loop approval workflow (approve/deny/defer)
- Black Vault: Permanent blocklist for denied content (SHA-256 hashing)
- Encrypted storage for pending requests (Fernet cipher)
- Automatic fingerprint checking before submission
- Request indexing and audit trail

**Key Data Structures**:
- Request index entry: id, topic, status, submitted_at, decided_at, content_hash
- Black Vault entry: content_hash, topic, denied_at, denied_by, reason, vault_id
- Encrypted pending request: full content stored encrypted in separate file

---

### Data Persistence & Storage

#### 05. Data Persistence Layer Model
**File**: `05-data-persistence-layer-model.md`  
**Module**: `src/app/core/data_persistence.py` [[src/app/core/data_persistence.py]]  
**Storage**: `data/.keys/` (key management), encrypted data files

**Topics Covered**:
- Multi-algorithm encryption (AES-256-GCM, ChaCha20-Poly1305, Fernet)
- Key management: automatic generation, rotation tracking, owner-only permissions
- Versioned configurations with semantic versioning and migration support
- Atomic operations with rollback capability
- Backup & recovery with configurable retention
- Data compression (gzip) support

**Key Data Structures**:
- Encrypted file format: [Algorithm ID][Key ID][Nonce][Ciphertext][Auth Tag]
- Metadata sidecar: algorithm, key_id, version, created_at, checksum
- DataVersion: major, minor, patch for semantic versioning

---

#### 06. Storage Abstraction Layer Model
**File**: `06-storage-abstraction-layer-model.md`  
**Module**: `src/app/core/storage.py` [[src/app/core/storage.py]]  
**Storage**: `data/cognition.db` (SQLite), legacy JSON files

**Topics Covered**:
- Dual storage engines: SQLite (primary) and JSON (legacy)
- Transactional support with ACID guarantees
- Schema evolution with automated migrations
- Thread-safe operations with connection pooling
- Table whitelisting for SQL injection prevention

**Key Data Structures**:
- governance_state: key, data, version, created_at, updated_at
- governance_decisions: decision_id, action_id, approved, reason, council_votes
- execution_history: trace_id, action_name, status, duration_ms, error
- reflection_history: trace_id, action_name, insights, triggered_by
- memory_records: trace_id, memory_type, content, metadata

---

#### 07. Cloud Synchronization Model
**File**: `07-cloud-sync-model.md`  
**Module**: `src/app/core/cloud_sync.py` [[src/app/core/cloud_sync.py]]  
**Storage**: `data/sync_metadata.json`

**Topics Covered**:
- Encrypted bidirectional sync with Fernet cipher
- Device identification via SHA-256 hashing of hardware characteristics
- Conflict resolution (last-write-wins strategy)
- Auto-sync with configurable intervals
- Offline support with operation queueing

**Key Data Structures**:
- Sync metadata: device_id, last_sync, sync_conflicts, sync_history, pending_uploads
- Sync history entry: sync_id, timestamp, direction, files_synced, bytes_transferred, status
- Conflict entry: file, local_hash, remote_hash, resolved, detected_at

---

### Monitoring & Control

#### 08. Telemetry Model
**File**: `08-telemetry-model.md`  
**Module**: `src/app/core/telemetry.py` [[src/app/core/telemetry.py]]  
**Storage**: `logs/telemetry.json`

**Topics Covered**:
- Opt-in event logging (disabled by default)
- Atomic writes with file locking
- Auto-rotation (keeps last 1000 events by default)
- Privacy-first design (no PII collection)
- Event types: authentication, persona, learning, command override, memory

**Key Data Structures**:
- Event: name, timestamp, payload
- Common payload fields: username, duration_ms, success, error, session_id

---

#### 09. Access Control Model
**File**: `09-access-control-model.md`  
**Module**: `src/app/core/access_control.py` [[src/app/core/access_control.py]]  
**Storage**: `data/access_control.json`

**Topics Covered**:
- Role-based access control (RBAC)
- User role assignments with persistent storage
- Default system user with integrator role
- Simple API: grant, revoke, check permissions
- Singleton pattern for global access

**Key Data Structures**:
- Access control document: {username: [roles]}
- Predefined roles: admin, integrator, expert, developer, user

---

### Learning & Knowledge

#### 10. Continuous Learning Model
**File**: `10-continuous-learning-model.md`  
**Module**: `src/app/core/continuous_learning.py` [[src/app/core/continuous_learning.py]]  
**Storage**: `data/continuous_learning/reports.json`, `data/continuous_learning/curated.json`

**Topics Covered**:
- Structured learning reports with automatic fact extraction
- Controversy detection (identifies debates, records both sides)
- Usage suggestion generation
- Neutral summary composition
- Persistent report archive

**Key Data Structures**:
- LearningReport: topic, timestamp, facts, usage_ideas, neutral_summary, pros_cons, metadata
- Fact extraction: Up to 3 key facts per content
- Pros/cons analysis for controversial topics

---

### Location & Emergency

#### 11. Location Tracking Model
**File**: `11-location-tracking-model.md`  
**Module**: `src/app/core/location_tracker.py` [[src/app/core/location_tracker.py]]  
**Storage**: `location_history_{username}.json` (encrypted)

**Topics Covered**:
- Dual source support: IP geolocation + GPS coordinates
- Encrypted history storage with Fernet cipher
- Privacy-first design (user-controlled activation)
- Timeout protection (10-second API timeout)
- GDPR compliance (right to access and erasure)

**Key Data Structures**:
- IP-based location: latitude, longitude, city, region, country, ip, timestamp, source
- GPS-based location: latitude, longitude, address, timestamp, source
- Encrypted history: Array of base64-encoded encrypted location entries

---

#### 12. Command Override Model
**File**: `12-command-override-model.md`  
**Module**: `src/app/core/command_override.py` [[src/app/core/command_override.py]], `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (CommandOverride class)  
**Storage**: `data/command_override_config.json`

**Topics Covered**:
- 10+ safety protocols (password, lockout, time limits, audit, IP tracking, etc.)
- SHA-256 password protection with salt
- Time-limited activation with auto-deactivation
- Complete audit trail with event logging
- Emergency access for critical situations

**Key Data Structures**:
- Config: master_password_hash, override_active, activation_timestamp, timeout_seconds
- Lockout tracking: max_failed_attempts, failed_attempts, locked_until
- Audit log: timestamp, event, user, success, reason, ip_address

---

#### 13. Emergency Alert Model
**File**: `13-emergency-alert-model.md`  
**Module**: `src/app/core/emergency_alert.py` [[src/app/core/emergency_alert.py]]  
**Storage**: `emergency_contacts_{username}.json`

**Topics Covered**:
- Contact management (multiple emergency contacts per user)
- Email notifications via SMTP
- Location integration in alerts
- Template system for customizable emails
- Priority levels (1=highest priority)

**Key Data Structures**:
- Contact: id, name, relationship, email, phone, priority, active, added_at
- Alert history: alert_id, timestamp, severity, message, location, contacts_notified, status

---

### Configuration

#### 14. Configuration Management Model
**File**: `14-config-management-model.md`  
**Module**: `src/app/core/config.py` [[src/app/core/config.py]]  
**Storage**: `data/settings.json`, `config.yaml`

**Topics Covered**:
- Multi-source configuration hierarchy (env vars > config files > defaults)
- Environment-specific configs (dev, test, staging, prod)
- Schema validation with Pydantic
- Hot reload with file watching
- Secret management for sensitive values

**Key Data Structures**:
- App config: name, version, debug, log_level
- Database config: engine, path, backup_enabled, backup_retention_days
- AI config: default_model, temperature, max_tokens, timeout_seconds
- Security config: password_min_length, session_timeout_minutes, max_login_attempts

---

## Data Model Relationships

### Dependency Graph

```
User Management (01)
    ├──> AI Persona (02)
    ├──> Memory & Knowledge Base (03)
    ├──> Learning Request & Black Vault (04)
    ├──> Access Control (09)
    └──> Cloud Sync (07)

Data Persistence Layer (05)
    ├──> Storage Abstraction (06)
    ├──> Cloud Sync (07)
    ├──> User Management (01)
    ├──> Location Tracking (11)
    └──> Command Override (12)

AI Persona (02)
    ├──> Memory & Knowledge Base (03)
    ├──> Continuous Learning (10)
    └──> Telemetry (08)

Learning Request & Black Vault (04)
    ├──> Continuous Learning (10)
    ├──> Memory & Knowledge Base (03)
    └──> Telemetry (08)

Location Tracking (11)
    └──> Emergency Alert (13)

Command Override (12)
    ├──> Telemetry (08)
    └──> Emergency Alert (13)

Configuration Management (14)
    └──> All Modules (provides config)
```

### Integration Patterns

#### User Session Flow

```
1. User logs in (User Management)
2. Persona loads for user (AI Persona)
3. Memory retrieves conversation history (Memory & Knowledge Base)
4. Telemetry logs login event (Telemetry)
5. Cloud Sync checks for updates (Cloud Sync)
```

#### Learning Flow

```
1. User submits learning request (Learning Request & Black Vault)
2. Admin approves request (User Management + Access Control)
3. Content absorbed by learning engine (Continuous Learning)
4. Facts extracted and stored (Memory & Knowledge Base)
5. Persona adjusts traits based on new knowledge (AI Persona)
6. Telemetry logs learning event (Telemetry)
```

#### Emergency Flow

```
1. Emergency detected (Command Override or manual trigger)
2. Location obtained (Location Tracking)
3. Alerts sent to contacts (Emergency Alert)
4. Telemetry logs emergency event (Telemetry)
5. Cloud Sync propagates alert status (Cloud Sync)
```

---

## Data Persistence Patterns

### JSON-Based Persistence

**Modules**: User Management, AI Persona, Memory, Learning Requests, Telemetry, Access Control, etc.

**Pattern**:
```python
# Atomic write with file locking
def _save_state(self):
    _atomic_write_json(file_path, data)

# Load with error handling
def _load_state(self):
    if os.path.exists(file_path):
        with open(file_path) as f:
            return json.load(f)
    return default_state()
```

**Advantages**:
- Simple, no external dependencies
- Human-readable for debugging
- Easy backup and version control
- Atomic writes prevent corruption

**Disadvantages**:
- No query capabilities
- Full file read/write for updates
- No concurrent access support

---

### SQLite-Based Persistence

**Modules**: Storage Abstraction Layer, Governance State, Execution History

**Pattern**:
```python
# Transactional operations
with storage._get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO table (key, data) VALUES (?, ?)", (key, data))
    conn.commit()
```

**Advantages**:
- ACID transactions
- Query capabilities (JOIN, WHERE, ORDER BY)
- Indexing for performance
- Concurrent read support

**Disadvantages**:
- Binary format (less human-readable)
- Requires schema migrations
- More complex than JSON

---

### Encrypted Persistence

**Modules**: Data Persistence Layer, Cloud Sync, Location Tracking, Learning Requests

**Pattern**:
```python
# Encrypt before write
encrypted = cipher_suite.encrypt(json.dumps(data).encode())
with open(file_path, 'wb') as f:
    f.write(encrypted)

# Decrypt on read
with open(file_path, 'rb') as f:
    encrypted = f.read()
data = json.loads(cipher_suite.decrypt(encrypted).decode())
```

**Advantages**:
- Data security at rest
- Compliance with privacy regulations
- Protection against file system access

**Disadvantages**:
- Performance overhead (~1-2ms per operation)
- Key management complexity
- Cannot inspect data directly

---

## Security Best Practices

### Password Storage

1. **Use bcrypt or pbkdf2_sha256**: Never SHA-256 alone
2. **Salt Automatically**: Passlib handles this
3. **Migrate Legacy Hashes**: Automatic migration on load
4. **Enforce Minimum Complexity**: 8+ characters, mixed case, numbers

### Encryption Key Management

1. **Environment Variables**: Store keys in `.env` [[.env]] file
2. **Never Commit Keys**: Add `.env` [[.env]] to `.gitignore`
3. **Rotate Keys Periodically**: Decrypt-reencrypt workflow
4. **File Permissions**: `chmod 600` for key files

### Data Validation

1. **Schema Validation**: Use Pydantic for all config
2. **Input Sanitization**: Validate before storage
3. **SQL Injection Prevention**: Parameterized queries only
4. **Path Traversal Protection**: `validate_filename()` checks

### Access Control

1. **Principle of Least Privilege**: Default to minimal permissions
2. **Role-Based Access**: Use Access Control module
3. **Audit Logging**: Log all sensitive operations
4. **Session Timeout**: 30-minute default, configurable

---

## Testing Strategy

### Unit Testing Pattern

```python
import tempfile
from app.core.module import ModuleClass

def test_module_operation():
    with tempfile.TemporaryDirectory() as tmpdir:
        instance = ModuleClass(data_dir=tmpdir)
        
        # Test operation
        result = instance.some_operation()
        assert result == expected_value
        
        # Verify persistence
        instance2 = ModuleClass(data_dir=tmpdir)
        assert instance2.state == instance.state
```

**Key Points**:
- Isolate tests with temporary directories
- Test persistence across instance reloads
- Verify state consistency
- Clean up automatically (context manager)

---

## Performance Considerations

### File I/O Optimization

1. **Lazy Loading**: Load data only when needed
2. **In-Memory Caching**: Cache frequently accessed data
3. **Batch Operations**: Group writes together
4. **Atomic Writes**: Prevent partial updates

### Database Optimization

1. **Indexing**: Add indices for frequently queried columns
2. **Connection Pooling**: Reuse connections
3. **Prepared Statements**: Cache query plans
4. **Pagination**: Limit result sets with LIMIT/OFFSET

### Encryption Overhead

- **AES-256-GCM**: Fastest (hardware acceleration)
- **ChaCha20-Poly1305**: Best for mobile/ARM
- **Fernet**: Moderate speed, includes timestamp validation

---

## Migration Guide

### JSON to SQLite Migration

```python
def migrate_json_to_sqlite():
    """Migrate from JSON storage to SQLite."""
    # 1. Load JSON data
    with open("data/old_storage.json") as f:
        json_data = json.load(f)
    
    # 2. Initialize SQLite storage
    storage = SQLiteStorage(db_path="data/new_storage.db")
    storage.initialize()
    
    # 3. Migrate data
    for key, value in json_data.items():
        storage.store("governance_state", key, value)
    
    # 4. Backup old JSON
    shutil.copy("data/old_storage.json", "data/old_storage.json.bak")
```

### Schema Version Upgrades

```python
def migrate_v1_to_v2():
    """Migrate schema from v1.0 to v2.0."""
    # 1. Load v1 data
    with open("data/config.json") as f:
        v1_data = json.load(f)
    
    # 2. Transform to v2 schema
    v2_data = {
        "version": "2.0",
        "users": v1_data.get("users", {}),
        "new_field": "default_value"  # New in v2
    }
    
    # 3. Save v2 data
    _atomic_write_json("data/config.json", v2_data)
```

---

## Troubleshooting

### Common Issues

#### File Lock Timeout

**Symptom**: `RuntimeError: Could not acquire lock for writing`

**Solutions**:
1. Check for stale lock files (`.lock` extension)
2. Increase timeout in `_acquire_lock(timeout=10.0)`
3. Verify no zombie processes holding locks

#### Encryption Key Mismatch

**Symptom**: `cryptography.fernet.InvalidToken`

**Solutions**:
1. Verify `FERNET_KEY` in `.env` [[.env]] matches original
2. Check for key rotation without re-encryption
3. Use backup if available

#### Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Solutions**:
1. Use connection pooling for concurrent access
2. Increase SQLite timeout: `conn.execute("PRAGMA busy_timeout=5000")`
3. Enable WAL mode: `conn.execute("PRAGMA journal_mode=WAL")`

---

## Documentation Standards

### Document Structure

All data model docs follow this structure:

1. **Header**: Module, storage location, persistence type, schema version
2. **Overview**: Purpose, key features
3. **Schema Structure**: JSON/SQL schema examples
4. **Field Specifications**: Table of fields with types and descriptions
5. **Operations**: CRUD operations and algorithms
6. **Usage Examples**: Real-world code snippets
7. **Security Considerations**: Best practices and warnings
8. **Testing Strategy**: Unit test patterns
9. **Performance Considerations**: Optimization tips
10. **Related Modules**: Integration points
11. **Future Enhancements**: Planned improvements

### Code Example Standards

- **Complete**: Runnable code with imports
- **Realistic**: Based on actual usage patterns
- **Commented**: Explain non-obvious logic
- **Error Handling**: Include try/except where appropriate

---

## Quick Reference

### File Locations

| Data Type | File Path |
|-----------|-----------|
| Users | `data/users.json` |
| AI Persona | `data/ai_persona/state.json` |
| Memory/Knowledge | `data/memory/knowledge.json` |
| Learning Requests | `data/learning_requests/request_index.json` |
| Telemetry | `logs/telemetry.json` |
| Access Control | `data/access_control.json` |
| Learning Reports | `data/continuous_learning/reports.json` |
| Location History | `location_history_{username}.json` |
| Emergency Contacts | `emergency_contacts_{username}.json` |
| Command Override | `data/command_override_config.json` |
| Settings | `data/settings.json` |
| Cloud Sync | `data/sync_metadata.json` |
| SQLite DB | `data/cognition.db` |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API access | None (required) |
| `HUGGINGFACE_API_KEY` | Hugging Face API access | None (required) |
| `FERNET_KEY` | Encryption key | Auto-generated |
| `TELEMETRY_ENABLED` | Enable telemetry | `false` |
| `TELEMETRY_MAX_EVENTS` | Max telemetry events | `1000` |
| `CLOUD_SYNC_URL` | Cloud sync endpoint | None |
| `SMTP_HOST` | Email server | None |
| `SMTP_PORT` | Email server port | `587` |
| `PROJECT_AI_ENV` | Environment (dev/prod) | `dev` |

---

## Contributing

### Adding New Data Models

1. **Create Documentation**: Follow structure in existing docs
2. **Update Index**: Add entry to this file
3. **Add Examples**: Include at least 3 usage examples
4. **Document Schema**: Provide JSON/SQL schema examples
5. **Test Coverage**: Include testing strategy section

### Documentation Review Checklist

- [ ] Schema structure documented with examples
- [ ] All fields have type and description
- [ ] CRUD operations explained with code
- [ ] Security considerations addressed
- [ ] Testing strategy outlined
- [ ] Performance tips included
- [ ] Related modules listed
- [ ] Usage examples provided (min 3)

---

## Glossary

| Term | Definition |
|------|------------|
| **ACID** | Atomicity, Consistency, Isolation, Durability (database properties) |
| **Atomic Write** | Write operation that completes fully or not at all |
| **Black Vault** | Permanent blocklist for denied learning content |
| **Fernet** | Symmetric encryption specification (AES-128-CBC + HMAC-SHA256) |
| **RBAC** | Role-Based Access Control |
| **ORM** | Object-Relational Mapping |
| **Schema Migration** | Process of updating database structure |
| **Semantic Versioning** | Version format: MAJOR.MINOR.PATCH |

---

**Document Count**: 15  
**Total Coverage**: 15 core data models + relationships + patterns  
**Completeness**: 100% of planned documentation delivered  

**Last Updated**: 2024-01-20  
**Next Review**: 2024-02-20  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/user_manager.py]]
