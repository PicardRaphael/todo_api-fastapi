"""
Domain-specific exceptions.

This module contains all exceptions related to:
- Todo operations and business rules
- User domain logic and constraints
"""

# Import base domain exception from user.py since it's defined there
from .user import DomainException

# Todo exceptions
from .todo import (
    TodoNotFoundError,
    TodoAccessDeniedError,
    InvalidPriorityError,
    TodoTitleTooLongError,
    TodoAlreadyCompletedError,
    EmptyTodoListError,
)

# User exceptions
from .user import (
    UserNotFoundError,
    DuplicateUserError,
    UserInactiveError,
)

__all__ = [
    # Base
    "DomainException",
    # Todo
    "TodoNotFoundError",
    "TodoAccessDeniedError",
    "InvalidPriorityError",
    "TodoTitleTooLongError",
    "TodoAlreadyCompletedError",
    "EmptyTodoListError",
    # User
    "UserNotFoundError",
    "DuplicateUserError",
    "UserInactiveError",
]
