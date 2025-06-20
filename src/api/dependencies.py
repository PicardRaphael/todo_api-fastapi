"""
Dépendances FastAPI - Couche API (Clean Architecture)

Ce module centralise toutes les dépendances injectées par FastAPI :
- Authentification et autorisation JWT
- Injection des Use Cases avec repositories
- Validation des scopes et permissions
- Gestion des erreurs d'authentification

Pattern Dependency Injection :
- Respecte l'inversion de dépendance (DIP)
- Facilite les tests unitaires (mock dependencies)
- Centralise la configuration des dépendances
- Permet la composition modulaire des services

Sécurité intégrée :
- Validation JWT automatique
- Vérification des scopes granulaires
- Gestion des erreurs standardisée
- Extraction sécurisée de l'user_id

Utilisation dans les routes :
- current_user = Security(get_current_user, scopes=["todos:read"])
- use_cases = Depends(get_todo_use_cases)
"""

from typing import Generator, Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, HTTPBearer
from sqlalchemy.orm import Session

# Imports Infrastructure (base de données et sécurité)
from src.infrastructure.database.sqlite.config import get_db
from src.infrastructure.database.sqlite.repository import SQLiteTodoRepository
from src.infrastructure.database.sqlite.user_repository import SQLiteUserRepository

# Imports Application (Use Cases)
from src.application.use_cases.todo_use_cases import TodoUseCases
from src.application.use_cases.auth_use_cases import AuthUseCases

# Imports Sécurité (JWT)
from src.infrastructure.auth.jwt_service import JWTService, verify_token, TokenData

# Imports exceptions JWT
from src.shared.exceptions.auth import (
    InvalidTokenError,
    ExpiredTokenError,
    MissingTokenError,
)


# ===== SCHÉMAS D'AUTHENTIFICATION =====

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",  # URL pour obtenir le token (endpoint /token)
    scopes={
        # Scopes granulaires pour contrôler les permissions
        "todos:read": "Lecture des todos (GET)",
        "todos:write": "Création et modification des todos (POST, PATCH)",
        "todos:delete": "Suppression des todos (DELETE)",
        "admin": "Accès administrateur (toutes opérations)",
    },
)
"""
Schéma OAuth2 principal pour l'authentification JWT.

Configuration :
- tokenUrl="/token" : URL pour obtenir un token d'accès
- scopes : Permissions granulaires pour contrôler l'accès

Intégration Swagger UI :
- Bouton "Authorize" automatique dans /docs
- Formulaire username/password standard OAuth2
- Sélection des scopes requis

Utilisation dans les routes :
    current_user = Security(get_current_user, scopes=["todos:read"])
"""

bearer_scheme = HTTPBearer()
"""
Schéma Bearer alternatif pour les tests manuels.

Plus simple que OAuth2 pour :
- Tests avec curl/Postman
- Débogage manuel
- Intégration avec outils tiers

Utilisation :
    Authorization: Bearer <token_jwt>
"""


