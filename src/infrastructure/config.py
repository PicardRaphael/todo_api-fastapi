from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis les variables d'environnement."""

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Application
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    ENVIRONMENT: str

    # Server
    HOST: str
    PORT: int

    # Security
    CORS_ORIGINS: List[str]
    ALLOWED_HOSTS: List[str]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance unique des paramètres de l'application."""
    return Settings()
