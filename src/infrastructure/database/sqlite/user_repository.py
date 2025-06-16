from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.domain.entities.user import User as UserEntity
from src.domain.repositories.user_repository import UserRepository
from .models import User as UserModel


class SQLiteUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, user: UserEntity) -> UserEntity:
        try:
            db_user = UserModel(
                email=user.email,
                username=user.username,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                last_login=user.last_login,
            )
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return UserEntity.model_validate(db_user)
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Username or email already exists")

    async def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        user = self.session.query(UserModel).filter(UserModel.email == email).first()
        return UserEntity.model_validate(user) if user else None

    async def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        user = (
            self.session.query(UserModel).filter(UserModel.username == username).first()
        )
        return UserEntity.model_validate(user) if user else None

    async def update_last_login(self, user_id: int) -> None:
        user = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            self.session.commit()
