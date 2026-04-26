# Storage Abstraction Layer

**Module:** `src/app/core/storage.py`  
**Type:** Core Infrastructure  
**Dependencies:** sqlite3, json  
**Related Modules:** data_persistence.py, governance.py

---

## Overview

The Storage Abstraction Layer provides a unified interface for transactional SQLite storage and legacy JSON file storage, supporting governance state, execution history, memory records, and reflection history with schema evolution and thread-safe operations.

### Core Features

- **SQLite Transactional Storage**: Primary storage engine with ACID properties
- **JSON Storage**: Legacy compatibility mode (deprecated)
- **Schema Evolution**: Automatic migration and versioning
- **Thread-Safe Operations**: Connection pooling with mutex locking
- **Whitelisted Tables**: SQL injection prevention
- **Indexed Queries**: Optimized timestamp-based queries

---

## Architecture

```
StorageEngine (Abstract Base)
├── SQLiteStorage (Primary)
│   ├── Transactional Operations (ACID)
│   ├── Schema Management (CREATE TABLE, migrations)
│   ├── Connection Pooling (thread-safe)
│   └── Indexed Queries (timestamp, trace_id)
└── JSONStorage (Legacy)
    ├── File-Based Storage
    └── Backward Compatibility
```

### Table Schema

```sql
-- Governance state (configuration snapshots)
CREATE TABLE governance_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    data TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Governance decisions (approval workflow)
CREATE TABLE governance_decisions (
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

-- Execution history (action traces)
CREATE TABLE execution_history (
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

-- Reflection history (post-action analysis)
CREATE TABLE reflection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    action_name TEXT NOT NULL,
    insights TEXT,
    triggered_by TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trace_id) REFERENCES execution_history(trace_id)
);

-- Memory records (knowledge capture)
CREATE TABLE memory_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trace_id) REFERENCES execution_history(trace_id)
);
```

---

## Core Classes

### SQLiteStorage (Recommended)

```python
from app.core.storage import SQLiteStorage

# Initialize SQLite storage
storage = SQLiteStorage(db_path="data/cognition.db")
storage.initialize()  # Create tables and indices

# Store governance state
storage.store("governance_state", "main_config", {
    "governance_enabled": True,
    "reflection_enabled": True,
    "memory_enabled": True
})

# Store governance decision
storage.store("governance_decisions", "decision_001", {
    "action_id": "modify_personality",
    "approved": True,
    "reason": "User requested trait adjustment",
    "council_votes": {"safety": True, "ethics": True},
    "timestamp": "2026-04-20T14:00:00Z"
})

# Store execution history
storage.store("execution_history", "trace_abc123", {
    "action_name": "generate_image",
    "action_type": "creative",
    "status": "success",
    "source": "user_request",
    "user_id": "admin",
    "duration_ms": 2500.0,
    "channels": {"input": "prompt", "output": "image_path"}
})

# Retrieve data
config = storage.retrieve("governance_state", "main_config")
# Returns: {"governance_enabled": True, ...}

# Query with filters
recent_actions = storage.query("execution_history", filters={
    "status": "success",
    "user_id": "admin"
})

# Delete data
storage.delete("governance_state", "old_config")

# Close connection
storage.close()
```

### Table Name Validation (SQL Injection Prevention)

```python
ALLOWED_TABLES = {
    "governance_state",
    "governance_decisions",
    "execution_history",
    "reflection_history",
    "memory_records"
}

def _validate_table_name(self, table: str) -> None:
    """Validate table name against whitelist."""
    if table not in self.ALLOWED_TABLES:
        raise ValueError(
            f"Invalid table name: {table}. "
            f"Allowed tables: {', '.join(self.ALLOWED_TABLES)}"
        )

# Usage
storage.store("governance_state", "key", data)  # ✅ Valid
storage.store("DROP TABLE users", "key", data)  # ❌ ValueError
```

---

## Store Operations

### Governance State

```python
# Store configuration snapshot
storage.store("governance_state", "runtime_config", {
    "governance_enabled": True,
    "four_laws_enforced": True,
    "reflection_depth": 3,
    "memory_retention_days": 90
})

# Upsert behavior (INSERT or UPDATE)
# If key exists: UPDATE data and updated_at
# If key doesn't exist: INSERT new record
```

### Governance Decisions

```python
# Store approval decision
storage.store("governance_decisions", "decision_xyz", {
    "action_id": "execute_system_command",
    "approved": False,
    "reason": "Violates Four Laws constraint (user safety)",
    "council_votes": {
        "safety_agent": False,
        "ethics_agent": False,
        "technical_agent": True
    },
    "mutation_intent": "run_shell_command",
    "consensus_required": True,
    "consensus_achieved": False,
    "timestamp": "2026-04-20T14:30:00Z"
})
```

### Execution History

