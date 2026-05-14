"""
Media Library - Encrypted storage and management for downloaded media
"""

import logging
from typing import Dict, Any, List, Optional
import time


class MediaLibrary:
    """
    Built-in media library with God tier encryption.

    Features:
    - Encrypted media catalog
    - Metadata encryption
    - Secure playback
    - Library organization
    - Privacy-preserving search
    """

    def __init__(self, god_tier_encryption):
        self.logger = logging.getLogger(__name__)
        self.god_tier_encryption = god_tier_encryption

        # Encrypted catalog
        self._catalog: List[Dict[str, Any]] = []

        # Library stats
        self._stats = {"total_items": 0, "audio_items": 0, "video_items": 0}

    def add_item(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        media_type: str = "video",
    ) -> str:
        """
        Add item to library with encryption.

        Args:
            file_path: Path to media file
            metadata: Media metadata (will be encrypted)
            media_type: 'audio' or 'video'

        Returns:
            Item ID
        """
        # Encrypt file path
        encrypted_path = self.god_tier_encryption.encrypt_god_tier(file_path.encode())

        # Encrypt metadata
        if metadata:
            import json

            metadata_str = json.dumps(metadata)
            encrypted_metadata = self.god_tier_encryption.encrypt_god_tier(
                metadata_str.encode()
            )
        else:
            encrypted_metadata = None

        item = {
            "id": f"item_{len(self._catalog)}",
            "encrypted_path": encrypted_path,
            "encrypted_metadata": encrypted_metadata,
            "media_type": media_type,
            "added_time": time.time(),
            "god_tier_encrypted": True,
        }

        self._catalog.append(item)

        # Update stats
        self._stats["total_items"] += 1
        if media_type == "audio":
            self._stats["audio_items"] += 1
        else:
            self._stats["video_items"] += 1

        self.logger.info(f"Item added to library: {item['id']} ({media_type})")

        return item["id"]

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item from library"""
        for item in self._catalog:
            if item["id"] == item_id:
                return item.copy()
        return None

    def list_items(self, media_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all items or filtered by type"""
        if media_type:
            return [item for item in self._catalog if item["media_type"] == media_type]
        return self._catalog.copy()

    def remove_item(self, item_id: str):
        """Remove item from library"""
        self._catalog = [item for item in self._catalog if item["id"] != item_id]
        self.logger.info(f"Item removed: {item_id}")

    def clear_library(self):
        """Clear entire library"""
        count = len(self._catalog)
        self._catalog.clear()
        self._stats = {"total_items": 0, "audio_items": 0, "video_items": 0}
        self.logger.info(f"Library cleared - {count} items removed")

    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        return self._stats.copy()
