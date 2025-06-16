"""
Use Cases Todo - Couche Application (Clean Architecture)

Cette classe implémente la logique métier de l'application Todo.
Elle orchestre les interactions entre les DTOs (API) et les entités (Domain).

Responsabilités des Use Cases :
- Logique métier pure (sans dépendance technique)
- Orchestration des entités et repositories
- Conversion entre DTOs et entités
- Validation des règles business
- Gestion de la sécurité (isolation par owner_id)

Position dans Clean Architecture :
- Dépend de : Domain Layer (entités, repositories)
- Utilisé par : API Layer (routes FastAPI)
- Ne connaît pas : Base de données, HTTP, JWT (détails techniques)

Pattern Use Case :
- Un use case = une action métier (créer, lire, modifier, supprimer)
- Chaque méthode représente un cas d'utilisation spécifique
- Réutilisable pour différentes interfaces (REST, GraphQL, CLI, etc.)
"""

from typing import List, Optional

from src.domain.entities.todo import Todo
from src.domain.repositories.todo_repository import TodoRepository
from src.application.dtos.todo_dto import TodoCreateDTO, TodoUpdateDTO


class TodoUseCases:
    """
    Orchestrateur de la logique métier pour la gestion des todos.

    Cette classe centralise tous les cas d'utilisation liés aux todos :
    - Consultation (avec sécurité par propriétaire)
    - Création (avec attribution automatique du propriétaire)
    - Mise à jour partielle (avec validation de propriété)
    - Suppression (avec validation de propriété)

    Principes appliqués :
    - Injection de dépendance (repository injecté)
    - Sécurité by design (toujours vérifier owner_id)
    - Single Responsibility (chaque méthode = 1 cas d'usage)
    - Clean Architecture (pas de dépendance technique)

    Threading Safety : ⚠️ Cette classe n'est PAS thread-safe.
    Créez une nouvelle instance par requête (FastAPI le fait automatiquement).
    """

    def __init__(self, todo_repository: TodoRepository):
        """
        Initialise les use cases avec injection de dépendance.

        Le repository est injecté depuis la couche Infrastructure,
        respectant ainsi le principe d'inversion de dépendance (DIP).

        Args:
            todo_repository (TodoRepository): Implémentation concrète du repository
                (ex: SQLiteTodoRepository, PostgreSQLTodoRepository, etc.)
        """
        self.todo_repository = todo_repository

    # ===== CONSULTATION SÉCURISÉE =====

    async def get_all_todos_by_owner(self, owner_id: int) -> List[Todo]:
        """
        Récupère toutes les todos d'un utilisateur spécifique.

        🛡️ SÉCURITÉ : Isolation stricte par propriétaire.
        Un utilisateur ne peut voir que ses propres todos.

        Use Case : "En tant qu'utilisateur, je veux voir toutes mes tâches"

        Args:
            owner_id (int): Identifiant de l'utilisateur connecté (extrait du JWT)

        Returns:
            List[Todo]: Liste des todos de l'utilisateur (peut être vide)

        Note:
            Cette méthode ne lance jamais d'exception, retourne une liste vide
            si l'utilisateur n'a aucune todo.
        """
        return await self.todo_repository.get_all_by_owner(owner_id)

    async def get_todo_by_id_and_owner(
        self, todo_id: int, owner_id: int
    ) -> Optional[Todo]:
        """
        Récupère une todo spécifique appartenant à un utilisateur.

        🛡️ SÉCURITÉ : Double vérification (ID + propriétaire).
        Empêche l'accès aux todos d'autres utilisateurs même avec un ID valide.

        Use Case : "En tant qu'utilisateur, je veux voir le détail d'une de mes tâches"

        Args:
            todo_id (int): Identifiant de la todo
            owner_id (int): Identifiant de l'utilisateur connecté

        Returns:
            Optional[Todo]: La todo si trouvée ET appartenant à l'utilisateur, None sinon

        Cas de retour None :
            - Todo inexistante
            - Todo appartenant à un autre utilisateur
            - ID invalide
        """
        return await self.todo_repository.get_by_id_and_owner(todo_id, owner_id)

    # ===== CRÉATION =====

    async def create_todo(self, todo_create: TodoCreateDTO, owner_id: int) -> Todo:
        """
        Crée une nouvelle todo pour un utilisateur.

        🔄 CONVERSION DTO → ENTITÉ :
        1. Valide les données avec TodoCreateDTO
        2. Convertit le DTO en entité Todo
        3. Ajoute automatiquement l'owner_id
        4. Persiste via le repository

        Use Case : "En tant qu'utilisateur, je veux créer une nouvelle tâche"

        Args:
            todo_create (TodoCreateDTO): Données validées de la todo à créer
            owner_id (int): Identifiant de l'utilisateur créateur

        Returns:
            Todo: La todo créée avec son ID généré par la DB

        Raises:
            ValidationError: Si les données du DTO sont invalides
            Exception: En cas d'erreur de persistance

        Note:
            L'ID est automatiquement généré (None en entrée).
            L'owner_id est automatiquement assigné (sécurité).
        """
        # Conversion DTO → Entité avec ajout de l'owner_id
        todo = Todo(id=None, owner_id=owner_id, **todo_create.model_dump())
        return await self.todo_repository.create(todo)

    # ===== MISE À JOUR PARTIELLE =====

    async def update_todo(
        self, todo_id: int, todo_update: TodoUpdateDTO, owner_id: int
    ) -> Optional[Todo]:
        """
        Met à jour partiellement une todo existante.

        🎯 MISE À JOUR PARTIELLE (PATCH) :
        1. Vérifie que la todo existe et appartient à l'utilisateur
        2. Extrait uniquement les champs fournis (exclude_unset=True)
        3. Fusionne avec les données existantes (model_copy)
        4. Persiste les modifications

        🛡️ SÉCURITÉ : Vérification de propriété avant modification.

        Use Case : "En tant qu'utilisateur, je veux modifier certains champs de ma tâche"

        Exemples :
        - update_todo(1, {"title": "Nouveau titre"}, user_id) → change le titre
        - update_todo(1, {"completed": True}, user_id) → marque comme terminée
        - update_todo(1, {"priority": 5, "title": "Urgent!"}, user_id) → change 2 champs

        Args:
            todo_id (int): Identifiant de la todo à modifier
            todo_update (TodoUpdateDTO): Données à mettre à jour (champs optionnels)
            owner_id (int): Identifiant du propriétaire

        Returns:
            Optional[Todo]: La todo mise à jour, None si inexistante ou pas propriétaire

        Workflow détaillé :
            1. Récupération sécurisée de la todo existante
            2. Extraction des champs modifiés (exclude_unset=True)
            3. Fusion intelligente avec model_copy(update=...)
            4. Persistance via repository
        """
        # Étape 1 : Vérification d'existence et de propriété
        existing_todo = await self.todo_repository.get_by_id_and_owner(
            todo_id, owner_id
        )
        if not existing_todo:
            return None  # Todo inexistante ou pas propriétaire

        # Étape 2 : Extraction des champs à mettre à jour
        # exclude_unset=True → uniquement les champs fournis dans la requête
        update_data = todo_update.model_dump(exclude_unset=True)

        # Étape 3 : Fusion intelligente des données
        # model_copy(update=...) crée une nouvelle instance avec les champs mis à jour
        updated_todo = existing_todo.model_copy(update=update_data)

        # Étape 4 : Persistance
        return await self.todo_repository.update(todo_id, updated_todo)

    # ===== SUPPRESSION =====

    async def delete_todo(self, todo_id: int, owner_id: int) -> bool:
        """
        Supprime définitivement une todo.

        🛡️ SÉCURITÉ : Vérification de propriété avant suppression.
        Empêche la suppression des todos d'autres utilisateurs.

        ⚠️ SUPPRESSION DÉFINITIVE : Cette action est irréversible.

        Use Case : "En tant qu'utilisateur, je veux supprimer une de mes tâches"

        Args:
            todo_id (int): Identifiant de la todo à supprimer
            owner_id (int): Identifiant du propriétaire

        Returns:
            bool: True si suppression réussie, False si todo inexistante ou pas propriétaire

        Workflow :
            1. Vérification d'existence et de propriété
            2. Suppression définitive si validée
            3. Retour du statut de l'opération
        """
        # Vérification de propriété avant suppression
        existing_todo = await self.todo_repository.get_by_id_and_owner(
            todo_id, owner_id
        )
        if not existing_todo:
            return False  # Todo inexistante ou pas propriétaire

        # Suppression définitive
        return await self.todo_repository.delete(todo_id)
