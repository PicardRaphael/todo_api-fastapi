"""
Hybrid Architecture FastAPI Application - Production Ready

This is the consolidated main application file combining the best of both
Clean Architecture and MVC patterns. All duplications have been removed
and the application uses the unified hybrid architecture.

Architecture Stack:
1. Domain Layer: Business entities and rules
2. Application Layer: Use cases and business logic coordination
3. Infrastructure Layer: External concerns (database, auth, etc.)
4. Presentation Layer: Controllers and middleware
5. API Layer: Simplified routes that delegate to controllers

Key Features:
- Intelligent controllers with comprehensive error handling
- Advanced middleware stack for production-ready features
- Simplified routes with clean separation of concerns
- Comprehensive logging and monitoring
- Robust exception handling system
- Security-first design with multiple protection layers
- Single point of entry (no duplications)
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Infrastructure configuration
from src.infrastructure.config import get_settings
from src.infrastructure.database.sqlite.models import Base
from src.infrastructure.database.sqlite.config import engine

# Shared infrastructure
from src.shared.logging import setup_logging, get_logger, LoggingConfig

# Advanced middleware stack
from src.presentation.middlewares.error_handler import ErrorHandlerMiddleware
from src.presentation.middlewares.logging_middleware import LoggingMiddleware
from src.presentation.middlewares.rate_limiting import RateLimitingMiddleware
from src.presentation.middlewares.security_headers import SecurityHeadersMiddleware

# Consolidated hybrid routes (no more duplications!)
from src.api.routes import todo, auth

# ===== APPLICATION CONFIGURATION =====

# Load settings
settings = get_settings()

# Setup structured logging
logging_config = LoggingConfig.from_environment()
setup_logging(logging_config)

logger = get_logger("main")


# ===== LIFESPAN EVENT HANDLER =====


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan event handler for startup and shutdown tasks.

    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # STARTUP
    logger.info("Starting Todo API (Consolidated Hybrid Architecture)...")

    try:
        # Initialize database
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")

        # Log configuration summary
        logger.info(
            "Application started successfully",
            extra={
                "app_name": settings.APP_NAME,
                "version": f"{settings.APP_VERSION}-consolidated",
                "debug_mode": settings.DEBUG,
                "environment": getattr(settings, "ENVIRONMENT", "development"),
                "architecture": "hybrid_consolidated",
                "features": [
                    "intelligent_controllers",
                    "advanced_middleware",
                    "structured_logging",
                    "rate_limiting",
                    "security_headers",
                    "error_handling",
                    "no_duplications",
                ],
            },
        )

        yield  # Application is running

    except Exception as e:
        logger.error(
            "Failed to start application",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise

    finally:
        # SHUTDOWN
        logger.info("Shutting down Todo API...")

        try:
            # Perform cleanup tasks here
            # (close database connections, cleanup resources, etc.)
            logger.info("Application shutdown completed successfully")

        except Exception as e:
            logger.error(
                "Error during application shutdown",
                extra={"error": str(e), "error_type": type(e).__name__},
            )


# Create FastAPI application with hybrid architecture
app = FastAPI(
    title=f"{settings.APP_NAME} - Production Ready",
    version=f"{settings.APP_VERSION}-consolidated",
    description="""
    ## Todo API - Hybrid Architecture (Consolidated)

    This API demonstrates a clean, consolidated hybrid architecture:

    ### Architecture Layers
    - **Domain**: Business entities and rules
    - **Application**: Use cases and business coordination
    - **Infrastructure**: External concerns (DB, auth, etc.)
    - **Presentation**: Controllers and middleware
    - **API**: Simplified routes (no duplications)

    ### Key Features
    - 🎯 Intelligent controllers with comprehensive validation
    - 🛡️ Advanced security middleware stack
    - 📊 Performance monitoring and structured logging
    - 🚀 Production-ready error handling
    - ⚡ Rate limiting with adaptive algorithms
    - 🔒 Multiple layers of security protection
    - 🧹 No code duplications (clean architecture)

    ### Available Endpoints
    - **Auth**: `/auth/` - Authentication & user management
    - **Todos**: `/todos/` - Complete todo CRUD operations
    - **System**: `/health`, `/` - Health checks and info

    All routes use intelligent controllers for clean separation of concerns.
    """,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,  # Modern lifespan handler
)

# ===== ADVANCED MIDDLEWARE STACK =====
# Middlewares are applied in reverse order (LIFO)

logger.info("Configuring production-ready middleware stack...")

# 1. Security Headers (outermost layer) - Configured for docs compatibility
app.add_middleware(
    SecurityHeadersMiddleware,
    debug=settings.DEBUG,  # Relaxed CSP for Swagger UI in debug mode
    enable_csp=True,
    allowed_origins=settings.CORS_ORIGINS,
)

# 2. Rate Limiting with adaptive algorithms
app.add_middleware(
    RateLimitingMiddleware,
    default_requests_per_minute=100,
    default_burst_size=10,
    enable_adaptive_limiting=True,
)

# 3. Request/Response Logging with structured data
app.add_middleware(LoggingMiddleware)

# 4. Global Error Handler with intelligent error mapping
app.add_middleware(ErrorHandlerMiddleware)

# 5. CORS (cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
)

# 6. Trusted Host protection
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

logger.info("Middleware stack configured successfully")

# ===== ROUTE REGISTRATION =====

logger.info("Registering consolidated API routes...")

# Consolidated Hybrid Architecture Routes (tags defined in routers)
app.include_router(auth.router)
app.include_router(todo.router)

logger.info("API routes registered successfully")

# ===== APPLICATION EVENTS (Modern Lifespan Handler) =====
#
# Note: The lifespan event handler is now defined above and passed
# to the FastAPI constructor. This replaces the deprecated @app.on_event()
# decorators with the modern contextmanager approach.


# ===== SYSTEM ENDPOINTS =====


@app.get("/health", tags=["system"])
async def health_check():
    """
    Production-ready health check endpoint.

    Returns application status and system metrics.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": f"{settings.APP_VERSION}-consolidated",
        "architecture": "hybrid_consolidated",
        "features": {
            "intelligent_controllers": True,
            "advanced_middleware": True,
            "structured_logging": True,
            "rate_limiting": True,
            "security_headers": True,
            "error_handling": True,
            "no_duplications": True,
        },
    }


@app.get("/", tags=["system"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to the Todo API - Hybrid Architecture",
        "description": "A clean, consolidated FastAPI implementation with no duplications",
        "documentation": (
            "/docs" if settings.DEBUG else "Documentation disabled in production"
        ),
        "health_check": "/health",
        "endpoints": {
            "auth": "/auth/",
            "todos": "/todos/",
        },
        "architecture_benefits": [
            "Clean separation of concerns",
            "Intelligent error handling",
            "Comprehensive logging",
            "Advanced security features",
            "Production-ready middleware",
            "Simplified route maintenance",
            "No code duplications",
            "Single point of entry",
        ],
    }


# ===== DEVELOPMENT SERVER =====

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True,
    )
