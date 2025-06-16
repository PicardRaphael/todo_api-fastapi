"""
Hybrid Architecture FastAPI Application

This is the main application file demonstrating the complete hybrid architecture
that combines the best of both Clean Architecture and MVC patterns.

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
"""

import logging
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
from src.presentation.middlewares.auth_middleware import AuthenticationMiddleware

# Simplified routes (hybrid architecture)
from src.api.routes import todo_simplified, auth_simplified

# Original routes for comparison
from src.api.routes import todo, auth

# ===== APPLICATION CONFIGURATION =====

# Load settings
settings = get_settings()

# Setup structured logging
logging_config = LoggingConfig.from_environment()
setup_logging(logging_config)

logger = get_logger("main_hybrid")

# Create FastAPI application
app = FastAPI(
    title=f"{settings.APP_NAME} - Hybrid Architecture",
    version=f"{settings.APP_VERSION}-hybrid",
    description="""
    ## Hybrid Architecture Demo

    This API demonstrates a sophisticated hybrid architecture combining:

    ### Architecture Layers
    - **Domain**: Business entities and rules
    - **Application**: Use cases and business coordination
    - **Infrastructure**: External concerns (DB, auth, etc.)
    - **Presentation**: Controllers and middleware
    - **API**: Simplified routes

    ### Key Features
    - 🎯 Intelligent controllers with comprehensive validation
    - 🛡️ Advanced security middleware stack
    - 📊 Performance monitoring and structured logging
    - 🚀 Production-ready error handling
    - ⚡ Rate limiting with adaptive algorithms
    - 🔒 Multiple layers of security protection

    ### Available Endpoints
    - **Original Routes**: `/todos/`, `/auth/` - Full-featured original implementation
    - **Simplified Routes**: `/todos-simplified/`, `/auth-simplified/` - Hybrid architecture demo

    The simplified routes demonstrate how clean and maintainable code becomes
    when using intelligent controllers and proper separation of concerns.
    """,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ===== MIDDLEWARE STACK =====
# Middlewares are applied in reverse order (LIFO)

logger.info("Configuring advanced middleware stack...")

# 1. Security Headers (outermost layer)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate Limiting
app.add_middleware(
    RateLimitingMiddleware,
    default_requests_per_minute=100,
    default_burst_size=10,
    enable_adaptive_limiting=True,
)

# 3. Request/Response Logging
app.add_middleware(LoggingMiddleware)

# 4. Global Error Handler
app.add_middleware(ErrorHandlerMiddleware)

# 5. CORS (built-in FastAPI middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
)

# 6. Trusted Host (built-in FastAPI middleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Note: AuthenticationMiddleware is applied per route via dependencies for fine-grained control

logger.info("Middleware stack configured successfully")

# ===== ROUTE REGISTRATION =====

logger.info("Registering API routes...")

# Hybrid Architecture Routes (Simplified)
app.include_router(todo_simplified.router, prefix="/api/v1", tags=["todos-hybrid"])

app.include_router(auth_simplified.router, prefix="/api/v1", tags=["auth-hybrid"])

# Original Routes (for comparison)
app.include_router(todo.router, prefix="/api/v1/original", tags=["todos-original"])

app.include_router(auth.router, prefix="/api/v1/original", tags=["auth-original"])

logger.info("API routes registered successfully")

# ===== APPLICATION EVENTS =====


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Initializes database, logging, and other startup tasks.
    """
    logger.info("Starting Hybrid Architecture Todo API...")

    try:
        # Initialize database
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")

        # Log configuration summary
        logger.info_structured(
            "Application started successfully",
            app_name=settings.APP_NAME,
            version=f"{settings.APP_VERSION}-hybrid",
            debug_mode=settings.DEBUG,
            environment=getattr(settings, "ENVIRONMENT", "development"),
            features=[
                "intelligent_controllers",
                "advanced_middleware",
                "structured_logging",
                "rate_limiting",
                "security_headers",
                "error_handling",
            ],
        )

    except Exception as e:
        logger.error_structured(
            "Failed to start application", error=str(e), error_type=type(e).__name__
        )
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.

    Performs cleanup tasks before application shutdown.
    """
    logger.info("Shutting down Hybrid Architecture Todo API...")

    try:
        # Perform cleanup tasks here
        # (close database connections, cleanup resources, etc.)

        logger.info("Application shutdown completed successfully")

    except Exception as e:
        logger.error_structured(
            "Error during application shutdown",
            error=str(e),
            error_type=type(e).__name__,
        )


# ===== HEALTH CHECK ENDPOINTS =====


@app.get("/health", tags=["system"])
async def health_check():
    """
    Basic health check endpoint.

    Returns application status and basic metrics.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": f"{settings.APP_VERSION}-hybrid",
        "architecture": "hybrid",
        "features": {
            "intelligent_controllers": True,
            "advanced_middleware": True,
            "structured_logging": True,
            "rate_limiting": True,
            "security_headers": True,
            "error_handling": True,
        },
    }


@app.get("/", tags=["system"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to the Hybrid Architecture Todo API",
        "description": "A sophisticated FastAPI implementation combining Clean Architecture and MVC patterns",
        "documentation": (
            "/docs" if settings.DEBUG else "Documentation disabled in production"
        ),
        "health_check": "/health",
        "endpoints": {
            "hybrid_routes": {"todos": "/api/v1/todos", "auth": "/api/v1/auth"},
            "original_routes": {
                "todos": "/api/v1/original/todos",
                "auth": "/api/v1/original/auth",
            },
        },
        "architecture_benefits": [
            "Clean separation of concerns",
            "Intelligent error handling",
            "Comprehensive logging",
            "Advanced security features",
            "Production-ready middleware",
            "Simplified route maintenance",
        ],
    }


# ===== DEVELOPMENT SERVER =====

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")

    uvicorn.run(
        "main_hybrid:app",
        host=settings.HOST,
        port=settings.PORT + 1,  # Use different port for hybrid version
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True,
    )
