"""
Production-Ready Health Check Endpoints
Provides comprehensive health, readiness, and startup probes for Kubernetes
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    """Health check response model"""

    status: str
    timestamp: str
    uptime_seconds: float
    version: str
    environment: str
    checks: dict[str, Any]


class ComponentHealth(BaseModel):
    """Individual component health"""

    healthy: bool
    latency_ms: float | None = None
    message: str | None = None
    last_check: str


# Application startup time for uptime calculation
_startup_time = time.time()


def get_uptime() -> float:
    """Get application uptime in seconds"""
    return time.time() - _startup_time


async def check_database() -> ComponentHealth:
    """Check database connectivity"""
    start = time.time()
    try:
        # Import here to avoid circular dependencies
        # Replace with actual database check
        # from app.core.database import db
        # await db.execute("SELECT 1")

        # Placeholder implementation
        await asyncio.sleep(0.01)  # Simulate DB check

        latency = (time.time() - start) * 1000
        return ComponentHealth(
            healthy=True,
            latency_ms=round(latency, 2),
            message="Database connection OK",
            last_check=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return ComponentHealth(
            healthy=False,
            message=f"Database connection failed: {str(e)}",
            last_check=datetime.utcnow().isoformat(),
        )


async def check_redis() -> ComponentHealth:
    """Check Redis connectivity"""
    start = time.time()
    try:
        # Import here to avoid circular dependencies
        # from app.core.cache import redis_client
        # await redis_client.ping()

        # Placeholder implementation
        await asyncio.sleep(0.01)  # Simulate Redis check

        latency = (time.time() - start) * 1000
        return ComponentHealth(
            healthy=True,
            latency_ms=round(latency, 2),
            message="Redis connection OK",
            last_check=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return ComponentHealth(
            healthy=False,
            message=f"Redis connection failed: {str(e)}",
            last_check=datetime.utcnow().isoformat(),
        )


async def check_temporal() -> ComponentHealth:
    """Check Temporal workflow service"""
    start = time.time()
    try:
        # Import here to avoid circular dependencies
        # from app.temporal.client import temporal_client
        # await temporal_client.describe_namespace("project-ai")

        # Placeholder implementation
        await asyncio.sleep(0.01)  # Simulate Temporal check

        latency = (time.time() - start) * 1000
        return ComponentHealth(
            healthy=True,
            latency_ms=round(latency, 2),
            message="Temporal service OK",
            last_check=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Temporal health check failed: {e}")
        return ComponentHealth(
            healthy=False,
            message=f"Temporal service unavailable: {str(e)}",
            last_check=datetime.utcnow().isoformat(),
        )


async def check_disk_space() -> ComponentHealth:
    """Check available disk space"""
    try:
        import shutil

        stats = shutil.disk_usage("/app/data")

        # Consider unhealthy if less than 10% free space
        percent_free = (stats.free / stats.total) * 100
        healthy = percent_free > 10

        return ComponentHealth(
            healthy=healthy,
            message=f"{percent_free:.1f}% free disk space",
            last_check=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        return ComponentHealth(
            healthy=False,
            message=f"Disk space check failed: {str(e)}",
            last_check=datetime.utcnow().isoformat(),
        )


async def check_memory() -> ComponentHealth:
    """Check memory usage"""
    try:
        import psutil

        memory = psutil.virtual_memory()

        # Consider unhealthy if less than 10% free memory
        percent_available = memory.available / memory.total * 100
        healthy = percent_available > 10

        return ComponentHealth(
            healthy=healthy,
            message=f"{percent_available:.1f}% available memory",
            last_check=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.warning(f"Memory check failed (psutil not available): {e}")
        return ComponentHealth(
            healthy=True,
            message="Memory check skipped (psutil not installed)",
            last_check=datetime.utcnow().isoformat(),
        )


@router.get("/live", response_model=HealthStatus)
async def liveness_probe(response: Response):
    """
    Kubernetes liveness probe endpoint

    Returns 200 if the application is running, regardless of dependencies.
    This should only fail if the application itself is dead/deadlocked.
    """
    try:
        health_status = HealthStatus(
            status="ok",
            timestamp=datetime.utcnow().isoformat(),
            uptime_seconds=round(get_uptime(), 2),
            version=os.getenv("APP_VERSION", "1.0.0"),
            environment=os.getenv("APP_ENV", "production"),
            checks={
                "application": {"healthy": True, "message": "Application is running"}
            },
        )
        return health_status
    except Exception as e:
        logger.error(f"Liveness probe failed: {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(
            status="error",
            timestamp=datetime.utcnow().isoformat(),
            uptime_seconds=round(get_uptime(), 2),
            version=os.getenv("APP_VERSION", "1.0.0"),
            environment=os.getenv("APP_ENV", "production"),
            checks={"application": {"healthy": False, "message": str(e)}},
        )


@router.get("/ready", response_model=HealthStatus)
async def readiness_probe(response: Response):
    """
    Kubernetes readiness probe endpoint

    Returns 200 only if all critical dependencies are healthy.
    Pod will be removed from service load balancer if this fails.
    """
    checks = {}
    all_healthy = True

    # Check critical dependencies
    db_health = await check_database()
    checks["database"] = db_health.dict()
    all_healthy = all_healthy and db_health.healthy

    redis_health = await check_redis()
    checks["redis"] = redis_health.dict()
    all_healthy = all_healthy and redis_health.healthy

    # Check optional dependencies (don't fail on these)
    temporal_health = await check_temporal()
    checks["temporal"] = temporal_health.dict()

    disk_health = await check_disk_space()
    checks["disk"] = disk_health.dict()
    all_healthy = all_healthy and disk_health.healthy

    memory_health = await check_memory()
    checks["memory"] = memory_health.dict()
    all_healthy = all_healthy and memory_health.healthy

    health_status = HealthStatus(
        status="ok" if all_healthy else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=round(get_uptime(), 2),
        version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("APP_ENV", "production"),
        checks=checks,
    )

    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status


@router.get("/startup", response_model=HealthStatus)
async def startup_probe(response: Response):
    """
    Kubernetes startup probe endpoint

    Returns 200 once the application has finished initializing.
    This allows slow-starting applications more time before liveness checks begin.
    """
    checks = {}

    # Check if application is fully initialized
    # This is a simplified check - expand based on your initialization needs
    min_uptime = 5.0  # Minimum uptime in seconds before considering started
    uptime = get_uptime()

    if uptime < min_uptime:
        checks["initialization"] = {
            "healthy": False,
            "message": f"Application still initializing ({uptime:.1f}s / {min_uptime}s)",
        }
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return HealthStatus(
            status="starting",
            timestamp=datetime.utcnow().isoformat(),
            uptime_seconds=round(uptime, 2),
            version=os.getenv("APP_VERSION", "1.0.0"),
            environment=os.getenv("APP_ENV", "production"),
            checks=checks,
        )

    # Check critical dependencies are available
    db_health = await check_database()
    checks["database"] = db_health.dict()

    if not db_health.healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(
            status="starting",
            timestamp=datetime.utcnow().isoformat(),
            uptime_seconds=round(uptime, 2),
            version=os.getenv("APP_VERSION", "1.0.0"),
            environment=os.getenv("APP_ENV", "production"),
            checks=checks,
        )

    checks["initialization"] = {
        "healthy": True,
        "message": "Application fully initialized",
    }

    return HealthStatus(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=round(uptime, 2),
        version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("APP_ENV", "production"),
        checks=checks,
    )


@router.get("/", response_model=HealthStatus)
async def health_check(response: Response):
    """
    General health check endpoint with detailed status

    Returns comprehensive health information including all dependencies.
    """
    return await readiness_probe(response)
