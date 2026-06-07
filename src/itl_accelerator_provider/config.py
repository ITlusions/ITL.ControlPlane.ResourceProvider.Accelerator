"""
Configuration management for Accelerator Resource Provider
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Service
    SERVICE_NAME: str = "accelerator-provider"
    SERVICE_PORT: int = 8003
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5434/accelerator_provider"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes

    # Control Plane Integration
    CONTROL_PLANE_API_URL: str = "http://localhost:8000"
    CONTROL_PLANE_AUTH_URL: str = "https://auth.itlusions.com"
    CONTROL_PLANE_CLIENT_ID: str = "accelerator-provider"
    CONTROL_PLANE_CLIENT_SECRET: str = ""

    # DGX Platform Integration
    DGX_PLATFORM_API_URL: str = "http://localhost:9504"
    DGX_PLATFORM_API_KEY: str = ""

    # OIDC / Auth
    OIDC_REALM: str = "itlusions"
    OIDC_CLIENT_ID: str = "accelerator-provider"
    OIDC_CLIENT_SECRET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
