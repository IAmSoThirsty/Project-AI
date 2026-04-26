---
title: Save Points API
category: api
layer: api-layer
audience: [integrator, maintainer, expert]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md, 02-FASTAPI-MAIN-ROUTES.md]
time_estimate: 20min
last_updated: 2025-06-09
version: 1.0.0
---

# Save Points API

## Purpose

The Save Points API provides **time-travel state management** for Project-AI. Users can create manual checkpoints or rely on automatic 15-minute snapshots, then restore to any previous state.

**File**: `api/save_points_routes.py` (91 lines)  
**Prefix**: `/api/savepoints`  
**Backend**: `project_ai.save_points` module  
**Auto-save**: 15-minute intervals (background service)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT REQUEST                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Router (/api/savepoints)               │
│  • POST /create       → SavePointsManager.create_user_save()│
│  • GET /list          → SavePointsManager.list_save_points()│
│  • POST /restore/{id} → SavePointsManager.restore_save_point()│
│  • DELETE /delete/{id}→ SavePointsManager.delete_save_point()│
│  • GET /auto/status   → AutoSaveService.get_stats()         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 SavePointsManager                           │
│  • Snapshot: Compress data/, config/ → .tar.gz              │
│  • Metadata: Timestamp, user/auto, custom metadata          │
│  • Storage: save_points/ directory                          │
│  • Restore: Extract + overwrite current state               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│            AutoSaveService (Background Task)                │
│  • Interval: 15 minutes                                     │
│  • Lifecycle: start_auto_save() / stop_auto_save()          │
│  • Naming: auto_YYYYMMDD_HHMMSS                             │
│  • Retention: Configurable (default: unlimited)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Endpoints

### 1. Create Save Point - `POST /api/savepoints/create`

**Purpose**: Create user-initiated save point

**Request**:
```bash
curl -X POST http://localhost:8001/api/savepoints/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "before-major-config-change",
    "metadata": {
      "reason": "Testing new AI model",
      "user": "admin",
      "git_commit": "abc123"
    }
  }'
```

**Request Schema**:
```python
class CreateSaveRequest(BaseModel):
    name: str  # Save point identifier
    metadata: dict | None = None  # Optional metadata
```

**Response** (Success):
```json
{
  "success": true,
  "save_point": {
    "id": "user_before-major-config-change_20250609_143025",
    "name": "before-major-config-change",
    "timestamp": "2025-06-09T14:30:25.123456",
    "type": "user",
    "size_bytes": 5242880,
    "metadata": {
      "reason": "Testing new AI model",
      "user": "admin",
      "git_commit": "abc123"
    },
    "path": "save_points/user_before-major-config-change_20250609_143025.tar.gz"
  }
}
```

**Response** (Error):
```json
{
  "detail": "Error creating save point: Permission denied"
}
```

**Status Codes**:
- `200 OK` - Save point created
- `500 Internal Server Error` - Creation failed (disk space, permissions, etc.)

**Snapshot Contents**:
```
save_points/user_<name>_<timestamp>.tar.gz
├── data/
│   ├── ai_persona/state.json
│   ├── memory/knowledge.json
│   ├── learning_requests/requests.json
│   └── users.json
├── config/
│   └── command_override_config.json
└── metadata.json
```

**Use Cases**:
- Before major configuration changes
- After successful training/learning
- Integration checkpoints
- Rollback-safe experimentation

---

### 2. List Save Points - `GET /api/savepoints/list`

**Purpose**: Retrieve all save points (user + auto)

**Request**:
```bash
curl http://localhost:8001/api/savepoints/list
```

**Response**:
```json
{
  "save_points": [
    {
      "id": "auto_20250609_140000",
      "name": "auto_20250609_140000",
      "timestamp": "2025-06-09T14:00:00.000000",
      "type": "auto",
      "size_bytes": 4194304,
      "metadata": {
        "auto_save": true,
        "interval": "15min"
      },
      "path": "save_points/auto_20250609_140000.tar.gz"
    },
    {
      "id": "user_before-major-config-change_20250609_143025",
      "name": "before-major-config-change",
      "timestamp": "2025-06-09T14:30:25.123456",
      "type": "user",
      "size_bytes": 5242880,
      "metadata": {
        "reason": "Testing new AI model",
        "user": "admin"
      },
      "path": "save_points/user_before-major-config-change_20250609_143025.tar.gz"
    }
  ],
  "total": 2,
  "total_size_bytes": 9437184
}
```

