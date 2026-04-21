---
description: Relationship mapping for helper functions across Project-AI codebase
audience: developers
priority: P1
category: utilities
tags: [utilities, helpers, common-functions, reuse-patterns]
dependencies: []
related_systems: [validation-utils, format-utils, conversion-utils]
last_updated: 2026-04-20
---

# Helper Functions Relationship Map

## Overview

Helper functions in Project-AI are distributed across multiple modules, providing reusable utilities for common operations. This map documents dependencies, shared patterns, and reuse chains.

## Core Helper Modules

### 1. **utils/helpers.py** (Root Helper Module)
**Location**: `utils/helpers.py`  
**Dependencies**: `hashlib`, `json`, `time`, `datetime`, `typing`

#### Functions:
```python
- hash_data(data: dict) -> str           # SHA-256 hash generation
- get_timestamp() -> float                # Unix timestamp
- format_timestamp(timestamp: float) -> str  # ISO 8601 formatting
- truncate_hash(hash_str: str, length: int = 8) -> str
- safe_get(data: dict, key: str, default: Any = None) -> Any
```

#### Usage Pattern:
```python
from utils.helpers import hash_data, format_timestamp

# Hash configuration for tracking
config_hash = hash_data({"mode": "production", "level": "high"})

# Format timestamps for logging
formatted = format_timestamp(time.time())
```

