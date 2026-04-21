# Cloud Synchronization Data Model

**Module**: `src/app/core/cloud_sync.py` [[src/app/core/cloud_sync.py]]  
**Storage**: `data/sync_metadata.json`  
**Persistence**: JSON with encrypted payloads  
**Schema Version**: 1.0

---

## Overview

The Cloud Synchronization system enables encrypted bidirectional sync of user data across devices with automatic conflict resolution, device identification, and metadata tracking.

### Key Features

- **Encrypted Sync**: Fernet-based payload encryption
- **Device Identification**: SHA-256 hashing of hardware characteristics
- **Conflict Resolution**: Last-write-wins with metadata tracking
- **Bidirectional Sync**: Upload and download with delta detection
- **Auto-Sync**: Configurable automatic synchronization
- **Offline Support**: Queue operations when offline

---

## Schema Structure

### Sync Metadata Document

**File**: `data/sync_metadata.json`

```json
{
  "device_id": "a3f7b8c2d1e4f5g6",
  "last_sync": "2024-01-20T14:30:00Z",
  "sync_conflicts": [
    {
      "file": "users.json",
      "local_hash": "abc123...",
      "remote_hash": "def456...",
      "resolved": false,
      "detected_at": "2024-01-20T14:35:00Z"
    }
  ],
  "sync_history": [
    {
      "sync_id": "sync_001",
      "timestamp": "2024-01-20T14:30:00Z",
      "direction": "upload",
      "files_synced": ["users.json", "ai_persona/state.json"],
      "bytes_transferred": 15240,
      "duration_ms": 450,
      "status": "success"
    }
  ],
  "pending_uploads": ["memory/knowledge.json"],
  "pending_downloads": [],
  "sync_errors": []
}
```

### Cloud Sync Payload

**Encrypted Format** (Fernet cipher):

```json
{
  "username": "alice",
  "device_id": "a3f7b8c2d1e4f5g6",
  "timestamp": "2024-01-20T14:30:00Z",
  "checksum": "sha256:abc123...",
  "data": {
    "users": {...},
    "ai_persona": {...},
    "memory": {...}
  },
  "metadata": {
    "app_version": "2.0.0",
    "sync_version": "1.0",
    "compression": false
  }
}
```

---

## Field Specifications

### Sync Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | string | Yes | Unique device identifier (16-char hash) |
| `last_sync` | datetime | No | Last successful sync timestamp |
| `sync_conflicts` | array | Yes | List of unresolved conflicts |
| `sync_history` | array | Yes | Recent sync operations (last 100) |
| `pending_uploads` | array | Yes | Files queued for upload |
| `pending_downloads` | array | Yes | Files queued for download |
| `sync_errors` | array | Yes | Recent error log |

### Sync History Entry

| Field | Type | Description |
|-------|------|-------------|
| `sync_id` | string | Unique sync operation ID |
| `timestamp` | datetime | Sync start time |
| `direction` | string | "upload", "download", or "bidirectional" |
| `files_synced` | array | List of synced files |
| `bytes_transferred` | integer | Total bytes uploaded/downloaded |
| `duration_ms` | float | Operation duration in milliseconds |
| `status` | string | "success", "failure", "partial" |

---

## Device Identification

### Device ID Generation

```python
import hashlib
import platform
import uuid

def _generate_device_id(self) -> str:
    """Generate unique device identifier using SHA-256."""
    device_info = f"{platform.node()}-{platform.system()}-{platform.machine()}-{uuid.getnode()}"
    device_hash = hashlib.sha256(device_info.encode()).hexdigest()
    return device_hash[:16]  # Use first 16 chars
```

**Components**:
- `platform.node()`: Computer hostname
- `platform.system()`: OS name (Windows, Linux, Darwin)
- `platform.machine()`: CPU architecture (x86_64, ARM64)
- `uuid.getnode()`: MAC address (48-bit integer)

**Example Device IDs**:
- Desktop: `a3f7b8c2d1e4f5g6`
- Laptop: `b4g8c9d2e5f6g7h8`
- Mobile: `c5h9d0e3f7g8h9i0`

---

## Encryption System

### Payload Encryption

```python
from cryptography.fernet import Fernet

def encrypt_data(self, data: dict[str, Any]) -> bytes:
    """Encrypt sync payload with Fernet."""
    json_data = json.dumps(data)
    encrypted_data = self.cipher_suite.encrypt(json_data.encode())
    return encrypted_data

def decrypt_data(self, encrypted_data: bytes) -> dict[str, Any]:
    """Decrypt sync payload."""
    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())
```

### Checksum Verification

```python
def _calculate_checksum(self, data: dict) -> str:
    """Calculate SHA-256 checksum of data."""
    json_str = json.dumps(data, sort_keys=True)
    return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"

def verify_checksum(self, data: dict, expected_checksum: str) -> bool:
    """Verify data integrity via checksum."""
    calculated = self._calculate_checksum(data)
    return calculated == expected_checksum
```

---

## Sync Operations

### Upload Data