**Response Fields**:
- `id` (str) - Unique save point identifier
- `name` (str) - Human-readable name
- `timestamp` (str) - ISO 8601 timestamp
- `type` (str) - "user" or "auto"
- `size_bytes` (int) - Archive size
- `metadata` (dict) - Custom metadata
- `path` (str) - File system path

**Sorting**: Chronological (newest first)

**Use Cases**:
- Save point browser UI
- Backup verification
- Disk space monitoring
- Restore point selection

---

### 3. Restore Save Point - `POST /api/savepoints/restore/{save_id}`

**Purpose**: Restore system state from save point

**⚠️ WARNING**: This operation **overwrites current state**. Create a save point first!

**Request**:
```bash
# ALWAYS create save point before restoring
curl -X POST http://localhost:8001/api/savepoints/create \
  -H "Content-Type: application/json" \
  -d '{"name": "before-restore", "metadata": {}}'

# Then restore
curl -X POST http://localhost:8001/api/savepoints/restore/user_before-major-config-change_20250609_143025
```

**Response** (Success):
```json
{
  "success": true,
  "message": "Restored to save point: user_before-major-config-change_20250609_143025",
  "restored": {
    "id": "user_before-major-config-change_20250609_143025",
    "timestamp": "2025-06-09T14:30:25.123456",
    "files_restored": [
      "data/ai_persona/state.json",
      "data/memory/knowledge.json",
      "data/users.json"
    ]
  }
}
```

**Response** (Not Found):
```json
{
  "detail": "Save point not found"
}
```

**Response** (Error):
```json
{
  "detail": "Error during restore: Corrupted archive"
}
```

**Status Codes**:
- `200 OK` - Restore completed
- `404 Not Found` - Save point doesn't exist
- `500 Internal Server Error` - Restore failed (corrupted archive, permission denied)

**Restore Process**:
1. **Validate**: Check save point exists and is readable
2. **Extract**: Decompress .tar.gz to temporary directory
3. **Backup**: Create emergency backup of current state
4. **Overwrite**: Copy extracted files to data/ and config/
5. **Verify**: Check critical files (users.json, state.json)
6. **Cleanup**: Remove temporary files

**Recovery from Failed Restore**:
```bash
# Emergency backup is in save_points/emergency_backup_<timestamp>.tar.gz
curl -X POST http://localhost:8001/api/savepoints/restore/emergency_backup_20250609_144530
```

**Use Cases**:
- Rollback after failed configuration
- Time-travel debugging
- Disaster recovery
- A/B testing state variations

---

### 4. Delete Save Point - `DELETE /api/savepoints/delete/{save_id}`

**Purpose**: Delete user save point (auto saves cannot be deleted via API)

**Request**:
```bash
curl -X DELETE http://localhost:8001/api/savepoints/delete/user_before-major-config-change_20250609_143025
```

**Response** (Success):
```json
{
  "success": true,
  "message": "Deleted save point: user_before-major-config-change_20250609_143025",
  "freed_bytes": 5242880
}
```

**Response** (Error):
```json
{
  "detail": "Save point not found or cannot be deleted"
}
```

**Status Codes**:
- `200 OK` - Save point deleted
- `404 Not Found` - Save point doesn't exist OR is auto-save (protected)
- `500 Internal Server Error` - Deletion failed (file locked, permissions)

**Protection Rules**:
- ✅ User save points: Can be deleted
- ❌ Auto save points: Cannot be deleted via API (require manual file deletion)
- ❌ Emergency backups: Cannot be deleted via API

**Use Cases**:
- Disk space cleanup
- Remove obsolete checkpoints
- Housekeeping after successful changes

---

### 5. Auto-Save Status - `GET /api/savepoints/auto/status`

**Purpose**: Get auto-save service statistics

**Request**:
```bash
curl http://localhost:8001/api/savepoints/auto/status
```

