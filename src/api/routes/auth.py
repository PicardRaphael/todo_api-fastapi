"""
Simplified Auth Routes - Hybrid Architecture Implementation

This module demonstrates simplified authentication routes that delegate
all business logic to intelligent controllers, maintaining clean separation
of concerns.

Key principles:
- Routes handle only HTTP routing and dependency injection
- Controllers coordinate authentication business logic
- Middleware handles security and logging concerns
- Clean error handling through controller layer

Benefits:
- Consistent error responses
- Centralized validation logic
- Better testability
- Improved maintainability
"""

from fastapi import APIRouter, Body, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

# Application layer
from src.application.use_cases.auth_use_cases import AuthUseCases
from src.application.dtos.auth_dto import (
    RegisterRequestDTO,
    LoginResponseDTO,
    TokenResponseDTO,
    UserResponseDTO,
)

# Presentation layer - intelligent controllers
from src.presentation.controllers.auth_controller import AuthController

# API dependencies
from src.api.dependencies import get_auth_use_cases, get_current_user
from src.infrastructure.auth.jwt_service import TokenData

# Shared logging
from src.shared.logging import get_logger

# Router configuration
router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("routes.auth")


# ===== DEPENDENCY INJECTION =====


async def get_auth_controller(
    use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> AuthController:
    """
    Dependency injection for AuthController.

    Provides a fully configured auth controller with all dependencies.
    """
    return AuthController(use_cases, logger)


# ===== SIMPLIFIED AUTHENTICATION ROUTES =====


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user (Simplified)",
    description="Register a new user account - Delegates to controller",
)
async def register(
    user_data: RegisterRequestDTO = Body(..., description="User registration data"),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Simplified user registration route.

    This route demonstrates the hybrid architecture approach:
    - Minimal HTTP handling
    - Complete delegation to intelligent controller
    - Controller handles validation, business rules, error handling
    - No manual password hashing or user creation logic

    The route is purely focused on HTTP routing.
    """
    return await controller.register_user(user_data)


@router.post(
    "/login",
    response_model=LoginResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="User login (Simplified)",
    description="Authenticate user and return access token - Delegates to controller",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Simplified user login route.

    Notice how clean this becomes:
    - No password verification logic
    - No token generation logic
    - No manual error handling
    - Controller handles all authentication complexity
    """
    return await controller.authenticate_user(form_data.username, form_data.password)


@router.post(
    "/token",
    response_model=TokenResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get access token (Simplified)",
    description="OAuth2 compatible token endpoint - Delegates to controller",
)
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Simplified OAuth2 token endpoint.

    This provides OAuth2-compatible token generation while
    maintaining clean architecture separation.
    """
    return await controller.generate_access_token(
        form_data.username, form_data.password
    )


@router.post(
    "/refresh",
    response_model=TokenResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token (Simplified)",
    description="Refresh an expired access token - Delegates to controller",
)
async def refresh_token(
    refresh_token_data: dict = Body(..., description="Refresh token data"),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Simplified token refresh route.

    The controller handles:
    - Refresh token validation
    - New token generation
    - Security logging
    - Error handling
    """
    refresh_token = refresh_token_data.get("refresh_token")

    # Validate refresh_token
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required"
        )

    return await controller.refresh_access_token(refresh_token)


@router.get(
    "/me",
    response_model=UserResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get current user (Simplified)",
    description="Get current authenticated user info - Delegates to controller",
)
async def get_current_user_info(
    controller: AuthController = Depends(get_auth_controller),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Simplified current user info route.

    This shows how even simple operations benefit from
    controller delegation for consistency and logging.
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    return await controller.get_current_user_info(user_id)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout (Simplified)",
    description="Logout user and invalidate token - Delegates to controller",
)
async def logout(
    controller: AuthController = Depends(get_auth_controller),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Simplified logout route.

    The controller handles:
    - Token invalidation
    - Security logging
    - Cleanup operations
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    await controller.logout_user(user_id, current_user.token_id)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password (Simplified)",
    description="Change user password - Delegates to controller",
)
async def change_password(
    password_data: dict = Body(..., description="Password change data"),
    controller: AuthController = Depends(get_auth_controller),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Simplified password change route.

    The controller handles:
    - Current password verification
    - Password policy validation
    - Secure password update
    - Security logging
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")

    # Validate password data
    if not old_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both old_password and new_password are required",
        )

    await controller.change_user_password(user_id, old_password, new_password)


@router.delete(
    "/account",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account (Simplified)",
    description="Delete user account and all data - Delegates to controller",
)
async def delete_account(
    confirmation_data: dict = Body(..., description="Account deletion confirmation"),
    controller: AuthController = Depends(get_auth_controller),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Simplified account deletion route.

    The controller handles:
    - Password confirmation
    - Account deletion cascade
    - Security logging
    - Cleanup operations
    """
    # Validate user_id is not None for type safety
    if current_user.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user session"
        )
    user_id: int = current_user.user_id

    password = confirmation_data.get("password")
    confirm_deletion = confirmation_data.get("confirm_deletion", False)

    # Validate confirmation data
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required for account deletion",
        )

    if not confirm_deletion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion must be explicitly confirmed",
        )

    await controller.delete_user_account(user_id)
