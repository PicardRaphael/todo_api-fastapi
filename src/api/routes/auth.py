from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from src.infrastructure.database.sqlite.config import get_db
from src.infrastructure.database.sqlite.user_repository import SQLiteUserRepository
from src.infrastructure.security.jwt import (
    Token,
    create_access_token,
    verify_password,
)
from src.infrastructure.config import get_settings
from src.domain.entities.user import User
from src.application.dtos.user_dto import UserCreateDTO, UserResponseDTO
from src.application.use_cases.user_use_cases import UserUseCases

settings = get_settings()
router = APIRouter(tags=["authentication"])


# Dépendance pour injecter UserUseCases
async def get_user_use_cases(db: Session = Depends(get_db)):
    repo = SQLiteUserRepository(db)
    return UserUseCases(repo)


@router.post("/register", response_model=UserResponseDTO)
async def register_user(
    user_data: UserCreateDTO, use_cases: UserUseCases = Depends(get_user_use_cases)
):
    """
    Enregistre un nouvel utilisateur.
    """
    # Vérifier si l'utilisateur existe déjà
    if await use_cases.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    if await use_cases.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    try:
        created_user = await use_cases.register_user(user_data)
        return UserResponseDTO.model_validate(created_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_cases: UserUseCases = Depends(get_user_use_cases),
):
    """
    Authentifie un utilisateur et retourne un token JWT.
    """
    user = await use_cases.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    if user.id is not None:
        await use_cases.update_last_login(user.id)
    scopes = ["todos:read", "todos:write", "todos:delete"]
    if user.is_superuser:
        scopes.append("admin")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