```python
def sync_upload(self, username: str, data: dict[str, Any]) -> bool:
    """Upload user data to cloud with encryption."""
    if not self.cloud_sync_url:
        logger.warning("Cloud sync URL not configured")
        return False
    
    try:
        # Prepare sync payload
        sync_data = {
            "username": username,
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "checksum": self._calculate_checksum(data),
            "data": data,
            "metadata": {
                "app_version": "2.0.0",
                "sync_version": "1.0",
                "compression": False
            }
        }
        
        # Encrypt payload
        encrypted_payload = self.encrypt_data(sync_data)
        
        # Upload to cloud
        response = requests.post(
            f"{self.cloud_sync_url}/sync/upload",
            data=encrypted_payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=30
        )
        
        if response.status_code == 200:
            self._log_sync_success("upload", data.keys(), len(encrypted_payload))
            return True
        else:
            self._log_sync_error("upload", f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error("Upload error: %s", e)
        self._log_sync_error("upload", str(e))
        return False
```

### Download Data

```python
def sync_download(self, username: str) -> dict[str, Any] | None:
    """Download and decrypt user data from cloud."""
    if not self.cloud_sync_url:
        logger.warning("Cloud sync URL not configured")
        return None
    
    try:
        # Request data from cloud
        response = requests.get(
            f"{self.cloud_sync_url}/sync/download",
            params={"username": username, "device_id": self.device_id},
            timeout=30
        )
        
        if response.status_code == 200:
            # Decrypt payload
            encrypted_data = response.content
            sync_data = self.decrypt_data(encrypted_data)
            
            # Verify checksum
            if not self.verify_checksum(sync_data["data"], sync_data["checksum"]):
                raise ValueError("Checksum verification failed")
            
            self._log_sync_success("download", sync_data["data"].keys(), len(encrypted_data))
            return sync_data["data"]
        else:
            self._log_sync_error("download", f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        logger.error("Download error: %s", e)
        self._log_sync_error("download", str(e))
        return None
```

---

## Conflict Resolution

### Conflict Detection

```python
def detect_conflicts(self, local_data: dict, remote_data: dict) -> list[dict]:
    """Detect conflicts between local and remote data."""
    conflicts = []
    
    for key in set(local_data.keys()) | set(remote_data.keys()):
        if key in local_data and key in remote_data:
            local_hash = self._calculate_checksum(local_data[key])
            remote_hash = self._calculate_checksum(remote_data[key])
            
            if local_hash != remote_hash:
                conflicts.append({
                    "file": key,
                    "local_hash": local_hash,
                    "remote_hash": remote_hash,
                    "resolved": False,
                    "detected_at": datetime.now().isoformat()
                })
    
    return conflicts
```

### Conflict Resolution (Last-Write-Wins)

```python
def resolve_conflict(self, conflict: dict, local_data: dict, remote_data: dict) -> dict:
    """Resolve conflict using last-write-wins strategy."""
    file_key = conflict["file"]
    
    # Get timestamps (if available)
    local_time = local_data.get(file_key, {}).get("updated_at", "1970-01-01T00:00:00Z")
    remote_time = remote_data.get(file_key, {}).get("updated_at", "1970-01-01T00:00:00Z")
    
    # Choose newer version
    if remote_time > local_time:
        logger.info("Conflict resolved: Using remote version for %s", file_key)
        return remote_data[file_key]
    else:
        logger.info("Conflict resolved: Using local version for %s", file_key)
        return local_data[file_key]
```

---

## Auto-Sync System

### Auto-Sync Configuration

```python
def enable_auto_sync(self, interval_seconds: int = 300):
    """Enable automatic synchronization every N seconds."""
    self.auto_sync_enabled = True
    self.auto_sync_interval = interval_seconds
    self._save_sync_metadata()
    
    # Start background sync thread (in production, use scheduler)
    logger.info("Auto-sync enabled (interval: %d seconds)", interval_seconds)

def disable_auto_sync(self):
    """Disable automatic synchronization."""
    self.auto_sync_enabled = False
    self._save_sync_metadata()
    logger.info("Auto-sync disabled")
```

### Background Sync (Conceptual)

```python
import threading
import time

def _background_sync_loop(self, username: str):
    """Background thread for periodic sync (conceptual)."""
    while self.auto_sync_enabled:
        try:
            # Perform bidirectional sync
            self.bidirectional_sync(username)
        except Exception as e:
            logger.error("Auto-sync error: %s", e)
        
        # Sleep until next interval
        time.sleep(self.auto_sync_interval)
```

---

## Usage Examples

### Manual Sync

```python
from app.core.cloud_sync import CloudSyncManager

sync_manager = CloudSyncManager(data_dir="data")

# Upload user data
user_data = {
    "users": load_users(),
    "ai_persona": load_persona_state(),
    "memory": load_memory()
}
success = sync_manager.sync_upload("alice", user_data)

# Download user data
remote_data = sync_manager.sync_download("alice")
if remote_data:
    merge_data(remote_data)
```

### Bidirectional Sync

