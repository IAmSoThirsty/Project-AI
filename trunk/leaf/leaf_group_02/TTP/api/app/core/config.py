# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / config.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / config.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables with validation.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "TTP API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENABLE_DOCS: bool = Field(default=True, description="Enable API documentation")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://ttp.example.com"],
        description="Allowed CORS origins"
    )

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://ttp:CHANGEME_PASSWORD@localhost:5432/ttp",
        description="PostgreSQL connection string - MUST be set via environment variable"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_MAX_CONNECTIONS: int = 50

    # Authentication
    SECRET_KEY: str = Field(
        default="INSECURE_DEFAULT_CHANGE_ME_IN_PRODUCTION",
        description="Secret key for JWT signing - Generate with: openssl rand -hex 32"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # OAuth2 (optional, for production)
    OAUTH2_ENABLED: bool = False
    OAUTH2_ISSUER: Optional[str] = None
    OAUTH2_AUDIENCE: Optional[str] = None

    # S3 Storage
    S3_BUCKET: str = Field(default="ttp-texture-assets", description="S3 bucket name")
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT: Optional[str] = None  # For MinIO or other S3-compatible storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # CDN
    CDN_BASE_URL: Optional[str] = Field(
        default=None,
        description="CloudFront or CDN base URL for serving assets"
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or console

    # Observability
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True

    # Feature Flags
    ENABLE_ASSET_UPLOAD: bool = True
    ENABLE_PACK_CREATION: bool = True
    ENABLE_SEARCH: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
