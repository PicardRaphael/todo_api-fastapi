"""
Entité User - Couche Domain (Clean Architecture)

Cette entité représente un utilisateur du système de gestion de todos.
Elle appartient à la couche Domain et encapsule toute la logique métier liée aux utilisateurs.

Aspects sécurité intégrés :
- Email unique pour l'identification
- Mot de passe hashé (jamais en clair)
- Système d'activation/désactivation de compte
- Gestion des privilèges (superuser)
- Audit avec timestamps (création, dernière connexion)

Principes Clean Architecture :
- Entité pure sans dépendance externe
- Validation des données avec Pydantic
- Type safety pour la sécurité
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr
from datetime import datetime


class User(BaseModel):
    """
    Entité représentant un utilisateur du système de gestion de todos.

    Cette entité contient toutes les informations nécessaires pour :
    - L'authentification (email/username + password hashé)
    - L'autorisation (is_active, is_superuser)
    - L'audit (created_at, last_login)
    - La gestion des todos (via owner_id dans Todo)

    Sécurité :
    - Le mot de passe est TOUJOURS hashé avec bcrypt
    - EmailStr valide automatiquement le format email
    - Les timestamps permettent l'audit et la conformité
    """

    # Identifiant unique - None lors de la création, généré par la DB
    id: Optional[int] = Field(
        default=None,
        description="Identifiant unique de l'utilisateur (auto-généré par la DB)"
    )

    # Email unique - utilisé pour l'identification et la récupération de compte
    email: EmailStr = Field(
        description="Adresse email de l'utilisateur (unique, format validé automatiquement)"
    )

    # Nom d'utilisateur - utilisé pour la connexion et l'affichage
    username: str = Field(
        description="Nom d'utilisateur pour la connexion (unique, lisible)"
    )

    # Mot de passe hashé - JAMAIS stocké en clair pour la sécurité
    hashed_password: str = Field(
        description="Mot de passe hashé avec bcrypt (JAMAIS en clair pour la sécurité)"
    )

    # Statut d'activation - permet de désactiver un compte sans le supprimer
    is_active: bool = Field(
        default=True,
        description="Indique si le compte utilisateur est actif (True=actif, False=désactivé)"
    )

    # Privilèges administrateur - pour les fonctionnalités admin futures
    is_superuser: bool = Field(
        default=False,
        description="Indique si l'utilisateur a des privilèges administrateur"
    )

    # Timestamp de création - pour l'audit et la conformité RGPD
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date et heure de création du compte (UTC, audit)"
    )

    # Dernière connexion - pour la sécurité et l'audit
    last_login: Optional[datetime] = Field(
        default=None,
        description="Date et heure de la dernière connexion (UTC, sécurité)"
    )

    class Config:
        """
        Configuration Pydantic pour l'entité User.

        from_attributes=True permet la conversion depuis les modèles SQLAlchemy,
        essentiel pour le mapping entre la couche Infrastructure et Domain.
        """
        from_attributes = True
