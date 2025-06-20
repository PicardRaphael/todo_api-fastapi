"""
Exception system for the Todo API.

This module provides a hierarchical exception system with proper HTTP status codes
and contextual error information.

NEW ARCHITECTURE:
- auth/: Authentication, authorization, and rate limiting exceptions
- domain/: Business logic exceptions for todos and users
- validation/: Input validation and format checking exceptions
- base.py: Core exception classes
"""

# Base exceptions (keep as is)
from .base import TodoAPIException, InternalServerError, BadRequestError, NotFoundError

# Domain exceptions (from new structure)
from .domain import (
    DomainException,
    # Todo exceptions
    TodoNotFoundError,
    InvalidPriorityError,
    TodoAccessDeniedError,
    TodoTitleTooLongError,
    TodoAlreadyCompletedError,
    EmptyTodoListError,
    # User exceptions
    UserNotFoundError,
    DuplicateUserError,
    UserInactiveError,
)

# Auth exceptions (from new structure)
from .auth import (
    # Authentication
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    ExpiredTokenError,
    MissingTokenError,
    # Session exceptions removed - JWT-based auth
    # New specific authentication exceptions
    UserNotFoundError,
    InvalidPasswordError,
    InactiveUserError,
    # Authorization
    AuthorizationError,
    # Advanced authorization exceptions removed
    # Rate limiting
    RateLimitExceededError,
    # IPBlockedError removed
)

# Validation exceptions (from new structure)
from .validation import (
    # Base validation
    ValidationError,
    # MultipleValidationErrors removed
    # Format validation
    InvalidEmailError,
    InvalidUsernameError,
    # InvalidDateFormatError removed
    # Password validation
    WeakPasswordError,
    # Length validation
    ValueTooLongError,
    ValueTooShortError,
    # Field validation exceptions removed
)

__all__ = [
    # Base exceptions
    "TodoAPIException",
    "InternalServerError",
    "BadRequestError",
    "NotFoundError",
    # Domain exceptions
    "DomainException",
    # Todo
    "TodoNotFoundError",
    "InvalidPriorityError",
    "TodoAccessDeniedError",
    "TodoTitleTooLongError",
    "TodoAlreadyCompletedError",
    "EmptyTodoListError",
    # User
    "UserNotFoundError",
    "DuplicateUserError",
    "UserInactiveError",
    # Auth exceptions
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
    # Validation exceptions
    # Base validation
    "ValidationError",
    # MultipleValidationErrors removed
    # Format validation
    "InvalidEmailError",
    "InvalidUsernameError",
    # InvalidDateFormatError removed
    # Password validation
    "WeakPasswordError",
    # Length validation
    "ValueTooLongError",
    "ValueTooShortError",
    # Field validation
    # Field validation exceptions removed
]
