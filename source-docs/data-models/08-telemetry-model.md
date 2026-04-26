# Telemetry Data Model

**Module**: `src/app/core/telemetry.py` [[src/app/core/telemetry.py]]  
**Storage**: `logs/telemetry.json`  
**Persistence**: JSON with atomic writes and rotation  
**Schema Version**: 1.0

---

## Overview

Telemetry provides opt-in event logging for monitoring system behavior with atomic writes, automatic rotation, and privacy-first design (disabled by default).

### Key Features

- **Opt-In**: Disabled by default, explicit enablement required
- **Atomic Writes**: File locking prevents corruption
- **Auto-Rotation**: Keeps last 1000 events (configurable)
- **Privacy-First**: No PII collection
- **Lightweight**: Minimal overhead (<1ms per event)
- **Fail-Silent**: Never affects app behavior

---

## Configuration

### Environment Variables

```bash
# .env
TELEMETRY_ENABLED=true              # Enable telemetry (default: false)
TELEMETRY_FILE=logs/telemetry.json  # Log file path (default: logs/telemetry.json)
TELEMETRY_MAX_EVENTS=1000           # Max events to retain (default: 1000)
```

### Enabling Telemetry

```python
import os
os.environ["TELEMETRY_ENABLED"] = "true"

from app.core.telemetry import TelemetryManager
assert TelemetryManager.enabled() == True
```

---

## Schema Structure

### Telemetry Log Document

**File**: `logs/telemetry.json`

```json
[
  {
    "name": "user_login",
    "timestamp": 1705764000.123,
    "payload": {
      "username": "alice",
      "success": true,
      "duration_ms": 145,
      "ip_address": "192.168.1.100"
    }
  },
  {
    "name": "persona_trait_changed",
    "timestamp": 1705764120.456,
    "payload": {
      "trait": "curiosity",
      "old_value": 0.8,
      "new_value": 0.85,
      "changed_by": "user_interaction"
    }
  },
  {
    "name": "learning_request_approved",
    "timestamp": 1705764240.789,
    "payload": {
      "request_id": "req_042",
      "topic": "Python Async Programming",
      "approved_by": "admin",
      "duration_ms": 250
    }
  }
]
```

---

## Field Specifications

### Event Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Event type identifier |
| `timestamp` | float | Yes | Unix timestamp (seconds since epoch) |
| `payload` | object | No | Event-specific data (optional) |

### Common Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | User identifier (no PII) |
| `duration_ms` | float | Operation duration in milliseconds |
| `success` | boolean | Operation outcome |
| `error` | string | Error message (if success=false) |
| `session_id` | string | Session identifier |

---

## Event Types

### User Authentication Events

```json
{
  "name": "user_login",
  "timestamp": 1705764000.0,
  "payload": {
    "username": "alice",
    "success": true,
    "duration_ms": 145
  }
}

{
  "name": "user_logout",
  "timestamp": 1705768000.0,
  "payload": {
    "username": "alice",
    "session_duration_seconds": 3600
  }
}

{
  "name": "user_login_failed",
  "timestamp": 1705764100.0,
  "payload": {
    "username": "bob",
    "reason": "invalid_password",
    "failed_attempts": 3
  }
}
```

### AI Persona Events

```json
{
  "name": "persona_trait_changed",
  "timestamp": 1705764200.0,
  "payload": {
    "trait": "playfulness",
    "old_value": 0.6,
    "new_value": 0.8,
    "changed_by": "user_preference"
  }
}

{
  "name": "persona_mood_updated",
  "timestamp": 1705764300.0,
  "payload": {
    "mood_dimension": "enthusiasm",
    "old_value": 0.7,
    "new_value": 0.85,
    "trigger": "positive_user_feedback"
  }
}
```

### Learning Request Events

