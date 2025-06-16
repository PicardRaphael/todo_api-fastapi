"""
Error handling middleware for the Todo API.

This middleware provides centralized error handling for all HTTP requests,
ensuring consistent error responses and proper logging of exceptions.
"""

import time
import traceback
from typing import Any, Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.exceptions import TodoAPIException, InternalServerError
from src.shared.logging import get_logger, log_exception, log_security_event


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global error handling and response formatting.

    This middleware catches all unhandled exceptions, logs them appropriately,
    and returns consistent error responses to clients.

    Features:
    - Catches and logs all unhandled exceptions
    - Formats errors into consistent JSON responses
    - Hides internal details in production
    - Logs security events for suspicious errors
    - Includes request correlation IDs for debugging
    """

    def __init__(self, app, debug: bool = False):
        """
        Initialize error handler middleware.

        Args:
            app: FastAPI application instance
            debug (bool): Whether to include debug information in responses
        """
        super().__init__(app)
        self.debug = debug
        self.logger = get_logger("middleware.error_handler")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with error handling.

        Args:
            request (Request): HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response: HTTP response (normal or error)
        """
        start_time = time.time()
        request_id = getattr(request.state, 'request_id', 'unknown')

        try:
            # Process the request
            response = await call_next(request)
            return response

        except TodoAPIException as api_error:
            # Handle known API exceptions
            return await self._handle_api_exception(request, api_error, start_time, request_id)

        except Exception as error:
            # Handle unexpected exceptions
            return await self._handle_unexpected_exception(request, error, start_time, request_id)

    async def _handle_api_exception(
        self,
        request: Request,
        error: TodoAPIException,
        start_time: float,
        request_id: str
    ) -> JSONResponse:
        """
        Handle known API exceptions.

        Args:
            request (Request): HTTP request
            error (TodoAPIException): API exception that occurred
            start_time (float): Request start time
            request_id (str): Request correlation ID

        Returns:
            JSONResponse: Formatted error response
        """
        duration = time.time() - start_time

        # Log the error with context
        error_context = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "duration": f"{duration:.3f}s",
            "error_code": error.error_code,
            "status_code": error.status_code,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
        }

        # Log at appropriate level based on status code
        if error.status_code >= 500:
            self.logger.error(
                f"API error: {error.detail}",
                extra=error_context,
                exc_info=True if self.debug else False
            )
        elif error.status_code >= 400:
            self.logger.warning(
                f"Client error: {error.detail}",
                extra=error_context
            )
        else:
            self.logger.info(
                f"API response: {error.detail}",
                extra=error_context
            )

        # Log security events for authentication/authorization errors
        if error.status_code in [401, 403]:
            log_security_event(
                event_type="authentication_error" if error.status_code == 401 else "authorization_error",
                ip_address=self._get_client_ip(request),
                details=f"{error.error_code}: {error.detail}"
            )

        # Create error response
        error_response = {
            "error": {
                "code": error.error_code,
                "message": error.detail,
                "status_code": error.status_code,
                "request_id": request_id,
                "timestamp": time.time()
            }
        }

        # Include extra data in debug mode or for client errors
        if self.debug or error.status_code < 500:
            if error.extra_data:
                error_response["error"]["details"] = error.extra_data

        # Include debug information in development
        if self.debug:
            error_response["debug"] = {
                "exception_type": type(error).__name__,
                "traceback": traceback.format_exc(),
                "request_info": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "duration": f"{duration:.3f}s"
                }
            }

        return JSONResponse(
            status_code=error.status_code,
            content=error_response,
            headers=getattr(error, 'headers', None)
        )

    async def _handle_unexpected_exception(
        self,
        request: Request,
        error: Exception,
        start_time: float,
        request_id: str
    ) -> JSONResponse:
        """
        Handle unexpected/unhandled exceptions.

        Args:
            request (Request): HTTP request
            error (Exception): Unexpected exception
            start_time (float): Request start time
            request_id (str): Request correlation ID

        Returns:
            JSONResponse: Formatted error response
        """
        duration = time.time() - start_time

        # Log the unexpected error with full context
        error_context = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "duration": f"{duration:.3f}s",
            "exception_type": type(error).__name__,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
        }

        log_exception(
            self.logger,
            "Unhandled exception in request processing",
            error,
            **error_context
        )

        # Log as security event if suspicious
        if self._is_suspicious_error(error, request):
            log_security_event(
                event_type="suspicious_error",
                ip_address=self._get_client_ip(request),
                details=f"Unhandled {type(error).__name__}: {str(error)}"
            )

        # Create internal server error
        internal_error = InternalServerError(
            detail="An internal server error occurred",
            original_error=error if self.debug else None
        )

        # Create error response (hide details in production)
        error_response = {
            "error": {
                "code": internal_error.error_code,
                "message": internal_error.detail,
                "status_code": 500,
                "request_id": request_id,
                "timestamp": time.time()
            }
        }

        # Include debug information only in debug mode
        if self.debug:
            error_response["debug"] = {
                "exception_type": type(error).__name__,
                "exception_message": str(error),
                "traceback": traceback.format_exc(),
                "request_info": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "duration": f"{duration:.3f}s"
                }
            }
        else:
            # In production, just add a generic message
            error_response["error"]["message"] = "An internal server error occurred. Please try again later."

        return JSONResponse(
            status_code=500,
            content=error_response
        )

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
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _is_suspicious_error(self, error: Exception, request: Request) -> bool:
        """
        Determine if an error appears suspicious and should be logged as a security event.

        Args:
            error (Exception): Exception that occurred
            request (Request): HTTP request

        Returns:
            bool: True if error appears suspicious
        """
        suspicious_indicators = [
            # SQL injection attempts
            "sql" in str(error).lower() and any(keyword in str(error).lower()
                                               for keyword in ["select", "union", "drop", "insert"]),

            # Path traversal attempts
            ".." in str(request.url) or "%" in str(request.url),

            # Script injection attempts
            any(keyword in str(request.url).lower()
                for keyword in ["<script", "javascript:", "data:"]),

            # Unusual exception types that might indicate attacks
            isinstance(error, (PermissionError, FileNotFoundError)) and "etc" in str(error),

            # Large request bodies (potential DoS)
            request.headers.get("content-length") and
            int(request.headers.get("content-length", 0)) > 10_000_000,  # 10MB
        ]

        return any(suspicious_indicators)

    def _sanitize_for_logging(self, data: Any) -> Any:
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
                if key.lower() in ["password", "token", "secret", "key", "authorization"]:
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_for_logging(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item) for item in data]
        else:
            return data