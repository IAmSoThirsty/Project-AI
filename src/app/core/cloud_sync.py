"""
Cloud Sync Module for User Data Synchronization
Syncs user data across multiple devices using encrypted cloud storage
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests  # type: ignore
from cryptography.fernet import Fernet


class CloudSyncManager:
    """Manages cloud synchronization of user data across devices."""
    
    def __init__(self, api_url: Optional[str] = None, encryption_key: Optional[bytes] = None):
        """
        Initialize cloud sync manager.
        
        Args:
            api_url: Cloud API endpoint (default: uses environment variable)
            encryption_key: Fernet encryption key for data security
        """
        self.api_url = api_url or os.getenv('CLOUD_SYNC_URL', 'https://api.project-ai.com/sync')
        self.api_key = os.getenv('CLOUD_SYNC_API_KEY', '')
        self.encryption_key = encryption_key or self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
        self.sync_enabled = os.getenv('CLOUD_SYNC_ENABLED', 'false').lower() == 'true'
        self.last_sync: Dict[str, datetime] = {}
        
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key."""
        key_str = os.getenv('FERNET_KEY')
        if key_str:
            return key_str.encode()
        return Fernet.generate_key()
    
    def _encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """Encrypt data before cloud upload."""
        if not self.cipher:
            raise ValueError("Encryption not configured")
        json_data = json.dumps(data).encode()
        return self.cipher.encrypt(json_data)
    
    def _decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt data from cloud."""
        if not self.cipher:
            raise ValueError("Encryption not configured")
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
    
    def _generate_device_id(self) -> str:
        """Generate unique device identifier."""
        import platform
        device_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
        return hashlib.sha256(device_info.encode()).hexdigest()[:16]
    
    def sync_user_data(self, username: str, user_data: Dict[str, Any]) -> bool:
        """
        Sync user data to cloud.
        
        Args:
            username: User identifier
            user_data: User data to sync
            
        Returns:
            True if sync successful, False otherwise
        """
        if not self.sync_enabled or not self.api_key:
            return False
        
        try:
            device_id = self._generate_device_id()
            encrypted_data = self._encrypt_data(user_data)
            
            payload = {
                'username': username,
                'device_id': device_id,
                'data': encrypted_data.decode('latin-1'),
                'timestamp': datetime.now().isoformat(),
                'data_hash': hashlib.sha256(encrypted_data).hexdigest()
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.api_url}/upload',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.last_sync[username] = datetime.now()
                return True
            
            print(f"Cloud sync failed: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"Cloud sync error: {e}")
            return False
    
    def fetch_user_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user data from cloud.
        
        Args:
            username: User identifier
            
        Returns:
            User data dict or None if fetch failed
        """
        if not self.sync_enabled or not self.api_key:
            return None
        
        try:
            device_id = self._generate_device_id()
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.api_url}/download',
                params={'username': username, 'device_id': device_id},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                encrypted_data = data.get('data', '').encode('latin-1')
                return self._decrypt_data(encrypted_data)
            
            return None
            
        except Exception as e:
            print(f"Cloud fetch error: {e}")
            return None
    
    def list_user_devices(self, username: str) -> List[Dict[str, Any]]:
        """
        List all devices for a user.
        
        Args:
            username: User identifier
            
        Returns:
            List of device information dictionaries
        """
        if not self.sync_enabled or not self.api_key:
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.api_url}/devices',
                params={'username': username},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('devices', [])
            
            return []
            
        except Exception as e:
            print(f"Device list error: {e}")
            return []
    
    def resolve_conflicts(
        self,
        local_data: Dict[str, Any],
        cloud_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between local and cloud data.
        
        Strategy: Most recent timestamp wins, with merge for non-conflicting keys.
        
        Args:
            local_data: Local user data
            cloud_data: Cloud user data
            
        Returns:
            Merged data dictionary
        """
        local_time = local_data.get('last_modified', 0)
        cloud_time = cloud_data.get('last_modified', 0)
        
        if local_time > cloud_time:
            base_data = local_data.copy()
            merge_data = cloud_data
        else:
            base_data = cloud_data.copy()
            merge_data = local_data
        
        # Merge non-conflicting keys
        for key, value in merge_data.items():
            if key not in base_data:
                base_data[key] = value
        
        base_data['last_modified'] = max(local_time, cloud_time)
        base_data['sync_timestamp'] = datetime.now().isoformat()
        
        return base_data
    
    def auto_sync(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform automatic bidirectional sync.
        
        1. Fetch cloud data
        2. Resolve conflicts
        3. Upload merged data
        
        Args:
            username: User identifier
            user_data: Local user data
            
        Returns:
            Merged and synced data
        """
        if not self.sync_enabled:
            return user_data
        
        try:
            # Fetch cloud data
            cloud_data = self.fetch_user_data(username)
            
            if cloud_data:
                # Resolve conflicts
                merged_data = self.resolve_conflicts(user_data, cloud_data)
            else:
                merged_data = user_data
            
            # Upload merged data
            merged_data['last_modified'] = datetime.now().timestamp()
            self.sync_user_data(username, merged_data)
            
            return merged_data
            
        except Exception as e:
            print(f"Auto sync error: {e}")
            return user_data
