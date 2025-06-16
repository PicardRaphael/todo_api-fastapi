from typing import Optional
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.application.dtos.user_dto import UserCreateDTO
from src.infrastructure.security.jwt import get_password_hash
from datetime import datetime


class UserUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_create: UserCreateDTO) -> User:
        # Vérifier si l'utilisateur existe déjà
        if await self.user_repository.get_user_by_email(user_create.email):
            raise ValueError("Email already registered")
        if await self.user_repository.get_user_by_username(user_create.username):
            raise ValueError("Username already taken")
        hashed_password = get_password_hash(user_create.password)
        new_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            last_login=None,
        )
        return await self.user_repository.create_user(new_user)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        return await self.user_repository.get_user_by_username(username)

    async def update_last_login(self, user_id: int) -> None:
        await self.user_repository.update_last_login(user_id)
