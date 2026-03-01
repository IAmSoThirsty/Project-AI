"""
AUTONOMOUS COMPLIANCE-AS-CODE ENGINE Microservice
Version: 1.0.0
Author: IAmSoThirsty

Production-grade microservice with:
- Full observability (metrics, logging, tracing)
- Security (both, rate limiting, RBAC)
- Health checks (liveness, readiness, startup)
- Graceful shutdown
- Database migrations
- API documentation
"""
import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import uvicorn

from .config import settings
from .logging_config import setup_logging, logger
from .routes import router
from .middleware import (
    RequestIDMiddleware,
    RateLimitMiddleware,
    AuthenticationMiddleware,
    MetricsMiddleware,
)
from .metrics import REQUEST_COUNT, REQUEST_DURATION, INFLIGHT_REQUESTS
from .health import health_router
from .errors import ServiceError, setup_exception_handlers
from .repository import database

# Setup logging
setup_logging()

# Graceful shutdown handler
shutdown_event = asyncio.Event()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Autonomous Compliance-as-Code Engine service v1.0.0")
    
    # Initialize database
    await database.connect()
    logger.info("Database connection established")
    
    # Run migrations if needed
from .repository import run_migrations
    await run_migrations()
    logger.info("Database migrations completed")
logger.info("Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Autonomous Compliance-as-Code Engine service")
    
    # Close database connections
    await database.disconnect()
    logger.info("Database connections closed")
    
    logger.info("Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Autonomous Compliance-as-Code Engine",
    description="Build a regulator-ready microservice fabric that:
Ingests policy (YAML/DSL)
Compiles invariants
Evaluates runtime actions deterministically
Produces signed audit trails
Exports SOC2 / ISO / NIST artifacts automatically
Add:
Continuous evidence generation
Machine-verifiable compliance proofs
API to expose compliance state to customers",
    version="1.0.0",
    lifespan=lifespan,
docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Custom Middleware (order matters!)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=250,
    burst=500,
)
app.add_middleware(AuthenticationMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(router, prefix="/api/v1", tags=["api"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Autonomous Compliance-as-Code Engine",
        "version": "1.0.0",
        "status": "operational",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,  # Use our custom logging
)
