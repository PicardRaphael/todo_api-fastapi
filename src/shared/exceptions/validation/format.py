"""
Format validation exceptions for the Todo API.

This module contains exceptions related to format validation
for email addresses, dates, usernames, and other formatted data.
"""

from .base import ValidationError


class InvalidEmailError(ValidationError):
    """Exception raised when email format is invalid."""

    def __init__(self, email: str):
        """
        Initialize invalid email error.

        Args:
            email (str): Invalid email address
        """
        super().__init__(
            field="email",
            value=email,
            reason="Invalid email format",
            valid_format="user@example.com",
        )
        self.error_code = "INVALID_EMAIL"


class InvalidUsernameError(ValidationError):
    """Exception raised when username format is invalid."""

    def __init__(self, username: str, reason: str = "Invalid username format"):
        """
        Initialize invalid username error.

        Args:
            username (str): Invalid username
            reason (str): Specific reason why username is invalid
        """
        super().__init__(
            field="username",
            value=username,
            reason=reason,
            valid_format="3-20 characters, letters, numbers and underscores only",
        )
        self.error_code = "INVALID_USERNAME"


class InvalidDateFormatError(ValidationError):
    """Exception raised when date format is invalid."""

    def __init__(self, date_value: str, field_name: str = "date"):
        """
        Initialize invalid date format error.

        Args:
            date_value (str): Invalid date value
            field_name (str): Name of the date field
        """
        super().__init__(
            field=field_name,
            value=date_value,
            reason="Invalid date format",
            valid_format="YYYY-MM-DD or ISO 8601 format",
        )
        self.error_code = "INVALID_DATE_FORMAT"