```python
# Store action trace
storage.store("execution_history", "trace_def456", {
    "action_name": "data_analysis",
    "action_type": "analytical",
    "status": "failed",
    "source": "automated_trigger",
    "user_id": None,
    "duration_ms": 150.5,
    "channels": {
        "input": "dataset.csv",
        "output": None
    },
    "error": "FileNotFoundError: dataset.csv not found",
    "timestamp": "2026-04-20T15:00:00Z"
})
```

---

## Query Operations

### Simple Retrieve

```python
# Retrieve by primary key
config = storage.retrieve("governance_state", "runtime_config")
if config:
    print(f"Governance enabled: {config['governance_enabled']}")
else:
    print("Config not found")
```

### Filtered Queries

```python
# Query governance decisions by approval status
approved_decisions = storage.query("governance_decisions", filters={
    "approved": 1  # SQLite uses 1/0 for boolean
})

# Query execution history by user and status
user_actions = storage.query("execution_history", filters={
    "user_id": "admin",
    "status": "success"
})

# Query reflection history by trace_id
reflections = storage.query("reflection_history", filters={
    "trace_id": "trace_abc123"
})
```

### Advanced Queries (Raw SQL)

```python
# For complex queries, use raw SQL (be careful with SQL injection)
with storage._get_connection() as conn:
    cursor = conn.cursor()
    
    # Get actions in last 24 hours
    cursor.execute("""
        SELECT * FROM execution_history
        WHERE timestamp >= datetime('now', '-1 day')
        ORDER BY timestamp DESC
    """)
    
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
```

---

## Thread Safety

### Connection Management

```python
class SQLiteStorage:
    def __init__(self, db_path: str = "data/cognition.db"):
        self.db_path = db_path
        self.lock = Lock()  # Thread-safe mutex
        self._conn: sqlite3.Connection | None = None
    
    @contextmanager
    def _get_connection(self):
        """Thread-safe connection context manager."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()
```

**Usage in Multi-Threaded Environment:**
```python
import threading

def worker_thread(storage, thread_id):
    """Example worker thread using storage."""
    for i in range(10):
        storage.store("execution_history", f"trace_{thread_id}_{i}", {
            "action_name": f"worker_{thread_id}",
            "action_type": "background",
            "status": "success"
        })

# Safe: Each thread uses same storage instance
storage = SQLiteStorage()
storage.initialize()

threads = [
    threading.Thread(target=worker_thread, args=(storage, i))
    for i in range(5)
]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

---

## Integration Examples

### With Governance System

```python
from app.core.storage import SQLiteStorage
from app.core.governance import GovernanceEngine

# Initialize storage and governance
storage = SQLiteStorage()
storage.initialize()

governance = GovernanceEngine(storage=storage)

# Governance workflow
decision = governance.evaluate_action(
    action="modify_ai_personality",
    context={"user": "admin", "trait": "friendliness", "value": 0.9}
)

# Store decision
storage.store("governance_decisions", decision.decision_id, {
    "action_id": decision.action_id,
    "approved": decision.approved,
    "reason": decision.reason,
    "council_votes": decision.council_votes,
    "timestamp": decision.timestamp
})
```

### With Execution Tracing

```python
import time
from app.core.storage import SQLiteStorage

def traced_function(storage, action_name, user_id):
    """Execute function with automatic trace logging."""
    trace_id = f"trace_{time.time()}"
    start_time = time.time()
    
    try:
        # Execute action
        result = perform_action(action_name)
        status = "success"
        error = None
    except Exception as e:
        result = None
        status = "failed"
        error = str(e)
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Store execution trace
    storage.store("execution_history", trace_id, {
        "action_name": action_name,
        "action_type": "user_action",
        "status": status,
        "source": "api_call",
        "user_id": user_id,
        "duration_ms": duration_ms,
        "error": error,
        "timestamp": datetime.now().isoformat()
    })
    
    return trace_id, result
```

### Analytics Queries

```python
def generate_usage_report(storage, start_date, end_date):
    """Generate usage analytics from execution history."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        
        # Total actions
        cursor.execute("""
            SELECT COUNT(*) as total_actions
            FROM execution_history
            WHERE timestamp BETWEEN ? AND ?
        """, (start_date, end_date))
        total_actions = cursor.fetchone()["total_actions"]
        
        # Success rate
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM execution_history
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Average duration
        cursor.execute("""
            SELECT AVG(duration_ms) as avg_duration
            FROM execution_history
            WHERE timestamp BETWEEN ? AND ?
            AND status = 'success'
        """, (start_date, end_date))
        avg_duration = cursor.fetchone()["avg_duration"]
        
        return {
            "total_actions": total_actions,
            "success_count": status_counts.get("success", 0),
            "failed_count": status_counts.get("failed", 0),
            "success_rate": status_counts.get("success", 0) / total_actions if total_actions else 0,
            "avg_duration_ms": avg_duration
        }

# Usage
report = generate_usage_report(storage, "2026-04-01", "2026-04-30")
print(f"Actions: {report['total_actions']}, Success Rate: {report['success_rate']:.1%}")
```

---

## Schema Evolution

### Adding New Table

```python
def add_audit_log_table(storage):
    """Add new audit_log table to existing database."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='audit_log'
        """)
        
        if not cursor.fetchone():
            # Create new table
            cursor.execute("""
                CREATE TABLE audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add index
            cursor.execute("""
                CREATE INDEX idx_audit_timestamp
                ON audit_log(timestamp)
            """)
            
            conn.commit()
            print("audit_log table created")
