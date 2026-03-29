import logging
logger = logging.getLogger(__name__)
# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: the-logic--perception-layer / main.py
# ============================================================================ #
"""
THE LOGIC & PERCEPTION LAYER Microservice
Version: 1.0.0
Author: Jeremy Karrick / IAmSoThirsty 

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
    logger.info("Starting The Logic & Perception Layer service v1.0.0")
    
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
    logger.info("Shutting down The Logic & Perception Layer service")
    
    # Close database connections
    await database.disconnect()
    logger.info("Database connections closed")
    
    logger.info("Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="The Logic & Perception Layer",
    description="Heuristic Drift Inhibitor: Works with your Semantic Drift Monitor. It doesn't just watch the drift; it actively forces the AI weights or logic gates back to a "Golden Baseline" if the system starts hallucinating or diverging from its original purpose.
Consensus Hallucination Filter: In a multi-cloud setup, this service compares outputs from the same request across different regions. If they differ, it flags a "Reality Fracture" and forces a re-compute.
Contextual Amnesia Service: A "Right to be Forgotten" engine. It ensures that when data is marked for Knowledge Decay, every trace, log, and cached fragment across the entire stack is purged simultaneously.",
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
    requests_per_minute=100,
    burst=200,
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
        "service": "The Logic & Perception Layer",
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
