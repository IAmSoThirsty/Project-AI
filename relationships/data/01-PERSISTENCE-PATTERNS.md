# Persistence Patterns and Data Flows

**Component:** Data Persistence Layer Patterns  
**Agent:** AGENT-058  
**Date:** 2026-04-20

---


## Navigation

**Location**: `relationships\data\01-PERSISTENCE-PATTERNS.md`

**Parent**: [[relationships\data\README.md]]


## Overview

This document details the persistence patterns used across Project-AI's 12 data systems, including JSON-based persistence, encrypted state management (see [[02-ENCRYPTION-CHAINS.md|Encryption Chains]]), database operations (see [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]]), and atomic write mechanisms. For performance metrics, see [[../monitoring/05-performance-monitoring.md|Performance Monitoring]].

---

## Core Persistence Mechanisms

### 1. Atomic JSON Write Pattern

**Implementation:** `_atomic_write_json()` in `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]]

```python
def _atomic_write_json(file_path: str, obj: Any) -> None:
    """Write JSON to temporary file and atomically replace target.
    
    Uses lockfile to prevent concurrent writer corruption.
    """
    # 1. Acquire lock
    lockfile = file_path + ".lock"
    if not _acquire_lock(lockfile, timeout=5.0):
        raise RuntimeError(f"Could not acquire lock for writing {file_path}")
    
    try:
        # 2. Create temp file in same directory (atomic rename requirement)
        fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp", suffix=".json")
        
        # 3. Write JSON with proper encoding
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        
        # 4. Atomic replace (single filesystem operation)
        os.replace(tmp_path, file_path)
    finally:
        # 5. Always release lock
        _release_lock(lockfile)
```

**Benefits:**
- **Atomic:** Write completes fully or not at all (no partial files)
- **Concurrent-safe:** Lockfile prevents multiple writers
- **Crash-resistant:** `fsync()` ensures data on disk before replace
- **Stale lock handling:** Auto-reclaims locks from dead processes

**Usage Locations:**
```
AIPersona._save_state()                  → data/ai_persona/state.json
MemoryExpansionSystem._save_knowledge()  → data/memory/knowledge.json
LearningRequestManager._save_state()     → data/learning_requests/requests.json
CommandOverrideSystem._save_config()     → data/command_override_config.json
CloudSyncManager._save_sync_metadata()   → data/sync_metadata.json (→ [[03-SYNC-STRATEGIES.md|Sync Strategies]])
TelemetryManager.send_event()            → logs/telemetry.json (→ [[../monitoring/04-telemetry-system.md|Telemetry System]])
```

---

### 2. Lockfile Pattern

**Implementation:** `_acquire_lock()` and `_release_lock()`

```python
def _acquire_lock(lock_path: str, timeout: float = 5.0, 
                  poll: float = 0.05, stale_after: float = 30.0) -> bool:
    """Acquire lock with stale detection and process liveness check."""
    start = time.time()
    
    while True:
        try:
            # Exclusive create (O_EXCL)
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            
            # Write PID and timestamp for stale detection
            _write_lockfile(lock_path, os.getpid(), time.time())
            return True
            
        except FileExistsError:
            # Check if lock is stale
            info = _read_lockfile(lock_path)
            if info:
                pid, ts = info
                age = time.time() - ts
                
                # Reclaim stale lock (process dead or timeout exceeded)
                if age > stale_after or not _is_process_alive(pid):
                    os.remove(lock_path)
                    continue
            
            # Wait and retry
            if (time.time() - start) >= timeout:
                return False
            time.sleep(poll)