```json
{
  "name": "learning_request_submitted",
  "timestamp": 1705764400.0,
  "payload": {
    "request_id": "req_042",
    "topic": "Python Async Programming",
    "priority": "high",
    "submitted_by": "alice"
  }
}

{
  "name": "learning_request_approved",
  "timestamp": 1705764500.0,
  "payload": {
    "request_id": "req_042",
    "approved_by": "admin",
    "duration_ms": 250
  }
}

{
  "name": "learning_request_denied",
  "timestamp": 1705764600.0,
  "payload": {
    "request_id": "req_043",
    "denied_by": "admin",
    "reason": "Content violates policy",
    "vault_entry": "BV_20240120_001"
  }
}
```

### Command Override Events

```json
{
  "name": "command_override_activated",
  "timestamp": 1705764700.0,
  "payload": {
    "activated_by": "admin",
    "reason": "emergency_system_repair",
    "duration_seconds": 300
  }
}

{
  "name": "command_override_deactivated",
  "timestamp": 1705765000.0,
  "payload": {
    "deactivated_by": "admin",
    "total_duration_seconds": 300,
    "commands_executed": 5
  }
}
```

### Memory & Knowledge Events

```json
{
  "name": "knowledge_added",
  "timestamp": 1705764800.0,
  "payload": {
    "category": "technical",
    "source": "user_conversation",
    "confidence": 0.9
  }
}

{
  "name": "conversation_logged",
  "timestamp": 1705764900.0,
  "payload": {
    "role": "user",
    "message_length": 250,
    "session_id": "abc123"
  }
}
```

---

## Usage Examples

### Sending Events

```python
from app.core.telemetry import send_event

# Simple event
send_event("user_login", {"username": "alice", "success": True})

# Event with detailed payload
send_event("learning_request_approved", {
    "request_id": "req_042",
    "topic": "Python Async",
    "approved_by": "admin",
    "duration_ms": 250
})

# Error event
send_event("system_error", {
    "error_type": "FileNotFoundError",
    "error_message": "users.json not found",
    "traceback": "..."
})
```

### Checking Telemetry Status

```python
from app.core.telemetry import TelemetryManager

if TelemetryManager.enabled():
    send_event("feature_used", {"feature": "image_generation"})
else:
    # Telemetry disabled, no logging
    pass
```

### Integration in Core Systems

```python
# In user_manager.py
def authenticate(self, username: str, password: str) -> bool:
    start_time = time.time()
    
    try:
        # Authentication logic
        is_valid = self._verify_password(username, password)
        
        duration = (time.time() - start_time) * 1000
        send_event("user_login", {
            "username": username,
            "success": is_valid,
            "duration_ms": duration
        })
        
        return is_valid
    except Exception as e:
        send_event("user_login_error", {
            "username": username,
            "error": str(e)
        })
        raise
```

---

## Atomic Write Implementation

### Thread-Safe Event Logging

```python
def send_event(name: str, payload: dict[str, Any] | None = None) -> None:
    """Send telemetry event with atomic write."""
    if not TelemetryManager.enabled():
        return
    
    _ensure_logs_dir()
    payload = payload or {}
    
    event = {
        "name": name,
        "timestamp": time.time(),
        "payload": payload,
    }
    
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
        # Fail silently - telemetry must not affect app
        pass
```

---

## Event Rotation

### Automatic Rotation Strategy

```python
TELEMETRY_MAX_EVENTS = int(os.getenv("TELEMETRY_MAX_EVENTS", "1000"))

# Rotation happens automatically during write:
# - Keep last 1000 events (default)
# - Oldest events are discarded
# - No archiving (to maintain simplicity)
```

### Manual Rotation (if needed)

```python
def rotate_telemetry_logs(archive_path: str | None = None):
    """Manually rotate telemetry logs."""
    if not os.path.exists(TELEMETRY_FILE):
        return
    
    # Archive current log
    if archive_path:
        shutil.copy2(TELEMETRY_FILE, archive_path)
    
    # Clear current log
    with open(TELEMETRY_FILE, 'w') as f:
        json.dump([], f)
```

