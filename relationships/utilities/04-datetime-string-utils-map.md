---
description: Date/Time and String utility functions across Project-AI
audience: developers
priority: P2
category: utilities
tags: [datetime, string-utils, formatting, parsing]
dependencies: [helper-functions]
related_systems: [format-utils, parse-utils]
last_updated: 2026-04-20
---

# Date/Time & String Utils Relationship Map

## Date/Time Utilities

### 1. **Timestamp Functions** (utils/helpers.py)

#### Core Functions:
```python
def get_timestamp() -> float:
    """Get current Unix timestamp."""
    return time.time()

def format_timestamp(timestamp: float) -> str:
    """Format Unix timestamp to ISO 8601 string."""
    return datetime.fromtimestamp(timestamp).isoformat()
```

**Usage Pattern**:
```python
from utils.helpers import get_timestamp, format_timestamp

# Current timestamp
now = get_timestamp()  # 1713600000.123

# Format for display/storage
formatted = format_timestamp(now)  # "2024-04-20T12:00:00"
```

**Consumers**: 40+ modules (audit, monitoring, logging)

---

### 2. **ISO Timestamp Functions** (e2e/utils/test_helpers.py)

#### Extended Functions:
```python
def get_timestamp_iso() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()

def parse_iso_timestamp(timestamp_str: str) -> float:
    """Parse ISO timestamp string to epoch seconds."""
    from datetime import datetime
    dt = datetime.fromisoformat(timestamp_str)
    return dt.timestamp()
```

**Bidirectional Conversion**:
```python
# String → Timestamp
iso_str = "2024-04-20T12:00:00"
epoch = parse_iso_timestamp(iso_str)  # 1713600000.0

# Timestamp → String
timestamp = 1713600000.0
iso_str = format_timestamp(timestamp)  # "2024-04-20T12:00:00"
```

**Reuse Chain**:
```
utils/helpers.py::format_timestamp()
    ↓ adopted pattern
e2e/utils/test_helpers.py::get_timestamp_iso()
    ↓ used by
src/app/audit/trace_logger.py → Event timestamps
    ↓
src/app/monitoring/metrics_collector.py → Metric timestamps
```

---

### 3. **Time Measurement** (e2e/utils/test_helpers.py)

#### Decorator Pattern:
```python
def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {execution_time}s")
        return result
    return wrapper
```

**Usage**:
```python
@measure_execution_time
def expensive_operation():
    # Long-running code
    pass

# Logs: "expensive_operation executed in 2.345s"
```

**Adoption**: Test suites use this for performance tracking

---

## String Utilities

### 1. **String Sanitization** (utils/validators.py)

#### Core Function:
```python
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.
    
    Operations:
    1. Type check (must be str)
    2. Truncate to max_length
    3. Remove null bytes (\x00)
    4. Strip whitespace
    """
    if not isinstance(value, str):
        raise ValidationError(f"Expected string, got {type(value)}")
    
    # Truncate
    value = value[:max_length]
    
    # Remove null bytes (security)
    value = value.replace("\x00", "")
    
    # Strip whitespace
    value = value.strip()
    
    return value
```

**Security Rationale**:
- Null byte removal: Prevents null byte injection attacks
- Max length: Prevents DoS via large strings
- Strip whitespace: Normalizes input

**Consumers**: 20+ modules requiring user input sanitization

---

### 2. **Dashboard String Utils** (src/app/gui/dashboard_utils.py)

#### Validation Functions:
```python
@staticmethod
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """GUI-specific sanitization with HTML escape."""
    if not value:
        return ""
    
    # Truncate
    value = value[:max_length]
    
    # Remove dangerous characters
    value = value.replace("\x00", "")
    value = value.replace("\n", " ")  # GUI: single line
    value = value.replace("\r", "")
    
    return value.strip()
```

**GUI-Specific**: Removes newlines for single-line text fields

---

### 3. **Hash Truncation** (utils/helpers.py)