**Response**:
```json
{
  "enabled": true,
  "interval_minutes": 15,
  "next_save_in_seconds": 420,
  "last_save": {
    "timestamp": "2025-06-09T14:00:00.000000",
    "id": "auto_20250609_140000",
    "success": true
  },
  "total_auto_saves": 12,
  "total_size_bytes": 50331648,
  "uptime_seconds": 3600,
  "save_history": [
    {
      "timestamp": "2025-06-09T14:00:00.000000",
      "id": "auto_20250609_140000",
      "duration_seconds": 2.5,
      "size_bytes": 4194304
    },
    {
      "timestamp": "2025-06-09T13:45:00.000000",
      "id": "auto_20250609_134500",
      "duration_seconds": 2.3,
      "size_bytes": 4194304
    }
  ]
}
```

**Use Cases**:
- Monitoring dashboard
- Auto-save health check
- Disk usage prediction
- Performance monitoring

---

## Auto-Save Service

### Lifecycle Management

**Startup Hook** (in `api/main.py`):
```python
@app.on_event("startup")
async def startup_auto_save():
    """Start auto-save service on app startup"""
    await start_auto_save()
    print("[OK] Auto-save service started (15-min intervals)")
```

**Shutdown Hook**:
```python
@app.on_event("shutdown")
async def shutdown_auto_save():
    """Stop auto-save service on app shutdown"""
    await stop_auto_save()
    print("[OK] Auto-save service stopped")
```

### Configuration

```python
# project_ai/save_points.py
AUTO_SAVE_INTERVAL = timedelta(minutes=15)  # Save every 15 minutes
MAX_AUTO_SAVES = 20  # Rotate after 20 saves (5 hours)
AUTO_SAVE_RETENTION = timedelta(days=7)  # Delete saves older than 7 days
```

### Automatic Rotation

Auto-saves are automatically rotated:
- **Retention**: 7 days by default
- **Max count**: 20 saves (oldest deleted first)
- **Naming**: `auto_YYYYMMDD_HHMMSS.tar.gz`

### Manual Control

```python
from project_ai.save_points import get_auto_save_service

# Stop auto-save temporarily
service = get_auto_save_service()
await service.stop()

# Start auto-save
await service.start()

# Force immediate save
await service.force_save()
```

---

## Data Model

### SavePoint Structure

```python
{
  "id": "user_<name>_<timestamp>",  # Unique identifier
  "name": "human-readable-name",    # User-provided or auto-generated
  "timestamp": "2025-06-09T14:30:25.123456",  # ISO 8601
  "type": "user" | "auto",          # Creation method
  "size_bytes": 5242880,            # Archive size
  "metadata": {                     # Custom metadata
    "reason": "string",
    "user": "string",
    "git_commit": "string",
    "auto_save": bool,
    "interval": "15min"
  },
  "path": "save_points/..."         # File system path
}
```

### Archive Contents

```
<save_id>.tar.gz
├── data/                          # All persisted state
│   ├── ai_persona/state.json
│   ├── memory/
│   │   ├── knowledge.json
│   │   └── conversations.json
│   ├── learning_requests/requests.json
│   ├── command_override_config.json
│   └── users.json
├── config/                        # Configuration files
│   └── app_config.json
└── metadata.json                  # Save point metadata
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Permission denied` | Insufficient file permissions | Check `save_points/` directory permissions |
| `Disk space` | Out of disk space | Delete old save points, free disk space |
| `Corrupted archive` | Incomplete/damaged .tar.gz | Restore from previous save point |
| `Save point not found` | Invalid ID or deleted file | Check `/list` for available save points |
| `Restore failed` | File conflicts or locked files | Ensure no processes are accessing data files |

### Error Response Format

```json
{
  "detail": "Error creating save point: Disk space full"
}
```

**HTTP Status Codes**:
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Save point doesn't exist
- `500 Internal Server Error` - Operation failed

---

## Security Considerations

### Access Control

- **User saves**: Require authentication (future enhancement)
- **Auto saves**: System-initiated, no auth required
- **Restore**: Requires admin privileges (future enhancement)
- **Delete**: Requires owner or admin (future enhancement)

### Data Protection

- **Encryption**: Save points are **not encrypted** by default
  - Recommendation: Enable Fernet encryption for sensitive data
  - Implementation: Wrap `SavePointsManager` with encryption layer

- **Backup integrity**: SHA-256 checksums in metadata.json (future enhancement)

### Rate Limiting

```python
# Recommended rate limits
CREATE_RATE_LIMIT = "10 per hour"  # Prevent abuse
RESTORE_RATE_LIMIT = "5 per hour"  # Destructive operation
DELETE_RATE_LIMIT = "20 per hour"  # Housekeeping
```

