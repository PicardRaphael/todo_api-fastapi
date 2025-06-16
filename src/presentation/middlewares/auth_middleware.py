"""
Authentication middleware for the Todo API.

This middleware handles JWT token validation and user context injection.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.logging import get_logger


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication and user context."""

    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("middleware.auth")

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication."""
        # TODO: Implement JWT token validation
        # This would validate tokens and set request.state.user
        return await call_next(request)
