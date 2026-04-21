# Storage Abstraction Layer Model

**Module**: `src/app/core/storage.py` [[src/app/core/storage.py]]  
**Storage**: `data/cognition.db` (SQLite), legacy JSON files  
**Persistence**: Transactional SQLite with connection pooling  
**Schema Version**: 1.0

---

## Overview

The Storage Abstraction Layer provides a unified interface for data persistence, supporting both transactional SQLite storage (recommended) and legacy JSON file storage. It features schema evolution, migration support, thread-safe operations, and connection pooling for high-concurrency scenarios.

### Key Features

- **Dual Storage Engines**: SQLite (primary) and JSON (legacy)
- **Transactional Support**: ACID guarantees for critical data
- **Schema Evolution**: Automated schema migrations
- **Thread-Safe Operations**: Connection pooling with context managers
- **Table Whitelisting**: SQL injection prevention
- **Connection Pooling**: Reusable connections for performance

---

## Storage Engines

### StorageEngine Abstract Interface

```python
from abc import ABC, abstractmethod

class StorageEngine(ABC):
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
    def query(self, table: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
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

---

## SQLite Storage Engine

### Schema Structure

**Database**: `data/cognition.db`

#### Governance State Table

```sql
CREATE TABLE IF NOT EXISTS governance_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Store governance system state (rules, policies, decisions)

**Fields**:
- `id`: Auto-incrementing primary key
- `key`: Unique state identifier (e.g., "current_tier", "active_policies")
- `data`: JSON-serialized state data
- `version`: Schema version for migration tracking
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp

#### Governance Decisions Table