```

### Modifying Existing Schema

```python
def add_priority_column(storage):
    """Add 'priority' column to execution_history table."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(execution_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "priority" not in columns:
            # Add column (SQLite allows adding columns)
            cursor.execute("""
                ALTER TABLE execution_history
                ADD COLUMN priority TEXT DEFAULT 'normal'
            """)
            conn.commit()
            print("Added 'priority' column to execution_history")
```

---

## Performance Optimization

### Index Usage

```python
# Indices are automatically created during initialization
# idx_execution_timestamp: execution_history(timestamp)
# idx_governance_timestamp: governance_decisions(timestamp)

# Query optimization
# ✅ Fast (uses index)
storage.query("execution_history", filters={"timestamp": "> 2026-04-01"})

# ❌ Slow (no index on user_id)
storage.query("execution_history", filters={"user_id": "admin"})

# Solution: Add index for frequently queried columns
with storage._get_connection() as conn:
    conn.execute("CREATE INDEX idx_execution_user ON execution_history(user_id)")
```

### Batch Operations

```python
def batch_store(storage, table, records):
    """Store multiple records in a single transaction."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        
        for key, data in records.items():
            data_json = json.dumps(data)
            cursor.execute(f"""
                INSERT OR REPLACE INTO {table} (key, data)
                VALUES (?, ?)
            """, (key, data_json))
        
        conn.commit()

# Usage
records = {
    "config1": {"setting": "value1"},
    "config2": {"setting": "value2"},
    "config3": {"setting": "value3"}
}
batch_store(storage, "governance_state", records)
```

---

## Error Handling

```python
from app.core.storage import SQLiteStorage
import sqlite3

storage = SQLiteStorage()

try:
    storage.initialize()
except sqlite3.OperationalError as e:
    print(f"Database initialization failed: {e}")

try:
    storage.store("governance_state", "key", {"data": "value"})
except sqlite3.IntegrityError as e:
    print(f"Constraint violation: {e}")

try:
    storage.store("invalid_table", "key", {"data": "value"})
except ValueError as e:
    print(f"Invalid table name: {e}")
```

---

## Testing

```python
import unittest
import tempfile
from app.core.storage import SQLiteStorage

class TestSQLiteStorage(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.storage = SQLiteStorage(db_path=self.temp_db.name)
        self.storage.initialize()
    
    def tearDown(self):
        self.storage.close()
        os.remove(self.temp_db.name)
    
    def test_store_retrieve(self):
        """Test basic store and retrieve operations."""
        data = {"key": "value", "number": 42}
        self.storage.store("governance_state", "test_key", data)
        
        retrieved = self.storage.retrieve("governance_state", "test_key")
        self.assertEqual(retrieved, data)
    
    def test_query_filters(self):
        """Test filtered queries."""
        # Store multiple records
        self.storage.store("execution_history", "trace1", {
            "action_name": "action1",
            "status": "success"
        })
        self.storage.store("execution_history", "trace2", {
            "action_name": "action2",
            "status": "failed"
        })
        
        # Query by status
        results = self.storage.query("execution_history", filters={"status": "success"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["trace_id"], "trace1")
```

---

## Configuration

```bash
# Database file location
export PROJECT_AI_DB_PATH="data/cognition.db"

# SQLite pragma settings (optional)
export SQLITE_JOURNAL_MODE="WAL"  # Write-Ahead Logging (better concurrency)
export SQLITE_CACHE_SIZE=2000     # Cache size in pages (default: 2000)
```

---

## Troubleshooting

### "database is locked"
```python
# Enable WAL mode for better concurrency
with storage._get_connection() as conn:
    conn.execute("PRAGMA journal_mode=WAL")

# Or increase timeout
conn = sqlite3.connect(db_path, timeout=10.0)  # Wait up to 10 seconds
```

### Large Database Files
```python
# Vacuum database to reclaim space
with storage._get_connection() as conn:
    conn.execute("VACUUM")

# Or enable auto_vacuum
conn.execute("PRAGMA auto_vacuum = FULL")
```

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
