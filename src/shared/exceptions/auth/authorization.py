"""
Authorization exceptions for the Todo API.

This module contains exceptions related to user authorization,
permissions, access control, and resource access.
"""

from typing import Optional, Dict, Any, Union, List
from ..base import TodoAPIException


class AuthorizationError(TodoAPIException):
    """Base class for authorization-related errors."""

    def __init__(
        self,
        detail: str = "Access denied",
        error_code: str = "ACCESS_DENIED",
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=403, detail=detail, error_code=error_code, extra_data=extra_data
        )


# Advanced authorization exceptions removed - this app uses simple scopes and TodoAccessDeniedError
