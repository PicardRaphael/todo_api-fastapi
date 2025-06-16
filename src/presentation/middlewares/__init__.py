"""
Middlewares for the Todo API presentation layer.

This module contains all middleware components that handle cross-cutting concerns
such as authentication, logging, error handling, rate limiting, and CORS.

Middlewares are executed in order and provide a clean separation of concerns
for HTTP request/response processing.

Available middlewares:
- ErrorHandlerMiddleware: Global error handling and response formatting
- LoggingMiddleware: Request/response logging with structured data
- AuthenticationMiddleware: JWT token validation and user context
- RateLimitingMiddleware: API rate limiting by IP/user
- CORSMiddleware: Cross-Origin Resource Sharing configuration
- SecurityHeadersMiddleware: Security headers (HSTS, CSP, etc.)
"""

from .error_handler import ErrorHandlerMiddleware
from .logging_middleware import LoggingMiddleware
from .auth_middleware import AuthenticationMiddleware
from .rate_limiting import RateLimitingMiddleware
from .security_headers import SecurityHeadersMiddleware

__all__ = [
    "ErrorHandlerMiddleware",
    "LoggingMiddleware",
    "AuthenticationMiddleware",
    "RateLimitingMiddleware",
    "SecurityHeadersMiddleware",
]