```

**Lock File Format:**
```
{pid}\n
{timestamp}\n
```

**Stale Lock Detection:**
- **Age check:** Lock older than 30 seconds
- **Process liveness:** Check if owning PID still exists
- **Auto-reclaim:** Remove stale locks automatically

**Edge Cases Handled:**
1. **Crashed writer:** Lock file remains but process dead → reclaimed
2. **Hung writer:** Lock older than stale_after → reclaimed
3. **Concurrent acquirers:** Only one succeeds (O_EXCL atomicity)
4. **Cross-platform:** Works on Windows and Unix (os.kill(pid, 0))

---

### 3. Encrypted State Persistence Pattern

**Implementation:** `EncryptedStateManager` in `src/app/core/data_persistence.py` [[src/app/core/data_persistence.py]]

See [[02-ENCRYPTION-CHAINS.md|Encryption Chains]] for encryption algorithm details and [[../security/03_defense_layers.md|Defense Layers]] for security architecture.

```python
class EncryptedStateManager:
    """Multi-algorithm encrypted state persistence with key rotation."""
    
    def save_encrypted_state(self, state_id: str, state_data: dict) -> bool:
        # Step 1: Serialize to JSON
        json_data = json.dumps(state_data, indent=2, default=str)
        data_bytes = json_data.encode("utf-8")
        
        # Step 2: Compress (gzip)
        compressed = gzip.compress(data_bytes)
        
        # Step 3: Encrypt (algorithm-specific)
        encrypted, metadata = self.encrypt_data(compressed)
        
        # Step 4: Save encrypted blob
        state_file = self.data_dir / f"{state_id}.enc"
        with open(state_file, "wb") as f:
            f.write(encrypted)
        
        # Step 5: Save metadata (plaintext JSON)
        metadata_file = self.data_dir / f"{state_id}.meta"
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "original_size": len(data_bytes),
            "compressed_size": len(compressed),
            "encrypted_size": len(encrypted),
        })
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
```

**Metadata File Example:**
```json
{
  "algorithm": "AES-256-GCM",
  "key_id": "20260420",
  "nonce_length": 12,
  "timestamp": "2026-04-20T14:30:00.123456",
  "original_size": 4567,
  "compressed_size": 1234,
  "encrypted_size": 1246
}
```

**Decryption Flow:**
```python
def load_encrypted_state(self, state_id: str) -> dict | None:
    # 1. Load metadata (determines algorithm/key)
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    # 2. Load encrypted blob
    with open(state_file, "rb") as f:
        encrypted = f.read()
    
    # 3. Decrypt (algorithm from metadata)
    compressed = self.decrypt_data(encrypted, metadata)
    
    # 4. Decompress
    data_bytes = gzip.decompress(compressed)
    
    # 5. Parse JSON
    return json.loads(data_bytes.decode("utf-8"))
```

---

### 4. Database Persistence Pattern

**Implementation:** `SecureDatabaseManager` in `src/app/security/database_security.py` [[src/app/security/database_security.py]]

See [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for SQL injection prevention and [[../security/02_threat_models.md|Threat Models]] for security considerations.

```python
class SecureDatabaseManager:
    """Parameterized SQL with transaction management."""
    
    @contextmanager
    def _get_connection(self):
        """Context manager for transaction safety."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Dict-like access
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_user(self, username: str, password_hash: str, email: str):
        """Parameterized insert (SQL injection safe)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            """, (username, password_hash, email))
            return cursor.lastrowid
```

**Transaction Pattern:**
```
BEGIN TRANSACTION (implicit in context manager)
   ↓
Execute SQL operations (parameterized)
   ↓
Success? → COMMIT
Failure? → ROLLBACK
   ↓
Close connection (always in finally block)
```

**SQL Injection Prevention:**
```python
# ❌ VULNERABLE (string concatenation)
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ SAFE (parameterized)
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

---

### 5. State Lifecycle Pattern

**Common pattern across AIPersona, MemoryExpansion, LearningRequest:**

```python
class SystemWithState:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.state_file = os.path.join(data_dir, "state.json")
        os.makedirs(data_dir, exist_ok=True)
        
        # 1. Initialize default state
        self.state = self._get_default_state()
        
        # 2. Load persisted state (if exists)
        self._load_state()
    
    def _get_default_state(self) -> dict:
        """Override in subclass."""
        return {}
    
    def _load_state(self) -> None:
        """Load state from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.state.update(loaded)
            except Exception as e:
                logger.error("Error loading state: %s", e)
    
    def _save_state(self) -> None:
        """Save state using atomic write."""
        try:
            _atomic_write_json(self.state_file, self.state)
        except Exception as e:
            logger.exception("Error saving state: %s", e)
    
    def modify_state(self, updates: dict):
        """Public method to modify state."""
        self.state.update(updates)
        self._save_state()  # Persist immediately
