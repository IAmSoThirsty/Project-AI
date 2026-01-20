# Cloud Synchronization Module

## Overview

The Cloud Synchronization module (`cloud_sync.py`) provides encrypted cross-device data synchronization for Project-AI. It allows users to seamlessly sync their AI persona, preferences, learning progress, and other data across multiple devices.

## Features

- **Device Identification**: Unique SHA-256-based device IDs for tracking and management
- **End-to-End Encryption**: All data encrypted using Fernet cipher before transmission
- **Bidirectional Sync**: Upload and download capabilities with automatic merging
- **Conflict Resolution**: Timestamp-based resolution (most recent data wins)
- **Auto-Sync**: Configurable automatic synchronization at regular intervals
- **Metadata Tracking**: Persistent metadata for sync status and history

## Quick Start

### 1. Configuration

Add the cloud sync URL to your `.env` file:

```bash
# .env
CLOUD_SYNC_URL=https://your-api-endpoint.com/sync
FERNET_KEY=<your-generated-fernet-key>
```

Generate a Fernet key if you don't have one:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### 2. Basic Usage

```python
from app.core.cloud_sync import CloudSyncManager

# Initialize sync manager
sync_manager = CloudSyncManager()

# Prepare user data
user_data = {
    "preferences": {"theme": "dark", "language": "en"},
    "ai_persona": {"curiosity": 0.8, "empathy": 0.9},
    "timestamp": datetime.now().isoformat(),
}

# Upload data to cloud
success = sync_manager.sync_upload("username", user_data)

# Download data from cloud
cloud_data = sync_manager.sync_download("username")

# Bidirectional sync with conflict resolution
synced_data = sync_manager.bidirectional_sync("username", user_data)
```

### 3. Enable Auto-Sync

```python
# Enable automatic sync every 10 minutes
sync_manager.enable_auto_sync(interval=600)

# Check sync status
status = sync_manager.get_sync_status("username")
print(f"Auto-sync enabled: {status['auto_sync_enabled']}")
print(f"Last upload: {status['last_upload']}")
```

## Architecture

### Data Flow

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Device A  │────────▶│  Cloud API   │◀────────│   Device B  │
│  (Desktop)  │  Upload │  (Encrypted) │ Download│  (Mobile)   │
└─────────────┘         └──────────────┘         └─────────────┘
       │                       │                        │
       │                       │                        │
       ▼                       ▼                        ▼
  Local Data            Encrypted Blob            Local Data
  + Metadata            + Device Info             + Metadata
```

### Security Model

1. **Encryption at Rest**: All data encrypted before leaving the device
2. **Device Fingerprinting**: SHA-256 hash of device characteristics
3. **Timestamp Validation**: Ensures data freshness and detects tampering
4. **Metadata Isolation**: Per-user sync metadata stored locally

## API Integration

The cloud sync module expects a REST API with the following endpoints:

### POST /upload

Upload encrypted user data.

**Request:**
```json
{
  "username": "string",
  "device_id": "string",
  "encrypted_data": "hex-encoded-bytes"
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "ISO-8601 datetime"
}
```

### GET /download

Download encrypted user data.

**Query Parameters:**
- `username` (string): User identifier
- `device_id` (string): Device identifier

**Response:**
```json
{
  "username": "string",
  "device_id": "string",
  "encrypted_data": "hex-encoded-bytes",
  "timestamp": "ISO-8601 datetime"
}
```

### GET /devices

List all devices that have synced for a user.

**Query Parameters:**
- `username` (string): User identifier

**Response:**
```json
{
  "devices": [
    {
      "device_id": "string",
      "last_sync": "ISO-8601 datetime"
    }
  ]
}
```

## Conflict Resolution

The module uses timestamp-based conflict resolution:

1. Compare timestamps of local and cloud data
2. Most recent data wins
3. Upload winning data to cloud
4. Update local data if cloud was newer

```python
# Example: Local data (older)
local_data = {
    "content": "local version",
    "timestamp": "2025-01-01T10:00:00"
}

# Cloud data (newer)
cloud_data = {
    "content": "cloud version",
    "timestamp": "2025-01-01T11:00:00"
}

# Resolution: Cloud wins
resolved = sync_manager.resolve_conflict(local_data, cloud_data)
# Result: resolved == cloud_data
```

## Testing

The module includes comprehensive tests:

```bash
# Run cloud sync tests
python -m pytest tests/test_cloud_sync.py -v

# Run all tests
python -m pytest tests/ -v
```

Test coverage includes:
- Device ID generation
- Encryption/decryption
- Upload/download operations
- Conflict resolution
- Auto-sync configuration
- Metadata persistence
- Error handling

## Example Scripts

See `examples/cloud_sync_demo.py` for a complete demonstration:

```bash
python examples/cloud_sync_demo.py
```

## Troubleshooting

### Cloud sync URL not configured

**Symptom:** Sync operations return `False` or `None`

**Solution:** Add `CLOUD_SYNC_URL` to your `.env` file

### Encryption errors

**Symptom:** `InvalidToken` exception during decryption

**Solution:** Ensure the same `FERNET_KEY` is used across all devices

### Network errors

**Symptom:** `RequestException` during upload/download

**Solution:** 
- Check network connectivity
- Verify cloud API endpoint is accessible
- Check firewall/proxy settings

### Conflict resolution loops

**Symptom:** Data keeps changing between syncs

**Solution:** Ensure timestamps are set correctly and devices have synchronized clocks

## Best Practices

1. **Regular Backups**: Always maintain local backups before syncing
2. **Network Security**: Use HTTPS for cloud API endpoints
3. **Key Management**: Store Fernet keys securely, never in source control
4. **Sync Frequency**: Balance between data freshness and API costs
5. **Error Handling**: Always check return values and handle failures gracefully

## Integration with Project-AI

The cloud sync module integrates with existing Project-AI components:

- **AI Persona**: Sync personality traits and mood across devices
- **Memory System**: Sync knowledge base and conversation history
- **User Preferences**: Sync UI settings, themes, and configurations
- **Learning Progress**: Sync completed courses and current topics

## Future Enhancements

- [ ] Selective sync (choose which data to sync)
- [ ] Compression for large data sets
- [ ] Offline queue for failed syncs
- [ ] WebSocket support for real-time sync
- [ ] End-to-end encryption with user-provided keys
- [ ] Sync history and rollback capabilities

## License

This module is part of Project-AI and follows the same license terms.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run the example script to verify setup
3. Check logs in `logs/` directory
4. Open an issue on GitHub
