"""
Configuration management with environment variable validation
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Service Metadata
    SERVICE_NAME: str = "Autonomous Negotiation Agent Infrastructure"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Security
API_KEYS: List[str] = Field(default_factory=lambda: os.getenv("API_KEYS", "changeme").split(","))
    API_KEY_HEADER: str = "X-API-Key"
JWT_SECRET: str = Field(default="changeme-secret-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
# Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 500
    RATE_LIMIT_BURST: int = 1000
    
    # CORS
    CORS_ORIGINS: List[str] = ['*']
    
    # Database
DB_POOL_SIZE: int = 20
    DB_TIMEOUT: int = 30
    
    # Observability
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = true
    ENABLE_TRACING: bool = true
    METRICS_PORT: int = 9090
    
    # Feature Flags
    ENABLE_API_DOCS: bool = true
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"


# Global settings instance
settings = Settings()

# Validate critical settings on import
if settings.is_production():
if "changeme" in settings.API_KEYS:
        raise ValueError("API_KEYS must be changed in production")
if settings.JWT_SECRET == "changeme-secret-key":
        raise ValueError("JWT_SECRET must be changed in production")
