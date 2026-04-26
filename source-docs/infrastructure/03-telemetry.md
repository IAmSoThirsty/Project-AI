# Telemetry System

**Module:** `src/app/core/telemetry.py`  
**Type:** Core Infrastructure  
**Dependencies:** json, app.core.ai_systems (_atomic_write_json)  
**Related Modules:** data_persistence.py, realtime_monitoring.py

---

## Overview

The Telemetry System provides opt-in event logging with atomic JSON writes and automatic rotation. Designed for production observability without performance impact, with privacy-first defaults (disabled by default).

### Core Principles

- **Opt-In by Default**: Telemetry disabled unless explicitly enabled
- **Atomic Writes**: No data corruption from concurrent writers
- **Automatic Rotation**: Configurable event limits (default: 1000 events)
- **Zero-Impact**: Silent failures never affect application behavior
- **Privacy-First**: No PII collection without explicit consent

---

## Architecture

### System Design

```
Application Events
        ↓
TelemetryManager.send_event()
        ↓
Check TELEMETRY_ENABLED
        ↓
    Disabled? → Silent return
        ↓
    Enabled? → Continue
        ↓
Load existing events (best-effort)
        ↓
Append new event
        ↓
Rotate if > TELEMETRY_MAX_EVENTS
        ↓
_atomic_write_json() (safe concurrent writes)
        ↓
logs/telemetry.json
```

### File Structure

```
logs/
├── telemetry.json          # Current event log (rotated at max size)
├── telemetry.json.1        # Previous rotation (optional backup)
└── telemetry.json.2        # Older rotation
```

---

## Core Classes

### TelemetryManager

**Purpose**: Minimal telemetry manager with atomic event logging and rotation.

```python
from app.core.telemetry import TelemetryManager, send_event

# Static methods (no initialization required)

# Check if telemetry is enabled
if TelemetryManager.enabled():
    print("Telemetry is enabled")

# Send event (only logged if enabled)
send_event(
    name="user_login",
    payload={
        "username": "admin",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0"
    }
)

# Convenience function (same as TelemetryManager.send_event)
send_event("feature_used", {"feature": "image_generation"})
```

---

## Configuration

### Environment Variables

```bash
# Enable telemetry (default: disabled)
export TELEMETRY_ENABLED=true   # or "1", "yes"

# Custom telemetry file path
export TELEMETRY_FILE="/var/log/project-ai/telemetry.json"

# Maximum events before rotation (default: 1000)
export TELEMETRY_MAX_EVENTS=5000
```

### Configuration Constants

```python
# src/app/core/telemetry.py
TELEMETRY_ENABLED = os.getenv("TELEMETRY_ENABLED", "false").lower() in ("1", "true", "yes")
TELEMETRY_FILE = os.getenv("TELEMETRY_FILE", os.path.join("logs", "telemetry.json"))
TELEMETRY_MAX_EVENTS = int(os.getenv("TELEMETRY_MAX_EVENTS", "1000"))
```

---

## Usage Examples

### Basic Event Logging

```python
from app.core.telemetry import send_event

# Application startup
send_event("app_started", {
    "version": "2.1.0",
    "platform": "Windows",
    "python_version": "3.11.5"
})

# User authentication
send_event("user_login", {
    "username": "admin",
    "timestamp": "2026-04-20T14:00:00Z",
    "method": "password"
})

# Feature usage
send_event("feature_used", {
    "feature": "image_generation",
    "backend": "huggingface",
    "model": "stable-diffusion-2-1"
})

# Error tracking
send_event("error_occurred", {
    "error_type": "NetworkError",
    "message": "Failed to connect to cloud sync server",
    "severity": "warning"
})

# Performance metrics
send_event("operation_completed", {
    "operation": "data_encryption",
    "duration_ms": 45.2,
    "size_bytes": 1048576
})
```

### Event Structure

```json
{
  "name": "user_login",
  "timestamp": 1713624000.0,
  "payload": {
    "username": "admin",
    "method": "password"
  }
}
```

**Fields:**
- `name` (string): Event identifier (snake_case)
- `timestamp` (float): Unix timestamp (seconds since epoch)
- `payload` (dict): Event-specific data (optional)

---

## Event Categories

### Application Lifecycle

```python
# Startup
send_event("app_started", {"version": "2.1.0"})

# Shutdown
send_event("app_stopped", {"uptime_seconds": 3600})

# Configuration change
send_event("config_changed", {
    "key": "cloud_sync.enabled",
    "old_value": False,
    "new_value": True
})
```

### User Actions

```python
# Authentication
send_event("user_login", {"username": "admin"})
send_event("user_logout", {"username": "admin", "session_duration": 1800})
send_event("login_failed", {"username": "admin", "reason": "invalid_password"})

# Feature usage
send_event("feature_accessed", {"feature": "ai_persona_panel"})
send_event("command_executed", {"command": "generate_learning_path"})
```