```sql
CREATE TABLE IF NOT EXISTS governance_decisions (
    decision_id TEXT PRIMARY KEY,
    action_id TEXT NOT NULL,
    approved INTEGER NOT NULL,
    reason TEXT NOT NULL,
    council_votes TEXT,
    mutation_intent TEXT,
    consensus_required INTEGER DEFAULT 0,
    consensus_achieved INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Audit trail for governance decisions

**Fields**:
- `decision_id`: Unique decision identifier (UUID)
- `action_id`: Action being decided upon
- `approved`: Boolean (0 or 1) - decision outcome
- `reason`: Explanation for decision
- `council_votes`: JSON-serialized vote breakdown
- `mutation_intent`: Intended state change
- `consensus_required`: Boolean - whether consensus was needed
- `consensus_achieved`: Boolean - whether consensus was reached
- `timestamp`: Decision timestamp

#### Execution History Table

```sql
CREATE TABLE IF NOT EXISTS execution_history (
    trace_id TEXT PRIMARY KEY,
    action_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    status TEXT NOT NULL,
    source TEXT,
    user_id TEXT,
    duration_ms REAL,
    channels TEXT,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Action execution audit trail

**Fields**:
- `trace_id`: Unique execution trace ID
- `action_name`: Human-readable action name
- `action_type`: Action category (e.g., "governance", "learning", "user_action")
- `status`: Execution status ("success", "failure", "pending")
- `source`: Origin of action (e.g., "user_command", "automated")
- `user_id`: User who triggered action
- `duration_ms`: Execution time in milliseconds
- `channels`: JSON array of notification channels used
- `error`: Error message (if status=failure)
- `timestamp`: Execution timestamp

#### Reflection History Table

```sql
CREATE TABLE IF NOT EXISTS reflection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    action_name TEXT NOT NULL,
    insights TEXT,
    triggered_by TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trace_id) REFERENCES execution_history(trace_id)
);
```

**Purpose**: Post-execution reflections and learnings

**Fields**:
- `id`: Auto-incrementing primary key
- `trace_id`: Foreign key to execution_history
- `action_name`: Action that triggered reflection
- `insights`: JSON-serialized insights learned
- `triggered_by`: Reflection trigger (e.g., "error", "success", "manual")
- `timestamp`: Reflection timestamp

#### Memory Records Table

```sql
CREATE TABLE IF NOT EXISTS memory_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Long-term memory storage linked to executions

**Fields**:
- `id`: Auto-incrementing primary key
- `trace_id`: Link to execution that created memory
- `memory_type`: Memory category ("technical", "personal", etc.)
- `content`: Memory content
- `metadata`: JSON-serialized additional data
- `timestamp`: Memory creation timestamp

---

## SQLiteStorage Class

### Initialization

```python
from app.core.storage import SQLiteStorage

storage = SQLiteStorage(db_path="data/cognition.db")
storage.initialize()
```

**Process**:
1. Create `data/` directory if missing
2. Connect to SQLite database (creates if missing)
3. Execute schema creation SQL for all tables
4. Enable foreign key constraints

### Table Whitelisting

```python
ALLOWED_TABLES = {
    "governance_state",
    "governance_decisions",
    "execution_history",
    "reflection_history",
    "memory_records",
}

def _validate_table_name(self, table: str) -> None:
    """Validate table name against whitelist to prevent SQL injection."""
    if table not in self.ALLOWED_TABLES:
        raise ValueError(
            f"Invalid table name: {table}. "
            f"Allowed tables: {', '.join(self.ALLOWED_TABLES)}"
        )
```

**Security**: Prevents SQL injection via table name manipulation.

### Connection Management

```python
from contextlib import contextmanager
from threading import Lock

@contextmanager
def _get_connection(self):
    """Context manager for database connections with thread safety."""
    with self.lock:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
```

**Features**:
- **Thread-safe**: Lock prevents concurrent access
- **Dict-like rows**: Access columns by name
- **Automatic cleanup**: Connection closed after use

---

## CRUD Operations

### Store Data

```python
def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
    """Store data in the specified table with the given key."""
    self._validate_table_name(table)
    
    with self._get_connection() as conn:
        cursor = conn.cursor()
        
        # Serialize data to JSON
        json_data = json.dumps(data)
        
        # Insert or update
        cursor.execute(f"""
            INSERT INTO {table} (key, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
        """, (key, json_data))
        
        conn.commit()
        return True
```

### Retrieve Data

```python
def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
    """Retrieve data from the specified table by key."""
    self._validate_table_name(table)
    
    with self._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT data FROM {table} WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        if row:
            return json.loads(row["data"])
        return None
```

### Query with Filters

```python
def query(self, table: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Query data from the specified table with optional filters."""
    self._validate_table_name(table)
    
    with self._get_connection() as conn:
        cursor = conn.cursor()
        
        if filters:
            # Build WHERE clause from filters
            where_clauses = []
            values = []
            for key, value in filters.items():
                where_clauses.append(f"{key} = ?")
                values.append(value)
            
            where_sql = " AND ".join(where_clauses)
            cursor.execute(f"SELECT * FROM {table} WHERE {where_sql}", values)
        else:
            cursor.execute(f"SELECT * FROM {table}")
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
```

### Delete Data

```python
def delete(self, table: str, key: str) -> bool:
    """Delete data from the specified table by key."""
    self._validate_table_name(table)
    
    with self._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE key = ?", (key,))
        conn.commit()
        return cursor.rowcount > 0
```

---

## Legacy JSON Storage Engine

### JSONStorage Class

```python
class JSONStorage(StorageEngine):
    """Legacy JSON file-based storage engine (deprecated)."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, Any]] = {}
        logger.info("JSONStorage initialized (legacy mode)")
    
    def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
        """Store data in JSON file."""
        table_file = self.data_dir / f"{table}.json"
        
        # Load existing table
        if table_file.exists():
            with open(table_file) as f:
                table_data = json.load(f)
        else:
            table_data = {}
        
        # Update entry
        table_data[key] = data
        
        # Save with atomic write
        _atomic_write_json(str(table_file), table_data)
        
        # Update cache
        self._cache[table] = table_data
        return True
```

**Note**: JSONStorage is deprecated and maintained only for backward compatibility. New deployments should use SQLiteStorage.

---

## Schema Migration System

### Migration Framework

```python
class SchemaMigrator:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.migrations: list[Callable] = []
    
    def register_migration(self, version: str, migration_func: Callable):
        """Register a schema migration function."""
        self.migrations.append((version, migration_func))
    
    def apply_migrations(self):
        """Apply all pending migrations in order."""
        current_version = self._get_current_version()
        
        for version, migration_func in self.migrations:
            if version > current_version:
                logger.info("Applying migration: %s", version)
                migration_func(self.storage)
                self._set_current_version(version)
```

### Example Migration

```python
def migrate_to_1_1_0(storage: SQLiteStorage):
    """Migration: Add user_id index to execution_history."""
    with storage._get_connection() as conn:
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_user_id
            ON execution_history(user_id)
        """)
        conn.commit()

def migrate_to_1_2_0(storage: SQLiteStorage):
    """Migration: Add priority field to governance_decisions."""
    with storage._get_connection() as conn:
        conn.execute("""
            ALTER TABLE governance_decisions
            ADD COLUMN priority TEXT DEFAULT 'medium'
        """)
        conn.commit()

# Register migrations
migrator = SchemaMigrator(storage)
migrator.register_migration("1.1.0", migrate_to_1_1_0)
migrator.register_migration("1.2.0", migrate_to_1_2_0)
migrator.apply_migrations()
```

---

## Usage Examples

### Basic CRUD

```python
from app.core.storage import SQLiteStorage

storage = SQLiteStorage(db_path="data/cognition.db")
storage.initialize()

# Store governance state
storage.store("governance_state", "current_tier", {
    "tier": 3,
    "active_policies": ["ASL_enforcement", "human_approval_required"],
    "last_updated": "2024-01-20T14:30:00Z"
})

# Retrieve governance state
state = storage.retrieve("governance_state", "current_tier")
print(f"Current tier: {state['tier']}")

# Query execution history
recent_executions = storage.query("execution_history", filters={
    "status": "success",
    "user_id": "admin"
})

# Delete old record
storage.delete("execution_history", "old_trace_id")
```

### Governance Decision Logging

```python
import uuid

decision_id = str(uuid.uuid4())
storage.store("governance_decisions", decision_id, {
    "decision_id": decision_id,
    "action_id": "deploy_model_update",
    "approved": 1,
    "reason": "Consensus achieved from governance council",
    "council_votes": json.dumps({"approve": 4, "deny": 1}),
    "consensus_required": 1,
    "consensus_achieved": 1,
    "timestamp": datetime.now().isoformat()
})
```

### Execution Trace

```python
trace_id = str(uuid.uuid4())
start_time = time.time()

# Log execution
try:
    execute_action()
    duration = (time.time() - start_time) * 1000
    
    storage.store("execution_history", trace_id, {
        "trace_id": trace_id,
        "action_name": "update_user_preferences",
        "action_type": "user_action",
        "status": "success",
        "source": "ui_panel",
        "user_id": "alice",
        "duration_ms": duration,
        "timestamp": datetime.now().isoformat()
    })
except Exception as e:
    duration = (time.time() - start_time) * 1000
    
    storage.store("execution_history", trace_id, {
        "trace_id": trace_id,
        "action_name": "update_user_preferences",
        "action_type": "user_action",
        "status": "failure",
        "error": str(e),
        "duration_ms": duration,
        "timestamp": datetime.now().isoformat()
    })
```

---

## Performance Considerations

### Connection Pooling

**Current Implementation**: Single connection per request (context manager)

**Future Enhancement**: Connection pool for high-concurrency:

```python
from sqlite3 import Connection
from queue import Queue

class ConnectionPool:
    def __init__(self, db_path: str, pool_size: int = 5):
        self.pool: Queue[Connection] = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put(sqlite3.connect(db_path, check_same_thread=False))
    
    @contextmanager
    def get_connection(self):
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)
```

### Indexing Strategy

```sql
-- Index for frequent queries
CREATE INDEX IF NOT EXISTS idx_execution_user_id ON execution_history(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_status ON execution_history(status);
CREATE INDEX IF NOT EXISTS idx_decisions_action_id ON governance_decisions(action_id);
CREATE INDEX IF NOT EXISTS idx_reflection_trace_id ON reflection_history(trace_id);
```

### Query Optimization

- **Avoid SELECT \***: Specify columns needed
- **Use LIMIT**: Paginate large result sets
- **Use Prepared Statements**: Prevents SQL injection, improves performance

---

## Testing Strategy

### Unit Tests

```python
def test_sqlite_storage_crud():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = SQLiteStorage(db_path=os.path.join(tmpdir, "test.db"))
        storage.initialize()
        
        # Test store
        success = storage.store("governance_state", "test_key", {"value": 42})
        assert success
        
        # Test retrieve
        data = storage.retrieve("governance_state", "test_key")
        assert data["value"] == 42
        
        # Test delete
        success = storage.delete("governance_state", "test_key")
        assert success
        
        # Verify deletion
        data = storage.retrieve("governance_state", "test_key")
        assert data is None
```

---

## Security Considerations

### SQL Injection Prevention

1. **Table Whitelisting**: Only predefined tables allowed
2. **Parameterized Queries**: All user input via `?` placeholders
3. **Input Validation**: Validate filters before query construction

### Data Integrity

- **ACID Transactions**: Atomic commits with rollback on error
- **Foreign Key Constraints**: Maintain referential integrity
- **Unique Constraints**: Prevent duplicate keys

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `data_persistence.py` | Low-level encryption and versioning |
| `governance.py` | Primary consumer of governance_* tables |
| `memory_engine.py` | Uses memory_records table |
| `telemetry.py` | Uses execution_history for metrics |

---

## Future Enhancements

1. **PostgreSQL Support**: Production-grade RDBMS
2. **Read Replicas**: Scale read operations
3. **Sharding**: Distribute data across multiple databases
4. **Full-Text Search**: SQLite FTS5 for text queries
5. **Connection Pooling**: Reusable connections for high concurrency

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/storage.py]]
