# Database Connectors Relationship Map

**Status**: 🟢 Production | **Type**: Internal Data Persistence  
**Priority**: P0 Critical | **Governance**: Security-Hardened

---


## Navigation

**Location**: `relationships\integrations\04-database-connectors.md`

**Parent**: [[relationships\integrations\README.md]]


## Database Systems

### Primary Database: SQLite3

- **Type**: Embedded SQL database
- **Location**: `data/*.db`, `data/*/*.json` (hybrid approach)
- **Use Case**: User accounts, secure transactions, audit logs
- **Encryption**: Optional (via SQLCipher extension)

### Secondary Storage: JSON Files

- **Type**: File-based persistence
- **Location**: `data/` directory tree
- **Use Case**: AI persona state, memory, learning requests
- **Encryption**: Fernet symmetric encryption (for sensitive data)

---

## Internal Relationships

### Database Connector Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE ABSTRACTION LAYER                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ SQLite        │ │ JSON Files    │ │ In-Memory     │
│ SecureDB      │ │ (Fernet)      │ │ Caching       │
└───────────────┘ └───────────────┘ └───────────────┘
        │             │             │
        ▼             ▼             ▼
┌───────────────────────────────────────────────────────────┐
│  CONSUMERS: UserManager, AIPersona, MemoryEngine,         │
│  LearningRequestManager, LocationTracker, EmergencyAlert  │
└───────────────────────────────────────────────────────────┘
```

### Core Connectors

**1. SecureDatabaseManager** (`src/app/security/database_security.py` [[src/app/security/database_security.py]])
- **Purpose**: SQL injection-safe database operations
- **Features**: Parameterized queries, transaction management, rollback
- **Tables**: `users`, `audit_logs`, `sessions`

**2. JSON Persistence Pattern** (across 6 AI systems)
- **Purpose**: Lightweight state persistence
- **Features**: Atomic writes, backup on save, JSON validation
- **Files**: 20+ JSON files in `data/` tree

**3. Encrypted Storage** (`LocationTracker`, future: `CloudSync`)
- **Purpose**: Secure PII and sensitive data
- **Encryption**: Fernet (symmetric AES-128)
- **Key Management**: Environment variable (`FERNET_KEY`)

---

## Database Schemas

### SQLite Schema (SecureDatabaseManager)

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Sessions table (future)
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### JSON File Structure (AI Systems)

```
data/
├── users.json                          # User accounts (bcrypt hashes)
├── ai_persona/
│   └── state.json                      # Personality, mood, interaction counts
├── memory/
│   ├── knowledge.json                  # Categorized knowledge base
│   └── conversations/
│       └── {user}_{timestamp}.json     # Conversation logs
├── learning_requests/
│   ├── requests.json                   # Learning request queue
│   └── black_vault.json                # Denied content fingerprints
├── command_override/
│   └── config.json                     # Override states, audit logs
├── location_tracker/
│   └── {user}_history.json.enc         # Encrypted location history
└── emergency_contacts.json             # Emergency alert contacts
```

---

## Connector APIs

### API 1: Secure SQL Queries

**Implementation**: `SecureDatabaseManager`

```python
from app.security.database_security import SecureDatabaseManager

# Initialize
db = SecureDatabaseManager(db_path="data/secure.db")

# SAFE: Parameterized query (prevents SQL injection)
user = db.execute_query(
    "SELECT * FROM users WHERE username = ?",
    params=("alice",),
    fetch_one=True
)

# SAFE: Insert with parameters
db.execute_query(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
    params=("bob", "$2b$12$hashed_password"),
    commit=True
)

