# Storage Engine Abstraction Layer

## Overview

The Storage module (`src/app/core/storage.py`) provides a unified abstraction layer for data persistence, supporting both transactional SQLite storage (recommended) and legacy JSON file storage. This design enables flexible data management with thread-safe operations, schema evolution, and connection pooling.

**Location**: `src/app/core/storage.py`  
**Lines of Code**: ~500  
**Key Features**: Transactional SQLite, JSON fallback, schema migration, thread-safe  
**Dependencies**: sqlite3, json, threading

---

## Architecture

### Storage Hierarchy

```
StorageEngine (ABC)
    ├── initialize()
    ├── store()
    ├── retrieve()
    ├── query()
    ├── delete()
    └── close()

├── SQLiteStorage (Primary)
│   ├── Transactional operations
│   ├── Schema evolution
│   ├── Connection pooling
│   ├── Thread-safe locking
│   └── Prepared statements
│
└── JSONStorage (Legacy)
    ├── File-based persistence
    ├── Simple key-value store
    ├── No transactions
    └── Backward compatibility
```

---

## Core Components

### 1. StorageEngine (Abstract Base Class)

**Purpose**: Defines the contract all storage engines must implement.

```python
class StorageEngine(ABC):
    """Abstract base class for storage engines."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage engine and create necessary structures."""
        pass
    
    @abstractmethod
    def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
        """Store data in the specified table with the given key."""
        pass
    
    @abstractmethod
    def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
        """Retrieve data from the specified table by key."""
        pass
    
    @abstractmethod
    def query(
        self, table: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Query data from the specified table with optional filters."""
        pass
    
    @abstractmethod
    def delete(self, table: str, key: str) -> bool:
        """Delete data from the specified table by key."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the storage engine and cleanup resources."""
        pass
```

**Design Pattern**: Strategy Pattern - allows switching between storage implementations without changing client code.

---

## 2. SQLiteStorage (Primary Engine)

**Purpose**: Production-grade transactional storage with ACID guarantees.

### Configuration

```python
class SQLiteStorage(StorageEngine):
    # Whitelist of allowed table names (SQL injection prevention)
    ALLOWED_TABLES = {
        "governance_state",
        "governance_decisions",
        "execution_history",
        "reflection_history",
        "memory_records",
    }
    
    def __init__(self, db_path: str = "data/cognition.db"):
        self.db_path = db_path
        self.lock = Lock()  # Thread safety
        self._conn: sqlite3.Connection | None = None
```

---

### Key Methods

#### initialize()
```python
def initialize(self) -> None:
    """Create database and tables if they don't exist."""
```

**Function**: Sets up database schema on first run.

**Tables Created**:
- `governance_state`: Current governance configuration
- `governance_decisions`: Decision audit trail
- `execution_history`: Action execution records
- `reflection_history`: Self-reflection insights
- `memory_records`: Long-term memory storage

**Schema Example**:
```sql
CREATE TABLE IF NOT EXISTS governance_state (
    key TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

#### store()
```python
def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
    """Store data with UPSERT (insert or update)."""
```

**SQL Pattern**:
```sql
INSERT INTO table (key, data, updated_at)
VALUES (?, ?, CURRENT_TIMESTAMP)
ON CONFLICT(key) DO UPDATE SET
    data = excluded.data,
    updated_at = CURRENT_TIMESTAMP
```

**Example**:
```python
storage = SQLiteStorage()
storage.initialize()

success = storage.store(
    "governance_state",
    "four_laws_enabled",
    {"enabled": True, "strictness": "high"}
)
```

**Thread Safety**: Uses `self.lock` to prevent concurrent writes.

---

#### retrieve()
```python
def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
    """Retrieve data by key."""
```

**Returns**:
- Dictionary of data if found
- `None` if key doesn't exist

**Example**:
```python
config = storage.retrieve("governance_state", "four_laws_enabled")
if config:
    print(f"Four Laws enabled: {config['enabled']}")
else:
    print("Configuration not found")
