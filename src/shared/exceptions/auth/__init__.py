"""
Authentication and authorization exceptions.

This module contains all exceptions related to:
- User authentication (login, tokens, credentials)
- User authorization (permissions, access control)
- Rate limiting and IP blocking
"""

# Authentication exceptions
from .authentication import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    ExpiredTokenError,
    MissingTokenError,
    # Session exceptions removed - JWT-based auth
    # New specific exceptions
    UserNotFoundError,
    InvalidPasswordError,
    InactiveUserError,
)

# Authorization exceptions
from .authorization import (
    AuthorizationError,
    # Advanced authorization exceptions removed
)

# Rate limiting exceptions
from .rate_limiting import (
    RateLimitExceededError,
    # IPBlockedError removed - no IP blocking in this app
)

__all__ = [
    # Authentication
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "MissingTokenError",
    # Session exceptions removed
    # New specific authentication exceptions
    "UserNotFoundError",
    "InvalidPasswordError",
    "InactiveUserError",
    # Authorization
    "AuthorizationError",
    # Advanced authorization removed
    # Rate limiting
    "RateLimitExceededError",
    # IPBlockedError removed
]
