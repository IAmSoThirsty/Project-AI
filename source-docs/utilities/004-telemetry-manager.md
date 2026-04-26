# Telemetry Manager

## Overview

The Telemetry Manager (`src/app/core/telemetry.py`) provides opt-in event tracking with atomic JSON logging, automatic rotation, and fail-safe operation. Telemetry is disabled by default and must be explicitly enabled via environment configuration.

**Location**: `src/app/core/telemetry.py`  
**Lines of Code**: 77  
**Key Features**: Opt-in, atomic writes, rotation, fail-safe  
**Dependencies**: json, os, time, app.core.ai_systems._atomic_write_json

---

## Design Philosophy

### Privacy-First Principles

1. **Opt-in by Default**: Telemetry is OFF unless explicitly enabled
2. **Local Storage**: Events stored locally, not sent to external servers
3. **Transparent Configuration**: Clear environment variable controls
4. **Fail-Safe**: Telemetry errors never affect application behavior
5. **Rotation**: Automatic cleanup prevents unbounded log growth

---

## Configuration

### Environment Variables

```bash
# Enable telemetry (default: false)
TELEMETRY_ENABLED=true

# Custom log file path (default: logs/telemetry.json)
TELEMETRY_FILE=logs/my_telemetry.json

# Maximum events to retain (default: 1000)
TELEMETRY_MAX_EVENTS=500
```

### Supported Values for TELEMETRY_ENABLED

```python
TELEMETRY_ENABLED = os.getenv("TELEMETRY_ENABLED", "false").lower() in (
    "1",
    "true",
    "yes",
)
```

**Accepted**: `1`, `true`, `yes`, `True`, `TRUE`, `YES`  
**All others**: Treated as disabled

---

## Core Components

### 1. TelemetryManager Class

```python
class TelemetryManager:
    """Minimal telemetry manager. Stores events as a JSON array in TELEMETRY_FILE."""
    
    @staticmethod
    def enabled() -> bool:
        """Check if telemetry is enabled."""
        return TELEMETRY_ENABLED
    
    @staticmethod
    def send_event(name: str, payload: dict[str, Any] | None = None) -> None:
        """Send an event (if telemetry enabled)."""
```

---

### 2. Event Structure

Each event is a dictionary with:
- `name`: Event identifier (string)
- `timestamp`: Unix timestamp (float)
- `payload`: Custom event data (dict)

**Example Event**:
```json
{
  "name": "user_login",
  "timestamp": 1706112345.678,
  "payload": {
    "username": "alice",
    "success": true,
    "auth_method": "password"
  }
}
```

---

### 3. File Format

Events are stored as a JSON array:

```json
[
  {
    "name": "app_start",
    "timestamp": 1706112000.0,
    "payload": {
      "version": "1.0.0"
    }
  },
  {
    "name": "user_login",
    "timestamp": 1706112100.0,
    "payload": {
      "username": "alice"
    }
  }
]
```

---

## API Reference

### enabled()

```python
@staticmethod
def enabled() -> bool
```

**Purpose**: Check if telemetry is enabled.

**Returns**: `True` if enabled, `False` otherwise

**Example**:
```python
if TelemetryManager.enabled():
    print("Telemetry is active")
else:
    print("Telemetry is disabled")
```

---

### send_event()

```python
@staticmethod
def send_event(name: str, payload: dict[str, Any] | None = None) -> None
```

**Purpose**: Log an event to the telemetry file.

**Parameters**:
- `name`: Event identifier (e.g., "user_login", "ai_decision")
- `payload`: Optional dictionary with event-specific data

**Behavior**:
- Does nothing if telemetry disabled
- Creates log directory if needed
- Loads existing events
- Appends new event
- Rotates if exceeds `TELEMETRY_MAX_EVENTS`
- Writes atomically to prevent corruption
- Silently fails on errors (never crashes app)

