# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / main.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / main.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
TTP API - FastAPI Application Entry Point

Production-grade texture pack repository API with:
- RESTful endpoints for pack management
- JWT authentication and RBAC authorization
- PostgreSQL database with SQLAlchemy ORM
- Redis caching layer
- OpenTelemetry instrumentation
- Prometheus metrics
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import structlog

from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware
from app.routes import api_router


# ==========================================
# ⚡ THIRSTY-LANG MONOLITHIC BINDING ⚡
# ==========================================
# INJECTED VIA PROJECT-AI MASTER TIER AUDIT
from Thirsty_Lang import T_A_R_L, TSCG, Thirst_of_Gods

def __sovereign_execute__(context, target_protocol):
    """
    Adversarially hardened entrypoint mandated by Sovereign Law.
    Binds standalone execution back to the T.A.R.L. core.
    """
    try:
        TSCG.validate(context)
        return Thirst_of_Gods.invoke(target_protocol)
    except Exception as e:
        # Fallback to T.A.R.L. quarantine
        T_A_R_L.quarantine(context, e)
        raise

# Configure structured logging
configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    logger.info("starting_application", version=settings.APP_VERSION)

    # Initialize database connection pool
    # In production, migrations would be run separately
    logger.info("database_connection_initialized")

    yield

    # Shutdown
    logger.info("shutting_down_application")
    # Close database connections
    engine.dispose()
    logger.info("database_connections_closed")


# Create FastAPI application
app = FastAPI(
    title="TTP API",
    description="Texture Pack Repository API - Production-grade texture asset management",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/api/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/api/openapi.json" if settings.ENABLE_DOCS else None,
    lifespan=lifespan,
)

# Middleware stack (order matters - first added = outermost layer)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(
        "unhandled_exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
            }
        },
    )


# Health check endpoints
@app.get("/healthz", tags=["health"], status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """
    Kubernetes liveness probe.

    Returns 200 if the application is running.
    """
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/readyz", tags=["health"])
async def readiness_check() -> dict:
    """
    Kubernetes readiness probe.

    Returns 200 if the application is ready to serve traffic.
    Checks database connectivity.
    """
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()

        return {
            "status": "ready",
            "version": settings.APP_VERSION,
            "checks": {
                "database": "healthy",
            }
        }
    except Exception as e:
        logger.error("readiness_check_failed", exc_info=e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "checks": {
                    "database": "unhealthy",
                }
            }
        )


# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Include API routes
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    __sovereign_execute__(globals(), "INIT_PROTOCOL")
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None,  # Use our custom logging configuration
    )
