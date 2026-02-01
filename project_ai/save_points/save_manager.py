#!/usr/bin/env python3
"""
Save Points Manager - User and Auto-Save System
Manages manual user save points and automatic 15-minute rotation saves
"""

import os
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SavePointsManager:
    """Manages user save points and auto-saves with rotation"""
    
    def __init__(self, base_dir: str = "data/savepoints"):
        self.base_dir = Path(base_dir)
        self.user_dir = self.base_dir / "user"
        self.auto_dir = self.base_dir / "auto"
        
        # Create directories
        self.user_dir.mkdir(parents=True, exist_ok=True)
        self.auto_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-save slots (rotating)
        self.auto_slots = ["latest", "previous1", "previous2"]
        
    def create_user_save(self, name: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Create a user-triggered save point
        
        Args:
            name: User-friendly name for the save point
            metadata: Optional metadata to store with save
            
        Returns:
            Save point info dictionary
        """
        timestamp = datetime.now().isoformat()
        save_id = f"{int(time.time())}_{name.replace(' ', '_')}"
        save_path = self.user_dir / save_id
        save_path.mkdir(exist_ok=True)
        
        # Create manifest
        manifest = {
            "id": save_id,
            "name": name,
            "type": "user",
            "timestamp": timestamp,
            "created_at": time.time(),
            "metadata": metadata or {}
        }
        
        # Save manifest
        with open(save_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Copy important files
        self._backup_files(save_path)
        
        logger.info(f"Created user save point: {name} ({save_id})")
        return manifest
    
    def create_auto_save(self) -> Dict:
        """
        Create an auto-save and rotate existing ones
        
        Returns:
            Auto-save info dictionary
        """
        timestamp = datetime.now().isoformat()
        
        # Rotate existing auto-saves
        self._rotate_auto_saves()
        
        # Create new auto-save in 'latest' slot
        save_path = self.auto_dir / "latest"
        save_path.mkdir(exist_ok=True)
        
        # Create manifest
        manifest = {
            "id": "auto_latest",
            "name": f"Auto-save {timestamp}",
            "type": "auto",
            "timestamp": timestamp,
            "created_at": time.time(),
            "slot": "latest"
        }
        
        # Save manifest
        with open(save_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Backup files
        self._backup_files(save_path)
        
        logger.info(f"Created auto-save at {timestamp}")
        return manifest
    
    def _rotate_auto_saves(self):
        """Rotate auto-save slots (latest -> previous1 -> previous2 -> deleted)"""
        # Delete oldest (previous2)
        oldest = self.auto_dir / "previous2"
        if oldest.exists():
            shutil.rmtree(oldest)
            
        # Shift previous1 -> previous2
        prev1 = self.auto_dir / "previous1"
        if prev1.exists():
            shutil.move(str(prev1), str(oldest))
        
        # Shift latest -> previous1
        latest = self.auto_dir / "latest"
        if latest.exists():
            shutil.move(str(latest), str(prev1))
    
    def _backup_files(self, save_path: Path):
        """Backup important files to save point"""
        files_to_backup = [
            "data/users.json",
            "data/conversations.db",
            ".env",
            "config/app-config.json"
        ]
        
        for file_path in files_to_backup:
            src = Path(file_path)
            if src.exists():
                dest = save_path / src.name
                shutil.copy2(src, dest)
    
    def restore_save_point(self, save_id: str) -> bool:
        """
        Restore from a save point
        
        Args:
            save_id: ID of save point to restore
            
        Returns:
            True if successful, False otherwise
        """
        # Find save point
        save_path = self._find_save_point(save_id)
        if not save_path:
            logger.error(f"Save point not found: {save_id}")
            return False
        
        # Read manifest
        manifest_path = save_path / "manifest.json"
        if not manifest_path.exists():
            logger.error(f"No manifest found for save point: {save_id}")
            return False
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Restore files
        for file in save_path.glob("*"):
            if file.name == "manifest.json":
                continue
                
            dest = Path("data") / file.name
            shutil.copy2(file, dest)
        
        logger.info(f"Restored save point: {manifest['name']}")
        return True
    
    def _find_save_point(self, save_id: str) -> Optional[Path]:
        """Find a save point by ID"""
        # Check user saves
        user_save = self.user_dir / save_id
        if user_save.exists():
            return user_save
        
        # Check auto-saves
        for slot in self.auto_slots:
            auto_save = self.auto_dir / slot
            if auto_save.exists():
                manifest_path = auto_save / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                        if manifest.get("id") == save_id or slot == save_id:
                            return auto_save
        
        return None
    
    def list_save_points(self) -> Dict[str, List[Dict]]:
        """
        List all save points
        
        Returns:
            Dictionary with 'user' and 'auto' lists
        """
        result = {"user": [], "auto": []}
        
        # List user saves
        for save_dir in sorted(self.user_dir.iterdir(), reverse=True):
            if save_dir.is_dir():
                manifest_path = save_dir / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        result["user"].append(json.load(f))
        
        # List auto-saves
        for slot in self.auto_slots:
            save_dir = self.auto_dir / slot
            if save_dir.exists():
                manifest_path = save_dir / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        result["auto"].append(json.load(f))
        
        return result
    
    def delete_save_point(self, save_id: str) -> bool:
        """Delete a save point"""
        save_path = self._find_save_point(save_id)
        if not save_path:
            return False
        
        # Don't allow deleting auto-saves
        if save_path.parent == self.auto_dir:
            logger.warning(f"Cannot delete auto-save: {save_id}")
            return False
        
        shutil.rmtree(save_path)
        logger.info(f"Deleted save point: {save_id}")
        return True
