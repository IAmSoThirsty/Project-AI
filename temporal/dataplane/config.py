"""
Data Plane Configuration

Centralized configuration for all data plane components with environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class MessageQueueType(str, Enum):
    """Message queue backend selection."""
    KAFKA = "kafka"
    NATS = "nats"


@dataclass
class KafkaConfig:
    """Kafka-specific configuration."""
    brokers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    security_protocol: str = "PLAINTEXT"  # PLAINTEXT, SSL, SASL_SSL
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    compression_type: str = "lz4"  # none, gzip, snappy, lz4, zstd
    acks: str = "all"  # 0, 1, all
    retries: int = 3
    max_in_flight_requests: int = 5
    linger_ms: int = 10  # Batch messages for 10ms
    batch_size: int = 16384  # 16KB batches
    buffer_memory: int = 33554432  # 32MB buffer

    @classmethod
    def from_env(cls) -> "KafkaConfig":
        """Load configuration from environment variables."""
        brokers_str = os.getenv("KAFKA_BROKERS", "localhost:9092")
        brokers = [b.strip() for b in brokers_str.split(",")]
        
        return cls(
            brokers=brokers,
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISM"),
            sasl_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_password=os.getenv("KAFKA_SASL_PASSWORD"),
            compression_type=os.getenv("KAFKA_COMPRESSION", "lz4"),
            acks=os.getenv("KAFKA_ACKS", "all"),
            retries=int(os.getenv("KAFKA_RETRIES", "3")),
            max_in_flight_requests=int(os.getenv("KAFKA_MAX_IN_FLIGHT", "5")),
            linger_ms=int(os.getenv("KAFKA_LINGER_MS", "10")),
            batch_size=int(os.getenv("KAFKA_BATCH_SIZE", "16384")),
            buffer_memory=int(os.getenv("KAFKA_BUFFER_MEMORY", "33554432")),
        )


@dataclass
class NATSConfig:
    """NATS-specific configuration."""
    url: str = "nats://localhost:4222"
    max_reconnect_attempts: int = 60
    reconnect_time_wait: int = 2  # seconds
    ping_interval: int = 120  # seconds
    max_outstanding_pings: int = 2
    allow_reconnect: bool = True
    name: str = "sovereign-dataplane"
    # TLS settings
    tls_cert: Optional[str] = None
    tls_key: Optional[str] = None
    tls_ca: Optional[str] = None
    # Credentials
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

    @classmethod
    def from_env(cls) -> "NATSConfig":
        """Load configuration from environment variables."""
        return cls(
            url=os.getenv("NATS_URL", "nats://localhost:4222"),
            max_reconnect_attempts=int(os.getenv("NATS_MAX_RECONNECT", "60")),
            reconnect_time_wait=int(os.getenv("NATS_RECONNECT_WAIT", "2")),
            ping_interval=int(os.getenv("NATS_PING_INTERVAL", "120")),
            max_outstanding_pings=int(os.getenv("NATS_MAX_PINGS", "2")),
            allow_reconnect=os.getenv("NATS_ALLOW_RECONNECT", "true").lower() == "true",
            name=os.getenv("NATS_CLIENT_NAME", "sovereign-dataplane"),
            tls_cert=os.getenv("NATS_TLS_CERT"),
            tls_key=os.getenv("NATS_TLS_KEY"),
            tls_ca=os.getenv("NATS_TLS_CA"),
            user=os.getenv("NATS_USER"),
            password=os.getenv("NATS_PASSWORD"),
            token=os.getenv("NATS_TOKEN"),
        )


@dataclass
class MinIOConfig:
    """MinIO/S3 storage configuration."""
    endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "sovereign-artifacts"
    secure: bool = False  # Use HTTPS
    region: str = "us-east-1"
    # Performance tuning
    max_pool_connections: int = 50
    multipart_threshold: int = 8 * 1024 * 1024  # 8MB
    multipart_chunksize: int = 8 * 1024 * 1024  # 8MB
    max_concurrency: int = 10

    @classmethod
    def from_env(cls) -> "MinIOConfig":
        """Load configuration from environment variables."""
        return cls(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            bucket=os.getenv("MINIO_BUCKET", "sovereign-artifacts"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
            region=os.getenv("MINIO_REGION", "us-east-1"),
            max_pool_connections=int(os.getenv("MINIO_MAX_CONNECTIONS", "50")),
            multipart_threshold=int(os.getenv("MINIO_MULTIPART_THRESHOLD", str(8 * 1024 * 1024))),
            multipart_chunksize=int(os.getenv("MINIO_MULTIPART_CHUNKSIZE", str(8 * 1024 * 1024))),
            max_concurrency=int(os.getenv("MINIO_MAX_CONCURRENCY", "10")),
        )


@dataclass
class RedisConfig:
    """Redis cache configuration."""
    url: str = "redis://localhost:6379"
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    socket_keepalive: bool = True
    # Sentinel support
    sentinel_enabled: bool = False
    sentinel_hosts: List[str] = field(default_factory=list)
    sentinel_master: str = "mymaster"
    # Cluster support
    cluster_enabled: bool = False
    cluster_nodes: List[str] = field(default_factory=list)
    # TTL settings
    default_ttl: int = 3600  # 1 hour default
    max_ttl: int = 86400  # 24 hours max

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Load configuration from environment variables."""
        sentinel_hosts_str = os.getenv("REDIS_SENTINEL_HOSTS", "")
        sentinel_hosts = [h.strip() for h in sentinel_hosts_str.split(",") if h.strip()]
        
        cluster_nodes_str = os.getenv("REDIS_CLUSTER_NODES", "")
        cluster_nodes = [n.strip() for n in cluster_nodes_str.split(",") if n.strip()]
        
        return cls(
            url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
            socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
            socket_connect_timeout=int(os.getenv("REDIS_CONNECT_TIMEOUT", "5")),
            socket_keepalive=os.getenv("REDIS_KEEPALIVE", "true").lower() == "true",
            sentinel_enabled=os.getenv("REDIS_SENTINEL_ENABLED", "false").lower() == "true",
            sentinel_hosts=sentinel_hosts,
            sentinel_master=os.getenv("REDIS_SENTINEL_MASTER", "mymaster"),
            cluster_enabled=os.getenv("REDIS_CLUSTER_ENABLED", "false").lower() == "true",
            cluster_nodes=cluster_nodes,
            default_ttl=int(os.getenv("REDIS_DEFAULT_TTL", "3600")),
            max_ttl=int(os.getenv("REDIS_MAX_TTL", "86400")),
        )


