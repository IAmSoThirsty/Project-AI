"""
Vault Integration for Secrets Management

Integrates with HashiCorp Vault for dynamic secrets, encryption, and key management.
"""

import os
import requests
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class VaultSecretEngine(Enum):
    """Vault secret engine types"""
    KV_V2 = "kv-v2"
    DATABASE = "database"
    PKI = "pki"
    TRANSIT = "transit"
    AWS = "aws"
    GCP = "gcp"


class SecretsManager:
    """
    HashiCorp Vault integration for secrets management
    
    Features:
    - Dynamic database credentials
    - PKI certificate management
    - Encryption as a service (transit engine)
    - Static secret storage (KV v2)
    - Cloud provider credentials (AWS, GCP)
    """
    
    def __init__(
        self,
        vault_addr: Optional[str] = None,
        vault_token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.namespace = namespace or os.getenv("VAULT_NAMESPACE")
        
        if not self.vault_token:
            raise ValueError("Vault token not provided")
        
        self.headers = {
            "X-Vault-Token": self.vault_token,
            "Content-Type": "application/json",
        }
        
        if self.namespace:
            self.headers["X-Vault-Namespace"] = self.namespace
    
    def read_secret(self, path: str, mount_point: str = "secret") -> Dict[str, Any]:
        """
        Read secret from KV v2 engine
        
        Args:
            path: Secret path (e.g., "temporal/database")
            mount_point: KV mount point
        
        Returns:
            Secret data dictionary
        """
        url = f"{self.vault_addr}/v1/{mount_point}/data/{path}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result["data"]["data"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to read secret {path}: {e}")
            raise
    
    def write_secret(
        self,
        path: str,
        data: Dict[str, Any],
        mount_point: str = "secret",
    ) -> bool:
        """
        Write secret to KV v2 engine
        
        Args:
            path: Secret path
            data: Secret data
            mount_point: KV mount point
        
        Returns:
            True if successful
        """
        url = f"{self.vault_addr}/v1/{mount_point}/data/{path}"
        payload = {"data": data}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Wrote secret to {path}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to write secret {path}: {e}")
            raise
    
    def delete_secret(self, path: str, mount_point: str = "secret") -> bool:
        """Delete secret from KV v2 engine"""
        url = f"{self.vault_addr}/v1/{mount_point}/metadata/{path}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Deleted secret {path}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete secret {path}: {e}")
            return False
    
    def generate_database_credentials(
        self,
        role_name: str,
        mount_point: str = "database",
    ) -> Dict[str, str]:
        """
        Generate dynamic database credentials
        
        Args:
            role_name: Database role name
            mount_point: Database engine mount point
        
        Returns:
            Dict with username and password
        """
        url = f"{self.vault_addr}/v1/{mount_point}/creds/{role_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            creds = result["data"]
            
            logger.info(f"Generated database credentials for role {role_name}")
            
            return {
                "username": creds["username"],
                "password": creds["password"],
                "lease_id": result["lease_id"],
                "lease_duration": result["lease_duration"],
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate database credentials: {e}")
            raise
    
    def encrypt_data(
        self,
        plaintext: str,
        key_name: str,
        mount_point: str = "transit",
    ) -> str:
        """
        Encrypt data using Vault transit engine
        
        Args:
            plaintext: Data to encrypt (will be base64 encoded)
            key_name: Encryption key name
            mount_point: Transit engine mount point
        
        Returns:
            Encrypted ciphertext
        """
        import base64
        
        url = f"{self.vault_addr}/v1/{mount_point}/encrypt/{key_name}"
        
        # Base64 encode plaintext
        plaintext_b64 = base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')
        
        payload = {"plaintext": plaintext_b64}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result["data"]["ciphertext"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(
        self,
        ciphertext: str,
        key_name: str,
        mount_point: str = "transit",
    ) -> str:
        """
        Decrypt data using Vault transit engine
        
        Args:
            ciphertext: Encrypted data
            key_name: Encryption key name
            mount_point: Transit engine mount point
        
        Returns:
            Decrypted plaintext
        """
        import base64
        
        url = f"{self.vault_addr}/v1/{mount_point}/decrypt/{key_name}"
        
        payload = {"ciphertext": ciphertext}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            plaintext_b64 = result["data"]["plaintext"]
            
            # Base64 decode
            plaintext = base64.b64decode(plaintext_b64).decode('utf-8')
            return plaintext
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def rotate_encryption_key(
        self,
        key_name: str,
        mount_point: str = "transit",
    ) -> bool:
        """Rotate transit encryption key"""
        url = f"{self.vault_addr}/v1/{mount_point}/keys/{key_name}/rotate"
        
        try:
            response = requests.post(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Rotated encryption key {key_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to rotate key: {e}")
            return False
    
    def create_transit_key(
        self,
        key_name: str,
        key_type: str = "aes256-gcm96",
        mount_point: str = "transit",
    ) -> bool:
        """
        Create new transit encryption key
        
        Args:
            key_name: Key name
            key_type: Key type (aes256-gcm96, chacha20-poly1305, etc.)
            mount_point: Transit engine mount point
        
        Returns:
            True if successful
        """
        url = f"{self.vault_addr}/v1/{mount_point}/keys/{key_name}"
        
        payload = {"type": key_type}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Created transit key {key_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create transit key: {e}")
            return False
    
    def configure_database_connection(
        self,
        name: str,
        plugin_name: str,
        connection_url: str,
        allowed_roles: List[str],
        mount_point: str = "database",
        **kwargs,
    ) -> bool:
        """
        Configure database connection in Vault
        
        Args:
            name: Connection name
            plugin_name: Database plugin (postgresql-database-plugin, etc.)
            connection_url: Database connection URL
            allowed_roles: List of allowed role names
            mount_point: Database engine mount point
        
        Returns:
            True if successful
        """
        url = f"{self.vault_addr}/v1/{mount_point}/config/{name}"
        
        payload = {
            "plugin_name": plugin_name,
            "connection_url": connection_url,
            "allowed_roles": allowed_roles,
            **kwargs,
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Configured database connection {name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to configure database connection: {e}")
            return False
    
    def create_database_role(
        self,
        role_name: str,
        db_name: str,
        creation_statements: List[str],
        default_ttl: str = "1h",
        max_ttl: str = "24h",
        mount_point: str = "database",
    ) -> bool:
        """
        Create database role for dynamic credential generation
        
        Args:
            role_name: Role name
            db_name: Database connection name
            creation_statements: SQL statements to create user
            default_ttl: Default credential TTL
            max_ttl: Maximum credential TTL
            mount_point: Database engine mount point
        
        Returns:
            True if successful
        """
        url = f"{self.vault_addr}/v1/{mount_point}/roles/{role_name}"
        
        payload = {
            "db_name": db_name,
            "creation_statements": creation_statements,
            "default_ttl": default_ttl,
            "max_ttl": max_ttl,
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Created database role {role_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create database role: {e}")
            return False
