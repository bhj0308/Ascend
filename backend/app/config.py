"""
Application Configuration
Loads settings from environment variables with sensible defaults
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Ascend"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ascend_dev"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_EXPIRE_SECONDS: int = 3600  # 1 hour

    # JWT / Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URL: str = "http://localhost:3000/auth/callback/google"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "*.ascendtalent.com",
    ]

    # Email / SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@ascendtalent.com"

    # Wise (Cross-border payments)
    WISE_API_KEY: str = ""
    WISE_API_URL: str = "https://api.wise.com"

    # DocuSign (E-signatures)
    DOCUSIGN_CLIENT_ID: str = ""
    DOCUSIGN_CLIENT_SECRET: str = ""
    DOCUSIGN_ACCOUNT_ID: str = ""
    DOCUSIGN_API_URL: str = (
        "https://demo.docusign.net"  # Production: https://na3.docusign.net
    )

    # Sentry (Error tracking)
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"

    # Feature Flags
    ENABLE_WISE_PAYMENTS: bool = False
    ENABLE_DOCUSIGN: bool = False
    ENABLE_GOOGLE_OAUTH: bool = False

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Settings = None


def get_settings() -> Settings:
    """
    Get application settings (cached singleton).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
