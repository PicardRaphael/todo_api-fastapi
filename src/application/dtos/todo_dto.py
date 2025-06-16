"""
DTOs Todo - Couche Application (Clean Architecture)

Les Data Transfer Objects (DTOs) servent d'interface entre les couches :
- Valident les données entrantes (API → Application)
- Formatent les données sortantes (Application → API)
- Découplent les entités métier des formats d'échange

Avantages des DTOs :
- Validation robuste avec Pydantic
- Contrôle précis des champs exposés à l'API
- Documentation automatique pour Swagger
- Type safety et auto-complétion
- Gestion des mises à jour partielles (PATCH)

Types de DTOs :
- Create : Données nécessaires pour créer une todo
- Update : Mise à jour partielle (tous champs optionnels)
- Response : Format de sortie avec ID et owner_id
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class TodoBaseDTO(BaseModel):
    """
    DTO de base contenant les champs communs aux todos.

    Sert de classe parente pour éviter la duplication de code.
    Contient toutes les validations métier communes :
    - Titre entre 3 et 50 caractères
    - Description entre 3 et 100 caractères
    - Priorité entre 1 et 5
    - Statut completed par défaut à False
    """

    # Titre de la tâche - obligatoire avec validation de longueur
    title: str = Field(
        min_length=3,           # Minimum 3 caractères pour être significatif
        max_length=50,          # Maximum 50 pour les affichages UI
        description="Le titre de la tâche (3-50 caractères, obligatoire)"
    )

    # Description détaillée - obligatoire mais peut être courte
    description: str = Field(
        min_length=3,           # Minimum pour éviter les descriptions vides
        max_length=100,         # Limite pour la lisibilité
        description="Description détaillée de la tâche (3-100 caractères)"
    )

    # Priorité numérique - système à 5 niveaux
    priority: int = Field(
        gt=0,                   # Strictement supérieur à 0 (donc >= 1)
        lt=6,                   # Strictement inférieur à 6 (donc <= 5)
        default=1,              # Priorité faible par défaut
        description="Niveau de priorité (1=faible, 2=normale, 3=moyenne, 4=haute, 5=critique)"
    )

    # Statut de completion - False par défaut (nouvelle tâche)
    completed: bool = Field(
        default=False,
        description="Indique si la tâche est terminée (False=en cours, True=terminée)"
    )


class TodoCreateDTO(TodoBaseDTO):
    """
    DTO pour la création d'une nouvelle todo.

    Hérite de TodoBaseDTO, donc tous les champs sont OBLIGATOIRES.
    Utilisé par l'endpoint POST /todos/create.

    Validation automatique :
    - Titre : 3-50 caractères
    - Description : 3-100 caractères
    - Priorité : 1-5
    - Completed : par défaut False

    L'ID et owner_id sont gérés automatiquement :
    - ID : généré par la base de données
    - owner_id : extrait du token JWT de l'utilisateur connecté
    """
    pass  # Hérite simplement de TodoBaseDTO


class TodoUpdateDTO(BaseModel):
    """
    DTO pour la mise à jour partielle d'une todo (PATCH).

    🎯 FONCTIONNALITÉ CLÉ : Mise à jour partielle
    - Tous les champs sont OPTIONNELS
    - Seuls les champs fournis sont mis à jour
    - Les autres champs restent inchangés

    Exemples d'utilisation :
    - {"title": "Nouveau titre"} → met à jour seulement le titre
    - {"priority": 4, "completed": true} → met à jour priorité et statut
    - {"description": "Nouvelle desc"} → met à jour seulement la description

    La validation s'applique uniquement aux champs fournis.
    """

    # Tous les champs sont optionnels pour la mise à jour partielle
    title: Optional[str] = Field(
        None,                   # None = champ non fourni, ne pas mettre à jour
        min_length=3,
        max_length=50,
        description="Nouveau titre de la tâche (optionnel, 3-50 caractères)"
    )

    description: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Nouvelle description de la tâche (optionnel, 3-100 caractères)"
    )

    priority: Optional[int] = Field(
        None,
        gt=0,
        lt=6,
        description="Nouvelle priorité (optionnel, 1-5)"
    )

    completed: Optional[bool] = Field(
        None,
        description="Nouveau statut de completion (optionnel)"
    )

    class Config:
        """Configuration avec exemple pour la documentation Swagger."""
        json_schema_extra = {
            "example": {
                "title": "Titre mis à jour",
                "priority": 3
                # Note : seuls title et priority sont fournis → mise à jour partielle
            }
        }


class TodoResponseDTO(TodoBaseDTO):
    """
    DTO pour les réponses API contenant une todo complète.

    Hérite de TodoBaseDTO et ajoute les champs systèmes :
    - id : identifiant unique généré par la DB
    - owner_id : propriétaire de la tâche (sécurité)

    Utilisé par tous les endpoints qui retournent des todos :
    - GET /todos/all
    - GET /todos/{id}
    - POST /todos/create (retour après création)
    - PATCH /todos/{id} (retour après mise à jour)

    La configuration from_attributes=True permet la conversion
    automatique depuis les entités Todo du domain.
    """

    # ID unique généré par la base de données
    id: int = Field(
        description="Identifiant unique de la tâche (généré automatiquement)"
    )

    # Propriétaire pour l'isolation des données et la sécurité
    owner_id: Optional[int] = Field(
        default=None,
        description="Identifiant du propriétaire de la tâche (sécurité)"
    )

    class Config:
        """
        Configuration Pydantic pour les réponses API.

        from_attributes=True : Permet la conversion automatique depuis
        les entités Todo du domain vers ce DTO de réponse.

        json_schema_extra : Exemple affiché dans la documentation Swagger.
        """
        from_attributes = True  # Conversion depuis entités Todo
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Compléter le projet",
                "description": "Finir l'implémentation de l'API FastAPI",
                "priority": 3,
                "completed": False,
                "owner_id": 1,
            }
        }
