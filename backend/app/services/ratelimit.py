"""Rate limiting for /auth/* endpoints (slowapi)."""

from fastapi import Request
from slowapi import Limiter

from app.config import get_settings


def client_ip(request: Request) -> str:
    """Resolve the real client IP behind Render's reverse proxy.

    Render terminates TLS and proxies every request, so `request.client.host`
    is the proxy's own address, not the caller's — without this, every user
    would share a single rate-limit bucket. Use the first (original client)
    entry of X-Forwarded-For when present.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=client_ip, enabled=get_settings().RATE_LIMIT_ENABLED)
