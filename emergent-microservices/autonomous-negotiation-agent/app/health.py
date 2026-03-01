"""
Health check endpoints
"""
from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from .config import settings
from .repository import database
from .logging_config import logger

health_router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str
    checks: Dict[str, Any] = {}


@health_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Basic health check - returns 200 if service is running"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@health_router.get("/health/ready", response_model=HealthResponse, tags=["health"])
async def readiness_check():
    """Readiness check - returns 200 if service is ready to accept traffic"""
    checks = {}
    all_ready = True
    
    # Check database connection
    try:
        db_ready = await database.is_connected()
        checks["database"] = "ready" if db_ready else "not_ready"
        if not db_ready:
            all_ready = False
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        checks["database"] = "error"
        all_ready = False
    
    response_status = "ready" if all_ready else "not_ready"
    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return HealthResponse(
        status=response_status,
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z",
        checks=checks,
    )


@health_router.get("/health/live", response_model=HealthResponse, tags=["health"])
async def liveness_check():
    """Liveness check - returns 200 if service is alive (not deadlocked)"""
    # Simple check - if we can respond, we're alive
    return HealthResponse(
        status="alive",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@health_router.get("/health/startup", response_model=HealthResponse, tags=["health"])
async def startup_check():
    """Startup check - returns 200 when service has completed initialization"""
    checks = {}
    startup_complete = True
    
    # Check database connection
    try:
        db_connected = await database.is_connected()
        checks["database"] = "connected" if db_connected else "not_connected"
        if not db_connected:
            startup_complete = False
    except Exception as e:
        logger.error(f"Database startup check failed: {e}")
        checks["database"] = "error"
        startup_complete = False
    
# Check migrations
    try:
        from .repository import check_migrations
        migrations_ok = await check_migrations()
        checks["migrations"] = "ok" if migrations_ok else "pending"
        if not migrations_ok:
            startup_complete = False
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        checks["migrations"] = "error"
        startup_complete = False
response_status = "started" if startup_complete else "starting"
    status_code = status.HTTP_200_OK if startup_complete else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return HealthResponse(
        status=response_status,
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat() + "Z",
        checks=checks,
    )