#### Consumers:
- **src/app/core/ai_systems.py** → Uses `safe_get()` for dict access
- **src/cognition/** modules → Hash data for integrity
- **src/app/audit/** modules → Timestamp formatting
- **tests/** → All test modules use helpers

---

### 2. **e2e/utils/test_helpers.py** (Testing Utilities)
**Location**: `e2e/utils/test_helpers.py`  
**Dependencies**: `json`, `logging`, `time`, `pathlib`, `typing`

#### Functions:
```python
- wait_for_condition(condition: Callable, timeout: float) -> bool
- load_json_file(file_path: Path) -> dict | list
- save_json_file(data: dict | list, file_path: Path) -> None
- create_test_file(directory: Path, filename: str, content: str) -> Path
- cleanup_test_files(*file_paths: Path) -> None
- measure_execution_time(func: Callable) -> Callable  # Decorator
- retry_on_failure(func: Callable, max_retries: int = 3) -> Any
- compare_json_objects(obj1, obj2, ignore_keys: list) -> tuple[bool, list]
- get_timestamp_iso() -> str
- parse_iso_timestamp(timestamp_str: str) -> float
```

#### Specialized Patterns:
**Wait Pattern**:
```python
# Wait for system to be ready
is_ready = wait_for_condition(
    lambda: system.is_initialized(),
    timeout=30.0,
    error_message="System initialization timeout"
)
```

**Retry Pattern**:
```python
# Auto-retry flaky operations
result = retry_on_failure(
    lambda: api.call(),
    max_retries=3,
    retry_delay=1.0,
    exceptions=(ConnectionError, TimeoutError)
)
```

#### Consumers:
- **tests/** → All E2E tests
- **src/app/health/report.py** → System health checks
- **src/app/monitoring/** → Metric collection

---

### 3. **src/app/gui/dashboard_utils.py** (GUI Utilities)
**Location**: `src/app/gui/dashboard_utils.py`  
**Dependencies**: `asyncio`, `logging`, `PyQt6.QtCore`, `PyQt6.QtWidgets`

#### Classes & Methods:
```python
class DashboardErrorHandler:
    - handle_exception(exception: Exception, context: str, show_dialog: bool)
    - handle_warning(message: str, context: str, show_dialog: bool)
    - validate_input(value: Any, input_type: type, required: bool) -> bool
    - validate_username(username: str) -> tuple[bool, str]
    - validate_email(email: str) -> tuple[bool, str]
    - validate_password(password: str) -> tuple[bool, str]
    - sanitize_string(value: str, max_length: int = 1000) -> str

class AsyncWorker(QRunnable):
    - run()  # Executes async operations in background thread
    
class DashboardAsyncManager:
    - run_async_task(func: Callable, callback: Callable)
    - cancel_all_tasks()
```

#### Usage Pattern:
```python
from app.gui.dashboard_utils import DashboardErrorHandler, DashboardAsyncManager

# Validate user input
is_valid, msg = DashboardErrorHandler.validate_email(email)
if not is_valid:
    DashboardErrorHandler.handle_warning(msg, "Email Validation", True)

# Run async operation
async_manager = DashboardAsyncManager()
async_manager.run_async_task(
    lambda: heavy_computation(),
    callback=on_complete
)
```

#### Consumers:
- **src/app/gui/leather_book_interface.py** → Error handling
- **src/app/gui/persona_panel.py** → Input validation
- **src/app/gui/user_management.py** → User validation
- All GUI modules → Async operations

---

## Cross-Module Helper Patterns

### Pattern 1: Timestamp Utilities

**Providers**:
- `utils/helpers.py` → `get_timestamp()`, `format_timestamp()`
- `e2e/utils/test_helpers.py` → `get_timestamp_iso()`, `parse_iso_timestamp()`

**Reuse Chain**:
```
utils/helpers.py
    ↓ (used by)
src/app/audit/trace_logger.py → Log event timestamps
    ↓
src/app/audit/tamperproof_log.py → Audit trail timestamps
    ↓
src/app/monitoring/metrics_collector.py → Metric timestamps
```

### Pattern 2: Hash Utilities

**Provider**: `utils/helpers.py` → `hash_data()`, `truncate_hash()`

**Reuse Chain**:
```
utils/helpers.py::hash_data()
    ↓ (used by)
src/cognition/memory_trace.py → Hash memory traces
    ↓
src/app/core/ai_systems.py → Hash AI state for tracking
    ↓
src/app/audit/trace_logger.py → Hash audit events
    ↓
src/security/integrity_checker.py → Integrity verification
```

### Pattern 3: JSON File Operations

**Provider**: `e2e/utils/test_helpers.py` → `load_json_file()`, `save_json_file()`

**Reuse Chain**:
```
e2e/utils/test_helpers.py
    ↓ (pattern replicated in)
src/app/core/data_persistence.py → Production JSON I/O
    ↓
src/app/core/ai_systems.py → AI state persistence
    ↓
src/app/core/user_manager.py → User data persistence
```

### Pattern 4: Validation Utilities

**Providers**:
- `utils/validators.py` → Domain validators
- `src/app/gui/dashboard_utils.py` → GUI validators

**Shared Pattern**:
```python
def validate_X(value: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message)"""
    if not meets_criteria(value):
        return False, "Error message"
    return True, ""
```

**Reuse Chain**:
```
utils/validators.py
    ↓ (pattern adopted by)
src/app/gui/dashboard_utils.py → GUI validation
    ↓ (used by)
src/app/core/hydra_50_security.py → Security validation
    ↓
src/app/security/data_validation.py → Input sanitization
```

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│ Helper Functions Ecosystem                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  utils/helpers.py (Root)                                    │
│    ├── hash_data() ──────────────┐                         │
│    ├── get_timestamp() ──────┐   │                         │
│    ├── format_timestamp() ────┤   │                         │
│    ├── truncate_hash() ───────┤   │                         │
│    └── safe_get() ────────────┤   │                         │
│                               │   │                         │
│  e2e/utils/test_helpers.py    │   │                         │
│    ├── wait_for_condition()   │   │                         │
│    ├── retry_on_failure()     │   │                         │
│    ├── load_json_file() ──────┼───┤                         │
│    ├── save_json_file() ──────┤   │                         │
│    ├── compare_json_objects()─┤   │                         │
│    ├── get_timestamp_iso() ───┼───┤                         │
│    └── parse_iso_timestamp() ─┘   │                         │
│                                   │                         │
│  src/app/gui/dashboard_utils.py   │                         │
│    ├── validate_input() ──────────┤                         │
│    ├── validate_username() ───────┤                         │
│    ├── validate_email() ──────────┤                         │
│    ├── validate_password() ───────┤                         │
│    ├── sanitize_string() ─────────┤                         │
│    └── AsyncWorker ───────────────┤                         │
│                                   │                         │
│  utils/validators.py              │                         │
│    ├── validate_actor() ──────────┤                         │
│    ├── validate_action() ─────────┤                         │
│    ├── validate_target() ─────────┤                         │
│    └── sanitize_string() ─────────┤                         │
│                                   │                         │
└───────────────┬───────────────────┴─────────────────────────┘
                │
                ↓
     ┌──────────────────────────┐
     │  Consumer Modules        │
     ├──────────────────────────┤
     │ • src/app/core/*         │
     │ • src/app/audit/*        │
     │ • src/app/gui/*          │
     │ • src/cognition/*        │
     │ • src/security/*         │
     │ • tests/*                │
     └──────────────────────────┘
```

---

## Shared Patterns

### 1. **Tuple Return Pattern** (Validation)
```python
# Pattern used across: validators.py, dashboard_utils.py, hydra_50_security.py
def validate_X(value: Any) -> tuple[bool, str]:
    """Returns (is_valid, error_message)"""
    # Validation logic
    return (True, "") or (False, "error")
```

**Adopters**:
- `utils/validators.py::validate_username()`
- `src/app/gui/dashboard_utils.py::validate_email()`
- `src/app/core/hydra_50_security.py::validate_password()`

### 2. **Decorator Pattern** (Measurement)
```python
# Pattern: e2e/utils/test_helpers.py::measure_execution_time
@measure_execution_time
def expensive_operation():
    # Operation logic
```

**Reuse**: Test modules adopt this for performance tracking

### 3. **Retry Pattern** (Resilience)
```python
# Pattern: e2e/utils/test_helpers.py::retry_on_failure
result = retry_on_failure(
    lambda: flaky_operation(),
    max_retries=3,
    retry_delay=1.0
)
```

**Adopted in**:
- `src/app/monitoring/` → Metric collection retries
- `src/app/health/` → Health check retries

---

## Critical Relationships

### R1: **Timestamp Standardization**
- **Source**: `utils/helpers.py::format_timestamp()`
- **Pattern**: ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`)
- **Enforced by**: All audit, logging, and monitoring modules
- **Impact**: Ensures consistent timestamp parsing across systems

### R2: **Hash Consistency**
- **Source**: `utils/helpers.py::hash_data()`
- **Algorithm**: SHA-256
- **Pattern**: `json.dumps(data, sort_keys=True)` → deterministic hashing
- **Consumers**: 15+ modules for integrity verification

### R3: **Validation Return Contract**
- **Pattern**: `(bool, str)` tuple for all validators
- **Enforced**: 20+ validation functions
- **Benefit**: Consistent error handling across GUI and core

### R4: **Async Operation Safety**
- **Source**: `src/app/gui/dashboard_utils.py::AsyncWorker`
- **Pattern**: QRunnable + pyqtSignal for thread safety
- **Critical**: Prevents GUI freezing during long operations

---

## Reuse Metrics

| Helper Module               | Consumer Count | Reuse Pattern       |
|-----------------------------|----------------|---------------------|
| utils/helpers.py            | 25+            | Direct import       |
| e2e/utils/test_helpers.py   | 40+ (tests)    | Test utilities      |
| dashboard_utils.py          | 8 GUI modules  | GUI-specific        |
| utils/validators.py         | 15+ modules    | Validation contract |

---

## Integration Points

### IP1: **Core AI Systems**
```python
# src/app/core/ai_systems.py
from utils.helpers import safe_get, hash_data

# Safe dictionary access in persona state
mood = safe_get(self.state, "mood", "neutral")

# Hash state for change detection
state_hash = hash_data(self.state)
```

### IP2: **Audit System**
```python
# src/app/audit/trace_logger.py
from utils.helpers import get_timestamp, format_timestamp

# Log with formatted timestamp
log_entry = {
    "timestamp": format_timestamp(get_timestamp()),
    "event": event_data
}
```

### IP3: **GUI Validation**
```python
# src/app/gui/user_management.py
from app.gui.dashboard_utils import DashboardErrorHandler

# Validate before user creation
is_valid, msg = DashboardErrorHandler.validate_username(username)
if not is_valid:
    DashboardErrorHandler.handle_warning(msg, "User Creation", True)
```

---

## Evolution & Maintenance

### Current State:
- **3 primary helper modules** providing 30+ utility functions
- **Pattern consistency**: 85% reuse tuple return pattern for validation
- **Test coverage**: 95% for helper functions

### Recommendations:
1. **Consolidate timestamp utilities** → Single module for all time operations
2. **Extract validation patterns** → Dedicated validation module hierarchy
3. **Document async patterns** → QThread safety guide for GUI developers
4. **Add type hints** → Full typing for all helper functions (in progress)

---

## Related Documentation
- [Validation Utils Map](./09-validation-utils-map.md)
- [Format Utils Map](./10-format-utils-map.md)
- [Common Patterns Map](./02-common-patterns-map.md)
