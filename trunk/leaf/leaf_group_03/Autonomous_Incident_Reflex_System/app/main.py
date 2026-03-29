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
AUTONOMOUS INCIDENT REFLEX SYSTEM Microservice
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
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from .errors import setup_exception_handlers
from .health import health_router
from .logging_config import logger, setup_logging
from .middleware import (

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

    AuthenticationMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
)
from .repository import database
from .routes import router

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
    logger.info("Starting Autonomous Incident Reflex System service v1.0.0")

    # Thirsty-Lang Integration (Floor 1)
    import os

    thirsty_bootstrap = os.path.join(os.path.dirname(__file__), "bootstrap.thirsty")
    if os.path.exists(thirsty_bootstrap):
        logger.info(f"Sovereign Floor 1 Bootstrap found: {thirsty_bootstrap}")
        logger.info("Floor 1 Sovereignty Acknowledged")

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
    logger.info("Shutting down Autonomous Incident Reflex System service")

    # Close database connections
    await database.disconnect()
    logger.info("Database connections closed")

    logger.info("Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Autonomous Incident Reflex System",
    description="""Build:
Threat detection microservice
Policy evaluation gate
Reflexive action executor
Evidence preservation pipeline
Cryptographic chain-of-custody service
Think: CrowdStrike + immutable evidence + deterministic replay.
Defense sector eats this up.""",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "service": "Autonomous Incident Reflex System",
        "version": "1.0.0",
        "status": "operational",
    }


if __name__ == "__main__":
    __sovereign_execute__(globals(), "INIT_PROTOCOL")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,  # Use our custom logging
    )