```

---

#### query()
```python
def query(
    self, table: str, filters: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Query multiple records with optional filters."""
```

**Filters**: Dictionary of column-value pairs (AND logic)

**Example**:
```python
# Get all decisions from the last hour
recent_decisions = storage.query(
    "governance_decisions",
    filters={"created_at": ">= datetime('now', '-1 hour')"}
)

for decision in recent_decisions:
    print(f"Decision: {decision['action']} - {decision['result']}")
```

**Note**: Filter values are parameterized to prevent SQL injection.

---

#### delete()
```python
def delete(self, table: str, key: str) -> bool:
    """Delete a record by key."""
```

**Returns**: `True` if deleted, `False` if not found

**Example**:
```python
was_deleted = storage.delete("governance_state", "deprecated_config")
```

---

### Connection Management

#### Context Manager Pattern
```python
@contextmanager
def _get_connection(self):
    """Thread-safe connection context manager."""
    with self.lock:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Dict-like row access
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Database error: %s", e)
            raise
        finally:
            conn.close()
```

**Usage Internally**:
```python
def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
    with self._get_connection() as conn:
        cursor = conn.cursor()
        # ... execute queries
        return True
```

**Benefits**:
- Automatic connection cleanup
- Transaction rollback on error
- Thread-safe locking

---

### Schema Evolution

```python
def _migrate_schema(self, current_version: int, target_version: int):
    """Apply schema migrations."""
    migrations = {
        1: self._migrate_v1_to_v2,
        2: self._migrate_v2_to_v3,
    }
    
    for version in range(current_version, target_version):
        if version in migrations:
            migrations[version]()
            logger.info("Migrated schema to v%d", version + 1)
```

**Example Migration**:
```python
def _migrate_v1_to_v2(self):
    """Add indexed column for faster queries."""
    with self._get_connection() as conn:
        conn.execute("""
            ALTER TABLE governance_decisions
            ADD COLUMN action_type TEXT
        """)
        conn.execute("""
            CREATE INDEX idx_action_type
            ON governance_decisions(action_type)
        """)
```

---

## 3. JSONStorage (Legacy Engine)

**Purpose**: Backward compatibility with JSON file-based storage.

```python
class JSONStorage(StorageEngine):
    """Legacy JSON file storage (deprecated)."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict] = {}
```

### Key Methods

#### store()
```python
def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
    """Store to JSON file: data/{table}.json"""
    file_path = self.data_dir / f"{table}.json"
    
    # Load existing data
    if file_path.exists():
        with open(file_path) as f:
            table_data = json.load(f)
    else:
        table_data = {}
    
    # Update and save
    table_data[key] = data
    with open(file_path, 'w') as f:
        json.dump(table_data, f, indent=2)
    
    return True
```

**File Structure**:
```
data/
├── governance_state.json
├── governance_decisions.json
├── execution_history.json
└── memory_records.json
```

**Limitations**:
- No transactions (file write is atomic, but no rollback)
- No concurrent write safety
- Entire file loaded into memory for updates
- No query optimization

---

## Usage Patterns

### Pattern 1: Governance State Management

```python
from app.core.storage import SQLiteStorage

class GovernanceSystem:
    def __init__(self):
        self.storage = SQLiteStorage("data/governance.db")
        self.storage.initialize()
    
    def save_state(self, state_data: dict):
        """Persist governance state."""
        self.storage.store(
            "governance_state",
            "current_state",
            state_data
        )
    
    def load_state(self) -> dict:
        """Load governance state."""
        state = self.storage.retrieve("governance_state", "current_state")
        return state or self._default_state()
    
    def log_decision(self, decision: dict):
        """Log governance decision to history."""
        decision_id = f"decision_{int(time.time())}"
        self.storage.store(
            "governance_decisions",
            decision_id,
            decision
        )
    
    def get_decision_history(self, limit: int = 100) -> list[dict]:
        """Retrieve recent decisions."""
        decisions = self.storage.query("governance_decisions")
        return sorted(decisions, key=lambda d: d.get("timestamp", 0), reverse=True)[:limit]
```

---

### Pattern 2: Memory System Integration

```python
class MemorySystem:
    def __init__(self):
        self.storage = SQLiteStorage("data/memory.db")
        self.storage.initialize()
    
    def store_memory(self, memory_id: str, memory_data: dict):
        """Store long-term memory."""
        memory_data["created_at"] = datetime.now().isoformat()
        self.storage.store("memory_records", memory_id, memory_data)
    
    def recall_memory(self, memory_id: str) -> dict | None:
        """Retrieve specific memory."""
        return self.storage.retrieve("memory_records", memory_id)
    
    def search_memories(self, category: str) -> list[dict]:
        """Search memories by category."""
        return self.storage.query(
            "memory_records",
            filters={"category": category}
        )
    
    def forget_memory(self, memory_id: str):
        """Delete a memory (GDPR compliance)."""
        self.storage.delete("memory_records", memory_id)
```

---

### Pattern 3: Migration from JSON to SQLite

```python
def migrate_json_to_sqlite():
    """Migrate data from JSON storage to SQLite."""
    json_storage = JSONStorage("data")
    sqlite_storage = SQLiteStorage("data/cognition.db")
    sqlite_storage.initialize()
    
    tables_to_migrate = [
        "governance_state",
        "governance_decisions",
        "execution_history",
        "memory_records",
    ]
    
    for table in tables_to_migrate:
        print(f"Migrating {table}...")
        
        # Query all records from JSON
        records = json_storage.query(table)
        
        # Store in SQLite
        for record in records:
            key = record.get("id") or record.get("key")
            if key:
                sqlite_storage.store(table, key, record)
        
        print(f"Migrated {len(records)} records from {table}")
    
    print("Migration complete!")
```

---

## Security Considerations

### 1. SQL Injection Prevention

**Whitelist Pattern**:
```python
ALLOWED_TABLES = {
    "governance_state",
    "governance_decisions",
    # ...
}

def _validate_table(self, table: str):
    if table not in self.ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' not in whitelist")
```

**Parameterized Queries**:
```python
# BAD: String concatenation
query = f"SELECT * FROM {table} WHERE key = '{key}'"  # SQL injection!

# GOOD: Parameterized
query = "SELECT * FROM {table} WHERE key = ?"
cursor.execute(query, (key,))
```

---

### 2. Data Encryption

**Enhancement for Sensitive Data**:
```python
from cryptography.fernet import Fernet

class EncryptedSQLiteStorage(SQLiteStorage):
    def __init__(self, db_path: str, encryption_key: bytes):
        super().__init__(db_path)
        self.cipher = Fernet(encryption_key)
    
    def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
        # Encrypt data before storing
        data_json = json.dumps(data)
        encrypted = self.cipher.encrypt(data_json.encode())
        return super().store(table, key, {"encrypted_data": encrypted.decode()})
    
    def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
        result = super().retrieve(table, key)
        if result and "encrypted_data" in result:
            # Decrypt data after retrieval
            encrypted = result["encrypted_data"].encode()
            decrypted = self.cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        return result
```

---

### 3. Access Control

```python
class SecureStorage(SQLiteStorage):
    def __init__(self, db_path: str, access_policy: dict):
        super().__init__(db_path)
        self.access_policy = access_policy  # {user: [tables]}
    
    def store(self, table: str, key: str, data: dict[str, Any], user: str) -> bool:
        if not self._check_access(user, table, "write"):
            raise PermissionError(f"User '{user}' cannot write to '{table}'")
        return super().store(table, key, data)
    
    def _check_access(self, user: str, table: str, operation: str) -> bool:
        user_permissions = self.access_policy.get(user, [])
        return table in user_permissions
```

---

## Performance Optimization

### 1. Batch Operations

```python
def store_batch(self, table: str, records: list[tuple[str, dict]]) -> bool:
    """Store multiple records in a single transaction."""
    with self._get_connection() as conn:
        cursor = conn.cursor()
        
        for key, data in records:
            self._validate_table(table)
            data_json = json.dumps(data)
            
            cursor.execute(f"""
                INSERT INTO {table} (key, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, data_json))
        
        return True

# Usage
records = [
    ("config1", {"value": 1}),
    ("config2", {"value": 2}),
    ("config3", {"value": 3}),
]
storage.store_batch("governance_state", records)
```

---

### 2. Connection Pooling

```python
import queue

class PooledSQLiteStorage(SQLiteStorage):
    def __init__(self, db_path: str, pool_size: int = 5):
        super().__init__(db_path)
        self.pool = queue.Queue(maxsize=pool_size)
        
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)
    
    @contextmanager
    def _get_connection(self):
        conn = self.pool.get()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.put(conn)
```

---

### 3. Indexing Strategy

```python
def _create_indexes(self):
    """Create indexes for common query patterns."""
    with self._get_connection() as conn:
        # Index for timestamp-based queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_decisions_timestamp
            ON governance_decisions(created_at)
        """)
        
        # Index for category filtering
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_category
            ON memory_records(json_extract(data, '$.category'))
        """)
        
        # Composite index for complex queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_status_time
            ON execution_history(status, created_at)
        """)
