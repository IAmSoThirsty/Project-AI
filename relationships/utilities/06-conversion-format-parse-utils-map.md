---
description: Conversion, Format, Parse, Generate, Transform, Filter, and Sort utilities
audience: developers
priority: P2
category: utilities
tags: [conversion, formatting, parsing, generation, transformation, filtering, sorting]
dependencies: [helper-functions, datetime-utils, string-utils]
related_systems: []
last_updated: 2026-04-20
---

# Conversion, Format, Parse & Transform Utils Map

## Overview

This consolidated map documents data transformation utilities across Project-AI, including type conversion, formatting, parsing, generation, transformation, filtering, and sorting operations.

## Conversion Utilities

### 1. **Type Conversion** (Distributed Across Modules)

#### Timestamp Conversions:
```python
# Float → ISO String (utils/helpers.py)
def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).isoformat()

# ISO String → Float (e2e/utils/test_helpers.py)
def parse_iso_timestamp(timestamp_str: str) -> float:
    dt = datetime.fromisoformat(timestamp_str)
    return dt.timestamp()

# Unix → ISO (bidirectional)
unix_time = 1713600000.0
iso_time = format_timestamp(unix_time)  # "2024-04-20T12:00:00"
back_to_unix = parse_iso_timestamp(iso_time)  # 1713600000.0
```

**Usage**: Audit logs, metrics, event timestamps

---

#### JSON ↔ Dict Conversions:
```python
# Dict → JSON String
def dict_to_json(data: dict, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, sort_keys=True)

# JSON String → Dict
def json_to_dict(json_str: str) -> dict:
    return json.loads(json_str)

# Dict → JSON File (e2e/utils/test_helpers.py)
def save_json_file(data: dict, file_path: Path, indent: int = 2):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent)

# JSON File → Dict
def load_json_file(file_path: Path) -> dict:
    with open(file_path) as f:
        return json.load(f)
```

**Pattern**: Used in all persistence modules for state serialization

---

#### Bytes ↔ String Conversions:
```python
# String → Bytes (for encryption)
data_bytes = "sensitive data".encode('utf-8')

# Bytes → String (after decryption)
data_str = encrypted_bytes.decode('utf-8')

# Used in: utils/encryption/, utils/storage/
```

---

### 2. **Neural Network Conversions** (src/app/core/snn_integration.py)

#### PyTorch → SNN:
```python
def convert_from_pytorch(pytorch_model: nn.Module) -> nn.Module:
    """
    Convert standard PyTorch model to Spiking Neural Network.
    
    Conversions:
    - nn.Linear → snn.Linear
    - nn.Conv2d → snn.Conv2d
    - nn.ReLU → snn.LIF (Leaky Integrate-and-Fire)
    """
```

**Use Case**: Neuromorphic computing, edge AI

---

## Format Utilities

### 1. **Timestamp Formatting** (utils/helpers.py)

```python
def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to ISO 8601.
    
    Input: 1713600000.123
    Output: "2024-04-20T12:00:00"
    """
    return datetime.fromtimestamp(timestamp).isoformat()
```

**Standardization**: All timestamps stored as ISO 8601 strings

---

### 2. **Hash Formatting** (utils/helpers.py)

```python
def truncate_hash(hash_str: str, length: int = 8) -> str:
    """
    Format hash for display.
    
    Input: "abc123def456789..."
    Output: "abc123de..."
    """
    return f"{hash_str[:length]}..." if len(hash_str) > length else hash_str
```

**Use Case**: GUI display, log messages

---

### 3. **Health Report Formatting** (src/app/core/tier_health_dashboard.py)

```python
def format_health_report(self, report: PlatformHealthReport) -> str:
    """
    Format health report for display.
    
    Returns:
        Formatted string with health metrics, alerts, recommendations
    """
    # Formats health data into human-readable report
```

**Use Case**: System monitoring dashboards

---

### 4. **Log Formatting** (utils/logger.py)

```python
# Standard log format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
```

**Output**: `2024-04-20 12:00:00 - module_name - INFO - Message`

---

## Parse Utilities

### 1. **ISO Timestamp Parsing** (e2e/utils/test_helpers.py)

```python
def parse_iso_timestamp(timestamp_str: str) -> float:
    """
    Parse ISO timestamp to Unix epoch.
    
    Input: "2024-04-20T12:00:00"
    Output: 1713600000.0
    """
    dt = datetime.fromisoformat(timestamp_str)
    return dt.timestamp()
```

---

### 2. **JSON Parsing** (Distributed)

```python
# Parse JSON file
def load_json_file(file_path: Path) -> dict:
    with open(file_path) as f:
        return json.load(f)

# Parse JSON string
def parse_json_string(json_str: str) -> dict:
    return json.loads(json_str)
```

