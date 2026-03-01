"""
Custom middleware components
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .logging_config import logger, request_id_var
from .metrics import REQUEST_COUNT, REQUEST_DURATION, INFLIGHT_REQUESTS, RATE_LIMIT_REJECTIONS
from .errors import RateLimitError
from .security import verify_api_key, verify_jwt_token

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set in context for logging
        request_id_var.set(request_id)
        
        # Add to request state
        request.state.request_id = request_id
        
        # Call next middleware
        response = await call_next(request)
        
        # Add to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics for requests"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Increment inflight requests
        INFLIGHT_REQUESTS.inc()
        
        # Record start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            status_class = f"{response.status_code // 100}xx"
            
            # Get route template (not raw path to avoid high cardinality)
            route_template = self._get_route_template(request)
            
            REQUEST_COUNT.labels(
                method=request.method,
                route_template=route_template,
                status_class=status_class,
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                route_template=route_template,
            ).observe(duration)
            
            return response
        
        finally:
            # Decrement inflight requests
            INFLIGHT_REQUESTS.dec()
    
    @staticmethod
    def _get_route_template(request: Request) -> str:
        """Get route template with path parameters"""
        if request.scope.get("route"):
            return request.scope["route"].path
        return request.url.path


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiter"""
    
    def __init__(self, app, requests_per_minute: int = 100, burst: int = 200):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.tokens = {}  # client_id -> (tokens, last_update)
        self.rate = requests_per_minute / 60.0  # tokens per second
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip health checks and metrics
        if request.url.path in ["/health", "/health/ready", "/health/live", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier (IP or authenticated user)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._allow_request(client_id):
            RATE_LIMIT_REJECTIONS.labels(client_type="api").inc()
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests",
                    }
                },
                headers={"Retry-After": "60"},
            )
        
        return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Use authenticated user if available
        if hasattr(request.state, "user"):
            return f"user:{request.state.user}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    def _allow_request(self, client_id: str) -> bool:
        """Check if request is allowed (token bucket algorithm)"""
        now = time.time()
        
        if client_id not in self.tokens:
            self.tokens[client_id] = (self.burst - 1, now)
            return True
        
        tokens, last_update = self.tokens[client_id]
        
        # Add tokens based on time elapsed
        elapsed = now - last_update
        tokens = min(self.burst, tokens + elapsed * self.rate)
        
        if tokens >= 1:
            self.tokens[client_id] = (tokens - 1, now)
            return True
        else:
            self.tokens[client_id] = (tokens, now)
            return False


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    # Public endpoints that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/health/ready",
        "/health/live",
        "/health/startup",
        "/metrics",
        "/api/v1/docs",
        "/api/v1/redoc",
        "/api/v1/openapi.json",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip public endpoints
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Try authentication
        authenticated = False
        user = None
        
# Try API key authentication
        api_key = request.headers.get("X-API-Key")
        if api_key:
            if verify_api_key(api_key):
                authenticated = True
                user = f"api_key:{api_key[:8]}"
# Try JWT authentication
        if not authenticated:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                payload = verify_jwt_token(token)
                if payload:
                    authenticated = True
                    user = payload.get("sub")
if not authenticated:
            logger.warning(f"Unauthorized access attempt: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Authentication required",
                    }
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Add user to request state
        request.state.user = user
        
        return await call_next(request)
