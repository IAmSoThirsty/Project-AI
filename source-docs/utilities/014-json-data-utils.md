# JSON & Data Serialization Utilities

## Overview

Utilities for JSON parsing, serialization, data conversion, and format handling across Project-AI for consistent data interchange.

**Purpose**: Safe JSON handling, data validation, format conversion  
**Dependencies**: json, typing, dataclasses

---

## Core JSON Operations

### 1. Safe JSON Loading

#### load_json_safe()
```python
import json
from typing import Any

def load_json_safe(
    file_path: str,
    default: Any = None
) -> Any:
    """
    Safely load JSON file with fallback.
    
    Args:
        file_path: Path to JSON file
        default: Default value if load fails
    
    Returns:
        Parsed JSON or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        logger.warning(f"Failed to load JSON from {file_path}: {e}")
        return default

# Usage
config = load_json_safe("config.json", default={})
users = load_json_safe("users.json", default=[])
```

---

#### parse_json_safe()
```python
def parse_json_safe(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default

# Usage
data = parse_json_safe('{"key": "value"}', default={})
```

---

### 2. JSON Writing

#### write_json_pretty()
```python
def write_json_pretty(
    data: Any,
    file_path: str,
    indent: int = 2,
    ensure_ascii: bool = False
) -> bool:
    """
    Write JSON with pretty formatting.
    
    Args:
        data: Data to serialize
        file_path: Output file path
        indent: Indentation spaces
        ensure_ascii: Escape non-ASCII characters
    
    Returns:
        True if successful
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                sort_keys=True
            )
        return True
    except Exception as e:
        logger.error(f"Failed to write JSON to {file_path}: {e}")
        return False
```

---

#### atomic_write_json()
```python
import tempfile
import shutil

def atomic_write_json(file_path: str, data: Any) -> None:
    """
    Atomically write JSON file (prevents corruption).
    
    Args:
        file_path: Target file path
        data: Data to write
    """
    # Write to temporary file
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=os.path.dirname(file_path),
        delete=False,
        encoding='utf-8'
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2)
        tmp_path = tmp_file.name
    
    # Atomic rename
    shutil.move(tmp_path, file_path)
```

---

### 3. JSON Validation

#### validate_json_schema()
```python
from jsonschema import validate, ValidationError

def validate_json_schema(
    data: dict,
    schema: dict
) -> tuple[bool, str | None]:
    """
    Validate JSON data against schema.
    
    Args:
        data: JSON data to validate
        schema: JSON schema
    
    Returns:
        (is_valid, error_message)
    
    Requires: jsonschema package
    """
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

# Usage
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

data = {"name": "Alice", "age": 30}
is_valid, error = validate_json_schema(data, schema)

if not is_valid:
    print(f"Validation error: {error}")
```

---

### 4. Data Conversion

#### dict_to_dataclass()
```python
from dataclasses import dataclass, fields
from typing import Type, TypeVar

T = TypeVar('T')

def dict_to_dataclass(cls: Type[T], data: dict) -> T:
    """
    Convert dictionary to dataclass instance.
    
    Args:
        cls: Dataclass type
        data: Dictionary with data
    
    Returns:
        Dataclass instance
    """
    field_names = {f.name for f in fields(cls)}
    filtered_data = {k: v for k, v in data.items() if k in field_names}
    return cls(**filtered_data)

# Usage
@dataclass
class User:
    name: str
    age: int
    email: str = ""

data = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com",
    "extra_field": "ignored"
}

user = dict_to_dataclass(User, data)
```

---

#### dataclass_to_dict()
```python
from dataclasses import asdict

def dataclass_to_dict(obj: Any) -> dict:
    """Convert dataclass to dictionary."""
    return asdict(obj)

# Usage
user = User(name="Alice", age=30)
user_dict = dataclass_to_dict(user)
# {"name": "Alice", "age": 30, "email": ""}
```

---

### 5. JSON Merging

