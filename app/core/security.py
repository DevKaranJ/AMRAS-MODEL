"""
API key authentication dependency for AMRAS.

All routers must declare `dependencies=[Depends(require_api_key)]` or
individual endpoints must add it to their signature.

The expected key is read from the environment variable AMRAS_API_KEY.
If the variable is unset, the server refuses all requests at startup to
prevent accidentally running an unprotected instance in production.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config.settings import settings
from app.core.logger import get_logger

logger = get_logger("amras.security")

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)


async def require_api_key(api_key: str = Depends(_API_KEY_HEADER)) -> str:
    """FastAPI dependency that validates the X-API-Key header."""
    expected = settings.api_key
    if expected is None:
        # Fail-safe: if the operator never set a key, deny everything.
        logger.error("amras_api_key_not_configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key not configured on this server. Set AMRAS_API_KEY.",
        )
    if api_key != expected:
        logger.warning("amras_invalid_api_key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return api_key
