from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr
from datetime import datetime


class User(BaseModel):
    """
    Entité représentant un utilisateur du système.
    Inclut des champs pour la sécurité et l'audit.
    """

    id: Optional[int] = Field(
        default=None, description="The unique identifier of the user"
    )
    email: EmailStr = Field(description="User's email address")
    username: str = Field(description="Username for login")
    hashed_password: str = Field(description="Hashed password using bcrypt")
    is_active: bool = Field(
        default=True, description="Whether the user account is active"
    )
    is_superuser: bool = Field(
        default=False, description="Whether the user has admin privileges"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Account creation timestamp"
    )
    last_login: Optional[datetime] = Field(
        default=None, description="Last login timestamp"
    )

    class Config:
        from_attributes = True
