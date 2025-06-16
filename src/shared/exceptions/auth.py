"""
Authentication and authorization exceptions for the Todo API.

This module contains exceptions related to user authentication, authorization,
rate limiting, and token management.
"""

from typing import Optional, Dict, Any, Union
from .base import TodoAPIException


class AuthenticationError(TodoAPIException):
    """Base class for authentication-related errors."""

    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_FAILED",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code=error_code,
            extra_data=extra_data,
            headers={"WWW-Authenticate": "Bearer"}
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
            extra_data=extra_data
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
            extra_data={"reason": reason}
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
            extra_data=extra_data
        )


class MissingTokenError(AuthenticationError):
    """Exception raised when required token is missing."""

    def __init__(self):
        super().__init__(
            detail="Authentication token is required",
            error_code="MISSING_TOKEN"
        )


# ===== AUTHORIZATION EXCEPTIONS =====

class AuthorizationError(TodoAPIException):
    """Base class for authorization-related errors."""

    def __init__(
        self,
        detail: str = "Access denied",
        error_code: str = "ACCESS_DENIED",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code=error_code,
            extra_data=extra_data
        )


class InsufficientPermissionsError(AuthorizationError):
    """Exception raised when user lacks required permissions."""

    def __init__(
        self,
        required_scopes: Union[str, list],
        user_scopes: Optional[list] = None,
        resource: Optional[str] = None
    ):
        """
        Initialize insufficient permissions error.

        Args:
            required_scopes (str|list): Scopes required for the operation
            user_scopes (list, optional): Scopes the user actually has
            resource (str, optional): Resource being accessed
        """
        if isinstance(required_scopes, str):
            required_scopes = [required_scopes]

        detail = f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}"
        if resource:
            detail += f" for resource: {resource}"

        extra_data = {
            "required_scopes": required_scopes,
            "user_scopes": user_scopes or []
        }
        if resource:
            extra_data["resource"] = resource

        super().__init__(
            detail=detail,
            error_code="INSUFFICIENT_PERMISSIONS",
            extra_data=extra_data
        )


class ResourceAccessDeniedError(AuthorizationError):
    """Exception raised when user cannot access a specific resource."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Union[str, int],
        user_id: Union[str, int],
        reason: str = "You don't have permission to access this resource"
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
                "reason": reason
            }
        )


# ===== RATE LIMITING EXCEPTIONS =====

class RateLimitExceededError(TodoAPIException):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        limit: str,
        retry_after: int,
        endpoint: Optional[str] = None,
        user_identifier: Optional[str] = None
    ):
        """
        Initialize rate limit exceeded error.

        Args:
            limit (str): Description of the rate limit (e.g., "5/minute")
            retry_after (int): Seconds to wait before retrying
            endpoint (str, optional): Endpoint that was rate limited
            user_identifier (str, optional): User or IP that hit the limit
        """
        detail = f"Rate limit exceeded: {limit}. Try again in {retry_after} seconds."
        if endpoint:
            detail += f" Endpoint: {endpoint}"

        extra_data = {
            "limit": limit,
            "retry_after": retry_after
        }
        if endpoint:
            extra_data["endpoint"] = endpoint
        if user_identifier:
            extra_data["user_identifier"] = user_identifier

        headers = {"Retry-After": str(retry_after)}

        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            extra_data=extra_data,
            headers=headers
        )


class IPBlockedError(TodoAPIException):
    """Exception raised when an IP address is blocked."""

    def __init__(self, ip_address: str, reason: str = "Suspicious activity detected"):
        """
        Initialize IP blocked error.

        Args:
            ip_address (str): The blocked IP address
            reason (str): Reason for blocking
        """
        super().__init__(
            status_code=403,
            detail=f"IP address {ip_address} is blocked. Reason: {reason}",
            error_code="IP_BLOCKED",
            extra_data={
                "ip_address": ip_address,
                "reason": reason
            }
        )


# ===== SESSION EXCEPTIONS =====

class SessionExpiredError(AuthenticationError):
    """Exception raised when user session has expired."""

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize session expired error.

        Args:
            session_id (str, optional): ID of the expired session
        """
        extra_data = {}
        if session_id:
            extra_data["session_id"] = session_id

        super().__init__(
            detail="Session has expired. Please login again.",
            error_code="SESSION_EXPIRED",
            extra_data=extra_data
        )


class ConcurrentSessionError(AuthenticationError):
    """Exception raised when too many concurrent sessions are detected."""

    def __init__(self, user_id: Union[str, int], max_sessions: int):
        """
        Initialize concurrent session error.

        Args:
            user_id (str|int): ID of the user
            max_sessions (int): Maximum allowed concurrent sessions
        """
        super().__init__(
            detail=f"Too many concurrent sessions. Maximum {max_sessions} sessions allowed.",
            error_code="CONCURRENT_SESSION_LIMIT",
            extra_data={
                "user_id": user_id,
                "max_sessions": max_sessions
            }
        )