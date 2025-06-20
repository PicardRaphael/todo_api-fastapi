"""
Rate limiting and IP blocking exceptions for the Todo API.

This module contains exceptions related to rate limiting,
IP blocking, and abuse prevention.
"""

import time
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
        limit_type: Optional[str] = None,
    ):
        """
        Initialize rate limit exceeded error.

        Args:
            limit (str): Description of the rate limit (e.g., "5/minute")
            retry_after (int): Seconds to wait before retrying
            endpoint (str, optional): Endpoint that was rate limited
            user_identifier (str, optional): User or IP that hit the limit
            limit_type (str, optional): Type of limit exceeded ('minute' or 'burst')
        """
        # Enhanced message with more helpful information
        if limit_type == "burst":
            detail = f"Burst rate limit exceeded: {limit}. Please slow down and try again in {retry_after} seconds."
        else:
            detail = f"Rate limit exceeded: {limit}. Please try again in {retry_after} seconds."

        if endpoint:
            detail += f" (Endpoint: {endpoint})"

        # Add helpful tip for users
        if retry_after > 60:
            minutes = retry_after // 60
            seconds = retry_after % 60
            time_str = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
            detail += f" ({time_str})"

        extra_data: Dict[str, Any] = {
            "limit": limit,
            "retry_after": retry_after,
            "limit_type": limit_type or "minute",
            "recommended_action": "Please reduce request frequency to stay within limits",
        }

        if endpoint:
            extra_data["endpoint"] = endpoint
        if user_identifier:
            extra_data["user_identifier"] = user_identifier

        # Enhanced headers for better client handling
        headers = {
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": limit,
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + retry_after),
        }

        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            extra_data=extra_data,
            headers=headers,
        )


# IP blocking functionality removed - not implemented in this app
