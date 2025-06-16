"""
Base exception classes for the Todo API.

This module provides the foundation for the hierarchical exception system
with proper HTTP status codes, error codes, and contextual information.
"""

from fastapi import HTTPException
from typing import Optional, Dict, Any, Union
import json


class TodoAPIException(HTTPException):
    """
    Base exception for all Todo API errors.

    Extends FastAPI's HTTPException with additional features:
    - Custom error codes for API consumers
    - Extra contextual data
    - Structured error responses
    - Logging integration
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize a Todo API exception.

        Args:
            status_code (int): HTTP status code
            detail (str): Human-readable error message
            error_code (str, optional): Machine-readable error code
            extra_data (dict, optional): Additional context data
            headers (dict, optional): HTTP headers to include in response
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self._generate_error_code()
        self.extra_data = extra_data or {}

    def _generate_error_code(self) -> str:
        """Generate a default error code based on the exception class name."""
        class_name = self.__class__.__name__
        # Convert CamelCase to UPPER_SNAKE_CASE
        import re
        error_code = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).upper()
        return error_code.replace('_ERROR', '').replace('_EXCEPTION', '')

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to a structured dictionary.

        Returns:
            dict: Structured error information
        """
        return {
            "error": {
                "code": self.error_code,
                "message": self.detail,
                "status_code": self.status_code,
                "extra_data": self.extra_data
            }
        }

    def to_json(self) -> str:
        """Convert exception to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self) -> str:
        """String representation of the exception."""
        return f"[{self.error_code}] {self.detail}"

    def __repr__(self) -> str:
        """Detailed representation of the exception."""
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code}, "
            f"detail='{self.detail}', "
            f"error_code='{self.error_code}', "
            f"extra_data={self.extra_data})"
        )


class InternalServerError(TodoAPIException):
    """
    Generic internal server error.

    Used for unexpected errors that should not expose internal details
    to API consumers.
    """

    def __init__(
        self,
        detail: str = "Internal server error",
        original_error: Optional[Exception] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize internal server error.

        Args:
            detail (str): Public error message
            original_error (Exception, optional): Original exception that caused this error
            extra_data (dict, optional): Additional context
        """
        extra_data = extra_data or {}
        if original_error:
            extra_data["original_error_type"] = type(original_error).__name__
            # Only include original error message in development/debug mode
            # In production, this should be logged but not exposed to users

        super().__init__(
            status_code=500,
            detail=detail,
            error_code="INTERNAL_SERVER_ERROR",
            extra_data=extra_data
        )
        self.original_error = original_error


class BadRequestError(TodoAPIException):
    """Generic bad request error for malformed requests."""

    def __init__(
        self,
        detail: str = "Bad request",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="BAD_REQUEST",
            extra_data=extra_data
        )


class NotFoundError(TodoAPIException):
    """Generic not found error."""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Union[str, int, None] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize not found error.

        Args:
            resource (str): Type of resource not found
            resource_id (str|int, optional): ID of the resource
            extra_data (dict, optional): Additional context
        """
        if resource_id is not None:
            detail = f"{resource} with id '{resource_id}' not found"
            extra_data = extra_data or {}
            extra_data.update({"resource_type": resource, "resource_id": resource_id})
        else:
            detail = f"{resource} not found"
            extra_data = extra_data or {}
            extra_data.update({"resource_type": resource})

        super().__init__(
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND",
            extra_data=extra_data
        )