**Error Handling**: Raises `json.JSONDecodeError` on invalid JSON

---

### 3. **Configuration Parsing** (src/app/core/god_tier_config.py)

```python
def validate_config(self) -> tuple[bool, list[str]]:
    """
    Parse and validate configuration.
    
    Returns:
        (is_valid, error_messages)
    """
    # Parses config dict and validates structure
```

---

## Generate Utilities

### 1. **Hash Generation** (utils/helpers.py)

```python
def hash_data(data: dict[str, Any]) -> str:
    """
    Generate SHA-256 hash of data.
    
    Process:
    1. Serialize to JSON (sorted keys)
    2. Encode to bytes
    3. SHA-256 hash
    4. Return hex digest
    """
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
```

**Deterministic**: Same input always produces same hash

---

### 2. **Timestamp Generation** (utils/helpers.py)

```python
def get_timestamp() -> float:
    """Generate current Unix timestamp."""
    return time.time()

def get_timestamp_iso() -> str:
    """Generate current ISO timestamp."""
    return datetime.now().isoformat()
```

---

### 3. **Key Generation** (utils/encryption/)

```python
# Fernet key
from cryptography.fernet import Fernet
key = Fernet.generate_key()

# Random bytes
import secrets
random_key = secrets.token_bytes(32)  # 256-bit key
```

**Security**: Uses cryptographically secure random number generator

---

## Transform Utilities

### 1. **String Transformation** (utils/validators.py)

```python
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Transform string for safety.
    
    Transformations:
    1. Truncate to max_length
    2. Remove null bytes (\x00)
    3. Strip whitespace
    """
    value = value[:max_length]
    value = value.replace("\x00", "")
    value = value.strip()
    return value
```

---

### 2. **Data Structure Transformation**

#### Dict → JSON (with sorting):
```python
def dict_to_sorted_json(data: dict) -> str:
    """Transform dict to sorted JSON string."""
    return json.dumps(data, sort_keys=True, indent=2)
```

#### Flatten Nested Dict:
```python
def flatten_dict(nested: dict, prefix: str = "") -> dict:
    """
    Transform nested dict to flat dict.
    
    Input: {"a": {"b": 1, "c": 2}}
    Output: {"a.b": 1, "a.c": 2}
    """
    flat = {}
    for key, value in nested.items():
        new_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_dict(value, new_key))
        else:
            flat[new_key] = value
    return flat
```

**Use Case**: Configuration flattening, metric aggregation

---

### 3. **Encryption Transformation** (utils/encryption/)

```python
# Plaintext → Encrypted
plaintext = "secret data"
encrypted = cipher.encrypt(plaintext.encode())

# Encrypted → Plaintext
decrypted = cipher.decrypt(encrypted).decode()
```

---

## Filter Utilities

### 1. **Validation Filters** (utils/validators.py)

```python
def filter_valid_actors(actors: list[str]) -> list[str]:
    """Filter to only valid actors."""
    valid = ["human", "agent", "system"]
    return [a for a in actors if a in valid]

def filter_valid_actions(actions: list[str]) -> list[str]:
    """Filter to only valid actions."""
    valid = ["read", "write", "execute", "mutate"]
    return [a for a in actions if a in valid]
```

---

### 2. **Expired Item Filter** (utils/storage/ephemeral_storage.py)

```python
def cleanup_expired(self):
    """Filter and remove expired items."""
    current_time = time.time()
    expired_keys = [
        key for key, item in self._storage.items()
        if item["ttl"] and current_time - item["created"] > item["ttl"]
    ]
    
    for key in expired_keys:
        self.delete(key)
```

---

### 3. **Null Byte Filter** (utils/validators.py)

```python
def remove_null_bytes(value: str) -> str:
    """Filter out null bytes (security)."""
    return value.replace("\x00", "")
```

**Security**: Prevents null byte injection attacks

---

## Sort Utilities

### 1. **Dictionary Key Sorting** (utils/helpers.py)

```python
def hash_data(data: dict) -> str:
    """Hash with sorted keys for determinism."""
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
```

**Benefit**: Deterministic hashing regardless of dict insertion order

---

### 2. **JSON Sorting** (Standard Pattern)

```python
# Save with sorted keys
def save_sorted_json(data: dict, path: Path):
    with open(path, "w") as f:
        json.dump(data, f, sort_keys=True, indent=2)
```

**Benefit**: Git-friendly diffs (consistent key ordering)

---

### 3. **Timestamp Sorting** (Implicit in Data Structures)

```python
# Audit logs sorted by timestamp
logs = sorted(log_entries, key=lambda x: x["timestamp"])

# Metrics sorted by timestamp
metrics = sorted(metric_list, key=lambda x: x["timestamp"])
```

