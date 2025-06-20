"""
Data Transfer Objects (DTOs) for authentication operations.

This module contains DTOs for authentication requests and responses,
providing clean data contracts between layers.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.domain.entities.user import User
from src.shared.exceptions.validation.password import WeakPasswordError
from src.shared.exceptions.validation.format import (
    InvalidEmailError,
    InvalidUsernameError,
)


class LoginRequestDTO(BaseModel):
    """DTO for user login requests."""

    username: str = Field(..., min_length=3, description="Username or email address")
    password: str = Field(..., min_length=1, description="User password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"username": "johndoe", "password": "securepassword123"}
        }
    )


class RegisterRequestDTO(BaseModel):
    """DTO for user registration requests."""

    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email format using InvalidEmailError."""
        InvalidEmailError.validate_email(v)
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format using InvalidUsernameError."""
        InvalidUsernameError.validate_username(v)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength using WeakPasswordError."""
        requirements = [
            "At least 8 characters long",
            "At least one uppercase letter",
            "At least one lowercase letter",
            "At least one digit",
            "At least one special character (!@#$%^&*)",
        ]

        missing_requirements = []

        if len(v) < 8:
            missing_requirements.append("At least 8 characters long")
        if not any(c.isupper() for c in v):
            missing_requirements.append("At least one uppercase letter")
        if not any(c.islower() for c in v):
            missing_requirements.append("At least one lowercase letter")
        if not any(c.isdigit() for c in v):
            missing_requirements.append("At least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            missing_requirements.append("At least one special character (!@#$%^&*)")

        if missing_requirements:
            raise WeakPasswordError(
                password_length=len(v),
                requirements=requirements,
                missing_requirements=missing_requirements,
            )

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "username": "johndoe",
                "password": "SecurePass123",
            }
        }
    )


class TokenRefreshRequestDTO(BaseModel):
    """DTO for token refresh requests."""

    refresh_token: str = Field(..., description="Valid refresh token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )


class TokenResponseDTO(BaseModel):
    """DTO for token-only responses."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )


class UserResponseDTO(BaseModel):
    """DTO for user information in responses."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")

    @classmethod
    def from_user(cls, user: User) -> "UserResponseDTO":
        """Create DTO from User entity."""
        return cls(
            id=user.id or 0,  # Handle None id with default
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True,
                "created_at": "2023-01-01T12:00:00Z",
            }
        },
    )


class LoginResponseDTO(BaseModel):
    """DTO for login responses including user data and tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponseDTO = Field(..., description="User information")

    @classmethod
    def create(
        cls, access_token: str, refresh_token: str, user: User, expires_in: int = 3600
    ) -> "LoginResponseDTO":
        """Create login response from tokens and user."""
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponseDTO.from_user(user),
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "is_active": True,
                    "created_at": "2023-01-01T12:00:00Z",
                },
            }
        }
    )


class ChangePasswordRequestDTO(BaseModel):
    """DTO for password change requests."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength using WeakPasswordError."""
        requirements = [
            "At least 8 characters long",
            "At least one uppercase letter",
            "At least one lowercase letter",
            "At least one digit",
            "At least one special character (!@#$%^&*)",
        ]

        missing_requirements = []

        if len(v) < 8:
            missing_requirements.append("At least 8 characters long")
        if not any(c.isupper() for c in v):
            missing_requirements.append("At least one uppercase letter")
        if not any(c.islower() for c in v):
            missing_requirements.append("At least one lowercase letter")
        if not any(c.isdigit() for c in v):
            missing_requirements.append("At least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            missing_requirements.append("At least one special character (!@#$%^&*)")

        if missing_requirements:
            raise WeakPasswordError(
                password_length=len(v),
                requirements=requirements,
                missing_requirements=missing_requirements,
            )

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "NewSecurePass456",
            }
        }
    )