---

## Privacy & Security

### No PII Collection

**Prohibited Data**:
- Real names (use usernames only)
- Email addresses
- IP addresses (unless explicitly needed for security)
- Passwords or tokens
- Credit card info
- Location data (GPS coordinates)

**Allowed Data**:
- Usernames (anonymized IDs preferred)
- Operation durations
- Success/failure status
- Error types (not full stack traces with sensitive data)

### GDPR Compliance

```python
def export_user_telemetry(username: str) -> list[dict]:
    """Export all telemetry for a specific user (GDPR right to data portability)."""
    events = _load_telemetry_events()
    user_events = [e for e in events if e.get("payload", {}).get("username") == username]
    return user_events

def delete_user_telemetry(username: str) -> int:
    """Delete all telemetry for a specific user (GDPR right to erasure)."""
    events = _load_telemetry_events()
    filtered_events = [e for e in events if e.get("payload", {}).get("username") != username]
    
    deleted_count = len(events) - len(filtered_events)
    _atomic_write_json(TELEMETRY_FILE, filtered_events)
    
    return deleted_count
```

---

## Analytics & Insights

### Event Aggregation

```python
def get_event_statistics() -> dict:
    """Aggregate telemetry statistics."""
    events = _load_telemetry_events()
    
    event_counts = {}
    for event in events:
        name = event["name"]
        event_counts[name] = event_counts.get(name, 0) + 1
    
    return {
        "total_events": len(events),
        "event_types": len(event_counts),
        "event_counts": event_counts,
        "earliest_event": min(e["timestamp"] for e in events) if events else None,
        "latest_event": max(e["timestamp"] for e in events) if events else None
    }
```

### Query Events

```python
def query_events(event_name: str | None = None, 
                 start_time: float | None = None,
                 end_time: float | None = None) -> list[dict]:
    """Query telemetry events with filters."""
    events = _load_telemetry_events()
    
    # Filter by event name
    if event_name:
        events = [e for e in events if e["name"] == event_name]
    
    # Filter by time range
    if start_time:
        events = [e for e in events if e["timestamp"] >= start_time]
    if end_time:
        events = [e for e in events if e["timestamp"] <= end_time]
    
    return events
```

---

## Performance Considerations

### Event Overhead

- **Per Event**: <1ms (atomic write + JSON serialization)
- **File Size**: ~200 bytes per event
- **1000 Events**: ~200KB total

### Optimization Strategies

1. **Batch Events**: Accumulate events in memory, flush periodically
2. **Async Logging**: Use background thread for I/O
3. **Compression**: gzip old telemetry logs

---

## Testing Strategy

### Unit Tests

```python
def test_telemetry_disabled_by_default():
    assert TelemetryManager.enabled() == False

def test_telemetry_event_logging():
    os.environ["TELEMETRY_ENABLED"] = "true"
    send_event("test_event", {"key": "value"})
    
    events = _load_telemetry_events()
    assert any(e["name"] == "test_event" for e in events)

def test_telemetry_rotation():
    os.environ["TELEMETRY_ENABLED"] = "true"
    os.environ["TELEMETRY_MAX_EVENTS"] = "10"
    
    # Send 15 events
    for i in range(15):
        send_event("test_event", {"index": i})
    
    events = _load_telemetry_events()
    assert len(events) == 10  # Only last 10 retained
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `user_manager.py` | Logs authentication events |
| `ai_systems.py` | Logs persona and learning events |
| `command_override.py` | Logs override activation/deactivation |
| `cloud_sync.py` | Logs sync operations |

---

## Future Enhancements

1. **Async Logging**: Background thread for zero-latency logging
2. **Structured Logging**: Integration with logging library
3. **Metrics Dashboard**: Real-time visualization
4. **Anomaly Detection**: Alert on unusual patterns
5. **Export Formats**: CSV, Parquet for analysis

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/telemetry.py]]
