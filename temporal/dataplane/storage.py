"""
Object Storage Client for MinIO/S3

Provides high-performance object storage for artifacts, build outputs, and datasets.
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass
class ObjectMetadata:
    """Metadata for stored objects."""
    key: str
    size: int
    etag: str
    last_modified: datetime
    content_type: str
    metadata: Dict[str, str]
    version_id: Optional[str] = None


class StorageClient(ABC):
    """Abstract base class for object storage."""

    @abstractmethod
    async def connect(self) -> None:
        """Initialize storage client."""
        pass

    @abstractmethod
    async def put_object(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> ObjectMetadata:
        """Upload an object."""
        pass

    @abstractmethod
    async def get_object(self, key: str) -> bytes:
        """Download an object."""
        pass

    @abstractmethod
    async def delete_object(self, key: str) -> None:
        """Delete an object."""
        pass

    @abstractmethod
    async def list_objects(self, prefix: str = "") -> List[ObjectMetadata]:
        """List objects with given prefix."""
        pass

    @abstractmethod
    async def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate presigned URL for direct access."""
        pass


class MinIOClient(StorageClient):
    """MinIO/S3 storage client implementation."""

    def __init__(self, config):
        """Initialize MinIO client with configuration."""
        from .config import MinIOConfig
        self.config: MinIOConfig = config
        self.client = None
        self._connected = False

    async def connect(self) -> None:
        """Initialize MinIO client and ensure bucket exists."""
        try:
            from minio import Minio
            from urllib3 import PoolManager
            from urllib3.util.retry import Retry

            # Configure connection pooling for high performance
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504],
            )
            
            http_client = PoolManager(
                maxsize=self.config.max_pool_connections,
                retries=retry_strategy,
            )

            self.client = Minio(
                self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=self.config.secure,
                region=self.config.region,
                http_client=http_client,
            )

            # Ensure bucket exists
            if not self.client.bucket_exists(self.config.bucket):
                self.client.make_bucket(self.config.bucket)
                logger.info(f"Created bucket: {self.config.bucket}")
            
            # Enable versioning for data protection
            self.client.set_bucket_versioning(
                self.config.bucket,
                {"Status": "Enabled"},
            )

            self._connected = True
            logger.info(f"Connected to MinIO: {self.config.endpoint}")

        except Exception as e:
            logger.error(f"Failed to connect to MinIO: {e}")
            raise

    async def put_object(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> ObjectMetadata:
        """Upload an object to MinIO."""
        if not self._connected:
            raise RuntimeError("Not connected to MinIO")

        try:
            data_stream = BytesIO(data)
            data_length = len(data)

            # Calculate MD5 for integrity
            md5 = hashlib.md5(data).hexdigest()

            # Upload with multipart if large
            part_size = self.config.multipart_chunksize if data_length > self.config.multipart_threshold else 0

            result = self.client.put_object(
                self.config.bucket,
                key,
                data_stream,
                length=data_length,
                content_type=content_type,
                metadata=metadata,
                part_size=part_size,
            )

            logger.debug(f"Uploaded object: {key} ({data_length} bytes)")

            return ObjectMetadata(
                key=key,
                size=data_length,
                etag=result.etag,
                last_modified=datetime.now(),
                content_type=content_type,
                metadata=metadata or {},
                version_id=result.version_id,
            )

        except Exception as e:
            logger.error(f"Failed to upload {key}: {e}")
            raise

    async def get_object(self, key: str) -> bytes:
        """Download an object from MinIO."""
        if not self._connected:
            raise RuntimeError("Not connected to MinIO")

        try:
            response = self.client.get_object(self.config.bucket, key)
            data = response.read()
            response.close()
            response.release_conn()

            logger.debug(f"Downloaded object: {key} ({len(data)} bytes)")
            return data

        except Exception as e:
            logger.error(f"Failed to download {key}: {e}")
            raise

    async def delete_object(self, key: str) -> None:
        """Delete an object from MinIO."""
        if not self._connected:
            raise RuntimeError("Not connected to MinIO")

        try:
            self.client.remove_object(self.config.bucket, key)
            logger.debug(f"Deleted object: {key}")
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            raise

    async def list_objects(self, prefix: str = "") -> List[ObjectMetadata]:
        """List objects in bucket with given prefix."""
        if not self._connected:
            raise RuntimeError("Not connected to MinIO")

        try:
            objects = []
            for obj in self.client.list_objects(self.config.bucket, prefix=prefix, recursive=True):
                metadata = ObjectMetadata(
                    key=obj.object_name,
                    size=obj.size,
                    etag=obj.etag,
                    last_modified=obj.last_modified,
                    content_type=obj.content_type or "application/octet-stream",
                    metadata={},
                    version_id=obj.version_id,
                )
                objects.append(metadata)

            logger.debug(f"Listed {len(objects)} objects with prefix: {prefix}")
            return objects

        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            raise

    async def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate presigned URL for direct client access."""
        if not self._connected:
            raise RuntimeError("Not connected to MinIO")

        try:
            from datetime import timedelta

            url = self.client.presigned_get_object(
                self.config.bucket,
                key,
                expires=timedelta(seconds=expiration),
            ) if method == "GET" else self.client.presigned_put_object(
                self.config.bucket,
                key,
                expires=timedelta(seconds=expiration),
            )

            logger.debug(f"Generated presigned URL for {key} (expires in {expiration}s)")
            return url

        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {key}: {e}")
            raise

    async def upload_file(self, key: str, file_path: str) -> ObjectMetadata:
        """Upload a file from disk."""
        with open(file_path, 'rb') as f:
            data = f.read()
        return await self.put_object(key, data)

    async def download_file(self, key: str, file_path: str) -> None:
        """Download object to disk."""
        data = await self.get_object(key)
        with open(file_path, 'wb') as f:
            f.write(data)