**Example**:
```python
from app.core.telemetry import send_event

# Simple event
send_event("app_started")

# Event with payload
send_event("user_action", {
    "action": "delete_file",
    "filename": "test.txt",
    "success": True
})

# AI decision tracking
send_event("ai_decision", {
    "decision_type": "four_laws",
    "action": "block_delete",
    "reason": "Potential harm to user",
    "timestamp": time.time()
})
```

---

## Usage Patterns

### Pattern 1: Application Lifecycle Events

```python
from app.core.telemetry import send_event

class Application:
    def __init__(self):
        send_event("app_started", {
            "version": self.get_version(),
            "platform": sys.platform,
            "python_version": sys.version
        })
    
    def shutdown(self):
        send_event("app_shutdown", {
            "uptime_seconds": time.time() - self.start_time,
            "total_actions": self.action_count
        })
        # Clean shutdown...
```

---

### Pattern 2: User Action Tracking

```python
class UserManager:
    def authenticate(self, username: str, password: str) -> bool:
        success = self._check_credentials(username, password)
        
        send_event("user_login", {
            "username": username,
            "success": success,
            "auth_method": "password",
            "ip_address": self._get_client_ip()
        })
        
        return success
    
    def perform_action(self, user: str, action: str, details: dict):
        result = self._execute_action(action, details)
        
        send_event("user_action", {
            "user": user,
            "action": action,
            "success": result.success,
            "duration_ms": result.duration
        })
```

---

### Pattern 3: AI Decision Tracking

```python
class FourLaws:
    def validate_action(self, action: str, context: dict) -> tuple[bool, str]:
        start_time = time.time()
        is_allowed, reason = self._check_laws(action, context)
        duration = time.time() - start_time
        
        send_event("four_laws_validation", {
            "action": action,
            "allowed": is_allowed,
            "reason": reason,
            "validation_time_ms": duration * 1000,
            "context_keys": list(context.keys())
        })
        
        return is_allowed, reason
```

---

### Pattern 4: Performance Monitoring

```python
from contextlib import contextmanager

@contextmanager
def track_performance(operation_name: str):
    """Context manager for performance tracking."""
    start_time = time.time()
    error = None
    
    try:
        yield
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        send_event("performance", {
            "operation": operation_name,
            "duration_ms": duration_ms,
            "success": error is None,
            "error": error
        })

# Usage
with track_performance("load_large_dataset"):
    df = pd.read_csv("large_file.csv")
```

---

### Pattern 5: Error Tracking

```python
def handle_error(error: Exception, context: dict):
    """Enhanced error handler with telemetry."""
    logger.error(f"Error: {error}", exc_info=True)
    
    send_event("error", {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "stack_trace": traceback.format_exc()
    })
    
    # Continue error handling...
```

---

## Atomic Write Pattern

### Implementation

The telemetry manager uses `_atomic_write_json` from `app.core.ai_systems` to ensure data integrity:

```python
from app.core.ai_systems import _atomic_write_json

def send_event(name: str, payload: dict[str, Any] | None = None) -> None:
    # ...
    try:
        # Load existing events
        events = []
        if os.path.exists(TELEMETRY_FILE):
            with open(TELEMETRY_FILE, encoding="utf-8") as f:
                try:
                    events = json.load(f)
                    if not isinstance(events, list):
                        events = []
                except Exception:
                    events = []
        
        # Append new event
        events.append(event)
        
        # Rotate if needed
        if len(events) > TELEMETRY_MAX_EVENTS:
            events = events[-TELEMETRY_MAX_EVENTS:]
        
        # Atomic write
        _atomic_write_json(TELEMETRY_FILE, events)
    except Exception:
        # Fail silently — telemetry must not affect app behavior
        pass
```

### Benefits

1. **No Corruption**: Write to temp file, then rename (atomic)
2. **Concurrent Safe**: Multiple processes can write simultaneously
3. **Partial Failure Recovery**: If write fails, old file remains intact

---

## Event Rotation

### Rotation Strategy

**Trigger**: When event count exceeds `TELEMETRY_MAX_EVENTS`

**Action**: Keep only the most recent N events

