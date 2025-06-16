"""
Exception system for the Todo API.

This module provides a hierarchical exception system with proper HTTP status codes
and contextual error information.
"""

from .base import TodoAPIException, InternalServerError, BadRequestError, NotFoundError
from .domain import (
    DomainException,
    TodoNotFoundError,
    InvalidPriorityError,
    TodoAccessDeniedError,
)
from .auth import (
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
    InvalidTokenError,
)
from .validation import (
    ValidationError,
    InvalidEmailError,
    WeakPasswordError,
)

__all__ = [
    # Base
    "TodoAPIException",
    "InternalServerError",
    "BadRequestError",
    "NotFoundError",
    # Domain
    "DomainException",
    "TodoNotFoundError",
    "InvalidPriorityError",
    "TodoAccessDeniedError",
    # Auth
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitExceededError",
    "InvalidTokenError",
    # Validation
    "ValidationError",
    "InvalidEmailError",
    "WeakPasswordError",
]
