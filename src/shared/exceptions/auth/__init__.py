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
    SessionExpiredError,
    ConcurrentSessionError,
    # New specific exceptions
    UserNotFoundError,
    InvalidPasswordError,
    InactiveUserError,
)

# Authorization exceptions
from .authorization import (
    AuthorizationError,
    InsufficientPermissionsError,
    ResourceAccessDeniedError,
)

# Rate limiting exceptions
from .rate_limiting import (
    RateLimitExceededError,
    IPBlockedError,
)

__all__ = [
    # Authentication
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "MissingTokenError",
    "SessionExpiredError",
    "ConcurrentSessionError",
    # New specific authentication exceptions
    "UserNotFoundError",
    "InvalidPasswordError",
    "InactiveUserError",
    # Authorization
    "AuthorizationError",
    "InsufficientPermissionsError",
    "ResourceAccessDeniedError",
    # Rate limiting
    "RateLimitExceededError",
    "IPBlockedError",
]
