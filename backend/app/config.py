"""
Application Configuration
Loads settings from environment variables with sensible defaults
"""

from typing import Any, List

from pydantic_settings import BaseSettings

_DEFAULT_SECRET_KEY = "your-super-secret-key-change-in-production"


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
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URL: str = "http://localhost:3000/auth/callback/google"

    # CORS / trusted hosts — comma-separated so they are easy to set in a
    # hosting dashboard, e.g. CORS_ORIGINS="https://app.example.com,https://example.com"
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173"
    )
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,*.onrender.com,*.ascendtalent.com"

    # Email / SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@ascendtalent.com"

    # Frontend origin used to build links in emails (password reset, verify email)
    APP_BASE_URL: str = "http://localhost:5173"
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFY_EXPIRE_HOURS: int = 24

    # Rate limiting on /auth/* — disable only for tests (see .env.example)
    RATE_LIMIT_ENABLED: bool = True

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

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_hosts_list(self) -> List[str]:
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",") if h.strip()]

    @property
    def database_url(self) -> str:
        """DATABASE_URL with the legacy `postgres://` scheme normalized.

        Some hosts still hand out `postgres://…`, which SQLAlchemy 2 rejects.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return "postgresql://" + url[len("postgres://") :]
        return url

    def model_post_init(self, __context: Any) -> None:
        """Refuse to start in production with an unsafe SECRET_KEY."""
        if self.ENVIRONMENT == "production" and (
            self.SECRET_KEY == _DEFAULT_SECRET_KEY or len(self.SECRET_KEY) < 32
        ):
            raise RuntimeError(
                "SECRET_KEY must be set to a random value of at least 32 characters "
                'in production (e.g. python -c "import secrets; print(secrets.token_hex(32))")'
            )

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