@dataclass
class RDMAConfig:
    """RDMA networking configuration (optional feature)."""
    enabled: bool = False
    device_name: str = "mlx5_0"  # Mellanox NIC device
    port: int = 1
    gid_index: int = 3  # For RoCE v2
    mtu: int = 4096
    queue_depth: int = 128
    max_inline_data: int = 128
    max_send_sge: int = 1
    max_recv_sge: int = 1
    # Performance tuning
    use_inline_recv: bool = True
    use_odp: bool = True  # On-Demand Paging
    timeout_ms: int = 1000

    @classmethod
    def from_env(cls) -> "RDMAConfig":
        """Load configuration from environment variables."""
        return cls(
            enabled=os.getenv("ENABLE_RDMA", "false").lower() == "true",
            device_name=os.getenv("RDMA_DEVICE", "mlx5_0"),
            port=int(os.getenv("RDMA_PORT", "1")),
            gid_index=int(os.getenv("RDMA_GID_INDEX", "3")),
            mtu=int(os.getenv("RDMA_MTU", "4096")),
            queue_depth=int(os.getenv("RDMA_QUEUE_DEPTH", "128")),
            max_inline_data=int(os.getenv("RDMA_MAX_INLINE", "128")),
            max_send_sge=int(os.getenv("RDMA_MAX_SEND_SGE", "1")),
            max_recv_sge=int(os.getenv("RDMA_MAX_RECV_SGE", "1")),
            use_inline_recv=os.getenv("RDMA_INLINE_RECV", "true").lower() == "true",
            use_odp=os.getenv("RDMA_USE_ODP", "true").lower() == "true",
            timeout_ms=int(os.getenv("RDMA_TIMEOUT_MS", "1000")),
        )


@dataclass
class DataPlaneConfig:
    """Unified data plane configuration."""
    # Message queue selection
    message_queue_type: MessageQueueType = MessageQueueType.KAFKA
    
    # Component configs
    kafka: KafkaConfig = field(default_factory=KafkaConfig)
    nats: NATSConfig = field(default_factory=NATSConfig)
    minio: MinIOConfig = field(default_factory=MinIOConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    rdma: RDMAConfig = field(default_factory=RDMAConfig)
    
    # Performance settings
    large_message_threshold: int = 1024 * 1024  # 1MB
    enable_compression: bool = True
    enable_metrics: bool = True
    metrics_port: int = 9090

    @classmethod
    def from_env(cls) -> "DataPlaneConfig":
        """Load complete configuration from environment."""
        mq_type_str = os.getenv("MESSAGE_QUEUE_TYPE", "kafka").lower()
        mq_type = MessageQueueType.KAFKA if mq_type_str == "kafka" else MessageQueueType.NATS
        
        return cls(
            message_queue_type=mq_type,
            kafka=KafkaConfig.from_env(),
            nats=NATSConfig.from_env(),
            minio=MinIOConfig.from_env(),
            redis=RedisConfig.from_env(),
            rdma=RDMAConfig.from_env(),
            large_message_threshold=int(os.getenv("LARGE_MESSAGE_THRESHOLD", str(1024 * 1024))),
            enable_compression=os.getenv("ENABLE_COMPRESSION", "true").lower() == "true",
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
        )

    def validate(self) -> None:
        """Validate configuration consistency."""
        if self.message_queue_type == MessageQueueType.KAFKA:
            if not self.kafka.brokers:
                raise ValueError("Kafka brokers must be specified")
        elif self.message_queue_type == MessageQueueType.NATS:
            if not self.nats.url:
                raise ValueError("NATS URL must be specified")
        
        if self.rdma.enabled and self.rdma.device_name == "":
            raise ValueError("RDMA device name must be specified when RDMA is enabled")
        
        if self.large_message_threshold < 1024:
            raise ValueError("Large message threshold must be at least 1KB")
