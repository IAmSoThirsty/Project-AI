"""
Unified Data Plane Client

Provides high-level API for agent communication with automatic routing between:
- Message queues (small messages)
- Object storage (large artifacts)
- Cache (hot data)
- RDMA (ultra-low latency, optional)
"""

import asyncio
import hashlib
import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .config import DataPlaneConfig, MessageQueueType
from .message_queue import KafkaClient, NATSClient, Message
from .storage import MinIOClient
from .cache import RedisClient
from .rdma import RDMAClient

logger = logging.getLogger(__name__)


@dataclass
class DataPlaneMessage:
    """High-level message abstraction."""
    topic: str
    data: bytes
    agent_id: str
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    use_rdma: bool = False


class DataPlaneClient:
    """Unified client for all data plane operations."""

    def __init__(self, config: Optional[DataPlaneConfig] = None):
        """Initialize data plane client."""
        self.config = config or DataPlaneConfig.from_env()
        self.config.validate()

        # Initialize components
        if self.config.message_queue_type == MessageQueueType.KAFKA:
            self.mq_client = KafkaClient(self.config.kafka)
        else:
            self.mq_client = NATSClient(self.config.nats)

        self.storage_client = MinIOClient(self.config.minio)
        self.cache_client = RedisClient(self.config.redis)
        self.rdma_client = RDMAClient(self.config.rdma) if self.config.rdma.enabled else None

        self._connected = False

    async def connect(self) -> None:
        """Connect all data plane components."""
        logger.info("Connecting data plane components...")

        # Connect in parallel for faster startup
        tasks = [
            self.mq_client.connect(),
            self.storage_client.connect(),
            self.cache_client.connect(),
        ]

        if self.rdma_client and self.config.rdma.enabled:
            tasks.append(self.rdma_client.connect())

        await asyncio.gather(*tasks)

        self._connected = True
        logger.info("Data plane connected successfully")

    async def disconnect(self) -> None:
        """Disconnect all data plane components."""
        logger.info("Disconnecting data plane components...")

        tasks = [
            self.mq_client.disconnect(),
            self.cache_client.disconnect(),
        ]

        if self.rdma_client and self.config.rdma.enabled:
            tasks.append(self.rdma_client.disconnect())

        await asyncio.gather(*tasks, return_exceptions=True)

        self._connected = False
        logger.info("Data plane disconnected")

    async def send_message(
        self,
        topic: str,
        data: bytes,
        agent_id: str,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
    ) -> None:
        """
        Send a message with automatic routing based on size.
        
        Small messages (< 1MB): Direct via message queue
        Large messages (>= 1MB): Upload to storage, send reference
        """
        if not self._connected:
            raise RuntimeError("Data plane not connected")

        message_size = len(data)
        headers = metadata or {}
        headers["agent_id"] = agent_id
        headers["timestamp"] = datetime.now().isoformat()
        if correlation_id:
            headers["correlation_id"] = correlation_id

        # Small message path - direct delivery
        if message_size < self.config.large_message_threshold:
            logger.debug(f"Sending small message ({message_size} bytes) via queue")
            
            # Cache if requested
            if use_cache:
                cache_key = f"msg:{topic}:{hashlib.md5(data).hexdigest()}"
                await self.cache_client.set(cache_key, data, ttl=300)  # 5 min cache
            
            await self.mq_client.publish(
                topic=topic,
                value=data,
                key=agent_id,
                headers=headers,
            )

        # Large message path - storage + reference
        else:
            logger.debug(f"Sending large message ({message_size} bytes) via storage")
            
            # Upload to object storage
            object_key = f"messages/{topic}/{datetime.now().strftime('%Y/%m/%d')}/{agent_id}/{hashlib.sha256(data).hexdigest()}"
            await self.storage_client.put_object(
                key=object_key,
                data=data,
                metadata=headers,
            )
            
            # Send reference via message queue
            reference = {
                "type": "storage_ref",
                "object_key": object_key,
                "size": message_size,
                "checksum": hashlib.sha256(data).hexdigest(),
            }
            
            import json
            reference_data = json.dumps(reference).encode('utf-8')
            
            await self.mq_client.publish(
                topic=topic,
                value=reference_data,
                key=agent_id,
                headers=headers,
            )

    async def receive_messages(
        self,
        topics: List[str],
        callback: Callable[[bytes, Dict[str, str]], None],
        group_id: Optional[str] = None,
    ) -> None:
        """
        Receive messages with automatic dereference of storage objects.
        """
        if not self._connected:
            raise RuntimeError("Data plane not connected")

        async def internal_callback(msg: Message):
            """Internal callback that handles storage references."""
            try:
                # Check if this is a storage reference
                import json
                try:
                    ref = json.loads(msg.value.decode('utf-8'))
                    if isinstance(ref, dict) and ref.get("type") == "storage_ref":
                        # Fetch from storage
                        object_key = ref["object_key"]
                        
                        # Try cache first
                        cache_key = f"obj:{object_key}"
                        cached_data = await self.cache_client.get(cache_key)
                        
                        if cached_data:
                            logger.debug(f"Cache hit for {object_key}")
                            data = cached_data
                        else:
                            logger.debug(f"Fetching {object_key} from storage")
                            data = await self.storage_client.get_object(object_key)
                            
                            # Cache for future access
                            await self.cache_client.set(cache_key, data, ttl=3600)
                        
                        # Verify checksum
                        checksum = hashlib.sha256(data).hexdigest()
                        if checksum != ref["checksum"]:
                            logger.error(f"Checksum mismatch for {object_key}")
                            return
                        
                        # Call user callback with actual data
                        callback(data, msg.headers)
                        return
                        
                except (json.JSONDecodeError, KeyError):
                    # Not a storage reference, treat as normal message
                    pass
                
                # Regular message
                callback(msg.value, msg.headers)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        # Subscribe to message queue
        await self.mq_client.subscribe(
            topics=topics,
            callback=internal_callback,
            group_id=group_id,
        )

    async def upload_artifact(
        self,
        artifact_name: str,
        data: bytes,
        artifact_type: str = "build",
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Upload artifact to storage and return object key."""
        if not self._connected:
            raise RuntimeError("Data plane not connected")

        object_key = f"artifacts/{artifact_type}/{datetime.now().strftime('%Y/%m/%d')}/{artifact_name}"
        
        await self.storage_client.put_object(
            key=object_key,
            data=data,
            content_type="application/octet-stream",
            metadata=metadata,
        )
        
        logger.info(f"Uploaded artifact: {artifact_name} ({len(data)} bytes)")
        return object_key

    async def download_artifact(
        self,
        object_key: str,
        use_cache: bool = True,
    ) -> bytes:
        """Download artifact from storage with optional caching."""
        if not self._connected:
            raise RuntimeError("Data plane not connected")

        # Try cache first
        if use_cache:
            cache_key = f"artifact:{object_key}"
            cached_data = await self.cache_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for artifact: {object_key}")
                return cached_data

        # Fetch from storage
        data = await self.storage_client.get_object(object_key)
        
        # Cache for future access
        if use_cache:
            cache_key = f"artifact:{object_key}"
            await self.cache_client.set(cache_key, data, ttl=7200)  # 2 hour cache
        
        logger.info(f"Downloaded artifact: {object_key} ({len(data)} bytes)")
        return data

    async def get_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600,
    ) -> str:
        """Get presigned URL for direct client-to-storage transfer."""
        if not self._connected:
            raise RuntimeError("Data plane not connected")

        return await self.storage_client.get_presigned_url(
            key=object_key,
            expiration=expiration,
        )

    async def cache_set(self, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        if not self._connected:
            raise RuntimeError("Data plane not connected")
        await self.cache_client.set(key, value, ttl)

    async def cache_get(self, key: str) -> Optional[bytes]:
        """Get value from cache."""
        if not self._connected:
            raise RuntimeError("Data plane not connected")
        return await self.cache_client.get(key)

    async def cache_delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self._connected:
            raise RuntimeError("Data plane not connected")
        await self.cache_client.delete(key)

    async def rdma_available(self) -> bool:
        """Check if RDMA is available and enabled."""
        return self.rdma_client is not None and self.config.rdma.enabled

    async def send_rdma(self, data: bytes, remote_addr: int, remote_rkey: int) -> None:
        """Send data using RDMA (if available)."""
        if not await self.rdma_available():
            raise RuntimeError("RDMA not available")
        await self.rdma_client.rdma_write(data, remote_addr, remote_rkey)

    def get_stats(self) -> Dict[str, Any]:
        """Get data plane statistics."""
        stats = {
            "connected": self._connected,
            "message_queue_type": self.config.message_queue_type.value,
            "rdma_enabled": self.config.rdma.enabled,
        }
        
        if self.rdma_client and self.config.rdma.enabled:
            rdma_stats = self.rdma_client.get_stats()
            stats["rdma"] = {
                "bytes_sent": rdma_stats.bytes_sent,
                "bytes_received": rdma_stats.bytes_received,
                "avg_latency_us": rdma_stats.avg_latency_us,
                "max_latency_us": rdma_stats.max_latency_us,
            }
        
        return stats