# ===== DÉPENDANCES D'AUTHENTIFICATION =====


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> TokenData:
    """
    Dépendance centrale pour l'authentification et l'autorisation.

    🛡️ PROCESSUS D'AUTHENTIFICATION :
    1. Extraction du token JWT depuis l'header Authorization
    2. Validation de la signature et de l'expiration
    3. Récupération de l'utilisateur depuis la base de données
    4. Vérification des scopes requis pour l'endpoint
    5. Enrichissement du TokenData avec l'user_id

    🔐 SÉCURITÉ MULTI-NIVEAUX :
    - Token JWT signé cryptographiquement
    - Vérification d'expiration automatique
    - Validation de l'existence de l'utilisateur
    - Contrôle granulaire des permissions (scopes)
    - Messages d'erreur standardisés pour la sécurité

    📊 SCOPES SUPPORTÉS :
    - todos:read : Lecture des todos (GET /todos/*)
    - todos:write : Création/modification (POST, PATCH /todos/*)
    - todos:delete : Suppression (DELETE /todos/*)
    - admin : Accès administrateur (toutes opérations)

    Args:
        security_scopes (SecurityScopes): Scopes requis par l'endpoint appelant
        token (str): Token JWT extrait de l'header Authorization
        db (Session): Session de base de données pour vérifier l'utilisateur

    Returns:
        TokenData: Données utilisateur avec user_id, username et scopes validés

    Raises:
        MissingTokenError: Si le token n'est pas fourni ou est vide
        InvalidTokenError: Si le token est malformé ou l'utilisateur n'existe pas
        ExpiredTokenError: Si le token a expiré
        HTTPException 403: Scopes insuffisants pour l'opération demandée

    Usage dans les routes :
        @router.get("/todos/all")
        async def get_todos(
            current_user: TokenData = Security(get_current_user, scopes=["todos:read"])
        ):
            # current_user.user_id est maintenant disponible
            todos = await use_cases.get_all_todos_by_owner(current_user.user_id)

    Note sur la sécurité :
        Les messages d'erreur sont volontairement génériques pour éviter
        de donner des informations aux attaquants (user enumeration).
    """
    # Configuration du header WWW-Authenticate pour les erreurs 401
    if security_scopes.scopes:
        # Format OAuth2 standard avec scopes requis
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        # Format Bearer simple sans scopes
        authenticate_value = "Bearer"

    try:
        # Étape 1 : Validation du token JWT (signature, expiration, format)
        token_data = verify_token(token)

        # Étape 2 : Vérification de l'existence de l'utilisateur en base
        if not token_data.username:
            raise InvalidTokenError("Token does not contain valid user information")

        user_repo = SQLiteUserRepository(db)
        user = await user_repo.get_user_by_username(token_data.username)
        if not user:
            # Utilisateur supprimé ou désactivé depuis la génération du token
            raise InvalidTokenError("User associated with token no longer exists")

    except (InvalidTokenError, ExpiredTokenError, MissingTokenError):
        # Les exceptions JWT remontent directement avec leurs messages spécifiques
        raise
    except Exception:
        # Fallback pour autres erreurs non prévues
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # Étape 3 : Enrichissement avec l'user_id pour les Use Cases
    token_data.user_id = user.id

    # Étape 4 : Vérification des scopes (permissions granulaires)
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            # Permissions insuffisantes pour cette opération
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return token_data


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[TokenData]:
    """
    Dépendance pour l'authentification optionnelle.

    Similaire à get_current_user mais ne lève pas d'exception si le token est absent.
    Utile pour les endpoints qui fonctionnent avec ou sans authentification.

    Args:
        token (str, optional): Token JWT optionnel
        db (Session): Session de base de données

    Returns:
        TokenData | None: Données utilisateur si token valide, None sinon

    Raises:
        InvalidTokenError: Si le token fourni est malformé
        ExpiredTokenError: Si le token fourni a expiré
    """
    if not token:
        return None

    try:
        # Utilise la même logique que get_current_user mais sans scopes
        token_data = verify_token(token)

        if not token_data.username:
            raise InvalidTokenError("Token does not contain valid user information")

        user_repo = SQLiteUserRepository(db)
        user = await user_repo.get_user_by_username(token_data.username)
        if not user:
            raise InvalidTokenError("User associated with token no longer exists")

        token_data.user_id = user.id
        return token_data

    except (InvalidTokenError, ExpiredTokenError, MissingTokenError):
        # Les exceptions remontent pour informer le client du problème
        raise


# ===== DÉPENDANCES MÉTIER =====


def get_todo_use_cases(
    db: Annotated[Session, Depends(get_db)],
) -> TodoUseCases:
    """
    Factory pour créer une instance des Use Cases Todo avec injection de dépendances.

    🏗️ PATTERN DEPENDENCY INJECTION :
    1. Injection de la session de base de données
    2. Création du repository SQLite avec cette session
    3. Injection du repository dans les Use Cases
    4. Retour de l'instance configurée

    ✅ AVANTAGES :
    - Respecte l'inversion de dépendance (DIP)
    - Facilite les tests unitaires (mock du repository)
    - Permet de changer d'implémentation facilement
    - Scope de vie géré par FastAPI (une instance par requête)
    - Type safety avec annotations complètes

    🔄 LIFECYCLE :
    - Créé à chaque requête HTTP
    - Session DB fermée automatiquement en fin de requête
    - Garbage collection automatique des objets
    - Thread-safe par design (pas de partage d'état)

    Args:
        db (Session): Session SQLAlchemy injectée automatiquement par get_db()

    Returns:
        TodoUseCases: Instance configurée avec le repository SQLite

    Usage dans les routes :
        @router.get("/todos/all")
        async def get_todos(
            use_cases: TodoUseCases = Depends(get_todo_use_cases),
            current_user: TokenData = Security(get_current_user, scopes=["todos:read"])
        ):
            return await use_cases.get_all_todos_by_owner(current_user.user_id)

    Tests unitaires :
        # Mock de la dépendance pour les tests
        app.dependency_overrides[get_todo_use_cases] = lambda: MockTodoUseCases()

    Note architecturale :
        Cette fonction respecte la Clean Architecture en ne créant que
        des instances de la couche Application, sans dépendance directe
        vers les détails techniques (SQLAlchemy, FastAPI, etc.)
    """
    # Création du repository avec la session injectée
    todo_repository = SQLiteTodoRepository(db)

    # Injection du repository dans les Use Cases (inversion de dépendance)
    return TodoUseCases(todo_repository)


def get_auth_use_cases(
    db: Annotated[Session, Depends(get_db)],
) -> AuthUseCases:
    """
    Factory pour créer une instance des Use Cases Auth avec injection de dépendances.

    Args:
        db (Session): Session SQLAlchemy injectée automatiquement par get_db()

    Returns:
        AuthUseCases: Instance configurée avec les services requis
    """
    from src.infrastructure.auth.jwt_service import JWTService
    from src.infrastructure.auth.password_service import PasswordService

    # Création du repository avec la session injectée
    user_repository = SQLiteUserRepository(db)

    # Création des services requis
    jwt_service = JWTService()
    password_service = PasswordService()

    # Injection de toutes les dépendances dans les Use Cases
    return AuthUseCases(user_repository, jwt_service, password_service)
