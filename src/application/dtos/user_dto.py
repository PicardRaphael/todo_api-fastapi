from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreateDTO(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="User password")


class UserDetailDTO(BaseModel):
    """DTO détaillé pour les informations utilisateur avec champs admin."""

    id: Optional[int] = Field(None, description="The unique identifier of the user")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether the user has admin privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True
