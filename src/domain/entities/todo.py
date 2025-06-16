"""
Entité Todo - Couche Domain (Clean Architecture)

Cette entité représente le concept métier central de l'application : une tâche à accomplir.
Elle appartient à la couche Domain et ne dépend d'aucune technologie externe (base de données, web, etc.).

Principes Clean Architecture respectés :
- Indépendance technologique : ne dépend pas de SQLAlchemy, FastAPI, etc.
- Logique métier pure : contient les règles business de base
- Stabilité : cette entité change rarement, elle est au cœur du système

Utilisation de Pydantic pour :
- Validation automatique des données
- Sérialisation/désérialisation JSON
- Documentation automatique des champs
- Type safety avec Python
"""

from typing import Optional
from pydantic import BaseModel, Field


class Todo(BaseModel):
    """
    Entité représentant une tâche dans le système de gestion de todos.

    Cette classe définit la structure et les règles métier d'une tâche :
    - Chaque todo appartient à un utilisateur (owner_id)
    - Les priorités vont de 1 (faible) à 5 (critique)
    - Le statut completed indique si la tâche est terminée
    - L'ID est optionnel car il est généré par la base de données

    Utilise Pydantic pour la validation et la conversion de types automatique.
    """

    # Identifiant unique - None lors de la création, généré par la DB
    id: Optional[int] = Field(
        default=None,
        description="L'identifiant unique de la tâche (auto-généré par la DB)"
    )

    # Titre de la tâche - champ obligatoire
    title: str = Field(
        description="Le titre de la tâche (obligatoire, décrit l'action à faire)"
    )

    # Description détaillée - optionnelle avec valeur par défaut
    description: str = Field(
        default="",
        description="La description détaillée de la tâche (optionnelle)"
    )

    # Statut de completion - False par défaut (tâche en cours)
    completed: bool = Field(
        default=False,
        description="Indique si la tâche est terminée (False = en cours, True = terminée)"
    )

    # Priorité de 1 à 5 - 1 par défaut (faible priorité)
    priority: int = Field(
        default=1,
        description="Priorité de la tâche (1=faible, 2=normale, 3=moyenne, 4=haute, 5=critique)"
    )

    # Propriétaire de la tâche - référence vers l'utilisateur
    owner_id: Optional[int] = Field(
        default=None,
        description="L'identifiant de l'utilisateur propriétaire de cette tâche"
    )

    class Config:
        """
        Configuration Pydantic pour l'entité Todo.

        from_attributes=True permet à Pydantic de créer des instances Todo
        directement depuis des objets SQLAlchemy (modèles de base de données).

        C'est essentiel pour la conversion entre la couche Infrastructure (SQLAlchemy)
        et la couche Domain (entités Pydantic) sans couplage direct.
        """
        from_attributes = True  # Permet la conversion depuis les modèles SQLAlchemy