#### merge_json()
```python
def merge_json(base: dict, updates: dict, deep: bool = True) -> dict:
    """
    Merge JSON objects.
    
    Args:
        base: Base dictionary
        updates: Updates to apply
        deep: Deep merge (recursive)
    
    Returns:
        Merged dictionary
    """
    if not deep:
        return {**base, **updates}
    
    result = base.copy()
    
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json(result[key], value, deep=True)
        else:
            result[key] = value
    
    return result

# Usage
base = {
    "config": {
        "timeout": 30,
        "retry": 3
    },
    "features": {
        "logging": True
    }
}

updates = {
    "config": {
        "timeout": 60  # Override
    },
    "features": {
        "metrics": True  # Add
    }
}

merged = merge_json(base, updates)
# {
#   "config": {"timeout": 60, "retry": 3},
#   "features": {"logging": True, "metrics": True}
# }
```

---

### 6. JSON Filtering

#### filter_json_keys()
```python
def filter_json_keys(
    data: dict,
    allowed_keys: set[str],
    recursive: bool = False
) -> dict:
    """
    Filter JSON to only include specified keys.
    
    Args:
        data: Input dictionary
        allowed_keys: Set of allowed keys
        recursive: Apply filtering recursively
    
    Returns:
        Filtered dictionary
    """
    result = {}
    
    for key, value in data.items():
        if key in allowed_keys:
            if recursive and isinstance(value, dict):
                result[key] = filter_json_keys(value, allowed_keys, True)
            else:
                result[key] = value
    
    return result

# Usage
data = {
    "name": "Alice",
    "age": 30,
    "password": "secret",  # Remove
    "email": "alice@example.com"
}

safe_data = filter_json_keys(
    data,
    allowed_keys={"name", "age", "email"}
)
# {"name": "Alice", "age": 30, "email": "alice@example.com"}
```

---

### 7. JSON Path Operations

#### get_nested_value()
```python
def get_nested_value(
    data: dict,
    path: str,
    separator: str = ".",
    default: Any = None
) -> Any:
    """
    Get value from nested JSON using path.
    
    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "user.profile.name")
        separator: Path separator
        default: Default if not found
    
    Returns:
        Value at path or default
    """
    keys = path.split(separator)
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current

# Usage
data = {
    "user": {
        "profile": {
            "name": "Alice",
            "age": 30
        }
    }
}

name = get_nested_value(data, "user.profile.name")  # "Alice"
city = get_nested_value(data, "user.profile.city", default="Unknown")  # "Unknown"
```

---

#### set_nested_value()
```python
def set_nested_value(
    data: dict,
    path: str,
    value: Any,
    separator: str = "."
) -> None:
    """
    Set value in nested JSON using path.
    
    Args:
        data: Dictionary to modify
        path: Dot-separated path
        value: Value to set
        separator: Path separator
    """
    keys = path.split(separator)
    current = data
    
    # Navigate/create path
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set final value
    current[keys[-1]] = value

# Usage
data = {}
set_nested_value(data, "user.profile.name", "Alice")
# data = {"user": {"profile": {"name": "Alice"}}}
```

---

## Advanced Patterns

### 1. JSON Encoder for Custom Types

```python
from datetime import datetime
from decimal import Decimal
from pathlib import Path

class CustomJSONEncoder(json.JSONEncoder):
    """JSON encoder for custom types."""
    
    def default(self, obj):
        """Convert custom types to JSON-serializable."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        
        return super().default(obj)

# Usage
data = {
    "timestamp": datetime.now(),
    "amount": Decimal("19.99"),
    "file_path": Path("/data/file.txt")
}

json_str = json.dumps(data, cls=CustomJSONEncoder)
```

---

### 2. JSON Stream Parser

```python
def parse_json_stream(file_path: str):
    """
    Parse large JSON file line-by-line.
    
    Assumes each line is a valid JSON object.
    """
    with open(file_path, 'r') as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                yield obj
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON line: {e}")
                continue

# Usage
for record in parse_json_stream("large_data.jsonl"):
    process_record(record)
```