---

## Performance

### Creation Time

| Data Size | Compression Time | Total Time |
|-----------|------------------|------------|
| 10 MB | 0.5s | 1s |
| 50 MB | 2s | 3s |
| 100 MB | 5s | 7s |
| 500 MB | 25s | 30s |

**Factors**:
- CPU: Gzip compression is CPU-bound
- I/O: Sequential reads from data/
- Compression level: Default is 6 (balance speed/size)

### Restore Time

| Archive Size | Extraction Time | Total Time |
|--------------|-----------------|------------|
| 10 MB | 0.3s | 0.5s |
| 50 MB | 1.5s | 2s |
| 100 MB | 3s | 4s |
| 500 MB | 15s | 20s |

**Factors**:
- I/O: Sequential writes to data/
- Validation: File integrity checks
- Verification: Critical file existence

### Disk Space

- **Per save point**: 5-50 MB (depends on state size)
- **20 auto-saves**: 100 MB - 1 GB
- **Compression ratio**: Typically 70-80% reduction

**Monitoring**:
```bash
# Check disk usage
du -sh save_points/

# List by size
ls -lhS save_points/
```

---

## Integration Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8001/api/savepoints"

# Create save point
response = requests.post(f"{BASE_URL}/create", json={
    "name": "before-experiment",
    "metadata": {"experiment": "model-tuning-v2"}
})
save_id = response.json()["save_point"]["id"]
print(f"Created: {save_id}")

# Run risky operation
try:
    risky_operation()
except Exception as e:
    # Restore on failure
    requests.post(f"{BASE_URL}/restore/{save_id}")
    print("Restored to checkpoint")

# Success - delete checkpoint
requests.delete(f"{BASE_URL}/delete/{save_id}")
```

### Bash Script

```bash
#!/bin/bash
# safe-config-update.sh

API="http://localhost:8001/api/savepoints"

# 1. Create checkpoint
SAVE_RESPONSE=$(curl -s -X POST "$API/create" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"before-config-update\", \"metadata\": {}}")

SAVE_ID=$(echo "$SAVE_RESPONSE" | jq -r '.save_point.id')
echo "Checkpoint: $SAVE_ID"

# 2. Apply configuration
if ! update-config.sh; then
  echo "Config update failed - restoring..."
  curl -X POST "$API/restore/$SAVE_ID"
  exit 1
fi

# 3. Verify
if verify-system.sh; then
  echo "Success - deleting checkpoint"
  curl -X DELETE "$API/delete/$SAVE_ID"
else
  echo "Verification failed - restoring..."
  curl -X POST "$API/restore/$SAVE_ID"
  exit 1
fi
```

---

## Troubleshooting

### Auto-Save Not Working

**Symptoms**: No new auto saves created

**Diagnosis**:
```bash
# Check auto-save status
curl http://localhost:8001/api/savepoints/auto/status

# Check FastAPI logs
grep "auto-save" logs/fastapi.log
```

**Solutions**:
1. Verify service started (check logs for `[OK] Auto-save service started`)
2. Check disk space: `df -h`
3. Verify write permissions: `touch save_points/test.txt && rm save_points/test.txt`
4. Restart FastAPI: `python start_api.py`

### Restore Fails

**Symptoms**: `500 Internal Server Error` during restore

**Diagnosis**:
```bash
# Check archive integrity
tar -tzf save_points/<save_id>.tar.gz

# Verify file exists
ls -lh save_points/<save_id>.tar.gz
```

**Solutions**:
1. **Corrupted archive**: Try previous save point
2. **File locked**: Stop all Project-AI processes
3. **Insufficient permissions**: `chmod 644 save_points/*.tar.gz`
4. **Disk full**: Free space in data/ directory

### Out of Disk Space

**Symptoms**: `500 Internal Server Error` with "disk space" message

**Solutions**:
```bash
# Delete old auto-saves
rm save_points/auto_202506*.tar.gz

# Delete user saves
curl -X DELETE http://localhost:8001/api/savepoints/delete/<save_id>

# Cleanup other data
rm -rf logs/*.log.old
```

---

## Related Documentation

- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - API architecture overview
- **[02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md)** - Core governance endpoints
- **[project_ai/save_points.py](../../project_ai/save_points.py)** - Implementation details

---

**Next**: See [04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md) for Legion agent integration.
