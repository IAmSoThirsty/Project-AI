"""
Production-Ready Rate Limiting Middleware
Implements token bucket algorithm for API rate limiting
"""

import time
from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: int = 60, per: int = 60):
        """
        Initialize rate limiter
        
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.tokens: Dict[str, float] = defaultdict(lambda: self.rate)
        self.last_update: Dict[str, float] = defaultdict(time.time)
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed
        
        Args:
            key: Identifier for rate limit bucket (e.g., IP address)
        
        Returns:
            True if request is allowed, False otherwise
        """
        async with self._lock:
            now = time.time()
            
            # Add tokens based on time elapsed
            time_passed = now - self.last_update[key]
            self.tokens[key] = min(
                self.rate,
                self.tokens[key] + time_passed * (self.rate / self.per)
            )
            self.last_update[key] = now
            
            # Check if we have tokens available
            if self.tokens[key] >= 1.0:
                self.tokens[key] -= 1.0
                return True
            
            return False
    
    def get_retry_after(self, key: str) -> int:
        """Get seconds until next request allowed"""
        if self.tokens[key] >= 1.0:
            return 0
        
        tokens_needed = 1.0 - self.tokens[key]
        return int(tokens_needed * (self.per / self.rate)) + 1


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""
    
    def __init__(
        self,
        app,
        rate: int = 60,
        per: int = 60,
        exempt_paths: list = None
    ):
        """
        Initialize rate limit middleware
        
        Args:
            app: FastAPI application
            rate: Number of requests allowed
            per: Time period in seconds
            exempt_paths: List of paths exempt from rate limiting
        """
        super().__init__(app)
        self.limiter = RateLimiter(rate=rate, per=per)
        self.exempt_paths = exempt_paths or ["/health", "/metrics"]
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get real IP from X-Forwarded-For header
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take first IP in chain
            return forwarded.split(",")[0].strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        # Check if path is exempt
        if self._is_exempt(request.url.path):
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not await self.limiter.is_allowed(client_id):
            retry_after = self.limiter.get_retry_after(client_id)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.limiter.rate),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = int(self.limiter.tokens.get(client_id, 0))
        response.headers["X-RateLimit-Limit"] = str(self.limiter.rate)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.limiter.per)
        )
        
        return response


# Usage example in FastAPI
"""
from fastapi import FastAPI
from rate_limiter import RateLimitMiddleware

app = FastAPI()

# Add rate limiting: 60 requests per minute
app.add_middleware(
    RateLimitMiddleware,
    rate=60,
    per=60,
    exempt_paths=["/health", "/metrics", "/docs"]
)
"""
