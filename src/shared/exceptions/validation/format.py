"""
Format validation exceptions for the Todo API.

This module contains exceptions related to format validation
for email addresses, dates, usernames, and other formatted data.
"""

import re
from .base import ValidationError


class InvalidEmailError(ValidationError):
    """Exception raised when email format is invalid."""

    def __init__(self, email: str, reason: str = "Invalid email format"):
        """
        Initialize invalid email error.

        Args:
            email (str): Invalid email address
            reason (str): Specific reason why email is invalid
        """
        super().__init__(
            field="email",
            value=email,
            reason=reason,
            valid_format="user@example.com",
        )
        self.error_code = "INVALID_EMAIL"

    @staticmethod
    def validate_email(email: str) -> None:
        """
        Validate email format and raise InvalidEmailError if invalid.

        Args:
            email (str): Email to validate

        Raises:
            InvalidEmailError: If email format is invalid
        """
        if not email or not isinstance(email, str):
            raise InvalidEmailError(email, "Email is required and must be a string")

        email = email.strip()
        if not email:
            raise InvalidEmailError(email, "Email cannot be empty")

        # RFC 5322 compliant regex pattern (simplified but robust)
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            raise InvalidEmailError(
                email, "Email must be in valid format (user@domain.com)"
            )

        # Length validation
        if len(email) > 254:  # RFC 5321 limit
            raise InvalidEmailError(
                email,
                f"Email is too long ({len(email)} characters). Maximum allowed is 254 characters",
            )


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

    @staticmethod
    def validate_username(username: str) -> None:
        """
        Validate username format and raise InvalidUsernameError if invalid.

        Args:
            username (str): Username to validate

        Raises:
            InvalidUsernameError: If username format is invalid
        """
        if not username or not isinstance(username, str):
            raise InvalidUsernameError(
                username, "Username is required and must be a string"
            )

        username = username.strip()
        if not username:
            raise InvalidUsernameError(username, "Username cannot be empty")

        # Length validation
        if len(username) < 3:
            raise InvalidUsernameError(
                username,
                f"Username is too short ({len(username)} characters). Minimum is 3 characters",
            )

        if len(username) > 20:
            raise InvalidUsernameError(
                username,
                f"Username is too long ({len(username)} characters). Maximum is 20 characters",
            )

        # Format validation: only letters, numbers, and underscores
        username_pattern = r"^[a-zA-Z0-9_]+$"
        if not re.match(username_pattern, username):
            raise InvalidUsernameError(
                username, "Username can only contain letters, numbers, and underscores"
            )

        # Cannot start or end with underscore
        if username.startswith("_") or username.endswith("_"):
            raise InvalidUsernameError(
                username, "Username cannot start or end with an underscore"
            )

        # Cannot have consecutive underscores
        if "__" in username:
            raise InvalidUsernameError(
                username, "Username cannot contain consecutive underscores"
            )


# InvalidDateFormatError removed - no date fields in this application
