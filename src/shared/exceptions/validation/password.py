"""
Password validation exceptions for the Todo API.

This module contains exceptions related to password strength
and security requirements validation.
"""

from typing import List
from .base import ValidationError


class WeakPasswordError(ValidationError):
    """Exception raised when password doesn't meet security requirements."""

    def __init__(
        self,
        password_length: int,
        requirements: List[str],
        missing_requirements: List[str],
    ):
        """
        Initialize weak password error.

        Args:
            password_length (int): Length of the provided password
            requirements (List[str]): All password requirements
            missing_requirements (List[str]): Requirements that are not met
        """
        reason = f"Password doesn't meet security requirements: {', '.join(missing_requirements)}"

        super().__init__(
            field="password",
            value="[HIDDEN]",
            reason=reason,
            valid_format="At least 8 characters with uppercase, lowercase, digit and special character",
        )

        self.extra_data.update(
            {
                "password_length": password_length,
                "all_requirements": requirements,
                "missing_requirements": missing_requirements,
            }
        )
        self.error_code = "WEAK_PASSWORD"
