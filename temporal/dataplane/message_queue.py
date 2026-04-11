"""
Message Queue Clients for Kafka and NATS

Provides unified interface for publishing and subscribing to messages across different queue backends.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Standard message format across all queue backends."""
    topic: str
    key: Optional[str]
    value: bytes
    headers: Dict[str, str]
    timestamp: datetime
    partition: Optional[int] = None
    offset: Optional[int] = None


class MessageQueueClient(ABC):
    """Abstract base class for message queue clients."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to message queue."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to message queue."""
        pass

    @abstractmethod
    async def publish(
        self,
        topic: str,
        value: bytes,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Publish a message to a topic."""
        pass

    @abstractmethod
    async def subscribe(
        self,
        topics: List[str],
        callback: Callable[[Message], None],
        group_id: Optional[str] = None,
    ) -> None:
        """Subscribe to topics and process messages with callback."""
        pass

    @abstractmethod
    async def create_topic(
        self,
        topic: str,
        partitions: int = 1,
        replication_factor: int = 1,
    ) -> None:
        """Create a new topic."""
        pass


class KafkaClient(MessageQueueClient):
    """Apache Kafka client implementation."""

    def __init__(self, config):
        """Initialize Kafka client with configuration."""
        from .config import KafkaConfig
        self.config: KafkaConfig = config
        self.producer = None
        self.consumer = None
        self.admin_client = None
        self._connected = False

    async def connect(self) -> None:
        """Establish connection to Kafka cluster."""
        try:
            from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
            from kafka.admin import KafkaAdminClient

            # Create producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.config.brokers,
                compression_type=self.config.compression_type,
                acks=self.config.acks,
                retries=self.config.retries,
                max_in_flight_requests_per_connection=self.config.max_in_flight_requests,
                linger_ms=self.config.linger_ms,
                batch_size=self.config.batch_size,
                security_protocol=self.config.security_protocol,
                sasl_mechanism=self.config.sasl_mechanism,
                sasl_plain_username=self.config.sasl_username,
                sasl_plain_password=self.config.sasl_password,
            )
            await self.producer.start()

            # Create admin client for topic management
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.config.brokers,
                security_protocol=self.config.security_protocol,
            )

            self._connected = True
            logger.info(f"Connected to Kafka cluster: {self.config.brokers}")

        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Kafka cluster."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        if self.admin_client:
            self.admin_client.close()
        self._connected = False
        logger.info("Disconnected from Kafka cluster")

    async def publish(
        self,
        topic: str,
        value: bytes,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Publish a message to Kafka topic."""
        if not self._connected:
            raise RuntimeError("Not connected to Kafka")

        # Convert headers to Kafka format
        kafka_headers = None
        if headers:
            kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]

        try:
            await self.producer.send_and_wait(
                topic,
                value=value,
                key=key.encode('utf-8') if key else None,
                headers=kafka_headers,
            )
            logger.debug(f"Published message to topic {topic}")
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            raise

    async def subscribe(
        self,
        topics: List[str],
        callback: Callable[[Message], None],
        group_id: Optional[str] = None,
    ) -> None:
        """Subscribe to Kafka topics and process messages."""
        from aiokafka import AIOKafkaConsumer

        if not group_id:
            group_id = "sovereign-default-group"

        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.config.brokers,
            group_id=group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            security_protocol=self.config.security_protocol,
            sasl_mechanism=self.config.sasl_mechanism,
            sasl_plain_username=self.config.sasl_username,
            sasl_plain_password=self.config.sasl_password,
        )

        await self.consumer.start()
        logger.info(f"Subscribed to topics: {topics} (group: {group_id})")

        try:
            async for msg in self.consumer:
                # Convert Kafka message to standard format
                headers = {}
                if msg.headers:
                    headers = {k: v.decode('utf-8') for k, v in msg.headers}

                message = Message(
                    topic=msg.topic,
                    key=msg.key.decode('utf-8') if msg.key else None,
                    value=msg.value,
                    headers=headers,
                    timestamp=datetime.fromtimestamp(msg.timestamp / 1000),
                    partition=msg.partition,
                    offset=msg.offset,
                )

                # Call user callback
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")

        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        finally:
            await self.consumer.stop()

    async def create_topic(
        self,
        topic: str,
        partitions: int = 1,
        replication_factor: int = 1,
    ) -> None:
        """Create a new Kafka topic."""
        from kafka.admin import NewTopic

        if not self.admin_client:
            raise RuntimeError("Admin client not initialized")

        new_topic = NewTopic(
            name=topic,
            num_partitions=partitions,
            replication_factor=replication_factor,
        )

        try:
            self.admin_client.create_topics([new_topic], validate_only=False)
            logger.info(f"Created topic: {topic} (partitions={partitions}, rf={replication_factor})")
        except Exception as e:
            if "TopicExistsError" not in str(e):
                logger.error(f"Failed to create topic {topic}: {e}")
                raise


