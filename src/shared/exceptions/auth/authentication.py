"""
Authentication exceptions for the Todo API.

This module contains exceptions related to user authentication,
login credentials, tokens, and session management.
"""

from typing import Optional, Dict, Any, Union
from ..base import TodoAPIException


class AuthenticationError(TodoAPIException):
    """Base class for authentication-related errors."""

    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_FAILED",
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code=error_code,
            extra_data=extra_data,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when login credentials are invalid."""

    def __init__(self, username: Optional[str] = None):
        """
        Initialize invalid credentials error.

        Args:
            username (str, optional): Username that failed authentication
        """
        extra_data = {}
        if username:
            extra_data["attempted_username"] = username

        super().__init__(
            detail="Invalid username or password",
            error_code="INVALID_CREDENTIALS",
            extra_data=extra_data,
        )


class InvalidTokenError(AuthenticationError):
    """Exception raised when JWT token is invalid or malformed."""

    def __init__(self, reason: str = "Invalid token"):
        """
        Initialize invalid token error.

        Args:
            reason (str): Specific reason why token is invalid
        """
        super().__init__(
            detail=f"Invalid token: {reason}",
            error_code="INVALID_TOKEN",
            extra_data={"reason": reason},
        )


class ExpiredTokenError(AuthenticationError):
    """Exception raised when JWT token has expired."""

    def __init__(self, expired_at: Optional[str] = None):
        """
        Initialize expired token error.

        Args:
            expired_at (str, optional): When the token expired
        """
        extra_data = {}
        if expired_at:
            extra_data["expired_at"] = expired_at

        super().__init__(
            detail="Token has expired. Please login again.",
            error_code="EXPIRED_TOKEN",
            extra_data=extra_data,
        )


class MissingTokenError(AuthenticationError):
    """Exception raised when required token is missing."""

    def __init__(self):
        super().__init__(
            detail="Authentication token is required", error_code="MISSING_TOKEN"
        )


# Sessions-related exceptions removed - this app uses JWT tokens, not sessions


# ===== NEW SPECIFIC AUTHENTICATION EXCEPTIONS =====


class UserNotFoundError(AuthenticationError):
    """Exception raised when a user is not found during authentication."""

    def __init__(self, identifier: str, identifier_type: str = "username"):
        """
        Initialize user not found error.

        Args:
            identifier (str): Username or email that was not found
            identifier_type (str): Type of identifier ("username", "email", "username/email")
        """
        if identifier_type == "username/email":
            detail = f"No user found with username or email '{identifier}'. You can login with either your username or email address."
        else:
            detail = f"No user found with {identifier_type} '{identifier}'"

        super().__init__(
            detail=detail,
            error_code="USER_NOT_FOUND",
            extra_data={
                "identifier": identifier,
                "identifier_type": identifier_type,
                "hint": "You can use either username or email to login",
            },
        )


class InvalidPasswordError(AuthenticationError):
    """Exception raised when the password is incorrect."""

    def __init__(self, identifier: str):
        """
        Initialize invalid password error.

        Args:
            identifier (str): Username or email for which password was incorrect
        """
        super().__init__(
            detail="Incorrect password. Please check your password and try again.",
            error_code="INVALID_PASSWORD",
            extra_data={
                "identifier": identifier,
                "hint": "Make sure Caps Lock is off and check for typos",
            },
        )


class InactiveUserError(AuthenticationError):
    """Exception raised when trying to authenticate an inactive user."""

    def __init__(
        self, user_id: Union[str, int], reason: str = "Account is deactivated"
    ):
        """
        Initialize inactive user error.

        Args:
            user_id (str|int): ID of the inactive user
            reason (str): Reason why the account is inactive
        """
        super().__init__(
            detail=f"Account is inactive: {reason}. Please contact support to reactivate your account.",
            error_code="USER_INACTIVE",
            extra_data={"user_id": user_id, "reason": reason, "contact_support": True},
        )