### System Events

```python
# Resource usage
send_event("memory_usage", {"used_mb": 512, "available_mb": 2048})
send_event("disk_usage", {"used_gb": 15.3, "total_gb": 100.0})

# Background tasks
send_event("backup_completed", {"duration_ms": 2500, "size_mb": 42.7})
send_event("sync_completed", {"files_synced": 15, "errors": 0})
```

### Errors and Warnings

```python
# Errors
send_event("error", {
    "type": "DatabaseError",
    "message": "Connection timeout",
    "severity": "critical",
    "stack_trace": traceback.format_exc()
})

# Warnings
send_event("warning", {
    "type": "DeprecationWarning",
    "message": "Using deprecated API endpoint",
    "recommendation": "Upgrade to /api/v2/"
})
```

---

## Rotation and Cleanup

### Automatic Rotation

```python
# Rotation happens automatically when event count exceeds TELEMETRY_MAX_EVENTS
# Example: TELEMETRY_MAX_EVENTS=1000

# Events 1-1000: Written to telemetry.json
# Event 1001 triggers rotation:
#   1. Keep only last 1000 events (events 2-1001)
#   2. Write back to telemetry.json

# Code in telemetry.py:
events.append(event)
if len(events) > TELEMETRY_MAX_EVENTS:
    events = events[-TELEMETRY_MAX_EVENTS:]  # Keep last N events
_atomic_write_json(TELEMETRY_FILE, events)
```

### Manual Rotation

```python
import json
import os
from datetime import datetime

def rotate_telemetry_file():
    """Manually rotate telemetry file."""
    telemetry_file = "logs/telemetry.json"
    
    if not os.path.exists(telemetry_file):
        return
    
    # Backup current file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"logs/telemetry_{timestamp}.json"
    
    os.rename(telemetry_file, backup_file)
    print(f"Rotated telemetry to {backup_file}")

# Usage
rotate_telemetry_file()
```

### Cleanup Old Logs

```python
import glob
import os
from datetime import datetime, timedelta

def cleanup_old_telemetry_logs(retention_days=30):
    """Delete telemetry logs older than retention period."""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    for log_file in glob.glob("logs/telemetry_*.json"):
        file_stat = os.stat(log_file)
        file_date = datetime.fromtimestamp(file_stat.st_mtime)
        
        if file_date < cutoff_date:
            os.remove(log_file)
            print(f"Deleted old telemetry log: {log_file}")

# Usage
cleanup_old_telemetry_logs(retention_days=30)
```

---

## Atomic Writes

### _atomic_write_json Implementation

```python
# From app.core.ai_systems
def _atomic_write_json(path: str, data: Any) -> None:
    """
    Atomically write JSON data to file using temp file + rename.
    
    Prevents corruption from concurrent writes or crashes during write.
    """
    import os
    import json
    import tempfile
    
    # Write to temporary file
    dir_name = os.path.dirname(path) or "."
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=dir_name,
        delete=False,
        suffix='.tmp'
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2)
        tmp_path = tmp_file.name
    
    # Atomic rename (POSIX guarantee)
    os.replace(tmp_path, path)
```

**Benefits:**
- No partial writes visible to readers
- Concurrent writes don't corrupt file
- Crash-safe (either old or new file, never half-written)

**Trade-offs:**
- Slightly slower than direct write
- Requires temp file space
- Not ideal for extremely high-frequency writes (use message queue instead)

---

## Analysis and Reporting

### Query Events

```python
import json
from datetime import datetime

def query_events(event_name=None, start_time=None, end_time=None):
    """Query telemetry events with filters."""
    with open("logs/telemetry.json") as f:
        events = json.load(f)
    
    filtered = events
    
    # Filter by event name
    if event_name:
        filtered = [e for e in filtered if e["name"] == event_name]
    
    # Filter by time range
    if start_time:
        start_ts = datetime.fromisoformat(start_time).timestamp()
        filtered = [e for e in filtered if e["timestamp"] >= start_ts]
    
    if end_time:
        end_ts = datetime.fromisoformat(end_time).timestamp()
        filtered = [e for e in filtered if e["timestamp"] <= end_ts]
    
    return filtered

# Usage
login_events = query_events(
    event_name="user_login",
    start_time="2026-04-20T00:00:00",
    end_time="2026-04-20T23:59:59"
)
print(f"Login events today: {len(login_events)}")
```

### Aggregate Metrics

