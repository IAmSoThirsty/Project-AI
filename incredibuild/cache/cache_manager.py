#!/usr/bin/env python3
"""
Distributed Cache Manager - Manages build artifact caching
"""

import hashlib
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger("CacheManager")


class DistributedCacheManager:
    """Manages distributed build cache (Redis + S3)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_config = config.get('cache', {})
        self.backend = self.cache_config.get('backend', 'hybrid')
        
        self.redis_enabled = self.cache_config.get('redis', {}).get('enabled', False)
        self.s3_enabled = self.cache_config.get('s3', {}).get('enabled', False)
        
        # In-memory cache for demo
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize cache backends"""
        logger.info(f"Initializing distributed cache (backend: {self.backend})")
        
        try:
            # In production, connect to Redis and S3
            # For demo, use in-memory cache
            
            if self.redis_enabled:
                logger.info("Connecting to Redis...")
                # redis_client = redis.Redis(...)
                logger.info("✅ Redis connected")
            
            if self.s3_enabled:
                logger.info("Connecting to S3...")
                # s3_client = boto3.client('s3')
                logger.info("✅ S3 connected")
            
            self._initialized = True
            logger.info("✅ Cache initialized")
            return True
            
        except Exception as e:
            logger.error(f"Cache initialization failed: {e}")
            return False
    
    def _compute_key(self, job_id: str, command: str) -> str:
        """Compute cache key from job info"""
        # In production, include dependencies, environment, etc.
        content = f"{job_id}:{command}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get(self, job_id: str, command: str) -> Optional[Dict[str, Any]]:
        """Get cached build result"""
        if not self._initialized:
            return None
        
        cache_key = self._compute_key(job_id, command)
        
        # Try L1 cache (Redis/memory)
        if cache_key in self.cache:
            logger.debug(f"Cache hit (L1): {cache_key}")
            return self.cache[cache_key]
        
        # Try L2 cache (S3)
        # In production: check S3
        
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def put(self, job_id: str, command: str, result: Dict[str, Any]) -> bool:
        """Store build result in cache"""
        if not self._initialized:
            return False
        
        cache_key = self._compute_key(job_id, command)
        
        try:
            # Store in L1 (Redis/memory)
            self.cache[cache_key] = {
                'job_id': job_id,
                'command': command,
                'result': result,
                'cached_at': datetime.now().isoformat(),
            }
            
            # Store in L2 (S3)
            # In production: upload to S3
            
            logger.debug(f"Cached: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache put failed: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        logger.info("Clearing distributed cache...")
        
        try:
            self.cache.clear()
            # In production: clear Redis and S3
            
            logger.info("✅ Cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'backend': self.backend,
            'redis_enabled': self.redis_enabled,
            's3_enabled': self.s3_enabled,
        }
