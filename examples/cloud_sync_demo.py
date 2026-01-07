#!/usr/bin/env python
"""
Example script demonstrating cloud sync integration with Project-AI.

This script shows how to use CloudSyncManager for cross-device synchronization.
"""

import json
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.core.cloud_sync import CloudSyncManager


def main():
    """Demonstrate cloud sync functionality."""
    print("=" * 60)
    print("Project-AI Cloud Sync Integration Example")
    print("=" * 60)
    print()

    # Initialize sync manager
    print("1. Initializing CloudSyncManager...")
    sync_manager = CloudSyncManager(data_dir="data")
    print(f"   ✓ Device ID: {sync_manager.device_id}")
    print(f"   ✓ Cloud sync configured: {sync_manager.cloud_sync_url is not None}")
    print()

    # Example user data
    username = "demo_user"
    user_data = {
        "username": username,
        "preferences": {
            "theme": "dark",
            "language": "en",
            "notifications": True,
        },
        "ai_persona": {
            "curiosity": 0.8,
            "empathy": 0.9,
            "humor": 0.6,
        },
        "learning_progress": {
            "completed_topics": ["intro_to_ai", "ethics_101"],
            "current_topic": "advanced_ml",
        },
        "timestamp": datetime.now().isoformat(),
    }

    # Test encryption
    print("2. Testing encryption...")
    encrypted = sync_manager.encrypt_data(user_data)
    print(f"   ✓ Data encrypted ({len(encrypted)} bytes)")
    
    decrypted = sync_manager.decrypt_data(encrypted)
    print(f"   ✓ Data decrypted successfully")
    print(f"   ✓ Data integrity verified: {decrypted['username'] == username}")
    print()

    # Test sync status
    print("3. Checking sync status...")
    status = sync_manager.get_sync_status(username)
    print(f"   ✓ Auto-sync enabled: {status['auto_sync_enabled']}")
    print(f"   ✓ Auto-sync interval: {status['auto_sync_interval']}s")
    print(f"   ✓ Last upload: {status.get('last_upload', 'Never')}")
    print(f"   ✓ Last download: {status.get('last_download', 'Never')}")
    print()

    # Enable auto-sync
    print("4. Configuring auto-sync...")
    sync_manager.enable_auto_sync(interval=600)  # 10 minutes
    print(f"   ✓ Auto-sync enabled with 600s interval")
    print()

    # Test conflict resolution
    print("5. Testing conflict resolution...")
    local_data = {
        "content": "Local version",
        "timestamp": "2025-01-07T10:00:00",
    }
    cloud_data = {
        "content": "Cloud version (newer)",
        "timestamp": "2025-01-07T11:00:00",
    }
    resolved = sync_manager.resolve_conflict(local_data, cloud_data)
    print(f"   ✓ Conflict resolved: Using {resolved['content']}")
    print()

    # Save sync metadata
    print("6. Persisting sync metadata...")
    sync_manager.sync_metadata[username] = {
        "last_sync": datetime.now().isoformat(),
        "device_id": sync_manager.device_id,
        "sync_count": 1,
    }
    sync_manager._save_sync_metadata()
    print(f"   ✓ Metadata saved to {sync_manager.sync_metadata_path}")
    print()

    # Note about cloud sync URL
    print("7. Cloud Sync Configuration:")
    if sync_manager.cloud_sync_url:
        print(f"   ✓ Cloud API URL: {sync_manager.cloud_sync_url}")
        print("   Note: To test actual sync, ensure the API endpoint is accessible")
    else:
        print("   ⚠ Cloud sync URL not configured")
        print("   To enable cloud sync:")
        print("   1. Add CLOUD_SYNC_URL to your .env file")
        print("   2. Example: CLOUD_SYNC_URL=https://your-api.com/sync")
        print("   3. Restart the application")
    print()

    print("=" * 60)
    print("Cloud Sync Integration Demonstration Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
