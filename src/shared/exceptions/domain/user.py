"""
User domain exceptions for the Todo API.

This module contains exceptions related to user operations
and business rules specific to users.
"""

from typing import Union
from ..base import TodoAPIException, NotFoundError


class DomainException(TodoAPIException):
    """Base class for all domain-related exceptions."""

    pass


class UserNotFoundError(NotFoundError):
    """Exception raised when a user is not found."""

    def __init__(self, user_identifier: Union[int, str], identifier_type: str = "id"):
        """
        Initialize user not found error.

        Args:
            user_identifier (int|str): User ID, email, or username
            identifier_type (str): Type of identifier used
        """
        super().__init__(
            resource="User",
            resource_id=user_identifier,
            extra_data={
                "identifier_type": identifier_type,
                "identifier_value": user_identifier,
            },
        )
        self.error_code = "USER_NOT_FOUND"


class DuplicateUserError(DomainException):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, field: str, value: str):
        """
        Initialize duplicate user error.

        Args:
            field (str): Field that has duplicate value (email, username)
            value (str): The duplicate value
        """
        super().__init__(
            status_code=409,
            detail=f"User with {field} '{value}' already exists",
            error_code="DUPLICATE_USER",
            extra_data={"duplicate_field": field, "duplicate_value": value},
        )


class UserInactiveError(DomainException):
    """Exception raised when trying to authenticate an inactive user."""

    def __init__(self, user_id: Union[int, str]):
        """
        Initialize user inactive error.

        Args:
            user_id (int|str): ID of the inactive user
        """
        super().__init__(
            status_code=403,
            detail="User account is inactive. Please contact support.",
            error_code="USER_INACTIVE",
            extra_data={"user_id": user_id},
        )
