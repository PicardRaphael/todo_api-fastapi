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


class InsufficientPermissionsError(AuthorizationError):
    """Exception raised when user lacks required permissions."""

    def __init__(
        self,
        required_scopes: Union[str, List[str]],
        user_scopes: Optional[List[str]] = None,
        resource: Optional[str] = None,
    ):
        """
        Initialize insufficient permissions error.

        Args:
            required_scopes (str|List[str]): Scopes required for the operation
            user_scopes (List[str], optional): Scopes the user actually has
            resource (str, optional): Resource being accessed
        """
        if isinstance(required_scopes, str):
            required_scopes = [required_scopes]

        detail = (
            f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}"
        )
        if resource:
            detail += f" for resource: {resource}"

        extra_data: Dict[str, Any] = {
            "required_scopes": required_scopes,
            "user_scopes": user_scopes or [],
        }
        if resource:
            extra_data["resource"] = resource

        super().__init__(
            detail=detail, error_code="INSUFFICIENT_PERMISSIONS", extra_data=extra_data
        )


class ResourceAccessDeniedError(AuthorizationError):
    """Exception raised when user cannot access a specific resource."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Union[str, int],
        user_id: Union[str, int],
        reason: str = "You don't have permission to access this resource",
    ):
        """
        Initialize resource access denied error.

        Args:
            resource_type (str): Type of resource (todo, user, etc.)
            resource_id (str|int): ID of the resource
            user_id (str|int): ID of the user trying to access
            reason (str): Specific reason for denial
        """
        super().__init__(
            detail=f"Access denied to {resource_type} '{resource_id}'. {reason}",
            error_code="RESOURCE_ACCESS_DENIED",
            extra_data={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "reason": reason,
            },
        )
