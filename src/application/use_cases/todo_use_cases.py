from typing import List, Optional

from src.domain.entities.todo import Todo
from src.domain.repositories.todo_repository import TodoRepository
from src.application.dtos.todo_dto import TodoCreateDTO, TodoUpdateDTO


class TodoUseCases:
    """
    Cas d'utilisation pour la gestion des tâches.
    Cette classe implémente la logique métier de l'application en utilisant
    le repository pour la persistance des données.

    Elle fait le lien entre les DTOs de l'API et les entités du domaine,
    assurant ainsi une séparation claire des responsabilités.
    """

    def __init__(self, todo_repository: TodoRepository):
        """
        Initialise les cas d'utilisation avec un repository.

        Args:
            todo_repository: Une implémentation de TodoRepository pour la persistance
        """
        self.todo_repository = todo_repository

    async def get_all_todos_by_owner(self, owner_id: int) -> List[Todo]:
        return await self.todo_repository.get_all_by_owner(owner_id)

    async def get_todo_by_id_and_owner(
        self, todo_id: int, owner_id: int
    ) -> Optional[Todo]:
        return await self.todo_repository.get_by_id_and_owner(todo_id, owner_id)

    async def create_todo(self, todo_create: TodoCreateDTO, owner_id: int) -> Todo:
        todo = Todo(id=None, owner_id=owner_id, **todo_create.model_dump())
        return await self.todo_repository.create(todo)

    async def update_todo(
        self, todo_id: int, todo_update: TodoUpdateDTO, owner_id: int
    ) -> Optional[Todo]:
        existing_todo = await self.todo_repository.get_by_id_and_owner(
            todo_id, owner_id
        )
        if not existing_todo:
            return None

        # Mettre à jour seulement les champs fournis (exclude_unset=True)
        update_data = todo_update.model_dump(exclude_unset=True)

        # Créer une nouvelle entité avec les données existantes et les nouvelles données
        updated_todo = existing_todo.model_copy(update=update_data)

        return await self.todo_repository.update(todo_id, updated_todo)

    async def delete_todo(self, todo_id: int, owner_id: int) -> bool:
        existing_todo = await self.todo_repository.get_by_id_and_owner(
            todo_id, owner_id
        )
        if not existing_todo:
            return False
        return await self.todo_repository.delete(todo_id)
