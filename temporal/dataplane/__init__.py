"""
High-Performance Data Plane for Agent Communication

Provides unified interface to:
- Message queues (Kafka/NATS)
- Object storage (MinIO/S3)
- Caching (Redis)
- RDMA networking (optional)
"""

from .config import DataPlaneConfig
from .client import DataPlaneClient
from .message_queue import MessageQueueClient, KafkaClient, NATSClient
from .storage import StorageClient, MinIOClient
from .cache import CacheClient, RedisClient
from .rdma import RDMAClient, RDMAFeature

__all__ = [
    "DataPlaneConfig",
    "DataPlaneClient",
    "MessageQueueClient",
    "KafkaClient",
    "NATSClient",
    "StorageClient",
    "MinIOClient",
    "CacheClient",
    "RedisClient",
    "RDMAClient",
    "RDMAFeature",
]

__version__ = "1.0.0"