```

**Initialization Sequence:**
```
1. Create data directory (os.makedirs)
2. Initialize in-memory state with defaults
3. Attempt to load from disk (graceful if missing)
4. Merge loaded state over defaults
5. Ready for operations
```

**Update Pattern:**
```
1. Modify in-memory state
2. Call _save_state() immediately
3. Atomic write to disk (locked)
4. State persisted and consistent
```

---

## System-Specific Persistence Details

### AIPersona Persistence

**Files:**
- `data/ai_persona/state.json`

**Schema:**
```json
{
  "personality": {
    "curiosity": 0.8,
    "patience": 0.9,
    "empathy": 0.85,
    "helpfulness": 0.95,
    "playfulness": 0.6,
    "formality": 0.3,
    "assertiveness": 0.5,
    "thoughtfulness": 0.9
  },
  "mood": {
    "energy": 0.7,
    "enthusiasm": 0.75,
    "contentment": 0.8,
    "engagement": 0.5
  },
  "interactions": 42
}
```

**Update Triggers:**
- `update_conversation_state(is_user)` → increment interactions
- `adjust_trait(trait, delta)` → modify personality trait
- Every change immediately persisted via `_save_state()`

---

### MemoryExpansionSystem Persistence

**Files:**
- `data/memory/knowledge.json`
- `data/memory/conversations.json` (future)

**Knowledge Base Schema:**
```json
{
  "technical": [
    {"key": "python_best_practices", "value": "...", "timestamp": "..."}
  ],
  "personal": [],
  "general": [],
  "code_snippets": [],
  "important_facts": [],
  "user_preferences": []
}
```

**Update Pattern:**
```python
def add_knowledge(self, category: str, key: str, value: str):
    if category not in self.knowledge_base:
        self.knowledge_base[category] = []
    
    self.knowledge_base[category].append({
        "key": key,
        "value": value,
        "timestamp": datetime.now().isoformat()
    })
    
    self._save_knowledge()  # Atomic write
```

---

### LearningRequestManager Persistence

**Files:**
- `data/learning_requests/requests.json`

**Schema:**
```json
{
  "requests": [
    {
      "id": "req_123",
      "topic": "quantum computing",
      "content": "Explain quantum entanglement",
      "status": "pending",
      "timestamp": "2026-04-20T14:00:00",
      "approved": false,
      "fingerprint": "sha256_hash_of_content"
    }
  ],
  "black_vault": [
    "sha256_hash_of_denied_content_1",
    "sha256_hash_of_denied_content_2"
  ]
}
```

**Black Vault Pattern:**
```python
def deny_request(self, request_id: str):
    request = self.get_request(request_id)
    
    # Calculate content fingerprint
    fingerprint = hashlib.sha256(request["content"].encode()).hexdigest()
    
    # Add to black vault (permanent deny list)
    if fingerprint not in self.black_vault:
        self.black_vault.append(fingerprint)
    
    # Remove request
    self.requests = [r for r in self.requests if r["id"] != request_id]
    
    self._save_state()
```

---

### UserManager Persistence

**Files:**
- `data/users.json`

**Schema:**
```json
{
  "admin": {
    "password_hash": "$pbkdf2-sha256$29000$...",
    "email": "admin@example.com",
    "role": "admin",
    "failed_attempts": 0,
    "locked_until": null,
    "created_at": "2026-04-20T10:00:00"
  }
}
```

**Password Migration Pattern:**
```python
def _migrate_plaintext_passwords(self):
    """One-time migration from plaintext to hashed (see [[../security/02_threat_models.md|Threat Models]])."""
    migrated = False
    for uname, udata in self.users.items():
        if "password" in udata and "password_hash" not in udata:
            # Hash plaintext password
            udata["password_hash"] = pwd_context.hash(udata["password"])
            del udata["password"]
            migrated = True
    
    if migrated:
        self.save_users()  # Persist migration
```

---

### CloudSyncManager Persistence

**Files:**
- `data/sync_metadata.json`

See [[03-SYNC-STRATEGIES.md|Sync Strategies]] for sync flow details and [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for encryption patterns.

**Schema:**
```json
{
  "user123": {
    "last_upload": "2026-04-20T14:30:00",
    "last_download": "2026-04-20T14:25:00",
    "device_id": "abc123..."
  }
}
```

**Sync Metadata Update:**
```python
def sync_upload(self, username: str, data: dict) -> bool:
    # ... upload logic ...
    
    # Update metadata on success
    self.sync_metadata[username] = {
        "last_upload": datetime.now().isoformat(),
        "device_id": self.device_id,
    }
    self._save_sync_metadata()  # Atomic write
```

---

### TelemetryManager Persistence

**Files:**
- `logs/telemetry.json`

See [[../monitoring/04-telemetry-system.md|Telemetry System]] for event tracking architecture and [[../configuration/02_environment_manager_relationships.md|Environment Manager]] for TELEMETRY_ENABLED configuration.

**Schema:**
```json
[
  {
    "name": "user_login",
    "timestamp": 1735012345.678,
    "payload": {"username": "user123", "success": true}
  },
  {
    "name": "state_change",
    "timestamp": 1735012350.123,
    "payload": {"system": "ai_persona", "field": "mood.energy"}
  }
]
```

**Rotation Pattern:**
```python
def send_event(name: str, payload: dict | None = None) -> None:
    if not TelemetryManager.enabled():
        return
    
    # Load existing events
    events = []
    if os.path.exists(TELEMETRY_FILE):
        with open(TELEMETRY_FILE, encoding="utf-8") as f:
            events = json.load(f)
    
    # Append new event
    events.append({
        "name": name,
        "timestamp": time.time(),
        "payload": payload or {}
    })
    
    # Rotate (keep last N events)
    if len(events) > TELEMETRY_MAX_EVENTS:
        events = events[-TELEMETRY_MAX_EVENTS:]
    
    # Atomic write
    _atomic_write_json(TELEMETRY_FILE, events)
