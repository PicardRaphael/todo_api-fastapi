from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities.todo import Todo as TodoEntity
from src.domain.repositories.todo_repository import TodoRepository
from .models import Todo as TodoModel


class SQLiteTodoRepository(TodoRepository):
    """
    Implémentation SQLite du TodoRepository.
    Cette classe concrète gère la persistance des Todos dans une base de données SQLite
    en utilisant SQLAlchemy comme ORM.

    L'utilisation de SQLAlchemy nous permet de :
    1. Gérer les connexions à la base de données
    2. Mapper les objets Python vers des tables SQL
    3. Écrire des requêtes de manière pythonique
    """

    def __init__(self, session: Session):
        """
        Initialise le repository avec une session SQLAlchemy.

        Args:
            session: Session SQLAlchemy active pour les opérations de base de données
        """
        self.session = session

    async def get_all(self) -> List[TodoEntity]:
        """
        Récupère toutes les tâches de la base de données SQLite.
        Convertit les modèles SQLAlchemy en entités de domaine.
        """
        todos = self.session.query(TodoModel).all()
        return [TodoEntity.model_validate(todo) for todo in todos]

    async def get_by_id(self, todo_id: int) -> Optional[TodoEntity]:
        """
        Récupère une tâche par son ID.
        Convertit le modèle SQLAlchemy en entité de domaine si trouvé.
        """
        todo = self.session.query(TodoModel).filter(TodoModel.id == todo_id).first()
        return TodoEntity.model_validate(todo) if todo else None

    async def create(self, todo: TodoEntity) -> TodoEntity:
        """
        Crée une nouvelle tâche dans la base de données.
        Convertit l'entité de domaine en modèle SQLAlchemy.
        """
        db_todo = TodoModel(
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            owner_id=todo.owner_id,
        )
        self.session.add(db_todo)
        self.session.commit()
        self.session.refresh(db_todo)
        return TodoEntity.model_validate(db_todo)

    async def update(self, todo_id: int, todo: TodoEntity) -> Optional[TodoEntity]:
        """
        Met à jour une tâche existante.
        Utilise model_dump pour convertir l'entité en dictionnaire et
        setattr pour mettre à jour les attributs du modèle SQLAlchemy.
        """
        db_todo = self.session.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not db_todo:
            return None

        for key, value in todo.model_dump(exclude_unset=True).items():
            setattr(db_todo, key, value)

        self.session.commit()
        self.session.refresh(db_todo)
        return TodoEntity.model_validate(db_todo)

    async def delete(self, todo_id: int) -> bool:
        """
        Supprime une tâche de la base de données.
        Retourne True si la suppression a réussi.
        """
        todo = self.session.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()
        return True

    async def get_all_by_owner(self, owner_id: int) -> List[TodoEntity]:
        todos = (
            self.session.query(TodoModel).filter(TodoModel.owner_id == owner_id).all()
        )
        return [TodoEntity.model_validate(todo) for todo in todos]

    async def get_by_id_and_owner(
        self, todo_id: int, owner_id: int
    ) -> Optional[TodoEntity]:
        todo = (
            self.session.query(TodoModel)
            .filter(TodoModel.id == todo_id, TodoModel.owner_id == owner_id)
            .first()
        )
        return TodoEntity.model_validate(todo) if todo else None