```python
def bidirectional_sync(self, username: str) -> bool:
    """Perform bidirectional sync with conflict resolution."""
    # 1. Get local data
    local_data = self._collect_local_data()
    
    # 2. Download remote data
    remote_data = self.sync_download(username)
    if not remote_data:
        # No remote data, just upload
        return self.sync_upload(username, local_data)
    
    # 3. Detect conflicts
    conflicts = self.detect_conflicts(local_data, remote_data)
    
    # 4. Resolve conflicts
    merged_data = local_data.copy()
    for conflict in conflicts:
        resolved = self.resolve_conflict(conflict, local_data, remote_data)
        merged_data[conflict["file"]] = resolved
    
    # 5. Upload merged data
    return self.sync_upload(username, merged_data)
```

### Enable Auto-Sync

```python
# Enable auto-sync every 5 minutes
sync_manager.enable_auto_sync(interval_seconds=300)

# Later: disable auto-sync
sync_manager.disable_auto_sync()
```

---

## Sync History & Analytics

### Sync Statistics

```python
def get_sync_statistics(self) -> dict:
    """Get sync statistics and metrics."""
    history = self.sync_metadata.get("sync_history", [])
    
    total_syncs = len(history)
    successful_syncs = sum(1 for h in history if h["status"] == "success")
    failed_syncs = sum(1 for h in history if h["status"] == "failure")
    
    total_bytes = sum(h.get("bytes_transferred", 0) for h in history)
    avg_duration = sum(h.get("duration_ms", 0) for h in history) / total_syncs if total_syncs > 0 else 0
    
    return {
        "total_syncs": total_syncs,
        "successful_syncs": successful_syncs,
        "failed_syncs": failed_syncs,
        "success_rate": successful_syncs / total_syncs if total_syncs > 0 else 0,
        "total_bytes_transferred": total_bytes,
        "average_duration_ms": avg_duration,
        "last_sync": self.sync_metadata.get("last_sync")
    }
```

---

## Security Considerations

### Encryption Key Management

```bash
# .env file
FERNET_KEY=<base64-encoded-32-byte-key>
CLOUD_SYNC_URL=https://sync.example.com
```

### Transport Security

- **HTTPS Only**: Enforce TLS 1.2+ for all sync operations
- **Certificate Pinning**: Validate server certificate
- **Timeout Protection**: 30-second timeout for network operations

### Data Privacy

- **End-to-End Encryption**: Server never sees plaintext data
- **Device Isolation**: Each device has unique ID
- **Audit Trail**: All sync operations logged

---

## Performance Considerations

### Delta Sync (Future Enhancement)

```python
def delta_sync(self, username: str) -> bool:
    """Sync only changed files (delta sync)."""
    # 1. Get file hashes from server
    remote_hashes = self._get_remote_file_hashes(username)
    
    # 2. Calculate local hashes
    local_hashes = self._calculate_local_file_hashes()
    
    # 3. Identify changed files
    changed_files = {
        key: local_data[key]
        for key, hash_val in local_hashes.items()
        if hash_val != remote_hashes.get(key)
    }
    
    # 4. Upload only changed files
    return self.sync_upload(username, changed_files)
```

### Compression

```python
import gzip

def _compress_payload(self, data: dict) -> bytes:
    """Compress data before encryption."""
    json_data = json.dumps(data).encode()
    return gzip.compress(json_data, compresslevel=6)

def _decompress_payload(self, compressed: bytes) -> dict:
    """Decompress data after decryption."""
    json_data = gzip.decompress(compressed)
    return json.loads(json_data.decode())
```

---

## Testing Strategy

### Unit Tests

```python
def test_device_id_generation():
    sync1 = CloudSyncManager(data_dir="data")
    sync2 = CloudSyncManager(data_dir="data")
    
    # Same device should generate same ID
    assert sync1.device_id == sync2.device_id

def test_encryption_roundtrip():
    sync = CloudSyncManager(data_dir="data")
    
    data = {"test": "value"}
    encrypted = sync.encrypt_data(data)
    decrypted = sync.decrypt_data(encrypted)
    
    assert decrypted == data

def test_conflict_detection():
    sync = CloudSyncManager(data_dir="data")
    
    local = {"file1": {"data": "v1"}}
    remote = {"file1": {"data": "v2"}}
    
    conflicts = sync.detect_conflicts(local, remote)
    assert len(conflicts) == 1
    assert conflicts[0]["file"] == "file1"
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `data_persistence.py` | Provides encryption primitives |
| `user_manager.py` | Syncs user profiles across devices |
| `ai_systems.py` | Syncs persona and memory state |
| `telemetry.py` | Logs sync operations |

---

## Future Enhancements

1. **Delta Sync**: Only sync changed files
2. **Compression**: gzip payloads before encryption
3. **Multi-Device Coordination**: Prevent concurrent writes
4. **Offline Queue**: Persist operations when offline
5. **Cloud Backends**: Support AWS S3, Azure Blob, Google Cloud Storage

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/cloud_sync.py]]
