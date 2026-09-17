"""
FastAPI Application Entry Point
Ascend - Tech Talent Marketplace
"""

import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.routes import (
    applications,
    auth,
    contracts,
    jobs,
    mentorships,
    messages,
    payments,
    profile,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("🚀 Ascend API starting up...")
    yield
    logger.info("🛑 Ascend API shutting down...")


def create_app(settings: Settings = None) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        settings: Application settings (uses environment if None)

    Returns:
        Configured FastAPI app
    """
    if settings is None:
        settings = get_settings()

    # Error tracking is a no-op until a DSN is configured.
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=0.0,
        )

    app = FastAPI(
        title="Ascend API",
        description="Tech talent marketplace connecting Korean-Canadian professionals with global talent",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    )

    # Middleware: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware: Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts_list,
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Check API health status."""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "0.1.0",
        }

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint - API information."""
        return {
            "name": "Ascend API",
            "version": "0.1.0",
            "description": "Tech talent marketplace connecting Korean-Canadian professionals with global talent",
            "docs": "/docs",
            "api_prefix": "/api",
        }

    # 500 Handler
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Register route modules
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(profile.router, prefix="/api/profile", tags=["Profiles"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
    app.include_router(
        applications.router, prefix="/api/applications", tags=["Applications"]
    )
    app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
    app.include_router(
        mentorships.router, prefix="/api/mentorships", tags=["Mentorships"]
    )
    app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
    app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])

    logger.info(f"✅ FastAPI app configured for {settings.ENVIRONMENT} environment")
    return app


# Create app instance
settings = get_settings()
app = create_app(settings)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
