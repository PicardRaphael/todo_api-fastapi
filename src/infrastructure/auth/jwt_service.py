"""
JWT Service for the Todo API.

This service handles JWT token creation, validation, and decoding
for authentication and authorization purposes.
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import HTTPException, status
from src.infrastructure.config import get_settings
from src.shared.exceptions.auth import (
    InvalidTokenError,
    ExpiredTokenError,
    MissingTokenError,
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: list[str] = []
    token_id: Optional[str] = None  # Pour logout


def verify_token(token: str) -> TokenData:
    """
    Fonction standalone pour vérifier un token JWT.

    Args:
        token: Le token JWT à vérifier

    Returns:
        TokenData contenant les informations du token

    Raises:
        InvalidTokenError: Si le token est invalide ou malformé
        ExpiredTokenError: Si le token a expiré
        MissingTokenError: Si le token est vide ou None
    """
    # Vérifier si le token est fourni
    if not token or token.strip() == "":
        raise MissingTokenError()

    try:
        settings = get_settings()
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub", "")
        if not username:
            raise InvalidTokenError("Token does not contain valid user information")

        token_scopes = payload.get("scopes", [])
        return TokenData(username=username, scopes=token_scopes)
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError()
    except Exception:
        raise InvalidTokenError(
            "Token format is invalid or signature verification failed"
        )


class JWTService:
    """
    Service for handling JWT operations.

    Provides methods for creating, validating, and decoding JWT tokens
    for authentication and authorization.
    """

    def __init__(self):
        """Initialize JWT service with configuration."""
        self.settings = get_settings()
        self.secret_key = self.settings.JWT_SECRET_KEY
        self.algorithm = self.settings.JWT_ALGORITHM
        self.access_token_expire = self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = getattr(
            self.settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7
        )

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data (Dict[str, Any]): Payload data to encode
            expires_delta (timedelta, optional): Custom expiration time

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)

        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token.

        Args:
            data (Dict[str, Any]): Payload data to encode

        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)

        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token (str): JWT token to decode

        Returns:
            Dict[str, Any]: Decoded payload

        Raises:
            InvalidTokenError: If token is invalid
            ExpiredTokenError: If token has expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError("Access token has expired")
        except Exception:
            raise InvalidTokenError("Token signature verification failed")

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify a token and check its type.

        Args:
            token (str): JWT token to verify
            token_type (str): Expected token type ('access' or 'refresh')

        Returns:
            Dict[str, Any]: Decoded payload

        Raises:
            InvalidTokenError: If token is invalid or wrong type
            ExpiredTokenError: If token has expired
        """
        payload = self.decode_token(token)

        if payload.get("type") != token_type:
            raise InvalidTokenError(f"Expected {token_type} token")

        return payload
