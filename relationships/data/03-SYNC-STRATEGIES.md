# Cloud Sync Strategies and Conflict Resolution

**Component:** Cloud Synchronization Architecture  
**Agent:** AGENT-058  
**Date:** 2026-04-20

---


## Navigation

**Location**: `relationships\data\03-SYNC-STRATEGIES.md`

**Parent**: [[relationships\data\README.md]]


## Overview

The CloudSyncManager provides encrypted bidirectional synchronization with automatic conflict resolution, device management, and failure recovery. This document details sync flows, conflict resolution strategies, and multi-device coordination. For encryption details, see [[02-ENCRYPTION-CHAINS.md|Encryption Chains]]. For data flow diagrams, see [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]].

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Cloud Sync Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Local State                     Cloud Storage             │
│  ┌────────────┐                 ┌────────────┐            │
│  │ User Data  │ ←─ Sync Flow ──→│ Encrypted  │            │
│  │ (JSON)     │                  │ Blob       │            │
│  └────────────┘                  └────────────┘            │
│        ↑                                ↑                   │
│        │                                │                   │
│  ┌────────────┐                 ┌────────────┐            │
│  │ Sync Meta  │                 │ Device     │            │
│  │ (local)    │                 │ Registry   │            │
│  └────────────┘                 └────────────┘            │
│        ↑                                                    │
│        │                                                    │
│  ┌────────────────────────────────────┐                   │
│  │     CloudSyncManager               │                   │
│  │  - Encryption (Fernet)             │  → [[02-ENCRYPTION-CHAINS.md|Encryption Chains]]
│  │  - Conflict Resolution             │  → [[../monitoring/06-error-tracking.md|Error Tracking]]
│  │  - Device ID Generation            │  → [[../security/01_security_system_overview.md|Security Overview]]
│  │  - Auto-sync Scheduler             │  → [[../configuration/10_default_values_relationships.md|Default Values]]
│  └────────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Sync Flow Patterns

### 1. Upload Flow (Local → Cloud)

**Trigger:** User data change, manual sync, auto-sync interval

```python
def sync_upload(self, username: str, data: dict) -> bool:
    """Upload encrypted user data to cloud."""
    
    # Step 1: Add metadata
    sync_data = {
        "username": username,
        "device_id": self.device_id,
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
    
    # Step 2: Encrypt (Fernet) (see [[02-ENCRYPTION-CHAINS.md|Encryption Chains]])
    encrypted_data = self.encrypt_data(sync_data)
    
    # Step 3: HTTP POST to cloud API
    response = requests.post(
        f"{self.cloud_sync_url}/upload",
        json={
            "username": username,
            "device_id": self.device_id,
            "encrypted_data": encrypted_data.hex(),
        },
        timeout=30,
    )
    
    # Step 4: Update sync metadata
    if response.status_code == 200:
        self.sync_metadata[username] = {
            "last_upload": datetime.now().isoformat(),
            "device_id": self.device_id,
        }
        self._save_sync_metadata()
        return True
    
    return False
```

**Sequence Diagram:**
```
Local System                CloudSyncManager           Cloud API
     |                             |                        |
     |--- modify data ------------>|                        |
     |                             |                        |
     |                             |--- add metadata -------|
     |                             |                        |
     |                             |--- encrypt (Fernet) ---|
     |                             |                        |
     |                             |--- POST /upload ------>|
     |                             |                        |
     |                             |<-- 200 OK -------------|
     |                             |                        |
     |                             |--- update metadata ----|
     |                             |                        |
     |<-- True (success) ----------|                        |
```

**Error Handling:**

See [[../monitoring/06-error-tracking.md|Error Tracking]] for comprehensive error logging and alerting.

```python
try:
    response = requests.post(..., timeout=30)
    if response.status_code == 200:
        return True
    else:
        logger.error("Upload failed: %s", response.text)
        return False
except requests.RequestException as e:
    logger.error("Network error: %s", e)
    return False  # Retry later
```

---

### 2. Download Flow (Cloud → Local)

