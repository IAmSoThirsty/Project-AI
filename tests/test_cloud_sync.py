"""Tests for cloud synchronization system."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from app.core.cloud_sync import CloudSyncManager


@pytest.fixture
def sync_manager(tmp_path):
    """Create a CloudSyncManager with temporary data directory."""
    key = Fernet.generate_key()
    manager = CloudSyncManager(encryption_key=key, data_dir=str(tmp_path))
    return manager


def test_device_id_generation(sync_manager):
    """Test that device ID is generated consistently."""
    device_id1 = sync_manager.device_id
    assert device_id1 is not None
    assert len(device_id1) == 16
    assert isinstance(device_id1, str)

    # Device ID should be consistent for the same machine
    manager2 = CloudSyncManager(encryption_key=sync_manager.encryption_key, data_dir="data")
    assert manager2.device_id == device_id1


def test_encryption_decryption(sync_manager):
    """Test data encryption and decryption."""
    test_data = {
        "username": "testuser",
        "preferences": {"theme": "dark", "language": "en"},
        "timestamp": datetime.now().isoformat(),
    }

    # Encrypt data
    encrypted = sync_manager.encrypt_data(test_data)
    assert encrypted is not None
    assert isinstance(encrypted, bytes)
    assert encrypted != json.dumps(test_data).encode()

    # Decrypt data
    decrypted = sync_manager.decrypt_data(encrypted)
    assert decrypted == test_data


def test_sync_metadata_persistence(tmp_path):
    """Test that sync metadata is persisted correctly."""
    key = Fernet.generate_key()
    manager1 = CloudSyncManager(encryption_key=key, data_dir=str(tmp_path))

    # Add metadata
    manager1.sync_metadata["testuser"] = {
        "last_upload": datetime.now().isoformat(),
        "device_id": manager1.device_id,
    }
    manager1._save_sync_metadata()

    # Create new manager and verify metadata loaded
    manager2 = CloudSyncManager(encryption_key=key, data_dir=str(tmp_path))
    assert "testuser" in manager2.sync_metadata
    assert manager2.sync_metadata["testuser"]["device_id"] == manager1.device_id


def test_conflict_resolution(sync_manager):
    """Test timestamp-based conflict resolution."""
    # Create local data (older)
    local_data = {
        "content": "local content",
        "timestamp": "2025-01-01T10:00:00",
    }

    # Create cloud data (newer)
    cloud_data = {
        "content": "cloud content",
        "timestamp": "2025-01-01T11:00:00",
    }

    # Cloud should win (newer timestamp)
    resolved = sync_manager.resolve_conflict(local_data, cloud_data)
    assert resolved == cloud_data
    assert resolved["content"] == "cloud content"

    # Local should win when newer
    local_data["timestamp"] = "2025-01-01T12:00:00"
    resolved = sync_manager.resolve_conflict(local_data, cloud_data)
    assert resolved == local_data
    assert resolved["content"] == "local content"


def test_auto_sync_configuration(sync_manager):
    """Test auto-sync enable/disable."""
    assert sync_manager.auto_sync_enabled is False

    # Enable auto-sync
    sync_manager.enable_auto_sync(interval=600)
    assert sync_manager.auto_sync_enabled is True
    assert sync_manager.auto_sync_interval == 600

    # Disable auto-sync
    sync_manager.disable_auto_sync()
    assert sync_manager.auto_sync_enabled is False


def test_get_sync_status(sync_manager):
    """Test sync status retrieval."""
    status = sync_manager.get_sync_status("testuser")

    assert "device_id" in status
    assert status["device_id"] == sync_manager.device_id
    assert "cloud_sync_configured" in status
    assert "auto_sync_enabled" in status
    assert "auto_sync_interval" in status


@patch("app.core.cloud_sync.requests.post")
def test_sync_upload_success(mock_post, sync_manager):
    """Test successful data upload to cloud."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Set cloud sync URL
    sync_manager.cloud_sync_url = "https://api.example.com/sync"

    test_data = {"preferences": {"theme": "dark"}}
    result = sync_manager.sync_upload("testuser", test_data)

    assert result is True
    assert mock_post.called
    assert "testuser" in sync_manager.sync_metadata


@patch("app.core.cloud_sync.requests.post")
def test_sync_upload_failure(mock_post, sync_manager):
    """Test upload failure handling."""
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    sync_manager.cloud_sync_url = "https://api.example.com/sync"

    test_data = {"preferences": {"theme": "dark"}}
    result = sync_manager.sync_upload("testuser", test_data)

    assert result is False


@patch("app.core.cloud_sync.requests.get")
def test_sync_download_success(mock_get, sync_manager):
    """Test successful data download from cloud."""
    # Prepare test data
    test_data = {
        "username": "testuser",
        "device_id": "test123",
        "timestamp": datetime.now().isoformat(),
        "data": {"preferences": {"theme": "dark"}},
    }
    encrypted = sync_manager.encrypt_data(test_data)

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"encrypted_data": encrypted.hex()}
    mock_get.return_value = mock_response

    sync_manager.cloud_sync_url = "https://api.example.com/sync"

    result = sync_manager.sync_download("testuser")

    assert result is not None
    assert result["username"] == "testuser"
    assert "testuser" in sync_manager.sync_metadata


@patch("app.core.cloud_sync.requests.get")
def test_sync_download_not_found(mock_get, sync_manager):
    """Test download when no cloud data exists."""
    # Mock 404 response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    sync_manager.cloud_sync_url = "https://api.example.com/sync"

    result = sync_manager.sync_download("testuser")

    assert result is None


def test_sync_without_url(sync_manager):
    """Test sync operations when cloud URL is not configured."""
    # Ensure no URL is set
    sync_manager.cloud_sync_url = None

    # Upload should fail gracefully
    result = sync_manager.sync_upload("testuser", {"data": "test"})
    assert result is False

    # Download should return None
    result = sync_manager.sync_download("testuser")
    assert result is None

    # Bidirectional sync should return local data unchanged
    local_data = {"content": "local", "timestamp": datetime.now().isoformat()}
    result = sync_manager.bidirectional_sync("testuser", local_data)
    assert result == local_data


@patch("app.core.cloud_sync.requests.get")
def test_list_devices(mock_get, sync_manager):
    """Test device listing functionality."""
    # Mock response with device list
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "devices": [
            {"device_id": "device1", "last_sync": "2025-01-01T10:00:00"},
            {"device_id": sync_manager.device_id, "last_sync": "2025-01-01T11:00:00"},
        ]
    }
    mock_get.return_value = mock_response

    sync_manager.cloud_sync_url = "https://api.example.com/sync"

    devices = sync_manager.list_devices("testuser")

    assert len(devices) == 2
    # Current device should be marked
    current_devices = [d for d in devices if d.get("current")]
    assert len(current_devices) == 1
    assert current_devices[0]["device_id"] == sync_manager.device_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