```

---

## Performance Characteristics

See [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] for comprehensive performance metrics and [[../monitoring/02-metrics-system.md|Metrics System]] for tracking.

### Atomic Write Performance

**Benchmark (typical JSON file ~10KB):**
```
Operation                    Time (ms)
──────────────────────────────────────
Lock acquisition             0.1-1.0
Temp file creation           0.5
JSON serialization           1.0-5.0
Write + fsync                5.0-20.0
Atomic rename                0.1
Lock release                 0.1
──────────────────────────────────────
Total                        7-27 ms
```

**Bottlenecks:**
1. **fsync() duration:** Disk-dependent (SSD vs HDD)
2. **Lock contention:** High-frequency updates can queue
3. **JSON serialization:** Large objects (>100KB) slow

**Optimizations:**
- **Batch updates:** Coalesce multiple changes before save
- **Async writes:** Background thread (not currently implemented)
- **Delta writes:** Store only changes (not currently implemented)

---

### Encrypted State Performance

**Encryption Overhead:**

See [[02-ENCRYPTION-CHAINS.md|Encryption Chains]] for algorithm-specific performance and [[../security/03_defense_layers.md|Defense Layers]] for security vs. performance trade-offs.

```
Operation                    Overhead
─────────────────────────────────────
Fernet encryption            ~15%
AES-256-GCM                  ~10% (hardware accel)
ChaCha20-Poly1305            ~12%
gzip compression             ~60% size reduction
───────────────────────────────────────
Total (serialize → compress → encrypt)
  10KB JSON → 4KB compressed → 4.4KB encrypted
  Time: ~30-50ms
```

---

### Database Performance

**SQLite Characteristics:**
```
Operation                    Time (typical)
─────────────────────────────────────────
Single INSERT                0.1-1 ms
Single SELECT by index       0.1 ms
Transaction (100 INSERTs)    10-50 ms
Full table scan (1000 rows)  5-20 ms
```

**Optimization:** Use transactions for bulk operations:
```python
# Slow (1000 commits)
for i in range(1000):
    cursor.execute("INSERT INTO ...", (...))
    conn.commit()

# Fast (1 commit)
for i in range(1000):
    cursor.execute("INSERT INTO ...", (...))
conn.commit()  # After loop
```

---

## Error Handling Patterns

See [[../monitoring/06-error-tracking.md|Error Tracking]] for comprehensive error logging and alerting.

### Graceful Load Failure

```python
def _load_state(self) -> None:
    """Load state with graceful fallback."""
    if os.path.exists(self.state_file):
        try:
            with open(self.state_file, encoding="utf-8") as f:
                loaded = json.load(f)
                self.state.update(loaded)
            logger.info("State loaded from %s", self.state_file)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", self.state_file, e)
            # Continue with default state
        except Exception as e:
            logger.exception("Failed to load state: %s", e)
            # Continue with default state
    else:
        logger.info("No existing state file, using defaults")
```

**Failure Modes:**
1. **File missing:** Use defaults (normal for first run)
2. **Corrupted JSON:** Log error, use defaults
3. **Permission denied:** Log error, use defaults
4. **Disk full (on save):** Exception raised, state unchanged

---

### Lock Timeout Handling

```python
def _save_state(self) -> None:
    """Save state with lock timeout handling."""
    try:
        _atomic_write_json(self.state_file, self.state)
    except RuntimeError as e:
        if "Could not acquire lock" in str(e):
            logger.warning("Lock timeout saving state, will retry later")
            # Queue for retry (not implemented)
        else:
            raise
    except Exception as e:
        logger.exception("Failed to save state: %s", e)
        # State remains in memory, can retry