```python
from collections import Counter
from datetime import datetime, timedelta

def generate_daily_report():
    """Generate daily telemetry summary."""
    with open("logs/telemetry.json") as f:
        events = json.load(f)
    
    # Filter to last 24 hours
    cutoff = (datetime.now() - timedelta(days=1)).timestamp()
    recent_events = [e for e in events if e["timestamp"] >= cutoff]
    
    # Count by event name
    event_counts = Counter(e["name"] for e in recent_events)
    
    # Count by user (if present)
    user_counts = Counter(
        e["payload"].get("username")
        for e in recent_events
        if "username" in e.get("payload", {})
    )
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_events": len(recent_events),
        "event_breakdown": dict(event_counts),
        "active_users": len(user_counts),
        "top_users": user_counts.most_common(10)
    }
    
    return report

# Usage
report = generate_daily_report()
print(json.dumps(report, indent=2))
```

### Export to CSV

```python
import csv
from datetime import datetime

def export_to_csv(output_file="telemetry_export.csv"):
    """Export telemetry events to CSV."""
    with open("logs/telemetry.json") as f:
        events = json.load(f)
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Event Name", "Payload JSON"])
        
        for event in events:
            timestamp = datetime.fromtimestamp(event["timestamp"]).isoformat()
            writer.writerow([
                timestamp,
                event["name"],
                json.dumps(event.get("payload", {}))
            ])
    
    print(f"Exported {len(events)} events to {output_file}")

# Usage
export_to_csv("telemetry_2026-04.csv")
```

---

## Performance Considerations

### Best-Effort Design

```python
# Telemetry failures NEVER affect application
try:
    events.append(event)
    if len(events) > TELEMETRY_MAX_EVENTS:
        events = events[-TELEMETRY_MAX_EVENTS:]
    _atomic_write_json(TELEMETRY_FILE, events)
except Exception:
    # Fail silently — telemetry must not affect app behavior
    pass
```

### High-Frequency Events

```python
# For high-frequency events, use batching
class BatchedTelemetry:
    def __init__(self, batch_size=100, flush_interval=10):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    def send_event(self, name, payload=None):
        self.batch.append({
            "name": name,
            "timestamp": time.time(),
            "payload": payload or {}
        })
        
        # Flush if batch full or interval elapsed
        if len(self.batch) >= self.batch_size or \
           time.time() - self.last_flush >= self.flush_interval:
            self.flush()
    
    def flush(self):
        if not self.batch:
            return
        
        # Write all events at once
        with open("logs/telemetry.json", 'a') as f:
            for event in self.batch:
                f.write(json.dumps(event) + "\n")
        
        self.batch = []
        self.last_flush = time.time()

# Usage
batched_telemetry = BatchedTelemetry()
for i in range(1000):
    batched_telemetry.send_event("high_freq_event", {"value": i})
```

---

## Privacy and Compliance

### PII Filtering

```python
def sanitize_payload(payload):
    """Remove PII from telemetry payloads."""
    sensitive_keys = ["password", "ssn", "credit_card", "api_key"]
    
    sanitized = payload.copy()
    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = "[REDACTED]"
    
    # Hash email addresses
    if "email" in sanitized:
        sanitized["email_hash"] = hashlib.sha256(
            sanitized["email"].encode()
        ).hexdigest()
        del sanitized["email"]
    
    return sanitized

# Usage
send_event("user_registered", sanitize_payload({
    "username": "admin",
    "email": "admin@example.com",  # Will be hashed
    "password": "secret123"         # Will be redacted
}))
```

### GDPR Compliance

```python
def delete_user_telemetry(username):
    """Delete all telemetry events for a user (GDPR right to erasure)."""
    with open("logs/telemetry.json") as f:
        events = json.load(f)
    
    # Filter out events for this user
    filtered_events = [
        e for e in events
        if e.get("payload", {}).get("username") != username
    ]
    
    _atomic_write_json("logs/telemetry.json", filtered_events)
    
    deleted_count = len(events) - len(filtered_events)
    print(f"Deleted {deleted_count} events for user {username}")

# Usage
delete_user_telemetry("admin")
```

### Consent Management

```python
from app.core.user_manager import UserManager

def check_telemetry_consent(username):
    """Check if user has consented to telemetry."""
    user_manager = UserManager()
    user_data = user_manager.get_user_data(username)
    return user_data.get("telemetry_consent", False)

def send_event_with_consent_check(username, event_name, payload):
    """Only send event if user has consented."""
    if check_telemetry_consent(username):
        payload["username"] = username
        send_event(event_name, payload)

# Usage
send_event_with_consent_check(
    "admin",
    "feature_used",
    {"feature": "image_generation"}
)
```

---

## Integration Examples

### With User Manager

```python
from app.core.telemetry import send_event
from app.core.user_manager import UserManager

user_manager = UserManager()

# Track authentication events
success, message = user_manager.authenticate("admin", "password123")
if success:
    send_event("user_login", {"username": "admin", "method": "password"})
else:
    send_event("login_failed", {"username": "admin", "reason": message})
```