class NATSClient(MessageQueueClient):
    """NATS messaging client implementation."""

    def __init__(self, config):
        """Initialize NATS client with configuration."""
        from .config import NATSConfig
        self.config: NATSConfig = config
        self.nc = None
        self.js = None
        self._connected = False

    async def connect(self) -> None:
        """Establish connection to NATS server."""
        try:
            import nats
            from nats.aio.client import Client as NATS

            self.nc = await nats.connect(
                servers=[self.config.url],
                name=self.config.name,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
                reconnect_time_wait=self.config.reconnect_time_wait,
                ping_interval=self.config.ping_interval,
                max_outstanding_pings=self.config.max_outstanding_pings,
                allow_reconnect=self.config.allow_reconnect,
                user=self.config.user,
                password=self.config.password,
                token=self.config.token,
            )

            # Enable JetStream for persistence
            self.js = self.nc.jetstream()

            self._connected = True
            logger.info(f"Connected to NATS server: {self.config.url}")

        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to NATS server."""
        if self.nc:
            await self.nc.drain()
            await self.nc.close()
        self._connected = False
        logger.info("Disconnected from NATS server")

    async def publish(
        self,
        topic: str,
        value: bytes,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Publish a message to NATS subject."""
        if not self._connected:
            raise RuntimeError("Not connected to NATS")

        # NATS uses subjects instead of topics
        subject = topic.replace("/", ".")

        try:
            # Use JetStream for persistence
            await self.js.publish(subject, value, headers=headers)
            logger.debug(f"Published message to subject {subject}")
        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            raise

    async def subscribe(
        self,
        topics: List[str],
        callback: Callable[[Message], None],
        group_id: Optional[str] = None,
    ) -> None:
        """Subscribe to NATS subjects and process messages."""
        if not self._connected:
            raise RuntimeError("Not connected to NATS")

        async def message_handler(msg):
            """Handle incoming NATS message."""
            subject = msg.subject
            data = msg.data
            headers = msg.headers or {}

            message = Message(
                topic=subject,
                key=None,  # NATS doesn't have message keys
                value=data,
                headers=headers,
                timestamp=datetime.now(),
            )

            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")

        # Subscribe to each subject
        for topic in topics:
            subject = topic.replace("/", ".")
            
            if group_id:
                # Queue subscription for load balancing
                await self.nc.subscribe(subject, queue=group_id, cb=message_handler)
            else:
                # Regular subscription
                await self.nc.subscribe(subject, cb=message_handler)

            logger.info(f"Subscribed to subject: {subject}")

    async def create_topic(
        self,
        topic: str,
        partitions: int = 1,
        replication_factor: int = 1,
    ) -> None:
        """Create a NATS JetStream stream."""
        if not self.js:
            raise RuntimeError("JetStream not initialized")

        subject = topic.replace("/", ".")

        try:
            from nats.js.api import StreamConfig

            config = StreamConfig(
                name=subject.replace(".", "_").upper(),
                subjects=[f"{subject}.>"],
                retention="limits",
                max_msgs=1000000,
                max_bytes=1024 * 1024 * 1024,  # 1GB
            )

            await self.js.add_stream(config)
            logger.info(f"Created NATS stream for subject: {subject}")

        except Exception as e:
            if "stream name already in use" not in str(e).lower():
                logger.error(f"Failed to create stream for {subject}: {e}")
                raise
