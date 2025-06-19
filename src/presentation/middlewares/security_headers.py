"""
Security headers middleware for the Todo API.

This middleware adds essential security headers to all responses to protect
against common web vulnerabilities and attacks.
"""

from typing import Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.logging import get_logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to HTTP responses.

    This middleware automatically adds security headers to protect against:
    - Cross-Site Scripting (XSS)
    - Content Type sniffing
    - Clickjacking
    - HTTPS downgrade attacks
    - Content Security Policy violations
    - Cross-Origin attacks

    Features:
    - Configurable security headers
    - Environment-specific settings
    - CORS support
    - Content Security Policy management
    """

    def __init__(
        self,
        app,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        enable_csp: bool = True,
        csp_policy: Optional[str] = None,
        allowed_origins: Optional[list] = None,
        debug: bool = False,
    ):
        """
        Initialize security headers middleware.

        Args:
            app: FastAPI application instance
            enable_hsts (bool): Enable HTTP Strict Transport Security
            hsts_max_age (int): HSTS max age in seconds
            enable_csp (bool): Enable Content Security Policy
            csp_policy (str, optional): Custom CSP policy
            allowed_origins (list, optional): Allowed CORS origins
            debug (bool): Enable debug mode (relaxes some security headers)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.enable_csp = enable_csp
        self.csp_policy = csp_policy or self._get_default_csp_policy(debug)
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]
        self.debug = debug
        self.logger = get_logger("middleware.security_headers")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request (Request): HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response: HTTP response with security headers
        """
        # Process the request
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(request, response)

        return response

    def _add_security_headers(self, request: Request, response: Response) -> None:
        """
        Add security headers to the response.

        Args:
            request (Request): HTTP request
            response (Response): HTTP response to modify
        """
        headers = self._get_security_headers(request)

        for header_name, header_value in headers.items():
            if header_value:  # Only add non-empty headers
                response.headers[header_name] = header_value

        # Log security headers application in debug mode
        if self.debug:
            self.logger.debug(
                f"Applied security headers to {request.method} {request.url.path}",
                extra={"headers_added": list(headers.keys()), "path": request.url.path},
            )

    def _get_security_headers(self, request: Request) -> Dict[str, str]:
        """
        Get security headers for the response.

        Args:
            request (Request): HTTP request

        Returns:
            Dict[str, str]: Security headers to add
        """
        headers = {}

        # X-Content-Type-Options: Prevent MIME type sniffing
        headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable XSS filtering
        headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # X-Permitted-Cross-Domain-Policies: Restrict cross-domain policies
        headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Feature-Policy: Control browser features
        headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "magnetometer=(), gyroscope=(), speaker=(), "
            "vibrate=(), fullscreen=(self), payment=()"
        )

        # HTTP Strict Transport Security (HSTS)
        if self.enable_hsts and self._is_https_request(request):
            headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )

        # Content Security Policy (CSP) - Skip for documentation endpoints
        if self.enable_csp and not self._is_docs_endpoint(request):
            headers["Content-Security-Policy"] = self.csp_policy

        # CORS headers for API endpoints
        if self._is_api_request(request):
            headers.update(self._get_cors_headers(request))

        # Cache control for sensitive endpoints
        if self._is_sensitive_endpoint(request):
            headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"

        return headers

    def _get_cors_headers(self, request: Request) -> Dict[str, str]:
        """
        Get CORS headers for API requests.

        Args:
            request (Request): HTTP request

        Returns:
            Dict[str, str]: CORS headers
        """
        cors_headers = {}

        # Get origin from request
        origin = request.headers.get("origin")

        # Check if origin is allowed
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            cors_headers["Access-Control-Allow-Origin"] = origin
        elif not origin:
            # For same-origin requests, allow
            cors_headers["Access-Control-Allow-Origin"] = "*"

        # Allow credentials for authenticated requests
        cors_headers["Access-Control-Allow-Credentials"] = "true"

        # Allowed methods
        cors_headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        )

        # Allowed headers
        cors_headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, Accept, "
            "X-API-Key, X-Request-ID"
        )

        # Exposed headers
        cors_headers["Access-Control-Expose-Headers"] = (
            "X-Request-ID, X-RateLimit-Remaining, X-RateLimit-Reset"
        )

        # Preflight cache time
        cors_headers["Access-Control-Max-Age"] = "86400"  # 24 hours

        return cors_headers

    def _get_default_csp_policy(self, debug: bool = False) -> str:
        """
        Get default Content Security Policy.

        Args:
            debug (bool): Whether to use debug-friendly policy

        Returns:
            str: CSP policy string
        """
        if debug:
            # Relaxed policy for development with Swagger UI support
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdn.jsdelivr.net https://unpkg.com https://cdn.redoc.ly "
                "http://localhost:* ws://localhost:*; "
                "style-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com "
                "http://localhost:*; "
                "img-src 'self' data: blob: "
                "https://cdn.jsdelivr.net https://unpkg.com "
                "http://localhost:*; "
                "connect-src 'self' http://localhost:* ws://localhost:*; "
                "font-src 'self' data: "
                "https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none';"
            )
        else:
            # Strict policy for production
            return (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self' data:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'; "
                "form-action 'self'; "
                "upgrade-insecure-requests;"
            )

    def _is_https_request(self, request: Request) -> bool:
        """
        Check if request is using HTTPS.

        Args:
            request (Request): HTTP request

        Returns:
            bool: True if HTTPS request
        """
        # Check scheme
        if request.url.scheme == "https":
            return True

        # Check forwarded protocol headers (behind proxy/load balancer)
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto == "https":
            return True

        forwarded_ssl = request.headers.get("x-forwarded-ssl")
        if forwarded_ssl == "on":
            return True

        return False

    def _is_api_request(self, request: Request) -> bool:
        """
        Check if request is an API request.

        Args:
            request (Request): HTTP request

        Returns:
            bool: True if API request
        """
        path = request.url.path
        return (
            path.startswith("/api/")
            or path.startswith("/todos")
            or path.startswith("/auth")
            or "application/json" in request.headers.get("accept", "")
        )

    def _is_sensitive_endpoint(self, request: Request) -> bool:
        """
        Check if endpoint contains sensitive data.

        Args:
            request (Request): HTTP request

        Returns:
            bool: True if sensitive endpoint
        """
        path = request.url.path.lower()
        sensitive_patterns = [
            "/auth/",
            "/login",
            "/register",
            "/password",
            "/token",
            "/refresh",
            "/admin",
            "/user",
        ]

        return any(pattern in path for pattern in sensitive_patterns)

    def _is_docs_endpoint(self, request: Request) -> bool:
        """
        Check if endpoint is a documentation endpoint (Swagger/ReDoc).

        Args:
            request (Request): HTTP request

        Returns:
            bool: True if documentation endpoint
        """
        path = request.url.path.lower()
        docs_patterns = ["/docs", "/redoc", "/openapi.json"]

        return any(pattern in path for pattern in docs_patterns)