**Trigger:** Login, explicit sync request, conflict resolution

See [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for decryption flow.

```python
def sync_download(self, username: str) -> dict | None:
    """Download and decrypt user data from cloud."""
    
    # Step 1: HTTP GET from cloud API
    response = requests.get(
        f"{self.cloud_sync_url}/download",
        params={
            "username": username,
            "device_id": self.device_id,
        },
        timeout=30,
    )
    
    # Step 2: Extract encrypted data
    if response.status_code == 200:
        data = response.json()
        encrypted_data = bytes.fromhex(data["encrypted_data"])
        
        # Step 3: Decrypt (Fernet) (see [[02-ENCRYPTION-CHAINS.md|Encryption Chains]])
        decrypted_data = self.decrypt_data(encrypted_data)
        
        # Step 4: Update sync metadata
        self.sync_metadata[username] = {
            "last_download": datetime.now().isoformat(),
            "device_id": self.device_id,
        }
        self._save_sync_metadata()
        
        return decrypted_data
    
    elif response.status_code == 404:
        return None  # No cloud data
    
    else:
        logger.error("Download failed: %s", response.text)
        return None
```

**Sequence Diagram:**
```
Local System                CloudSyncManager           Cloud API
     |                             |                        |
     |--- request sync ----------->|                        |
     |                             |                        |
     |                             |--- GET /download ----->|
     |                             |                        |
     |                             |<-- encrypted blob -----|
     |                             |                        |
     |                             |--- decrypt (Fernet) ---|
     |                             |                        |
     |                             |--- update metadata ----|
     |                             |                        |
     |<-- decrypted data ----------|                        |
```

**Status Codes:**
- `200 OK`: Data found and returned
- `404 Not Found`: No cloud data for user (normal on first upload)
- `401 Unauthorized`: Authentication failure
- `500 Server Error`: Cloud service error

---

### 3. Bidirectional Sync Flow (Most Complex)

**Trigger:** Auto-sync, login, manual sync

```python
def bidirectional_sync(self, username: str, local_data: dict) -> dict:
    """Sync with conflict resolution."""
    
    if not self.cloud_sync_url:
        return local_data  # No cloud configured
    
    # Step 1: Download cloud data
    cloud_data = self.sync_download(username)
    
    if cloud_data is None:
        # No cloud data → upload local
        self.sync_upload(username, local_data)
        return local_data
    
    # Step 2: Compare timestamps
    local_timestamp = local_data.get("timestamp")
    cloud_timestamp = cloud_data.get("timestamp")
    
    if local_timestamp and cloud_timestamp:
        local_dt = datetime.fromisoformat(local_timestamp)
        cloud_dt = datetime.fromisoformat(cloud_timestamp)
        
        # Step 3: Resolve conflict
        if local_dt >= cloud_dt:
            # Local is newer or same
            if local_dt > cloud_dt:
                self.sync_upload(username, local_data)
            return local_data
        else:
            # Cloud is newer
            resolved_data = cloud_data.get("data", cloud_data)
            return resolved_data
    
    # Step 4: Fallback conflict resolution
    resolved_data = self.resolve_conflict(local_data, cloud_data)
    if resolved_data == local_data:
        self.sync_upload(username, resolved_data)
    
    return resolved_data
```

**Decision Tree:**
```
Start Bidirectional Sync
   ↓
Download Cloud Data
   ↓
Cloud Data Exists?
   ├─ No → Upload Local → Return Local
   └─ Yes ↓
          Compare Timestamps
             ├─ Local >= Cloud
             │    ├─ Equal → Return Local (no upload)
             │    └─ Local Newer → Upload Local → Return Local
             └─ Cloud Newer
                  └─ Extract Cloud Data → Return Cloud
```

---

## Conflict Resolution Strategies

### Strategy 1: Last-Write-Wins (Current Implementation)

**Algorithm:**
```python
def resolve_conflict(self, local_data: dict, cloud_data: dict) -> dict:
    """Timestamp-based conflict resolution."""
    try:
        local_timestamp = datetime.fromisoformat(
            local_data.get("timestamp", "1970-01-01T00:00:00")
        )
        cloud_timestamp = datetime.fromisoformat(
            cloud_data.get("timestamp", "1970-01-01T00:00:00")
        )
        
        if local_timestamp >= cloud_timestamp:
            return local_data
        else:
            return cloud_data
    
    except Exception as e:
        logger.error("Conflict resolution error: %s", e)
        return local_data  # Default to local
```

**Properties:**
- ✅ **Simple:** Easy to understand and implement
- ✅ **Deterministic:** Same result on all devices
- ⚠️ **Data loss:** Older changes discarded
- ⚠️ **No merge:** Cannot combine changes from both sides

**Example Scenario:**
```
Device A (10:00): data = {"mood": 0.8, "interactions": 100}
Device B (10:05): data = {"mood": 0.6, "interactions": 100}

Sync Result: Device B wins (newer timestamp)
Final: {"mood": 0.6, "interactions": 100}
Lost: Device A's mood update (0.8)
```

---

### Strategy 2: Field-Level Merge (Future Enhancement)

**Algorithm (not implemented):**
```python
def merge_fields(self, local_data: dict, cloud_data: dict) -> dict:
    """Merge individual fields by timestamp."""
    merged = {}
    
    # For each field, choose newer timestamp
    all_fields = set(local_data.keys()) | set(cloud_data.keys())
    
    for field in all_fields:
        local_ts = local_data.get(f"{field}_timestamp")
        cloud_ts = cloud_data.get(f"{field}_timestamp")
        
        if local_ts and cloud_ts:
            if local_ts >= cloud_ts:
                merged[field] = local_data[field]
                merged[f"{field}_timestamp"] = local_ts
            else:
                merged[field] = cloud_data[field]
                merged[f"{field}_timestamp"] = cloud_ts
        elif field in local_data:
            merged[field] = local_data[field]
        else:
            merged[field] = cloud_data[field]
    
    return merged
```

**Example Scenario:**
```
Device A (10:00): {"mood": 0.8, "mood_ts": "10:00", "interactions": 100, "interactions_ts": "10:00"}
Device B (10:05): {"mood": 0.6, "mood_ts": "10:05", "interactions": 105, "interactions_ts": "10:05"}

Merge Result: {
    "mood": 0.6,  # Newer from Device B
    "interactions": 105,  # Newer from Device B
}
```

**Benefits:**
- ✅ **No data loss:** Preserves all updates
- ✅ **Fine-grained:** Field-level resolution
- ⚠️ **Complexity:** Requires per-field timestamps
- ⚠️ **Storage overhead:** Double metadata per field

---

### Strategy 3: Operational Transformation (Advanced)

**Concept:** Track operations instead of state

```python
# Example: Track increments instead of final values
operations = [
    {"op": "increment", "field": "interactions", "delta": 1, "ts": "10:00"},
    {"op": "set", "field": "mood", "value": 0.8, "ts": "10:01"},
]

# Replay operations in timestamp order on all devices
def apply_operations(initial_state, operations):
    state = initial_state.copy()
    for op in sorted(operations, key=lambda x: x["ts"]):
        if op["op"] == "increment":
            state[op["field"]] += op["delta"]
        elif op["op"] == "set":
            state[op["field"]] = op["value"]
    return state
```

**Benefits:**
- ✅ **No conflicts:** All operations commute
- ✅ **Eventual consistency:** All devices converge
- ⚠️ **Complex:** Requires operation log
- ⚠️ **Large logs:** Must prune old operations

---

## Device Management

### Device ID Generation

```python
def _generate_device_id(self) -> str:
    """Generate unique device identifier using SHA-256."""
    # Combine device characteristics
    device_info = (
        f"{platform.node()}-"      # Hostname
        f"{platform.system()}-"    # OS (Windows, Linux, Darwin)
        f"{platform.machine()}-"   # Architecture (AMD64, ARM64)
        f"{uuid.getnode()}"        # MAC address
    )
    
    # Hash to 16-character ID
    device_hash = hashlib.sha256(device_info.encode()).hexdigest()
    return device_hash[:16]
```

**Example Device IDs:**
```
Desktop (Windows):  "a1b2c3d4e5f6g7h8"
Laptop (Linux):     "x9y8z7w6v5u4t3s2"
Mobile (Android):   "m1n2o3p4q5r6s7t8"
```

**Properties:**
- ✅ **Stable:** Same ID across restarts
- ✅ **Unique:** Different per device
- ⚠️ **Linkable:** Can track user across devices (privacy concern)

**Privacy Enhancement (Future):**
```python
# Use user-specific salt to prevent cross-user tracking
device_id = hashlib.sha256(f"{device_info}-{username}".encode()).hexdigest()[:16]
```

---

### Device List Management

```python
def list_devices(self, username: str) -> list[dict]:
    """List all devices that have synced for a user."""
    
    response = requests.get(
        f"{self.cloud_sync_url}/devices",
        params={"username": username},
        timeout=30,
    )
    
    if response.status_code == 200:
        devices = response.json().get("devices", [])
        
        # Mark current device
        for device in devices:
            device["current"] = (device.get("device_id") == self.device_id)
        
        return devices
    
    return [{"device_id": self.device_id, "current": True}]
```

**Example Response:**
```json
[
  {
    "device_id": "a1b2c3d4e5f6g7h8",
    "device_name": "Desktop-PC",
    "last_sync": "2026-04-20T14:30:00",
    "current": true
  },
  {
    "device_id": "x9y8z7w6v5u4t3s2",
    "device_name": "Laptop",
    "last_sync": "2026-04-19T09:15:00",
    "current": false
  }
]
```

---

## Auto-Sync Management

### Enable Auto-Sync

See [[../configuration/10_default_values_relationships.md|Default Values]] for default interval configuration.

```python
def enable_auto_sync(self, interval: int = 300) -> None:
    """Enable automatic synchronization.
    
    Args:
        interval: Sync interval in seconds (default: 300 = 5 minutes)
    """
    self.auto_sync_enabled = True
    self.auto_sync_interval = interval
    logger.info("Auto-sync enabled with %ss interval", interval)
```

**Implementation (requires background thread):**
```python
import threading
import time

class AutoSyncThread(threading.Thread):
    def __init__(self, sync_manager, username, get_data_fn):
        super().__init__(daemon=True)
        self.sync_manager = sync_manager
        self.username = username
        self.get_data_fn = get_data_fn
        self.running = True
    
    def run(self):
        while self.running:
            time.sleep(self.sync_manager.auto_sync_interval)
            
            if self.sync_manager.auto_sync_enabled:
                try:
                    local_data = self.get_data_fn()
                    self.sync_manager.bidirectional_sync(
                        self.username, local_data
                    )
                except Exception as e:
                    logger.error("Auto-sync error: %s", e)

# Start auto-sync
sync_thread = AutoSyncThread(sync_manager, "user123", lambda: get_current_state())
sync_thread.start()
```

---

## Sync Metadata Management

### Metadata Schema

**File:** `data/sync_metadata.json` (see [[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] for atomic write details)

```json
{
  "user123": {
    "last_upload": "2026-04-20T14:30:00.123456",
    "last_download": "2026-04-20T14:25:00.987654",
    "device_id": "a1b2c3d4e5f6g7h8",
    "sync_count": 42,
    "last_conflict": "2026-04-19T10:00:00",
    "conflict_resolution": "local_won"
  }
}
```

### Update Pattern

```python
def _save_sync_metadata(self) -> None:
    """Atomically save sync metadata."""
    try:
        _atomic_write_json(self.sync_metadata_path, self.sync_metadata)
    except Exception as e:
        logger.error("Error saving sync metadata: %s", e)
```

---

## Failure Modes and Recovery

See [[../monitoring/06-error-tracking.md|Error Tracking]] for failure monitoring and [[04-BACKUP-RECOVERY.md|Backup & Recovery]] for data recovery strategies.

### Network Timeout

**Scenario:** Cloud API unreachable

```python
try:
    response = requests.post(..., timeout=30)
except requests.Timeout:
    logger.warning("Sync timeout, will retry later")
    return False
```

**Recovery:**
- Retry on next auto-sync interval
- Queue upload for background retry
- Gracefully degrade to local-only mode

---

### Encryption Key Mismatch

**Scenario:** Device has different FERNET_KEY (see [[../configuration/07_secrets_management_relationships.md|Secrets Management]])

```python
try:
    decrypted = self.cipher_suite.decrypt(encrypted_data)
except cryptography.fernet.InvalidToken:
    logger.error("Decryption failed - key mismatch?")
    return None
```

**Recovery:**
- Prompt user to verify FERNET_KEY (see [[../configuration/02_environment_manager_relationships.md|Environment Manager]])
- Check .env file consistency
- Re-sync from scratch if needed

---

### Cloud Data Corruption

**Scenario:** Invalid encrypted blob

```python
try:
    encrypted_data = bytes.fromhex(data["encrypted_data"])
    decrypted = self.decrypt_data(encrypted_data)
except (ValueError, json.JSONDecodeError):
    logger.error("Cloud data corrupted")
    return None
```

**Recovery:**
- Fall back to local data
- Upload local data to overwrite corrupted cloud data
- Alert user to potential data loss

---

### Timestamp Desync

**Scenario:** Device clock skewed

```python
# Detect large timestamp difference
cloud_ts = datetime.fromisoformat(cloud_data["timestamp"])
local_ts = datetime.fromisoformat(local_data["timestamp"])
skew = abs((cloud_ts - local_ts).total_seconds())

if skew > 86400:  # 1 day
    logger.warning("Large timestamp skew detected: %s seconds", skew)
    # Prompt user to check system clock
```

**Recovery:**
- Warn user about clock skew
- Use version numbers instead of timestamps (future)
- Manual conflict resolution UI

---

## Performance Optimization

See [[../monitoring/05-performance-monitoring.md|Performance Monitoring]] for sync performance metrics.

### Batch Sync

```python
def sync_batch(self, username: str, data_items: list[dict]) -> list[bool]:
    """Sync multiple items in single request."""
    results = []
    
    # Encrypt all items
    encrypted_items = [
        self.encrypt_data({
            "username": username,
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "data": item,
        })
        for item in data_items
    ]
    
    # Single HTTP request
    response = requests.post(
        f"{self.cloud_sync_url}/batch_upload",
        json={
            "username": username,
            "device_id": self.device_id,
            "items": [enc.hex() for enc in encrypted_items],
        },
        timeout=60,
    )
    
    if response.status_code == 200:
        results = response.json().get("results", [])
    
    return results
```

---

### Delta Sync (Future)

```python
def delta_sync(self, username: str, changes: dict) -> bool:
    """Sync only changed fields."""
    delta_data = {
        "username": username,
        "device_id": self.device_id,
        "timestamp": datetime.now().isoformat(),
        "changes": changes,  # {"mood": 0.8, "interactions": 105}
    }
    
    encrypted_delta = self.encrypt_data(delta_data)
    
    response = requests.post(
        f"{self.cloud_sync_url}/delta_upload",
        json={
            "username": username,
            "encrypted_delta": encrypted_delta.hex(),
        },
        timeout=30,
    )
    
    return response.status_code == 200
```

---

## Security Considerations

See [[../security/02_threat_models.md|Threat Models]] for comprehensive threat analysis and [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for security flows.

### Encryption in Transit

**Current:** HTTPS + Fernet (double encryption) (see [[02-ENCRYPTION-CHAINS.md|Encryption Chains]])

```
Data → Fernet encrypt → HTTPS → Cloud
                        (TLS 1.3)
```

**Threat Model:**

See [[../security/02_threat_models.md|Threat Models]] for complete threat analysis.

- ✅ Protected from network sniffing (HTTPS)
- ✅ Protected from cloud provider (Fernet)
- ⚠️ Vulnerable if FERNET_KEY compromised (see [[../configuration/07_secrets_management_relationships.md|Secrets Management]])

---

### Authentication

**Current:** No authentication (cloud API trusts all requests) (see [[../security/01_security_system_overview.md|Security Overview]] for authentication architecture)

**Future Enhancement:**
```python
def sync_upload(self, username: str, data: dict) -> bool:
    # Generate HMAC for authentication
    auth_token = hmac.new(
        self.api_key.encode(),
        f"{username}:{self.device_id}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    response = requests.post(
        f"{self.cloud_sync_url}/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={...},
        timeout=30,
    )
```

---

### Rate Limiting

**Current:** No rate limiting

**Future Enhancement:**
```python
class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def allow_request(self) -> bool:
        now = time.time()
        # Remove old requests
        self.requests = [t for t in self.requests if now - t < self.window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False

# Usage
rate_limiter = RateLimiter(max_requests=10, window=60)

def sync_upload(self, username: str, data: dict) -> bool:
    if not rate_limiter.allow_request():
        logger.warning("Rate limit exceeded, waiting...")
        time.sleep(1)
    
    # ... proceed with upload
```

---

## Testing Strategies

### Mock Cloud API

```python
class MockCloudAPI:
    def __init__(self):
        self.storage = {}
    
    def upload(self, username: str, device_id: str, encrypted_data: str):
        self.storage[username] = {
            "device_id": device_id,
            "encrypted_data": encrypted_data,
            "timestamp": datetime.now().isoformat(),
        }
        return {"status": "ok"}
    
    def download(self, username: str, device_id: str):
        if username in self.storage:
            return self.storage[username]
        return None

# Test
mock_api = MockCloudAPI()
sync_manager = CloudSyncManager(cloud_sync_url="http://mock")
sync_manager.sync_upload("user123", {"data": "test"})
downloaded = sync_manager.sync_download("user123")
assert downloaded["data"] == "test"
```

---

### Conflict Simulation

```python
def test_conflict_resolution():
    sync_manager = CloudSyncManager()
    
    # Device A: older data
    local_data = {
        "timestamp": "2026-04-20T10:00:00",
        "mood": 0.8,
    }
    
    # Device B: newer data (in cloud)
    cloud_data = {
        "timestamp": "2026-04-20T10:05:00",
        "mood": 0.6,
    }
    
    resolved = sync_manager.resolve_conflict(local_data, cloud_data)
    
    assert resolved == cloud_data
    assert resolved["mood"] == 0.6
```

---

## Related Documentation

### Data Layer Documentation
- **[[00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]]** - Complete architecture
- **[[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]]** - Persistence mechanisms
- **[[02-ENCRYPTION-CHAINS.md|Encryption Chains]]** - Fernet encryption details
- **[[04-BACKUP-RECOVERY.md|Backup & Recovery]]** - Data recovery strategies

### Cross-System Documentation
- **[[../security/01_security_system_overview.md|Security Overview]]** - Authentication architecture
- **[[../security/02_threat_models.md|Threat Models]]** - Threat analysis
- **[[../security/06_data_flow_diagrams.md|Data Flow Diagrams]]** - Security data flows
- **[[../monitoring/05-performance-monitoring.md|Performance Monitoring]]** - Sync performance metrics
- **[[../monitoring/06-error-tracking.md|Error Tracking]]** - Error logging and recovery
- **[[../configuration/02_environment_manager_relationships.md|Environment Manager]]** - FERNET_KEY configuration
- **[[../configuration/07_secrets_management_relationships.md|Secrets Management]]** - Key storage and rotation
- **[[../configuration/10_default_values_relationships.md|Default Values]]** - Auto-sync defaults

---

**Document Version:** 1.0.0  
**Related:** [[02-ENCRYPTION-CHAINS.md|Encryption Chains]]  
**Next:** [[04-BACKUP-RECOVERY.md|Backup & Recovery]]


---

## See Also

### Related Source Documentation

- **07 Cloud Sync Model**: [[source-docs\data-models\07-cloud-sync-model.md]]
- **Documentation Index**: [[source-docs\data-models\README.md]]
