"""
Redis Cache Client

Provides high-performance caching layer for hot data and session state.
"""

import asyncio
import json
import logging
import pickle
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheClient(ABC):
    """Abstract base class for cache clients."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to cache."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to cache."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        """Get value by key."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: bytes,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value with optional TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment counter."""
        pass

    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        """Get multiple keys at once."""
        pass

    @abstractmethod
    async def set_many(self, mapping: Dict[str, bytes], ttl: Optional[int] = None) -> None:
        """Set multiple keys at once."""
        pass


class RedisClient(CacheClient):
    """Redis cache client implementation."""

    def __init__(self, config):
        """Initialize Redis client with configuration."""
        from .config import RedisConfig
        self.config: RedisConfig = config
        self.redis = None
        self._connected = False

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            import redis.asyncio as redis

            if self.config.cluster_enabled:
                # Redis Cluster mode
                from redis.asyncio.cluster import RedisCluster
                startup_nodes = [
                    {"host": node.split(":")[0], "port": int(node.split(":")[1])}
                    for node in self.config.cluster_nodes
                ]
                self.redis = RedisCluster(
                    startup_nodes=startup_nodes,
                    password=self.config.password,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    socket_keepalive=self.config.socket_keepalive,
                    max_connections=self.config.max_connections,
                )
            elif self.config.sentinel_enabled:
                # Redis Sentinel mode
                from redis.asyncio.sentinel import Sentinel
                sentinel_list = [
                    (host.split(":")[0], int(host.split(":")[1]))
                    for host in self.config.sentinel_hosts
                ]
                sentinel = Sentinel(
                    sentinel_list,
                    socket_timeout=self.config.socket_timeout,
                )
                self.redis = sentinel.master_for(
                    self.config.sentinel_master,
                    password=self.config.password,
                    db=self.config.db,
                )
            else:
                # Standard Redis mode
                self.redis = redis.from_url(
                    self.config.url,
                    password=self.config.password,
                    db=self.config.db,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    socket_keepalive=self.config.socket_keepalive,
                    max_connections=self.config.max_connections,
                )

            # Test connection
            await self.redis.ping()

            self._connected = True
            logger.info(f"Connected to Redis: {self.config.url}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Redis."""
        if self.redis:
            await self.redis.close()
        self._connected = False
        logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[bytes]:
        """Get value by key."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
            else:
                logger.debug(f"Cache MISS: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            raise

    async def set(
        self,
        key: str,
        value: bytes,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value with optional TTL."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            if ttl is None:
                ttl = self.config.default_ttl

            # Cap TTL at max
            if ttl > self.config.max_ttl:
                ttl = self.config.max_ttl

            await self.redis.setex(key, ttl, value)
            logger.debug(f"Set key: {key} (ttl={ttl}s)")
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            raise

    async def delete(self, key: str) -> None:
        """Delete key."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            await self.redis.delete(key)
            logger.debug(f"Deleted key: {key}")
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            raise

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to check existence of {key}: {e}")
            raise

    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment counter."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            result = await self.redis.incrby(key, delta)
            logger.debug(f"Incremented {key} by {delta} to {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to increment {key}: {e}")
            raise

    async def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        """Get multiple keys at once using pipeline."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            async with self.redis.pipeline() as pipe:
                for key in keys:
                    pipe.get(key)
                values = await pipe.execute()

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = value

            logger.debug(f"Batch GET: {len(result)}/{len(keys)} hits")
            return result

        except Exception as e:
            logger.error(f"Failed to get multiple keys: {e}")
            raise

    async def set_many(
        self,
        mapping: Dict[str, bytes],
        ttl: Optional[int] = None,
    ) -> None:
        """Set multiple keys at once using pipeline."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            if ttl is None:
                ttl = self.config.default_ttl

            async with self.redis.pipeline() as pipe:
                for key, value in mapping.items():
                    pipe.setex(key, ttl, value)
                await pipe.execute()

            logger.debug(f"Batch SET: {len(mapping)} keys (ttl={ttl}s)")

        except Exception as e:
            logger.error(f"Failed to set multiple keys: {e}")
            raise

    async def acquire_lock(
        self,
        lock_key: str,
        timeout: int = 10,
        blocking_timeout: Optional[int] = None,
    ) -> bool:
        """Acquire distributed lock."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            from redis.asyncio.lock import Lock
            lock = Lock(self.redis, lock_key, timeout=timeout)
            acquired = await lock.acquire(blocking=blocking_timeout is not None, blocking_timeout=blocking_timeout)
            
            if acquired:
                logger.debug(f"Acquired lock: {lock_key}")
            else:
                logger.debug(f"Failed to acquire lock: {lock_key}")
            
            return acquired

        except Exception as e:
            logger.error(f"Failed to acquire lock {lock_key}: {e}")
            raise

    async def release_lock(self, lock_key: str) -> None:
        """Release distributed lock."""
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        try:
            from redis.asyncio.lock import Lock
            lock = Lock(self.redis, lock_key)
            await lock.release()
            logger.debug(f"Released lock: {lock_key}")
        except Exception as e:
            logger.error(f"Failed to release lock {lock_key}: {e}")
            raise

    async def get_json(self, key: str) -> Optional[Dict]:
        """Get JSON value."""
        data = await self.get(key)
        if data:
            return json.loads(data.decode('utf-8'))
        return None

    async def set_json(self, key: str, value: Dict, ttl: Optional[int] = None) -> None:
        """Set JSON value."""
        data = json.dumps(value).encode('utf-8')
        await self.set(key, data, ttl)

    async def get_object(self, key: str) -> Optional[Any]:
        """Get pickled Python object."""
        data = await self.get(key)
        if data:
            return pickle.loads(data)
        return None

    async def set_object(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set pickled Python object."""
        data = pickle.dumps(value)
        await self.set(key, data, ttl)
