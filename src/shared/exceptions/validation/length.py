"""
Length validation exceptions for the Todo API.

This module contains exceptions related to string length validation
(too long, too short, etc.).
"""

from typing import Optional
from .base import ValidationError


class ValueTooLongError(ValidationError):
    """Exception raised when a string value exceeds maximum length."""

    def __init__(
        self,
        field: str,
        value: str,
        max_length: int,
        actual_length: Optional[int] = None,
    ):
        """
        Initialize value too long error.

        Args:
            field (str): Field name
            value (str): Value that is too long
            max_length (int): Maximum allowed length
            actual_length (int, optional): Actual length of the value
        """
        actual_length = actual_length or len(value)

        super().__init__(
            field=field,
            value=value[:50] + "..." if len(value) > 50 else value,
            reason=f"Value too long. Maximum {max_length} characters allowed, got {actual_length}",
            valid_format=f"Maximum {max_length} characters",
        )

        self.extra_data.update(
            {"max_length": max_length, "actual_length": actual_length}
        )
        self.error_code = "VALUE_TOO_LONG"


class ValueTooShortError(ValidationError):
    """Exception raised when a string value is below minimum length."""

    def __init__(
        self,
        field: str,
        value: str,
        min_length: int,
        actual_length: Optional[int] = None,
    ):
        """
        Initialize value too short error.

        Args:
            field (str): Field name
            value (str): Value that is too short
            min_length (int): Minimum required length
            actual_length (int, optional): Actual length of the value
        """
        actual_length = actual_length or len(value)

        super().__init__(
            field=field,
            value=value,
            reason=f"Value too short. Minimum {min_length} characters required, got {actual_length}",
            valid_format=f"Minimum {min_length} characters",
        )

        self.extra_data.update(
            {"min_length": min_length, "actual_length": actual_length}
        )
        self.error_code = "VALUE_TOO_SHORT"
