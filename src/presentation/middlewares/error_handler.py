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
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            # Process the request
            response = await call_next(request)
            return response

        except TodoAPIException as api_error:
            # Handle known API exceptions
            return await self._handle_api_exception(
                request, api_error, start_time, request_id
            )

        except Exception as error:
            # Handle unexpected exceptions
            return await self._handle_unexpected_exception(
                request, error, start_time, request_id
            )

    async def _handle_api_exception(
        self,
        request: Request,
        error: TodoAPIException,
        start_time: float,
        request_id: str,
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
                exc_info=True if self.debug else False,
            )
        elif error.status_code >= 400:
            self.logger.warning(f"Client error: {error.detail}", extra=error_context)
        else:
            self.logger.info(f"API response: {error.detail}", extra=error_context)

        # Log security events for authentication/authorization errors
        if error.status_code in [401, 403]:
            log_security_event(
                event_type=(
                    "authentication_error"
                    if error.status_code == 401
                    else "authorization_error"
                ),
                ip_address=self._get_client_ip(request),
                details=f"{error.error_code}: {error.detail}",
            )

        # Create error response with consistent structure
        error_response = {
            "error_code": error.error_code,
            "message": error.detail,
            "status_code": error.status_code,
            "timestamp": int(time.time()),
            "request_id": request_id,
        }

        # Include extra data for client errors (4xx) or in debug mode
        if error.extra_data and (error.status_code < 500 or self.debug):
            # Flatten extra_data to top level for better readability
            if isinstance(error.extra_data, dict):
                error_response["extra_data"] = error.extra_data
            else:
                error_response["extra_data"] = {"details": error.extra_data}

        # Include debug information in development
        if self.debug:
            error_response["debug"] = {
                "exception_type": type(error).__name__,
                "traceback": traceback.format_exc(),
                "request_info": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "duration": f"{duration:.3f}s",
                },
            }

        # Add specific formatting for certain error types
        if hasattr(error, "error_code"):
            error_response = self._enhance_error_response(error_response, error)

        return JSONResponse(
            status_code=error.status_code,
            content=error_response,
            headers=getattr(error, "headers", None),
        )

    async def _handle_unexpected_exception(
        self, request: Request, error: Exception, start_time: float, request_id: str
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
            **error_context,
        )

        # Log as security event if suspicious
        if self._is_suspicious_error(error, request):
            log_security_event(
                event_type="suspicious_error",
                ip_address=self._get_client_ip(request),
                details=f"Unhandled {type(error).__name__}: {str(error)}",
            )

        # Create internal server error
        internal_error = InternalServerError(
            detail="An internal server error occurred",
            original_error=error if self.debug else None,
        )

        # Create error response with consistent structure (hide details in production)
        error_response = {
            "error_code": internal_error.error_code,
            "message": (
                internal_error.detail
                if self.debug
                else "An internal server error occurred. Please try again later."
            ),
            "status_code": 500,
            "timestamp": int(time.time()),
            "request_id": request_id,
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
                    "duration": f"{duration:.3f}s",
                },
            }

        return JSONResponse(status_code=500, content=error_response)

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
            "sql" in str(error).lower()
            and any(
                keyword in str(error).lower()
                for keyword in ["select", "union", "drop", "insert"]
            ),
            # Path traversal attempts
            ".." in str(request.url) or "%" in str(request.url),
            # Script injection attempts
            any(
                keyword in str(request.url).lower()
                for keyword in ["<script", "javascript:", "data:"]
            ),
            # Unusual exception types that might indicate attacks
            isinstance(error, (PermissionError, FileNotFoundError))
            and "etc" in str(error),
            # Large request bodies (potential DoS)
            request.headers.get("content-length")
            and int(request.headers.get("content-length", 0)) > 10_000_000,  # 10MB
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
                if key.lower() in [
                    "password",
                    "token",
                    "secret",
                    "key",
                    "authorization",
                ]:
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_for_logging(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item) for item in data]
        else:
            return data

    def _enhance_error_response(
        self, error_response: Dict[str, Any], error: TodoAPIException
    ) -> Dict[str, Any]:
        """
        Enhance error response with specific formatting for certain error types.

        Args:
            error_response (Dict[str, Any]): Base error response
            error (TodoAPIException): Exception that occurred

        Returns:
            Dict[str, Any]: Enhanced error response
        """
        # Special formatting for authentication errors
        if error.error_code in ["USER_NOT_FOUND", "INVALID_PASSWORD", "USER_INACTIVE"]:
            # Add user-friendly hints for authentication errors
            if "extra_data" in error_response:
                extra_data = error_response["extra_data"]

                # Add helpful context for different auth errors
                if error.error_code == "USER_NOT_FOUND":
                    extra_data["hint"] = (
                        "You can login with either your username or email address"
                    )
                    extra_data["suggestion"] = (
                        "Double-check the spelling of your username/email"
                    )

                elif error.error_code == "INVALID_PASSWORD":
                    extra_data["hint"] = "Password is case-sensitive"
                    extra_data["suggestion"] = (
                        "Check if Caps Lock is enabled or try retyping your password"
                    )

                elif error.error_code == "USER_INACTIVE":
                    extra_data["hint"] = "Your account has been deactivated"
                    extra_data["contact_support"] = True

        # Format validation errors more clearly
        elif error.error_code.startswith("VALIDATION_"):
            if "extra_data" in error_response:
                error_response["type"] = "validation_error"

        # Format authorization errors
        elif error.error_code.startswith("AUTHORIZATION_"):
            if "extra_data" in error_response:
                error_response["type"] = "authorization_error"

        return error_response
