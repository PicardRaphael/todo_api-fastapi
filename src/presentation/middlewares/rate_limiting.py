"""
Rate limiting middleware for the Todo API.

This middleware implements intelligent rate limiting based on IP addresses,
user IDs, and endpoint-specific limits to prevent abuse and ensure fair usage.
"""

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.exceptions.auth import RateLimitExceededError
from src.shared.logging import get_logger, log_security_event


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API rate limiting.

    This middleware implements multiple rate limiting strategies:
    - Global rate limits by IP address
    - Per-user rate limits for authenticated requests
    - Endpoint-specific rate limits
    - Adaptive rate limiting based on response patterns

    Features:
    - Sliding window rate limiting
    - Different limits for different endpoints
    - Bypass for whitelisted IPs
    - Security event logging for violations
    - Configurable burst allowances
    """

    def __init__(
        self,
        app,
        default_requests_per_minute: int = 60,
        default_burst_size: int = 10,
        endpoint_limits: Optional[Dict[str, Tuple[int, int]]] = None,
        whitelist_ips: Optional[list] = None,
        enable_adaptive_limiting: bool = True,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application instance
            default_requests_per_minute (int): Default requests per minute limit
            default_burst_size (int): Default burst size
            endpoint_limits (dict, optional): Endpoint-specific limits {pattern: (rpm, burst)}
            whitelist_ips (list, optional): IPs to exclude from rate limiting
            enable_adaptive_limiting (bool): Enable adaptive rate limiting
        """
        super().__init__(app)
        self.default_rpm = default_requests_per_minute
        self.default_burst = default_burst_size
        self.endpoint_limits = endpoint_limits or self._get_default_endpoint_limits()
        self.whitelist_ips = set(whitelist_ips or ["127.0.0.1", "::1"])
        self.enable_adaptive = enable_adaptive_limiting

        # Rate limiting storage (in production, use Redis)
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.burst_counts: Dict[str, int] = defaultdict(int)
        self.last_reset: Dict[str, float] = defaultdict(float)

        # Adaptive limiting data
        self.error_counts: Dict[str, deque] = defaultdict(deque)
        self.response_times: Dict[str, deque] = defaultdict(deque)

        self.logger = get_logger("middleware.rate_limiting")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with rate limiting.

        Args:
            request (Request): HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response: HTTP response or rate limit error
        """
        client_ip = self._get_client_ip(request)

        # Skip rate limiting for whitelisted IPs
        if client_ip in self.whitelist_ips:
            return await call_next(request)

        # Get rate limit key and limits
        rate_key = self._get_rate_key(request)
        rpm_limit, burst_limit = self._get_limits_for_request(request)

        # Apply adaptive adjustments if enabled
        if self.enable_adaptive:
            rpm_limit, burst_limit = self._apply_adaptive_adjustments(
                rate_key, rpm_limit, burst_limit
            )

        # Check rate limits
        is_allowed, retry_after = self._check_rate_limits(
            rate_key, rpm_limit, burst_limit
        )

        if not is_allowed:
            # Determine limit type based on retry_after duration
            limit_type = "burst" if retry_after <= 10 else "minute"
            limit_description = (
                f"{burst_limit}/10s" if limit_type == "burst" else f"{rpm_limit}/minute"
            )

            # Log security event with more details
            log_security_event(
                event_type="rate_limit_exceeded",
                ip_address=client_ip,
                details=f"Rate limit exceeded ({limit_type}) for {request.method} {request.url.path} - {limit_description}",
            )

            # Return enhanced rate limit error
            error = RateLimitExceededError(
                limit=limit_description,
                retry_after=retry_after,
                endpoint=request.url.path,
                user_identifier=rate_key,  # Use rate_key instead of just IP
                limit_type=limit_type,
            )

            return JSONResponse(
                status_code=error.status_code,
                content=error.to_dict(),
                headers=error.headers,
            )

        # Record request
        current_time = time.time()
        self._record_request(rate_key, current_time)

        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)

            # Record response metrics for adaptive limiting
            if self.enable_adaptive:
                duration = time.time() - start_time
                self._record_response_metrics(rate_key, response.status_code, duration)

            # Add rate limit headers to successful responses
            rate_limit_headers = self.get_rate_limit_headers(
                rate_key, rpm_limit, burst_limit
            )
            for header_name, header_value in rate_limit_headers.items():
                response.headers[header_name] = header_value

            return response

        except Exception as error:
            # Record error for adaptive limiting
            if self.enable_adaptive:
                self._record_error(rate_key, current_time)
            raise

    def _get_rate_key(self, request: Request) -> str:
        """
        Generate rate limiting key for the request.

        Args:
            request (Request): HTTP request

        Returns:
            str: Rate limiting key
        """
        client_ip = self._get_client_ip(request)

        # Use user ID if authenticated, otherwise fall back to IP
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", None)
            if user_id:
                return f"user:{user_id}"

        return f"ip:{client_ip}"

    def _get_limits_for_request(self, request: Request) -> Tuple[int, int]:
        """
        Get rate limits for the specific request.

        Args:
            request (Request): HTTP request

        Returns:
            Tuple[int, int]: (requests_per_minute, burst_size)
        """
        path = request.url.path
        method = request.method

        # Check endpoint-specific limits
        for pattern, (rpm, burst) in self.endpoint_limits.items():
            if pattern in path or (method + ":" + pattern) in (method + ":" + path):
                return rpm, burst

        # Return default limits
        return self.default_rpm, self.default_burst

    def _check_rate_limits(
        self, rate_key: str, rpm_limit: int, burst_limit: int
    ) -> Tuple[bool, int]:
        """
        Check if request is within rate limits.

        Args:
            rate_key (str): Rate limiting key
            rpm_limit (int): Requests per minute limit
            burst_limit (int): Burst limit

        Returns:
            Tuple[bool, int]: (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        window_start = current_time - 60  # 60 seconds window

        # Clean old requests from sliding window
        request_times = self.request_counts[rate_key]
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        # Check minute-based limit
        if len(request_times) >= rpm_limit:
            # Calculate retry after based on oldest request
            oldest_request = request_times[0] if request_times else current_time
            retry_after = int(60 - (current_time - oldest_request)) + 1
            return False, retry_after

        # Check burst limit
        burst_window_start = current_time - 10  # 10 seconds burst window
        recent_requests = sum(1 for t in request_times if t >= burst_window_start)

        if recent_requests >= burst_limit:
            return False, 10  # Wait 10 seconds for burst recovery

        return True, 0

    def _record_request(self, rate_key: str, timestamp: float) -> None:
        """
        Record a request in the rate limiting storage.

        Args:
            rate_key (str): Rate limiting key
            timestamp (float): Request timestamp
        """
        self.request_counts[rate_key].append(timestamp)

        # Limit memory usage by keeping only recent data
        if len(self.request_counts[rate_key]) > 1000:
            # Remove oldest half
            for _ in range(500):
                if self.request_counts[rate_key]:
                    self.request_counts[rate_key].popleft()

    def _apply_adaptive_adjustments(
        self, rate_key: str, base_rpm: int, base_burst: int
    ) -> Tuple[int, int]:
        """
        Apply adaptive rate limiting adjustments based on behavior patterns.

        Args:
            rate_key (str): Rate limiting key
            base_rpm (int): Base requests per minute limit
            base_burst (int): Base burst limit

        Returns:
            Tuple[int, int]: Adjusted (rpm, burst) limits
        """
        current_time = time.time()

        # Check error rate in the last 5 minutes
        error_window = current_time - 300
        error_times = self.error_counts[rate_key]
        recent_errors = sum(1 for t in error_times if t >= error_window)

        # Check average response time
        response_times = self.response_times[rate_key]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        else:
            avg_response_time = 0

        # Apply penalties for high error rates
        if recent_errors > 10:  # More than 10 errors in 5 minutes
            rpm_multiplier = 0.5  # Reduce to 50%
            burst_multiplier = 0.3  # Reduce to 30%
            self.logger.warning(
                f"Adaptive rate limiting: High error rate detected for {rate_key}",
                extra={
                    "rate_key": rate_key,
                    "recent_errors": recent_errors,
                    "rpm_reduction": "50%",
                    "burst_reduction": "70%",
                },
            )
        elif avg_response_time > 2.0:  # Slow responses (>2 seconds)
            rpm_multiplier = 0.7  # Reduce to 70%
            burst_multiplier = 0.5  # Reduce to 50%
            self.logger.info(
                f"Adaptive rate limiting: Slow responses detected for {rate_key}",
                extra={
                    "rate_key": rate_key,
                    "avg_response_time": f"{avg_response_time:.2f}s",
                    "rpm_reduction": "30%",
                    "burst_reduction": "50%",
                },
            )
        else:
            # No penalties
            rpm_multiplier = 1.0
            burst_multiplier = 1.0

        adjusted_rpm = max(1, int(base_rpm * rpm_multiplier))
        adjusted_burst = max(1, int(base_burst * burst_multiplier))

        return adjusted_rpm, adjusted_burst

    def _record_response_metrics(
        self, rate_key: str, status_code: int, duration: float
    ) -> None:
        """
        Record response metrics for adaptive limiting.

        Args:
            rate_key (str): Rate limiting key
            status_code (int): HTTP status code
            duration (float): Response duration in seconds
        """
        current_time = time.time()

        # Record response time
        response_times = self.response_times[rate_key]
        response_times.append(duration)

        # Keep only recent response times (last 100)
        if len(response_times) > 100:
            response_times.popleft()

        # Record errors
        if status_code >= 400:
            self._record_error(rate_key, current_time)

    def _record_error(self, rate_key: str, timestamp: float) -> None:
        """
        Record an error for adaptive limiting.

        Args:
            rate_key (str): Rate limiting key
            timestamp (float): Error timestamp
        """
        error_times = self.error_counts[rate_key]
        error_times.append(timestamp)

        # Clean old errors (keep last 5 minutes)
        window_start = timestamp - 300
        while error_times and error_times[0] < window_start:
            error_times.popleft()

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Args:
            request (Request): HTTP request

        Returns:
            str: Client IP address
        """
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _get_default_endpoint_limits(self) -> Dict[str, Tuple[int, int]]:
        """
        Get default endpoint-specific rate limits.

        Returns:
            Dict[str, Tuple[int, int]]: Endpoint patterns and their limits
        """
        return {
            # Authentication endpoints - stricter limits
            "/auth/login": (10, 3),  # 10/min, burst 3
            "/auth/register": (5, 2),  # 5/min, burst 2
            "/auth/refresh": (20, 5),  # 20/min, burst 5
            # Todo CRUD - moderate limits
            "POST:/todos": (30, 10),  # 30/min, burst 10
            "PUT:/todos": (20, 8),  # 20/min, burst 8
            "DELETE:/todos": (15, 5),  # 15/min, burst 5
            # Read operations - higher limits
            "GET:/todos": (120, 30),  # 120/min, burst 30
            # Health checks - very high limits
            "/health": (1000, 100),  # 1000/min, burst 100
        }

    def get_rate_limit_headers(
        self, rate_key: str, rpm_limit: int, burst_limit: int
    ) -> Dict[str, str]:
        """
        Get current rate limit headers for successful responses.

        Args:
            rate_key (str): Rate limiting key
            rpm_limit (int): Requests per minute limit
            burst_limit (int): Burst limit

        Returns:
            Dict[str, str]: Headers to add to response
        """
        current_time = time.time()
        window_start = current_time - 60

        # Calculate remaining requests
        request_times = self.request_counts[rate_key]
        recent_requests = sum(1 for t in request_times if t >= window_start)
        remaining = max(0, rpm_limit - recent_requests)

        # Calculate reset time (next minute boundary)
        reset_time = int(current_time + (60 - (current_time % 60)))

        return {
            "X-RateLimit-Limit": str(rpm_limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Burst": str(burst_limit),
        }
