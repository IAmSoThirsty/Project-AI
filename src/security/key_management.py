"""
Enterprise-Grade Key Management System
Supports HSM, Cloud KMS (AWS KMS, GCP KMS, Azure Key Vault), and automated key rotation.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError:
    pass  # Will be handled at runtime

logger = logging.getLogger(__name__)


class KeyProvider(Enum):
    """Supported key management providers"""

    LOCAL = "local"
    AWS_KMS = "aws_kms"
    GCP_KMS = "gcp_kms"
    AZURE_KEY_VAULT = "azure_key_vault"
    HSM_PKCS11 = "hsm_pkcs11"


class KeyType(Enum):
    """Types of cryptographic keys"""

    SIGNING = "signing"
    ENCRYPTION = "encryption"
    SYMMETRIC = "symmetric"


class KeyStatus(Enum):
    """Key lifecycle status"""

    ACTIVE = "active"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


@dataclass
class KeyMetadata:
    """Metadata for a cryptographic key"""

    key_id: str
    key_type: KeyType
    provider: KeyProvider
    status: KeyStatus
    created_at: datetime
    rotated_at: datetime | None = None
    expires_at: datetime | None = None
    rotation_policy: dict[str, Any] | None = None
    access_control: dict[str, list[str]] | None = None
    audit_trail: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["key_type"] = self.key_type.value
        data["provider"] = self.provider.value
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        if self.rotated_at:
            data["rotated_at"] = self.rotated_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KeyMetadata":
        """Create from dictionary"""
        data["key_type"] = KeyType(data["key_type"])
        data["provider"] = KeyProvider(data["provider"])
        data["status"] = KeyStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("rotated_at"):
            data["rotated_at"] = datetime.fromisoformat(data["rotated_at"])
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)


class KeyManagementSystem:
    """
    Enterprise-grade key management system with support for:
    - Cloud KMS providers (AWS, GCP, Azure)
    - HSM via PKCS#11
    - Automated key rotation
    - RBAC-integrated access control
    - Full audit trail
    - SIEM integration
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize key management system

        Args:
            config: Configuration dictionary with provider settings
        """
        self.config = config or {}
        self.provider = KeyProvider(self.config.get("provider", "local"))
        self.keys: dict[str, KeyMetadata] = {}
        self.audit_log: list[dict[str, Any]] = []

        # Initialize storage paths
        self.data_dir = self.config.get("data_dir", "data/keys")
        self.audit_dir = os.path.join(self.data_dir, "audit")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.audit_dir, exist_ok=True)

        # Load existing keys
        self._load_keys()

        # Initialize provider-specific clients
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the configured key provider"""
        try:
            if self.provider == KeyProvider.AWS_KMS:
                self._initialize_aws_kms()
            elif self.provider == KeyProvider.GCP_KMS:
                self._initialize_gcp_kms()
            elif self.provider == KeyProvider.AZURE_KEY_VAULT:
                self._initialize_azure_kv()
            elif self.provider == KeyProvider.HSM_PKCS11:
                self._initialize_hsm()
            logger.info(f"Initialized key provider: {self.provider.value}")
        except Exception as e:
            logger.error(f"Failed to initialize provider {self.provider.value}: {e}")
            raise

    def _initialize_aws_kms(self):
        """Initialize AWS KMS client"""
        try:
            import boto3

            self.kms_client = boto3.client(
                "kms",
                region_name=self.config.get("aws_region", "us-east-1"),
                aws_access_key_id=self.config.get("aws_access_key_id"),
                aws_secret_access_key=self.config.get("aws_secret_access_key"),
            )
            logger.info("AWS KMS client initialized")
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS KMS: {e}")
            raise

    def _initialize_gcp_kms(self):
        """Initialize GCP KMS client"""
        try:
            from google.cloud import kms

            self.kms_client = kms.KeyManagementServiceClient()
            self.gcp_project_id = self.config.get("gcp_project_id")
            self.gcp_location = self.config.get("gcp_location", "us-central1")
            logger.info("GCP KMS client initialized")
        except ImportError:
            logger.error("google-cloud-kms not installed. Install with: pip install google-cloud-kms")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize GCP KMS: {e}")
            raise

    def _initialize_azure_kv(self):
        """Initialize Azure Key Vault client"""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.keys import KeyClient

            vault_url = self.config.get("azure_vault_url")
            if not vault_url:
                raise ValueError("azure_vault_url is required for Azure Key Vault")

            credential = DefaultAzureCredential()
            self.kms_client = KeyClient(vault_url=vault_url, credential=credential)
            logger.info("Azure Key Vault client initialized")
        except ImportError:
            logger.error(
                "azure-keyvault-keys not installed. Install with: pip install azure-keyvault-keys azure-identity"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Azure Key Vault: {e}")
            raise

    def _initialize_hsm(self):
        """Initialize HSM via PKCS#11"""
        try:
            import PyKCS11

            self.pkcs11_lib = PyKCS11.PyKCS11Lib()
            lib_path = self.config.get("pkcs11_library_path")
            if not lib_path:
                raise ValueError("pkcs11_library_path is required for HSM")

            self.pkcs11_lib.load(lib_path)
            self.hsm_slot = self.config.get("hsm_slot", 0)
            self.hsm_pin = self.config.get("hsm_pin")
            logger.info("HSM PKCS#11 interface initialized")
        except ImportError:
            logger.error("PyKCS11 not installed. Install with: pip install PyKCS11")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize HSM: {e}")
            raise

    def generate_key(
        self,
        key_id: str,
        key_type: KeyType,
        rotation_policy: dict[str, Any] | None = None,
        access_control: dict[str, list[str]] | None = None,
    ) -> KeyMetadata:
        """
        Generate a new cryptographic key

        Args:
            key_id: Unique identifier for the key
            key_type: Type of key to generate
            rotation_policy: Automatic rotation policy (days, enabled)
            access_control: RBAC access control rules

        Returns:
            KeyMetadata: Metadata for the generated key
        """
        if key_id in self.keys:
            raise ValueError(f"Key {key_id} already exists")

        # Default rotation policy: 90 days for production keys
        if rotation_policy is None:
            rotation_policy = {"enabled": True, "rotation_days": 90}

        # Generate key based on provider
        if self.provider == KeyProvider.AWS_KMS:
            self._generate_aws_key(key_id, key_type)
        elif self.provider == KeyProvider.GCP_KMS:
            self._generate_gcp_key(key_id, key_type)
        elif self.provider == KeyProvider.AZURE_KEY_VAULT:
            self._generate_azure_key(key_id, key_type)
        elif self.provider == KeyProvider.HSM_PKCS11:
            self._generate_hsm_key(key_id, key_type)
        else:
            # Local key generation (development only)
            self._generate_local_key(key_id, key_type)

        # Create metadata
        metadata = KeyMetadata(
            key_id=key_id,
            key_type=key_type,
            provider=self.provider,
            status=KeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=rotation_policy.get("rotation_days", 90)),
            rotation_policy=rotation_policy,
            access_control=access_control,
            audit_trail=[],
        )

        self.keys[key_id] = metadata
        self._save_keys()

        # Audit log
        self._audit_log_event(
            {
                "event": "key_generated",
                "key_id": key_id,
                "key_type": key_type.value,
                "provider": self.provider.value,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        logger.info(f"Generated key {key_id} with provider {self.provider.value}")
        return metadata

    def _generate_local_key(self, key_id: str, key_type: KeyType):
        """Generate local key (development only)"""
        key_path = os.path.join(self.data_dir, f"{key_id}.key")

        if key_type == KeyType.SYMMETRIC:
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
        else:
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())

            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(b"changeme"),
            )

            with open(key_path, "wb") as f:
                f.write(pem)

            # Save public key
            public_key = private_key.public_key()
            pub_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            with open(key_path + ".pub", "wb") as f:
                f.write(pub_pem)

        logger.info(f"Created local key: {key_path}")

    def rotate_key(self, key_id: str, force: bool = False) -> KeyMetadata:
        """
        Rotate a cryptographic key

        Args:
            key_id: Key identifier to rotate
            force: Force rotation even if not due

        Returns:
            KeyMetadata: Updated metadata
        """
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        metadata = self.keys[key_id]

        # Check if rotation is due
        if not force and metadata.expires_at and datetime.utcnow() < metadata.expires_at:
            logger.info(f"Key {key_id} rotation not due yet")
            return metadata

        # Mark old key as deprecated
        metadata.status = KeyStatus.DEPRECATED

        # Generate new key version
        new_key_id = f"{key_id}_v{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        new_metadata = self.generate_key(
            key_id=new_key_id,
            key_type=metadata.key_type,
            rotation_policy=metadata.rotation_policy,
            access_control=metadata.access_control,
        )

        # Update metadata
        metadata.rotated_at = datetime.utcnow()
        self._save_keys()

        # Audit log
        self._audit_log_event(
            {
                "event": "key_rotated",
                "old_key_id": key_id,
                "new_key_id": new_key_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        logger.info(f"Rotated key {key_id} to {new_key_id}")
        return new_metadata

    def check_access(self, key_id: str, identity: str, action: str) -> bool:
        """
        Check if an identity has access to perform an action on a key

        Args:
            key_id: Key identifier
            identity: User/service identity
            action: Action to perform (use, rotate, revoke)

        Returns:
            bool: True if access is granted
        """
        if key_id not in self.keys:
            return False

        metadata = self.keys[key_id]

        if not metadata.access_control:
            # No access control defined, allow all (development mode)
            return True

        allowed_identities = metadata.access_control.get(action, [])
        has_access = identity in allowed_identities or "*" in allowed_identities

        # Audit log
        self._audit_log_event(
            {
                "event": "access_check",
                "key_id": key_id,
                "identity": identity,
                "action": action,
                "granted": has_access,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return has_access

    def export_audit_log(self, format: str = "json") -> str:
        """
        Export audit log for SIEM integration

        Args:
            format: Export format (json, csv, syslog)

        Returns:
            str: Path to exported file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            output_path = os.path.join(self.audit_dir, f"audit_log_{timestamp}.json")
            with open(output_path, "w") as f:
                json.dump(self.audit_log, f, indent=2)
        elif format == "csv":
            import csv

            output_path = os.path.join(self.audit_dir, f"audit_log_{timestamp}.csv")
            with open(output_path, "w", newline="") as f:
                if self.audit_log:
                    writer = csv.DictWriter(f, fieldnames=self.audit_log[0].keys())
                    writer.writeheader()
                    writer.writerows(self.audit_log)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        logger.info(f"Exported audit log to {output_path}")
        return output_path

    def _audit_log_event(self, event: dict[str, Any]):
        """Add event to audit log"""
        self.audit_log.append(event)

        # Write to file immediately for durability
        log_file = os.path.join(self.audit_dir, "current.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _load_keys(self):
        """Load keys from storage"""
        keys_file = os.path.join(self.data_dir, "keys.json")
        if os.path.exists(keys_file):
            try:
                with open(keys_file) as f:
                    data = json.load(f)
                    self.keys = {k: KeyMetadata.from_dict(v) for k, v in data.items()}
                logger.info(f"Loaded {len(self.keys)} keys from storage")
            except Exception as e:
                logger.error(f"Failed to load keys: {e}")

    def _save_keys(self):
        """Save keys to storage"""
        keys_file = os.path.join(self.data_dir, "keys.json")
        try:
            with open(keys_file, "w") as f:
                data = {k: v.to_dict() for k, v in self.keys.items()}
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.keys)} keys to storage")
        except Exception as e:
            logger.error(f"Failed to save keys: {e}")

    def get_key_metadata(self, key_id: str) -> KeyMetadata | None:
        """Get metadata for a key"""
        return self.keys.get(key_id)

    def list_keys(self, status: KeyStatus | None = None) -> list[KeyMetadata]:
        """List all keys, optionally filtered by status"""
        if status:
            return [m for m in self.keys.values() if m.status == status]
        return list(self.keys.values())

    def _generate_aws_key(self, key_id: str, key_type: KeyType) -> str:
        """Generate key in AWS KMS"""
        key_spec = "SYMMETRIC_DEFAULT" if key_type == KeyType.SYMMETRIC else "RSA_4096"
        key_usage = "ENCRYPT_DECRYPT" if key_type == KeyType.ENCRYPTION else "SIGN_VERIFY"

        response = self.kms_client.create_key(
            Description=f"Project-AI Key: {key_id}",
            KeyUsage=key_usage,
            KeySpec=key_spec,
            Tags=[
                {"TagKey": "Project", "TagValue": "Project-AI"},
                {"TagKey": "KeyID", "TagValue": key_id},
                {"TagKey": "KeyType", "TagValue": key_type.value},
            ],
        )

        key_arn = response["KeyMetadata"]["Arn"]

        # Create alias
        self.kms_client.create_alias(
            AliasName=f"alias/project-ai/{key_id}",
            TargetKeyId=response["KeyMetadata"]["KeyId"],
        )

        logger.info(f"Created AWS KMS key: {key_arn}")
        return key_arn

    def _generate_gcp_key(self, key_id: str, key_type: KeyType) -> str:
        """Generate key in GCP KMS"""
        from google.cloud import kms

        # Create key ring if not exists
        key_ring_id = self.config.get("gcp_key_ring", "project-ai-keys")
        parent = f"projects/{self.gcp_project_id}/locations/{self.gcp_location}"

        try:
            self.kms_client.create_key_ring(request={"parent": parent, "key_ring_id": key_ring_id})
        except Exception:
            # Key ring may already exist
            pass

        # Create key
        key_ring_name = f"{parent}/keyRings/{key_ring_id}"

        purpose = kms.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
        if key_type == KeyType.SIGNING:
            purpose = kms.CryptoKey.CryptoKeyPurpose.ASYMMETRIC_SIGN

        crypto_key = self.kms_client.create_crypto_key(
            request={
                "parent": key_ring_name,
                "crypto_key_id": key_id,
                "crypto_key": {
                    "purpose": purpose,
                    "version_template": {
                        "algorithm": (
                            kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.RSA_SIGN_PKCS1_4096_SHA256
                            if key_type == KeyType.SIGNING
                            else kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.GOOGLE_SYMMETRIC_ENCRYPTION
                        )
                    },
                    "labels": {
                        "project": "project-ai",
                        "key-id": key_id,
                        "key-type": key_type.value,
                    },
                },
            }
        )

        logger.info(f"Created GCP KMS key: {crypto_key.name}")
        return crypto_key.name

    def _generate_azure_key(self, key_id: str, key_type: KeyType) -> str:
        """Generate key in Azure Key Vault"""

        key_size = 4096

        key = self.kms_client.create_rsa_key(
            name=key_id,
            size=key_size,
            tags={
                "project": "project-ai",
                "key-id": key_id,
                "key-type": key_type.value,
            },
        )

        logger.info(f"Created Azure Key Vault key: {key.id}")
        return key.id

    def _generate_hsm_key(self, key_id: str, key_type: KeyType) -> int:
        """Generate key in HSM via PKCS#11"""
        import PyKCS11

        session = self.pkcs11_lib.openSession(self.hsm_slot)
        session.login(self.hsm_pin)

        # Generate RSA key pair
        public_template = [
            (PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY),
            (PyKCS11.CKA_TOKEN, True),
            (PyKCS11.CKA_PRIVATE, False),
            (PyKCS11.CKA_MODULUS_BITS, 4096),
            (PyKCS11.CKA_PUBLIC_EXPONENT, (0x01, 0x00, 0x01)),
            (PyKCS11.CKA_ENCRYPT, True),
            (PyKCS11.CKA_VERIFY, True),
            (PyKCS11.CKA_WRAP, True),
            (PyKCS11.CKA_LABEL, key_id),
        ]

        private_template = [
            (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
            (PyKCS11.CKA_TOKEN, True),
            (PyKCS11.CKA_PRIVATE, True),
            (PyKCS11.CKA_DECRYPT, True),
            (PyKCS11.CKA_SIGN, True),
            (PyKCS11.CKA_UNWRAP, True),
            (PyKCS11.CKA_LABEL, key_id),
        ]

        (public_key, private_key) = session.generateKeyPair(public_template, private_template)

        session.logout()
        session.closeSession()

        logger.info(f"Created HSM key: {key_id}")
        return private_key