```python
if len(events) > TELEMETRY_MAX_EVENTS:
    events = events[-TELEMETRY_MAX_EVENTS:]
```

**Example**:
- Max events: 1000
- Current: 1050 events
- After rotation: 1000 most recent events

### Manual Rotation

```python
def rotate_telemetry():
    """Manually rotate telemetry file."""
    if not os.path.exists(TELEMETRY_FILE):
        return
    
    with open(TELEMETRY_FILE, encoding="utf-8") as f:
        events = json.load(f)
    
    if len(events) > TELEMETRY_MAX_EVENTS:
        events = events[-TELEMETRY_MAX_EVENTS:]
        _atomic_write_json(TELEMETRY_FILE, events)
        print(f"Rotated telemetry to {len(events)} events")
```

---

## Fail-Safe Design

### Principle: Never Crash the Application

```python
try:
    # All telemetry operations
    ...
except Exception:
    # Fail silently — telemetry must not affect app behavior
    pass
```

### What This Means

1. **Disk Full**: Telemetry stops, app continues
2. **Permission Denied**: Telemetry disabled, app continues
3. **JSON Corruption**: Old events discarded, new events start fresh
4. **Concurrent Write Conflict**: One write wins, app continues

### Debugging Failures

To debug telemetry issues:

```python
import logging
logger = logging.getLogger(__name__)

def send_event(name: str, payload: dict[str, Any] | None = None) -> None:
    if not TelemetryManager.enabled():
        return
    
    try:
        # ... telemetry logic
    except Exception as e:
        # Log for debugging, but don't crash
        logger.debug("Telemetry error: %s", e)
```

---

## Analysis Tools

### Reading Telemetry Data

```python
import json
from collections import Counter
from datetime import datetime

def analyze_telemetry(filepath: str = "logs/telemetry.json"):
    """Analyze telemetry data."""
    with open(filepath) as f:
        events = json.load(f)
    
    # Event counts
    event_counts = Counter(e["name"] for e in events)
    print("Event Counts:")
    for event_name, count in event_counts.most_common():
        print(f"  {event_name}: {count}")
    
    # Time range
    timestamps = [e["timestamp"] for e in events]
    start = datetime.fromtimestamp(min(timestamps))
    end = datetime.fromtimestamp(max(timestamps))
    print(f"\nTime Range: {start} to {end}")
    
    # User activity
    user_events = [e for e in events if e["name"] == "user_action"]
    print(f"\nTotal User Actions: {len(user_events)}")
```

---

### Event Filtering

```python
def filter_events(events: list[dict], event_name: str) -> list[dict]:
    """Filter events by name."""
    return [e for e in events if e["name"] == event_name]

def filter_by_time_range(
    events: list[dict],
    start_time: float,
    end_time: float
) -> list[dict]:
    """Filter events by timestamp range."""
    return [
        e for e in events
        if start_time <= e["timestamp"] <= end_time
    ]

# Usage
with open("logs/telemetry.json") as f:
    events = json.load(f)

# Get all login events from the last hour
one_hour_ago = time.time() - 3600
recent_logins = filter_by_time_range(
    filter_events(events, "user_login"),
    one_hour_ago,
    time.time()
)
```

---

### Exporting to CSV

```python
import csv

def export_to_csv(json_file: str, csv_file: str):
    """Export telemetry to CSV."""
    with open(json_file) as f:
        events = json.load(f)
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "event_name", "payload"])
        
        for event in events:
            writer.writerow([
                datetime.fromtimestamp(event["timestamp"]),
                event["name"],
                json.dumps(event["payload"])
            ])
    
    print(f"Exported {len(events)} events to {csv_file}")
```

---

## Privacy & GDPR Compliance

### Data Minimization

**DO**:
- Log event types and counts
- Log anonymized performance metrics
- Log error types (not sensitive data)

**DON'T**:
- Log passwords or API keys
- Log personal identifiable information (PII) without consent
- Log sensitive business data

