"""
Interface TodoRepository - Couche Domain (Clean Architecture)

Cette interface définit le contrat pour la persistance des entités Todo.
Elle appartient à la couche Domain mais ne connaît AUCUN détail d'implémentation.

Pattern Repository :
- Encapsule la logique d'accès aux données
- Permet de changer de base de données sans impacter la logique métier
- Facilite les tests unitaires avec des mocks
- Respecte le principe d'inversion de dépendance (DIP)

Implémentations possibles :
- SQLiteRepository (actuellement utilisée)
- PostgreSQLRepository (future)
- MongoDBRepository (future)
- InMemoryRepository (pour les tests)

Sécurité intégrée :
- Toutes les méthodes incluent l'owner_id pour l'isolation des données
- Aucune méthode ne permet d'accéder aux todos d'autres utilisateurs
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.todo import Todo


class TodoRepository(ABC):
    """
    Interface abstraite définissant les opérations de persistance pour les entités Todo.

    Cette interface suit le pattern Repository de la Clean Architecture :

    Avantages :
    - Découplage total entre la logique métier et la persistance
    - Facilite le changement de base de données (SQLite → PostgreSQL → MongoDB)
    - Permet les tests unitaires avec des mocks/stubs
    - Respecte le principe d'inversion de dépendance (DIP)

    Sécurité :
    - Toutes les opérations incluent la notion de propriétaire (owner_id)
    - Isolation stricte des données entre utilisateurs
    - Aucune méthode ne permet l'accès cross-utilisateur

    Implémentations :
    - SQLiteTodoRepository : Implémentation actuelle avec SQLAlchemy
    - Futures : PostgreSQL, MongoDB, Redis, etc.
    """

    # ===== MÉTHODES CRUD DE BASE =====

    @abstractmethod
    async def get_all(self) -> List[Todo]:
        """
        Récupère toutes les tâches (sans filtrage par utilisateur).

        ⚠️ ATTENTION : Cette méthode est utilisée pour l'administration uniquement.
        Pour les utilisateurs normaux, utilisez get_all_by_owner().

        Returns:
            List[Todo]: Liste de toutes les tâches du système
        """
        pass

    @abstractmethod
    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        """
        Récupère une tâche par son identifiant unique.

        ⚠️ ATTENTION : Cette méthode ne vérifie PAS le propriétaire.
        Pour les utilisateurs normaux, utilisez get_by_id_and_owner().

        Args:
            todo_id (int): L'identifiant unique de la tâche

        Returns:
            Optional[Todo]: La tâche si trouvée, None sinon
        """
        pass

    @abstractmethod
    async def create(self, todo: Todo) -> Todo:
        """
        Crée une nouvelle tâche dans le système de persistance.

        L'ID de la tâche doit être None en entrée et sera généré automatiquement
        par le système de persistance (auto-increment en base de données).

        Args:
            todo (Todo): L'entité Todo à créer (avec id=None)

        Returns:
            Todo: La tâche créée avec son ID généré et tous les champs persistés

        Raises:
            ValueError: Si todo.id n'est pas None
            Exception: En cas d'erreur de persistance
        """
        pass

    @abstractmethod
    async def update(self, todo_id: int, todo: Todo) -> Optional[Todo]:
        """
        Met à jour une tâche existante avec de nouvelles données.

        Utilise la technique du "partial update" : seuls les champs fournis
        dans l'entité todo sont mis à jour (exclude_unset=True).

        Args:
            todo_id (int): L'identifiant de la tâche à mettre à jour
            todo (Todo): L'entité contenant les nouvelles données

        Returns:
            Optional[Todo]: La tâche mise à jour si trouvée, None si inexistante

        Note:
            Cette méthode ne vérifie PAS le propriétaire.
            Utilisez les use cases pour la logique de sécurité.
        """
        pass

    @abstractmethod
    async def delete(self, todo_id: int) -> bool:
        """
        Supprime définitivement une tâche du système.

        ⚠️ SUPPRESSION DÉFINITIVE : Cette action est irréversible.

        Args:
            todo_id (int): L'identifiant de la tâche à supprimer

        Returns:
            bool: True si la suppression a réussi, False si la tâche n'existait pas

        Note:
            Cette méthode ne vérifie PAS le propriétaire.
            Utilisez les use cases pour la logique de sécurité.
        """
        pass

    # ===== MÉTHODES AVEC SÉCURITÉ INTÉGRÉE =====

    @abstractmethod
    async def get_all_by_owner(self, owner_id: int) -> List[Todo]:
        """
        Récupère toutes les tâches appartenant à un utilisateur spécifique.

        🛡️ SÉCURITÉ : Cette méthode garantit l'isolation des données.
        Chaque utilisateur ne voit que ses propres tâches.

        Args:
            owner_id (int): L'identifiant de l'utilisateur propriétaire

        Returns:
            List[Todo]: Liste des tâches de l'utilisateur (peut être vide)

        Note:
            Retourne une liste vide si l'utilisateur n'a aucune tâche.
        """
        pass

    @abstractmethod
    async def get_by_id_and_owner(self, todo_id: int, owner_id: int) -> Optional[Todo]:
        """
        Récupère une tâche par son ID ET son propriétaire.

        🛡️ SÉCURITÉ : Cette méthode est la version sécurisée de get_by_id().
        Elle garantit qu'un utilisateur ne peut accéder qu'à ses propres tâches.

        Args:
            todo_id (int): L'identifiant de la tâche
            owner_id (int): L'identifiant du propriétaire

        Returns:
            Optional[Todo]: La tâche si trouvée ET appartenant à l'utilisateur, None sinon

        Cas de retour None :
            - La tâche n'existe pas
            - La tâche existe mais appartient à un autre utilisateur
        """
        pass
