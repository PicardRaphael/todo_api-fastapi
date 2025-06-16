"""
Domain-specific exceptions for the Todo API.

This module contains exceptions related to business logic and domain rules
for todos, users, and other business entities.
"""

from typing import Optional, Dict, Any, Union
from .base import TodoAPIException, NotFoundError


class DomainException(TodoAPIException):
    """Base class for all domain-related exceptions."""
    pass


# ===== TODO DOMAIN EXCEPTIONS =====

class TodoNotFoundError(NotFoundError):
    """Exception raised when a todo is not found."""

    def __init__(self, todo_id: Union[int, str], owner_id: Optional[int] = None):
        """
        Initialize todo not found error.

        Args:
            todo_id (int|str): ID of the todo that was not found
            owner_id (int, optional): ID of the user who tried to access the todo
        """
        extra_data = {"todo_id": todo_id}
        if owner_id is not None:
            extra_data["owner_id"] = owner_id

        super().__init__(
            resource="Todo",
            resource_id=todo_id,
            extra_data=extra_data
        )
        self.error_code = "TODO_NOT_FOUND"


class TodoAccessDeniedError(DomainException):
    """Exception raised when a user tries to access a todo they don't own."""

    def __init__(self, todo_id: Union[int, str], user_id: int, actual_owner_id: Optional[int] = None):
        """
        Initialize todo access denied error.

        Args:
            todo_id (int|str): ID of the todo
            user_id (int): ID of the user trying to access
            actual_owner_id (int, optional): ID of the actual owner
        """
        extra_data = {
            "todo_id": todo_id,
            "requesting_user_id": user_id
        }
        if actual_owner_id is not None:
            extra_data["actual_owner_id"] = actual_owner_id

        super().__init__(
            status_code=403,
            detail=f"Access denied to todo {todo_id}. You can only access your own todos.",
            error_code="TODO_ACCESS_DENIED",
            extra_data=extra_data
        )


class InvalidPriorityError(DomainException):
    """Exception raised when an invalid priority value is provided."""

    def __init__(self, priority: Union[int, str], valid_range: str = "1-5"):
        """
        Initialize invalid priority error.

        Args:
            priority (int|str): The invalid priority value provided
            valid_range (str): Description of valid priority range
        """
        super().__init__(
            status_code=400,
            detail=f"Invalid priority '{priority}'. Priority must be between {valid_range}.",
            error_code="INVALID_PRIORITY",
            extra_data={
                "provided_priority": priority,
                "valid_range": valid_range,
                "valid_values": [1, 2, 3, 4, 5]
            }
        )


class TodoTitleTooLongError(DomainException):
    """Exception raised when todo title exceeds maximum length."""

    def __init__(self, title: str, max_length: int = 100):
        """
        Initialize title too long error.

        Args:
            title (str): The title that is too long
            max_length (int): Maximum allowed length
        """
        super().__init__(
            status_code=400,
            detail=f"Todo title is too long. Maximum {max_length} characters allowed.",
            error_code="TODO_TITLE_TOO_LONG",
            extra_data={
                "provided_length": len(title),
                "max_length": max_length,
                "title_preview": title[:50] + "..." if len(title) > 50 else title
            }
        )


class TodoAlreadyCompletedError(DomainException):
    """Exception raised when trying to complete an already completed todo."""

    def __init__(self, todo_id: Union[int, str]):
        """
        Initialize already completed error.

        Args:
            todo_id (int|str): ID of the todo that is already completed
        """
        super().__init__(
            status_code=400,
            detail=f"Todo {todo_id} is already completed",
            error_code="TODO_ALREADY_COMPLETED",
            extra_data={"todo_id": todo_id}
        )


class EmptyTodoListError(DomainException):
    """Exception raised when trying to perform operations on empty todo list."""

    def __init__(self, user_id: int, operation: str = "operation"):
        """
        Initialize empty todo list error.

        Args:
            user_id (int): ID of the user
            operation (str): Operation that was attempted
        """
        super().__init__(
            status_code=404,
            detail=f"No todos found for user. Cannot perform {operation}.",
            error_code="EMPTY_TODO_LIST",
            extra_data={
                "user_id": user_id,
                "attempted_operation": operation
            }
        )


# ===== USER DOMAIN EXCEPTIONS =====

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
                "identifier_value": user_identifier
            }
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
            extra_data={
                "duplicate_field": field,
                "duplicate_value": value
            }
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
            extra_data={"user_id": user_id}
        )