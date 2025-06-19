"""
Rate limiting and IP blocking exceptions for the Todo API.

This module contains exceptions related to rate limiting,
IP blocking, and abuse prevention.
"""

from typing import Optional, Dict, Any
from ..base import TodoAPIException


class RateLimitExceededError(TodoAPIException):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        limit: str,
        retry_after: int,
        endpoint: Optional[str] = None,
        user_identifier: Optional[str] = None,
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

        extra_data: Dict[str, Any] = {"limit": limit, "retry_after": retry_after}
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
            headers=headers,
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
            extra_data={"ip_address": ip_address, "reason": reason},
        )