**Example**:
```python
# BAD
send_event("user_login", {
    "username": "alice@company.com",  # PII
    "password": "secret123",           # Credential!
    "ip_address": "192.168.1.1"        # PII
})

# GOOD
send_event("user_login", {
    "username_hash": hashlib.sha256("alice@company.com".encode()).hexdigest(),
    "auth_method": "password",
    "success": True
})
```

---

### User Control

```python
class TelemetrySettings:
    def opt_in(self):
        """User opts into telemetry."""
        os.environ["TELEMETRY_ENABLED"] = "true"
        # Save to config file for persistence
        self._save_config()
    
    def opt_out(self):
        """User opts out of telemetry."""
        os.environ["TELEMETRY_ENABLED"] = "false"
        self._save_config()
    
    def delete_telemetry_data(self):
        """Delete all telemetry data (GDPR right to erasure)."""
        if os.path.exists(TELEMETRY_FILE):
            os.remove(TELEMETRY_FILE)
            logger.info("Telemetry data deleted")
```

---

## Performance Impact

### Overhead Analysis

**send_event() costs**:
1. File existence check: ~0.01ms
2. File read: ~1-5ms (for 1000 events)
3. JSON parse: ~1-2ms
4. JSON serialize: ~1-2ms
5. Atomic write: ~2-5ms

**Total per event**: ~5-15ms

**Mitigation**:
- Async writes (future enhancement)
- In-memory buffer with periodic flush
- Conditional logging (only log important events)

---

### Async Enhancement (Future)

```python
import asyncio
from queue import Queue
from threading import Thread

class AsyncTelemetryManager:
    def __init__(self):
        self.event_queue = Queue()
        self.worker_thread = Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def send_event(self, name: str, payload: dict | None = None):
        """Queue event for async processing."""
        if not TELEMETRY_ENABLED:
            return
        
        event = {
            "name": name,
            "timestamp": time.time(),
            "payload": payload or {}
        }
        self.event_queue.put(event)
    
    def _worker(self):
        """Background worker to flush events."""
        buffer = []
        
        while True:
            # Collect events for up to 1 second
            try:
                event = self.event_queue.get(timeout=1.0)
                buffer.append(event)
                
                # Flush when buffer reaches 10 events
                if len(buffer) >= 10:
                    self._flush_buffer(buffer)
                    buffer = []
            except:
                # Timeout - flush whatever we have
                if buffer:
                    self._flush_buffer(buffer)
                    buffer = []
    
    def _flush_buffer(self, buffer: list):
        """Flush buffer to disk."""
        # ... atomic write logic
```

---

## Testing

### Unit Tests

```python
import unittest
import tempfile
import os
from pathlib import Path

class TestTelemetry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.telemetry_file = os.path.join(self.temp_dir, "test_telemetry.json")
        
        # Override environment
        os.environ["TELEMETRY_ENABLED"] = "true"
        os.environ["TELEMETRY_FILE"] = self.telemetry_file
        os.environ["TELEMETRY_MAX_EVENTS"] = "5"
    
    def tearDown(self):
        Path(self.telemetry_file).unlink(missing_ok=True)
        os.rmdir(self.temp_dir)
    
    def test_send_event(self):
        send_event("test_event", {"key": "value"})
        
        with open(self.telemetry_file) as f:
            events = json.load(f)
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "test_event")
        self.assertEqual(events[0]["payload"], {"key": "value"})
    
    def test_rotation(self):
        for i in range(10):
            send_event(f"event_{i}")
        
        with open(self.telemetry_file) as f:
            events = json.load(f)
        
        # Should only keep last 5
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0]["name"], "event_5")
```

---

## Related Documentation

- **AI Systems**: `source-docs/core/ai-systems.md`
- **Data Persistence**: `source-docs/utilities/005-data-persistence.md`
- **Logging Guidelines**: `docs/logging-best-practices.md`

---

## Version History

- **v1.0** (Current): Initial opt-in telemetry with atomic writes
- **v0.5**: Prototype with basic file logging

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: Core Infrastructure Team