---

### 3. JSON Diff

```python
def json_diff(obj1: dict, obj2: dict) -> dict:
    """
    Compute difference between two JSON objects.
    
    Returns:
        Dictionary with added, removed, changed keys
    """
    diff = {
        "added": {},
        "removed": {},
        "changed": {}
    }
    
    # Find added and changed
    for key, value in obj2.items():
        if key not in obj1:
            diff["added"][key] = value
        elif obj1[key] != value:
            diff["changed"][key] = {
                "old": obj1[key],
                "new": value
            }
    
    # Find removed
    for key in obj1:
        if key not in obj2:
            diff["removed"][key] = obj1[key]
    
    return diff

# Usage
old_config = {"timeout": 30, "retry": 3, "debug": True}
new_config = {"timeout": 60, "retry": 3, "logging": True}

diff = json_diff(old_config, new_config)
# {
#   "added": {"logging": True},
#   "removed": {"debug": True},
#   "changed": {"timeout": {"old": 30, "new": 60}}
# }
```

---

### 4. JSON Compression

```python
import gzip

def save_json_compressed(data: Any, file_path: str) -> None:
    """Save JSON with gzip compression."""
    json_str = json.dumps(data)
    json_bytes = json_str.encode('utf-8')
    
    with gzip.open(file_path, 'wb') as f:
        f.write(json_bytes)

def load_json_compressed(file_path: str) -> Any:
    """Load compressed JSON file."""
    with gzip.open(file_path, 'rb') as f:
        json_bytes = f.read()
    
    json_str = json_bytes.decode('utf-8')
    return json.loads(json_str)

# Usage
large_data = {"items": [{"id": i} for i in range(10000)]}

save_json_compressed(large_data, "data.json.gz")
loaded = load_json_compressed("data.json.gz")
```

---

## Data Format Conversion

### CSV to JSON

```python
import csv

def csv_to_json(csv_file: str) -> list[dict]:
    """Convert CSV to list of dictionaries."""
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Usage
users = csv_to_json("users.csv")
write_json_pretty(users, "users.json")
```

---

### JSON to CSV

```python
def json_to_csv(
    data: list[dict],
    csv_file: str,
    fieldnames: list[str] | None = None
) -> None:
    """Convert list of dictionaries to CSV."""
    if not data:
        return
    
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Usage
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]

json_to_csv(users, "users.csv")
```

---

## Testing

```python
import unittest

class TestJSONUtils(unittest.TestCase):
    def test_merge_json(self):
        base = {"a": 1, "b": {"c": 2}}
        updates = {"b": {"d": 3}, "e": 4}
        
        result = merge_json(base, updates)
        
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"]["c"], 2)
        self.assertEqual(result["b"]["d"], 3)
        self.assertEqual(result["e"], 4)
    
    def test_get_nested_value(self):
        data = {"a": {"b": {"c": "value"}}}
        
        self.assertEqual(
            get_nested_value(data, "a.b.c"),
            "value"
        )
        self.assertEqual(
            get_nested_value(data, "a.b.x", default="default"),
            "default"
        )
```

---

## Best Practices

### DO ✅

- Use `ensure_ascii=False` for non-ASCII characters
- Validate JSON before processing critical data
- Use atomic writes for important files
- Handle JSONDecodeError explicitly
- Sort keys for consistent output
- Use compression for large JSON files

### DON'T ❌

- Trust external JSON without validation
- Use `eval()` to parse JSON
- Store sensitive data in plain JSON
- Ignore encoding issues
- Parse huge JSON files into memory (use streaming)
- Hardcode JSON structure assumptions

---

## Related Documentation

- **Data Persistence**: `source-docs/utilities/005-data-persistence.md`
- **Test Helpers**: `source-docs/utilities/007-test-helpers.md`
- **Configuration Management**: `source-docs/utilities/008-configuration-management.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Utilities Team
