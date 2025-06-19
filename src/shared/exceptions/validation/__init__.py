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
    MultipleValidationErrors,
)

# Format validation
from .format import (
    InvalidEmailError,
    InvalidUsernameError,
    InvalidDateFormatError,
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
from .fields import (
    RequiredFieldMissingError,
    InvalidChoiceError,
    InvalidRangeError,
)

__all__ = [
    # Base
    "ValidationError",
    "MultipleValidationErrors",
    # Format
    "InvalidEmailError",
    "InvalidUsernameError",
    "InvalidDateFormatError",
    # Password
    "WeakPasswordError",
    # Length
    "ValueTooLongError",
    "ValueTooShortError",
    # Fields
    "RequiredFieldMissingError",
    "InvalidChoiceError",
    "InvalidRangeError",
]
