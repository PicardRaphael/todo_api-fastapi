"""
Todo Controller - Couche Presentation

Controller intelligent pour les todos qui gère :
- Logique de présentation des opérations CRUD todos
- Validation et transformation des données
- Délégation aux Use Cases de todos
- Gestion des erreurs et logging contextualisé
- Formatage des réponses HTTP

Architecture Hybride :
- Routes simpifiées → Controller intelligent → Use Cases → Repositories
- Sépare les préoccupations HTTP de la logique métier
- Facilite les tests et la maintenance
"""

from typing import List, Optional
from fastapi import HTTPException, status

# Application layer imports
from src.application.use_cases.todo_use_cases import TodoUseCases
from src.application.dtos.todo_dto import (
    TodoCreateDTO,
    TodoUpdateDTO,
    TodoResponseDTO,
)

# Shared logging
from src.shared.logging import get_logger


class TodoController:
    """
    Controller intelligent pour les opérations Todo.

    Gère la logique de présentation et délègue la logique métier
    aux Use Cases de todos.
    """

    def __init__(self, todo_use_cases: TodoUseCases, logger):
        """
        Initialise le controller avec ses dépendances.

        Args:
            todo_use_cases (TodoUseCases): Use cases pour les todos
            logger: Logger pour le suivi des opérations
        """
        self.todo_use_cases = todo_use_cases
        self.logger = logger

    async def get_all_todos(self, user_id: int) -> List[TodoResponseDTO]:
        """
        Récupère tous les todos de l'utilisateur.

        Args:
            user_id (int): ID de l'utilisateur

        Returns:
            List[TodoResponseDTO]: Liste des todos

        Raises:
            HTTPException: En cas d'erreur
        """
        try:
            self.logger.info("Getting all todos", extra={"user_id": user_id})

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Déléguer aux Use Cases
            todos = await self.todo_use_cases.get_all_todos_by_owner(user_id)

            self.logger.info(
                "Retrieved todos successfully",
                extra={"user_id": user_id, "todos_count": len(todos)},
            )

            return [TodoResponseDTO.model_validate(todo) for todo in todos]

        except Exception as e:
            self.logger.error(
                "Failed to get todos", extra={"error": str(e), "user_id": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve todos",
            )

    async def get_todo_by_id(self, todo_id: int, user_id: int) -> TodoResponseDTO:
        """
        Récupère un todo spécifique par ID.

        Args:
            todo_id (int): ID du todo
            user_id (int): ID de l'utilisateur

        Returns:
            TodoResponseDTO: Le todo demandé

        Raises:
            TodoNotFoundError: Si le todo n'existe pas ou n'appartient pas à l'utilisateur
        """
        self.logger.info(
            "Getting todo by ID", extra={"todo_id": todo_id, "user_id": user_id}
        )

        # Validation user_id
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session",
            )

        # Déléguer aux Use Cases (les exceptions remontent automatiquement)
        todo = await self.todo_use_cases.get_todo_by_id_and_owner(todo_id, user_id)

        self.logger.info(
            "Retrieved todo successfully",
            extra={"todo_id": todo_id, "user_id": user_id},
        )

        return todo

    async def create_todo(
        self, todo_data: TodoCreateDTO, user_id: int
    ) -> TodoResponseDTO:
        """
        Crée un nouveau todo.

        Args:
            todo_data (TodoCreateDTO): Données du todo à créer
            user_id (int): ID de l'utilisateur

        Returns:
            TodoResponseDTO: Le todo créé

        Raises:
            HTTPException: En cas d'erreur de création
        """
        try:
            self.logger.info(
                "Creating new todo",
                extra={"user_id": user_id, "title": todo_data.title},
            )

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Déléguer aux Use Cases
            created_todo = await self.todo_use_cases.create_todo(todo_data, user_id)

            self.logger.info(
                "Todo created successfully",
                extra={
                    "todo_id": created_todo.id,
                    "user_id": user_id,
                    "title": created_todo.title,
                },
            )

            return created_todo

        except Exception as e:
            self.logger.error(
                "Failed to create todo",
                extra={"error": str(e), "user_id": user_id, "title": todo_data.title},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create todo"
            )

    async def update_todo(
        self, todo_id: int, todo_update: TodoUpdateDTO, user_id: int
    ) -> TodoResponseDTO:
        """
        Met à jour un todo existant.

        Args:
            todo_id (int): ID du todo à mettre à jour
            todo_update (TodoUpdateDTO): Données de mise à jour
            user_id (int): ID de l'utilisateur

        Returns:
            TodoResponseDTO: Le todo mis à jour

        Raises:
            HTTPException: En cas d'erreur ou todo introuvable
        """
        try:
            self.logger.info(
                "Updating todo", extra={"todo_id": todo_id, "user_id": user_id}
            )

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Déléguer aux Use Cases
            updated_todo = await self.todo_use_cases.update_todo(
                todo_id, todo_update, user_id
            )

            if not updated_todo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found or not yours",
                )

            self.logger.info(
                "Todo updated successfully",
                extra={"todo_id": todo_id, "user_id": user_id},
            )

            return updated_todo

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to update todo",
                extra={"error": str(e), "todo_id": todo_id, "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update todo",
            )

    async def delete_todo(self, todo_id: int, user_id: int) -> None:
        """
        Supprime un todo.

        Args:
            todo_id (int): ID du todo à supprimer
            user_id (int): ID de l'utilisateur

        Raises:
            HTTPException: En cas d'erreur ou todo introuvable
        """
        try:
            self.logger.info(
                "Deleting todo", extra={"todo_id": todo_id, "user_id": user_id}
            )

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Déléguer aux Use Cases
            deleted = await self.todo_use_cases.delete_todo(todo_id, user_id)

            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found or not yours",
                )

            self.logger.info(
                "Todo deleted successfully",
                extra={"todo_id": todo_id, "user_id": user_id},
            )

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to delete todo",
                extra={"error": str(e), "todo_id": todo_id, "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete todo",
            )

    async def complete_todo(self, todo_id: int, user_id: int) -> TodoResponseDTO:
        """
        Marque un todo comme terminé.

        Args:
            todo_id (int): ID du todo à compléter
            user_id (int): ID de l'utilisateur

        Returns:
            TodoResponseDTO: Le todo mis à jour

        Raises:
            HTTPException: En cas d'erreur
        """
        try:
            self.logger.info(
                "Completing todo", extra={"todo_id": todo_id, "user_id": user_id}
            )

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Utiliser update avec is_completed = True
            from src.application.dtos.todo_dto import TodoUpdateDTO

            update_data = TodoUpdateDTO(is_completed=True)

            updated_todo = await self.todo_use_cases.update_todo(
                todo_id, update_data, user_id
            )

            if not updated_todo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found or not yours",
                )

            self.logger.info(
                "Todo completed successfully",
                extra={"todo_id": todo_id, "user_id": user_id},
            )

            return updated_todo

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to complete todo",
                extra={"error": str(e), "todo_id": todo_id, "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete todo",
            )

    async def uncomplete_todo(self, todo_id: int, user_id: int) -> TodoResponseDTO:
        """
        Marque un todo comme non terminé.

        Args:
            todo_id (int): ID du todo à décompléter
            user_id (int): ID de l'utilisateur

        Returns:
            TodoResponseDTO: Le todo mis à jour

        Raises:
            HTTPException: En cas d'erreur
        """
        try:
            self.logger.info(
                "Uncompleting todo", extra={"todo_id": todo_id, "user_id": user_id}
            )

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Utiliser update avec is_completed = False
            from src.application.dtos.todo_dto import TodoUpdateDTO

            update_data = TodoUpdateDTO(is_completed=False)

            updated_todo = await self.todo_use_cases.update_todo(
                todo_id, update_data, user_id
            )

            if not updated_todo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found or not yours",
                )

            self.logger.info(
                "Todo uncompleted successfully",
                extra={"todo_id": todo_id, "user_id": user_id},
            )

            return updated_todo

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to uncomplete todo",
                extra={"error": str(e), "todo_id": todo_id, "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to uncomplete todo",
            )

    async def get_todos_by_priority(
        self, user_id: int, priority: int
    ) -> List[TodoResponseDTO]:
        """
        Récupère les todos par niveau de priorité.

        Args:
            user_id (int): ID de l'utilisateur
            priority (int): Niveau de priorité (1-5)

        Returns:
            List[TodoResponseDTO]: Todos filtrés par priorité

        Raises:
            HTTPException: En cas d'erreur
        """
        try:
            self.logger.info(
                "Getting todos by priority",
                extra={"user_id": user_id, "priority": priority},
            )

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Pour l'instant, récupérer tous les todos et filtrer
            # Dans une vraie implémentation, on ajouterait get_todos_by_priority aux Use Cases
            all_todos = await self.todo_use_cases.get_all_todos_by_owner(user_id)
            filtered_todos = [todo for todo in all_todos if todo.priority == priority]

            self.logger.info(
                "Retrieved todos by priority",
                extra={
                    "user_id": user_id,
                    "priority": priority,
                    "count": len(filtered_todos),
                },
            )

            return filtered_todos

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to get todos by priority",
                extra={"error": str(e), "user_id": user_id, "priority": priority},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve todos by priority",
            )

    async def get_completed_todos(self, user_id: int) -> List[TodoResponseDTO]:
        """
        Récupère tous les todos terminés.

        Args:
            user_id (int): ID de l'utilisateur

        Returns:
            List[TodoResponseDTO]: Todos terminés

        Raises:
            HTTPException: En cas d'erreur
        """
        try:
            self.logger.info("Getting completed todos", extra={"user_id": user_id})

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Filtrer les todos terminés
            all_todos = await self.todo_use_cases.get_all_todos_by_owner(user_id)
            completed_todos = [todo for todo in all_todos if todo.is_completed]

            self.logger.info(
                "Retrieved completed todos",
                extra={"user_id": user_id, "count": len(completed_todos)},
            )

            return completed_todos

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to get completed todos",
                extra={"error": str(e), "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve completed todos",
            )

    async def get_pending_todos(self, user_id: int) -> List[TodoResponseDTO]:
        """
        Récupère tous les todos en attente (non terminés).

        Args:
            user_id (int): ID de l'utilisateur

        Returns:
            List[TodoResponseDTO]: Todos en attente

        Raises:
            HTTPException: En cas d'erreur
        """
        try:
            self.logger.info("Getting pending todos", extra={"user_id": user_id})

            # Validation user_id
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user session",
                )

            # Filtrer les todos non terminés
            all_todos = await self.todo_use_cases.get_all_todos_by_owner(user_id)
            pending_todos = [todo for todo in all_todos if not todo.is_completed]

            self.logger.info(
                "Retrieved pending todos",
                extra={"user_id": user_id, "count": len(pending_todos)},
            )

            return pending_todos

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to get pending todos",
                extra={"error": str(e), "user_id": user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve pending todos",
            )
