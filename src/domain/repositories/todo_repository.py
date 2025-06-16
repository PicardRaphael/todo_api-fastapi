from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.todo import Todo


class TodoRepository(ABC):
    """
    Interface abstraite définissant les opérations possibles sur les Todos.
    Cette interface suit le pattern Repository et permet de découpler la logique métier
    de l'implémentation concrète de la persistance des données.

    Pour ajouter un nouveau type de stockage (ex: PostgreSQL, MongoDB), il suffit de créer
    une nouvelle classe qui implémente cette interface.
    """

    @abstractmethod
    async def get_all(self) -> List[Todo]:
        """Récupère toutes les tâches."""
        pass

    @abstractmethod
    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """
        Récupère une tâche par son ID.

        Args:
            todo_id: L'identifiant unique de la tâche

        Returns:
            La tâche si trouvée, None sinon
        """
        pass

    @abstractmethod
    async def create(self, todo: Todo) -> Todo:
        """
        Crée une nouvelle tâche.

        Args:
            todo: L'entité Todo à créer (sans ID)

        Returns:
            La tâche créée avec son ID généré
        """
        pass

    @abstractmethod
    async def update(self, todo_id: int, todo: Todo) -> Optional[Todo]:
        """
        Met à jour une tâche existante.

        Args:
            todo_id: L'identifiant de la tâche à mettre à jour
            todo: Les nouvelles données de la tâche

        Returns:
            La tâche mise à jour si trouvée, None sinon
        """
        pass

    @abstractmethod
    async def delete(self, todo_id: int) -> bool:
        """
        Supprime une tâche.

        Args:
            todo_id: L'identifiant de la tâche à supprimer

        Returns:
            True si la suppression a réussi, False si la tâche n'existait pas
        """
        pass

    @abstractmethod
    async def get_all_by_owner(self, owner_id: int) -> List[Todo]:
        """Récupère toutes les tâches d'un utilisateur."""
        pass

    @abstractmethod
    async def get_by_id_and_owner(self, todo_id: int, owner_id: int) -> Optional[Todo]:
        """Récupère une tâche par son ID et son propriétaire."""
        pass