---

## Utility Dependency Map

```
┌─────────────────────────────────────────────────────────────┐
│ Conversion, Format, Parse & Transform Utilities             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Conversion                                                 │
│    ├── format_timestamp() ──────────→ float → ISO string   │
│    ├── parse_iso_timestamp() ───────→ ISO string → float   │
│    ├── dict_to_json() ──────────────→ dict → JSON string   │
│    ├── load_json_file() ────────────→ JSON file → dict     │
│    └── convert_from_pytorch() ──────→ PyTorch → SNN        │
│                                                              │
│  Format                                                     │
│    ├── format_timestamp() ──────────→ ISO 8601 format      │
│    ├── truncate_hash() ─────────────→ Hash display         │
│    ├── format_health_report() ──────→ Report formatting    │
│    └── log formatter ───────────────→ Log message format   │
│                                                              │
│  Parse                                                      │
│    ├── parse_iso_timestamp() ───────→ ISO → epoch          │
│    ├── json.loads() ────────────────→ JSON → dict          │
│    └── validate_config() ───────────→ Config parsing       │
│                                                              │
│  Generate                                                   │
│    ├── hash_data() ─────────────────→ SHA-256 hash         │
│    ├── get_timestamp() ─────────────→ Unix timestamp       │
│    └── Fernet.generate_key() ───────→ Encryption key       │
│                                                              │
│  Transform                                                  │
│    ├── sanitize_string() ───────────→ Safe string          │
│    ├── dict → sorted JSON ──────────→ Sorted JSON          │
│    ├── flatten_dict() ──────────────→ Flat dict            │
│    └── encrypt/decrypt ─────────────→ Cipher transform     │
│                                                              │
│  Filter                                                     │
│    ├── filter_valid_actors() ───────→ Valid actors only    │
│    ├── cleanup_expired() ───────────→ Remove expired       │
│    └── remove_null_bytes() ─────────→ Security filter      │
│                                                              │
│  Sort                                                       │
│    ├── sort_keys=True ──────────────→ Deterministic hash   │
│    ├── sorted JSON ─────────────────→ Git-friendly         │
│    └── timestamp sorting ───────────→ Chronological order  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Patterns

### Pattern 1: **Bidirectional Conversion**
```python
# Forward conversion
iso_time = format_timestamp(unix_time)

# Reverse conversion
unix_time = parse_iso_timestamp(iso_time)

# Roundtrip test
assert parse_iso_timestamp(format_timestamp(t)) == t
```

---

### Pattern 2: **Transform + Validate**
```python
# Transform first
safe_input = sanitize_string(user_input)

# Then validate
validate_action(safe_input)
```

---

### Pattern 3: **Generate → Store → Retrieve**
```python
# Generate hash
data_hash = hash_data(data)

# Store
save_to_db(data_hash)

# Retrieve and verify
stored_hash = load_from_db()
assert hash_data(data) == stored_hash
```

---

## Usage Statistics

| Utility Category  | Function Count | Consumer Modules | Primary Use Case           |
|-------------------|----------------|------------------|----------------------------|
| Conversion        | 10+            | 40+              | Type/format conversion     |
| Format            | 5+             | 50+              | Display/storage formatting |
| Parse             | 5+             | 30+              | Data deserialization       |
| Generate          | 8+             | 40+              | Hash/key/timestamp gen     |
| Transform         | 10+            | 30+              | Data normalization         |
| Filter            | 5+             | 20+              | Validation/security        |
| Sort              | 3+             | 25+              | Deterministic ordering     |

---

## Best Practices

### BP1: **Always Use ISO 8601 for Timestamps**
```python
# ✅ CORRECT
timestamp = format_timestamp(time.time())  # ISO 8601

# ❌ WRONG
timestamp = str(time.time())  # "1713600000.123" (ambiguous)
```

### BP2: **Sanitize Before Parse/Validate**
```python
# ✅ CORRECT
safe_input = sanitize_string(user_input)
parsed = json.loads(safe_input)

# ❌ WRONG
parsed = json.loads(user_input)  # May contain null bytes
```

### BP3: **Use Sorted Keys for Determinism**
```python
# ✅ CORRECT
hash1 = hash_data({"b": 2, "a": 1})
hash2 = hash_data({"a": 1, "b": 2})
assert hash1 == hash2  # Deterministic

# ❌ WRONG
json.dumps(data)  # Order may vary
```

---

## Related Documentation
- [Helper Functions Map](./01-helper-functions-map.md)
- [Date/Time & String Utils Map](./04-datetime-string-utils-map.md)
- [File, Crypto & Validation Utils Map](./05-file-crypto-validation-utils-map.md)
- [Common Patterns Map](./02-common-patterns-map.md)