```

---

## Testing Strategies

### Unit Tests

```python
import unittest
import tempfile
from pathlib import Path

class TestSQLiteStorage(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.storage = SQLiteStorage(self.temp_db.name)
        self.storage.initialize()
    
    def tearDown(self):
        self.storage.close()
        Path(self.temp_db.name).unlink()
    
    def test_store_and_retrieve(self):
        data = {"value": 42, "name": "test"}
        self.storage.store("governance_state", "test_key", data)
        
        retrieved = self.storage.retrieve("governance_state", "test_key")
        self.assertEqual(retrieved, data)
    
    def test_update_existing(self):
        self.storage.store("governance_state", "key1", {"version": 1})
        self.storage.store("governance_state", "key1", {"version": 2})
        
        result = self.storage.retrieve("governance_state", "key1")
        self.assertEqual(result["version"], 2)
    
    def test_delete(self):
        self.storage.store("governance_state", "key1", {"data": "test"})
        self.assertTrue(self.storage.delete("governance_state", "key1"))
        self.assertIsNone(self.storage.retrieve("governance_state", "key1"))
```

---

## Related Documentation

- **Data Persistence Layer**: `source-docs/utilities/005-data-persistence.md`
- **Governance System**: `source-docs/core/governance.md`
- **Memory System**: `source-docs/core/memory-engine.md`
- **SQLite Documentation**: https://www.sqlite.org/docs.html

---

## Version History

- **v2.0** (Current): Added SQLiteStorage as primary engine
- **v1.5**: Schema evolution support
- **v1.0**: Initial JSONStorage implementation

---

**Last Updated**: 2025-01-24  
**Status**: Stable - SQLiteStorage recommended for production  
**Maintainer**: Core Infrastructure Team
