# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / database.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / database.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Database configuration and session management.

Uses SQLAlchemy 2.0+ async engine with connection pooling.
"""

from typing import Generator

from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using them
    echo=settings.DATABASE_ECHO,
    poolclass=pool.QueuePool,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to get database session.

    Usage:
        @app.get("/")
        def route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Event listeners for connection pool monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log database connections."""
    pass  # In production, increment Prometheus counter


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log database disconnections."""
    pass  # In production, decrement Prometheus counter
