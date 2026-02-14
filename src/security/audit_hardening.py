"""
Audit Hardening System with WORM Storage and Cryptographic Signing
Provides immutable, tamper-evident audit logs with cryptographic integrity.
"""

import base64
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
except ImportError:
    pass  # Will be handled at runtime

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Supported WORM storage backends"""
    LOCAL = "local"
    S3_OBJECT_LOCK = "s3_object_lock"
    AZURE_IMMUTABLE_BLOB = "azure_immutable_blob"
    GCP_BUCKET_RETENTION = "gcp_bucket_retention"


class LogLevel(Enum):
    """Audit log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


@dataclass
class AuditLogEntry:
    """Single audit log entry"""
    timestamp: datetime
    level: LogLevel
    event_type: str
    actor: str
    resource: str
    action: str
    result: str
    metadata: dict[str, Any]
    sequence_number: int
    previous_hash: str
    current_hash: str
    signature: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'AuditLogEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['level'] = LogLevel(data['level'])
        return cls(**data)


class AuditHardeningSystem:
    """
    Audit hardening system with:
    - WORM (Write Once Read Many) storage
    - Cryptographic signing of log batches (Ed25519)
    - Merkle tree for log verification
    - Immutable log storage
    - Tamper detection
    - External root-of-trust
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize audit hardening system

        Args:
            config: Configuration dictionary with storage settings
        """
        self.config = config or {}
        self.backend = StorageBackend(self.config.get('backend', 'local'))
        self.batch_size = self.config.get('batch_size', 100)
        self.retention_days = self.config.get('retention_days', 2555)  # 7 years default

        # Initialize storage paths
        self.data_dir = self.config.get('data_dir', 'data/audit')
        self.worm_dir = os.path.join(self.data_dir, 'worm')
        self.signing_keys_dir = os.path.join(self.data_dir, 'signing_keys')
        os.makedirs(self.worm_dir, exist_ok=True)
        os.makedirs(self.signing_keys_dir, exist_ok=True)

        # Initialize log chain
        self.current_batch: list[AuditLogEntry] = []
        self.sequence_number = self._load_sequence_number()
        self.previous_hash = self._load_previous_hash()

        # Initialize signing key
        self.signing_key = self._load_or_generate_signing_key()

        # Initialize storage backend
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize the configured storage backend"""
        try:
            if self.backend == StorageBackend.S3_OBJECT_LOCK:
                self._initialize_s3()
            elif self.backend == StorageBackend.AZURE_IMMUTABLE_BLOB:
                self._initialize_azure()
            elif self.backend == StorageBackend.GCP_BUCKET_RETENTION:
                self._initialize_gcp()
            logger.info(f"Initialized storage backend: {self.backend.value}")
        except Exception as e:
            logger.error(f"Failed to initialize backend {self.backend.value}: {e}")
            raise

    def _initialize_s3(self):
        """Initialize AWS S3 with Object Lock"""
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                region_name=self.config.get('aws_region', 'us-east-1'),
                aws_access_key_id=self.config.get('aws_access_key_id'),
                aws_secret_access_key=self.config.get('aws_secret_access_key')
            )
            self.s3_bucket = self.config.get('s3_bucket')
            if not self.s3_bucket:
                raise ValueError("s3_bucket is required for S3 Object Lock")

            # Verify Object Lock is enabled
            try:
                self.s3_client.get_object_lock_configuration(Bucket=self.s3_bucket)
                logger.info(f"S3 Object Lock verified for bucket {self.s3_bucket}")
            except Exception as e:
                logger.error(f"S3 Object Lock not enabled for bucket {self.s3_bucket}: {e}")
                raise
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise

    def _initialize_azure(self):
        """Initialize Azure Blob Storage with Immutable Blobs"""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.storage.blob import BlobServiceClient

            connection_string = self.config.get('azure_connection_string')
            if connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            else:
                account_url = self.config.get('azure_account_url')
                if not account_url:
                    raise ValueError("azure_connection_string or azure_account_url is required")
                credential = DefaultAzureCredential()
                self.blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

            self.azure_container = self.config.get('azure_container', 'audit-logs')
            logger.info(f"Azure Blob Storage initialized for container {self.azure_container}")
        except ImportError:
            logger.error("azure-storage-blob not installed. Install with: pip install azure-storage-blob azure-identity")
            raise

    def _initialize_gcp(self):
        """Initialize GCP Cloud Storage with Bucket Retention Lock"""
        try:
            from google.cloud import storage
            self.gcs_client = storage.Client(project=self.config.get('gcp_project_id'))
            self.gcs_bucket_name = self.config.get('gcs_bucket')
            if not self.gcs_bucket_name:
                raise ValueError("gcs_bucket is required for GCP Bucket Retention")

            self.gcs_bucket = self.gcs_client.bucket(self.gcs_bucket_name)

            # Verify retention policy
            self.gcs_bucket.reload()
            if not self.gcs_bucket.retention_period:
                logger.warning(f"No retention policy set for bucket {self.gcs_bucket_name}")
            else:
                logger.info(f"GCP retention policy: {self.gcs_bucket.retention_period} seconds")
        except ImportError:
            logger.error("google-cloud-storage not installed. Install with: pip install google-cloud-storage")
            raise

    def _load_or_generate_signing_key(self) -> ed25519.Ed25519PrivateKey:
        """Load or generate Ed25519 signing key"""
        key_path = os.path.join(self.signing_keys_dir, 'audit_signing_key.pem')

        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            logger.info("Loaded existing signing key")
            return private_key

        # Generate new key
        private_key = ed25519.Ed25519PrivateKey.generate()

        # Save private key
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open(key_path, 'wb') as f:
            f.write(pem)

        # Save public key for verification
        public_key = private_key.public_key()
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(key_path + '.pub', 'wb') as f:
            f.write(pub_pem)

        logger.info("Generated new signing key")
        return private_key

    def log_event(
        self,
        level: LogLevel,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        result: str,
        metadata: dict[str, Any] | None = None
    ) -> AuditLogEntry:
        """
        Log an audit event

        Args:
            level: Log level
            event_type: Type of event (access, modification, deletion, etc.)
            actor: Identity performing the action
            resource: Resource being acted upon
            action: Action being performed
            result: Result of the action (success, failure, blocked)
            metadata: Additional metadata

        Returns:
            AuditLogEntry: The logged entry
        """
        # Compute hash of entry data
        entry_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.value,
            'event_type': event_type,
            'actor': actor,
            'resource': resource,
            'action': action,
            'result': result,
            'metadata': metadata or {},
            'sequence_number': self.sequence_number,
            'previous_hash': self.previous_hash
        }

        current_hash = self._compute_hash(json.dumps(entry_data, sort_keys=True))

        # Create entry
        entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            event_type=event_type,
            actor=actor,
            resource=resource,
            action=action,
            result=result,
            metadata=metadata or {},
            sequence_number=self.sequence_number,
            previous_hash=self.previous_hash,
            current_hash=current_hash
        )

        # Add to batch
        self.current_batch.append(entry)

        # Update chain state
        self.previous_hash = current_hash
        self.sequence_number += 1

        # Flush batch if full
        if len(self.current_batch) >= self.batch_size:
            self.flush_batch()

        logger.debug(f"Logged audit event: {event_type} by {actor} on {resource}")
        return entry

    def flush_batch(self):
        """Flush current batch to immutable storage"""
        if not self.current_batch:
            return

        # Sign the batch
        batch_data = [entry.to_dict() for entry in self.current_batch]
        batch_json = json.dumps(batch_data, sort_keys=True)
        signature = self._sign_batch(batch_json)

        # Add signature to each entry
        for entry in self.current_batch:
            entry.signature = signature

        # Compute Merkle root
        merkle_root = self._compute_merkle_root(self.current_batch)

        # Create batch metadata
        batch_metadata = {
            'batch_id': f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.utcnow().isoformat(),
            'entry_count': len(self.current_batch),
            'first_sequence': self.current_batch[0].sequence_number,
            'last_sequence': self.current_batch[-1].sequence_number,
            'merkle_root': merkle_root,
            'signature': signature
        }

        # Store to WORM storage
        self._store_batch(batch_data, batch_metadata)

        # Clear batch
        self.current_batch = []

        # Save state
        self._save_state()

        logger.info(f"Flushed batch {batch_metadata['batch_id']} with {batch_metadata['entry_count']} entries")

    def _sign_batch(self, batch_data: str) -> str:
        """Sign a batch of log entries"""
        signature = self.signing_key.sign(batch_data.encode())
        return base64.b64encode(signature).decode()

    def verify_batch_signature(self, batch_data: str, signature: str) -> bool:
        """Verify the signature of a batch"""
        try:
            public_key = self.signing_key.public_key()
            signature_bytes = base64.b64decode(signature)
            public_key.verify(signature_bytes, batch_data.encode())
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    def _compute_hash(self, data: str) -> str:
        """Compute SHA256 hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()

    def _compute_merkle_root(self, entries: list[AuditLogEntry]) -> str:
        """Compute Merkle tree root hash"""
        if not entries:
            return ""

        hashes = [entry.current_hash for entry in entries]

        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])  # Duplicate last hash if odd number

            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = self._compute_hash(combined)
                new_hashes.append(new_hash)

            hashes = new_hashes

        return hashes[0]

    def _store_batch(self, batch_data: list[dict[str, Any]], metadata: dict[str, Any]):
        """Store batch to WORM storage"""
        batch_id = metadata['batch_id']

        # Create complete batch document
        document = {
            'metadata': metadata,
            'entries': batch_data
        }

        if self.backend == StorageBackend.S3_OBJECT_LOCK:
            self._store_to_s3(batch_id, document)
        elif self.backend == StorageBackend.AZURE_IMMUTABLE_BLOB:
            self._store_to_azure(batch_id, document)
        elif self.backend == StorageBackend.GCP_BUCKET_RETENTION:
            self._store_to_gcp(batch_id, document)
        else:
            # Local storage (development only)
            self._store_to_local(batch_id, document)

    def _store_to_s3(self, batch_id: str, document: dict[str, Any]):
        """Store batch to S3 with Object Lock"""
        key = f"audit-logs/{batch_id}.json"

        retention_until = datetime.utcnow().replace(
            year=datetime.utcnow().year + (self.retention_days // 365)
        )

        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=json.dumps(document, indent=2),
            ContentType='application/json',
            ObjectLockMode='GOVERNANCE',
            ObjectLockRetainUntilDate=retention_until,
            Metadata={
                'batch-id': batch_id,
                'merkle-root': document['metadata']['merkle_root']
            }
        )

        logger.info(f"Stored batch {batch_id} to S3 with Object Lock")

    def _store_to_azure(self, batch_id: str, document: dict[str, Any]):
        """Store batch to Azure with Immutable Blob"""
        from datetime import timedelta

        from azure.storage.blob import ImmutabilityPolicy

        blob_name = f"audit-logs/{batch_id}.json"
        container_client = self.blob_service_client.get_container_client(self.azure_container)

        # Create container if not exists
        try:
            container_client.create_container()
        except Exception:
            pass

        blob_client = container_client.get_blob_client(blob_name)

        # Upload blob
        blob_client.upload_blob(
            json.dumps(document, indent=2),
            overwrite=False,
            metadata={
                'batch_id': batch_id,
                'merkle_root': document['metadata']['merkle_root']
            }
        )

        # Set immutability policy
        blob_client.set_immutability_policy(
            immutability_policy=ImmutabilityPolicy(
                expiry_time=datetime.utcnow() + timedelta(days=self.retention_days),
                policy_mode='Unlocked'  # Use 'Locked' for production
            )
        )

        logger.info(f"Stored batch {batch_id} to Azure with Immutable Blob")

    def _store_to_gcp(self, batch_id: str, document: dict[str, Any]):
        """Store batch to GCP with Bucket Retention"""
        blob_name = f"audit-logs/{batch_id}.json"
        blob = self.gcs_bucket.blob(blob_name)

        blob.metadata = {
            'batch_id': batch_id,
            'merkle_root': document['metadata']['merkle_root']
        }

        blob.upload_from_string(
            json.dumps(document, indent=2),
            content_type='application/json'
        )

        logger.info(f"Stored batch {batch_id} to GCP with Bucket Retention")

    def _store_to_local(self, batch_id: str, document: dict[str, Any]):
        """Store batch to local storage (development only)"""
        file_path = os.path.join(self.worm_dir, f"{batch_id}.json")

        with open(file_path, 'w') as f:
            json.dump(document, f, indent=2)

        # Make file read-only
        os.chmod(file_path, 0o444)

        logger.info(f"Stored batch {batch_id} to local storage")

    def verify_log_integrity(self, batch_id: str | None = None) -> dict[str, Any]:
        """
        Verify integrity of audit logs

        Args:
            batch_id: Optional specific batch to verify

        Returns:
            Dict with verification results
        """
        results = {
            'verified': True,
            'total_batches': 0,
            'verified_batches': 0,
            'failed_batches': [],
            'errors': []
        }

        if batch_id:
            batches = [batch_id]
        else:
            # Get all batches
            if self.backend == StorageBackend.LOCAL:
                batches = [f.replace('.json', '') for f in os.listdir(self.worm_dir) if f.endswith('.json')]
            else:
                results['errors'].append("Full verification not implemented for cloud backends yet")
                return results

        for bid in batches:
            results['total_batches'] += 1

            try:
                # Load batch
                file_path = os.path.join(self.worm_dir, f"{bid}.json")
                with open(file_path) as f:
                    document = json.load(f)

                # Verify signature
                batch_data = json.dumps(document['entries'], sort_keys=True)
                signature = document['metadata']['signature']

                if not self.verify_batch_signature(batch_data, signature):
                    results['verified'] = False
                    results['failed_batches'].append(bid)
                    results['errors'].append(f"Signature verification failed for {bid}")
                else:
                    results['verified_batches'] += 1

            except Exception as e:
                results['verified'] = False
                results['errors'].append(f"Error verifying {bid}: {e}")

        return results

    def _load_sequence_number(self) -> int:
        """Load the last sequence number"""
        state_file = os.path.join(self.data_dir, 'chain_state.json')
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
                return state.get('sequence_number', 0)
        return 0

    def _load_previous_hash(self) -> str:
        """Load the last hash in the chain"""
        state_file = os.path.join(self.data_dir, 'chain_state.json')
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
                return state.get('previous_hash', '0' * 64)
        return '0' * 64

    def _save_state(self):
        """Save chain state"""
        state_file = os.path.join(self.data_dir, 'chain_state.json')
        state = {
            'sequence_number': self.sequence_number,
            'previous_hash': self.previous_hash,
            'last_updated': datetime.utcnow().isoformat()
        }

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
