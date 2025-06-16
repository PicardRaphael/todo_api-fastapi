from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import HTTPException, status

from src.infrastructure.config import get_settings
from src.infrastructure.database.sqlite.user_repository import SQLiteUserRepository

settings = get_settings()

# Context pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: list[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Génère un hash sécurisé du mot de passe."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un JWT token avec les données fournies.

    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Vérifie la validité d'un token JWT.

    Args:
        token: Le token JWT à vérifier

    Returns:
        TokenData contenant les informations du token

    Raises:
        HTTPException: Si le token est invalide
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub", "")  # Valeur par défaut vide si non trouvé
        if not username:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        return TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
