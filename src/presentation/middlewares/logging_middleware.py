"""
Logging middleware for the Todo API.

This middleware logs all HTTP requests and responses with structured data,
providing comprehensive audit trails and performance monitoring.
"""

import time
import uuid
from typing import Any, Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from src.shared.logging import get_logger, log_request


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    This middleware provides comprehensive request/response logging with
    structured data including timing, user context, and performance metrics.

    Features:
    - Logs all HTTP requests and responses
    - Adds unique request IDs for correlation
    - Measures request duration and performance
    - Captures user context when available
    - Sanitizes sensitive data in logs
    - Provides structured data for analysis
    """

    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_size: int = 1024,
        exclude_paths: Optional[list] = None
    ):
        """
        Initialize logging middleware.

        Args:
            app: FastAPI application instance
            log_request_body (bool): Whether to log request bodies
            log_response_body (bool): Whether to log response bodies
            max_body_size (int): Maximum body size to log (in bytes)
            exclude_paths (list, optional): Paths to exclude from logging
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.logger = get_logger("middleware.logging")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with comprehensive logging.

        Args:
            request (Request): HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response: HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Check if path should be excluded from logging
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Log request
        await self._log_request(request, request_id, start_time)

        # Process request and capture response
        try:
            response = await call_next(request)

            # Log response
            await self._log_response(request, response, request_id, start_time)

            return response

        except Exception as error:
            # Log error (handled by error middleware, but capture timing here)
            duration = time.time() - start_time
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "duration": f"{duration:.3f}s",
                    "error": str(error),
                    "client_ip": self._get_client_ip(request),
                }
            )
            raise

    async def _log_request(self, request: Request, request_id: str, start_time: float) -> None:
        """
        Log incoming HTTP request.

        Args:
            request (Request): HTTP request
            request_id (str): Unique request identifier
            start_time (float): Request start timestamp
        """
        # Gather request information
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "referer": request.headers.get("referer"),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length"),
            "timestamp": start_time,
        }

        # Add authentication context if available
        if hasattr(request.state, 'user'):
            request_data["user_id"] = getattr(request.state.user, 'id', None)
            request_data["username"] = getattr(request.state.user, 'username', None)

        # Add request body if enabled and appropriate
        if self.log_request_body and self._should_log_body(request):
            try:
                request_data["body"] = await self._get_request_body(request)
            except Exception as e:
                request_data["body_error"] = f"Failed to read body: {str(e)}"

        # Add custom headers (filtered)
        request_data["headers"] = self._get_filtered_headers(request.headers)

        # Log the request
        self.logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra=request_data
        )

    async def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        start_time: float
    ) -> None:
        """
        Log outgoing HTTP response.

        Args:
            request (Request): HTTP request
            response (Response): HTTP response
            request_id (str): Unique request identifier
            start_time (float): Request start timestamp
        """
        duration = time.time() - start_time

        # Gather response information
        response_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": f"{duration:.3f}s",
            "response_size": response.headers.get("content-length"),
            "content_type": response.headers.get("content-type"),
            "client_ip": self._get_client_ip(request),
        }

        # Add user context if available
        if hasattr(request.state, 'user'):
            response_data["user_id"] = getattr(request.state.user, 'id', None)

        # Add response body if enabled and appropriate
        if self.log_response_body and self._should_log_response_body(response):
            try:
                response_data["body"] = await self._get_response_body(response)
            except Exception as e:
                response_data["body_error"] = f"Failed to read response body: {str(e)}"

        # Add response headers (filtered)
        response_data["headers"] = self._get_filtered_headers(response.headers)

        # Use the centralized request logging function
        log_request(
            method=request.method,
            url=request.url.path,
            status_code=response.status_code,
            duration=duration,
            user_id=response_data.get("user_id"),
            request_id=request_id,
            **{k: v for k, v in response_data.items()
               if k not in ["method", "url", "status_code", "duration", "user_id", "request_id"]}
        )

    def _should_exclude_path(self, path: str) -> bool:
        """
        Check if a path should be excluded from logging.

        Args:
            path (str): Request path

        Returns:
            bool: True if path should be excluded
        """
        return any(excluded in path for excluded in self.exclude_paths)

    def _should_log_body(self, request: Request) -> bool:
        """
        Determine if request body should be logged.

        Args:
            request (Request): HTTP request

        Returns:
            bool: True if body should be logged
        """
        # Don't log bodies for certain content types
        content_type = request.headers.get("content-type", "").lower()
        excluded_types = [
            "multipart/form-data",
            "application/octet-stream",
            "image/",
            "video/",
            "audio/"
        ]

        if any(excluded_type in content_type for excluded_type in excluded_types):
            return False

        # Don't log large bodies
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return False

        return True

    def _should_log_response_body(self, response: Response) -> bool:
        """
        Determine if response body should be logged.

        Args:
            response (Response): HTTP response

        Returns:
            bool: True if body should be logged
        """
        # Don't log streaming responses
        if isinstance(response, StreamingResponse):
            return False

        # Don't log large responses
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return False

        # Don't log binary content
        content_type = response.headers.get("content-type", "").lower()
        if not content_type.startswith(("application/json", "text/", "application/xml")):
            return False

        return True

    async def _get_request_body(self, request: Request) -> Any:
        """
        Safely extract request body for logging.

        Args:
            request (Request): HTTP request

        Returns:
            Any: Request body data (sanitized)
        """
        try:
            body = await request.body()
            if not body:
                return None

            # Try to parse as JSON
            content_type = request.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                import json
                body_data = json.loads(body.decode('utf-8'))
                return self._sanitize_data(body_data)
            else:
                # Return first part of body as string
                body_str = body.decode('utf-8', errors='ignore')
                if len(body_str) > self.max_body_size:
                    body_str = body_str[:self.max_body_size] + "..."
                return self._sanitize_data(body_str)

        except Exception:
            return "[Could not parse request body]"

    async def _get_response_body(self, response: Response) -> Any:
        """
        Safely extract response body for logging.

        Args:
            response (Response): HTTP response

        Returns:
            Any: Response body data (sanitized)
        """
        try:
            if hasattr(response, 'body') and response.body:
                body_str = response.body.decode('utf-8', errors='ignore')

                # Try to parse as JSON
                content_type = response.headers.get("content-type", "").lower()
                if "application/json" in content_type:
                    import json
                    try:
                        body_data = json.loads(body_str)
                        return self._sanitize_data(body_data)
                    except json.JSONDecodeError:
                        pass

                # Return as string (truncated if necessary)
                if len(body_str) > self.max_body_size:
                    body_str = body_str[:self.max_body_size] + "..."
                return body_str

        except Exception:
            return "[Could not parse response body]"

        return None

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Args:
            request (Request): HTTP request

        Returns:
            str: Client IP address
        """
        # Check for forwarded headers (behind proxy/load balancer)
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

    def _get_filtered_headers(self, headers) -> Dict[str, str]:
        """
        Get headers with sensitive information filtered out.

        Args:
            headers: HTTP headers

        Returns:
            Dict[str, str]: Filtered headers
        """
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "x-csrf-token", "x-forwarded-for", "x-real-ip"
        }

        filtered = {}
        for name, value in headers.items():
            name_lower = name.lower()
            if name_lower in sensitive_headers:
                filtered[name] = "[REDACTED]"
            elif "token" in name_lower or "key" in name_lower or "secret" in name_lower:
                filtered[name] = "[REDACTED]"
            else:
                filtered[name] = value

        return filtered

    def _sanitize_data(self, data: Any) -> Any:
        """
        Sanitize sensitive data for logging.

        Args:
            data (Any): Data to sanitize

        Returns:
            Any: Sanitized data
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = key.lower()
                if key_lower in ["password", "token", "secret", "key", "authorization"]:
                    sanitized[key] = "[REDACTED]"
                elif "password" in key_lower or "token" in key_lower or "secret" in key_lower:
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data