#### Function:
```python
def truncate_hash(hash_str: str, length: int = 8) -> str:
    """
    Truncate hash to specified length with ellipsis.
    
    Args:
        hash_str: Full hash string (e.g., SHA-256 64 chars)
        length: Number of characters to keep
    
    Returns:
        Truncated hash with "..." suffix
    
    Example:
        truncate_hash("abc123def456...", 8) → "abc123de..."
    """
    return f"{hash_str[:length]}..." if len(hash_str) > length else hash_str
```

**Usage Context**: Display shortened hashes in GUI/logs

---

### 4. **Safe Dictionary Access** (utils/helpers.py)

#### Function:
```python
def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary.
    
    Equivalent to dict.get() but with explicit typing.
    """
    return data.get(key, default)
```

**Why Exists**: Explicit typing for better IDE autocomplete and type checking

**Adoption**: Used in `src/app/core/ai_systems.py` for state access

---

## Utility Dependency Map

```
┌─────────────────────────────────────────────────────────────┐
│ Date/Time & String Utilities                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Date/Time Functions                                        │
│    ├── get_timestamp() ─────────────→ 40+ modules          │
│    ├── format_timestamp() ───────────→ audit/monitoring    │
│    ├── get_timestamp_iso() ──────────→ tests/e2e           │
│    ├── parse_iso_timestamp() ────────→ data parsing        │
│    └── measure_execution_time() ─────→ performance tests   │
│                                                              │
│  String Functions                                           │
│    ├── sanitize_string() ────────────→ 20+ modules         │
│    ├── truncate_hash() ──────────────→ GUI/logging         │
│    └── safe_get() ───────────────────→ config/state access │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

### Pattern 1: **Timestamp for Audit Logs**
```python
from utils.helpers import get_timestamp, format_timestamp

log_entry = {
    "timestamp": format_timestamp(get_timestamp()),
    "event": "user_login",
    "user": "alice"
}
# Result: {"timestamp": "2024-04-20T12:00:00", "event": "user_login", ...}
```

### Pattern 2: **Sanitize + Validate**
```python
from utils.validators import sanitize_string, validate_target

# User input
raw_path = user_input()

# Sanitize first
safe_path = sanitize_string(raw_path, max_length=500)

# Then validate
validate_target(safe_path)  # Raises ValidationError if invalid
```

### Pattern 3: **Display Hash**
```python
from utils.helpers import hash_data, truncate_hash

# Generate hash
data_hash = hash_data({"key": "value"})  # 64-char SHA-256

# Display shortened version
display_hash = truncate_hash(data_hash, 12)  # "abc123def456..."
```

---

## Usage Statistics

| Utility Function          | Consumer Count | Primary Use Case     |
|---------------------------|----------------|----------------------|
| get_timestamp()           | 40+            | Event timestamping   |
| format_timestamp()        | 30+            | ISO 8601 formatting  |
| sanitize_string()         | 20+            | Input sanitization   |
| truncate_hash()           | 10+            | Display formatting   |
| safe_get()                | 15+            | Config access        |
| measure_execution_time()  | 25+ (tests)    | Performance tracking |

---

## Best Practices

### BP1: **Always Use ISO 8601 for Storage**
```python
# ✅ CORRECT
timestamp = format_timestamp(get_timestamp())
# Stores: "2024-04-20T12:00:00"

# ❌ WRONG
timestamp = str(time.time())
# Stores: "1713600000.123" (ambiguous format)
```

### BP2: **Sanitize Before Validation**
```python
# ✅ CORRECT
safe_input = sanitize_string(user_input)
validate_action(safe_input)

# ❌ WRONG
validate_action(user_input)  # May contain \x00, excess whitespace
```

### BP3: **Use Truncation for Display Only**
```python
# ✅ CORRECT
full_hash = hash_data(data)
save_to_db(full_hash)  # Store full hash
display(truncate_hash(full_hash))  # Show shortened

# ❌ WRONG
truncated = truncate_hash(hash_data(data))
save_to_db(truncated)  # Lost data!
```

---

## Related Documentation
- [Helper Functions Map](./01-helper-functions-map.md)
- [Format Utils Map](./10-format-utils-map.md)
- [Parse Utils Map](./11-parse-utils-map.md)
- [Validation Utils Map](./09-validation-utils-map.md)