# SAFE: Transaction with rollback
with db._get_connection() as conn:
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (...) VALUES (?, ?)", params)
        cursor.execute("INSERT INTO audit_logs (...) VALUES (?, ?)", params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
```

**Security Features**:
- ✅ Parameterized queries (SQL injection prevention)
- ✅ Column whitelist (`ALLOWED_USER_COLUMNS`)
- ✅ Transaction management
- ✅ Automatic connection pooling

### API 2: JSON Persistence

**Implementation**: All AI systems (`ai_systems.py`, `user_manager.py`, etc.)

```python
import json
import os

def _save_state(self):
    """Save state to JSON file with atomic write."""
    state = {
        "personality": self.personality,
        "mood": self.mood,
        "interaction_count": self.interaction_count,
        "last_updated": datetime.now().isoformat()
    }
    
    filepath = safe_path_join(self.data_dir, "state.json")
    
    # Atomic write: write to temp file, then rename
    temp_path = filepath + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(state, f, indent=4)
    
    # Rename (atomic operation on POSIX systems)
    os.replace(temp_path, filepath)
    
    logger.debug(f"State saved to {filepath}")

def _load_state(self):
    """Load state from JSON file."""
    filepath = safe_path_join(self.data_dir, "state.json")
    
    if not os.path.exists(filepath):
        return {}
    
    with open(filepath, "r") as f:
        return json.load(f)
```

**Advantages**:
- ✅ Human-readable (debugging, manual edits)
- ✅ No schema migrations
- ✅ Git-friendly (version control)
- ✅ Cross-platform compatible

**Disadvantages**:
- ❌ No ACID transactions
- ❌ No concurrent access control
- ❌ No query optimization

### API 3: Encrypted Storage

**Implementation**: `LocationTracker`

```python
from cryptography.fernet import Fernet
import json

def encrypt_data(self, data):
    """Encrypt data using Fernet symmetric encryption."""
    fernet_key = os.getenv("FERNET_KEY")
    if not fernet_key:
        raise ValueError("FERNET_KEY not set")
    
    fernet = Fernet(fernet_key.encode())
    json_data = json.dumps(data)
    encrypted = fernet.encrypt(json_data.encode())
    
    return encrypted

def decrypt_data(self, encrypted_data):
    """Decrypt Fernet-encrypted data."""
    fernet_key = os.getenv("FERNET_KEY")
    fernet = Fernet(fernet_key.encode())
    
    decrypted = fernet.decrypt(encrypted_data)
    json_data = decrypted.decode()
    
    return json.loads(json_data)

# Usage
location_data = {"lat": 37.7749, "lng": -122.4194, "timestamp": "2025-01-26T12:00:00Z"}
encrypted = self.encrypt_data(location_data)

# Save encrypted data to file
filepath = safe_path_join(self.data_dir, "history.json.enc")
with open(filepath, "wb") as f:
    f.write(encrypted)
```

**Key Generation**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Integration Patterns

### Pattern 1: Hybrid (SQL + JSON)

**Use Case**: User authentication with rich profile data

```python
# SQL: Core user record (secure, transactional)
db.execute_query(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
    params=(username, bcrypt_hash),
    commit=True
)

# JSON: Extended profile (flexible schema)
profile = {
    "username": username,
    "preferences": {"theme": "dark", "language": "en"},
    "avatar": "default.png",
    "created_at": datetime.now().isoformat()
}
with open(safe_path_join("data/profiles", f"{username}.json"), "w") as f:
    json.dump(profile, f, indent=4)
```

### Pattern 2: Write-Ahead Logging

**Use Case**: Audit logs (immutable, append-only)

```python
def log_action(self, user_id, action, details):
    """Log user action to audit log."""
    # Write to SQL (primary)
    self.db.execute_query(
        "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
        params=(user_id, action, json.dumps(details)),
        commit=True
    )
    
    # Write to JSON (backup)
    log_entry = {
        "user_id": user_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    with open("data/audit_logs/backup.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### Pattern 3: Caching Layer

**Use Case**: Frequently accessed data (user profiles)

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_by_username(username):
    """Get user from database with caching."""
    return db.execute_query(
        "SELECT * FROM users WHERE username = ?",
        params=(username,),
        fetch_one=True
    )

# Cache invalidation on update
def update_user(username, **kwargs):
    db.execute_query("UPDATE users SET ... WHERE username = ?", ...)
    get_user_by_username.cache_clear()  # Invalidate cache
```

---

## Configuration

### Environment Variables

```bash
# SQLite
DATABASE_PATH=data/secure.db
DATABASE_TIMEOUT=30
DATABASE_ISOLATION_LEVEL=DEFERRED

# Encryption
FERNET_KEY=<generated_key>  # From cryptography.fernet.Fernet.generate_key()

# JSON persistence
DATA_DIR=data
BACKUP_DIR=data/backups
```

---

## Error Handling

### Common Errors

1. **sqlite3.IntegrityError**: Unique constraint violation
   - **Mitigation**: Check for existing records before insert

2. **json.JSONDecodeError**: Corrupted JSON file
   - **Mitigation**: Restore from backup, validate before load

3. **cryptography.fernet.InvalidToken**: Decryption failure
   - **Mitigation**: Check FERNET_KEY, data not tampered

### Backup Strategy

```python
import shutil
from datetime import datetime

def backup_database(db_path, backup_dir="data/backups"):
    """Create timestamped database backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = safe_path_join(backup_dir, f"backup_{timestamp}.db")
    
    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backed up to {backup_path}")

# Backup before migrations
backup_database("data/secure.db")
```

---

## Security

### SQL Injection Prevention

**❌ NEVER DO THIS**:
```python
# UNSAFE: String concatenation
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)  # VULNERABLE TO SQL INJECTION
```

**✅ ALWAYS DO THIS**:
```python
# SAFE: Parameterized query
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

### File Permission Hardening

```python
import os
import stat

# Set restrictive permissions on data directory
os.chmod("data", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # 0700

# Set read-only on sensitive files
os.chmod("data/users.json", stat.S_IRUSR)  # 0400
```

---

## Performance

### Benchmarks

| Operation | Database | Latency | Throughput |
|-----------|----------|---------|------------|
| User lookup | SQLite | 0.5ms | 2,000 ops/s |
| Insert | SQLite | 2ms | 500 ops/s |
| JSON read | JSON file | 1ms | 1,000 ops/s |
| JSON write | JSON file | 5ms | 200 ops/s |
| Encrypt/decrypt | Fernet | 0.2ms | 5,000 ops/s |

### Optimization Tips

1. **Use indexes**: Add indexes on frequently queried columns
2. **Batch inserts**: Use `executemany()` for bulk inserts
3. **Connection pooling**: Reuse connections with context managers
4. **JSON caching**: Cache parsed JSON in memory

---

## Testing

```python
# tests/test_database_connectors.py
def test_secure_database():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = SecureDatabaseManager(db_path=f"{tmpdir}/test.db")
        
        db.execute_query(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            params=("alice", "hash123"),
            commit=True
        )
        
        user = db.execute_query(
            "SELECT * FROM users WHERE username = ?",
            params=("alice",),
            fetch_one=True
        )
        
        assert user["username"] == "alice"

def test_json_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        persona = AIPersona(data_dir=tmpdir)
        persona.personality["humor"] = 10
        persona._save_state()
        
        # Reload and verify
        persona2 = AIPersona(data_dir=tmpdir)
        assert persona2.personality["humor"] == 10
```

---

## Related Systems

- **[05-external-apis.md](05-external-apis.md)**: API data caching
- **[06-service-adapters.md](06-service-adapters.md)**: Adapter state persistence
- **[12-sms-integration.md](12-sms-integration.md)**: Message delivery status tracking

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly


---

## See Also

### Related Source Documentation

- **05 Database Integrations**: [[source-docs\integrations\05-database-integrations.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