```

---

## Consistency Guarantees

### Atomicity Guarantees

1. **JSON files:** Single atomic `os.replace()` (filesystem guarantee)
2. **Encrypted files:** Two files (.enc + .meta) NOT atomic together
   - Recovery: If .meta missing, consider .enc invalid
3. **Database:** ACID transactions (SQLite guarantee)

### Durability Guarantees

1. **fsync() called:** Data on disk before returning
2. **Atomic rename:** No partial files visible
3. **Crash recovery:** Last completed write is recoverable

### Isolation Guarantees

1. **Lockfiles:** Serialize writers (readers not blocked)
2. **Database:** SQLite default isolation (SERIALIZABLE)

---

## Migration and Versioning

### Data Version Management

```python
class DataMigrationManager:
    def __init__(self):
        self.current_version = DataVersion(1, 0, 0)
        self.migrations = {}
    
    def register_migration(self, from_version: DataVersion, 
                          to_version: DataVersion, 
                          migration_fn: callable):
        """Register migration function."""
        key = f"{from_version} -> {to_version}"
        self.migrations[key] = migration_fn
    
    def migrate(self, data: dict, from_version: DataVersion) -> dict:
        """Apply migrations to bring data up to current version."""
        current = from_version
        
        while current < self.current_version:
            # Find next migration
            next_version = self._find_next_version(current)
            key = f"{current} -> {next_version}"
            
            if key not in self.migrations:
                raise ValueError(f"No migration path from {current}")
            
            # Apply migration
            logger.info("Applying migration %s", key)
            data = self.migrations[key](data)
            current = next_version
        
        return data
```

**Example Migration:**
```python
def migrate_1_0_to_1_1(data: dict) -> dict:
    """Add lockout fields to user data."""
    for user in data.get("users", {}).values():
        if "failed_attempts" not in user:
            user["failed_attempts"] = 0
        if "locked_until" not in user:
            user["locked_until"] = None
    return data

migration_mgr.register_migration(
    DataVersion(1, 0, 0),
    DataVersion(1, 1, 0),
    migrate_1_0_to_1_1
)
```

---

## Best Practices

### When to Use Each Pattern

1. **Atomic JSON Write:**
   - Small to medium files (<10MB)
   - Frequent updates
   - Need crash resistance
   - Examples: AI state, user profiles

2. **Encrypted State Manager:**
   - Sensitive data requiring encryption
   - Large state blobs (compression helps)
   - Key rotation needed
   - Examples: Secure configurations, private keys

3. **Database (SQLite):**
   - Structured data with relationships
   - Complex queries needed
   - ACID transactions required
   - Examples: Audit logs, user sessions

4. **Plain File (No Lock):**
   - Append-only logs
   - Read-only configuration
   - Single writer guaranteed
   - Examples: Application logs

---

### Persistence Checklist

```markdown
✅ Create data directory in __init__ (os.makedirs)
✅ Initialize in-memory state with defaults
✅ Load existing state (graceful if missing)
✅ Use atomic writes for updates (_atomic_write_json)
✅ Call _save_state() after every modification
✅ Handle JSON decode errors gracefully
✅ Log errors but don't crash on load failure
✅ Use appropriate file permissions (0o600 for sensitive)
✅ Document schema in docstrings or separate docs
✅ Plan for schema evolution (versioning)
```

---

## Related Documentation

### Data Layer Documentation
- **[[00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]]** - Complete system architecture
- **[[02-ENCRYPTION-CHAINS.md|Encryption Chains]]** - Encryption algorithms and key management
- **[[03-SYNC-STRATEGIES.md|Sync Strategies]]** - Cloud synchronization patterns
- **[[04-BACKUP-RECOVERY.md|Backup & Recovery]]** - Backup and disaster recovery

### Cross-System Documentation
- **[[../security/01_security_system_overview.md|Security System Overview]]** - Security architecture
- **[[../security/02_threat_models.md|Threat Models]]** - Password hashing and threat mitigation
- **[[../security/03_defense_layers.md|Defense Layers]]** - Multi-layer encryption
- **[[../security/06_data_flow_diagrams.md|Data Flow Diagrams]]** - Database security flows
- **[[../monitoring/04-telemetry-system.md|Telemetry System]]** - Event tracking
- **[[../monitoring/05-performance-monitoring.md|Performance Monitoring]]** - Performance metrics
- **[[../monitoring/06-error-tracking.md|Error Tracking]]** - Error logging
- **[[../configuration/01_config_loader_relationships.md|Config Loader]]** - Configuration management
- **[[../configuration/02_environment_manager_relationships.md|Environment Manager]]** - Environment variables

---

**Document Version:** 1.0.0  
**Related:** [[00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]]  
**Next:** [[02-ENCRYPTION-CHAINS.md|Encryption Chains]]


---

## See Also

### Related Source Documentation

- **05 Data Persistence Layer Model**: [[source-docs\data-models\05-data-persistence-layer-model.md]]
- **Documentation Index**: [[source-docs\data-models\README.md]]