### With AI Systems

```python
from app.core.telemetry import send_event
from app.core.ai_systems import AIPersona

persona = AIPersona()

# Track personality changes
old_trait = persona.personality_traits["friendliness"]
persona.adjust_personality("friendliness", 0.9)
send_event("personality_adjusted", {
    "trait": "friendliness",
    "old_value": old_trait,
    "new_value": 0.9
})
```

### With Image Generation

```python
from app.core.telemetry import send_event
from app.core.image_generator import ImageGenerator

generator = ImageGenerator()

# Track generation requests
start_time = time.time()
image_path, metadata = generator.generate(
    prompt="cyberpunk city at night",
    style="cyberpunk",
    backend="huggingface"
)
duration_ms = (time.time() - start_time) * 1000

send_event("image_generated", {
    "backend": "huggingface",
    "style": "cyberpunk",
    "duration_ms": duration_ms,
    "success": image_path is not None
})
```

---

## Monitoring and Alerting

### Real-Time Monitoring

```python
import threading
import time
from collections import deque

class TelemetryMonitor(threading.Thread):
    def __init__(self, alert_threshold=100):
        super().__init__(daemon=True)
        self.alert_threshold = alert_threshold
        self.recent_errors = deque(maxlen=100)
        self.running = True
    
    def run(self):
        last_position = 0
        
        while self.running:
            # Read new events
            with open("logs/telemetry.json") as f:
                events = json.load(f)
            
            # Process new events
            new_events = events[last_position:]
            for event in new_events:
                if event["name"] == "error":
                    self.recent_errors.append(event)
                    
                    # Alert if error rate exceeds threshold
                    if len(self.recent_errors) >= self.alert_threshold:
                        self.send_alert("High error rate detected")
            
            last_position = len(events)
            time.sleep(10)  # Check every 10 seconds
    
    def send_alert(self, message):
        print(f"ALERT: {message}")
        # Send email, Slack notification, etc.
    
    def stop(self):
        self.running = False

# Usage
monitor = TelemetryMonitor(alert_threshold=50)
monitor.start()
```

---

## Testing

### Unit Tests

```python
import unittest
import tempfile
import os
from app.core.telemetry import TelemetryManager, send_event

class TestTelemetry(unittest.TestCase):
    def setUp(self):
        # Use temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='.json'
        )
        self.temp_file.close()
        
        # Override telemetry file path
        os.environ["TELEMETRY_FILE"] = self.temp_file.name
        os.environ["TELEMETRY_ENABLED"] = "true"
    
    def tearDown(self):
        os.remove(self.temp_file.name)
    
    def test_send_event(self):
        """Test event logging."""
        send_event("test_event", {"key": "value"})
        
        with open(self.temp_file.name) as f:
            events = json.load(f)
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "test_event")
        self.assertEqual(events[0]["payload"]["key"], "value")
    
    def test_disabled_telemetry(self):
        """Test that events are not logged when disabled."""
        os.environ["TELEMETRY_ENABLED"] = "false"
        
        send_event("test_event", {"key": "value"})
        
        # File should not be created or modified
        # (Implementation detail: may create empty file)
```

---

## Configuration Examples

### Production Configuration

```bash
# .env (production)
TELEMETRY_ENABLED=true
TELEMETRY_FILE=/var/log/project-ai/telemetry.json
TELEMETRY_MAX_EVENTS=10000
```

### Development Configuration

```bash
# .env (development)
TELEMETRY_ENABLED=true
TELEMETRY_FILE=logs/telemetry_dev.json
TELEMETRY_MAX_EVENTS=500
```

### Disabled (Default)

```bash
# .env (telemetry disabled)
TELEMETRY_ENABLED=false
```

---

## Troubleshooting

### "PermissionError: [Errno 13] Permission denied"

```bash
# Ensure logs directory exists and is writable
mkdir -p logs
chmod 755 logs
```

### "JSONDecodeError: Expecting value"

```bash
# Corrupted telemetry file - reset it
echo "[]" > logs/telemetry.json
```

### High Disk Usage

```bash
# Reduce max events or implement rotation
export TELEMETRY_MAX_EVENTS=500  # Reduce from default 1000

# Or manually rotate logs
python -c "from scripts.rotate_telemetry import rotate_telemetry_file; rotate_telemetry_file()"
```

---

## Future Enhancements

1. **Structured Logging Integration**: Unify with Python logging module
2. **Real-Time Streaming**: Push events to external analytics (Elasticsearch, Prometheus)
3. **Event Schema Validation**: Enforce event structure with JSON schema
4. **Compression**: Gzip old telemetry logs automatically
5. **Multi-Format Export**: Support CSV, Parquet, Avro exports

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
