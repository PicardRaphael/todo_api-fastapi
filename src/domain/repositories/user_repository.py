from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User


class UserRepository(ABC):
    """Interface abstraite pour la gestion des utilisateurs."""

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Crée un nouvel utilisateur."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email."""
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur."""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: int) -> None:
        """Met à jour la date de dernière connexion."""
        pass
