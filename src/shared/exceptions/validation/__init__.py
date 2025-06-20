"""
Validation exceptions.

This module contains all exceptions related to:
- Input format validation (email, date, username)
- Password strength validation
- Field length validation
- Required fields and choice validation
"""

# Base validation classes
from .base import (
    ValidationError,
    # MultipleValidationErrors removed - Pydantic handles multiple errors
)

# Format validation
from .format import (
    InvalidEmailError,
    InvalidUsernameError,
    # InvalidDateFormatError removed - no date fields
)

# Password validation
from .password import (
    WeakPasswordError,
)

# Length validation
from .length import (
    ValueTooLongError,
    ValueTooShortError,
)

# Field validation
# Field validation exceptions removed - Pydantic handles these cases

__all__ = [
    # Base
    "ValidationError",
    # MultipleValidationErrors removed
    # Format
    "InvalidEmailError",
    "InvalidUsernameError",
    # InvalidDateFormatError removed
    # Password
    "WeakPasswordError",
    # Length
    "ValueTooLongError",
    "ValueTooShortError",
    # Fields
    # Field validation exceptions removed
]
